#!/usr/bin/env python3
"""
Test Script for 50,000+ Papers Dataset
Tests the backend with real research papers including agentic AI topics
"""

import requests
import json
import time

# Configuration
API_BASE_URL = "https://vector-similarity-search-for-document.onrender.com"
LOCAL_URL = "http://localhost:8000"

def test_api_connection(base_url):
    """Test if API is accessible"""
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            print(f"✅ API accessible at {base_url}")
            return True
        else:
            print(f"❌ API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API connection failed: {e}")
        return False

def test_search(query, base_url, top_k=10):
    """Test search functionality"""
    try:
        response = requests.post(
            f"{base_url}/api/search",
            json={"query": query, "top_k": top_k, "threshold": 0.1},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"🔍 Search '{query}': {len(data['results'])} results")
            
            # Show first few results
            for i, result in enumerate(data['results'][:3]):
                print(f"  {i+1}. {result.get('title', 'No title')} (similarity: {result['score']:.3f})")
            
            return data
        else:
            print(f"❌ Search failed with status {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Search error: {e}")
        return None

def test_stats(base_url):
    """Test stats endpoint"""
    try:
        response = requests.get(f"{base_url}/api/stats", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"📊 Dataset Stats:")
            print(f"  Total papers: {data['index_stats']['total_documents']}")
            print(f"  Embedding dim: {data['index_stats']['embedding_dimension']}")
            print(f"  Model: {data['embedder_info']['model']}")
            return data
        else:
            print(f"❌ Stats failed with status {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Stats error: {e}")
        return None

def test_qa(query, base_url):
    """Test Q&A functionality"""
    try:
        response = requests.post(
            f"{base_url}/api/qa",
            json={"query": query, "top_k": 3},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"🤖 Q&A '{query}':")
            print(f"  Answer: {data['answer'][:200]}...")
            print(f"  Sources: {len(data['sources'])} papers")
            return data
        else:
            print(f"❌ Q&A failed with status {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Q&A error: {e}")
        return None

def main():
    """Main test function"""
    print("🚀 Testing Vector Similarity Search Engine")
    print("=" * 50)
    
    # Test both local and remote APIs
    urls_to_test = [
        ("Local", LOCAL_URL),
        ("Remote", API_BASE_URL)
    ]
    
    for name, url in urls_to_test:
        print(f"\n📡 Testing {name} API: {url}")
        print("-" * 30)
        
        # Test connection
        if not test_api_connection(url):
            continue
        
        # Test stats
        stats = test_stats(url)
        if not stats:
            continue
        
        # Test searches
        test_queries = [
            "agentic AI",
            "machine learning",
            "transformer attention",
            "reinforcement learning",
            "computer vision",
            "natural language processing"
        ]
        
        print(f"\n🔍 Testing searches:")
        for query in test_queries:
            test_search(query, url, top_k=5)
            time.sleep(1)  # Rate limiting
        
        # Test Q&A
        print(f"\n🤖 Testing Q&A:")
        test_qa("What is agentic AI?", url)
        test_qa("How do transformers work?", url)
        
        print(f"\n✅ {name} API testing completed")
        print("=" * 50)

if __name__ == "__main__":
    main()
