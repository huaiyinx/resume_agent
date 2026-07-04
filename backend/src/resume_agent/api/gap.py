"""Gap 报告端点（桩实现）。

对比简历与 JD，生成技能差距报告。
"""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from resume_agent.api.response import success

router = APIRouter(prefix="/gap-report", tags=["gap"])


class GapRequest(BaseModel):
    """Gap 报告请求体。"""

    resume_node_id: str
    jd_analysis_id: str


@router.post("")
def generate_gap_report(req: GapRequest) -> dict[str, Any]:
    """生成 Gap 报告（桩实现）。

    Args:
        req: Gap 报告请求，含简历节点 ID 与 JD 分析 ID。

    Returns:
        统一响应 envelope，``data`` 为 mock Gap 报告。
    """
    mock_report = {
        "report_id": str(uuid.uuid4()),
        "resume_node_id": req.resume_node_id,
        "jd_analysis_id": req.jd_analysis_id,
        "matched": ["Python", "PostgreSQL", "系统设计"],
        "gaps": [
            {"skill": "PyTorch", "severity": "high", "suggestion": "补充模型训练项目经验"},
            {"skill": "Spark", "severity": "medium", "suggestion": "学习分布式数据处理"},
        ],
        "overall_score": 72,
    }
    return success(mock_report)
