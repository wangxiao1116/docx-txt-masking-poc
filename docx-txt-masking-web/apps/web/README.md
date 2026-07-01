# Web 前端

Next.js 15 前端工作台，通过 `NEXT_PUBLIC_API_BASE_URL` 调用 FastAPI，不使用 Mock 数据。

推荐 Node.js 22 LTS。不要在 Windows 与 WSL/Linux 之间复用 `node_modules`。

## 启动

```powershell
npm install
$env:NEXT_PUBLIC_API_BASE_URL = "http://localhost:8000/api/v1"
npm run dev
```

当前本机 Windows 前端依赖安装和 SWC 原生模块加载存在环境阻塞，前端 Gate 以 Ubuntu CI 的 `npm ci`、`npm run lint`、`npm run build` 和 Playwright 验收为准。

## 页面

- `/`：上传区、指标卡、处理清单、筛选、单文件下载、CSV/ZIP 导出。
- `/files/[id]`：文件详情、原文和脱敏预览、实体、映射、复检、下载。
