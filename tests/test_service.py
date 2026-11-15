import numpy as np
import pytest

from notesage.service import NoteSageError, build_index_from_uploads


class FakeEmbedder:
    def embed_texts(self, texts):
        vectors = np.array([[len(t), 1.0, 2.0] for t in texts], dtype="float32")
        return vectors / np.linalg.norm(vectors, axis=1, keepdims=True)


def test_no_files_raises():
    with pytest.raises(NoteSageError):
        build_index_from_uploads([], FakeEmbedder())


def test_builds_index_from_text_upload():
    index, skipped = build_index_from_uploads(
        [("notes.txt", b"hello world " * 20)], FakeEmbedder()
    )
    assert len(index) >= 1
    assert skipped == []


def test_unsupported_file_is_skipped_but_others_used():
    index, skipped = build_index_from_uploads(
        [("notes.txt", b"some text here"), ("data.csv", b"a,b")], FakeEmbedder()
    )
    assert len(index) == 1
    assert any("data.csv" in s for s in skipped)


def test_only_unreadable_files_raise():
    with pytest.raises(NoteSageError):
        build_index_from_uploads([("empty.txt", b"   ")], FakeEmbedder())


def test_corrupt_pdf_is_skipped():
    index, skipped = build_index_from_uploads(
        [("good.txt", b"valid notes"), ("bad.pdf", b"not a real pdf")], FakeEmbedder()
    )
    assert len(index) == 1
    assert any("bad.pdf" in s for s in skipped)


def test_oversized_file_is_skipped(monkeypatch):
    monkeypatch.setattr("notesage.service.MAX_FILE_MB", 0)
    with pytest.raises(NoteSageError, match="larger than"):
        build_index_from_uploads([("big.txt", b"some text")], FakeEmbedder())