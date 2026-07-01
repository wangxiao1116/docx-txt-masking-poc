# API 服务

FastAPI 后端负责文件上传、真实处理链路编排、SQLite 记录、预览、下载、CSV 和 ZIP 导出。

## 启动

```powershell
pip install -r requirements.txt
$env:PYTHONPATH = (Get-Location).Path
python -m uvicorn app.main:app --reload --port 8000
```

## 测试

```powershell
cd ../..
python -m pytest
```

## 入口

- `app/main.py`：FastAPI 应用。
- `app/api/routes.py`：API 路由。
- `app/services/processing_service.py`：处理编排，复用 `packages/poc-core`。
- `app/models/file_task.py`：SQLite 数据模型。

