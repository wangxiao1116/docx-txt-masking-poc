from __future__ import annotations

import json
import shutil
from pathlib import Path
from uuid import uuid4

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.file_task import FileTask, SensitiveEntityRecord
from app.services.poc_imports import core_path as _core_path
from app.services.security import mask_sensitive_value, sanitize_filename

from models import ClassificationLabel
from processors import process_file
from verification import verify_output


ALLOWED_SUFFIXES = {".docx": "DOCX", ".txt": "TXT"}


class ProcessingError(Exception):
    def __init__(self, code: int, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def _ensure_storage() -> None:
    for folder in ["originals", "outputs", "exports"]:
        (settings.storage_dir / folder).mkdir(parents=True, exist_ok=True)


def _output_filename(filename: str) -> str:
    path = Path(filename)
    return f"{path.stem}_masked{path.suffix.lower()}"


def _status(entity_count: int, processed_count: int, verification_passed: bool) -> str:
    if entity_count == 0:
        return "未发现敏感实体"
    if processed_count == 0:
        return "处理失败"
    if processed_count < entity_count:
        return "部分成功"
    return "处理成功" if verification_passed else "处理失败"


def _processed_count(entity_count: int, mappings_count: int, replacement_count: int, verification_passed: bool) -> int:
    if entity_count == 0:
        return 0
    if verification_passed:
        return entity_count
    return min(entity_count, mappings_count, replacement_count)


def _safe_mappings(mappings) -> list[dict[str, str]]:
    return [
        {
            "entity_type": item.entity_type,
            "masked_original_value": mask_sensitive_value(item.original_value),
            "masked_value": item.masked_value,
            "location": item.location,
        }
        for item in mappings
    ]


def _serialize_task(task: FileTask) -> dict:
    return {
        "id": task.id,
        "original_file_name": task.original_file_name,
        "output_file_name": task.output_file_name,
        "file_type": task.file_type,
        "file_size": task.file_size,
        "category_code": task.category_code,
        "category_name": task.category_name,
        "level": task.level,
        "label_source": task.label_source,
        "note": task.note,
        "entity_count": task.entity_count,
        "processed_entity_count": task.processed_entity_count,
        "unprocessed_entity_count": task.unprocessed_entity_count,
        "process_status": task.process_status,
        "verification_status": task.verification_status,
        "error_message": task.error_message,
        "created_at": task.created_at,
        "updated_at": task.updated_at,
    }


def validate_upload(filename: str, content: bytes) -> tuple[str, str]:
    if not content:
        raise ProcessingError(40002, "文件为空")
    if len(content) > settings.max_upload_size_mb * 1024 * 1024:
        raise ProcessingError(40003, "文件超过大小限制")
    safe_name = sanitize_filename(filename)
    suffix = Path(safe_name).suffix.lower()
    if suffix not in ALLOWED_SUFFIXES:
        raise ProcessingError(40001, "文件格式不支持")
    return safe_name, ALLOWED_SUFFIXES[suffix]


def create_and_process_task(
    db: Session,
    filename: str,
    content: bytes,
    category_code: str,
    category_name: str,
    level: str,
    note: str = "",
) -> FileTask:
    _ensure_storage()
    safe_name, file_type = validate_upload(filename, content)
    task_id = str(uuid4())
    suffix = Path(safe_name).suffix.lower()
    original_path = settings.storage_dir / "originals" / f"{task_id}{suffix}"
    output_path = settings.storage_dir / "outputs" / f"{task_id}_masked{suffix}"
    original_path.write_bytes(content)

    task = FileTask(
        id=task_id,
        original_file_name=safe_name,
        stored_original_path=str(original_path),
        stored_output_path="",
        output_file_name=_output_filename(safe_name),
        file_type=file_type,
        file_size=len(content),
        category_code=category_code.strip(),
        category_name=category_name.strip(),
        level=level.strip(),
        label_source="MANUAL",
        note=note.strip(),
        process_status="处理中",
        verification_status="未通过",
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return process_stored_task(db, task)


def process_stored_task(db: Session, task: FileTask) -> FileTask:
    label = ClassificationLabel(
        category_code=task.category_code,
        category_name=task.category_name,
        level=task.level,
        source=task.label_source,
    )
    output_path = Path(task.stored_output_path) if task.stored_output_path else (
        settings.storage_dir / "outputs" / f"{task.id}_masked{Path(task.original_file_name).suffix.lower()}"
    )

    try:
        source_bytes = Path(task.stored_original_path).read_bytes()
        output_bytes, entities, mappings, metadata = process_file(
            task.original_file_name,
            source_bytes,
            label,
        )
        verification = verify_output(task.original_file_name, output_bytes, label, mappings)
        output_path.write_bytes(output_bytes)

        replacement_count = int(metadata.get("replacement_count") or 0)
        processed_count = _processed_count(
            len(entities),
            len(mappings),
            replacement_count,
            verification.passed,
        )
        verification_status = "通过" if verification.passed and entities else "未通过"

        task.stored_output_path = str(output_path)
        task.output_file_name = _output_filename(task.original_file_name)
        task.entity_count = len(entities)
        task.processed_entity_count = processed_count
        task.unprocessed_entity_count = max(len(entities) - processed_count, 0)
        task.process_status = _status(len(entities), processed_count, verification.passed)
        task.verification_status = verification_status
        task.error_message = ""
        task.verification_json = json.dumps(verification.as_dict(), ensure_ascii=False)
        task.metadata_json = json.dumps(metadata, ensure_ascii=False)
        task.mappings_json = json.dumps(_safe_mappings(mappings), ensure_ascii=False)

        task.entities.clear()
        for entity, mapping in zip(entities, mappings, strict=False):
            task.entities.append(
                SensitiveEntityRecord(
                    entity_type=entity.entity_type,
                    masked_original_value=mask_sensitive_value(entity.original_value),
                    masked_value=mapping.masked_value,
                    location=entity.location,
                    extractor=entity.extractor,
                    format_valid=entity.format_valid,
                    checksum_valid=entity.checksum_valid,
                    processed=mapping.masked_value != "",
                )
            )
    except Exception as exc:
        task.process_status = "处理失败"
        task.verification_status = "未通过"
        task.error_message = str(exc)
        task.verification_json = json.dumps(
            {"passed": False, "details": [str(exc)]},
            ensure_ascii=False,
        )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def delete_task_files(task: FileTask) -> None:
    for value in [task.stored_original_path, task.stored_output_path]:
        if not value:
            continue
        path = Path(value)
        if path.exists() and path.is_file():
            path.unlink()


def duplicate_sample_data() -> None:
    sample_dir = settings.repo_root / "sample-data"
    sample_dir.mkdir(parents=True, exist_ok=True)
