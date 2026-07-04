"""import 冒烟测试。

验证所有关键模块可正常导入，捕获打包/路径配置问题。
"""

from __future__ import annotations


def test_import_top_level() -> None:
    """顶层包可导入。"""
    import resume_agent

    assert resume_agent.__version__ == "0.1.0"


def test_import_config() -> None:
    """配置模块可导入。"""
    from resume_agent.config import settings

    assert hasattr(settings, "sqlite_path")
    assert hasattr(settings, "chroma_path")
    assert hasattr(settings, "llm_configured")


def test_import_api_modules() -> None:
    """所有 API 路由模块可导入。"""
    from resume_agent.api import (
        export,
        gap,
        generate,
        health,
        jd,
        knowledge,
        resumes,
        tree,
    )
    from resume_agent.api.router import api_router

    assert api_router is not None
    assert health.router is not None
    assert tree.router is not None
    assert resumes.router is not None
    assert knowledge.router is not None
    assert jd.router is not None
    assert gap.router is not None
    assert generate.router is not None
    assert export.router is not None


def test_import_db_modules() -> None:
    """数据库模块可导入。"""
    from resume_agent.db.connection import get_connection
    from resume_agent.db.init_db import init_database

    assert callable(get_connection)
    assert callable(init_database)


def test_import_rag_modules() -> None:
    """RAG 模块可导入。"""
    from resume_agent.rag.chroma_client import get_chroma_client
    from resume_agent.rag.embeddings import EmbeddingProvider, OpenAIEmbedding

    assert callable(get_chroma_client)
    assert OpenAIEmbedding is not None
    assert issubclass(OpenAIEmbedding, EmbeddingProvider)


def test_import_main_app() -> None:
    """FastAPI 应用实例可创建。"""
    from resume_agent.main import app, create_app

    assert app is not None
    assert callable(create_app)
