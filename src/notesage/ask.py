import argparse

from .answer import answer_question
from .config import DEFAULT_K, MIN_SCORE
from .embeddings import Embedder
from .llm import LLMError, OllamaClient
from .vector_index import VectorIndex


def main(argv=None):
    parser = argparse.ArgumentParser(description="Ask a question about your notes.")
    parser.add_argument("index_dir", help="directory created by build_index")
    parser.add_argument("question", help="your question in plain language")
    parser.add_argument("-k", type=int, default=DEFAULT_K, help="chunks to retrieve")
    parser.add_argument("--min-score", type=float, default=MIN_SCORE)
    parser.add_argument("--model", default="llama3.2", help="Ollama model name")
    args = parser.parse_args(argv)

    index = VectorIndex.load(args.index_dir)
    try:
        result = answer_question(
            args.question,
            index,
            Embedder(),
            OllamaClient(model=args.model),
            k=args.k,
            min_score=args.min_score,
        )
    except LLMError as exc:
        parser.exit(1, f"Error: {exc}\n")

    print(result.text)
    if result.found:
        print("\nSources:")
        for source in result.sources:
            chunk = source.chunk
            print(f"  - {chunk.source}, page {chunk.page} (score {source.score:.2f})")


if __name__ == "__main__":
    main()