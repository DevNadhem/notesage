from dataclasses import dataclass

from .prompt import build_prompt


@dataclass(frozen=True)
class Answer:
    """An answer plus the chunks it was based on."""

    text: str
    sources: list  # list of SearchResult, best first


def answer_question(question, index, embedder, llm, k=3):
    """Search the index, build a grounded prompt, and ask the model."""
    results = index.search(question, embedder, k=k)
    prompt = build_prompt(question, results)
    text = llm.generate(prompt)
    return Answer(text=text, sources=results)