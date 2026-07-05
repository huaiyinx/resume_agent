"""简历上传与解析端点。

实现 US-1 资产冷启动的简历上传、解析、列表三个端点。
对齐 design.md 第 3.1-3.3 节。
"""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any

from fastapi import APIRouter, UploadFile
from pydantic import BaseModel

from resume_agent.api.response import error, success
from resume_agent.config import settings
from resume_agent.db.connection import get_connection
from resume_agent.llm.client import LLMClient
from resume_agent.parsers.docx_parser import extract_text_from_docx
from resume_agent.parsers.extractor import ResumeExtractor
from resume_agent.parsers.pdf_parser import extract_text_from_pdf
from resume_agent.services.tree_builder import TreeBuilder

router = APIRouter(prefix="/resumes", tags=["resumes"])

# 支持的文件类型
_ALLOWED_FILE_TYPES: tuple[str, ...] = ("pdf", "docx")


class ParseRequest(BaseModel):
    """解析简历请求体。"""

    upload_id: str


def _get_file_ext(filename: str | None) -> str | None:
    """从文件名提取小写扩展名（不含点）。"""
    if not filename or "." not in filename:
        return None
    return filename.rsplit(".", 1)[-1].lower()


def _extract_text(file_path: Path, file_type: str) -> str:
    """根据文件类型调用对应解析器提取纯文本。

    Args:
        file_path: 文件绝对路径。
        file_type: 文件扩展名（pdf / docx）。

    Returns:
        提取的纯文本。

    Raises:
        ValueError: 不支持的文件类型。
    """
    if file_type == "pdf":
        return extract_text_from_pdf(file_path)
    if file_type == "docx":
        return extract_text_from_docx(file_path)
    raise ValueError(f"不支持的文件类型: {file_type}")


@router.post("/upload")
async def upload_resume(file: UploadFile) -> dict[str, Any]:
    """上传简历文件。

    验证文件扩展名（pdf/docx），保存到 ``{files_root}/resumes/{uuid}.{ext}``，
    并写入 ``upload_records`` 表。

    Args:
        file: 上传的文件对象。

    Returns:
        统一响应 envelope，``data`` 含上传记录信息（upload_id、file_name、
        file_type、parse_status="pending"）。
    """
    file_ext = _get_file_ext(file.filename)
    if file_ext not in _ALLOWED_FILE_TYPES:
        return error(
            "INVALID_FILE_TYPE",
            f"不支持的文件类型: {file_ext}，仅支持 {list(_ALLOWED_FILE_TYPES)}",
        )

    # 保存文件
    upload_id = str(uuid.uuid4())
    resumes_dir = settings.files_root / "resumes"
    resumes_dir.mkdir(parents=True, exist_ok=True)
    saved_filename = f"{upload_id}.{file_ext}"
    saved_path = resumes_dir / saved_filename
    content = await file.read()
    saved_path.write_bytes(content)

    # 写入 DB（file_path 存储相对路径，相对 files_root）
    relative_path = f"resumes/{saved_filename}"
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO upload_records (id, file_name, file_type, file_path, parse_status)
            VALUES (?, ?, ?, ?, ?)
            """,
            (upload_id, file.filename or saved_filename, file_ext, relative_path, "pending"),
        )

    data = {
        "upload_id": upload_id,
        "file_name": file.filename or saved_filename,
        "file_type": file_ext,
        "file_path": relative_path,
        "parse_status": "pending",
    }
    return success(data)


@router.post("/parse")
async def parse_resume(req: ParseRequest) -> dict[str, Any]:
    """解析已上传的简历为结构化 JSON 并构建版本树节点。

    流程：
    1. 从 DB 获取 upload_record，不存在返回错误。
    2. 若 LLM 未配置，返回错误并保持 parse_status=pending。
    3. 根据文件类型调用解析器提取文本。
    4. 调用 ``ResumeExtractor.extract`` 提取结构化简历。
    5. 调用 ``TreeBuilder.build_from_resume`` 创建/更新版本树节点。
    6. 更新 upload_records.parse_status=success。
    7. 解析失败 → parse_status=needs_review。

    Args:
        req: 解析请求，含上传记录 ID。

    Returns:
        统一响应 envelope，``data`` 含 structured_resume、tree_node、deduplicated。
    """
    # 1. 获取上传记录
    with get_connection() as conn:
        record = conn.execute(
            "SELECT * FROM upload_records WHERE id = ?",
            (req.upload_id,),
        ).fetchone()

    if record is None:
        return error("UPLOAD_NOT_FOUND", f"上传记录不存在: {req.upload_id}")

    # 2. 检查 LLM 配置
    llm_client = LLMClient()
    if not llm_client.configured:
        return error(
            "LLM_NOT_CONFIGURED",
            "LLM 未配置，请先在设置中配置 API Key 后再解析简历",
        )

    # 3. 标记为 parsing 中
    _update_parse_status(req.upload_id, "parsing")

    file_path = settings.files_root / record["file_path"]
    try:
        raw_text = _extract_text(Path(file_path), record["file_type"])
    except Exception as exc:  # noqa: BLE001 - 解析失败需标记 needs_review
        _update_parse_status(req.upload_id, "needs_review")
        return error("PARSE_FAILED", f"文件解析失败: {exc}")

    # 4. LLM 结构化提取
    try:
        extractor = ResumeExtractor(llm_client)
        structured_resume = await extractor.extract(raw_text)
    except Exception as exc:  # noqa: BLE001 - LLM 提取失败需标记 needs_review
        _update_parse_status(req.upload_id, "needs_review")
        return error("EXTRACT_FAILED", f"LLM 结构化提取失败: {exc}")

    # 5. 构建版本树节点
    try:
        builder = TreeBuilder()
        tree_result = builder.build_from_resume(structured_resume)
    except Exception as exc:  # noqa: BLE001 - 版本树构建失败需标记 needs_review
        _update_parse_status(req.upload_id, "needs_review")
        return error("TREE_BUILD_FAILED", f"版本树构建失败: {exc}")

    # 6. 更新状态为成功
    _update_parse_status(req.upload_id, "success")

    data = {
        "upload_id": req.upload_id,
        "structured_resume": structured_resume.model_dump(),
        "tree_node": tree_result["node"],
        "deduplicated": tree_result["deduplicated"],
    }
    return success(data)


@router.get("/list")
def list_resumes() -> dict[str, Any]:
    """列出所有上传记录。

    Returns:
        统一响应 envelope，``data`` 为上传记录列表
        （id、file_name、file_type、parse_status、created_at）。
    """
    with get_connection() as conn:
        records = conn.execute(
            """
            SELECT id, file_name, file_type, file_path, parse_status, created_at
            FROM upload_records
            ORDER BY created_at DESC
            """
        ).fetchall()

    return success(records)


def _update_parse_status(upload_id: str, status: str) -> None:
    """更新上传记录的解析状态。"""
    with get_connection() as conn:
        conn.execute(
            "UPDATE upload_records SET parse_status = ? WHERE id = ?",
            (status, upload_id),
        )
