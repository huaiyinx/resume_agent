"""SQLite 连接管理。

使用原生 ``sqlite3`` 模块，启用外键约束，提供上下文管理器与行工厂。
"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any


def _row_to_dict(cursor: sqlite3.Cursor, row: tuple[Any, ...]) -> dict[str, Any]:
    """将行转换为字典，键为列名。"""
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}


@contextmanager
def get_connection(db_path: Path | str | None = None) -> Iterator[sqlite3.Connection]:
    """获取 SQLite 连接的上下文管理器。

    Args:
        db_path: 数据库路径，默认使用 ``settings.sqlite_path``。

    Yields:
        ``sqlite3.Connection`` 实例，退出上下文时自动提交并关闭。

    Note:
        - 启用 ``PRAGMA foreign_keys = ON`` 以支持外键级联删除。
        - 启用 ``row_factory`` 让查询结果以字典形式返回。
        - 延迟导入 ``settings`` 以兼容测试期 ``config_module.settings`` 重置。
    """
    if db_path is None:
        # 延迟导入：测试期 conftest 会重置 config 模块的 settings 单例，
        # 此处每次调用都读取最新引用，避免持有过期实例。
        from resume_agent.config import settings

        db_path = settings.sqlite_path
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(path))
    conn.row_factory = _row_to_dict
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
