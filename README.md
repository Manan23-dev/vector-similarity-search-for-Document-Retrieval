# Vector Similarity Search for Document Retrieval

A high-performance RAG-based system with LangChain and Hugging Face, enabling automated document retrieval and intelligent question-answering for large collections of text.

## 🚀 Live Demo

**Click here to access the working demo with search functionality:**
**[https://manan23-dev.github.io/vector-similarity-search-for-Document-Retrieval/docs/](https://manan23-dev.github.io/vector-similarity-search-for-Document-Retrieval/docs/)**

*Note: If the above link doesn't work, try: [https://manan23-dev.github.io/vector-similarity-search-for-Document-Retrieval/](https://manan23-dev.github.io/vector-similarity-search-for-Document-Retrieval/)*

## Features

- **Vector Search**: HNSWlib for fast similarity search
- **Embeddings**: Hugging Face sentence-transformers
- **RAG System**: Retrieval-Augmented Generation
- **API**: FastAPI with interactive documentation
- **Frontend**: Static HTML/CSS/JavaScript demo

## Live Demo

- **Frontend**: [GitHub Pages](https://manan23-dev.github.io/vector-similarity-search-for-Document-Retrieval/)
- **Backend API**: [Render](https://vector-similarity-search-for-document.onrender.com)
- **API Documentation**: [Interactive Docs](https://vector-similarity-search-for-document.onrender.com/docs)

## API Endpoints

- `GET /` - Welcome message
- `GET /health` - Health check
- `GET /docs` - Interactive API documentation
- `POST /api/search` - Vector similarity search
- `POST /api/qa` - Question answering with RAG
- `GET /api/stats` - Index statistics
- `POST /api/reindex` - Rebuild vector index

## Technology Stack

- **Backend**: FastAPI, Python
- **Vector Search**: HNSWlib
- **Embeddings**: sentence-transformers (all-MiniLM-L6-v2)
- **Frontend**: HTML, CSS, JavaScript
- **Deployment**: Render (backend), GitHub Pages (frontend)

## Project Structure

```
├── src/
│   ├── api/endpoints.py      # FastAPI endpoints
│   ├── embeddings/embedder.py # Embedding generation
│   └── index/index_manager.py # Vector index management
├── assets/                   # Frontend assets
│   ├── css/demo.css         # Styling
│   └── js/demo.js          # Frontend logic
├── example_data/            # Sample documents
├── main.py                  # FastAPI application
└── requirements.txt         # Python dependencies
```

## Local Development

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the server:
   ```bash
   python main.py
   ```

3. Open frontend:
   ```bash
   # Serve assets directory with any static server
   python -m http.server 8000
   ```

## Deployment

- **Backend**: Deployed on Render with automatic deployments from master branch
- **Frontend**: Served from GitHub Pages with static file serving

## License

This project is part of a demonstration of vector similarity search capabilities for document retrieval systems.