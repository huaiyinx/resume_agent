"""Idempotently import reviewed Career-Ops Markdown into Resume-Agent.

The script talks only to the local Resume-Agent HTTP API. It does not copy
source paths or file contents into logs, and it skips files already present by
their original filename.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

import requests


SUPPORTED_KNOWLEDGE_SUFFIXES = {".md", ".txt"}


def _response_data(response: requests.Response) -> Any:
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, dict) or not payload.get("ok"):
        error = payload.get("error") if isinstance(payload, dict) else {}
        message = error.get("message") if isinstance(error, dict) else "invalid response"
        raise RuntimeError(str(message or "Resume-Agent request failed"))
    return payload.get("data")


def _headers(token: str) -> dict[str, str]:
    return {"X-Resume-Agent-Token": token} if token else {}


def _knowledge_files(source_dir: Path, resume_file: Path) -> list[Path]:
    return sorted(
        path
        for path in source_dir.rglob("*")
        if path.is_file()
        and path.suffix.lower() in SUPPORTED_KNOWLEDGE_SUFFIXES
        and path.resolve() != resume_file.resolve()
        and not path.name.startswith(".")
    )


def import_career_ops(
    *,
    source_dir: Path,
    resume_file: Path,
    api_url: str,
    token: str,
    timeout: float,
) -> dict[str, Any]:
    session = requests.Session()
    session.headers.update(_headers(token))
    api_root = api_url.rstrip("/")

    documents = _response_data(session.get(f"{api_root}/knowledge/documents", timeout=timeout))
    existing_documents = {
        str(item.get("file_name") or "")
        for item in (documents if isinstance(documents, list) else [])
        if isinstance(item, dict)
    }
    resumes = _response_data(session.get(f"{api_root}/resumes/list", timeout=timeout))
    existing_resumes = {
        str(item.get("file_name") or "")
        for item in (resumes if isinstance(resumes, list) else [])
        if isinstance(item, dict)
    }

    imported_documents: list[str] = []
    skipped_documents: list[str] = []
    for path in _knowledge_files(source_dir, resume_file):
        if path.name in existing_documents:
            skipped_documents.append(path.name)
            continue
        with path.open("rb") as handle:
            result = _response_data(
                session.post(
                    f"{api_root}/knowledge/upload",
                    files={"file": (path.name, handle, "text/markdown")},
                    timeout=timeout,
                )
            )
        if isinstance(result, dict) and result.get("index_error"):
            raise RuntimeError(f"knowledge indexing failed for {path.name}")
        imported_documents.append(path.name)

    resume_result: dict[str, Any] = {"status": "skipped", "file_name": resume_file.name}
    if resume_file.name not in existing_resumes:
        with resume_file.open("rb") as handle:
            uploaded = _response_data(
                session.post(
                    f"{api_root}/resumes/upload",
                    files={"file": (resume_file.name, handle, "text/markdown")},
                    timeout=timeout,
                )
            )
        upload_id = str((uploaded or {}).get("upload_id") or "")
        if not upload_id:
            raise RuntimeError("resume upload did not return upload_id")
        parsed = _response_data(
            session.post(
                f"{api_root}/resumes/parse",
                json={"upload_id": upload_id},
                timeout=max(timeout, 180.0),
            )
        )
        resume_result = {
            "status": "imported",
            "file_name": resume_file.name,
            "node_id": str(((parsed or {}).get("tree_node") or {}).get("node_id") or "master"),
        }

    return {
        "ok": True,
        "source_document_count": len(_knowledge_files(source_dir, resume_file)),
        "imported_document_count": len(imported_documents),
        "skipped_document_count": len(skipped_documents),
        "imported_documents": imported_documents,
        "skipped_documents": skipped_documents,
        "resume": resume_result,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--resume-file", type=Path)
    parser.add_argument("--api-url", default="http://127.0.0.1:5173/api")
    parser.add_argument("--token", default=os.getenv("INTERNAL_API_TOKEN", ""))
    parser.add_argument("--timeout", type=float, default=60.0)
    args = parser.parse_args()

    source_dir = args.source_dir.resolve()
    resume_file = (args.resume_file or source_dir / "cv.md").resolve()
    if not source_dir.is_dir():
        raise SystemExit("source directory is missing")
    if not resume_file.is_file() or resume_file.suffix.lower() not in {".md", ".txt"}:
        raise SystemExit("reviewed Markdown/TXT resume is missing")

    result = import_career_ops(
        source_dir=source_dir,
        resume_file=resume_file,
        api_url=args.api_url,
        token=args.token,
        timeout=args.timeout,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
