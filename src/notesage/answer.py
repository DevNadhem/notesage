import re
from dataclasses import dataclass

from .config import DEFAULT_K, MIN_SCORE
from .prompt import NOT_FOUND_MESSAGE, build_prompt

CITATION_PATTERN = re.compile(r"\[(\d+)\]")


@dataclass(frozen=True)
class Answer:
    """An answer, the sources it is based on, and whether the notes had it."""

    text: str
    sources: list  # list of SearchResult
    found: bool = True


def cited_sources(text, results):
    """Return the results whose [n] numbers appear in the answer text."""
    numbers = {int(n) for n in CITATION_PATTERN.findall(text)}
    return [r for i, r in enumerate(results, start=1) if i in numbers]


def answer_question(question, index, embedder, llm, k=DEFAULT_K, min_score=MIN_SCORE):
    """Answer from the notes, or say they don't contain the answer.

    Chunks scoring below `min_score` are dropped. If none remain, the model
    is never called. Otherwise the answer lists only the chunks it cites,
    or all relevant chunks if it cites none.
    """
    results = index.search(question, embedder, k=k)
    relevant = [r for r in results if r.score >= min_score]
    if not relevant:
        return Answer(text=NOT_FOUND_MESSAGE, sources=[], found=False)

    text = llm.generate(build_prompt(question, relevant))
    if NOT_FOUND_MESSAGE in text:
        return Answer(text=NOT_FOUND_MESSAGE, sources=[], found=False)

    return Answer(text=text, sources=cited_sources(text, relevant) or relevant)