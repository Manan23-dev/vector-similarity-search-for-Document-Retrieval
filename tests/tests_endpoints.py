from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Vector Similarity Search API" in data["message"]
    assert "features" in data

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "components" in data

def test_search():
    response = client.post("/api/search", json={"query": "machine learning", "top_k": 2})
    assert response.status_code == 200
    data = response.json()
    assert "query" in data
    assert "results" in data
    assert data["query"] == "machine learning"

def test_qa():
    response = client.post("/api/qa", json={"query": "What is machine learning?", "top_k": 3})
    assert response.status_code == 200
    data = response.json()
    assert "question" in data
    assert "answer" in data
    assert "sources" in data

def test_stats():
    response = client.get("/api/stats")
    assert response.status_code == 200
    data = response.json()
    assert "index_stats" in data
    assert "embedder_info" in data
