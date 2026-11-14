from pathlib import Path

from pypdf import PdfReader


def load_pdf(path):
    """Return a list of strings, one per page of the PDF."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {path}")

    reader = PdfReader(path)
    return [page.extract_text() or "" for page in reader.pages]

def load_text(path):
    """Return the contents of a .txt or .md file as a single string."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Text file not found: {path}")

    return path.read_text(encoding="utf-8", errors="replace")


SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md"}


def load_document(path):
    """Load a document and return a list of (page_number, text) tuples.

    Plain-text files are treated as a single page (page 1).
    """
    path = Path(path)
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        pages = load_pdf(path)
        return [(i + 1, text) for i, text in enumerate(pages)]
    if suffix in {".txt", ".md"}:
        return [(1, load_text(path))]

    supported = ", ".join(sorted(SUPPORTED_EXTENSIONS))
    raise ValueError(f"Unsupported file type '{suffix}'. Supported: {supported}")