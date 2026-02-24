# Repository Overview: Vector Similarity Search for Document Retrieval

## 1. Project purpose

Web app for **research paper discovery** via **vector similarity search**: users search in natural language, and the system is intended to retrieve similar papers using embeddings and an HNSW vector index. The backend exposes a **document search API** and a **Q&A-style endpoint** (retrieval + simple answer generation). The frontend is a **static demo** that currently uses a small local dataset and **client-side token-based similarity**, not the live vector-search API.

---

## 2. Repo structure

| Path | Contents |
|------|----------|
| **`docs/`** | Frontend for GitHub Pages: `index.html`, `assets/css/demo.css`, `assets/js/demo.js`, `assets/data/sample-papers.json`, `.nojekyll` |
| **`src/`** | Backend Python: `api/endpoints.py` (FastAPI routes), `embeddings/embedder.py` (sentence-transformers), `index/index_manager.py` (HNSWlib) |
| **`data/`** | Intended storage for `vector_index/` (HNSW index + metadata) and `research_papers_50k.json` (from `initialize_dataset.py`); not committed, created at runtime |
| **Root** | `main.py` (FastAPI app), `data_loader.py` (multi-source paper loading), `initialize_dataset.py` (build dataset + index), `requirements.txt`, `Procfile`, `runtime.txt`, `Dockerfile`, `docker-compose.yml`, `api_config.py`, `nginx.conf`, `build.sh`, `docker-deploy.sh` |
| **Other** | `README.md`, `DATASET_INTEGRATION.md`, `API_SETUP.md`, `test_api.py`; duplicate frontend under root `index.html`, `assets/`, `demo.html` |

---

## 3. Tech stack

- **Backend:** Python 3.9, FastAPI, Uvicorn.
- **Vector search:** HNSWlib (cosine space), 768-d embeddings.
- **Embeddings:** `sentence-transformers` with `all-mpnet-base-v2`.
- **Data loading:** Hugging Face `datasets`, `arxiv` Python client, optional Kaggle, IEEE Xplore and Springer (via `data_loader.py`; require API keys and are disabled by default).
- **Frontend:** HTML5, CSS3, vanilla JS; no framework.
- **Deployment:** Render (backend), GitHub Pages from `/docs` (frontend).
- **Containers:** Docker (multi-stage Dockerfile), docker-compose with optional nginx.

**Not in the stack:** LangChain and any LLM (e.g. OpenAI) are not in `requirements.txt` or the codebase; RAG-style Q&A is retrieval + a small rule-based answer function.

---

## 4. Data flow

- **Frontend (GitHub Pages):**
  - Loads **only** `docs/assets/data/sample-papers.json` and keeps it in memory.
  - Search is implemented in **client-side JS**: token overlap / weighted similarity (`calculateTokenSimilarity` in `docs/assets/js/demo.js`), with simulated latency.
  - **It does not call the Render (or any) backend** for search; `API_BASE_URL` is defined in `CONFIG` but never used for requests.

- **Backend (Render / local):**
  - On startup, `src/api/endpoints.py` runs `initialize_index()`: loads papers from `DATA_CONFIG` (Hugging Face, arXiv, local JSON, optional IEEE/Springer, and synthetic 50k), builds 768-d embeddings with `Embedder`, and builds/loads the HNSW index via `IndexManager` from `data/vector_index`.
  - Search: `POST /api/search` embeds the query, runs HNSWlib `knn_query`, returns matching papers with scores.
  - Q&A: `POST /api/qa` runs the same retrieval, then returns a short answer from `generate_simple_answer()` (keyword-based, no LLM).

- **External APIs/datasets:**
  - Hugging Face (`scientific_papers`), arXiv API, optional IEEE Xplore and Springer (env vars in `api_config.py`).
  - Local/sample data: `docs/assets/data/sample-papers.json` (and optionally other paths in `DATA_CONFIG`).

---

## 5. Key files (10–15)

| File | One-line description |
|------|------------------------|
| `README.md` | Project description, architecture diagram, setup, deployment, API summary. |
| `main.py` | FastAPI app entry: CORS, router mount at `/api`, root and `/health` handlers. |
| `src/api/endpoints.py` | API routes: `/api/search`, `/api/qa`, `/api/stats`, `/api/rebuild`; index init on import; HNSWlib search and simple Q&A. |
| `src/index/index_manager.py` | HNSWlib index: init, add_embeddings, search, save/load to `data/vector_index`, rebuild. |
| `src/embeddings/embedder.py` | SentenceTransformer wrapper: `all-mpnet-base-v2`, 768-d, batch encoding for papers. |
| `data_loader.py` | Multi-source loader: Hugging Face, arXiv, Kaggle, IEEE, Springer, local JSON, synthetic 50k; `DATA_CONFIG` at bottom. |
| `initialize_dataset.py` | Script to load all sources, save `research_papers_50k.json`, build embeddings and HNSW index under `data/`. |
| `docs/index.html` | Main frontend page: search UI, filters, metrics panel, dark mode. |
| `docs/assets/js/demo.js` | Frontend logic: load `sample-papers.json`, client-side token similarity search, filters, pagination, no backend API calls. |
| `docs/assets/data/sample-papers.json` | Small static paper list used by the frontend (dozens of papers). |
| `requirements.txt` | Python deps: FastAPI, uvicorn, sentence-transformers, hnswlib, torch, datasets, arxiv, etc.; no LangChain/LLM. |
| `Dockerfile` | Multi-stage Python 3.9 image; copies `src/`, `main.py`, `example_data/` (folder not in repo). |
| `Procfile` | Render: `uvicorn main:app --host 0.0.0.0 --port $PORT`. |
| `runtime.txt` | Python version for Render (e.g. `python-3.9.18`). |
| `api_config.py` | Data-source config with env-based API keys for IEEE/Springer. |

---

## 6. Deployment

- **Backend (Render):** Connect repo, build with `pip install -r requirements.txt`, start with `uvicorn main:app --host 0.0.0.0 --port $PORT`. Index is built or loaded at startup from `DATA_CONFIG`; `data/vector_index` is ephemeral unless persisted (e.g. disk or external store). No env vars are required for basic run; optional: `IEEE_XPLORE_API_KEY`, `IEEE_XPLORE_ENABLED`, `SPRINGER_API_KEY`, `SPRINGER_ENABLED`.
- **Frontend (GitHub Pages):** Serve from branch (e.g. `main`), source = `/docs`. Live URL format: `https://<user>.github.io/vector-similarity-search-for-Document-Retrieval/docs/`.
- **Docker:** Dockerfile expects `example_data/` (missing in repo); docker-compose runs backend on 8000 and optional nginx on 80 with a production profile.

---

## 7. Claims vs reality

| Claim | Reality |
|-------|--------|
| **50,000+ papers** | Supported in **config**: synthetic generator can create 50k papers and `initialize_dataset.py` can write `research_papers_50k.json`. Actual size at runtime depends on enabled sources and run; frontend uses only **sample-papers.json** (small fixed set). |
| **HNSWlib** | **Implemented**: `src/index/index_manager.py` uses `hnswlib.Index(space='cosine')`, init_index, add_items, knn_query, save/load; used by `/api/search` and `/api/qa`. |
| **RAG / LangChain** | **Not implemented**. README and UI text mention "RAG-based" and "LangChain". Code has no LangChain or LLM; `/api/qa` uses retrieval plus `generate_simple_answer()` (keyword rules). Comments in `endpoints.py` say "placeholder for LangChain + LLM". |
| **Frontend–backend integration** | README and diagram describe frontend calling the API. **In code, the frontend never calls the backend**: it only loads `sample-papers.json` and does client-side token similarity. |
| **IEEE / Springer** | **Implemented** in `data_loader.py` (and config in `api_config.py`); **disabled by default** and require API keys. |

---

## Summary for an AI

This repo is a vector search backend (FastAPI + HNSWlib + sentence-transformers) plus a static GitHub Pages demo. The demo does not use the backend; it uses a small local JSON file and client-side similarity. RAG/LangChain are advertised but not present; Q&A is retrieval + a small rule-based answer function. HNSWlib and 50k-paper data pipeline (including synthetic) are implemented on the backend side.
