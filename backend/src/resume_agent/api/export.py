"""PDF 导出端点（桩实现）。

将指定简历节点导出为 PDF。
"""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from resume_agent.api.response import success

router = APIRouter(prefix="/export", tags=["export"])


class ExportRequest(BaseModel):
    """PDF 导出请求体。"""

    resume_node_id: str
    template: str = "modern"  # modern / classic / minimal


@router.post("/pdf")
def export_pdf(req: ExportRequest) -> dict[str, Any]:
    """导出简历为 PDF（桩实现）。

    Args:
        req: 导出请求，含简历节点 ID 与模板名。

    Returns:
        统一响应 envelope，``data`` 为 mock 导出结果。
    """
    mock_export = {
        "export_id": str(uuid.uuid4()),
        "resume_node_id": req.resume_node_id,
        "template": req.template,
        "file_path": f"files/exports/{uuid.uuid4()}.pdf",
        "status": "completed",
    }
    return success(mock_export)
