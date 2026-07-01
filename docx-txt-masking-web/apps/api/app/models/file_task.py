from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class FileTask(Base):
    __tablename__ = "file_tasks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    original_file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_original_path: Mapped[str] = mapped_column(Text, nullable=False)
    stored_output_path: Mapped[str] = mapped_column(Text, nullable=True)
    output_file_name: Mapped[str] = mapped_column(String(255), nullable=True)
    file_type: Mapped[str] = mapped_column(String(16), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    category_code: Mapped[str] = mapped_column(String(64), nullable=False)
    category_name: Mapped[str] = mapped_column(String(128), nullable=False)
    level: Mapped[str] = mapped_column(String(64), nullable=False)
    label_source: Mapped[str] = mapped_column(String(32), default="MANUAL")
    note: Mapped[str] = mapped_column(Text, default="")
    entity_count: Mapped[int] = mapped_column(Integer, default=0)
    processed_entity_count: Mapped[int] = mapped_column(Integer, default=0)
    unprocessed_entity_count: Mapped[int] = mapped_column(Integer, default=0)
    process_status: Mapped[str] = mapped_column(String(32), default="待处理")
    verification_status: Mapped[str] = mapped_column(String(32), default="未通过")
    error_message: Mapped[str] = mapped_column(Text, default="")
    verification_json: Mapped[str] = mapped_column(Text, default="{}")
    metadata_json: Mapped[str] = mapped_column(Text, default="{}")
    mappings_json: Mapped[str] = mapped_column(Text, default="[]")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    entities: Mapped[list["SensitiveEntityRecord"]] = relationship(
        back_populates="file_task",
        cascade="all, delete-orphan",
    )


class SensitiveEntityRecord(Base):
    __tablename__ = "sensitive_entities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    file_task_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("file_tasks.id", ondelete="CASCADE"),
        nullable=False,
    )
    entity_type: Mapped[str] = mapped_column(String(64), nullable=False)
    masked_original_value: Mapped[str] = mapped_column(String(64), nullable=False)
    masked_value: Mapped[str] = mapped_column(String(64), nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    extractor: Mapped[str] = mapped_column(String(64), nullable=False)
    format_valid: Mapped[bool] = mapped_column(Boolean, default=True)
    checksum_valid: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    processed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    file_task: Mapped[FileTask] = relationship(back_populates="entities")
