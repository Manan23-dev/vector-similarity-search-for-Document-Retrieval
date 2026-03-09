import logging
from sentence_transformers import SentenceTransformer
from typing import List, Union, Dict, Any, Optional
import numpy as np
from tqdm import tqdm
import torch
import os
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Embedder:
    def __init__(self, model_name: str = "all-mpnet-base-v2", use_cache: bool = True, cache_size: int = 500):
        """
        Initialize the embedder with a sentence transformer model.
        UPDATED: Using all-mpnet-base-v2 for better performance (768 dimensions)
        
        Args:
            model_name: Name of the sentence transformer model to use
            use_cache: Enable LRU cache for query embeddings (reduces latency on repeated queries)
            cache_size: Max cached query embeddings when use_cache=True
        """
        try:
            self.model_name = model_name
            self.model = SentenceTransformer(model_name, device='cpu')
            self.embedding_dim = self.get_embedding_dimension()
            self._use_cache = use_cache
            self._cache = None
            if use_cache:
                try:
                    from src.utils.embedding_cache import EmbeddingCache
                    self._cache = EmbeddingCache(max_size=cache_size)
                except ImportError:
                    pass
            logger.info(f"Initialized embedder with model: {model_name} (cache={'on' if self._cache else 'off'})")
            logger.info(f"Embedding dimension: {self.embedding_dim}")
        except Exception as e:
            logger.error(f"Failed to initialize embedder: {e}")
            raise
    
    def generate_embeddings(self, texts: Union[str, List[str]], 
                          batch_size: int = 32, 
                          show_progress: bool = True,
                          use_cache: Optional[bool] = None) -> np.ndarray:
        """
        Generate embeddings for the given text(s).
        UPDATED: Optimized for large-scale processing with query embedding cache.
        
        Args:
            texts: Single text string or list of text strings
            batch_size: Batch size for processing
            show_progress: Whether to show progress bar
            use_cache: Override instance cache setting (None = use instance default)
            
        Returns:
            Numpy array of embeddings
        """
        try:
            if isinstance(texts, str):
                texts = [texts]
            
            if not texts:
                return np.array([])
            
            cache = self._cache if (use_cache if use_cache is not None else self._use_cache) else None
            if cache and len(texts) == 1:
                cached = cache.get(texts[0])
                if cached is not None:
                    return cached
            elif cache and len(texts) > 1 and len(texts) <= 20:
                results = []
                to_compute = []
                to_compute_idx = []
                for i, t in enumerate(texts):
                    c = cache.get(t)
                    if c is not None:
                        results.append((i, c))
                    else:
                        to_compute.append(t)
                        to_compute_idx.append(i)
                if not to_compute:
                    return np.vstack([r[1] for r in sorted(results, key=lambda x: x[0])])
                computed = self.model.encode(
                    to_compute,
                    convert_to_numpy=True,
                    show_progress_bar=show_progress,
                    batch_size=batch_size,
                )
                for j, emb in enumerate(computed):
                    cache.set(to_compute[j], emb.reshape(1, -1) if emb.ndim == 1 else emb)
                idx_to_emb = {to_compute_idx[j]: computed[j] for j in range(len(computed))}
                combined = [None] * len(texts)
                for i, emb in results:
                    combined[i] = emb if emb.ndim == 2 else emb.reshape(1, -1)
                for i, emb in idx_to_emb.items():
                    combined[i] = emb.reshape(1, -1) if emb.ndim == 1 else emb
                return np.vstack(combined)
            
            logger.info(f"Generating embeddings for {len(texts)} texts")
            
            # Generate embeddings with progress bar for large batches
            if len(texts) > batch_size and show_progress:
                embeddings = []
                for i in tqdm(range(0, len(texts), batch_size), desc="Generating embeddings"):
                    batch = texts[i:i + batch_size]
                    batch_embeddings = self.model.encode(
                        batch, 
                        convert_to_numpy=True,
                        show_progress_bar=False,
                        batch_size=batch_size
                    )
                    embeddings.append(batch_embeddings)
                embeddings = np.vstack(embeddings)
            else:
                embeddings = self.model.encode(
                    texts, 
                    convert_to_numpy=True,
                    show_progress_bar=show_progress,
                    batch_size=batch_size
                )
            
            logger.info(f"Generated embeddings with shape: {embeddings.shape}")
            if cache and len(texts) == 1:
                cache.set(texts[0], embeddings)
            return embeddings
            
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            raise
    
    def generate_paper_embeddings(self, papers: List[Dict[str, Any]]) -> np.ndarray:
        """
        Generate embeddings for research papers.
        UPDATED: Specialized method for paper processing
        
        Args:
            papers: List of paper dictionaries
            
        Returns:
            Numpy array of embeddings
        """
        logger.info(f"Generating embeddings for {len(papers)} papers")
        
        # Combine title and abstract for better representation
        combined_texts = []
        for paper in papers:
            title = paper.get("title", "")
            abstract = paper.get("abstract", "")
            # Combine title and abstract with special separator
            combined_text = f"{title} [SEP] {abstract}"
            combined_texts.append(combined_text)
        
        return self.generate_embeddings(combined_texts)
    
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of embeddings produced by this model.
        
        Returns:
            Embedding dimension
        """
        try:
            # Generate a dummy embedding to get the dimension
            dummy_embedding = self.model.encode(["dummy text"])
            return dummy_embedding.shape[1]
        except Exception as e:
            logger.error(f"Failed to get embedding dimension: {e}")
            return 384  # fallback to MiniLM dimension
    
    def save_model(self, path: str):
        """Save the model to disk"""
        try:
            self.model.save(path)
            logger.info(f"Model saved to {path}")
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
            raise
    
    def load_model(self, path: str):
        """Load the model from disk"""
        try:
            self.model = SentenceTransformer(path)
            self.embedding_dim = self.get_embedding_dimension()
            logger.info(f"Model loaded from {path}")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        info = {
            "model_name": self.model_name,
            "embedding_dimension": self.embedding_dim,
            "max_seq_length": self.model.max_seq_length,
            "device": str(self.model.device),
        }
        if self._cache:
            info["embedding_cache"] = self._cache.stats()
        return info