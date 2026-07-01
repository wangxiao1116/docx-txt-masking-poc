from __future__ import annotations

import re
from models import SensitiveEntity


# PoC策略：
# 1. 先按身份证号码格式提取候选实体；
# 2. 校验码只作为质量字段，不作为“是否属于敏感实体”的拦截条件；
# 3. 这样可处理人工编辑、仿真、测试数据中的格式化身份证号码。
ID_CARD_PATTERN = re.compile(
    r"(?<![0-9A-Za-z])(?:"
    r"\d{6}(?:18|19|20)\d{2}(?:0[1-9]|1[0-2])"
    r"(?:0[1-9]|[12]\d|3[01])\d{3}[\dXx]"
    r"|"
    r"\d{6}\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])\d{3}"
    r")(?![0-9A-Za-z])"
)

WEIGHTS = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
CHECK_CODES = "10X98765432"


def is_valid_cn_id_card(value: str) -> bool:
    """校验身份证号码。18位校验校验码；15位仅做数字格式校验。"""
    normalized = value.upper()
    if len(normalized) == 15:
        return normalized.isdigit()
    if len(normalized) != 18 or not normalized[:17].isdigit():
        return False
    checksum = sum(int(normalized[i]) * WEIGHTS[i] for i in range(17)) % 11
    return normalized[-1] == CHECK_CODES[checksum]


def extract_id_cards(text: str, location: str) -> list[SensitiveEntity]:
    entities: list[SensitiveEntity] = []
    for match in ID_CARD_PATTERN.finditer(text):
        value = match.group(0).upper()
        entities.append(
            SensitiveEntity(
                entity_type="CN_ID_CARD",
                original_value=value,
                start=match.start(),
                end=match.end(),
                location=location,
                extractor="REGEX_IDCARD_FORMAT",
                format_valid=True,
                checksum_valid=is_valid_cn_id_card(value),
            )
        )
    return entities
