import hnswlib
import numpy as np
import logging
import os
import pickle
from typing import List, Tuple, Optional

logger = logging.getLogger(__name__)

class IndexManager:
    def __init__(self, dim=384, max_elements=10000, index_path: Optional[str] = None):
        """
        Initialize the HNSW index manager.
        
        Args:
            dim (int): Dimension of the embeddings
            max_elements (int): Maximum number of elements the index can hold
            index_path (str): Path to save/load the index
        """
        self.dim = dim
        self.max_elements = max_elements
        self.index_path = index_path
        self.document_ids = []  # Store document IDs for retrieval
        self.documents = []     # Store actual documents
        
        # Initialize HNSW index
        self.index = hnswlib.Index(space='cosine', dim=dim)
        self.index.init_index(
            max_elements=max_elements, 
            ef_construction=200, 
            M=16
        )
        self.index.set_ef(50)  # Controls search speed vs accuracy
        
        logger.info(f"Initialized HNSW index with dim={dim}, max_elements={max_elements}")

    def add_embeddings(self, embeddings: np.ndarray, documents: List[str], document_ids: Optional[List[str]] = None):
        """
        Add embeddings and their corresponding documents to the index.
        
        Args:
            embeddings (np.ndarray): Array of embeddings to add
            documents (List[str]): List of document texts
            document_ids (List[str], optional): List of document IDs. If None, auto-generated.
        """
        try:
            if len(embeddings) != len(documents):
                raise ValueError("Number of embeddings must match number of documents")
            
            # Generate document IDs if not provided
            if document_ids is None:
                start_id = len(self.document_ids)
                document_ids = [f"doc_{start_id + i}" for i in range(len(documents))]
            
            # Add embeddings to index
            ids = np.arange(len(self.document_ids), len(self.document_ids) + len(embeddings))
            self.index.add_items(embeddings, ids)
            
            # Store document metadata
            self.document_ids.extend(document_ids)
            self.documents.extend(documents)
            
            logger.info(f"Added {len(embeddings)} embeddings to index. Total: {len(self.documents)}")
            
        except Exception as e:
            logger.error(f"Failed to add embeddings: {e}")
            raise

    def search(self, query_embedding: np.ndarray, top_k: int = 5) -> Tuple[List[str], List[float], List[str]]:
        """
        Search for similar documents.
        
        Args:
            query_embedding (np.ndarray): Query embedding vector
            top_k (int): Number of top results to return
            
        Returns:
            Tuple[List[str], List[float], List[str]]: (documents, distances, document_ids)
        """
        try:
            if len(self.documents) == 0:
                logger.warning("No documents in index")
                return [], [], []
            
            # Perform search
            labels, distances = self.index.knn_query(query_embedding, k=min(top_k, len(self.documents)))
            
            # Convert labels to document information
            result_documents = [self.documents[label] for label in labels[0]]
            result_ids = [self.document_ids[label] for label in labels[0]]
            
            logger.info(f"Found {len(result_documents)} similar documents")
            return result_documents, distances[0].tolist(), result_ids
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise

    def get_stats(self) -> dict:
        """Get index statistics."""
        return {
            "total_documents": len(self.documents),
            "embedding_dimension": self.dim,
            "max_elements": self.max_elements,
            "current_size": len(self.documents)
        }

    def save_index(self, path: Optional[str] = None):
        """Save the index and metadata to disk."""
        save_path = path or self.index_path
        if not save_path:
            logger.warning("No save path specified")
            return
        
        try:
            # Save HNSW index
            self.index.save_index(save_path + ".hnsw")
            
            # Save metadata
            metadata = {
                'document_ids': self.document_ids,
                'documents': self.documents,
                'dim': self.dim,
                'max_elements': self.max_elements
            }
            
            with open(save_path + ".metadata", 'wb') as f:
                pickle.dump(metadata, f)
            
            logger.info(f"Index saved to {save_path}")
            
        except Exception as e:
            logger.error(f"Failed to save index: {e}")
            raise

    def load_index(self, path: Optional[str] = None):
        """Load the index and metadata from disk."""
        load_path = path or self.index_path
        if not load_path or not os.path.exists(load_path + ".hnsw"):
            logger.warning(f"No index found at {load_path}")
            return
        
        try:
            # Load HNSW index
            self.index.load_index(load_path + ".hnsw")
            
            # Load metadata
            with open(load_path + ".metadata", 'rb') as f:
                metadata = pickle.load(f)
            
            self.document_ids = metadata['document_ids']
            self.documents = metadata['documents']
            self.dim = metadata['dim']
            self.max_elements = metadata['max_elements']
            
            logger.info(f"Index loaded from {load_path}. Documents: {len(self.documents)}")
            
        except Exception as e:
            logger.error(f"Failed to load index: {e}")
            raise
