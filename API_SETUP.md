# API Setup Guide - IEEE Xplore & Springer Integration

## 🔑 API Keys Setup

### **IEEE Xplore API**

1. **Register for IEEE Xplore API:**
   - Visit: https://developer.ieee.org/
   - Create an account
   - Request API access
   - Get your API key

2. **Configure Environment Variables:**
   ```bash
   export IEEE_XPLORE_API_KEY="your_api_key_here"
   export IEEE_XPLORE_ENABLED="true"
   ```

3. **Update Configuration:**
   ```python
   # In data_loader.py or api_config.py
   "ieee_xplore": {
       "enabled": True,
       "api_key": "your_api_key_here",
       "query": "machine learning artificial intelligence",
       "max_results": 1000
   }
   ```

### **Springer API**

1. **Register for Springer API:**
   - Visit: https://dev.springernature.com/
   - Create an account
   - Request API access
   - Get your API key

2. **Configure Environment Variables:**
   ```bash
   export SPRINGER_API_KEY="your_api_key_here"
   export SPRINGER_ENABLED="true"
   ```

3. **Update Configuration:**
   ```python
   # In data_loader.py or api_config.py
   "springer": {
       "enabled": True,
       "api_key": "your_api_key_here",
       "query": "machine learning artificial intelligence",
       "max_results": 1000
   }
   ```

## 🚀 Usage Examples

### **Load Papers from IEEE Xplore**
```python
from data_loader import ResearchPaperDataLoader

loader = ResearchPaperDataLoader()

# Load papers from IEEE Xplore
ieee_papers = loader.load_from_ieee_xplore(
    api_key="your_ieee_api_key",
    query="deep learning neural networks",
    max_results=500
)

print(f"Loaded {len(ieee_papers)} papers from IEEE Xplore")
```

### **Load Papers from Springer**
```python
# Load papers from Springer
springer_papers = loader.load_from_springer(
    api_key="your_springer_api_key",
    query="computer vision image processing",
    max_results=500
)

print(f"Loaded {len(springer_papers)} papers from Springer")
```

### **Load from All Sources**
```python
# Load from all configured sources
config = {
    "ieee_xplore": {
        "enabled": True,
        "api_key": "your_ieee_api_key",
        "query": "machine learning",
        "max_results": 1000
    },
    "springer": {
        "enabled": True,
        "api_key": "your_springer_api_key",
        "query": "artificial intelligence",
        "max_results": 1000
    },
    "arxiv": {
        "enabled": True,
        "query": "cat:cs.AI OR cat:cs.CV",
        "max_results": 2000
    },
    "synthetic": {
        "enabled": True,
        "num_papers": 50000
    }
}

all_papers = loader.load_all_sources(config)
print(f"Total papers loaded: {len(all_papers)}")
```

## 📊 API Response Formats

### **IEEE Xplore Response**
```json
{
    "articles": [
        {
            "article_number": "12345678",
            "title": "Deep Learning for Computer Vision",
            "abstract": "This paper presents...",
            "authors": {
                "authors": [
                    {"full_name": "John Doe"},
                    {"full_name": "Jane Smith"}
                ]
            },
            "publication_year": "2023",
            "publication_title": "IEEE Transactions on Pattern Analysis",
            "index_terms": {
                "ieee_terms": {
                    "terms": ["deep learning", "computer vision"]
                }
            },
            "pdf_url": "https://ieeexplore.ieee.org/document/12345678"
        }
    ]
}
```

### **Springer Response**
```json
{
    "records": [
        {
            "identifier": "10.1007/s12345-023-01234-5",
            "title": "Machine Learning in Healthcare",
            "abstract": "This study investigates...",
            "creators": [
                {"creator": "Alice Johnson"},
                {"creator": "Bob Wilson"}
            ],
            "publicationDate": "2023-06-15",
            "publicationName": "Nature Machine Intelligence",
            "subjects": ["machine learning", "healthcare"],
            "url": [
                {"value": "https://link.springer.com/article/10.1007/s12345-023-01234-5"}
            ]
        }
    ]
}
```

## 🔧 Configuration Options

### **IEEE Xplore Parameters**
- `api_key`: Your IEEE Xplore API key (required)
- `query`: Search query string
- `max_results`: Maximum number of results (default: 1000)
- `start_record`: Starting record number for pagination

### **Springer Parameters**
- `api_key`: Your Springer API key (required)
- `query`: Search query string
- `max_results`: Maximum number of results (default: 1000)
- `start_record`: Starting record number for pagination

## 🚨 Rate Limits & Best Practices

### **IEEE Xplore**
- Rate limit: 200 requests per day (free tier)
- Batch size: Up to 200 records per request
- Recommended: Use pagination for large datasets

### **Springer**
- Rate limit: 5000 requests per day (free tier)
- Batch size: Up to 50 records per request
- Recommended: Use pagination for large datasets

### **Best Practices**
1. **Cache Results**: Save API responses to avoid repeated calls
2. **Batch Processing**: Process papers in batches
3. **Error Handling**: Implement retry logic for failed requests
4. **Rate Limiting**: Respect API rate limits
5. **Data Validation**: Validate API responses before processing

## 🧪 Testing API Integration

### **Test IEEE Xplore API**
```python
# Test IEEE Xplore connection
try:
    papers = loader.load_from_ieee_xplore(
        api_key="your_api_key",
        query="machine learning",
        max_results=10
    )
    print(f"✅ IEEE Xplore API working: {len(papers)} papers loaded")
except Exception as e:
    print(f"❌ IEEE Xplore API error: {e}")
```

### **Test Springer API**
```python
# Test Springer connection
try:
    papers = loader.load_from_springer(
        api_key="your_api_key",
        query="artificial intelligence",
        max_results=10
    )
    print(f"✅ Springer API working: {len(papers)} papers loaded")
except Exception as e:
    print(f"❌ Springer API error: {e}")
```

## 📝 Environment Variables

Create a `.env` file for local development:
```bash
# IEEE Xplore API
IEEE_XPLORE_API_KEY=your_ieee_api_key_here
IEEE_XPLORE_ENABLED=true

# Springer API
SPRINGER_API_KEY=your_springer_api_key_here
SPRINGER_ENABLED=true
```

Load environment variables in Python:
```python
from dotenv import load_dotenv
load_dotenv()

# Now use os.getenv() to access the variables
import os
ieee_key = os.getenv("IEEE_XPLORE_API_KEY")
springer_key = os.getenv("SPRINGER_API_KEY")
```
