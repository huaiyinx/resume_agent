"""AI 生成端点（桩实现）。

根据简历节点、JD 分析、知识库检索结果生成简历内容。
"""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from resume_agent.api.response import success

router = APIRouter(prefix="/generate", tags=["generate"])


class GenerateRequest(BaseModel):
    """AI 生成请求体。"""

    resume_node_id: str
    jd_analysis_id: str
    gap_report_id: str | None = None
    section: str = "experience"  # basic / education / experience / projects / skills


@router.post("")
def generate(req: GenerateRequest) -> dict[str, Any]:
    """AI 生成简历内容（桩实现）。

    Args:
        req: 生成请求，含简历节点 ID、JD 分析 ID、目标段落。

    Returns:
        统一响应 envelope，``data`` 为 mock 生成结果。
    """
    mock_generated = {
        "generation_id": str(uuid.uuid4()),
        "resume_node_id": req.resume_node_id,
        "section": req.section,
        "content": {
            "experience": [
                {
                    "company": "某公司",
                    "role": "推荐算法工程师",
                    "period": "2021-至今",
                    "highlights": [
                        "主导推荐召回模型升级，离线 AUC 提升 2%",
                        "设计分布式训练 pipeline，日均处理 10 亿条样本",
                    ],
                }
            ]
        }
        if req.section == "experience"
        else {"text": f"已生成 {req.section} 段落内容（mock）"},
        "tokens_used": 1024,
    }
    return success(mock_generated)
