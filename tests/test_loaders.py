import pytest
from pypdf import PdfWriter

from notesage.loaders import load_pdf


def test_blank_pdf_returns_empty_string(tmp_path):
    pdf_path = tmp_path / "blank.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    with open(pdf_path, "wb") as f:
        writer.write(f)

    assert load_pdf(pdf_path) == [""]


def test_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        load_pdf("nope.pdf")