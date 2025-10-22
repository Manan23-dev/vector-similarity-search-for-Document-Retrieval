#!/usr/bin/env python3
"""
Dataset Loading and Index Initialization Script
UPDATED: Load real datasets and initialize HNSWlib index with 50,000+ papers
"""

import os
import sys
import logging
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from data_loader import ResearchPaperDataLoader, DATA_CONFIG
from src.embeddings.embedder import Embedder
from src.index.index_manager import IndexManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Main function to load dataset and initialize vector index"""
    
    logger.info("Starting dataset loading and index initialization")
    
    # Initialize components
    data_loader = ResearchPaperDataLoader("data")
    embedder = Embedder("all-mpnet-base-v2")  # 768 dimensions
    index_manager = IndexManager(embedder.embedding_dim, "data/vector_index")
    
    # Load papers from all sources
    logger.info("Loading papers from configured sources...")
    papers = data_loader.load_all_sources(DATA_CONFIG)
    
    if not papers:
        logger.error("No papers loaded! Check your configuration.")
        return
    
    logger.info(f"Loaded {len(papers)} papers total")
    
    # Save the combined dataset
    output_file = data_loader.save_papers(papers, "research_papers_50k.json")
    logger.info(f"Saved combined dataset to: {output_file}")
    
    # Generate embeddings for all papers
    logger.info("Generating embeddings for all papers...")
    embeddings = embedder.generate_paper_embeddings(papers)
    
    # Extract document IDs
    document_ids = [paper["id"] for paper in papers]
    
    # Add embeddings to HNSWlib index
    logger.info("Building HNSWlib vector index...")
    index_manager.add_embeddings(
        embeddings=embeddings,
        document_ids=document_ids,
        documents=papers,
        ef_construction=200,  # Higher for better quality
        M=16  # Good balance for memory and performance
    )
    
    # Save the index
    logger.info("Saving vector index...")
    index_manager.save_index()
    
    # Print statistics
    stats = index_manager.get_stats()
    logger.info("Index Statistics:")
    for key, value in stats.items():
        logger.info(f"  {key}: {value}")
    
    # Test search
    logger.info("Testing search functionality...")
    test_query = "machine learning deep neural networks"
    test_embedding = embedder.generate_embeddings([test_query])
    
    results_ids, distances, results_docs = index_manager.search(
        test_embedding[0], k=5, ef=50
    )
    
    logger.info(f"Test search for '{test_query}' returned {len(results_ids)} results:")
    for i, (doc_id, distance, doc) in enumerate(zip(results_ids, distances, results_docs)):
        similarity = 1 - distance
        logger.info(f"  {i+1}. {doc['title'][:60]}... (similarity: {similarity:.3f})")
    
    logger.info("Dataset loading and index initialization completed successfully!")
    logger.info(f"Total papers indexed: {len(papers)}")
    logger.info(f"Vector dimensions: {embedder.embedding_dim}")
    logger.info(f"Index saved to: data/vector_index/")

if __name__ == "__main__":
    main()
