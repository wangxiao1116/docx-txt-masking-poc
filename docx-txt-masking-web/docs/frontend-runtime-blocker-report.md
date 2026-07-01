# 前端运行环境阻塞报告

## 现象

在当前本机 Windows 环境中，前端依赖安装和运行无法稳定完成：

- `npm install` / `npm ci` 多次长时间挂起，超时后留下不完整 `node_modules`。
- 失败安装产物曾出现缺少 `.bin`、缺少 `next` 类型文件、缺少 Next 运行文件的问题。
- `@next/swc-win32-x64-msvc` 原生模块加载时报错：`not a valid Win32 application`。
- 早期失败安装产物中的 `esbuild.exe` 也曾出现同类 Win32 加载错误。

## 当前运行环境

- Shell：Windows PowerShell 5.1。
- OS：Windows x64。
- 原始 Node 路径：`D:\01 setup\AI\node.js\node.exe`。
- 原始 npm 路径：`D:\01 setup\AI\node.js\npm.cmd`。
- 原始版本：Node `v24.16.0`，npm `11.13.0`，平台 `win32 x64`。

调试中额外验证过官方 Windows x64 便携 Node：

- Node `v24.16.0` / npm `11.13.0` 可启动。
- Node `v22.22.0` / npm `10.9.4` 可启动。

## 已排除

- WSL 与 Windows 交叉安装：当前 WSL 不可用，未发现可复用的 WSL `node_modules`。
- x86、ARM64、x64 架构混用：OS、PowerShell 进程、Node 进程均为 x64。
- `node_modules` 跨环境复用：每次验证前均删除了 `apps/web/node_modules`。
- 单纯 Next 版本问题：Next 15.5.x 和 15.1.x 的 Windows x64 SWC 原生模块均无法加载。
- Node 24 单版本 ABI 问题：官方 Node 22 LTS 也无法加载同一个 Next SWC 原生模块。
- 纯网络不可达：`npm pack next@15.1.0` 可以下载 tarball。
- 全部原生模块不可用：`sharp` 原生模块可以加载，`esbuild` 在一次完整安装后可运行。

## 已验证

- 官方 Windows x64 Node 22/24 可启动。
- esbuild 在完整安装产物中可运行。
- sharp 原生模块可加载。
- Next SWC 原生模块无法加载。
- npm/Yarn 安装过程在当前机器无法稳定正常结束。

## 根因结论

当前 Windows 机器不能作为可靠的前端验收环境。问题集中在本机 Node 包管理器安装链路和 Next SWC Windows 原生模块加载链路，而不是业务源码、WSL 混用或架构混用。

## 修复步骤

本机不再继续尝试新的包管理器、Node 版本或 Next 版本。后续验证路径固定为 Ubuntu CI：

1. 使用 Node.js 22 LTS。
2. 执行 `npm ci`。
3. 执行 `npm run lint`。
4. 执行 `npm run build`。
5. 启动 FastAPI。
6. 启动 Next.js。
7. 执行 Playwright 真实端到端测试。
8. 上传测试报告和截图。

注意：当前本机未生成可提交的 `package-lock.json`，因为本机 npm/Yarn 安装过程无法稳定结束。CI 已配置为使用 `npm ci`，但需要在可靠的 Ubuntu/Node 22 环境中生成并提交 lockfile 后，CI 前端构建和端到端验收才可能通过。

## 防止复发

- 固定 `.nvmrc` 和 `.node-version` 为 Node 22 LTS。
- README 明确禁止 Windows/WSL 交叉复用 `node_modules`。
- `.gitignore` 忽略 `node_modules/`、`.next/`、`.local-tools/`、日志、缓存和运行时文件。
- 前端 Gate 只允许通过 CI 前端构建与端到端验收关闭。

## 当前 Gate 结论

高保真 Web 产品工程 Gate：Conditional Pass。

前端源码已生成，后端真实链路和 Python 测试通过；但本机前端构建、运行和浏览器端到端验收未通过，必须转由 CI 完成验证。
