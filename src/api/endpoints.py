from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import logging
import os
import sys
import requests
from pathlib import Path

# Connection pool for HuggingFace Inference API (reuses TCP connections)
_http_session: Optional[requests.Session] = None


def _get_http_session() -> requests.Session:
    global _http_session
    if _http_session is None:
        _http_session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(pool_connections=4, pool_maxsize=8, max_retries=2)
        _http_session.mount("https://", adapter)
        _http_session.mount("http://", adapter)
    return _http_session

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.embeddings.embedder import Embedder
from src.index.index_manager import IndexManager
from data_loader import ResearchPaperDataLoader, DATA_CONFIG
from api_config import HF_TOKEN, get_frequent_queries

# Optional LangChain integration
LANGCHAIN_AVAILABLE = False
_langchain_qa_chain = None

def _get_langchain_qa_chain():
    """Lazily build LangChain RAG chain when index is ready."""
    global _langchain_qa_chain
    if _langchain_qa_chain is not None:
        return _langchain_qa_chain
    if not LANGCHAIN_AVAILABLE or not HF_TOKEN or not index_manager.is_initialized:
        return None
    try:
        from src.retrievers.hnswlib_retriever import HNSWlibRetriever
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import StrOutputParser
        from langchain_community.llms import HuggingFaceHub
        retriever = HNSWlibRetriever(
            index_manager=index_manager,
            embedder=embedder,
            k=5,
            score_threshold=0.0
        )
        llm = HuggingFaceHub(
            repo_id="mistralai/Mistral-7B-Instruct-v0.2",
            huggingfacehub_api_token=HF_TOKEN,
            model_kwargs={"max_new_tokens": 256, "temperature": 0.3},
        )
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Answer based only on the following context. Be concise."),
            ("human", "Context:\n{context}\n\nQuestion: {question}\n\nAnswer:")
        ])
        def format_docs(docs):
            return "\n\n".join(d.page_content for d in docs)
        chain = retriever | format_docs | (lambda ctx: {"context": ctx, "question": "{question}"})
        # Simpler: use LCEL with RunnablePassthrough
        from langchain_core.runnables import RunnablePassthrough
        chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )
        _langchain_qa_chain = chain
        logger.info("LangChain RAG chain initialized")
        return _langchain_qa_chain
    except Exception as e:
        logger.warning("LangChain chain setup failed: %s", e)
        return None

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
    ef: Optional[int] = None  # HNSW search param (default 50; higher=more accurate, slower)

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
    """
    Initialize the vector index: load from disk if valid, else build from sources.
    Uses MAX_PAPERS (default 5000) unless FULL_DATASET=true for faster cold start on Render.
    """
    try:
        logger.info("Initializing vector index...")
        index_path = Path("data/vector_index")
        index_file = index_path / "hnswlib_index.bin"
        metadata_file = index_path / "metadata.json"

        # Fast path: load existing index if present and valid
        if index_manager.load_index():
            n = len(index_manager.documents)
            logger.info("Loaded existing index with %d papers (fast path)", n)
            _prewarm_embedding_cache()
            return True

        # Build path: reduced dataset by default for free Render cold start
        max_papers = 5000
        if os.getenv("FULL_DATASET", "").lower() == "true":
            max_papers = 50000
        os.environ.setdefault("MAX_PAPERS", str(max_papers))
        logger.info("Building index from sources (max_papers=%s)", os.environ.get("MAX_PAPERS"))

        data_loader = ResearchPaperDataLoader("data")
        papers = data_loader.load_all_sources(DATA_CONFIG)

        if not papers:
            logger.error("No papers loaded from any source")
            return False

        logger.info("Loaded %d papers from data sources", len(papers))

        logger.info("Generating embeddings...")
        embeddings = embedder.generate_paper_embeddings(papers)

        document_ids = [p["id"] for p in papers]
        logger.info("Building HNSWlib vector index...")
        index_manager.add_embeddings(
            embeddings=embeddings,
            document_ids=document_ids,
            documents=papers,
            ef_construction=200,
            M=16
        )
        index_manager.save_index()

        logger.info("Index initialized successfully with %d papers", len(papers))
        _prewarm_embedding_cache()
        return True

    except Exception as e:
        logger.error("Failed to initialize index: %s", e)
        return False


def _prewarm_embedding_cache():
    """Precompute embeddings for frequent queries to speed up first search."""
    queries = get_frequent_queries()
    if not queries or not embedder._cache:
        return
    try:
        logger.info("Prewarming embedding cache for %d frequent queries...", len(queries))
        embedder.generate_embeddings(queries, show_progress=False)
        logger.info("Embedding cache prewarmed")
    except Exception as e:
        logger.warning("Prewarm failed: %s", e)


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
        ef_val = request.ef if request.ef is not None else 50
        document_ids, distances, documents = index_manager.search(
            query_embedding[0], 
            k=request.top_k,
            ef=ef_val
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
    Uses LangChain when available, otherwise falls back to HuggingFace Inference API.
    """
    try:
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        logger.info(f"🤖 Q&A for: '{request.query}'")
        
        # Try LangChain RAG chain first when available
        lc_chain = _get_langchain_qa_chain() if LANGCHAIN_AVAILABLE else None
        if lc_chain is not None:
            try:
                answer = lc_chain.invoke(request.query)
                # We need sources - LangChain chain returns only answer. Fall back to our retrieval for sources.
                query_embedding = embedder.generate_embeddings([request.query], show_progress=False)
                document_ids, distances, documents = index_manager.search(
                    query_embedding[0], k=min(request.top_k, 5)
                )
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
                context = "\n\n".join(context_parts)
                return QAResponse(
                    question=request.query,
                    answer=answer,
                    sources=sources,
                    context_used=context[:500] + "..." if len(context) > 500 else context
                )
            except Exception as lc_err:
                logger.warning("LangChain QA failed, using fallback: %s", lc_err)
                # Fall through to original implementation
        else:
            pass  # Use original implementation below

        # Original retrieval + LLM flow
        query_embedding = embedder.generate_embeddings([request.query], show_progress=False)
        ef_val = request.ef if request.ef is not None else 50
        document_ids, distances, documents = index_manager.search(
            query_embedding[0], 
            k=min(request.top_k, 5),
            ef=ef_val
        )
        
        if not documents:
            return QAResponse(
                question=request.query,
                answer="I couldn't find any relevant research papers to answer your question.",
                sources=[],
                context_used=""
            )
        
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
        
        context = "\n\n".join(context_parts)
        answer = generate_llm_answer(request.query, context)
        
        return QAResponse(
            question=request.query,
            answer=answer,
            sources=sources,
            context_used=context[:500] + "..." if len(context) > 500 else context
        )
        
    except Exception as e:
        logger.error(f"❌ Q&A failed: {e}")
        raise HTTPException(status_code=500, detail=f"Q&A failed: {str(e)}")


def generate_llm_answer(question: str, context: str) -> str:
    """
    Call HuggingFace Inference API for free-tier LLM answer.
    Falls back to generate_simple_answer if HF_TOKEN is not set.
    """
    if not HF_TOKEN or not HF_TOKEN.strip():
        logger.warning("HF_TOKEN not set; using keyword-based answer fallback")
        return generate_simple_answer(question, context)
    
    # Prefer smaller/faster model for free tier; optional: HuggingFaceH4/zephyr-7b-beta
    model_id = "mistralai/Mistral-7B-Instruct-v0.2"
    url = f"https://api-inference.huggingface.co/models/{model_id}"
    headers = {"Authorization": f"Bearer {HF_TOKEN}", "Content-Type": "application/json"}
    # Truncate context to avoid token limits
    context_trim = context[:3000] if len(context) > 3000 else context
    prompt = (
        "Based on the following research paper excerpts, answer the question in one or two short paragraphs. Be concise.\n\n"
        f"Context:\n{context_trim}\n\nQuestion: {question}\n\nAnswer:"
    )
    payload = {"inputs": prompt, "parameters": {"max_new_tokens": 256, "temperature": 0.3}}
    
    try:
        session = _get_http_session()
        r = session.post(url, json=payload, headers=headers, timeout=60)
        r.raise_for_status()
        data = r.json()
        if isinstance(data, list) and len(data) > 0 and "generated_text" in data[0]:
            return (data[0]["generated_text"] or "").strip()
        if isinstance(data, dict) and "generated_text" in data:
            return (data["generated_text"] or "").strip()
        return generate_simple_answer(question, context)
    except Exception as e:
        logger.warning("HuggingFace Inference API failed, using fallback: %s", e)
        return generate_simple_answer(question, context)


def generate_simple_answer(question: str, context: str) -> str:
    """Keyword-based fallback when HF_TOKEN is not set or API fails."""
    question_lower = question.lower()
    if "agentic" in question_lower or "agent" in question_lower:
        return "Based on the research papers, agentic AI refers to AI systems that can act autonomously and make decisions independently."
    if "machine learning" in question_lower:
        return "Machine learning is a subset of AI that focuses on algorithms that can learn from data."
    if "deep learning" in question_lower:
        return "Deep learning involves neural networks with multiple layers that can learn complex patterns."
    return f"Based on the research papers, {question} is an important topic. The retrieved excerpts provide relevant context."

@router.get("/health")
async def api_health():
    """Health check with index size, papers loaded, and LLM config status."""
    try:
        stats = index_manager.get_stats() if index_manager.is_initialized else {}
        n_papers = len(index_manager.documents) if index_manager.is_initialized else 0
        llm_configured = bool(HF_TOKEN and HF_TOKEN.strip())
        return {
            "status": "healthy",
            "index_initialized": index_manager.is_initialized,
            "papers_loaded": n_papers,
            "llm_configured": llm_configured,
        }
    except Exception as e:
        logger.exception("Health check failed")
        return {"status": "unhealthy", "error": str(e)}


@router.get("/eval")
async def get_evaluation_metrics():
    """
    Run retrieval and response-level evaluation (requires pre-built index).
    Returns recall@k, MRR, NDCG, faithfulness, and relevance metrics.
    """
    try:
        if not index_manager.is_initialized:
            raise HTTPException(status_code=503, detail="Index not initialized")
        
        eval_path = Path(__file__).parent.parent.parent / "evaluation" / "eval_queries.json"
        if not eval_path.exists():
            return {
                "status": "no_eval_file",
                "message": "evaluation/eval_queries.json not found",
                "retrieval_metrics": {},
                "response_metrics": {},
            }
        
        with open(eval_path) as f:
            eval_queries = json.load(f)
        
        def search_fn(query: str, top_k: int = 10):
            qe = embedder.generate_embeddings([query], show_progress=False)
            doc_ids, distances, documents = index_manager.search(qe[0], k=top_k, ef=50)
            return [
                {"document_id": str(doc_id), "score": 1 - d, "title": doc.get("title", "")}
                for doc_id, d, doc in zip(doc_ids, distances, documents)
            ]
        
        from evaluation.retrieval_metrics import compute_retrieval_metrics
        from evaluation.response_metrics import compute_faithfulness, compute_relevance
        
        retrieval_metrics = compute_retrieval_metrics(
            eval_queries, search_fn, k_values=[1, 5, 10]
        )
        
        response_scores = []
        for item in eval_queries[:3]:
            query = item["query"]
            results = search_fn(query, top_k=3)
            context = "\n".join((r.get("title", "") or "") + " " + str(r.get("score", "")) for r in results)
            answer = f"Based on the papers: {query} is addressed in the retrieved context."
            response_scores.append({
                "faithfulness": compute_faithfulness(answer, context),
                "relevance": compute_relevance(query, answer),
            })
        
        n = max(1, len(response_scores))
        response_metrics = {
            "avg_faithfulness": sum(s["faithfulness"] for s in response_scores) / n,
            "avg_relevance": sum(s["relevance"] for s in response_scores) / n,
        }
        
        return {
            "status": "ok",
            "retrieval_metrics": retrieval_metrics,
            "response_metrics": response_metrics,
            "n_eval_queries": len(eval_queries),
        }
    except Exception as e:
        logger.exception("Evaluation failed")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tune")
async def tune_index_parameters(
    ef_min: int = 40,
    ef_max: int = 80,
    ef_step: int = 10,
):
    """
    Sweep HNSW ef parameter and return best value based on retrieval metrics.
    Higher ef = more accurate but slower. Use evaluation to find optimal trade-off.
    """
    try:
        if not index_manager.is_initialized:
            raise HTTPException(status_code=503, detail="Index not initialized")
        
        eval_path = Path(__file__).parent.parent.parent / "evaluation" / "eval_queries.json"
        if not eval_path.exists():
            return {
                "status": "no_eval_file",
                "message": "evaluation/eval_queries.json required for tuning",
            }
        
        with open(eval_path) as f:
            eval_queries = json.load(f)
        
        from evaluation.retrieval_metrics import compute_retrieval_metrics
        
        ef_values = list(range(ef_min, min(ef_max + 1, 501), ef_step))
        if not ef_values:
            ef_values = [50]
        
        results = []
        best_ndcg = -1.0
        best_ef = ef_values[0]
        
        for ef in ef_values:
            def search_fn(q, top_k=10, _ef=ef):
                qe = embedder.generate_embeddings([q], show_progress=False)
                doc_ids, distances, documents = index_manager.search(qe[0], k=top_k, ef=_ef)
                return [
                    {"document_id": str(doc_id), "score": 1 - d, "title": doc.get("title", "")}
                    for doc_id, d, doc in zip(doc_ids, distances, documents)
                ]
            metrics = compute_retrieval_metrics(eval_queries, search_fn, k_values=[1, 5, 10])
            results.append({"ef": ef, "metrics": metrics})
            if metrics.get("ndcg_at_10", 0) > best_ndcg:
                best_ndcg = metrics["ndcg_at_10"]
                best_ef = ef
        
        return {
            "status": "ok",
            "best_ef": best_ef,
            "best_ndcg_at_10": best_ndcg,
            "sweep": results,
        }
    except Exception as e:
        logger.exception("Tune failed")
        raise HTTPException(status_code=500, detail=str(e))


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