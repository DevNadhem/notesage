import argparse
import json
from pathlib import Path

from .chunking import chunk_document
from .embeddings import Embedder
from .evaluate import load_questions
from .vector_index import VectorIndex


def top_score(index, embedder, question):
    """Best similarity score the index finds for a question."""
    return index.search(question, embedder, k=1)[0].score


def suggest_threshold(in_scope, out_of_scope):
    """Return (lowest in-scope score, highest out-of-scope score, midpoint)."""
    if not in_scope or not out_of_scope:
        raise ValueError("Need scores for both in-scope and out-of-scope questions")
    low, high = min(in_scope), max(out_of_scope)
    return low, high, (low + high) / 2


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Compare top scores of answerable and unanswerable questions."
    )
    parser.add_argument("notes", nargs="+", help="notes files to index")
    parser.add_argument("--in-scope", default="docs/eval_questions.json")
    parser.add_argument("--out-of-scope", default="docs/out_of_scope_questions.json")
    parser.add_argument("--chunk-size", type=int, default=500)
    parser.add_argument("--overlap", type=int, default=50)
    args = parser.parse_args(argv)

    chunks = []
    for path in args.notes:
        chunks.extend(chunk_document(path, args.chunk_size, args.overlap))
    embedder = Embedder()
    index = VectorIndex.build(chunks, embedder)

    answerable = [q["question"] for q in load_questions(args.in_scope)]
    unanswerable = json.loads(Path(args.out_of_scope).read_text(encoding="utf-8"))
    in_scores = [top_score(index, embedder, q) for q in answerable]
    out_scores = [top_score(index, embedder, q) for q in unanswerable]

    print(f"chunk_size={args.chunk_size} overlap={args.overlap} chunks={len(chunks)}")
    print("\nAnswerable questions (top score):")
    for score, q in sorted(zip(in_scores, answerable)):
        print(f"  {score:.2f}  {q}")
    print("\nUnanswerable questions (top score):")
    for score, q in sorted(zip(out_scores, unanswerable), reverse=True):
        print(f"  {score:.2f}  {q}")

    low, high, mid = suggest_threshold(in_scores, out_scores)
    print(f"\nlowest answerable: {low:.2f}   highest unanswerable: {high:.2f}")
    if low > high:
        print(f"Clean gap. A threshold near {mid:.2f} separates them.")
    else:
        print("The ranges overlap, so no single threshold is perfect.")


if __name__ == "__main__":
    main()