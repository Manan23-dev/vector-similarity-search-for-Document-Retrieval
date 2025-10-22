import logging
import hnswlib
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
import json
import pickle
from pathlib import Path
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IndexManager:
    def __init__(self, embedding_dim: int, index_path: str = "data/vector_index"):
        """
        Initialize the HNSWlib index manager.
        UPDATED: Proper HNSWlib implementation for scalable vector search
        
        Args:
            embedding_dim: Dimension of the embeddings
            index_path: Path to save/load the index
        """
        self.embedding_dim = embedding_dim
        self.index_path = Path(index_path)
        self.index_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize HNSWlib index
        self.index = hnswlib.Index(space='cosine', dim=embedding_dim)
        
        # Metadata storage
        self.document_ids = []
        self.documents = []
        self.is_initialized = False
        
        logger.info(f"Initialized IndexManager with embedding dimension: {embedding_dim}")
    
    def add_embeddings(self, embeddings: np.ndarray, document_ids: List[str], 
                      documents: List[Dict[str, Any]], 
                      ef_construction: int = 200, 
                      M: int = 16) -> None:
        """
        Add embeddings to the HNSWlib index.
        UPDATED: Proper HNSWlib configuration for large-scale search
        
        Args:
            embeddings: Numpy array of embeddings
            document_ids: List of document IDs
            documents: List of document dictionaries
            ef_construction: Construction parameter for HNSWlib
            M: Maximum number of bi-directional links for each node
        """
        try:
            if len(embeddings) == 0:
                logger.warning("No embeddings to add")
                return
            
            logger.info(f"Adding {len(embeddings)} embeddings to HNSWlib index")
            
            # Initialize index with first batch
            if not self.is_initialized:
                self.index.init_index(
                    max_elements=len(embeddings),
                    ef_construction=ef_construction,
                    M=M
                )
                self.is_initialized = True
                logger.info(f"Initialized HNSWlib index with max_elements={len(embeddings)}")
            
            # Add embeddings to index
            self.index.add_items(embeddings, document_ids)
            
            # Store metadata
            self.document_ids.extend(document_ids)
            self.documents.extend(documents)
            
            logger.info(f"Successfully added {len(embeddings)} embeddings to index")
            
        except Exception as e:
            logger.error(f"Failed to add embeddings: {e}")
            raise
    
    def search(self, query_embedding: np.ndarray, k: int = 10, 
               ef: int = 50) -> Tuple[List[str], List[float], List[Dict[str, Any]]]:
        """
        Search for similar documents using HNSWlib.
        UPDATED: Optimized search with proper ef parameter
        
        Args:
            query_embedding: Query embedding vector
            k: Number of results to return
            ef: Search parameter (higher = more accurate but slower)
            
        Returns:
            Tuple of (document_ids, distances, documents)
        """
        try:
            if not self.is_initialized:
                logger.warning("Index not initialized")
                return [], [], []
            
            # Set ef parameter for search
            self.index.set_ef(ef)
            
            # Perform search
            indices, distances = self.index.knn_query(query_embedding, k=k)
            
            # Convert indices to document IDs and get documents
            result_ids = [self.document_ids[i] for i in indices[0]]
            result_distances = distances[0].tolist()
            result_documents = [self.documents[i] for i in indices[0]]
            
            logger.info(f"Found {len(result_ids)} similar documents")
            return result_ids, result_distances, result_documents
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return [], [], []
    
    def search_with_threshold(self, query_embedding: np.ndarray, k: int = 10, 
                            threshold: float = 0.0, ef: int = 50) -> Tuple[List[str], List[float], List[Dict[str, Any]]]:
        """
        Search for similar documents with similarity threshold.
        UPDATED: Threshold-based filtering
        
        Args:
            query_embedding: Query embedding vector
            k: Maximum number of results to return
            threshold: Minimum similarity threshold (0-1)
            ef: Search parameter
            
        Returns:
            Tuple of (document_ids, distances, documents)
        """
        try:
            # Get more results than needed to filter by threshold
            search_k = min(k * 3, len(self.document_ids))
            indices, distances = self.index.knn_query(query_embedding, k=search_k)
            
            # Convert distances to similarities (1 - distance for cosine similarity)
            similarities = 1 - distances[0]
            
            # Filter by threshold
            valid_indices = similarities >= threshold
            
            # Limit to k results
            valid_indices = valid_indices[:k]
            
            result_ids = [self.document_ids[indices[0][i]] for i in range(len(valid_indices)) if valid_indices[i]]
            result_distances = distances[0][valid_indices].tolist()
            result_documents = [self.documents[indices[0][i]] for i in range(len(valid_indices)) if valid_indices[i]]
            
            logger.info(f"Found {len(result_ids)} documents above threshold {threshold}")
            return result_ids, result_distances, result_documents
            
        except Exception as e:
            logger.error(f"Threshold search failed: {e}")
            return [], [], []
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the index.
        UPDATED: Comprehensive statistics
        
        Returns:
            Dictionary with index statistics
        """
        try:
            stats = {
                "total_documents": len(self.document_ids),
                "embedding_dimension": self.embedding_dim,
                "is_initialized": self.is_initialized,
                "index_path": str(self.index_path),
                "max_elements": self.index.get_max_elements() if self.is_initialized else 0,
                "current_count": self.index.get_current_count() if self.is_initialized else 0,
                "ef_construction": self.index.get_ef_construction() if self.is_initialized else 0,
                "M": self.index.get_M() if self.is_initialized else 0
            }
            
            # Add document source statistics
            if self.documents:
                sources = {}
                for doc in self.documents:
                    source = doc.get("source", "unknown")
                    sources[source] = sources.get(source, 0) + 1
                stats["sources"] = sources
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {"error": str(e)}
    
    def save_index(self) -> None:
        """
        Save the HNSWlib index and metadata to disk.
        UPDATED: Proper serialization
        
        """
        try:
            if not self.is_initialized:
                logger.warning("No index to save")
                return
            
            # Save HNSWlib index
            index_file = self.index_path / "hnswlib_index.bin"
            self.index.save_index(str(index_file))
            
            # Save metadata
            metadata = {
                "document_ids": self.document_ids,
                "documents": self.documents,
                "embedding_dim": self.embedding_dim,
                "is_initialized": self.is_initialized
            }
            
            metadata_file = self.index_path / "metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Index saved to {self.index_path}")
            
        except Exception as e:
            logger.error(f"Failed to save index: {e}")
            raise
    
    def load_index(self) -> bool:
        """
        Load the HNSWlib index and metadata from disk.
        UPDATED: Proper deserialization
        
        Returns:
            True if successful, False otherwise
        """
        try:
            index_file = self.index_path / "hnswlib_index.bin"
            metadata_file = self.index_path / "metadata.json"
            
            if not index_file.exists() or not metadata_file.exists():
                logger.warning("Index files not found")
                return False
            
            # Load metadata
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            self.document_ids = metadata["document_ids"]
            self.documents = metadata["documents"]
            self.embedding_dim = metadata["embedding_dim"]
            
            # Load HNSWlib index
            self.index.load_index(str(index_file))
            self.is_initialized = True
            
            logger.info(f"Index loaded from {self.index_path}")
            logger.info(f"Loaded {len(self.document_ids)} documents")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load index: {e}")
            return False
    
    def rebuild_index(self, embeddings: np.ndarray, document_ids: List[str], 
                     documents: List[Dict[str, Any]], 
                     ef_construction: int = 200, M: int = 16) -> None:
        """
        Rebuild the entire index from scratch.
        UPDATED: Complete rebuild functionality
        
        Args:
            embeddings: All embeddings to index
            document_ids: All document IDs
            documents: All document dictionaries
            ef_construction: Construction parameter
            M: Maximum number of bi-directional links
        """
        try:
            logger.info("Rebuilding HNSWlib index from scratch")
            
            # Clear existing data
            self.document_ids = []
            self.documents = []
            self.is_initialized = False
            
            # Initialize new index
            self.index = hnswlib.Index(space='cosine', dim=self.embedding_dim)
            self.index.init_index(
                max_elements=len(embeddings),
                ef_construction=ef_construction,
                M=M
            )
            
            # Add all embeddings
            self.add_embeddings(embeddings, document_ids, documents, ef_construction, M)
            
            logger.info("Index rebuild completed")
            
        except Exception as e:
            logger.error(f"Failed to rebuild index: {e}")
            raise