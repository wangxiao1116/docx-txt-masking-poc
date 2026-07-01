from __future__ import annotations

import re
from pathlib import Path


SAFE_NAME_PATTERN = re.compile(r"[^A-Za-z0-9._\-\u4e00-\u9fff]+")


def sanitize_filename(filename: str) -> str:
    name = Path(filename).name.strip()
    if not name:
        raise ValueError("文件名不能为空")
    sanitized = SAFE_NAME_PATTERN.sub("_", name)
    return sanitized[:180]


def mask_sensitive_value(value: str) -> str:
    normalized = value.upper()
    if len(normalized) <= 8:
        return "*" * len(normalized)
    return f"{normalized[:6]}{'*' * max(len(normalized) - 10, 4)}{normalized[-4:]}"
