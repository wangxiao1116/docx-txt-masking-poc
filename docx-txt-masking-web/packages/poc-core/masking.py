from __future__ import annotations

from models import SensitiveEntity, ReplacementMapping


def mask_cn_id_card(value: str) -> str:
    normalized = value.upper()
    if len(normalized) == 18:
        return normalized[:6] + "********" + normalized[-4:]
    if len(normalized) == 15:
        return normalized[:6] + "*****" + normalized[-4:]
    raise ValueError(f"Unsupported ID card length: {len(normalized)}")


def build_replacement_mappings(
    entities: list[SensitiveEntity],
) -> list[ReplacementMapping]:
    mappings: list[ReplacementMapping] = []
    for entity in entities:
        if entity.entity_type != "CN_ID_CARD":
            continue
        mappings.append(
            ReplacementMapping(
                entity_type=entity.entity_type,
                original_value=entity.original_value,
                masked_value=mask_cn_id_card(entity.original_value),
                location=entity.location,
            )
        )
    return mappings
