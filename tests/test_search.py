import numpy as np
import pytest

from notesage.chunking import Chunk
from notesage.vector_index import SearchResult, VectorIndex

VOCAB = ["cat", "dog", "stock"]


class FakeEmbedder:
    """Keyword-count vectors: similar words give similar vectors, no model needed."""

    def embed_texts(self, texts):
        rows = []
        for text in texts:
            words = text.lower().split()
            rows.append([words.count(w) for w in VOCAB] + [0.01])  # avoid zero vectors
        vectors = np.array(rows, dtype="float32")
        return vectors / np.linalg.norm(vectors, axis=1, keepdims=True)

    def embed_query(self, query):
        return self.embed_texts([query])


def make_index():
    chunks = [
        Chunk(text="the cat sat", source="a.txt", page=1, chunk_id="a.txt-p1-c0"),
        Chunk(text="dog dog barked", source="a.txt", page=2, chunk_id="a.txt-p2-c1"),
        Chunk(text="stock market fell", source="b.md", page=1, chunk_id="b.md-p1-c0"),
    ]
    return VectorIndex.build(chunks, FakeEmbedder())


def test_best_match_is_ranked_first():
    results = make_index().search("cat", FakeEmbedder(), k=3)
    assert results[0].chunk.text == "the cat sat"
    scores = [r.score for r in results]
    assert scores == sorted(scores, reverse=True)


def test_results_carry_citation_metadata():
    top = make_index().search("dog", FakeEmbedder(), k=1)[0]
    assert isinstance(top, SearchResult)
    assert (top.chunk.source, top.chunk.page) == ("a.txt", 2)


def test_k_larger_than_index_returns_all_chunks():
    assert len(make_index().search("stock", FakeEmbedder(), k=10)) == 3


@pytest.mark.parametrize("k", [0, -1])
def test_invalid_k_raises(k):
    with pytest.raises(ValueError):
        make_index().search("cat", FakeEmbedder(), k=k)


def test_search_works_after_save_and_load(tmp_path):
    make_index().save(tmp_path)
    loaded = VectorIndex.load(tmp_path)
    assert loaded.search("stock", FakeEmbedder(), k=1)[0].chunk.source == "b.md"