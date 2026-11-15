import pytest

from notesage.chunking import Chunk
from notesage.prompt import NOT_FOUND_MESSAGE, build_context, build_prompt
from notesage.vector_index import SearchResult


def make_results(texts):
    return [
        SearchResult(
            Chunk(text=t, source="a.txt", page=i + 1, chunk_id=f"a.txt-p{i + 1}-c{i}"),
            score=0.9,
        )
        for i, t in enumerate(texts)
    ]


def test_prompt_contains_every_chunk_with_metadata():
    prompt = build_prompt("What is X?", make_results(["alpha text", "bravo text"]))
    assert "alpha text" in prompt and "bravo text" in prompt
    assert "(a.txt, page 1)" in prompt
    assert "(a.txt, page 2)" in prompt


def test_chunks_are_numbered_in_rank_order():
    prompt = build_prompt("What is X?", make_results(["zebra note", "yak note"]))
    notes = prompt.split("Notes:")[1]
    assert notes.index("[1]") < notes.index("zebra note")
    assert notes.index("zebra note") < notes.index("[2]") < notes.index("yak note")


def test_prompt_contains_the_question():
    assert "Why is the sky blue?" in build_prompt(
        "  Why is the sky blue?  ", make_results(["note"])
    )


def test_prompt_asks_for_grounded_cited_answers():
    prompt = build_prompt("What is X?", make_results(["note"]))
    assert "only" in prompt.lower()
    assert "Cite" in prompt
    assert NOT_FOUND_MESSAGE in prompt


def test_context_drops_chunks_that_do_not_fit():
    context = build_context(make_results(["a" * 50] * 3), max_chars=150)
    assert "[1]" in context and "[2]" in context
    assert "[3]" not in context
    assert len(context) <= 150


def test_oversized_first_chunk_is_truncated():
    context = build_context(make_results(["x" * 500]), max_chars=100)
    assert len(context) == 100
    assert context.startswith("[1]")


def test_invalid_max_chars_raises():
    with pytest.raises(ValueError):
        build_context(make_results(["note"]), max_chars=0)


def test_empty_question_raises():
    with pytest.raises(ValueError):
        build_prompt("   ", make_results(["note"]))


def test_empty_results_raise():
    with pytest.raises(ValueError):
        build_prompt("What is X?", [])

def test_prompt_allows_paraphrased_questions():
    prompt = build_prompt("What is X?", make_results(["note"]))
    assert "Match by meaning" in prompt