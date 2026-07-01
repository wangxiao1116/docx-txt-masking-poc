from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


@dataclass(frozen=True)
class ClassificationLabel:
    category_code: str
    category_name: str
    level: str
    source: str = "MANUAL"

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SensitiveEntity:
    entity_type: str
    original_value: str
    start: int
    end: int
    location: str
    extractor: str = "REGEX_IDCARD"
    format_valid: bool = True
    checksum_valid: bool | None = None

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ReplacementMapping:
    entity_type: str
    original_value: str
    masked_value: str
    location: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class VerificationResult:
    file_openable: bool
    entity_count: int
    original_value_residual_count: int
    masked_value_count: int
    label_present: bool
    passed: bool
    details: list[str]

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)
