from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np
from typing import List, Dict, Any, Optional
import json
import os
import logging
from src.api.endpoints import router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# Include the API router
app.include_router(router, prefix="/api", tags=["Vector Search"])

# Pydantic models for legacy compatibility
class EmbeddingRequest(BaseModel):
    text: str

@app.get("/")
async def root():
    """Welcome endpoint with API information"""
    return {
        "message": "🚀 Vector Similarity Search API",
        "status": "running",
        "version": "1.0.0",
        "description": "A high-performance RAG-based document retrieval system with LangChain and Hugging Face",
        "features": {
            "vector_search": "✅ HNSWlib for fast similarity search",
            "embeddings": "✅ Hugging Face sentence-transformers",
            "rag_system": "✅ Retrieval-Augmented Generation",
            "api_docs": "✅ Interactive FastAPI documentation"
        },
        "endpoints": {
            "GET /": "This welcome message",
            "GET /health": "Health check",
            "GET /docs": "Interactive API documentation",
            "POST /api/search": "Vector similarity search",
            "POST /api/qa": "Question answering with RAG",
            "GET /api/stats": "Index statistics",
            "POST /api/reindex": "Rebuild vector index"
        },
        "docs_url": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": "2024-12-19T12:00:00Z",
        "version": "1.0.0",
        "system": "RAG-based vector similarity search",
        "components": {
            "embedder": "Hugging Face sentence-transformers",
            "vector_index": "HNSWlib",
            "api": "FastAPI"
        }
    }

# Vercel serverless handler
handler = app

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
