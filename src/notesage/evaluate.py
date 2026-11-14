import argparse
import json
from pathlib import Path

from .chunking import chunk_document
from .embeddings import Embedder
from .vector_index import VectorIndex

REQUIRED_KEYS = ("question", "source", "answer_contains")


def load_questions(path):
    """Load evaluation questions from a JSON file and validate them."""
    questions = json.loads(Path(path).read_text(encoding="utf-8"))
    for item in questions:
        for key in REQUIRED_KEYS:
            if key not in item:
                raise ValueError(f"Question is missing '{key}': {item}")
    return questions


def is_hit(results, question):
    """True if any result is from the expected file and contains the answer phrase."""
    needle = question["answer_contains"].lower()
    return any(
        r.chunk.source == question["source"] and needle in r.chunk.text.lower()
        for r in results
    )


def evaluate(index, embedder, questions, ks=(1, 3)):
    """Return ({k: hit_rate}, misses), where misses failed even at the largest k."""
    if not questions:
        raise ValueError("No questions to evaluate")

    max_k = max(ks)
    hits = {k: 0 for k in ks}
    misses = []
    for question in questions:
        results = index.search(question["question"], embedder, k=max_k)
        for k in ks:
            if is_hit(results[:k], question):
                hits[k] += 1
        if not is_hit(results, question):
            misses.append(question["question"])

    rates = {k: hits[k] / len(questions) for k in ks}
    return rates, misses

def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Measure retrieval hit rate on a set of questions."
    )
    parser.add_argument("notes", nargs="+", help="notes files to index")
    parser.add_argument("--questions", default="docs/eval_questions.json")
    parser.add_argument("--chunk-size", type=int, default=500)
    parser.add_argument("--overlap", type=int, default=50)
    args = parser.parse_args(argv)

    chunks = []
    for path in args.notes:
        chunks.extend(chunk_document(path, args.chunk_size, args.overlap))
    if not chunks:
        parser.error("no text could be extracted from the given files")

    embedder = Embedder()
    index = VectorIndex.build(chunks, embedder)
    questions = load_questions(args.questions)
    rates, misses = evaluate(index, embedder, questions)

    print(
        f"chunk_size={args.chunk_size} overlap={args.overlap} "
        f"chunks={len(chunks)} questions={len(questions)}"
    )
    for k, rate in rates.items():
        print(f"hit@{k}: {rate:.0%}")
    if misses:
        print(f"Missed even within the top {max(rates)}:")
        for question in misses:
            print(f"  - {question}")


if __name__ == "__main__":
    main()