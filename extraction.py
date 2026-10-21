"""Extract clean text from PDF and DOCX files."""

import re
import unicodedata
from collections import Counter
from pathlib import Path

from docx import Document
from docx.table import Table
from pypdf import PdfReader

SUPPORTED_TYPES = (".pdf", ".docx")
# Headers and footers are looked for only in the first and last few lines of a page.
EDGE_LINES = 3


class ExtractionError(Exception):
    """Raised when text could not be extracted from a file."""


def extract_text(path: str | Path) -> str:
    """Return the clean text of a PDF or DOCX file, with paragraphs separated by blank lines."""
    path = Path(path)
    if not path.is_file():
        raise ExtractionError(f"File not found: {path}")

    suffix = path.suffix.lower()
    if suffix not in SUPPORTED_TYPES:
        raise ExtractionError(
            f"Unsupported file type: {suffix or '(none)'} (use .pdf or .docx)"
        )

    text = _read_pdf(path) if suffix == ".pdf" else _read_docx(path)

    if not text:
        hint = " If it is a scanned PDF, it contains only images of text." if suffix == ".pdf" else ""
        raise ExtractionError(f"No text found in {path.name}.{hint}")
    return text


def _read_pdf(path: Path) -> str:
    """Read a PDF page by page, drop repeated headers/footers and rejoin broken lines."""
    try:
        reader = PdfReader(path)
    except Exception as error:
        raise ExtractionError(
            f"Could not read {path.name}. The PDF may be damaged."
        ) from error

    if reader.is_encrypted:
        raise ExtractionError(f"PDF is encrypted: {path.name}")

    try:
        # Layout mode keeps the vertical gaps, so paragraphs stay separated by blank lines.
        pages = [page.extract_text(extraction_mode="layout") for page in reader.pages]
    except Exception as error:
        raise ExtractionError(
            f"Could not read the text in {path.name}. The PDF may be damaged."
        ) from error

    pages = _remove_headers_and_footers(pages)
    return _join_broken_lines(clean_text("\n\n".join(pages)))


def _read_docx(path: Path) -> str:
    """Read a DOCX file's paragraphs and tables in document order."""
    try:
        document = Document(path)
    except Exception as error:
        raise ExtractionError(
            f"Could not read {path.name}. The DOCX file may be damaged."
        ) from error

    blocks = []
    for item in document.iter_inner_content():
        if isinstance(item, Table):
            # One line per row, so a row's cells stay together.
            rows = [" | ".join(cell.text.strip() for cell in row.cells) for row in item.rows]
            blocks.append("\n".join(rows))
        else:
            blocks.append(item.text)

    return clean_text("\n\n".join(blocks))


def clean_text(text: str) -> str:
    """Tidy whitespace: one space between words, one blank line between paragraphs."""
    # NFKC turns special characters into plain ones, e.g. the "ﬁ" ligature into "fi".
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("\r\n", "\n").replace("\r", "\n").replace("­", "")

    lines = [re.sub(r"\s+", " ", line).strip() for line in text.split("\n")]
    text = "\n".join(lines)

    return re.sub(r"\n{3,}", "\n\n", text).strip()


def _remove_headers_and_footers(pages: list[str]) -> list[str]:
    """Remove lines that repeat at the top or bottom of most pages (e.g. titles, page numbers)."""
    if len(pages) < 2:
        return pages

    counts = Counter()
    for page in pages:
        counts.update({_line_key(line) for _, line in _edge_lines(page)})
    repeated = {key for key, count in counts.items() if count >= max(2, len(pages) / 2)}

    cleaned = []
    for page in pages:
        lines = page.split("\n")
        drop = {i for i, line in _edge_lines(page) if _line_key(line) in repeated}
        cleaned.append("\n".join(line for i, line in enumerate(lines) if i not in drop))
    return cleaned


def _edge_lines(page: str) -> list[tuple[int, str]]:
    """Return (index, line) for the first and last few non-empty lines of a page."""
    lines = [(i, line) for i, line in enumerate(page.split("\n")) if line.strip()]
    return lines[:EDGE_LINES] + lines[-EDGE_LINES:]


def _line_key(line: str) -> str:
    """Normalize a line for comparison, so "Page 1" and "Page 2" count as the same line."""
    return re.sub(r"\d+", "#", " ".join(line.split()))


def _join_broken_lines(text: str) -> str:
    """Join lines inside each paragraph that the PDF broke in the middle of a sentence."""
    paragraphs = []
    for paragraph in text.split("\n\n"):
        joined = ""
        for line in paragraph.split("\n"):
            if joined.endswith("-") and line[:1].islower():
                # A word split across lines with a hyphen, e.g. "authenti-" + "cation".
                joined = joined[:-1] + line
            else:
                joined = f"{joined} {line}" if joined else line
        paragraphs.append(joined)
    return "\n\n".join(paragraphs)
