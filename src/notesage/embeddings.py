import numpy as np

DEFAULT_MODEL = "all-MiniLM-L6-v2"


class Embedder:
    """Turns text into normalized vectors using a sentence-transformers model.

    The model is loaded lazily on first use, so importing this module is
    cheap and tests can avoid loading a model at all.
    """

    def __init__(self, model_name=DEFAULT_MODEL):
        self.model_name = model_name
        self._model = None

    def _load(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.model_name)
        return self._model

    def embed_texts(self, texts):
        """Return a float32 array of shape (len(texts), dim), L2-normalized."""
        if not texts:
            return np.zeros((0, 0), dtype="float32")
        vectors = self._load().encode(
            list(texts),
            convert_to_numpy=True,
            normalize_embeddings=True,
        )
        return vectors.astype("float32")

    def embed_query(self, query):
        """Return a 1 x dim array for a single query string."""
        return self.embed_texts([query])