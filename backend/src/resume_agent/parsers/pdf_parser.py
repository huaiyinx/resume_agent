"""PDF 文件解析器。

使用 PyMuPDF（``import fitz``）按页提取文本，页间用 ``\\n\\n`` 分隔。
对齐 design.md 第 2.2 节。
"""

from __future__ import annotations

from pathlib import Path

import fitz  # type: ignore[import-not-found]


def extract_text_from_pdf(file_path: Path) -> str:
    """从 PDF 文件提取全文文本。

    按页读取，页间用两个换行符分隔，保留原始段落结构。

    Args:
        file_path: PDF 文件路径。

    Returns:
        提取的纯文本。空 PDF 返回空字符串。

    Raises:
        FileNotFoundError: 文件不存在。
        RuntimeError: PyMuPDF 打开或解析失败。
    """
    if not file_path.exists():
        raise FileNotFoundError(f"PDF 文件不存在: {file_path}")

    try:
        doc = fitz.open(str(file_path))
    except Exception as exc:  # noqa: BLE001 - 转换为统一异常
        raise RuntimeError(f"打开 PDF 失败: {file_path}: {exc}") from exc

    try:
        pages: list[str] = []
        for page in doc:
            text = page.get_text()
            if text:
                pages.append(text)
        return "\n\n".join(pages)
    finally:
        doc.close()
