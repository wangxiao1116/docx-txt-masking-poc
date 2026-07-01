# Codex执行指令：生成高保真可交互 DOCX/TXT 脱敏验证 Web 产品工程

## 一、任务目标

请基于当前已经验证通过的 `docx_txt_masking_poc` 工程，生成一个可推送至 GitHub、可本地运行、可部署演示、可供客户验证业务场景的高保真 Web 产品工程。

目标业务闭环：

已标注 DOCX/TXT 文件上传  
→ 人工填写分类编码、分类名称、分级标签、备注  
→ 文件解析  
→ 敏感实体提取（当前先支持身份证号码，保留扩展接口）  
→ 基于敏感实体创建脱敏任务  
→ 调用遮蔽算法生成遮蔽结果  
→ 生成原值—遮蔽值映射  
→ 文件内容替换与重建  
→ 分类分级标签作为任务元数据保存  
→ 输出结果复检  
→ 文件进入处理清单  
→ 单文件预览、下载  
→ 导出处理清单 CSV  
→ 打包下载全部脱敏文件 ZIP

本次不是继续修改 Streamlit 页面，而是形成前后端分离、可持续扩展的产品工程。

---

## 二、推荐技术栈

采用以下固定技术栈，不得随意更换：

### 前端
- Next.js 15+
- TypeScript
- App Router
- Tailwind CSS
- shadcn/ui
- TanStack Table
- React Hook Form
- Zod
- Lucide Icons
- 支持桌面端优先，兼容 1440×900、1920×1080
- 页面语言：中文

### 后端
- Python 3.11+
- FastAPI
- Pydantic v2
- SQLAlchemy
- SQLite（本轮客户验证）
- Uvicorn
- pytest
- 复用现有 Python PoC 的：
  - `entity_extractor.py`
  - `masking.py`
  - `processors.py`
  - `verification.py`
  - `models.py`
  - `docx_metadata.py`

### 工程与交付
- Monorepo
- Docker Compose
- `.env.example`
- GitHub Actions
- README
- API 文档
- 自动测试
- 示例文件
- 一键启动脚本

---

## 三、必须遵守的边界

1. 不重写已验证通过的核心脱敏算法和文件处理逻辑，只进行适配封装。
2. 当前仅支持：
   - DOCX
   - TXT
   - 身份证号码敏感实体
   - 身份证遮蔽
3. 不实现自动分类分级。
4. 分类、分级由用户在上传时人工填写。
5. DOCX 分类分级标签不得写入正文。
6. 分类分级标签作为文件任务元数据保存在数据库，并在页面、清单、CSV、JSON 中展示。
7. TXT 不强制把标签写入正文，避免改变文件业务内容。
8. 无敏感实体时：
   - 状态显示“未发现敏感实体”
   - 复检状态显示“未通过”
   - 不得显示“处理成功”
9. 不记录身份证原值到普通日志。
10. 不使用真实客户敏感文件作为 GitHub 示例数据。
11. 本工程定位为客户验证版本，不得宣称生产可用。

---

## 四、仓库目录结构

在当前仓库中创建：

```text
docx-txt-masking-web/
├─ apps/
│  ├─ web/
│  │  ├─ app/
│  │  ├─ components/
│  │  ├─ lib/
│  │  ├─ types/
│  │  ├─ public/
│  │  ├─ package.json
│  │  └─ README.md
│  └─ api/
│     ├─ app/
│     │  ├─ api/
│     │  ├─ core/
│     │  ├─ db/
│     │  ├─ models/
│     │  ├─ schemas/
│     │  ├─ services/
│     │  └─ main.py
│     ├─ tests/
│     ├─ requirements.txt
│     └─ README.md
├─ packages/
│  └─ poc-core/
│     ├─ entity_extractor.py
│     ├─ masking.py
│     ├─ processors.py
│     ├─ verification.py
│     ├─ models.py
│     └─ docx_metadata.py
├─ sample-data/
│  ├─ sample_labeled.docx
│  └─ sample_labeled.txt
├─ storage/
│  ├─ originals/
│  ├─ outputs/
│  └─ exports/
├─ docs/
│  ├─ architecture.md
│  ├─ api-contract.md
│  ├─ acceptance-checklist.md
│  └─ customer-demo-guide.md
├─ .github/workflows/
├─ docker-compose.yml
├─ .env.example
├─ .gitignore
├─ README.md
└─ AGENTS.md
```

`storage/` 下只保留 `.gitkeep`，不得提交用户上传文件。

---

## 五、页面与交互设计

### 1. 产品工作台首页 `/`

页面采用企业级数据安全产品风格：

- 左侧深色导航栏
- 顶部产品名称与环境标识
- 主区使用卡片、表格、抽屉、步骤条
- 主色偏蓝，状态色规范：
  - 成功：绿色
  - 处理中：蓝色
  - 部分成功：橙色
  - 失败：红色
  - 未发现实体：灰色
- 不使用夸张渐变和营销风格
- 高密度但清晰
- 支持键盘操作和基础无障碍

顶部概览卡：

- 已上传文件数
- 已处理文件数
- 提取敏感实体数
- 已处理敏感实体数
- 复检通过文件数

主区包含：

#### 上传区

字段：

- 文件：DOCX/TXT，单次一个
- 分类编码
- 分类名称
- 分级标签
- 备注

按钮：

- 上传并创建任务
- 清空

交互：

1. 上传后显示文件名、大小、格式。
2. 分类编码、分类名称不能为空。
3. 文件上传成功后创建任务记录。
4. 可继续上传下一个文件。
5. 上传时显示进度和错误原因。

#### 处理清单

字段：

- 文件名
- 格式
- 分类编码
- 分类名称
- 分级标签
- 敏感实体数量
- 已处理实体数量
- 未处理实体数量
- 处理状态
- 复检状态
- 上传时间
- 操作

支持：

- 搜索文件名
- 按格式筛选
- 按分级筛选
- 按处理状态筛选
- 按复检状态筛选
- 分页
- 刷新
- 删除记录
- 查看详情
- 下载脱敏文件

#### 文件详情抽屉或详情页 `/files/[id]`

必须展示：

- 文件基础信息
- 人工分类分级标签
- 处理时间线
- 原文文本预览
- 脱敏后文本预览
- 敏感实体清单
- 原值—遮蔽值映射
- 复检结果
- 下载按钮

敏感实体原值默认遮蔽显示，不得在列表中直接完整展示。提供“显示原值”开关时，要增加二次确认提示。

#### 导出区

按钮：

- 导出处理清单 CSV
- 打包下载全部脱敏文件 ZIP

ZIP必须包含：

```text
处理清单.csv
脱敏文件/
  xxx_masked.docx
  xxx_masked.txt
```

---

## 六、后端数据模型

至少实现以下表：

### `file_tasks`

字段：

- id
- original_file_name
- stored_original_path
- stored_output_path
- file_type
- file_size
- category_code
- category_name
- level
- label_source
- note
- entity_count
- processed_entity_count
- unprocessed_entity_count
- process_status
- verification_status
- error_message
- created_at
- updated_at

### `sensitive_entities`

字段：

- id
- file_task_id
- entity_type
- masked_original_value
- masked_value
- location
- extractor
- format_valid
- checksum_valid
- processed
- created_at

禁止在数据库中保存身份证完整原值。仅允许：

- 内存处理中短暂使用
- 数据库存储掩码后的原值
- 映射结果存储遮蔽值

---

## 七、API设计

实现以下接口：

```text
POST   /api/v1/files
GET    /api/v1/files
GET    /api/v1/files/{id}
POST   /api/v1/files/{id}/process
GET    /api/v1/files/{id}/preview/original
GET    /api/v1/files/{id}/preview/masked
GET    /api/v1/files/{id}/entities
GET    /api/v1/files/{id}/download
DELETE /api/v1/files/{id}
GET    /api/v1/exports/manifest.csv
GET    /api/v1/exports/results.zip
GET    /api/v1/health
```

### 上传接口

`POST /api/v1/files`

使用 `multipart/form-data`：

- file
- category_code
- category_name
- level
- note

上传完成后可同步触发处理，或创建任务后立即处理。本轮优先采用同步处理，但前端必须显示：

- 上传中
- 解析中
- 提取实体
- 执行遮蔽
- 文件重建
- 输出复检
- 完成

后端返回统一格式：

```json
{
  "code": 0,
  "message": "success",
  "data": {}
}
```

异常返回：

```json
{
  "code": 40001,
  "message": "文件格式不支持",
  "data": null
}
```

---

## 八、处理服务编排

新增 `processing_service.py`，只负责串联，不重写核心算法：

```text
保存原文件
→ 调用 processors.process_file
→ 获取 entities
→ 获取 mappings
→ 调用 verification.verify_output
→ 保存脱敏文件
→ 保存任务摘要
→ 保存实体摘要
→ 返回任务结果
```

必须处理：

- DOCX损坏
- TXT编码无法识别
- 文件无扩展名
- 文件格式不支持
- 文件为空
- 文件过大
- 无敏感实体
- 输出文件无法打开
- 原值残留
- 标签元数据缺失

---

## 九、文件安全与限制

实现以下限制：

- 仅允许 `.docx`、`.txt`
- 最大文件大小默认 20MB，可配置
- 文件名清洗，防止路径穿越
- 上传文件使用 UUID 存储
- 原文件与输出文件分目录
- 删除记录时同步删除本地文件
- 日志不得打印文件正文、身份证原值
- Git仓库不得提交 storage 中的实际文件

---

## 十、自动测试

### 后端测试

至少覆盖：

1. DOCX上传与处理成功
2. TXT上传与处理成功
3. 身份证实体提取
4. 身份证遮蔽
5. 跨Run身份证处理
6. 无实体文件状态
7. CSV导出
8. ZIP导出
9. 文件下载
10. 删除任务
11. 不支持格式拒绝
12. 标签元数据保存
13. DOCX正文不出现可见分类分级标签
14. 数据库不保存身份证完整原值

### 前端测试

至少覆盖：

1. 上传表单校验
2. 创建任务
3. 清单加载
4. 筛选
5. 查看详情
6. 单文件下载
7. CSV导出
8. ZIP导出
9. 无实体状态展示
10. 错误提示

---

## 十一、GitHub与工程要求

### `.gitignore`

必须忽略：

```text
.venv/
node_modules/
.next/
__pycache__/
.pytest_cache/
storage/originals/*
storage/outputs/*
storage/exports/*
*.db
.env
```

### GitHub Actions

实现：

- 前端 lint
- 前端 build
- 后端 pytest
- Docker build

### README必须包含

- 产品目标
- 技术架构
- 页面截图位置
- 本地启动方式
- Docker启动方式
- 测试命令
- 客户验证步骤
- 已知限制
- 隐私与安全说明
- GitHub推送步骤

---

## 十二、本地启动命令

最终必须支持：

```powershell
docker compose up --build
```

前端：

```text
http://localhost:3000
```

后端：

```text
http://localhost:8000
```

API文档：

```text
http://localhost:8000/docs
```

同时保留非Docker启动方式。

---

## 十三、客户验证脚本

在 `docs/customer-demo-guide.md` 中写明：

1. 上传包含身份证号码的 DOCX
2. 填写分类编码、分类名称、分级标签
3. 执行处理
4. 在清单查看实体数量和处理数量
5. 打开详情查看原文和脱敏后文本
6. 下载脱敏文件
7. 用 Word 打开并确认文件可用
8. 上传 TXT 重复验证
9. 导出 CSV
10. 打包下载 ZIP
11. 验证无身份证文件状态

---

## 十四、验收标准

必须全部满足：

1. 连续处理至少10个文件，记录不串。
2. DOCX/TXT均可上传、处理、下载。
3. 身份证实体数量准确。
4. 处理实体数量准确。
5. 原身份证值无残留。
6. DOCX输出可打开。
7. TXT输出编码正常。
8. 分类分级在页面、详情、CSV中可见。
9. DOCX正文顶部不新增分类分级文字。
10. 单文件可预览、可下载。
11. CSV可导出。
12. ZIP包含清单和全部脱敏文件。
13. 无敏感实体文件状态正确。
14. 前后端测试通过。
15. Docker Compose一键启动成功。
16. GitHub Actions通过。

---

## 十五、执行顺序

请严格按以下顺序执行：

1. 审计当前PoC代码和测试。
2. 输出迁移方案。
3. 创建新分支：
   `feature/high-fidelity-web-poc`
4. 创建Monorepo结构。
5. 迁移并封装PoC核心代码。
6. 完成后端API。
7. 完成数据库与文件存储。
8. 完成前端高保真页面。
9. 完成预览、下载、CSV、ZIP。
10. 完成自动测试。
11. 完成Docker Compose。
12. 完成GitHub Actions。
13. 完成README与客户验证文档。
14. 运行全部测试。
15. 启动系统并执行完整客户验证脚本。
16. 输出最终报告。

---

## 十六、Codex最终输出格式

执行完成后必须输出：

1. 新增和修改文件清单
2. 技术架构说明
3. 复用的PoC能力
4. 新增的产品能力
5. 自动测试结果
6. 前端访问地址
7. 后端访问地址
8. Docker启动结果
9. 客户验证步骤
10. 已知限制
11. Git状态
12. 建议提交信息

建议提交信息：

```text
feat: build high fidelity docx txt masking validation web app
```

不要只生成静态页面。必须保证：

- 页面可交互
- 文件可上传
- 后端真实处理
- 输出文件可下载
- 清单可导出
- 全链路可验证
