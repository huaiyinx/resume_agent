"""JD 分析端点（桩实现）。

上传 JD 截图或文本，返回结构化提取结果。
"""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, UploadFile
from pydantic import BaseModel

from resume_agent.api.response import success

router = APIRouter(prefix="/jd", tags=["jd"])


class JDTextRequest(BaseModel):
    """JD 文本分析请求体。"""

    text: str


@router.post("/analyze")
async def analyze_jd(file: UploadFile | None = None) -> dict[str, Any]:
    """分析 JD（桩实现）。

    接受 JD 截图上传，返回 mock 结构化提取结果。

    Args:
        file: 上传的 JD 截图文件（可选）。

    Returns:
        统一响应 envelope，``data`` 为 mock JD 分析结果。
    """
    file_name = file.filename if file else "jd-screenshot.png"
    mock_analysis = {
        "analysis_id": str(uuid.uuid4()),
        "source": file_name,
        "job_title": "推荐算法工程师",
        "tech_stack": ["Python", "PyTorch", "Linux", "Spark"],
        "hard_skills": ["模型训练", "分布式系统", "特征工程"],
        "soft_skills": ["跨团队协作", "技术文档"],
        "bonus": ["顶会论文", "开源贡献", "竞赛获奖"],
    }
    return success(mock_analysis)


@router.post("/analyze-text")
def analyze_jd_text(req: JDTextRequest) -> dict[str, Any]:
    """分析 JD 文本（桩实现）。

    Args:
        req: JD 文本分析请求。

    Returns:
        统一响应 envelope，``data`` 为 mock JD 分析结果。
    """
    mock_analysis = {
        "analysis_id": str(uuid.uuid4()),
        "source": "text-input",
        "job_title": "后端工程师",
        "tech_stack": ["Go", "Kubernetes", "PostgreSQL"],
        "hard_skills": ["系统设计", "性能优化"],
        "soft_skills": ["沟通", "责任心"],
        "bonus": ["开源项目", "技术博客"],
    }
    return success(mock_analysis)
