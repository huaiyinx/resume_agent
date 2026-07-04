"""知识库端点（桩实现）。

提供上传、索引、语义检索的桩实现。
"""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, UploadFile
from pydantic import BaseModel

from resume_agent.api.response import success

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


class IndexRequest(BaseModel):
    """触发索引请求体。"""

    upload_id: str


class SearchRequest(BaseModel):
    """语义检索请求体。"""

    query: str
    top_k: int = 5


@router.post("/upload")
async def upload_knowledge(file: UploadFile) -> dict[str, Any]:
    """上传知识素材（桩实现）。

    Args:
        file: 上传的文件对象。

    Returns:
        统一响应 envelope，``data`` 为 mock 上传记录。
    """
    file_ext = file.filename.rsplit(".", 1)[-1].lower() if file.filename else "md"
    mock_record = {
        "id": str(uuid.uuid4()),
        "file_name": file.filename or "knowledge.md",
        "file_type": file_ext,
        "file_path": f"files/knowledge/{uuid.uuid4()}.{file_ext}",
        "parse_status": "pending",
    }
    return success(mock_record)


@router.post("/index")
def index_knowledge(req: IndexRequest) -> dict[str, Any]:
    """触发知识素材索引（桩实现）。

    Args:
        req: 索引请求，含上传记录 ID。

    Returns:
        统一响应 envelope，``data`` 为 mock 索引结果。
    """
    mock_result = {
        "upload_id": req.upload_id,
        "status": "indexed",
        "chunk_count": 12,
    }
    return success(mock_result)


@router.post("/search")
def search_knowledge(req: SearchRequest) -> dict[str, Any]:
    """语义检索知识库（桩实现）。

    Args:
        req: 检索请求，含查询文本与 top_k。

    Returns:
        统一响应 envelope，``data`` 为 mock 检索结果。
    """
    mock_results = [
        {
            "chunk_id": str(uuid.uuid4()),
            "source_file": "周报-2025-W30.md",
            "chunk_text": "本周完成了推荐召回模型的离线评估，AUC 提升 2%。",
            "score": 0.92,
        },
        {
            "chunk_id": str(uuid.uuid4()),
            "source_file": "技术分享-向量检索.md",
            "chunk_text": "Chroma 嵌入式向量库支持余弦相似度检索。",
            "score": 0.85,
        },
    ][: req.top_k]
    return success({"query": req.query, "results": mock_results})
