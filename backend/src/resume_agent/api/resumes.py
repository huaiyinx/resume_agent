"""简历上传与解析端点（桩实现）。

返回 mock 记录与 mock 结构化简历，供前端联调。
"""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, UploadFile
from pydantic import BaseModel

from resume_agent.api.response import success

router = APIRouter(prefix="/resumes", tags=["resumes"])


class ParseRequest(BaseModel):
    """解析简历请求体。"""

    upload_id: str


@router.post("/upload")
async def upload_resume(file: UploadFile) -> dict[str, Any]:
    """上传简历文件（桩实现）。

    Args:
        file: 上传的文件对象。

    Returns:
        统一响应 envelope，``data`` 为 mock 上传记录。
    """
    file_ext = file.filename.rsplit(".", 1)[-1].lower() if file.filename else "pdf"
    mock_record = {
        "id": str(uuid.uuid4()),
        "file_name": file.filename or "resume.pdf",
        "file_type": file_ext,
        "file_path": f"files/resumes/{uuid.uuid4()}.{file_ext}",
        "parse_status": "pending",
    }
    return success(mock_record)


@router.post("/parse")
def parse_resume(req: ParseRequest) -> dict[str, Any]:
    """解析简历为结构化 JSON（桩实现）。

    Args:
        req: 解析请求，含上传记录 ID。

    Returns:
        统一响应 envelope，``data`` 为 mock 结构化简历。
    """
    mock_resume = {
        "upload_id": req.upload_id,
        "basic": {
            "name": "张三",
            "phone": "138****8888",
            "email": "zhangsan@example.com",
        },
        "education": [
            {
                "school": "某大学",
                "degree": "硕士",
                "major": "计算机科学",
                "period": "2018-2021",
            }
        ],
        "experience": [
            {
                "company": "某公司",
                "role": "后端工程师",
                "period": "2021-至今",
                "highlights": ["负责核心服务", "推动架构升级"],
            }
        ],
        "projects": [{"name": "示例项目", "role": "负责人", "description": "项目描述"}],
        "skills": ["Python", "FastAPI", "PostgreSQL"],
    }
    return success(mock_resume)
