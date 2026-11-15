import io
import json
import urllib.error


import numpy as np
import pytest

from notesage.prompt import NOT_FOUND_MESSAGE
from notesage.answer import Answer, answer_question
from notesage.chunking import Chunk
from notesage.llm import LLMError, OllamaClient
from notesage.vector_index import VectorIndex

VOCAB = ["cat", "dog", "stock"]


class FakeEmbedder:
    def embed_texts(self, texts):
        rows = []
        for text in texts:
            words = text.lower().split()
            rows.append([words.count(w) for w in VOCAB] + [0.01])
        vectors = np.array(rows, dtype="float32")
        return vectors / np.linalg.norm(vectors, axis=1, keepdims=True)

    def embed_query(self, query):
        return self.embed_texts([query])


class FakeLLM:
    """Records the prompt it receives and returns a canned reply."""

    def __init__(self, reply="The cat sat [1]."):
        self.reply = reply
        self.prompts = []

    def generate(self, prompt):
        self.prompts.append(prompt)
        return self.reply


def make_index():
    chunks = [
        Chunk(text="the cat sat", source="a.txt", page=1, chunk_id="a.txt-p1-c0"),
        Chunk(text="dog dog barked", source="a.txt", page=2, chunk_id="a.txt-p2-c1"),
        Chunk(text="stock market fell", source="b.md", page=1, chunk_id="b.md-p1-c0"),
    ]
    return VectorIndex.build(chunks, FakeEmbedder())


def test_answer_returns_model_text_and_cited_source():
    result = answer_question("cat", make_index(), FakeEmbedder(), FakeLLM(), k=2)
    assert isinstance(result, Answer)
    assert result.found
    assert result.text == "The cat sat [1]."
    assert [s.chunk.text for s in result.sources] == ["the cat sat"]


def test_prompt_sent_to_model_contains_retrieved_chunk_and_question():
    llm = FakeLLM()
    answer_question("cat", make_index(), FakeEmbedder(), llm, k=1)
    assert "the cat sat" in llm.prompts[0]
    assert "Question: cat" in llm.prompts[0]


def test_llm_errors_propagate():
    class BrokenLLM:
        def generate(self, prompt):
            raise LLMError("boom")

    with pytest.raises(LLMError):
        answer_question("cat", make_index(), FakeEmbedder(), BrokenLLM())


class FakeResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def test_ollama_client_parses_response(monkeypatch):
    body = json.dumps({"response": "  hello  "}).encode("utf-8")
    monkeypatch.setattr(
        "urllib.request.urlopen", lambda req, timeout=None: FakeResponse(body)
    )
    assert OllamaClient().generate("hi") == "hello"


def test_ollama_client_reports_unreachable_server(monkeypatch):
    def refuse(req, timeout=None):
        raise urllib.error.URLError("connection refused")

    monkeypatch.setattr("urllib.request.urlopen", refuse)
    with pytest.raises(LLMError):
        OllamaClient().generate("hi")


def test_ollama_client_rejects_empty_answer(monkeypatch):
    body = json.dumps({"response": "   "}).encode("utf-8")
    monkeypatch.setattr(
        "urllib.request.urlopen", lambda req, timeout=None: FakeResponse(body)
    )
    with pytest.raises(LLMError):
        OllamaClient().generate("hi")


def test_out_of_scope_question_skips_the_model():
    llm = FakeLLM()
    result = answer_question("zebra", make_index(), FakeEmbedder(), llm)
    assert result.text == NOT_FOUND_MESSAGE
    assert result.sources == []
    assert not result.found
    assert llm.prompts == []


def test_model_not_found_reply_returns_no_sources():
    llm = FakeLLM(reply=NOT_FOUND_MESSAGE)
    result = answer_question("cat", make_index(), FakeEmbedder(), llm)
    assert not result.found
    assert result.sources == []


def test_only_cited_sources_are_returned():
    result = answer_question(
        "cat dog", make_index(), FakeEmbedder(), FakeLLM("Answer [1]."), k=2
    )
    assert len(result.sources) == 1


def test_uncited_answer_falls_back_to_all_relevant_sources():
    result = answer_question(
        "cat dog", make_index(), FakeEmbedder(), FakeLLM("No numbers here."), k=2
    )
    assert len(result.sources) == 2


def test_min_score_is_configurable():
    llm = FakeLLM()
    answer_question("zebra", make_index(), FakeEmbedder(), llm, min_score=0.0)
    assert len(llm.prompts) == 1