# Vector Similarity Search Engine - Research Paper Discovery

A high-performance RAG-based system with LangChain and Hugging Face, enabling automated document retrieval and intelligent question-answering for large collections of text.

## 🚀 Live Demo

**Click here to access the working demo with search functionality:**
**[https://manan23-dev.github.io/vector-similarity-search-for-Document-Retrieval/docs/](https://manan23-dev.github.io/vector-similarity-search-for-Document-Retrieval/docs/)**

*Note: If the above link doesn't work, try: [https://manan23-dev.github.io/vector-similarity-search-for-Document-Retrieval/](https://manan23-dev.github.io/vector-similarity-search-for-Document-Retrieval/)*

## Features

- **Natural Language Search**: Enter-to-search with real-time results
- **Similarity Scoring**: Real-time similarity percentage display
- **Keyword Highlighting**: Search terms highlighted in titles and abstracts
- **Advanced Filters**: Filter by year range, venue, and author
- **Pagination**: 10 results per page with navigation
- **Metrics Dashboard**: Query speed, dataset size, precision, and vector dimensions
- **Dark Mode**: Persistent theme switching with localStorage
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Accessibility**: ARIA labels, keyboard navigation, and screen reader support

## Technology Stack

- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Backend**: FastAPI, Python
- **Vector Search**: HNSWlib
- **Embeddings**: sentence-transformers (all-MiniLM-L6-v2)
- **Deployment**: Render (backend), GitHub Pages (frontend)

## Local Development

### Prerequisites
- Node.js (for serving static files)
- Modern web browser

### Running Locally

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Manan23-dev/vector-similarity-search-for-Document-Retrieval.git
   cd vector-similarity-search-for-Document-Retrieval
   ```

2. **Serve the frontend:**
   ```bash
   # Using npx serve (recommended)
   npx serve docs
   
   # Or using Python
   cd docs
   python -m http.server 8000
   
   # Or using Node.js http-server
   npx http-server docs
   ```

3. **Open in browser:**
   ```
   http://localhost:3000  # for npx serve
   http://localhost:8000  # for Python server
   ```

### Backend Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the server:**
   ```bash
   python main.py
   ```

3. **Access API documentation:**
   ```
   http://localhost:8000/docs
   ```

## API Integration

The frontend is designed to work with the Render backend API. To swap in a real API:

1. **Update the API configuration** in `docs/assets/js/demo.js`:
   ```javascript
   const CONFIG = {
       API_BASE_URL: 'https://your-api-endpoint.com',
       // ... other config
   };
   ```

2. **Modify the search function** to use your API:
   ```javascript
   const searchEngine = {
       async search(query) {
           const response = await fetch(`${CONFIG.API_BASE_URL}/api/search`, {
               method: 'POST',
               headers: { 'Content-Type': 'application/json' },
               body: JSON.stringify({ query, top_k: 10 })
           });
           return await response.json();
       }
   };
   ```

## Project Structure

```
docs/
├── index.html              # Main frontend page
├── assets/
│   ├── css/
│   │   └── demo.css        # Styling with dark mode support
│   ├── js/
│   │   └── demo.js         # Frontend logic and search engine
│   └── data/
│       └── sample-papers.json # Sample research papers dataset
├── README.md               # This file
└── ...                     # Other project files
```

## Sample Data

The demo includes 25+ research papers across various AI/ML domains:
- **NLP**: Transformers, BERT, GPT-3, Neural Machine Translation
- **Computer Vision**: ResNet, YOLO, Mask R-CNN, Vision Transformers
- **Reinforcement Learning**: DQN, AlphaGo, Robot Navigation
- **GANs**: Progressive GAN, StyleGAN, DALL-E
- **Robotics**: SLAM, Motion Planning, Autonomous Systems

## Search Algorithm

The frontend implements a hybrid search approach:

1. **Token-based Similarity**: Weighted token overlap scoring
   - Title: 1.5x weight
   - Keywords: 1.3x weight  
   - Abstract: 1.0x weight

2. **Vector Similarity**: Cosine similarity for vector embeddings (when available)

3. **Real-time Metrics**: Query speed measurement and performance tracking

## Browser Support

- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is part of a demonstration of vector similarity search capabilities for document retrieval systems.

## Live Demo Links

- **Frontend**: [GitHub Pages](https://manan23-dev.github.io/vector-similarity-search-for-Document-Retrieval/docs/)
- **Backend API**: [Render](https://vector-similarity-search-for-document.onrender.com)
- **API Documentation**: [Interactive Docs](https://vector-similarity-search-for-document.onrender.com/docs)