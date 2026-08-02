"""Text embedding service.

Uses sentence-transformers when available and falls back to a deterministic
feature-hashing embedding so the API remains functional without the heavy
NLP dependency. Embeddings are cached in-process.
"""

from __future__ import annotations

import hashlib
import logging
import threading

import numpy as np

from app.core.config import settings

logger = logging.getLogger("app.ml.embeddings")

_fallback_dim = max(64, settings.embedding_dim)


def _hash_embedding(text: str, dim: int = _fallback_dim) -> np.ndarray:
    """Deterministic hashed n-gram embedding (bag-of-char-ngrams)."""
    vector = np.zeros(dim, dtype=np.float32)
    normalized = " ".join(text.lower().split())
    grams: set[str] = set()
    for n in (1, 2, 3):
        for i in range(len(normalized) - n + 1):
            grams.add(normalized[i : i + n])
    for gram in grams:
        digest = hashlib.md5(gram.encode()).digest()
        idx = int.from_bytes(digest[:4], "little") % dim
        sign = 1.0 if digest[4] % 2 == 0 else -1.0
        vector[idx] += sign
    norm = np.linalg.norm(vector)
    if norm > 0:
        vector /= norm
    return vector


class EmbeddingService:
    """Lazily-loaded sentence-transformer wrapper with a hashed fallback."""

    _instance: EmbeddingService | None = None
    _lock = threading.Lock()

    def __init__(self) -> None:
        self._model = None
        self._model_name = settings.embedding_model

    @classmethod
    def instance(cls) -> EmbeddingService:
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    @property
    def dimension(self) -> int:
        if self._model is not None:
            return self._model.get_sentence_embedding_dimension()
        return _fallback_dim

    def _get_model(self):
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer

                logger.info("loading embedding model %s", self._model_name)
                self._model = SentenceTransformer(self._model_name)
            except ImportError:
                logger.warning("sentence-transformers not installed; using hashed embeddings")
                self._model = None
        return self._model

    def encode(self, texts: list[str]) -> np.ndarray:
        """Embed a list of texts into a (n, dim) matrix."""
        if not texts:
            return np.zeros((0, self.dimension), dtype=np.float32)
        model = self._get_model()
        if model is not None:
            return np.asarray(model.encode(texts, normalize_embeddings=True), dtype=np.float32)
        return np.vstack([_hash_embedding(t) for t in texts])

    def encode_single(self, text: str) -> np.ndarray:
        """Embed a single text into a (dim,) vector."""
        if not text:
            return np.zeros(self.dimension, dtype=np.float32)
        return self.encode([text])[0]


def cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    """Cosine similarity between two 1-D vectors."""
    a = np.asarray(vec_a, dtype=np.float64)
    b = np.asarray(vec_b, dtype=np.float64)
    denom = (np.linalg.norm(a) * np.linalg.norm(b)) or 1e-9
    return float(np.dot(a, b) / denom)
