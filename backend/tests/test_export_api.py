"""US-7 PDF 导出测试。"""
from __future__ import annotations

from fastapi.testclient import TestClient


def _make_resume_data() -> dict:
    """构造测试简历数据。"""
    return {
        "name": "张三",
        "email": "zhangsan@example.com",
        "phone": "13800138000",
        "experience": [
            {
                "company": "腾讯",
                "role": "推荐算法工程师",
                "period": "2021-至今",
                "highlights": [
                    "主导推荐召回模型升级，离线 AUC 提升 2%",
                    "设计分布式训练 pipeline，日均处理 10 亿条样本",
                ],
            }
        ],
        "projects": [
            {
                "name": "实时推荐系统",
                "role": "核心开发",
                "period": "2022-2023",
                "description": "从零搭建实时推荐服务",
                "tech_stack": ["Python", "PyTorch", "Kafka"],
            }
        ],
        "skills": {
            "tech_stack": [
                {"name": "Python", "context": "3 年后端开发经验"},
                {"name": "PyTorch", "context": "模型训练与部署"},
            ],
            "hard_skills": [
                {"name": "模型训练", "context": "推荐系统召回排序"},
            ],
            "soft_skills": [
                {"name": "跨团队协作", "context": "与产品/设计团队对接"},
            ],
        },
    }


def test_export_pdf_success() -> None:
    """导出 PDF 成功，返回 application/pdf。"""
    from resume_agent.main import app

    client = TestClient(app)
    response = client.post(
        "/api/export/pdf",
        json={"resume_data": _make_resume_data(), "job_title": "推荐算法工程师"},
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    # 检查 PDF magic bytes
    content = response.content
    assert content[:4] == b"%PDF"


def test_export_empty_data_returns_error() -> None:
    """空数据返回错误。"""
    from resume_agent.main import app

    client = TestClient(app)
    response = client.post(
        "/api/export/pdf",
        json={"resume_data": {}},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is False
    assert body["error"]["code"] == "INVALID_REQUEST"


def test_export_pdf_with_experience_only() -> None:
    """只有工作经历的 PDF。"""
    from resume_agent.main import app

    client = TestClient(app)
    data = {
        "name": "李四",
        "experience": [
            {
                "company": "字节跳动",
                "role": "前端工程师",
                "period": "2020-2023",
                "highlights": ["重构核心页面", "性能优化 30%"],
            }
        ],
    }
    response = client.post("/api/export/pdf", json={"resume_data": data})

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content[:4] == b"%PDF"


def test_export_pdf_with_projects_only() -> None:
    """只有项目经历的 PDF。"""
    from resume_agent.main import app

    client = TestClient(app)
    data = {
        "name": "王五",
        "projects": [
            {
                "name": "开源项目 X",
                "role": "作者",
                "period": "2023",
                "description": "一个工具库",
                "tech_stack": ["Go", "Docker"],
            }
        ],
    }
    response = client.post("/api/export/pdf", json={"resume_data": data})

    assert response.status_code == 200
    assert response.content[:4] == b"%PDF"


def test_export_pdf_chinese_text_extractable() -> None:
    """中文内容应在 PDF 中可提取（ATS 友好 + CJK 字体）。"""
    from resume_agent.main import app

    client = TestClient(app)
    data = {
        "name": "张三",
        "experience": [
            {
                "company": "腾讯",
                "role": "推荐算法工程师",
                "period": "2021-至今",
                "highlights": ["主导推荐召回模型升级"],
            }
        ],
    }
    response = client.post("/api/export/pdf", json={"resume_data": data})

    assert response.status_code == 200
    assert response.content[:4] == b"%PDF"

    # 用 pymupdf 提取文本，验证中文可提取
    import io as _io

    import fitz  # pymupdf

    doc = fitz.open(stream=_io.BytesIO(response.content), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()

    # 验证关键中文内容可提取
    assert "张三" in text
    assert "腾讯" in text
    assert "推荐算法工程师" in text


def test_export_pdf_with_skills_only() -> None:
    """只有技能的 PDF。"""
    from resume_agent.main import app

    client = TestClient(app)
    data = {
        "name": "赵六",
        "skills": {
            "tech_stack": [{"name": "Java", "context": "5 年经验"}],
            "hard_skills": [{"name": "系统设计", "context": "高并发架构"}],
        },
    }
    response = client.post("/api/export/pdf", json={"resume_data": data})

    assert response.status_code == 200
    assert response.content[:4] == b"%PDF"


def test_export_pdf_full_resume() -> None:
    """完整简历 PDF（经历 + 项目 + 技能）。"""
    from resume_agent.main import app

    client = TestClient(app)
    response = client.post(
        "/api/export/pdf",
        json={
            "resume_data": _make_resume_data(),
            "job_title": "推荐算法工程师",
            "company": "腾讯",
        },
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    # PDF 大小应大于 1KB
    assert len(response.content) > 1024


def test_export_pdf_xml_special_chars() -> None:
    """包含 XML 特殊字符的内容应正确转义。"""
    from resume_agent.main import app

    client = TestClient(app)
    data = {
        "name": "Test <User>",
        "experience": [
            {
                "company": "A & B Corp",
                "role": "Engineer",
                "period": "2020",
                "highlights": ["Handled <script> & other chars"],
            }
        ],
    }
    response = client.post("/api/export/pdf", json={"resume_data": data})

    assert response.status_code == 200
    assert response.content[:4] == b"%PDF"
