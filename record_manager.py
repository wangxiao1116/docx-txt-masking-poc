from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from models import (
    ClassificationLabel,
    ReplacementMapping,
    SensitiveEntity,
    VerificationResult,
)
from preview_service import extract_preview_text


MANIFEST_COLUMNS = [
    "文件名",
    "文件格式",
    "分类编码",
    "分类名称",
    "分级标签",
    "敏感实体数量",
    "处理敏感实体数量",
    "未处理敏感实体数量",
    "处理状态",
    "复检状态",
    "备注",
    "处理时间",
]


@dataclass
class FileProcessingRecord:
    record_id: str
    filename: str
    file_format: str
    category_code: str
    category_name: str
    level: str
    remark: str
    processed_at: str
    source_bytes: bytes
    output_bytes: bytes
    output_filename: str
    entities: list[SensitiveEntity]
    mappings: list[ReplacementMapping]
    verification: VerificationResult
    metadata: dict[str, Any]
    original_preview: str
    masked_preview: str
    sensitive_entity_count: int
    processed_entity_count: int
    unprocessed_entity_count: int
    processing_status: str
    verification_status: str
    error_message: str = ""

    def manifest_row(self) -> dict[str, Any]:
        return {
            "文件名": self.filename,
            "文件格式": self.file_format,
            "分类编码": self.category_code,
            "分类名称": self.category_name,
            "分级标签": self.level,
            "敏感实体数量": self.sensitive_entity_count,
            "处理敏感实体数量": self.processed_entity_count,
            "未处理敏感实体数量": self.unprocessed_entity_count,
            "处理状态": self.processing_status,
            "复检状态": self.verification_status,
            "备注": self.remark,
            "处理时间": self.processed_at,
        }

    def entities_table(self) -> list[dict[str, Any]]:
        return [item.as_dict() for item in self.entities]

    def mappings_table(self) -> list[dict[str, Any]]:
        return [item.as_dict() for item in self.mappings]

    def verification_table(self) -> dict[str, Any]:
        return self.verification.as_dict()


def _file_format(filename: str) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix == ".docx":
        return "DOCX"
    if suffix == ".txt":
        return "TXT"
    return suffix.lstrip(".").upper() or "UNKNOWN"


def _output_filename(filename: str) -> str:
    path = Path(filename)
    return f"{path.stem}_masked{path.suffix.lower()}"


def _processed_entity_count(
    entity_count: int,
    mappings: list[ReplacementMapping],
    verification: VerificationResult,
    metadata: dict[str, Any],
) -> int:
    if entity_count == 0:
        return 0

    replacement_count = int(metadata.get("replacement_count") or 0)
    mapped_count = len(mappings)

    if verification.passed:
        return entity_count
    if replacement_count <= 0:
        return 0
    return min(entity_count, mapped_count, replacement_count)


def _processing_status(
    entity_count: int,
    processed_count: int,
    verification: VerificationResult,
    failed: bool = False,
) -> str:
    if entity_count == 0 and not failed:
        return "未发现敏感实体"
    if failed or processed_count == 0:
        return "处理失败"
    if processed_count < entity_count:
        return "部分成功"
    if verification.passed:
        return "处理成功"
    return "处理失败"


def _verification_status(verification: VerificationResult, entity_count: int) -> str:
    if entity_count == 0:
        return "未通过"
    return "通过" if verification.passed else "未通过"


def create_file_record(
    filename: str,
    source_bytes: bytes,
    output_bytes: bytes,
    label: ClassificationLabel,
    entities: list[SensitiveEntity],
    mappings: list[ReplacementMapping],
    verification: VerificationResult,
    metadata: dict[str, Any],
    remark: str = "",
    processed_at: datetime | None = None,
) -> FileProcessingRecord:
    entity_count = len(entities)
    processed_count = _processed_entity_count(
        entity_count,
        mappings,
        verification,
        metadata,
    )
    unprocessed_count = max(entity_count - processed_count, 0)

    return FileProcessingRecord(
        record_id=uuid4().hex,
        filename=filename,
        file_format=_file_format(filename),
        category_code=label.category_code,
        category_name=label.category_name,
        level=label.level,
        remark=remark,
        processed_at=(processed_at or datetime.now()).strftime("%Y-%m-%d %H:%M:%S"),
        source_bytes=source_bytes,
        output_bytes=output_bytes,
        output_filename=_output_filename(filename),
        entities=entities,
        mappings=mappings,
        verification=verification,
        metadata=metadata,
        original_preview=extract_preview_text(filename, source_bytes),
        masked_preview=extract_preview_text(filename, output_bytes),
        sensitive_entity_count=entity_count,
        processed_entity_count=processed_count,
        unprocessed_entity_count=unprocessed_count,
        processing_status=_processing_status(entity_count, processed_count, verification),
        verification_status=_verification_status(verification, entity_count),
    )


def create_failed_record(
    filename: str,
    source_bytes: bytes,
    label: ClassificationLabel,
    error: Exception,
    remark: str = "",
    processed_at: datetime | None = None,
) -> FileProcessingRecord:
    verification = VerificationResult(
        file_openable=False,
        entity_count=0,
        original_value_residual_count=-1,
        masked_value_count=0,
        label_present=False,
        passed=False,
        details=[str(error)],
    )
    original_preview = ""
    try:
        original_preview = extract_preview_text(filename, source_bytes)
    except Exception:
        original_preview = ""

    return FileProcessingRecord(
        record_id=uuid4().hex,
        filename=filename,
        file_format=_file_format(filename),
        category_code=label.category_code,
        category_name=label.category_name,
        level=label.level,
        remark=remark,
        processed_at=(processed_at or datetime.now()).strftime("%Y-%m-%d %H:%M:%S"),
        source_bytes=source_bytes,
        output_bytes=b"",
        output_filename=_output_filename(filename),
        entities=[],
        mappings=[],
        verification=verification,
        metadata={"error": str(error)},
        original_preview=original_preview,
        masked_preview="",
        sensitive_entity_count=0,
        processed_entity_count=0,
        unprocessed_entity_count=0,
        processing_status="处理失败",
        verification_status="未通过",
        error_message=str(error),
    )


def manifest_rows(records: list[FileProcessingRecord]) -> list[dict[str, Any]]:
    return [record.manifest_row() for record in records]


def empty_manifest_row() -> dict[str, Any]:
    return {column: "" for column in MANIFEST_COLUMNS}
