"""版本树端点（桩实现）。

返回 mock 版本树结构，供前端联调。
对齐 design.md 第 5.3 节。
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from resume_agent.api.response import success

router = APIRouter(prefix="/tree", tags=["tree"])


# === Mock 数据 ===
MOCK_NODES: list[dict[str, Any]] = [
    {
        "id": "master",
        "node_id": "master",
        "parent_id": None,
        "node_type": "master",
        "title": "Master 主干",
        "company": None,
        "direction": None,
    },
    {
        "id": "branch-security",
        "node_id": "security",
        "parent_id": "master",
        "node_type": "branch",
        "title": "安全岗方向",
        "company": None,
        "direction": "安全",
    },
    {
        "id": "company-tencent-rs",
        "node_id": "tencent-researcher",
        "parent_id": "security",
        "node_type": "company",
        "title": "Tencent 安全研究员",
        "company": "Tencent",
        "direction": None,
    },
]

MOCK_EDGES: list[dict[str, str]] = [
    {"source": "master", "target": "security"},
    {"source": "security", "target": "tencent-researcher"},
]


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

    Returns:
        统一响应 envelope，``data`` 含 ``nodes`` 与 ``edges`` 数组。
    """
    data = {"nodes": MOCK_NODES, "edges": MOCK_EDGES}
    return success(data)


@router.post("/node")
def create_node(req: CreateNodeRequest) -> dict[str, Any]:
    """新建版本树节点（桩实现）。

    Args:
        req: 节点创建请求。

    Returns:
        统一响应 envelope，``data`` 为 mock 节点对象。
    """
    import uuid

    mock_node = {
        "id": str(uuid.uuid4()),
        "node_id": req.title.lower().replace(" ", "-"),
        "parent_id": req.parent_id,
        "node_type": req.node_type,
        "title": req.title,
        "company": req.company,
        "direction": req.direction,
    }
    return success(mock_node)
