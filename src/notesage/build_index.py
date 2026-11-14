import argparse

from .chunking import chunk_document
from .embeddings import Embedder
from .vector_index import VectorIndex


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Build a searchable index from documents."
    )
    parser.add_argument("paths", nargs="+", help=".pdf, .txt or .md files")
    parser.add_argument("--out", default="data/index", help="index directory")
    parser.add_argument("--chunk-size", type=int, default=500)
    parser.add_argument("--overlap", type=int, default=50)
    args = parser.parse_args(argv)

    chunks = []
    for path in args.paths:
        chunks.extend(chunk_document(path, args.chunk_size, args.overlap))
    if not chunks:
        parser.error("no text could be extracted from the given files")

    index = VectorIndex.build(chunks, Embedder())
    index.save(args.out)
    print(f"Indexed {len(index)} chunks from {len(args.paths)} file(s) into {args.out}")


if __name__ == "__main__":
    main()