from pathlib import Path


def test_frontend_router_uses_vite_base_path() -> None:
    project_root = Path(__file__).resolve().parents[2]
    entry = (project_root / "frontend" / "src" / "main.tsx").read_text(
        encoding="utf-8"
    )

    assert "import.meta.env.BASE_URL" in entry
    assert "<BrowserRouter basename={routerBase}>" in entry
