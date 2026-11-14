import argparse

from .chunking import chunk_document


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Load a document and show how it gets chunked."
    )
    parser.add_argument("path", help="path to a .pdf, .txt or .md file")
    parser.add_argument("--chunk-size", type=int, default=500)
    parser.add_argument("--overlap", type=int, default=50)
    args = parser.parse_args(argv)

    chunks = chunk_document(args.path, args.chunk_size, args.overlap)
    print(f"{len(chunks)} chunks from {args.path}")
    for chunk in chunks[:3]:
        print(f"[{chunk.chunk_id}] page {chunk.page}: {chunk.text[:80]!r}")


if __name__ == "__main__":
    main()