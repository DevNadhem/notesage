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

    def save(self, directory):
        """Write the FAISS index and chunk metadata into `directory`."""
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(directory / INDEX_FILE))
        data = [asdict(chunk) for chunk in self.chunks]
        (directory / META_FILE).write_text(
            json.dumps(data, indent=2), encoding="utf-8"
        )

    @classmethod
    def load(cls, directory):
        """Load an index previously written by `save`."""
        directory = Path(directory)
        index_path = directory / INDEX_FILE
        meta_path = directory / META_FILE
        if not index_path.exists() or not meta_path.exists():
            raise FileNotFoundError(f"No saved index found in: {directory}")

        index = faiss.read_index(str(index_path))
        raw = json.loads(meta_path.read_text(encoding="utf-8"))
        chunks = [Chunk(**item) for item in raw]
        if index.ntotal != len(chunks):
            raise ValueError(
                f"Index has {index.ntotal} vectors but {len(chunks)} chunks; "
                "the saved files do not match"
            )
        return cls(index, chunks)