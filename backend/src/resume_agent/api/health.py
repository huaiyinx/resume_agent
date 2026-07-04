"""健康检查端点（完整实现）。

对齐 design.md 第 5.2 节：返回应用状态、数据库与 Chroma 就绪状态、LLM 配置状态、
版本树节点数。
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from resume_agent import __version__
from resume_agent.api.response import success
from resume_agent.config import settings
from resume_agent.db.init_db import count_nodes
from resume_agent.rag.chroma_client import is_chroma_ready

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, Any]:
    """健康检查端点。

    返回应用运行状态、数据库/向量库就绪状态、LLM 配置状态、版本树节点数。

    Returns:
        统一响应 envelope，``data`` 字段为健康状态字典。
    """
    data = {
        "status": "ok",
        "version": f"{__version__}-mvp",
        "db": "ready",
        "chroma": "ready" if is_chroma_ready() else "unavailable",
        "llm_configured": settings.llm_configured,
        "node_count": count_nodes(),
    }
    return success(data)
