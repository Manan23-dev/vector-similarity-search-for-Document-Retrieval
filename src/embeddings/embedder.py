from sentence_transformers import SentenceTransformer

class Embedder:
    def __init__(self):
        # Force the use of PyTorch explicitly
        self.model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')  # Use 'cuda' if you have a GPU

    def generate_embeddings(self, documents):
        """
        Generate embeddings for a list of documents using PyTorch backend.
        :return: List of embeddings.
        """
        return self.model.encode(documents, convert_to_tensor=False)
