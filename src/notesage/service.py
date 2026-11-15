import tempfile
from pathlib import Path

from .chunking import chunk_document
from .config import DEFAULT_K, MIN_SCORE
from .loaders import SUPPORTED_EXTENSIONS
from .vector_index import VectorIndex

MAX_FILE_MB = 20


class NoteSageError(Exception):
    """A problem the user can fix, with a message safe to show in the UI."""


def build_index_from_uploads(files, embedder, chunk_size=300, overlap=50):
    """Build an index from uploaded files.

    `files` is a list of (filename, bytes) pairs. Returns (index, skipped),
    where skipped lists files that could not be used and why.
    """
    if not files:
        raise NoteSageError("Upload at least one file first.")

    chunks, skipped = [], []
    with tempfile.TemporaryDirectory() as tmp:
        for name, data in files:
            suffix = Path(name).suffix.lower()
            if len(data) > MAX_FILE_MB * 1024 * 1024:
                skipped.append(f"{name}: larger than {MAX_FILE_MB} MB")
                continue
            if suffix not in SUPPORTED_EXTENSIONS:
                skipped.append(f"{name}: unsupported type '{suffix}'")
                continue
            path = Path(tmp) / Path(name).name
            path.write_bytes(data)
            try:
                file_chunks = chunk_document(path, chunk_size, overlap)
            except Exception as exc:  # corrupt PDFs raise many different errors
                skipped.append(f"{name}: could not be read ({exc})")
                continue
            if not file_chunks:
                skipped.append(f"{name}: no text found (scanned PDF or empty file)")
                continue
            chunks.extend(file_chunks)

    if not chunks:
        raise NoteSageError("No readable text was found. " + "; ".join(skipped))
    return VectorIndex.build(chunks, embedder), skipped