# 验收清单

- [x] DOCX/TXT 均可上传、处理、下载。
- [x] 身份证实体提取和遮蔽复用 PoC 核心能力。
- [x] DOCX 跨 Run 身份证可处理。
- [x] 原身份证值无残留。
- [x] DOCX 输出可打开。
- [x] DOCX 分类分级标签不写入正文。
- [x] 分类分级在页面、详情和 CSV 中可见。
- [x] 单文件可预览、可下载。
- [x] CSV 可导出。
- [x] ZIP 包含清单和脱敏文件。
- [x] 无敏感实体文件状态为“未发现敏感实体”，复检为“未通过”。
- [x] 数据库不保存完整身份证原值。
- [ ] 前端依赖安装、lint、生产构建需在 Ubuntu CI 验证。
- [ ] Playwright 真实端到端测试需在 Ubuntu CI 验证。
- [ ] Docker Compose 一键启动需在目标 Docker 环境验证。
- [ ] GitHub Actions 需推送后在 GitHub 环境验证。

## 2026-07-01 本机验收状态

- 后端 Python 测试通过。
- 后端真实 HTTP 上传、处理、预览、CSV、ZIP 链路已验证。
- 本机 Windows 前端运行环境阻塞，详见 `frontend-runtime-blocker-report.md`。
- 当前 Gate：Conditional Pass。
