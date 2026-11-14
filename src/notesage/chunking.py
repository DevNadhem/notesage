from dataclasses import dataclass
from pathlib import Path

from .loaders import load_document


@dataclass(frozen=True)
class Chunk:
    """A piece of a document, with what a citation will need later."""

    text: str
    source: str
    page: int
    chunk_id: str

    
def chunk_text(text, chunk_size=500, overlap=50):
    """Split text into chunks of up to `chunk_size` characters.

    Consecutive chunks share `overlap` characters, so a sentence cut at a
    boundary still appears whole in at least one chunk.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be >= 0 and smaller than chunk_size")

    text = text.strip()
    if not text:
        return []

    step = chunk_size - overlap
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        piece = text[start:end].strip()
        if piece:
            chunks.append(piece)
        if end >= len(text):
            break
        start += step
    return chunks

def chunk_document(path, chunk_size=500, overlap=50):
    """Load a document and return a list of Chunk objects."""
    source = Path(path).name
    chunks = []
    index = 0
    for page, text in load_document(path):
        for piece in chunk_text(text, chunk_size, overlap):
            chunks.append(
                Chunk(
                    text=piece,
                    source=source,
                    page=page,
                    chunk_id=f"{source}-p{page}-c{index}",
                )
            )
            index += 1
    return chunks