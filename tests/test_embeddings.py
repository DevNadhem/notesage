import numpy as np
import pytest

from notesage.embeddings import Embedder


class FakeModel:
    """Stands in for SentenceTransformer so tests don't download anything."""

    def encode(self, texts, convert_to_numpy=True, normalize_embeddings=True):
        vectors = np.array([[len(t), 1.0, 2.0] for t in texts], dtype="float64")
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        return vectors / norms


def make_embedder():
    embedder = Embedder()
    embedder._model = FakeModel()
    return embedder


def test_embed_texts_shape_and_dtype():
    vectors = make_embedder().embed_texts(["a", "bb", "ccc"])
    assert vectors.shape == (3, 3)
    assert vectors.dtype == np.float32


def test_embed_texts_empty_returns_empty_array():
    vectors = make_embedder().embed_texts([])
    assert vectors.shape[0] == 0


def test_embed_query_returns_single_row():
    assert make_embedder().embed_query("hello").shape == (1, 3)


@pytest.mark.slow
def test_real_model_similar_sentences_score_higher():
    embedder = Embedder()
    a, b, c = embedder.embed_texts(
        ["The cat sat on the mat.", "A kitten rests on a rug.", "Stock markets fell today."]
    )
    assert float(a @ b) > float(a @ c)