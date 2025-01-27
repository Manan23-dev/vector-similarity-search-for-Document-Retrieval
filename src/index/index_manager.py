import hnswlib
import numpy as np

class IndexManager:
    def __init__(self, dim=384, max_elements=10000):
        self.dim = dim
        self.index = hnswlib.Index(space='cosine', dim=dim)
        self.index.init_index(max_elements=max_elements, ef_construction=200, M=16)
        self.index.set_ef(50)  # Controls search speed vs accuracy

    def add_embeddings(self, embeddings):
        ids = np.arange(len(embeddings))
        self.index.add_items(embeddings, ids)

    def search(self, query_embedding, top_k=5):
        
        return self.index.knn_query(query_embedding, k=top_k)
