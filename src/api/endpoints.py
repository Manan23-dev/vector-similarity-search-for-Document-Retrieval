from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.embeddings.embedder import Embedder
from src.index.index_manager import IndexManager
from data_loader import ResearchPaperDataLoader, DATA_CONFIG

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize components
embedder = Embedder("all-mpnet-base-v2")  # Use better model
index_manager = IndexManager(
    embedding_dim=embedder.get_embedding_dimension(), 
    index_path="data/vector_index"
)

# Pydantic models
class SearchRequest(BaseModel):
    query: str
    top_k: int = 5
    threshold: float = 0.0

class SearchResult(BaseModel):
    document: str
    document_id: str
    score: float
    distance: float
    title: Optional[str] = None
    authors: Optional[List[str]] = None
    venue: Optional[str] = None
    year: Optional[int] = None
    url: Optional[str] = None

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    total_found: int
    returned: int

class QAResponse(BaseModel):
    question: str
    answer: str
    sources: List[SearchResult]
    context_used: str

# Load documents and build index
def initialize_index():
    """Initialize the vector index with real research papers."""
    try:
        logger.info("🚀 Initializing vector index with real research papers...")
        
        # Try to load existing index first
        if index_manager.load_index():
            logger.info(f"✅ Loaded existing index with {len(index_manager.documents)} papers")
            return True
        
        # Load papers from all sources
        data_loader = ResearchPaperDataLoader("data")
        papers = data_loader.load_all_sources(DATA_CONFIG)
        
        if not papers:
            logger.error("❌ No papers loaded from any source")
            return False
        
        logger.info(f"📚 Loaded {len(papers)} papers from data sources")
        
        # Generate embeddings for all papers
        logger.info("🔄 Generating embeddings...")
        embeddings = embedder.generate_paper_embeddings(papers)
        
        # Extract document IDs and texts
        document_ids = [paper["id"] for paper in papers]
        documents = [f"{paper['title']} [SEP] {paper['abstract']}" for paper in papers]
        
        # Add to HNSWlib index
        logger.info("🔍 Building HNSWlib vector index...")
        index_manager.add_embeddings(
            embeddings=embeddings,
            document_ids=document_ids,
            documents=papers,
            ef_construction=200,
            M=16
        )
        
        # Save the index
        index_manager.save_index()
        
        logger.info(f"✅ Index initialized successfully with {len(papers)} papers")
        logger.info(f"📊 Embedding dimension: {embedder.get_embedding_dimension()}")
        logger.info(f"🎯 Index type: HNSWlib")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize index: {e}")
        return False

# Initialize index on startup
if not initialize_index():
    logger.error("❌ Failed to initialize vector index")

@router.post("/search", response_model=SearchResponse)
async def search_documents(request: SearchRequest):
    """
    Search for research papers similar to the query using vector similarity.
    """
    try:
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        logger.info(f"🔍 Searching for: '{request.query}'")
        
        # Generate query embedding
        query_embedding = embedder.generate_embeddings([request.query])
        
        # Search for similar documents
        document_ids, distances, documents = index_manager.search(
            query_embedding[0], 
            k=request.top_k,
            ef=50
        )
        
        # Convert distances to similarity scores (1 - distance for cosine similarity)
        scores = [1 - distance for distance in distances]
        
        # Filter by threshold and create results
        filtered_results = []
        for doc_id, doc, score, distance in zip(document_ids, documents, scores, distances):
            if score >= request.threshold:
                filtered_results.append(SearchResult(
                    document=f"{doc['title']} [SEP] {doc['abstract']}",
                    document_id=doc_id,
                    score=round(score, 4),
                    distance=round(distance, 4),
                    title=doc.get('title', ''),
                    authors=doc.get('authors', []),
                    venue=doc.get('venue', ''),
                    year=doc.get('year', None),
                    url=doc.get('url', '')
                ))
        
        logger.info(f"📊 Found {len(filtered_results)} results for '{request.query}'")
        
        return SearchResponse(
            query=request.query,
            results=filtered_results,
            total_found=len(filtered_results),
            returned=len(filtered_results)
        )
        
    except Exception as e:
        logger.error(f"❌ Search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.post("/qa", response_model=QAResponse)
async def question_answering(request: SearchRequest):
    """
    Answer questions using RAG (Retrieval-Augmented Generation).
    """
    try:
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        logger.info(f"🤖 Q&A for: '{request.query}'")
        
        # Retrieve relevant documents
        query_embedding = embedder.generate_embeddings([request.query])
        document_ids, distances, documents = index_manager.search(
            query_embedding[0], 
            k=min(request.top_k, 5)
        )
        
        if not documents:
            return QAResponse(
                question=request.query,
                answer="I couldn't find any relevant research papers to answer your question.",
                sources=[],
                context_used=""
            )
        
        # Create sources
        sources = []
        context_parts = []
        
        for doc_id, doc, distance in zip(document_ids, documents, distances):
            score = 1 - distance
            sources.append(SearchResult(
                document=f"{doc['title']} [SEP] {doc['abstract']}",
                document_id=doc_id,
                score=round(score, 4),
                distance=round(distance, 4),
                title=doc.get('title', ''),
                authors=doc.get('authors', []),
                venue=doc.get('venue', ''),
                year=doc.get('year', None),
                url=doc.get('url', '')
            ))
            context_parts.append(f"Title: {doc['title']}\nAbstract: {doc['abstract']}")
        
        # Generate answer (simplified - in production use LangChain + LLM)
        context = "\n\n".join(context_parts)
        answer = generate_simple_answer(request.query, context)
        
        return QAResponse(
            question=request.query,
            answer=answer,
            sources=sources,
            context_used=context[:500] + "..." if len(context) > 500 else context
        )
        
    except Exception as e:
        logger.error(f"❌ Q&A failed: {e}")
        raise HTTPException(status_code=500, detail=f"Q&A failed: {str(e)}")

def generate_simple_answer(question: str, context: str) -> str:
    """Generate a simple answer based on context (placeholder for LangChain + LLM)."""
    # This is a simplified implementation
    # In production, you'd use LangChain with GPT-4, Claude, or other LLMs
    
    question_lower = question.lower()
    
    if "agentic" in question_lower or "agent" in question_lower:
        return "Based on the research papers, agentic AI refers to AI systems that can act autonomously and make decisions independently. These systems are designed to operate with minimal human intervention and can adapt to new situations."
    
    if "machine learning" in question_lower:
        return "Machine learning is a subset of artificial intelligence that focuses on algorithms that can learn from data. The research shows various applications in data science, classification, and neural networks."
    
    if "deep learning" in question_lower:
        return "Deep learning involves neural networks with multiple layers that can learn complex patterns. The research covers various architectures, activation functions, and applications."
    
    return f"Based on the research papers, {question} is an important topic in artificial intelligence. The papers provide insights into various approaches and applications in this field."

@router.get("/stats")
async def get_index_stats():
    """Get statistics about the vector index."""
    try:
        stats = index_manager.get_stats()
        embedder_info = embedder.get_model_info()
        
        return {
            "index_stats": stats,
            "embedder_info": embedder_info,
            "status": "ready"
        }
        
    except Exception as e:
        logger.error(f"❌ Stats failed: {e}")
        raise HTTPException(status_code=500, detail=f"Stats failed: {str(e)}")

@router.post("/rebuild")
async def rebuild_index():
    """Rebuild the vector index from scratch."""
    try:
        logger.info("🔄 Rebuilding vector index...")
        
        # Load papers from all sources
        data_loader = ResearchPaperDataLoader("data")
        papers = data_loader.load_all_sources(DATA_CONFIG)
        
        if not papers:
            raise HTTPException(status_code=400, detail="No papers loaded")
        
        # Generate embeddings
        embeddings = embedder.generate_paper_embeddings(papers)
        
        # Extract document IDs and texts
        document_ids = [paper["id"] for paper in papers]
        
        # Rebuild index
        index_manager.rebuild_index(
            embeddings=embeddings,
            document_ids=document_ids,
            documents=papers,
            ef_construction=200,
            M=16
        )
        
        # Save the index
        index_manager.save_index()
        
        logger.info(f"✅ Index rebuilt successfully with {len(papers)} papers")
        
        return {
            "message": f"Index rebuilt successfully with {len(papers)} papers",
            "total_papers": len(papers),
            "embedding_dimension": embedder.get_embedding_dimension()
        }
        
    except Exception as e:
        logger.error(f"❌ Rebuild failed: {e}")
        raise HTTPException(status_code=500, detail=f"Rebuild failed: {str(e)}")