from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, Response
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.session import get_db
from app.models.file_task import FileTask
from app.schemas.file_task import ApiResponse, EntityOut, FileTaskDetail, FileTaskOut
from app.services.export_service import build_manifest_csv, build_results_zip
from app.services.preview_service import extract_preview
from app.services.processing_service import (
    ProcessingError,
    create_and_process_task,
    delete_task_files,
    process_stored_task,
)


router = APIRouter()


def ok(data=None) -> ApiResponse:
    return ApiResponse(data=data)


def task_out(task: FileTask) -> dict:
    return FileTaskOut.model_validate(task).model_dump(mode="json")


def json_field(value: str | None, fallback: Any) -> Any:
    if not value:
        return fallback
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return fallback


def task_detail(task: FileTask) -> dict:
    data = FileTaskOut.model_validate(task).model_dump()
    data["entities"] = [EntityOut.model_validate(item).model_dump() for item in task.entities]
    data["verification"] = json_field(task.verification_json, {})
    data["mappings"] = json_field(task.mappings_json, [])
    data["metadata"] = json_field(task.metadata_json, {})
    return FileTaskDetail.model_validate(data).model_dump(mode="json")


def error_response(code: int, message: str, status_code: int = 400) -> Response:
    return Response(
        content=ApiResponse(code=code, message=message, data=None).model_dump_json(),
        status_code=status_code,
        media_type="application/json",
    )


def get_task(db: Session, task_id: str) -> FileTask:
    task = db.scalar(
        select(FileTask)
        .options(selectinload(FileTask.entities))
        .where(FileTask.id == task_id)
    )
    if task is None:
        raise HTTPException(status_code=404, detail="文件任务不存在")
    return task


@router.get("/health")
def health():
    return ok({"status": "ok"})


@router.post("/files")
async def upload_file(
    file: UploadFile = File(...),
    category_code: str = Form(...),
    category_name: str = Form(...),
    level: str = Form(...),
    note: str = Form(""),
    db: Session = Depends(get_db),
):
    if not category_code.strip() or not category_name.strip():
        return error_response(40004, "分类编码和分类名称不能为空")
    content = await file.read()
    try:
        task = create_and_process_task(
            db,
            file.filename or "",
            content,
            category_code,
            category_name,
            level,
            note,
        )
    except ProcessingError as exc:
        return error_response(exc.code, exc.message)
    return ok(task_out(task))


@router.get("/files")
def list_files(
    search: str = "",
    file_type: str = "",
    level: str = "",
    process_status: str = "",
    verification_status: str = "",
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
):
    statement = select(FileTask).order_by(FileTask.created_at.desc())
    tasks = list(db.scalars(statement).all())
    if search:
        tasks = [task for task in tasks if search.lower() in task.original_file_name.lower()]
    if file_type:
        tasks = [task for task in tasks if task.file_type == file_type]
    if level:
        tasks = [task for task in tasks if task.level == level]
    if process_status:
        tasks = [task for task in tasks if task.process_status == process_status]
    if verification_status:
        tasks = [task for task in tasks if task.verification_status == verification_status]
    total = len(tasks)
    start = max(page - 1, 0) * page_size
    end = start + page_size
    return ok(
        {
            "items": [task_out(task) for task in tasks[start:end]],
            "total": total,
            "page": page,
            "page_size": page_size,
        }
    )


@router.get("/files/{task_id}")
def file_detail(task_id: str, db: Session = Depends(get_db)):
    return ok(task_detail(get_task(db, task_id)))


@router.post("/files/{task_id}/process")
def process_file_again(task_id: str, db: Session = Depends(get_db)):
    task = process_stored_task(db, get_task(db, task_id))
    return ok(task_out(task))


@router.get("/files/{task_id}/preview/original")
def preview_original(task_id: str, db: Session = Depends(get_db)):
    task = get_task(db, task_id)
    text = extract_preview(task.original_file_name, Path(task.stored_original_path).read_bytes())
    return ok({"text": text})


@router.get("/files/{task_id}/preview/masked")
def preview_masked(task_id: str, db: Session = Depends(get_db)):
    task = get_task(db, task_id)
    if not task.stored_output_path:
        return error_response(40401, "脱敏文件不存在", status_code=404)
    text = extract_preview(task.original_file_name, Path(task.stored_output_path).read_bytes())
    return ok({"text": text})


@router.get("/files/{task_id}/entities")
def file_entities(task_id: str, db: Session = Depends(get_db)):
    task = get_task(db, task_id)
    return ok([EntityOut.model_validate(item).model_dump(mode="json") for item in task.entities])


@router.get("/files/{task_id}/download")
def download_file(task_id: str, db: Session = Depends(get_db)):
    task = get_task(db, task_id)
    if not task.stored_output_path or not Path(task.stored_output_path).exists():
        raise HTTPException(status_code=404, detail="脱敏文件不存在")
    return FileResponse(
        task.stored_output_path,
        filename=task.output_file_name or f"{task_id}_masked",
    )


@router.delete("/files/{task_id}")
def delete_file(task_id: str, db: Session = Depends(get_db)):
    task = get_task(db, task_id)
    delete_task_files(task)
    db.delete(task)
    db.commit()
    return ok({"deleted": task_id})


@router.get("/exports/manifest.csv")
def export_manifest(db: Session = Depends(get_db)):
    tasks = list(db.scalars(select(FileTask).order_by(FileTask.created_at.asc())).all())
    return Response(
        content=build_manifest_csv(tasks),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename*=UTF-8''%E5%A4%84%E7%90%86%E6%B8%85%E5%8D%95.csv"},
    )


@router.get("/exports/results.zip")
def export_zip(db: Session = Depends(get_db)):
    tasks = list(db.scalars(select(FileTask).order_by(FileTask.created_at.asc())).all())
    return Response(
        content=build_results_zip(tasks),
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=masked-results.zip"},
    )
