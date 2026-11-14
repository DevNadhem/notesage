import json

import numpy as np
import pytest

from notesage.chunking import Chunk
from notesage.vector_index import META_FILE, VectorIndex


class FakeEmbedder:
    """Deterministic embeddings so tests need no model download."""

    def embed_texts(self, texts):
        vectors = np.array([[len(t), 1.0, 2.0] for t in texts], dtype="float32")
        return vectors / np.linalg.norm(vectors, axis=1, keepdims=True)


def make_chunks():
    return [
        Chunk(text="alpha", source="a.txt", page=1, chunk_id="a.txt-p1-c0"),
        Chunk(text="bravo bravo", source="a.txt", page=2, chunk_id="a.txt-p2-c1"),
        Chunk(text="charlie", source="b.md", page=1, chunk_id="b.md-p1-c0"),
    ]


def test_build_rejects_empty_chunk_list():
    with pytest.raises(ValueError):
        VectorIndex.build([], FakeEmbedder())


def test_build_stores_one_vector_per_chunk():
    index = VectorIndex.build(make_chunks(), FakeEmbedder())
    assert len(index) == 3
    assert index.index.ntotal == 3


def test_save_and_load_round_trip(tmp_path):
    original = VectorIndex.build(make_chunks(), FakeEmbedder())
    original.save(tmp_path / "idx")

    loaded = VectorIndex.load(tmp_path / "idx")

    assert loaded.chunks == original.chunks
    assert loaded.index.ntotal == original.index.ntotal


def test_load_missing_directory_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        VectorIndex.load(tmp_path / "nothing-here")


def test_load_detects_mismatched_metadata(tmp_path):
    VectorIndex.build(make_chunks(), FakeEmbedder()).save(tmp_path)
    meta = tmp_path / META_FILE
    data = json.loads(meta.read_text(encoding="utf-8"))
    meta.write_text(json.dumps(data[:-1]), encoding="utf-8")

    with pytest.raises(ValueError):
        VectorIndex.load(tmp_path)