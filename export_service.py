from __future__ import annotations

import csv
from io import BytesIO, StringIO
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from record_manager import FileProcessingRecord, MANIFEST_COLUMNS, manifest_rows


def generate_manifest_csv(records: list[FileProcessingRecord]) -> bytes:
    buffer = StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=MANIFEST_COLUMNS, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(manifest_rows(records))
    return buffer.getvalue().encode("utf-8-sig")


def _unique_zip_name(filename: str, used_names: set[str]) -> str:
    candidate = filename
    path = Path(filename)
    index = 2
    while candidate in used_names:
        candidate = f"{path.stem}_{index}{path.suffix}"
        index += 1
    used_names.add(candidate)
    return candidate


def generate_results_zip(records: list[FileProcessingRecord]) -> bytes:
    output = BytesIO()
    used_names = {"处理清单.csv"}

    with ZipFile(output, "w", ZIP_DEFLATED) as archive:
        archive.writestr("处理清单.csv", generate_manifest_csv(records))
        for record in records:
            if not record.output_bytes:
                continue
            filename = _unique_zip_name(record.output_filename, used_names)
            archive.writestr(filename, record.output_bytes)

    return output.getvalue()
