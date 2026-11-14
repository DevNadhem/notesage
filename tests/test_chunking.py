import dataclasses

import pytest
from pypdf import PdfWriter

from notesage.chunking import Chunk, chunk_document, chunk_text
from notesage.chunking import chunk_text


def test_empty_text_returns_no_chunks():
    assert chunk_text("") == []
    assert chunk_text("   \n  ") == []


def test_short_text_is_a_single_chunk():
    assert chunk_text("hello", chunk_size=500, overlap=50) == ["hello"]


def test_text_exactly_chunk_size_is_a_single_chunk():
    assert chunk_text("abcd", chunk_size=4, overlap=1) == ["abcd"]


def test_chunks_overlap_by_requested_amount():
    chunks = chunk_text("abcdefghij", chunk_size=4, overlap=2)
    assert chunks == ["abcd", "cdef", "efgh", "ghij"]
    for current, following in zip(chunks, chunks[1:]):
        assert current[-2:] == following[:2]


def test_zero_overlap_splits_cleanly():
    assert chunk_text("abcdefgh", chunk_size=4, overlap=0) == ["abcd", "efgh"]


def test_no_chunk_exceeds_chunk_size():
    text = "word " * 200
    assert all(len(c) <= 50 for c in chunk_text(text, chunk_size=50, overlap=10))


@pytest.mark.parametrize(
    "chunk_size, overlap",
    [(0, 0), (-5, 0), (10, -1), (10, 10), (10, 15)],
)
def test_invalid_parameters_raise(chunk_size, overlap):
    with pytest.raises(ValueError):
        chunk_text("some text", chunk_size=chunk_size, overlap=overlap)

def test_chunk_document_attaches_metadata(tmp_path):
    f = tmp_path / "note.txt"
    f.write_text("a" * 25, encoding="utf-8")

    chunks = chunk_document(f, chunk_size=10, overlap=0)

    assert len(chunks) == 3
    assert all(c.source == "note.txt" and c.page == 1 for c in chunks)
    assert [c.chunk_id for c in chunks] == [
        "note.txt-p1-c0",
        "note.txt-p1-c1",
        "note.txt-p1-c2",
    ]


def test_chunk_ids_are_unique(tmp_path):
    f = tmp_path / "note.md"
    f.write_text("word " * 100, encoding="utf-8")

    chunks = chunk_document(f, chunk_size=50, overlap=10)

    ids = [c.chunk_id for c in chunks]
    assert len(ids) == len(set(ids))


def test_blank_pdf_produces_no_chunks(tmp_path):
    pdf_path = tmp_path / "blank.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    with open(pdf_path, "wb") as f:
        writer.write(f)

    assert chunk_document(pdf_path) == []


def test_chunk_is_immutable():
    chunk = Chunk(text="hi", source="a.txt", page=1, chunk_id="a.txt-p1-c0")
    with pytest.raises(dataclasses.FrozenInstanceError):
        chunk.text = "changed"