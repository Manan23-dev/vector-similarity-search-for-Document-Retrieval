# API Configuration for Research Paper Data Sources
# UPDATED: Support for IEEE Xplore and Springer APIs

import os
from typing import Dict, Any

def get_api_config() -> Dict[str, Any]:
    """
    Get API configuration with environment variables for security
    """
    return {
        "huggingface": {
            "enabled": True,
            "dataset_name": "scientific_papers"
        },
        "kaggle": {
            "enabled": False,
            "dataset_path": "research-papers-dataset"
        },
        "arxiv": {
            "enabled": True,
            "query": "cat:cs.AI OR cat:cs.CV OR cat:cs.LG OR cat:cs.CL OR cat:cs.RO",
            "max_results": 2000
        },
        "ieee_xplore": {
            "enabled": os.getenv("IEEE_XPLORE_ENABLED", "false").lower() == "true",
            "api_key": os.getenv("IEEE_XPLORE_API_KEY", ""),
            "query": "machine learning artificial intelligence",
            "max_results": 1000
        },
        "springer": {
            "enabled": os.getenv("SPRINGER_ENABLED", "false").lower() == "true",
            "api_key": os.getenv("SPRINGER_API_KEY", ""),
            "query": "machine learning artificial intelligence",
            "max_results": 1000
        },
        "local": {
            "enabled": True,
            "file_path": "docs/assets/data/sample-papers.json"
        },
        "synthetic": {
            "enabled": True,
            "num_papers": 50000
        }
    }

# Instructions for setting up API keys:
"""
To use IEEE Xplore and Springer APIs:

1. IEEE Xplore API:
   - Register at: https://developer.ieee.org/
   - Get your API key
   - Set environment variable: IEEE_XPLORE_API_KEY=your_key_here
   - Set environment variable: IEEE_XPLORE_ENABLED=true

2. Springer API:
   - Register at: https://dev.springernature.com/
   - Get your API key
   - Set environment variable: SPRINGER_API_KEY=your_key_here
   - Set environment variable: SPRINGER_ENABLED=true

3. Run the data loader:
   python initialize_dataset.py
"""
