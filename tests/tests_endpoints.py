from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Vector Similarity Search Engine is running!"}

def test_search():
    response = client.post("/api/search/", json={"query": "machine learning", "top_k": 2})
    assert response.status_code == 200
    assert "documents" in response.json()
