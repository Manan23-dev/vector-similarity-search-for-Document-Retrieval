"""
LRU cache for query embeddings to avoid recomputation on repeated queries.
Improves latency and reduces CPU load for popular search terms.
"""

import hashlib
import logging
import threading
from collections import OrderedDict
from typing import Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


class EmbeddingCache:
    """Thread-safe LRU cache for embeddings. Key: query hash, Value: embedding array."""

    def __init__(self, max_size: int = 500):
        self._cache: OrderedDict[str, np.ndarray] = OrderedDict()
        self._max_size = max(1, max_size)
        self._lock = threading.RLock()
        self._hits = 0
        self._misses = 0

    def _key(self, text: str) -> str:
        normalized = text.strip().lower()
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:32]

    def get(self, text: str) -> Optional[np.ndarray]:
        k = self._key(text)
        with self._lock:
            if k in self._cache:
                self._cache.move_to_end(k)
                self._hits += 1
                return self._cache[k].copy()
            self._misses += 1
            return None

    def set(self, text: str, embedding: np.ndarray) -> None:
        k = self._key(text)
        with self._lock:
            if k in self._cache:
                self._cache.move_to_end(k)
            else:
                while len(self._cache) >= self._max_size and self._cache:
                    self._cache.popitem(last=False)
            self._cache[k] = embedding.copy()

    def stats(self) -> dict:
        with self._lock:
            total = self._hits + self._misses
            hit_rate = self._hits / total if total > 0 else 0.0
            return {
                "size": len(self._cache),
                "max_size": self._max_size,
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": round(hit_rate, 4),
            }
