# 架构说明

## 总体结构

工程采用 monorepo：

- `apps/web`：Next.js 前端。
- `apps/api`：FastAPI 后端。
- `packages/poc-core`：迁移自原 PoC 的核心处理能力。
- `storage`：本地文件和 SQLite 存储目录。

## 数据流

1. 前端提交 `multipart/form-data` 到 `POST /api/v1/files`。
2. 后端校验扩展名、文件大小和人工分类字段。
3. 原文以 UUID 文件名保存到 `storage/originals`。
4. `processing_service.py` 调用 `processors.process_file`。
5. 核心模块完成身份证提取、遮蔽、DOCX/TXT 重建和 DOCX 自定义属性写入。
6. 后端调用 `verification.verify_output` 复检输出。
7. 脱敏文件保存到 `storage/outputs`。
8. SQLite 保存任务摘要、分类分级元数据、复检结果和实体摘要。
9. 前端刷新清单并支持详情、预览、下载和导出。

## 安全边界

- 数据库不保存完整身份证原值。
- 日志不输出文件正文或身份证原值。
- 上传文件名只用于展示，实际存储使用 UUID。
- 删除记录时同步删除原文和输出文件。

## 前端运行环境

- 推荐 Node.js 22 LTS。
- Windows 原生和 WSL/Linux 必须二选一，不得复用同一个 `node_modules`。
- 当前本机 Windows 前端运行环境存在 SWC/npm 安装阻塞，前端 Gate 以 Ubuntu CI 为准。
- CI 固定执行 `npm ci`、`npm run lint`、`npm run build` 和 Playwright 端到端测试。
