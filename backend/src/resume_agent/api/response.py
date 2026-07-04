"""统一响应格式辅助工具。

所有 API 端点返回 ``{"ok": bool, "data": ..., "error": ...}`` envelope。
对齐 design.md 第 5.4 节。
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class ErrorDetail(BaseModel):
    """错误详情。"""

    code: str
    message: str


class ApiResponse(BaseModel):
    """统一响应 envelope。"""

    ok: bool
    data: Any = None
    error: ErrorDetail | None = None


def success(data: Any = None) -> dict[str, Any]:
    """构造成功响应。

    Args:
        data: 业务数据，默认为 ``None``。

    Returns:
        ``{"ok": true, "data": ..., "error": null}`` 字典。
    """
    return {"ok": True, "data": data, "error": None}


def error(code: str, message: str) -> dict[str, Any]:
    """构造错误响应。

    Args:
        code: 错误码（如 ``"PARSE_FAILED"``）。
        message: 人类可读的错误信息。

    Returns:
        ``{"ok": false, "data": null, "error": {"code": ..., "message": ...}}`` 字典。
    """
    return {"ok": False, "data": None, "error": {"code": code, "message": message}}
