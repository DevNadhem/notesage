import json
from dataclasses import asdict
from pathlib import Path

import faiss

from .chunking import Chunk

INDEX_FILE = "index.faiss"
META_FILE = "chunks.json"


class VectorIndex:
    """FAISS index plus the chunk metadata for each stored vector.

    Row i of the index corresponds to chunks[i], so a search hit can be
    turned back into text, source file and page.
    """

    def __init__(self, index, chunks):
        self.index = index
        self.chunks = chunks

    @classmethod
    def build(cls, chunks, embedder):
        """Embed every chunk and store the vectors in an inner-product index."""
        if not chunks:
            raise ValueError("Cannot build an index from zero chunks")
        vectors = embedder.embed_texts([c.text for c in chunks])
        index = faiss.IndexFlatIP(vectors.shape[1])
        index.add(vectors)
        return cls(index, list(chunks))

    def __len__(self):
        return len(self.chunks)