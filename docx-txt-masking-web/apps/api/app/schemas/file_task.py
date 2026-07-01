from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ApiResponse(BaseModel):
    code: int = 0
    message: str = "success"
    data: Any = None


class EntityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    entity_type: str
    masked_original_value: str
    masked_value: str
    location: str
    extractor: str
    format_valid: bool
    checksum_valid: bool | None
    processed: bool
    created_at: datetime


class FileTaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    original_file_name: str
    output_file_name: str | None
    file_type: str
    file_size: int
    category_code: str
    category_name: str
    level: str
    label_source: str
    note: str
    entity_count: int
    processed_entity_count: int
    unprocessed_entity_count: int
    process_status: str
    verification_status: str
    error_message: str
    created_at: datetime
    updated_at: datetime


class FileTaskDetail(FileTaskOut):
    entities: list[EntityOut] = Field(default_factory=list)
    verification: dict[str, Any] = Field(default_factory=dict)
    mappings: list[dict[str, Any]] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
