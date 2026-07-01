from __future__ import annotations

import pandas as pd
import streamlit as st

from export_service import generate_manifest_csv, generate_results_zip
from models import ClassificationLabel
from processors import process_file
from record_manager import (
    FileProcessingRecord,
    create_failed_record,
    create_file_record,
    manifest_rows,
)
from verification import verify_output


def _init_session_state() -> None:
    if "file_records" not in st.session_state:
        st.session_state.file_records = []
    if "uploader_key" not in st.session_state:
        st.session_state.uploader_key = 0
    if "last_message" not in st.session_state:
        st.session_state.last_message = ""


def _mime_type(filename: str) -> str:
    if filename.lower().endswith(".docx"):
        return "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    return "text/plain"


def _append_record(record: FileProcessingRecord) -> None:
    st.session_state.file_records.append(record)
    st.session_state.uploader_key += 1
    st.session_state.last_message = (
        f"已加入清单：{record.filename}（{record.processing_status}）"
    )
    st.rerun()


def _delete_record(record_id: str) -> None:
    st.session_state.file_records = [
        record
        for record in st.session_state.file_records
        if record.record_id != record_id
    ]
    st.session_state.last_message = "记录已删除"
    st.rerun()


st.set_page_config(
    page_title="DOCX/TXT 脱敏清单工作台 PoC v0.2",
    page_icon="🛡️",
    layout="wide",
)

_init_session_state()

st.title("DOCX/TXT 脱敏清单工作台 PoC v0.2")
st.caption(
    "逐个上传文件，人工填写分类分级信息，处理后加入当前会话清单；不引入数据库。"
)
st.info("DOCX 预览为文本提取预览，不是完整 Word 版式渲染。")

if st.session_state.last_message:
    st.success(st.session_state.last_message)
    st.session_state.last_message = ""

with st.container(border=True):
    st.subheader("单文件上传与人工批注")
    uploaded = st.file_uploader(
        "上传 DOCX 或 TXT 文件",
        type=["docx", "txt"],
        key=f"file_upload_{st.session_state.uploader_key}",
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        category_code = st.text_input("分类编码", value="A1-4")
    with col2:
        category_name = st.text_input("分类名称", value="个人信息")
    with col3:
        level = st.selectbox("分级标签", ["第1级", "第2级", "第3级", "第4级"], index=2)
    remark = st.text_area("备注（可选）", height=80)

    if uploaded is not None:
        st.write(
            {
                "文件名": uploaded.name,
                "文件大小": f"{uploaded.size} bytes",
                "人工分类": f"{category_code.strip()} {category_name.strip()}",
                "人工分级": level,
            }
        )

    if st.button("处理并加入清单", type="primary"):
        if uploaded is None:
            st.warning("请先上传 DOCX 或 TXT 文件。")
        elif not category_code.strip() or not category_name.strip():
            st.error("分类编码和分类名称不能为空。")
        else:
            label = ClassificationLabel(
                category_code=category_code.strip(),
                category_name=category_name.strip(),
                level=level,
            )
            source_bytes = uploaded.getvalue()
            try:
                output_bytes, entities, mappings, metadata = process_file(
                    uploaded.name,
                    source_bytes,
                    label,
                )
                verification = verify_output(
                    uploaded.name,
                    output_bytes,
                    label,
                    mappings,
                )
                record = create_file_record(
                    filename=uploaded.name,
                    source_bytes=source_bytes,
                    output_bytes=output_bytes,
                    label=label,
                    entities=entities,
                    mappings=mappings,
                    verification=verification,
                    metadata=metadata,
                    remark=remark.strip(),
                )
            except Exception as exc:
                record = create_failed_record(
                    filename=uploaded.name,
                    source_bytes=source_bytes,
                    label=label,
                    error=exc,
                    remark=remark.strip(),
                )
            _append_record(record)

records: list[FileProcessingRecord] = st.session_state.file_records

st.subheader("全部文件处理清单")
if not records:
    st.info("当前会话暂无处理记录。")
else:
    st.dataframe(
        pd.DataFrame(manifest_rows(records)),
        use_container_width=True,
        hide_index=True,
    )

    export_col1, export_col2 = st.columns(2)
    with export_col1:
        st.download_button(
            "导出处理清单 CSV",
            data=generate_manifest_csv(records),
            file_name="处理清单.csv",
            mime="text/csv",
        )
    with export_col2:
        st.download_button(
            "打包下载全部结果 ZIP",
            data=generate_results_zip(records),
            file_name="脱敏结果包.zip",
            mime="application/zip",
        )

    st.subheader("单文件查看、下载与删除")
    for index, record in enumerate(records, start=1):
        title = (
            f"{index}. {record.filename} | {record.processing_status} | "
            f"复检{record.verification_status}"
        )
        with st.expander(title):
            metric_cols = st.columns(4)
            metric_cols[0].metric("敏感实体数量", record.sensitive_entity_count)
            metric_cols[1].metric("处理数量", record.processed_entity_count)
            metric_cols[2].metric("未处理数量", record.unprocessed_entity_count)
            metric_cols[3].metric("文件格式", record.file_format)

            tabs = st.tabs(
                [
                    "原文文本预览",
                    "脱敏后文本预览",
                    "敏感实体明细",
                    "原值—遮蔽值映射",
                    "输出复检结果",
                ]
            )
            with tabs[0]:
                st.text_area(
                    "原文文本提取预览",
                    value=record.original_preview,
                    height=260,
                    disabled=True,
                    key=f"original_{record.record_id}",
                )
            with tabs[1]:
                st.text_area(
                    "脱敏后文本提取预览",
                    value=record.masked_preview,
                    height=260,
                    disabled=True,
                    key=f"masked_{record.record_id}",
                )
            with tabs[2]:
                if record.entities:
                    st.dataframe(
                        pd.DataFrame(record.entities_table()),
                        use_container_width=True,
                        hide_index=True,
                    )
                else:
                    st.warning("未发现敏感实体。")
            with tabs[3]:
                if record.mappings:
                    st.dataframe(
                        pd.DataFrame(record.mappings_table()),
                        use_container_width=True,
                        hide_index=True,
                    )
                else:
                    st.info("没有原值—遮蔽值映射。")
            with tabs[4]:
                st.json(record.verification_table())
                if record.error_message:
                    st.error(record.error_message)

            action_col1, action_col2 = st.columns(2)
            with action_col1:
                if record.output_bytes:
                    st.download_button(
                        "下载脱敏文件",
                        data=record.output_bytes,
                        file_name=record.output_filename,
                        mime=_mime_type(record.output_filename),
                        key=f"download_{record.record_id}",
                    )
                else:
                    st.button(
                        "下载脱敏文件",
                        key=f"download_disabled_{record.record_id}",
                        disabled=True,
                    )
            with action_col2:
                if st.button(
                    "从清单中删除",
                    key=f"delete_{record.record_id}",
                    type="secondary",
                ):
                    _delete_record(record.record_id)
