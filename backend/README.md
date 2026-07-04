# Resume-Agent Backend

Resume-Agent MVP 后端，基于 FastAPI + SQLite + Chroma。

## 技术栈

- Python 3.12+
- FastAPI + uvicorn
- SQLite（原生 sqlite3，不使用 ORM）
- Chroma（嵌入式 PersistentClient）
- pydantic-settings 配置管理

## 快速开始

```bash
# 安装依赖
uv sync

# 启动开发服务器（端口 5173）
uv run uvicorn resume_agent.main:app --reload --port 5173

# 运行测试
uv run pytest

# Lint 检查
uv run ruff check .
```

## 目录结构

```
src/resume_agent/
├── main.py          # FastAPI 入口 + 静态托管
├── config.py        # 环境变量配置
├── api/             # 路由层
├── db/              # SQLite 数据库层
├── rag/             # Chroma 向量库 + Embedding
├── parsers/         # 简历解析器（骨架）
└── agents/          # LangGraph 工作流（骨架）
```

## 数据存储

所有数据默认落在 `~/.resume-agent/`：

- `data.db` — SQLite 元数据
- `chroma/` — Chroma 嵌入式向量库
- `files/` — 上传文件与生成产物
