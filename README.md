# Vector Similarity Search Engine for Document Retrieval
A high-performance document retrieval system that leverages HNSWlib, FastAPI, and PyTorch for efficient vector similarity searches. This project provides sub-millisecond query times, supports large-scale datasets (10,000+ documents), and is deployable using Docker and Kubernetes.

---

## Features
- **Vector Similarity Search**: Uses HNSWlib for fast and accurate similarity search.
- **High-Dimensional Embedding Generation**: Generates embeddings with `SentenceTransformers` (PyTorch-based).
- **Scalable Deployment**: Fully containerized with Docker and deployable to Kubernetes.
- **Efficient Operations**: Supports parallel indexing, clustering, and cloud integrations (AWS S3, Lambda).
- **RESTful API**: Built with FastAPI, providing endpoints for embedding and similarity search.

---

## Tech Stack
- **Core Libraries**: 
  - HNSWlib
  - PyTorch
  - SentenceTransformers
- **API Framework**: FastAPI
- **Containerization**: Docker
- **Cloud Integration**: AWS S3 and Lambda
- **Deployment**: Kubernetes

---

## Installation

### Prerequisites
- Python 3.9+
- Docker
- Git

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/Manan23-dev/vector-similarity-search-for-Document-Retrieval.git
   cd vector-similarity-search-for-Document-Retrieval
