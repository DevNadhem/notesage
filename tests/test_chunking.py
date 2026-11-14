import pytest

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