from sentence_transformers import SentenceTransformer
import numpy as np
import logging

logger = logging.getLogger(__name__)

class Embedder:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        """
        Initialize the embedder with a sentence transformer model.
        
        Args:
            model_name (str): Name of the sentence transformer model to use
        """
        try:
            self.model = SentenceTransformer(model_name, device='cpu')
            self.dimension = self.model.get_sentence_embedding_dimension()
            logger.info(f"Initialized embedder with model: {model_name}, dimension: {self.dimension}")
        except Exception as e:
            logger.error(f"Failed to initialize embedder: {e}")
            raise

    def generate_embeddings(self, documents):
        """
        Generate embeddings for a list of documents.
        
        Args:
            documents (list): List of text documents to embed
            
        Returns:
            numpy.ndarray: Array of embeddings with shape (n_documents, embedding_dim)
        """
        try:
            if not documents:
                return np.array([])
            
            # Handle single document case
            if isinstance(documents, str):
                documents = [documents]
            
            embeddings = self.model.encode(
                documents, 
                convert_to_tensor=False,
                show_progress_bar=True if len(documents) > 10 else False
            )
            
            logger.info(f"Generated embeddings for {len(documents)} documents")
            return embeddings
            
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            raise

    def get_embedding_dimension(self):
        """Get the dimension of the embeddings."""
        return self.dimension
