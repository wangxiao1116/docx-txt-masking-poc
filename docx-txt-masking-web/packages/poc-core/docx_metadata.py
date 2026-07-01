from __future__ import annotations

from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile
from xml.etree import ElementTree as ET


CT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"
REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
CP_NS = "http://schemas.openxmlformats.org/officeDocument/2006/custom-properties"
VT_NS = "http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes"

CUSTOM_CONTENT_TYPE = (
    "application/vnd.openxmlformats-officedocument.custom-properties+xml"
)
CUSTOM_REL_TYPE = (
    "http://schemas.openxmlformats.org/officeDocument/2006/relationships/"
    "custom-properties"
)
CUSTOM_PART_NAME = "/docProps/custom.xml"
CUSTOM_TARGET = "docProps/custom.xml"
FMTID = "{D5CDD505-2E9C-101B-9397-08002B2CF9AE}"

ET.register_namespace("", CP_NS)
ET.register_namespace("vt", VT_NS)


def _build_custom_xml(properties: dict[str, str]) -> bytes:
    root = ET.Element(f"{{{CP_NS}}}Properties")
    for pid, (name, value) in enumerate(properties.items(), start=2):
        prop = ET.SubElement(
            root,
            f"{{{CP_NS}}}property",
            {
                "fmtid": FMTID,
                "pid": str(pid),
                "name": name,
            },
        )
        child = ET.SubElement(prop, f"{{{VT_NS}}}lpwstr")
        child.text = str(value)
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def _upsert_content_type(xml_bytes: bytes) -> bytes:
    root = ET.fromstring(xml_bytes)
    existing = root.findall(f"{{{CT_NS}}}Override")
    if not any(item.get("PartName") == CUSTOM_PART_NAME for item in existing):
        ET.SubElement(
            root,
            f"{{{CT_NS}}}Override",
            {
                "PartName": CUSTOM_PART_NAME,
                "ContentType": CUSTOM_CONTENT_TYPE,
            },
        )
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def _upsert_relationship(xml_bytes: bytes) -> bytes:
    root = ET.fromstring(xml_bytes)
    relationships = root.findall(f"{{{REL_NS}}}Relationship")
    for item in relationships:
        if item.get("Type") == CUSTOM_REL_TYPE:
            item.set("Target", CUSTOM_TARGET)
            return ET.tostring(root, encoding="utf-8", xml_declaration=True)

    used_ids = {item.get("Id") for item in relationships}
    index = 1
    while f"rIdCustom{index}" in used_ids:
        index += 1

    ET.SubElement(
        root,
        f"{{{REL_NS}}}Relationship",
        {
            "Id": f"rIdCustom{index}",
            "Type": CUSTOM_REL_TYPE,
            "Target": CUSTOM_TARGET,
        },
    )
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def write_custom_properties(
    docx_bytes: bytes,
    properties: dict[str, str],
) -> bytes:
    """Write invisible custom document properties without changing document body."""
    source = BytesIO(docx_bytes)
    output = BytesIO()

    with ZipFile(source, "r") as zin, ZipFile(output, "w", ZIP_DEFLATED) as zout:
        names = set(zin.namelist())
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "[Content_Types].xml":
                data = _upsert_content_type(data)
            elif item.filename == "_rels/.rels":
                data = _upsert_relationship(data)
            elif item.filename == "docProps/custom.xml":
                continue
            zout.writestr(item, data)

        if "_rels/.rels" not in names:
            rel_root = ET.Element(f"{{{REL_NS}}}Relationships")
            rel_xml = ET.tostring(
                rel_root, encoding="utf-8", xml_declaration=True
            )
            zout.writestr("_rels/.rels", _upsert_relationship(rel_xml))

        zout.writestr("docProps/custom.xml", _build_custom_xml(properties))

    return output.getvalue()


def read_custom_properties(docx_bytes: bytes) -> dict[str, str]:
    with ZipFile(BytesIO(docx_bytes), "r") as archive:
        if "docProps/custom.xml" not in archive.namelist():
            return {}
        root = ET.fromstring(archive.read("docProps/custom.xml"))

    result: dict[str, str] = {}
    for prop in root.findall(f"{{{CP_NS}}}property"):
        name = prop.get("name")
        if not name:
            continue
        value = ""
        for child in list(prop):
            value = child.text or ""
            break
        result[name] = value
    return result
