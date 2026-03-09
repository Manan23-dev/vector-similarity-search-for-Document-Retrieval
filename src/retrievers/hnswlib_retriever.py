"""
LangChain custom retriever wrapping HNSWlib index for RAG pipeline.
Provides a standard BaseRetriever interface for integration with LangChain chains.
"""

from typing import List, Optional, Any
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from pydantic import Field

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class HNSWlibRetriever(BaseRetriever):
    """
    LangChain retriever that uses the project's HNSWlib IndexManager.
    Enables LangChain RAG chains and evaluation pipelines.
    """

    index_manager: Any = Field(description="IndexManager instance with search capability")
    embedder: Any = Field(description="Embedder instance for query encoding")
    k: int = Field(default=5, description="Number of documents to retrieve")
    score_threshold: float = Field(default=0.0, description="Minimum similarity score (0-1)")

    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager: Optional[CallbackManagerForRetrieverRun] = None,
    ) -> List[Document]:
        """Retrieve documents relevant to the query using HNSWlib vector search."""
        if not self.index_manager.is_initialized:
            return []

        query_embedding = self.embedder.generate_embeddings([query], show_progress=False)
        doc_ids, distances, documents = self.index_manager.search(
            query_embedding[0], k=self.k, ef=50
        )

        langchain_docs = []
        for doc_id, doc, distance in zip(doc_ids, documents, distances):
            score = 1.0 - distance
            if score < self.score_threshold:
                continue
            content = f"{doc.get('title', '')} [SEP] {doc.get('abstract', '')}"
            langchain_docs.append(
                Document(
                    page_content=content,
                    metadata={
                        "document_id": doc_id,
                        "title": doc.get("title", ""),
                        "authors": doc.get("authors", []),
                        "venue": doc.get("venue", ""),
                        "year": doc.get("year"),
                        "url": doc.get("url", ""),
                        "source": doc.get("source", ""),
                        "score": round(score, 4),
                    },
                )
            )
        return langchain_docs
