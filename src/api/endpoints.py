from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
import os
from src.embeddings.embedder import Embedder
from src.index.index_manager import IndexManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize components
embedder = Embedder()
index_manager = IndexManager(
    dim=embedder.get_embedding_dimension(), 
    max_elements=20000,
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
    """Initialize the vector index with documents."""
    try:
        documents_path = "example_data/documents.txt"
        
        if not os.path.exists(documents_path):
            logger.warning(f"Documents file not found at {documents_path}")
            return False
        
        # Load documents
        with open(documents_path, "r", encoding="utf-8") as file:
            documents = [line.strip() for line in file.readlines() if line.strip()]
        
        if not documents:
            logger.warning("No documents found in the file")
            return False
        
        logger.info(f"Loaded {len(documents)} documents")
        
        # Generate embeddings
        embeddings = embedder.generate_embeddings(documents)
        
        # Add to index
        index_manager.add_embeddings(embeddings, documents)
        
        logger.info("Index initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize index: {e}")
        return False

# Initialize index on startup
if not initialize_index():
    logger.error("Failed to initialize vector index")

@router.post("/search", response_model=SearchResponse)
async def search_documents(request: SearchRequest):
    """
    Search for documents similar to the query using vector similarity.
    """
    try:
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Generate query embedding
        query_embedding = embedder.generate_embeddings([request.query])
        
        # Search for similar documents
        documents, distances, document_ids = index_manager.search(
            query_embedding[0], 
            top_k=request.top_k
        )
        
        # Convert distances to similarity scores (1 - distance for cosine similarity)
        scores = [1 - distance for distance in distances]
        
        # Filter by threshold
        filtered_results = []
        for doc, doc_id, score, distance in zip(documents, document_ids, scores, distances):
            if score >= request.threshold:
                filtered_results.append(SearchResult(
                    document=doc,
                    document_id=doc_id,
                    score=round(score, 4),
                    distance=round(distance, 4)
                ))
        
        return SearchResponse(
            query=request.query,
            results=filtered_results,
            total_found=len(filtered_results),
            returned=len(filtered_results)
        )
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.post("/qa", response_model=QAResponse)
async def question_answering(request: SearchRequest):
    """
    Answer questions using RAG (Retrieval-Augmented Generation).
    This is a simplified implementation - in production you'd use LangChain with LLMs.
    """
    try:
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Retrieve relevant documents
        query_embedding = embedder.generate_embeddings([request.query])
        documents, distances, document_ids = index_manager.search(
            query_embedding[0], 
            top_k=min(request.top_k, 3)  # Use fewer docs for QA
        )
        
        if not documents:
            return QAResponse(
                question=request.query,
                answer="I couldn't find any relevant information to answer your question.",
                sources=[],
                context_used=""
            )
        
        # Create context from retrieved documents
        context = "\n\n".join(documents)
        
        # Simple answer generation (in production, use LangChain with LLMs)
        answer = generate_simple_answer(request.query, documents)
        
        # Create source results
        sources = []
        for doc, doc_id, distance in zip(documents, document_ids, distances):
            sources.append(SearchResult(
                document=doc,
                document_id=doc_id,
                score=round(1 - distance, 4),
                distance=round(distance, 4)
            ))
        
        return QAResponse(
            question=request.query,
            answer=answer,
            sources=sources,
            context_used=context[:500] + "..." if len(context) > 500 else context
        )
        
    except Exception as e:
        logger.error(f"QA failed: {e}")
        raise HTTPException(status_code=500, detail=f"Question answering failed: {str(e)}")

def generate_simple_answer(question: str, documents: List[str]) -> str:
    """
    Simple answer generation based on retrieved documents.
    In production, this would use LangChain with LLMs like OpenAI or Hugging Face.
    """
    # Extract keywords from question
    question_words = set(question.lower().split())
    
    # Find the most relevant sentence from documents
    best_sentence = ""
    best_score = 0
    
    for doc in documents:
        sentences = doc.split('. ')
        for sentence in sentences:
            sentence_words = set(sentence.lower().split())
            overlap = len(question_words & sentence_words)
            if overlap > best_score:
                best_score = overlap
                best_sentence = sentence
    
    if best_sentence:
        return f"Based on the available information: {best_sentence.strip()}."
    else:
        return "I found some relevant documents but couldn't generate a specific answer. Please try rephrasing your question."

@router.get("/stats")
async def get_index_stats():
    """Get statistics about the vector index."""
    try:
        stats = index_manager.get_stats()
        return {
            "index_stats": stats,
            "embedder_info": {
                "model": "all-MiniLM-L6-v2",
                "dimension": embedder.get_embedding_dimension()
            },
            "status": "ready"
        }
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@router.post("/reindex")
async def rebuild_index():
    """Rebuild the vector index from documents."""
    try:
        # Reinitialize the index
        global index_manager
        index_manager = IndexManager(
            dim=embedder.get_embedding_dimension(), 
            max_elements=20000,
            index_path="data/vector_index"
        )
        
        success = initialize_index()
        if success:
            return {"message": "Index rebuilt successfully", "status": "success"}
        else:
            raise HTTPException(status_code=500, detail="Failed to rebuild index")
            
    except Exception as e:
        logger.error(f"Failed to rebuild index: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to rebuild index: {str(e)}")
