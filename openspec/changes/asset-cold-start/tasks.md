# Tasks: asset-cold-start

## 依赖添加
- [ ] 在 backend/pyproject.toml 添加 PyMuPDF, python-docx, openai 依赖
- [ ] `uv sync --extra dev` 安装

## 后端 — LLM Client
- [ ] 创建 `llm/__init__.py` 和 `llm/client.py`
- [ ] 实现 LLMClient 类（基于 openai SDK，支持 base_url）
- [ ] 测试：mock openai SDK，验证 chat 方法调用参数

## 后端 — 文件解析器
- [ ] 创建 `parsers/pdf_parser.py`（PyMuPDF 提取文本）
- [ ] 创建 `parsers/docx_parser.py`（python-docx 提取文本）
- [ ] 测试：创建测试 PDF，验证文本提取
- [ ] 测试：创建测试 DOCX，验证文本提取

## 后端 — 结构化提取器
- [ ] 创建 `parsers/extractor.py`（ResumeExtractor 类）
- [ ] 定义 StructuredResume Pydantic 模型
- [ ] 编写提取 prompt（system + user）
- [ ] 测试：mock LLMClient，验证提取结果解析

## 后端 — TreeBuilder
- [ ] 创建 `services/__init__.py` 和 `services/tree_builder.py`
- [ ] 实现 build_from_resume 方法
- [ ] 测试：空 DB → 创建 branch + company 节点
- [ ] 测试：已有 company 节点 → 去重更新

## 后端 — API 实现
- [ ] 改造 `api/resumes.py`：upload 保存文件+写 DB
- [ ] 改造 `api/resumes.py`：parse 调用解析器+提取器+TreeBuilder
- [ ] 新增 `api/resumes.py`：GET /list 端点
- [ ] 改造 `api/tree.py`：从 DB 读取替代 mock
- [ ] 测试：upload 集成测试
- [ ] 测试：parse 集成测试（mock LLM）
- [ ] 测试：tree 集成测试

## 前端 — API 层
- [ ] `lib/api.ts` 新增 uploadResume, parseResume, getTree, getResumeList

## 前端 — UploadZone
- [ ] 添加文件输入和拖拽处理
- [ ] 调用上传+解析 API
- [ ] 显示上传/解析进度状态
- [ ] 成功后触发版本树刷新

## 前端 — VersionTree
- [ ] 从 API 获取数据替代 mockTree
- [ ] 添加刷新机制

## 验证
- [ ] 后端 `uv run pytest` 全通过
- [ ] 后端 `uv run ruff check .` 零错误
- [ ] 前端 `tsc --noEmit` 零错误
- [ ] 前端 `vite build` 成功
