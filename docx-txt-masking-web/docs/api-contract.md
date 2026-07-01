# API 合同

所有 JSON 接口返回：

```json
{
  "code": 0,
  "message": "success",
  "data": {}
}
```

异常示例：

```json
{
  "code": 40001,
  "message": "文件格式不支持",
  "data": null
}
```

## 接口

- `POST /api/v1/files`：上传 DOCX/TXT 并同步处理。
- `GET /api/v1/files`：查询处理清单，支持文件名、格式、分级、处理状态、复检状态筛选。
- `GET /api/v1/files/{id}`：查询文件详情。
- `POST /api/v1/files/{id}/process`：重新处理已上传文件。
- `GET /api/v1/files/{id}/preview/original`：原文文本预览。
- `GET /api/v1/files/{id}/preview/masked`：脱敏后文本预览。
- `GET /api/v1/files/{id}/entities`：实体摘要列表。
- `GET /api/v1/files/{id}/download`：下载脱敏文件。
- `DELETE /api/v1/files/{id}`：删除任务和本地文件。
- `GET /api/v1/exports/manifest.csv`：导出 UTF-8 BOM CSV。
- `GET /api/v1/exports/results.zip`：导出包含清单和脱敏文件的 ZIP。
- `GET /api/v1/health`：健康检查。

