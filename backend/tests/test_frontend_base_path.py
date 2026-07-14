from pathlib import Path

from fastapi.testclient import TestClient


def test_frontend_router_uses_vite_base_path() -> None:
    project_root = Path(__file__).resolve().parents[2]
    entry = (project_root / "frontend" / "src" / "main.tsx").read_text(
        encoding="utf-8"
    )

    assert "import.meta.env.BASE_URL" in entry
    assert "<BrowserRouter basename={routerBase}>" in entry


def test_frontend_viewport_supports_mobile_safe_area() -> None:
    project_root = Path(__file__).resolve().parents[2]
    html = (project_root / "frontend" / "index.html").read_text(encoding="utf-8")

    assert "viewport-fit=cover" in html


def test_mobile_layout_uses_single_pane_instead_of_fixed_three_columns() -> None:
    project_root = Path(__file__).resolve().parents[2]
    layout = (
        project_root / "frontend" / "src" / "components" / "layout" / "MainLayout.tsx"
    ).read_text(encoding="utf-8")
    styles = (
        project_root / "frontend" / "src" / "styles" / "tokens.css"
    ).read_text(encoding="utf-8")

    assert "data-mobile-pane={mobilePane}" in layout
    assert "@media (max-width: 1023px)" in styles
    assert "data-mobile-pane='workspace'" in styles
    assert "data-mobile-pane='materials'" in styles
    assert "data-mobile-pane='career'" in styles


def test_spa_entry_disables_stale_browser_cache(tmp_path, monkeypatch) -> None:
    from resume_agent import main as main_module

    static_dir = tmp_path / "static"
    (static_dir / "assets").mkdir(parents=True)
    (static_dir / "index.html").write_text(
        '<div id="root"></div>', encoding="utf-8"
    )
    monkeypatch.chdir(tmp_path)

    client = TestClient(main_module.create_app())
    response = client.get("/career/")

    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-cache, no-store, must-revalidate"
    assert response.headers["pragma"] == "no-cache"
