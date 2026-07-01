# DOCX/TXT 脱敏清单工作台 PoC v0.2

本工程验证 DOCX/TXT 文件的身份证号码提取、遮蔽、重建、复检，以及人工分类分级标签写入能力。v0.2 将单文件 PoC 升级为 Streamlit 多文件处理清单工作台。

## 当前能力

1. 支持逐个上传 DOCX/TXT 文件。
2. 每个文件由人工填写分类编码、分类名称、分级标签和备注。
3. 提取中国居民身份证号码实体。
4. 按“前 6 位 + 星号 + 后 4 位”遮蔽身份证号码。
5. 保留原值—遮蔽值映射。
6. 重建脱敏后的 DOCX/TXT 文件。
7. 输出文件复检，检查原值残留、遮蔽值出现和分类分级标签。
8. 使用 `st.session_state.file_records` 保存当前 PoC 会话清单。
9. 支持单文件查看、下载、删除，支持清单 CSV 导出和全部结果 ZIP 导出。

## 分类分级标签

本 PoC 不执行自动分类分级。分类编码、分类名称、分级标签均来自页面人工输入。

- DOCX：写入不可见的自定义文档属性，不写入正文。
- TXT：在文件头部写入元数据块。

DOCX 自定义文档属性包括：

- `DataCategoryCode`
- `DataCategoryName`
- `DataLevel`
- `LabelSource`

## 清单字段

处理清单包含：

- 文件名
- 文件格式
- 分类编码
- 分类名称
- 分级标签
- 敏感实体数量
- 处理敏感实体数量
- 未处理敏感实体数量
- 处理状态
- 复检状态
- 备注
- 处理时间

## 状态规则

- 敏感实体数量为 0：处理状态为“未发现敏感实体”，复检状态为“未通过”。
- 实体全部成功遮蔽且复检通过：处理状态为“处理成功”。
- 仅部分实体处理：处理状态为“部分成功”。
- 实体未处理或文件失败：处理状态为“处理失败”。

## 导出

- `导出处理清单 CSV`：生成 UTF-8 BOM 编码的 `处理清单.csv`。
- `打包下载全部结果 ZIP`：ZIP 内包含 `处理清单.csv` 和全部脱敏文件。
- ZIP 中脱敏文件重名时自动追加唯一编号。

## 启动

```powershell
cd "D:\00 my code\docx_txt_masking_poc"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m streamlit run app.py
```

浏览器访问 Streamlit 输出的本地地址，通常为：

```text
http://localhost:8501
```

## 自动测试

```powershell
python -m pytest -q
```

## 样本

`sample_data` 目录包含 DOCX 和 TXT 样本，使用测试身份证号码：

```text
11010519491231002X
```

预期遮蔽结果：

```text
110105********002X
```

## 限制

- 仅支持 DOCX 和 TXT。
- 仅识别身份证号码，不扩展其他敏感实体类型。
- 不执行自动分类分级。
- DOCX 页面预览是文本提取预览，不是完整 Word 版式渲染。
- 会话记录仅保存在当前 Streamlit 会话中，刷新或重启后不会持久化。
