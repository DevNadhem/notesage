import argparse

from .embeddings import Embedder
from .vector_index import VectorIndex


def main(argv=None):
    parser = argparse.ArgumentParser(description="Search a saved NoteSage index.")
    parser.add_argument("index_dir", help="directory created by build_index")
    parser.add_argument("query", help="your question in plain language")
    parser.add_argument("-k", type=int, default=3, help="number of results")
    args = parser.parse_args(argv)

    index = VectorIndex.load(args.index_dir)
    results = index.search(args.query, Embedder(), k=args.k)
    for rank, result in enumerate(results, start=1):
        chunk = result.chunk
        print(f"{rank}. score {result.score:.3f}  {chunk.source} (page {chunk.page})")
        print(f"   {chunk.text[:150]!r}")


if __name__ == "__main__":
    main()