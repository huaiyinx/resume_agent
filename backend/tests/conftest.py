"""pytest 全局配置。

提供测试用临时数据库 fixture 与应用配置隔离。
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def _isolated_env(
    tmp_path_factory: pytest.TempPathFactory, monkeypatch: pytest.MonkeyPatch
) -> Iterator[None]:
    """隔离测试环境：将所有数据存储重定向到临时目录。

    避免测试污染用户真实的 ``~/.resume-agent/`` 数据。
    """
    tmp_home = tmp_path_factory.mktemp("resume-agent-home")
    monkeypatch.setenv("RESUME_AGENT_HOME", str(tmp_home))
    monkeypatch.setenv("SQLITE_PATH", str(tmp_home / "data.db"))
    monkeypatch.setenv("CHROMA_PATH", str(tmp_home / "chroma"))
    monkeypatch.setenv("FILES_ROOT", str(tmp_home / "files"))
    # 重置 settings 单例，使其读取新的环境变量
    from resume_agent import config as config_module

    config_module.settings = config_module.Settings()
    yield


@pytest.fixture
def tmp_db_path(tmp_path: Path) -> Path:
    """提供一个临时数据库路径。"""
    return tmp_path / "test_data.db"


@pytest.fixture
def initialized_db(tmp_db_path: Path) -> Path:
    """初始化一个临时数据库并返回路径。"""
    from resume_agent.db.init_db import init_database

    init_database(tmp_db_path)
    return tmp_db_path
