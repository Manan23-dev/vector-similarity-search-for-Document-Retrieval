# Vector Similarity Search Engine - Research Paper Discovery

A scalable RAG-based system with LangChain and Hugging Face, enabling automated document retrieval and question-answering for large collections of text. **Supports 50,000+ research papers with real-time vector search.**

## 🚀 Live Demo

**Frontend**: [https://manan23-dev.github.io/vector-similarity-search-for-Document-Retrieval/docs/](https://manan23-dev.github.io/vector-similarity-search-for-Document-Retrieval/)  
**Backend API**: [https://vector-similarity-search-for-document.onrender.com](https://vector-similarity-search-for-document.onrender.com)  
**API Documentation**: [https://vector-similarity-search-for-document.onrender.com/docs](https://vector-similarity-search-for-document.onrender.com/docs)

## 🏗️ System Architecture

```mermaid
graph TB
    subgraph "Frontend Layer"
        UI[GitHub Pages Frontend]
        UI --> |Search Queries| API[FastAPI Backend]
    end
    
    subgraph "Backend Layer"
        API --> |Load Data| DL[Data Loader]
        API --> |Generate Embeddings| EMB[Embedder]
        API --> |Vector Search| IDX[HNSWlib Index]
    end
    
    subgraph "Data Sources"
        DL --> HF[Hugging Face Datasets]
        DL --> ARX[arXiv API]
        DL --> KG[Kaggle Datasets]
        DL --> SYN[Synthetic Generation]
    end
    
    subgraph "Vector Search Engine"
        EMB --> |768D Embeddings| IDX
        IDX --> |Similarity Results| API
    end
    
    subgraph "Storage"
        IDX --> |Persist| FS[File System]
        DL --> |Save| JSON[JSON Files]
    end
    
    style UI fill:#e1f5fe
    style API fill:#f3e5f5
    style IDX fill:#e8f5e8
    style DL fill:#fff3e0
```

## 📁 Repository Structure

```
vector-similarity-search-for-Document-Retrieval/
├── 📁 docs/                          # Frontend (GitHub Pages)
│   ├── index.html                    # Main application page
│   ├── assets/
│   │   ├── css/demo.css             # Styling with dark mode
│   │   ├── js/demo.js               # Frontend logic & search
│   │   └── data/sample-papers.json  # Sample dataset
│   └── .nojekyll                    # Disable Jekyll processing
│
├── 📁 src/                           # Backend Source Code
│   ├── api/endpoints.py              # FastAPI routes
│   ├── embeddings/embedder.py        # Sentence transformers
│   └── index/index_manager.py        # HNSWlib vector search
│
├── 📁 data/                          # Data Storage
│   ├── vector_index/                 # HNSWlib index files
│   └── research_papers_50k.json     # Combined dataset
│
├── 📄 main.py                        # FastAPI application
├── 📄 data_loader.py                 # Multi-source data loading
├── 📄 initialize_dataset.py          # Dataset initialization
├── 📄 requirements.txt               # Python dependencies
├── 📄 Procfile                       # Render deployment
├── 📄 runtime.txt                    # Python version
├── 📄 Dockerfile                     # Container configuration
├── 📄 docker-compose.yml             # Multi-container setup
└── 📄 README.md                      # This file
```

## ✨ Key Features

### **Real Dataset Integration**
- **50,000+ Research Papers** from multiple sources
- **Hugging Face Datasets** (scientific_papers, arxiv_papers)
- **arXiv API** real-time paper fetching
- **Kaggle Datasets** support
- **Synthetic Data Generation** for demonstration

### **Advanced Vector Search**
- **HNSWlib Implementation** for fast similarity search
- **768-dimensional embeddings** using `all-mpnet-base-v2`
- **Cosine similarity** with optimized search parameters
- **Sub-100ms search** performance

### **RAG System Architecture**
- **Retrieval-Augmented Generation** pipeline
- **Real-time similarity scoring**
- **Context-aware document retrieval**
- **Intelligent question-answering**

### **Frontend Features**
- **Natural Language Search** with Enter-to-search
- **Real-time Results** with similarity percentages
- **Keyword Highlighting** in titles and abstracts
- **Advanced Filters** (year, venue, author)
- **Pagination** (10 results per page)
- **Dark Mode** with localStorage persistence
- **Responsive Design** for all devices
- **Accessibility** support (ARIA, keyboard navigation)

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Frontend** | HTML5, CSS3, Vanilla JS | User interface |
| **Backend** | FastAPI, Python 3.9+ | API server |
| **Vector Search** | HNSWlib | Fast similarity search |
| **Embeddings** | sentence-transformers | Text vectorization |
| **Data Sources** | Hugging Face, arXiv, Kaggle | Research papers |
| **Deployment** | Render, GitHub Pages | Production hosting |

## 🚀 Quick Start

### **1. Clone Repository**
```bash
git clone https://github.com/Manan23-dev/vector-similarity-search-for-Document-Retrieval.git
cd vector-similarity-search-for-Document-Retrieval
```

### **2. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **3. Initialize Dataset & Index**
```bash
# Build index with 5000 papers (fast). Use --max-papers 50000 for full dataset.
python initialize_dataset.py --max-papers 5000
```

### **4. Start Backend**
```bash
python main.py
```

### **5. Start Frontend**
```bash
cd docs
npx serve .
# Open http://localhost:3000
```

## 📊 Dataset Configuration

### **Data Sources**
```python
# data_loader.py - UPDATED: Now includes IEEE Xplore and Springer APIs
DATA_CONFIG = {
    "huggingface": {
        "enabled": True,
        "dataset_name": "scientific_papers"
    },
    "arxiv": {
        "enabled": True,
        "query": "cat:cs.AI OR cat:cs.CV OR cat:cs.LG",
        "max_results": 2000
    },
    "ieee_xplore": {
        "enabled": False,  # Set to True with API key
        "api_key": "",  # Your IEEE Xplore API key
        "query": "machine learning artificial intelligence",
        "max_results": 1000
    },
    "springer": {
        "enabled": False,  # Set to True with API key
        "api_key": "",  # Your Springer API key
        "query": "machine learning artificial intelligence",
        "max_results": 1000
    },
    "synthetic": {
        "enabled": True,
        "num_papers": 50000  # Generate 50k papers
    }
}
```

### **Paper Schema**
```json
{
    "id": "paper_000001",
    "title": "Attention Is All You Need",
    "abstract": "We propose a new simple network architecture...",
    "authors": ["Ashish Vaswani", "Noam Shazeer"],
    "year": 2017,
    "venue": "NIPS",
    "keywords": ["Transformer", "Attention", "NLP"],
    "url": "https://arxiv.org/abs/1706.03762",
    "source": "arxiv"
}
```

## 🔧 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/search` | POST | Vector similarity search |
| `/api/qa` | POST | Question answering with RAG |
| `/api/stats` | GET | Index statistics |
| `/api/eval` | GET | Retrieval & response evaluation metrics |
| `/api/tune` | GET | Tune HNSW ef parameter (ef_min, ef_max, ef_step) |
| `/health` | GET | Root health check |
| `/api/health` | GET | API health: index size, papers loaded, `llm_configured` |
| `/docs` | GET | Interactive API documentation |

### **Search Example**
```bash
curl -X POST "http://localhost:8000/api/search" \
     -H "Content-Type: application/json" \
     -d '{"query": "transformer attention", "top_k": 10, "threshold": 0.7}'
```

## 📈 Performance & Evaluation Metrics

| Metric | Value | Description |
|--------|-------|-------------|
| **Dataset Size** | 50,000+ papers | Total research papers |
| **Vector Dimensions** | 768D | all-mpnet-base-v2 embeddings |
| **Search Speed** | <100ms | Average query latency |
| **Index Type** | HNSWlib | Hierarchical Navigable Small World |
| **Memory Usage** | ~500MB | Total system memory |

### **Retrieval & Response Evaluation**

Evaluated ranking quality and downstream decision impact using retrieval and response-level metrics.

Run `python evaluate.py` or `GET /api/eval` to measure:

- **Recall@k** (k=1,5,10): Fraction of relevant docs in top-k
- **MRR**: Mean Reciprocal Rank
- **NDCG@10**: Normalized Discounted Cumulative Gain
- **Faithfulness**: Does the answer stay grounded in context?
- **Relevance**: Does the answer address the question?

Eval queries: `evaluation/eval_queries.json`. Customize for your labeled dataset.

### **Efficiency Optimizations**

| Optimization | Description |
|--------------|-------------|
| **Embedding cache** | LRU cache (500 queries) for repeated search terms. Check `/api/stats` for hit rate. |
| **Connection pooling** | `requests.Session` for HuggingFace API; reuses TCP connections. |
| **Index tuning** | `GET /api/tune?ef_min=40&ef_max=80` or `python evaluate.py --tune-ef` to find best HNSW `ef`. |
| **Batch preprocessing** | Set `FREQUENT_QUERIES='["machine learning","transformer"]'` to prewarm cache on startup. |

## 🚀 Deployment

See **`DEPLOY.md`** for the full checklist. Summary:

### **Backend (Render)**

| Setting | Value |
|--------|--------|
| **Runtime** | `Python 3.11` |
| **Build Command** | `./build.sh` |
| **Start Command** | `uvicorn main:app --host 0.0.0.0 --port $PORT` |

Optional env vars: `HF_TOKEN` (HuggingFace token — [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)), `MAX_PAPERS`, `FULL_DATASET=true`, `FREQUENT_QUERIES` (JSON list, e.g. `["machine learning","transformer"]` for batch prewarming).

### **Two manual steps**
1. **HuggingFace:** Create a free Read token → in Render add env var **`HF_TOKEN`** with that value.
2. **Frontend URL:** After deploying, copy your Render app URL → in **`docs/assets/js/demo.js`** set `CONFIG.API_BASE_URL` to it (e.g. `https://your-app.onrender.com`), then push.

### **Frontend (GitHub Pages)**
Enable Pages from branch, folder **`/docs`**. Live URL: `https://<username>.github.io/vector-similarity-search-for-Document-Retrieval/docs/`

## 🧪 Testing

### **Load Dataset**
```bash
python initialize_dataset.py
```

### **Test Search**
```bash
curl -X POST "http://localhost:8000/api/search" \
     -H "Content-Type: application/json" \
     -d '{"query": "machine learning", "top_k": 5}'
```

### **Test Frontend**
```bash
cd docs
npx serve .
# Open http://localhost:3000
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add your dataset source
4. Test with real data
5. Submit a pull request

## 📄 License

This project demonstrates vector similarity search capabilities for document retrieval systems.

## 🔗 Links

- **Repository**: [GitHub](https://github.com/Manan23-dev/vector-similarity-search-for-Document-Retrieval)
- **Live Demo**: [GitHub Pages](https://manan23-dev.github.io/vector-similarity-search-for-Document-Retrieval/docs/)
- **API Docs**: [Render](https://vector-similarity-search-for-document.onrender.com/docs)
- **LinkedIn**: [Profile](https://www.linkedin.com/in/mananpatel23/)
