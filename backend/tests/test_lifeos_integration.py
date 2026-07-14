from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient


def test_gap_report_openapi_uses_structured_jd_schema() -> None:
    from resume_agent.main import app

    schema = TestClient(app).get("/openapi.json").json()
    operation = schema["paths"]["/api/gap-report"]["post"]
    request_schema = operation["requestBody"]["content"]["application/json"]["schema"]

    assert request_schema["$ref"] == "#/components/schemas/GapReportRequest"
    properties = schema["components"]["schemas"]["GapReportRequest"]["properties"]
    assert "structured_jd" in properties
    assert "resume_node_id" not in properties
    assert "jd_analysis_id" not in properties


def test_internal_token_protects_business_api(monkeypatch) -> None:
    from resume_agent import config as config_module
    from resume_agent import main as main_module

    settings = config_module.Settings(
        internal_api_token="test-internal-token",
        cors_origins="https://chat.19991023.xyz",
    )
    monkeypatch.setattr(config_module, "settings", settings)
    monkeypatch.setattr(main_module, "settings", settings)
    client = TestClient(main_module.create_app())

    assert client.get("/api/health").status_code == 200
    assert client.get("/api/test-protected").status_code == 401
    assert (
        client.get(
            "/api/test-protected",
            headers={"X-Resume-Agent-Token": "test-internal-token"},
        ).status_code
        == 404
    )


def test_upload_limit_rejects_large_requests(monkeypatch) -> None:
    from resume_agent import config as config_module
    from resume_agent import main as main_module

    settings = config_module.Settings(max_upload_bytes=8)
    monkeypatch.setattr(config_module, "settings", settings)
    monkeypatch.setattr(main_module, "settings", settings)
    client = TestClient(main_module.create_app())

    response = client.post(
        "/api/knowledge/upload",
        content=b"123456789",
        headers={"content-type": "application/octet-stream"},
    )
    assert response.status_code == 413
    assert response.json()["error"]["code"] == "PAYLOAD_TOO_LARGE"


def test_markdown_resume_upload_and_direct_extract(tmp_path: Path, monkeypatch) -> None:
    from resume_agent import config as config_module
    from resume_agent.api import resumes
    from resume_agent.db.init_db import init_database
    from resume_agent.main import app

    settings = config_module.Settings(
        resume_agent_home=tmp_path,
        sqlite_path=tmp_path / "data.db",
        chroma_path=tmp_path / "chroma",
        files_root=tmp_path / "files",
    )
    settings.ensure_dirs()
    init_database(settings.sqlite_path)
    monkeypatch.setattr(config_module, "settings", settings)
    monkeypatch.setattr(resumes, "settings", settings)

    client = TestClient(app)
    response = client.post(
        "/api/resumes/upload",
        files={"file": ("cv.md", b"# Resume\n\nPython FastAPI", "text/markdown")},
    )
    assert response.status_code == 200
    assert response.json()["data"]["file_type"] == "md"

    source = tmp_path / "cv.md"
    source.write_text("# Resume\n\nPython FastAPI", encoding="utf-8")
    assert resumes._extract_text(source, "md") == "# Resume\n\nPython FastAPI"
