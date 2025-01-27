from fastapi import APIRouter
from src.embeddings.embedder import Embedder
from src.index.index_manager import IndexManager

router = APIRouter()
embedder = Embedder()
index_manager = IndexManager(max_elements=20000)

# Load dataset from example_data/documents.txt
with open("example_data/documents.txt", "r") as file:
    documents = [line.strip() for line in file.readlines()]

# Generate embeddings and add them to the index
embeddings = embedder.generate_embeddings(documents)
index_manager.add_embeddings(embeddings)

@router.post("/search/")
async def search(query: str, top_k: int = 5):
    query_embedding = embedder.generate_embeddings([query])
    labels, distances = index_manager.search(query_embedding, top_k)
    return {"documents": [documents[i] for i in labels[0]], "distances": distances[0].tolist()}
