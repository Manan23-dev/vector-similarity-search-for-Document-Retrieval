import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np
from typing import List, Optional
import json

app = FastAPI(
    title="Vector Similarity Search API",
    description="A high-performance document retrieval system",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class SearchQuery(BaseModel):
    query: str
    top_k: int = 5

class EmbedRequest(BaseModel):
    text: str

# Global variables for models (loaded lazily)
model = None
index = None

def load_model():
    """Load the model lazily"""
    global model
    if model is None:
        try:
            # Try to import and load sentence transformers
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer('all-MiniLM-L6-v2')
        except ImportError:
            # Fallback: use a simple mock for demonstration
            model = "mock_model"
    return model

def load_index():
    """Load or create the HNSW index"""
    global index
    if index is None:
        try:
            import hnswlib
            # Create a simple index for demonstration
            index = hnswlib.Index(space='cosine', dim=384)
            index.init_index(max_elements=1000, ef_construction=200, M=16)
        except ImportError:
            # Mock index for demonstration
            index = {"type": "mock_index", "data": []}
    return index

@app.get("/")
async def root():
    return {
        "message": "Vector Similarity Search API", 
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

@app.post("/embed")
async def create_embedding(request: EmbedRequest):
    """Create embeddings for text"""
    try:
        model = load_model()
        if model == "mock_model":
            # Return mock embedding for demonstration
            return {
                "text": request.text,
                "embedding": np.random.rand(384).tolist(),
                "note": "This is a mock embedding for demonstration"
            }
        
        embedding = model.encode([request.text])[0]
        return {
            "text": request.text,
            "embedding": embedding.tolist()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating embedding: {str(e)}")

@app.post("/search")
async def similarity_search(request: SearchQuery):
    """Perform similarity search"""
    try:
        # For demonstration, return mock results
        return {
            "query": request.query,
            "results": [
                {
                    "text": f"Sample document {i+1} related to: {request.query}",
                    "score": 0.9 - (i * 0.1),
                    "id": i+1
                }
                for i in range(min(request.top_k, 3))
            ],
            "note": "These are mock results for demonstration"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in search: {str(e)}")

@app.get("/info")
async def get_info():
    """Get API information"""
    return {
        "api_name": "Vector Similarity Search",
        "version": "1.0.0",
        "endpoints": {
            "POST /embed": "Create text embeddings",
            "POST /search": "Perform similarity search",
            "GET /health": "Health check",
            "GET /docs": "API documentation"
        }
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
