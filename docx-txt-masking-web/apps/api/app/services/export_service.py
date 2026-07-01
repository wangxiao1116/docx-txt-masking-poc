from __future__ import annotations

import csv
from io import BytesIO, StringIO
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from app.models.file_task import FileTask


MANIFEST_COLUMNS = [
    "文件名",
    "格式",
    "分类编码",
    "分类名称",
    "分级标签",
    "敏感实体数量",
    "已处理实体数量",
    "未处理实体数量",
    "处理状态",
    "复检状态",
    "上传时间",
    "备注",
]


def task_to_manifest_row(task: FileTask) -> dict[str, str | int]:
    return {
        "文件名": task.original_file_name,
        "格式": task.file_type,
        "分类编码": task.category_code,
        "分类名称": task.category_name,
        "分级标签": task.level,
        "敏感实体数量": task.entity_count,
        "已处理实体数量": task.processed_entity_count,
        "未处理实体数量": task.unprocessed_entity_count,
        "处理状态": task.process_status,
        "复检状态": task.verification_status,
        "上传时间": task.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        "备注": task.note,
    }


def build_manifest_csv(tasks: list[FileTask]) -> bytes:
    buffer = StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=MANIFEST_COLUMNS)
    writer.writeheader()
    writer.writerows(task_to_manifest_row(task) for task in tasks)
    return buffer.getvalue().encode("utf-8-sig")


def _unique_name(filename: str, used: set[str]) -> str:
    path = Path(filename)
    candidate = filename
    index = 2
    while candidate in used:
        candidate = f"{path.stem}_{index}{path.suffix}"
        index += 1
    used.add(candidate)
    return candidate


def build_results_zip(tasks: list[FileTask]) -> bytes:
    output = BytesIO()
    used = set[str]()
    with ZipFile(output, "w", ZIP_DEFLATED) as archive:
        archive.writestr("处理清单.csv", build_manifest_csv(tasks))
        for task in tasks:
            if not task.stored_output_path or not task.output_file_name:
                continue
            path = Path(task.stored_output_path)
            if not path.exists():
                continue
            name = _unique_name(task.output_file_name, used)
            archive.write(path, f"脱敏文件/{name}")
    return output.getvalue()
