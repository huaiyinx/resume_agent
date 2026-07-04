"""FastAPI 应用入口。

职责：
1. 创建 FastAPI 实例并注册中间件。
2. 启动时初始化 SQLite（建表）与 Chroma（PersistentClient）。
3. 挂载 ``/api`` 路由。
4. 静态托管前端 build 产物，并提供 SPA 兜底。

对齐 design.md 第 10.3 节。
"""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from resume_agent.api.router import api_router
from resume_agent.config import settings
from resume_agent.db.init_db import init_database
from resume_agent.rag.chroma_client import (
    get_knowledge_collection,
    get_resume_collection,
)

logger = logging.getLogger("resume_agent")


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """应用生命周期：启动时初始化数据库与向量库。"""
    logger.info("启动 Resume-Agent 后端 ...")
    # 1. 确保存储目录存在
    settings.ensure_dirs()
    # 2. SQLite 建表（幂等）
    init_database(settings.sqlite_path)
    logger.info("SQLite 初始化完成: %s", settings.sqlite_path)
    # 3. Chroma 初始化（创建客户端即触发目录创建与集合就绪）
    get_resume_collection()
    get_knowledge_collection()
    logger.info("Chroma 初始化完成: %s", settings.chroma_path)
    # 4. 确保文件目录存在
    settings.files_root.mkdir(parents=True, exist_ok=True)
    logger.info("文件目录就绪: %s", settings.files_root)
    yield
    logger.info("Resume-Agent 后端已停止")


def create_app() -> FastAPI:
    """构建 FastAPI 应用实例。

    Returns:
        配置好的 ``FastAPI`` 实例。
    """
    app = FastAPI(
        title="Resume-Agent",
        description="Resume-Agent MVP 后端：版本树、知识库 RAG、JD 分析、AI 生成。",
        version="0.1.0",
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # API 路由
    app.include_router(api_router, prefix="/api")

    # 静态文件托管前端 build 产物（生产态）
    static_dir = Path("static")
    assets_dir = static_dir / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

        @app.get("/{full_path:path}")
        async def spa_fallback(full_path: str) -> FileResponse:
            """SPA 兜底：所有非 /api 路径返回 index.html。

            Args:
                full_path: 请求路径。

            Returns:
                ``static/index.html`` 文件响应。
            """
            index_html = static_dir / "index.html"
            return FileResponse(index_html)

    return app


app = create_app()
