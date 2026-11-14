import pytest
from pypdf import PdfWriter
from notesage.loaders import load_document, load_pdf, load_text
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
def test_load_text_reads_file(tmp_path):
    f = tmp_path / "note.txt"
    f.write_text("hello notes", encoding="utf-8")
    assert load_text(f) == "hello notes"


def test_load_text_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        load_text("missing.txt")


def test_load_document_text_returns_single_page(tmp_path):
    f = tmp_path / "note.md"
    f.write_text("# Title", encoding="utf-8")
    assert load_document(f) == [(1, "# Title")]


def test_load_document_pdf_numbers_pages(tmp_path):
    pdf_path = tmp_path / "two.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    writer.add_blank_page(width=72, height=72)
    with open(pdf_path, "wb") as f:
        writer.write(f)

    assert load_document(pdf_path) == [(1, ""), (2, "")]


def test_load_document_unsupported_type_raises(tmp_path):
    f = tmp_path / "data.csv"
    f.write_text("a,b", encoding="utf-8")
    with pytest.raises(ValueError):
        load_document(f)