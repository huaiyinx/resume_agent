"""ATS 友好 PDF 简历生成器。

使用 reportlab platypus 框架，生成文本可选、可解析的 PDF。
ATS（Applicant Tracking System）友好意味着：
- 文本可选可复制（非图片）
- 清晰的段落结构
- 无复杂表格嵌套

字体：STSong-Light（reportlab 内置 CJK CID 字体，支持中英文）
模板：modern（简洁现代风）
"""

from __future__ import annotations

import io
from typing import Any

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)

# 注册 CJK 字体（reportlab 内置，无需额外字体文件）
_FONT_NORMAL = "STSong-Light"
_FONT_BOLD = "STSong-Light"  # CID 字体无 bold 变体，用同字体
# 字体注册标记
_font_registered = False


def _ensure_font_registered() -> None:
    """注册 CJK CID 字体（仅注册一次）。"""
    global _font_registered
    if not _font_registered:
        from reportlab.pdfbase import pdfmetrics

        pdfmetrics.registerFont(UnicodeCIDFont(_FONT_NORMAL))
        _font_registered = True


# 颜色
_COLOR_PRIMARY = HexColor("#1a1a1a")
_COLOR_SECONDARY = HexColor("#555555")
_COLOR_ACCENT = HexColor("#2563eb")
_COLOR_LIGHT = HexColor("#e5e7eb")

# 段落样式
def _build_styles() -> dict[str, ParagraphStyle]:
    """构建段落样式。"""
    _ensure_font_registered()
    styles = getSampleStyleSheet()

    name_style = ParagraphStyle(
        "ResumeName",
        parent=styles["Title"],
        fontName=_FONT_BOLD,
        fontSize=18,
        textColor=_COLOR_PRIMARY,
        alignment=TA_CENTER,
        spaceAfter=2 * mm,
    )

    contact_style = ParagraphStyle(
        "ResumeContact",
        parent=styles["Normal"],
        fontName=_FONT_NORMAL,
        fontSize=9,
        textColor=_COLOR_SECONDARY,
        alignment=TA_CENTER,
        spaceAfter=4 * mm,
    )

    section_title_style = ParagraphStyle(
        "SectionTitle",
        parent=styles["Heading2"],
        fontName=_FONT_BOLD,
        fontSize=11,
        textColor=_COLOR_PRIMARY,
        spaceBefore=4 * mm,
        spaceAfter=2 * mm,
        borderWidth=0,
        borderPadding=0,
    )

    job_title_style = ParagraphStyle(
        "JobTitle",
        parent=styles["Normal"],
        fontName=_FONT_BOLD,
        fontSize=10,
        textColor=_COLOR_PRIMARY,
        spaceBefore=2 * mm,
        spaceAfter=0.5 * mm,
    )

    job_meta_style = ParagraphStyle(
        "JobMeta",
        parent=styles["Normal"],
        fontName=_FONT_NORMAL,
        fontSize=9,
        textColor=_COLOR_SECONDARY,
        spaceAfter=1 * mm,
    )

    body_style = ParagraphStyle(
        "ResumeBody",
        parent=styles["Normal"],
        fontName=_FONT_NORMAL,
        fontSize=9,
        textColor=_COLOR_PRIMARY,
        leading=12,
        spaceAfter=0.5 * mm,
        leftIndent=4 * mm,
    )

    skill_style = ParagraphStyle(
        "SkillItem",
        parent=styles["Normal"],
        fontName=_FONT_NORMAL,
        fontSize=9,
        textColor=_COLOR_PRIMARY,
        leading=12,
        spaceAfter=0.5 * mm,
        leftIndent=4 * mm,
    )

    return {
        "name": name_style,
        "contact": contact_style,
        "section_title": section_title_style,
        "job_title": job_title_style,
        "job_meta": job_meta_style,
        "body": body_style,
        "skill": skill_style,
    }


def _escape_xml(text: str) -> str:
    """转义 XML 特殊字符（reportlab Paragraph 使用 XML 标记）。"""
    if not text:
        return ""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def build_pdf(
    resume_data: dict[str, Any],
    job_title: str = "",
    company: str = "",
) -> bytes:
    """生成 ATS 友好 PDF。

    Args:
        resume_data: 简历数据，包含 experience / projects / skills 等段落。
        job_title: 目标岗位名称（用于标题）。
        company: 目标公司名称。

    Returns:
        PDF 文件的二进制内容。
    """
    styles = _build_styles()
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=15 * mm,
        rightMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
    )

    story: list[Any] = []

    # === 标题 ===
    name = resume_data.get("name", "简历")
    story.append(Paragraph(_escape_xml(name), styles["name"]))

    # 联系信息
    contact_parts = []
    if resume_data.get("email"):
        contact_parts.append(resume_data["email"])
    if resume_data.get("phone"):
        contact_parts.append(resume_data["phone"])
    if job_title:
        contact_parts.append(f"目标岗位: {job_title}")
    if contact_parts:
        story.append(
            Paragraph(
                " | ".join(_escape_xml(str(p)) for p in contact_parts),
                styles["contact"],
            )
        )

    story.append(HRFlowable(width="100%", thickness=0.5, color=_COLOR_LIGHT))
    story.append(Spacer(1, 2 * mm))

    # === 工作经历 ===
    experiences = resume_data.get("experience", [])
    if experiences:
        story.append(Paragraph("工作经历", styles["section_title"]))
        story.append(HRFlowable(width="100%", thickness=0.3, color=_COLOR_LIGHT))
        for exp in experiences:
            company_name = exp.get("company", "")
            role = exp.get("role", "")
            period = exp.get("period", "")
            highlights = exp.get("highlights", [])

            story.append(
                Paragraph(
                    f"{_escape_xml(role)} | {_escape_xml(company_name)}",
                    styles["job_title"],
                )
            )
            if period:
                story.append(
                    Paragraph(_escape_xml(period), styles["job_meta"])
                )
            for h in highlights:
                story.append(
                    Paragraph(f"• {_escape_xml(h)}", styles["body"])
                )

    # === 项目经历 ===
    projects = resume_data.get("projects", [])
    if projects:
        story.append(Spacer(1, 2 * mm))
        story.append(Paragraph("项目经历", styles["section_title"]))
        story.append(HRFlowable(width="100%", thickness=0.3, color=_COLOR_LIGHT))
        for proj in projects:
            proj_name = proj.get("name", "")
            proj_role = proj.get("role", "")
            proj_period = proj.get("period", "")
            description = proj.get("description", "")
            tech_stack = proj.get("tech_stack", [])

            story.append(
                Paragraph(
                    f"{_escape_xml(proj_name)} | {_escape_xml(proj_role)}",
                    styles["job_title"],
                )
            )
            if proj_period:
                story.append(
                    Paragraph(_escape_xml(proj_period), styles["job_meta"])
                )
            if description:
                story.append(
                    Paragraph(_escape_xml(description), styles["body"])
                )
            if tech_stack:
                story.append(
                    Paragraph(
                        f"<b>技术栈:</b> {_escape_xml(', '.join(tech_stack))}",
                        styles["body"],
                    )
                )

    # === 技能 ===
    skills = resume_data.get("skills", {})
    if skills and isinstance(skills, dict):
        story.append(Spacer(1, 2 * mm))
        story.append(Paragraph("技能", styles["section_title"]))
        story.append(HRFlowable(width="100%", thickness=0.3, color=_COLOR_LIGHT))

        for category_key, _category_label in [
            ("tech_stack", "技术栈"),
            ("hard_skills", "硬技能"),
            ("soft_skills", "软技能"),
        ]:
            items = skills.get(category_key, [])
            if items:
                for item in items:
                    if isinstance(item, dict):
                        skill_name = item.get("name", "")
                        context = item.get("context", "")
                        if context:
                            story.append(
                                Paragraph(
                                    f"<b>{_escape_xml(skill_name)}</b>: {_escape_xml(context)}",
                                    styles["skill"],
                                )
                            )
                        else:
                            story.append(
                                Paragraph(_escape_xml(skill_name), styles["skill"]),
                            )
                    elif isinstance(item, str):
                        story.append(
                            Paragraph(_escape_xml(item), styles["skill"]),
                        )

    doc.build(story)
    return buffer.getvalue()


__all__ = ["build_pdf"]
