"""
file_parser.py
--------------
Extracts plain text from uploaded files.
Supported: PDF (.pdf) and plain text (.txt, .md, .markdown)
"""

import fitz  # PyMuPDF


def extract_text(file_bytes: bytes, filename: str) -> str:
    """
    Extract text from a file given its raw bytes and filename.

    Args:
        file_bytes : raw bytes of the uploaded file
        filename   : original filename — used to detect the type

    Returns:
        Extracted text as a plain string.

    Raises:
        ValueError if the file type is not supported.
    """
    ext = filename.lower().rsplit(".", 1)[-1]

    if ext == "pdf":
        return _extract_pdf(file_bytes)

    if ext in {"txt", "md", "markdown"}:
        return file_bytes.decode("utf-8", errors="replace")

    raise ValueError(
        f"Unsupported file type '.{ext}'. Supported: pdf, txt, md, markdown"
    )


def _extract_pdf(file_bytes: bytes) -> str:
    """Extract text page-by-page from a PDF using PyMuPDF."""
    pages = []
    with fitz.open(stream=file_bytes, filetype="pdf") as doc:
        for i, page in enumerate(doc, start=1):
            text = page.get_text("text").strip()
            if text:
                pages.append(f"[Page {i}]\n{text}")

    return "\n\n".join(pages) if pages else "[No readable text found in this PDF]"