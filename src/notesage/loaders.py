from pathlib import Path

from pypdf import PdfReader


def load_pdf(path):
    """Return a list of strings, one per page of the PDF."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {path}")

    reader = PdfReader(path)
    return [page.extract_text() or "" for page in reader.pages]