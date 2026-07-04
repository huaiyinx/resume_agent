# === Stage 1: 前端构建 ===
FROM node:22-alpine AS frontend-build
WORKDIR /app/frontend
RUN corepack enable && corepack prepare pnpm@latest --activate
COPY frontend/package.json frontend/pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile
COPY frontend/ ./
RUN pnpm build

# === Stage 2: 后端运行时 ===
FROM python:3.12-slim AS runtime

# 安装 uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# 复制后端依赖文件并安装
COPY backend/pyproject.toml backend/uv.lock backend/README.md ./
RUN uv sync --frozen --no-dev

# 复制后端源码
COPY backend/src ./src

# 复制前端构建产物到 static/ 目录（FastAPI 静态托管）
COPY --from=frontend-build /app/frontend/dist ./static

# 环境变量
ENV RESUME_AGENT_HOME=/root/.resume-agent
ENV PYTHONUNBUFFERED=1

EXPOSE 5173

CMD ["uv", "run", "uvicorn", "resume_agent.main:app", "--host", "0.0.0.0", "--port", "5173"]
