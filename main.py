from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np
from typing import List, Dict, Any, Optional
import json
import os

app = FastAPI(
    title="Vector Similarity Search API",
    description="A high-performance document retrieval system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class SearchRequest(BaseModel):
    query: str
    top_k: int = 5
    threshold: float = 0.5

class Document(BaseModel):
    id: str
    content: str
    metadata: Optional[Dict[str, Any]] = {}

class SearchResult(BaseModel):
    document: Document
    score: float

class EmbeddingRequest(BaseModel):
    text: str

# Mock document database
MOCK_DOCUMENTS = [
    {
        "id": "doc_001", 
        "content": "Introduction to machine learning algorithms and their applications in data science",
        "metadata": {"category": "AI/ML", "author": "Dr. Smith", "year": 2024}
    },
    {
        "id": "doc_002",
        "content": "Deep learning neural networks for computer vision and natural language processing",
        "metadata": {"category": "Deep Learning", "author": "Prof. Johnson", "year": 2024}
    },
    {
        "id": "doc_003",
        "content": "Python programming fundamentals for beginners with practical examples",
        "metadata": {"category": "Programming", "author": "Jane Doe", "year": 2023}
    },
    {
        "id": "doc_004",
        "content": "Vector similarity search and information retrieval systems overview",
        "metadata": {"category": "Information Retrieval", "author": "Alex Chen", "year": 2024}
    },
    {
        "id": "doc_005",
        "content": "FastAPI framework for building high-performance REST APIs with Python",
        "metadata": {"category": "Web Development", "author": "Mike Wilson", "year": 2024}
    },
    {
        "id": "doc_006",
        "content": "HNSWlib library for efficient approximate nearest neighbor search",
        "metadata": {"category": "Search Algorithms", "author": "Dr. Brown", "year": 2023}
    },
    {
        "id": "doc_007",
        "content": "Sentence transformers for semantic text embedding and similarity",
        "metadata": {"category": "NLP", "author": "Sarah Lee", "year": 2024}
    },
    {
        "id": "doc_008",
        "content": "PyTorch deep learning framework tutorial and best practices",
        "metadata": {"category": "Deep Learning", "author": "David Kim", "year": 2024}
    }
]

def calculate_similarity(query: str, document: str) -> float:
    """
    Simple keyword-based similarity calculation for demonstration.
    In production, this would use vector embeddings.
    """
    query_words = set(query.lower().split())
    doc_words = set(document.lower().split())
    
    if not query_words or not doc_words:
        return 0.0
    
    # Calculate Jaccard similarity
    intersection = query_words & doc_words
    union = query_words | doc_words
    
    jaccard_sim = len(intersection) / len(union) if union else 0.0
    
    # Add some weighted scoring for exact phrase matches
    phrase_bonus = 0.0
    if query.lower() in document.lower():
        phrase_bonus = 0.3
    
    # Combine scores
    final_score = min(jaccard_sim + phrase_bonus + np.random.uniform(0, 0.1), 1.0)
    return round(final_score, 3)

@app.get("/")
async def root():
    """Welcome endpoint with API information"""
    return {
        "message": "🚀 Vector Similarity Search API",
        "status": "running",
        "version": "1.0.0",
        "description": "A high-performance document retrieval system",
        "endpoints": {
            "GET /": "This welcome message",
            "GET /health": "Health check",
            "GET /docs": "Interactive API documentation",
            "GET /documents": "List all available documents",
            "POST /search": "Search for similar documents",
            "POST /embed": "Generate text embeddings (mock)",
            "GET /stats": "API usage statistics"
        },
        "docs_url": "/docs",
        "total_documents": len(MOCK_DOCUMENTS)
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": "2024-06-01T12:00:00Z",
        "version": "1.0.0",
        "database_status": "connected",
        "documents_loaded": len(MOCK_DOCUMENTS)
    }

@app.get("/documents")
async def get_documents():
    """Get all available documents"""
    return {
        "documents": MOCK_DOCUMENTS,
        "total_count": len(MOCK_DOCUMENTS),
        "categories": list(set(doc["metadata"].get("category", "Unknown") for doc in MOCK_DOCUMENTS))
    }

@app.get("/documents/{doc_id}")
async def get_document(doc_id: str):
    """Get a specific document by ID"""
    document = next((doc for doc in MOCK_DOCUMENTS if doc["id"] == doc_id), None)
    if not document:
        raise HTTPException(status_code=404, detail=f"Document with ID '{doc_id}' not found")
    return {"document": document}

@app.post("/search")
async def search_documents(request: SearchRequest):
    """
    Search for documents similar to the query.
    This demo uses keyword-based similarity. In production, 
    this would use vector embeddings with HNSWlib.
    """
    try:
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        results = []
        
        for doc in MOCK_DOCUMENTS:
            similarity_score = calculate_similarity(request.query, doc["content"])
            
            if similarity_score >= request.threshold:
                results.append({
                    "document": doc,
                    "score": similarity_score
                })
        
        # Sort by similarity score (highest first)
        results.sort(key=lambda x: x["score"], reverse=True)
        
        # Limit to top_k results
        top_results = results[:request.top_k]
        
        return {
            "query": request.query,
            "results": top_results,
            "total_found": len(results),
            "returned": len(top_results),
            "threshold_used": request.threshold,
            "note": "Demo using keyword similarity. Production version would use vector embeddings."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.post("/embed")
async def create_embedding(request: EmbeddingRequest):
    """
    Generate text embedding (mock implementation).
    In production, this would use sentence-transformers.
    """
    try:
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        # Generate mock 384-dimensional embedding
        # In production: model.encode(request.text)
        mock_embedding = np.random.rand(384).tolist()
        
        return {
            "text": request.text,
            "embedding": mock_embedding,
            "dimensions": 384,
            "model": "mock-sentence-transformer",
            "note": "This is a mock embedding for demonstration. Production would use real sentence-transformers."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Embedding generation failed: {str(e)}")

@app.get("/stats")
async def get_stats():
    """Get API statistics"""
    categories = {}
    for doc in MOCK_DOCUMENTS:
        category = doc["metadata"].get("category", "Unknown")
        categories[category] = categories.get(category, 0) + 1
    
    return {
        "total_documents": len(MOCK_DOCUMENTS),
        "categories": categories,
        "api_version": "1.0.0",
        "features": {
            "search": "✅ Keyword-based similarity",
            "embeddings": "✅ Mock embeddings (384-dim)",
            "filtering": "🔄 Coming soon",
            "real_vectors": "🔄 Use Railway/Render for full ML stack"
        }
    }

@app.get("/demo")
async def demo_endpoint():
    """Demo endpoint with example usage"""
    return {
        "message": "API Demo Examples",
        "examples": {
            "search": {
                "method": "POST",
                "url": "/search",
                "body": {
                    "query": "machine learning",
                    "top_k": 3,
                    "threshold": 0.3
                }
            },
            "embed": {
                "method": "POST", 
                "url": "/embed",
                "body": {
                    "text": "Vector similarity search"
                }
            },
            "get_document": {
                "method": "GET",
                "url": "/documents/doc_001"
            }
        },
        "try_it": "Visit /docs for interactive API testing"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
