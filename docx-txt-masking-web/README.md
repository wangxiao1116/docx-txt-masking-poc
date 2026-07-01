# DOCX/TXT 脱敏验证 Web 产品工程

客户验证版 Web PoC，用于演示 DOCX/TXT 文件上传、人工分类分级、身份证实体提取、遮蔽、文件重建、输出复检、清单导出和 ZIP 打包下载的完整链路。

## 技术架构

- 前端：Next.js 15、TypeScript、App Router、Tailwind CSS、shadcn 风格组件、TanStack Table、React Hook Form、Zod、Lucide Icons。
- 后端：FastAPI、Pydantic v2、SQLAlchemy、SQLite、Uvicorn、pytest。
- 核心能力：复用 `packages/poc-core` 中已验证的 DOCX/TXT 处理、身份证提取、遮蔽、复检和 DOCX 自定义属性写入逻辑。
- 存储：SQLite 保存任务和实体摘要；`storage/originals` 保存原文文件；`storage/outputs` 保存脱敏文件；`storage/exports` 预留导出目录。

## 页面截图位置

本地启动后访问：

- 前端工作台：`http://localhost:3000`
- 后端 API 文档：`http://localhost:8000/docs`

页面包含左侧深色导航、指标卡、上传区、筛选表格、详情页、预览、实体、映射、复检和导出操作。

## 本地启动

推荐 Node.js 环境：

- Node.js 22 LTS。
- npm 10.x。
- Windows 原生或 WSL/Linux 必须二选一。
- 禁止跨环境复用 `apps/web/node_modules`。

后端：

```powershell
cd docx-txt-masking-web/apps/api
$env:PYTHONPATH = (Get-Location).Path
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

前端：

```powershell
cd docx-txt-masking-web/apps/web
npm install
$env:NEXT_PUBLIC_API_BASE_URL = "http://localhost:8000/api/v1"
npm run dev
```

也可以使用：

```powershell
.\scripts-start.ps1
```

## Docker 启动

```powershell
docker compose up --build
```

- 前端：`http://localhost:3000`
- 后端：`http://localhost:8000`
- API 文档：`http://localhost:8000/docs`

## 测试命令

```powershell
python -m pytest
cd apps/web
npm run lint
npm run build
```

当前本机 Windows 前端运行环境存在阻塞，详见 [docs/frontend-runtime-blocker-report.md](docs/frontend-runtime-blocker-report.md)。前端构建和端到端验收以 Ubuntu CI 为准。

## 客户验证步骤

见 [docs/customer-demo-guide.md](docs/customer-demo-guide.md)。

## 隐私与安全说明

- 数据库不保存完整身份证原值，只保存掩码后的原值摘要和遮蔽值。
- 不记录文件正文和身份证原值到日志。
- 上传文件使用 UUID 文件名存储，避免路径穿越。
- 删除任务时同步删除本地原文和脱敏文件。
- `storage/` 下实际文件不进入 Git。

## 已知限制

- 仅支持 DOCX/TXT。
- 仅支持身份证号码实体和身份证遮蔽。
- 不实现自动分类分级。
- DOCX 预览是文本抽取预览，不是 Word 版式渲染。
- SQLite 和本地文件存储仅用于客户验证版。
- 当前 Gate 为 Conditional Pass，前端仍需 CI 构建和 Playwright 端到端验收。

## GitHub 推送步骤

```powershell
git status
git add docx-txt-masking-web
git commit -m "feat: build high fidelity docx txt masking validation web app"
git push origin feature/high-fidelity-web-poc
```
