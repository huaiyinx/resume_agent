"""版本树端点。

从 ``resume_versions`` 表读取所有节点，构建 nodes + edges 数组返回。
对齐 design.md 第 3.4 节。

edges 逻辑：每个有 ``parent_id`` 的节点生成一条 ``{source: parent_id, target: node_id}``。
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from resume_agent.api.response import success
from resume_agent.db.connection import get_connection

router = APIRouter(prefix="/tree", tags=["tree"])


class CreateNodeRequest(BaseModel):
    """新建节点请求体。"""

    parent_id: str
    node_type: str  # master / branch / company
    title: str
    company: str | None = None
    direction: str | None = None


@router.get("")
def get_tree() -> dict[str, Any]:
    """获取版本树结构。

    从 ``resume_versions`` 表读取所有节点，构建 ``nodes`` 与 ``edges`` 数组。

    Returns:
        统一响应 envelope，``data`` 含 ``nodes`` 与 ``edges`` 数组。
        edges 由每个有 parent_id 的节点生成：``{source: parent_id, target: node_id}``。
    """
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, node_id, parent_id, node_type, title, company, direction,
                   content_json, created_at, updated_at
            FROM resume_versions
            ORDER BY created_at, node_id
            """
        ).fetchall()

    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, str]] = []
    for row in rows:
        node = {
            "id": row["id"],
            "node_id": row["node_id"],
            "parent_id": row["parent_id"],
            "node_type": row["node_type"],
            "title": row["title"],
            "company": row["company"],
            "direction": row["direction"],
            "content_json": row["content_json"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }
        nodes.append(node)
        if row["parent_id"]:
            edges.append({"source": row["parent_id"], "target": row["node_id"]})

    data = {"nodes": nodes, "edges": edges}
    return success(data)


@router.post("/node")
def create_node(req: CreateNodeRequest) -> dict[str, Any]:
    """新建版本树节点（桩实现，保留以兼容前端调用）。

    Args:
        req: 节点创建请求。

    Returns:
        统一响应 envelope，``data`` 为 mock 节点对象。
    """
    import uuid as uuid_lib

    mock_node = {
        "id": str(uuid_lib.uuid4()),
        "node_id": req.title.lower().replace(" ", "-"),
        "parent_id": req.parent_id,
        "node_type": req.node_type,
        "title": req.title,
        "company": req.company,
        "direction": req.direction,
    }
    return success(mock_node)
