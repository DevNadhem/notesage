import json

import numpy as np
import pytest

from notesage.chunking import Chunk
from notesage.evaluate import evaluate, is_hit, load_questions
from notesage.vector_index import VectorIndex

VOCAB = ["cat", "dog", "stock"]


class FakeEmbedder:
    """Keyword-count vectors, so rankings are predictable without a model."""

    def embed_texts(self, texts):
        rows = []
        for text in texts:
            words = text.lower().split()
            rows.append([words.count(w) for w in VOCAB] + [0.01])
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


def q(question, source, needle):
    return {"question": question, "source": source, "answer_contains": needle}


def test_is_hit_requires_matching_source_and_text():
    results = make_index().search("cat", FakeEmbedder(), k=3)
    assert is_hit(results, q("cat", "a.txt", "the cat"))
    assert not is_hit(results, q("cat", "b.md", "the cat"))
    assert not is_hit(results, q("cat", "a.txt", "giraffe"))


def test_perfect_retrieval_scores_one():
    questions = [
        q("cat", "a.txt", "cat sat"),
        q("dog", "a.txt", "dog dog"),
        q("stock", "b.md", "market"),
    ]
    rates, misses = evaluate(make_index(), FakeEmbedder(), questions, ks=(1, 3))
    assert rates == {1: 1.0, 3: 1.0}
    assert misses == []


def test_hit_rate_can_differ_between_k_values():
    # "dog" ranks the stock chunk lower than first, but it is still in the top 3
    questions = [q("cat", "a.txt", "cat sat"), q("dog", "b.md", "market")]
    rates, misses = evaluate(make_index(), FakeEmbedder(), questions, ks=(1, 3))
    assert rates == {1: 0.5, 3: 1.0}
    assert misses == []


def test_unfindable_answer_is_reported_as_a_miss():
    questions = [q("cat", "a.txt", "cat sat"), q("dog", "a.txt", "giraffe")]
    rates, misses = evaluate(make_index(), FakeEmbedder(), questions, ks=(1, 3))
    assert rates == {1: 0.5, 3: 0.5}
    assert misses == ["dog"]


def test_empty_question_list_raises():
    with pytest.raises(ValueError):
        evaluate(make_index(), FakeEmbedder(), [])


def test_load_questions_reads_valid_file(tmp_path):
    path = tmp_path / "questions.json"
    path.write_text(json.dumps([q("cat", "a.txt", "cat")]), encoding="utf-8")
    assert load_questions(path) == [q("cat", "a.txt", "cat")]


def test_load_questions_rejects_missing_keys(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text(json.dumps([{"question": "cat"}]), encoding="utf-8")
    with pytest.raises(ValueError):
        load_questions(path)