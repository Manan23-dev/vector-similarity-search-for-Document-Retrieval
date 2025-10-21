// Configuration for API endpoints
const API_CONFIG = {
    // Change this to your deployed backend URL
    BASE_URL: 'https://your-backend-url.railway.app', // Replace with your actual backend URL
    LOCAL_URL: 'http://localhost:8000', // For local development
    ENDPOINTS: {
        SEARCH: '/api/search',
        QA: '/api/qa',
        STATS: '/api/stats',
        HEALTH: '/health'
    }
};

// Determine which API URL to use
const API_URL = window.location.hostname === 'localhost' ? API_CONFIG.LOCAL_URL : API_CONFIG.BASE_URL;

// Fallback data for demo purposes
const fallbackPapers = [
    {
        title: "Introduction to Machine Learning",
        abstract: "Machine learning is a subset of artificial intelligence that focuses on algorithms that can learn from data.",
        similarity: 0.95,
        keywords: ["Machine Learning", "AI", "Algorithms", "Data Science"],
        authors: "Dr. Smith",
        year: "2024",
        venue: "AI Journal"
    },
    {
        title: "Deep Learning Neural Networks",
        abstract: "Deep learning uses multiple layers of neural networks to model complex patterns in data.",
        similarity: 0.88,
        keywords: ["Deep Learning", "Neural Networks", "AI", "Pattern Recognition"],
        authors: "Prof. Johnson",
        year: "2024",
        venue: "Deep Learning Review"
    },
    {
        title: "Python Programming Fundamentals",
        abstract: "Python is a versatile programming language widely used in data science, web development, and automation.",
        similarity: 0.82,
        keywords: ["Python", "Programming", "Data Science", "Web Development"],
        authors: "Jane Doe",
        year: "2023",
        venue: "Programming Today"
    }
];

function searchQuery(query) {
    document.getElementById('searchInput').value = query;
    performSearch();
}

async function performSearch() {
    const query = document.getElementById('searchInput').value.trim();
    if (!query) {
        alert('Please enter a search query');
        return;
    }

    const resultsDiv = document.getElementById('searchResults');
    
    // Show loading
    resultsDiv.innerHTML = `
        <div class="loading">
            <div class="spinner"></div>
            <p>🔍 Searching through documents using vector similarity...</p>
            <p>⚡ Computing embeddings with Hugging Face transformers...</p>
            <p>🧠 Using HNSWlib for fast similarity search...</p>
        </div>
    `;

    try {
        // Try to connect to the actual API
        const response = await fetch(`${API_URL}${API_CONFIG.ENDPOINTS.SEARCH}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: query,
                top_k: 5,
                threshold: 0.0
            })
        });

        if (response.ok) {
            const data = await response.json();
            displayAPIResults(data);
        } else {
            throw new Error(`API Error: ${response.status}`);
        }
    } catch (error) {
        console.warn('API not available, using fallback data:', error);
        // Fallback to demo data
        setTimeout(() => {
            displayFallbackResults(query);
        }, 1000);
    }
}

function displayAPIResults(data) {
    const resultsDiv = document.getElementById('searchResults');
    
    if (!data.results || data.results.length === 0) {
        resultsDiv.innerHTML = `
            <div class="no-results">
                <h3>🔍 No Results Found</h3>
                <p>No documents matched your query "${data.query}". Try different keywords or a broader search term.</p>
            </div>
        `;
        return;
    }

    let html = `
        <div class="search-header">
            <h3>🎯 Search Results for "${data.query}"</h3>
            <p>Found ${data.total_found} relevant documents (showing ${data.returned})</p>
        </div>
        <div class="results-grid">
    `;

    data.results.forEach((result, index) => {
        const similarityPercent = Math.round(result.score * 100);
        html += `
            <div class="result-card" style="animation-delay: ${index * 0.1}s">
                <div class="result-header">
                    <div class="similarity-badge">${similarityPercent}% match</div>
                    <div class="result-id">${result.document_id}</div>
                </div>
                <div class="result-content">
                    <p class="result-text">${result.document}</p>
                </div>
                <div class="result-footer">
                    <span class="distance-info">Distance: ${result.distance.toFixed(4)}</span>
                </div>
            </div>
        `;
    });

    html += `</div>`;
    resultsDiv.innerHTML = html;
}

// Question Answering functionality
async function performQA() {
    const query = document.getElementById('searchInput').value.trim();
    if (!query) {
        alert('Please enter a question');
        return;
    }

    const resultsDiv = document.getElementById('searchResults');
    
    // Show loading
    resultsDiv.innerHTML = `
        <div class="loading">
            <div class="spinner"></div>
            <p>🤖 Generating answer using RAG...</p>
            <p>🔍 Retrieving relevant documents...</p>
            <p>🧠 Processing with language model...</p>
        </div>
    `;

    try {
        // Try to connect to the QA API
        const response = await fetch(`${API_URL}${API_CONFIG.ENDPOINTS.QA}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: query,
                top_k: 3
            })
        });

        if (response.ok) {
            const data = await response.json();
            displayQAResults(data);
        } else {
            throw new Error(`API Error: ${response.status}`);
        }
    } catch (error) {
        console.warn('QA API not available, using fallback:', error);
        // Fallback QA response
        setTimeout(() => {
            displayFallbackQA(query);
        }, 1000);
    }
}

function displayQAResults(data) {
    const resultsDiv = document.getElementById('searchResults');
    
    let html = `
        <div class="qa-results">
            <div class="qa-header">
                <h3>🤖 RAG Answer</h3>
                <p><strong>Question:</strong> "${data.question}"</p>
            </div>
            <div class="qa-answer">
                <h4>Answer:</h4>
                <p class="answer-text">${data.answer}</p>
            </div>
            <div class="qa-sources">
                <h4>📚 Sources Used:</h4>
                <div class="sources-grid">
    `;

    data.sources.forEach((source, index) => {
        const similarityPercent = Math.round(source.score * 100);
        html += `
            <div class="source-card">
                <div class="source-header">
                    <span class="source-id">${source.document_id}</span>
                    <span class="source-similarity">${similarityPercent}% relevant</span>
                </div>
                <p class="source-text">${source.document}</p>
            </div>
        `;
    });

    html += `
                </div>
            </div>
            <div class="qa-context">
                <h4>📖 Context Used:</h4>
                <p class="context-text">${data.context_used}</p>
            </div>
        </div>
    `;
    
    resultsDiv.innerHTML = html;
}

function displayFallbackQA(query) {
    const resultsDiv = document.getElementById('searchResults');
    
    // Simple fallback QA
    const answers = {
        'machine learning': 'Machine learning is a subset of artificial intelligence that focuses on algorithms that can learn from data.',
        'deep learning': 'Deep learning uses multiple layers of neural networks to model complex patterns in data.',
        'python': 'Python is a versatile programming language widely used in data science, web development, and automation.',
        'vector search': 'Vector similarity search enables finding semantically similar documents using embedding representations.'
    };

    let answer = 'I found some relevant information but need more context to provide a complete answer.';
    for (const [key, value] of Object.entries(answers)) {
        if (query.toLowerCase().includes(key)) {
            answer = value;
            break;
        }
    }

    resultsDiv.innerHTML = `
        <div class="qa-results">
            <div class="qa-header">
                <h3>🤖 Demo Answer</h3>
                <p><strong>Question:</strong> "${query}"</p>
                <p><em>Note: This is a demo response. Connect your backend API for real RAG answers.</em></p>
            </div>
            <div class="qa-answer">
                <h4>Answer:</h4>
                <p class="answer-text">${answer}</p>
            </div>
        </div>
    `;
}

// Add QA button functionality
function toggleMode() {
    const searchBtn = document.querySelector('.search-btn');
    const isSearchMode = searchBtn.textContent.includes('Search');
    
    if (isSearchMode) {
        searchBtn.textContent = '🤖 Ask Question (RAG)';
        searchBtn.onclick = performQA;
        document.getElementById('searchInput').placeholder = 'Ask a question (e.g., "What is machine learning?")';
    } else {
        searchBtn.textContent = '🔍 Search Documents';
        searchBtn.onclick = performSearch;
        document.getElementById('searchInput').placeholder = 'Enter your search query (e.g., "machine learning algorithms")';
    }
}

function displayFallbackResults(query) {
    const resultsDiv = document.getElementById('searchResults');
    
    // Simple keyword matching for demo
    const queryWords = query.toLowerCase().split(' ');
    let relevantPapers = fallbackPapers.map(paper => {
        let relevanceScore = 0;
        queryWords.forEach(word => {
            if (paper.title.toLowerCase().includes(word) || 
                paper.abstract.toLowerCase().includes(word) ||
                paper.keywords.some(k => k.toLowerCase().includes(word))) {
                relevanceScore += 0.1;
            }
        });
        return {
            ...paper,
            similarity: Math.min(0.98, paper.similarity + relevanceScore)
        };
    });

    // Sort by similarity score
    relevantPapers.sort((a, b) => b.similarity - a.similarity);

    let html = `
        <div class="search-header">
            <h3>🎯 Demo Results for "${query}"</h3>
            <p><em>Note: This is demo data. Connect your backend API for real results.</em></p>
        </div>
        <div class="results-grid">
    `;

    relevantPapers.forEach((paper, index) => {
        const similarityPercent = Math.round(paper.similarity * 100);
        html += `
            <div class="result-card" style="animation-delay: ${index * 0.1}s">
                <div class="result-header">
                    <div class="similarity-badge">${similarityPercent}% match</div>
                    <div class="result-meta">${paper.year} • ${paper.venue}</div>
                </div>
                <div class="result-content">
                    <h4 class="result-title">${paper.title}</h4>
                    <p class="result-abstract">${paper.abstract}</p>
                    <div class="result-keywords">
                        ${paper.keywords.map(k => `<span class="keyword">${k}</span>`).join('')}
                    </div>
                </div>
                <div class="result-footer">
                    <span class="result-author">By ${paper.authors}</span>
                </div>
            </div>
        `;
    });

    html += `</div>`;
    resultsDiv.innerHTML = html;
}

// Question Answering functionality
async function performQA() {
    const query = document.getElementById('searchInput').value.trim();
    if (!query) {
        alert('Please enter a question');
        return;
    }

    const resultsDiv = document.getElementById('searchResults');
    
    // Show loading
    resultsDiv.innerHTML = `
        <div class="loading">
            <div class="spinner"></div>
            <p>🤖 Generating answer using RAG...</p>
            <p>🔍 Retrieving relevant documents...</p>
            <p>🧠 Processing with language model...</p>
        </div>
    `;

    try {
        // Try to connect to the QA API
        const response = await fetch(`${API_URL}${API_CONFIG.ENDPOINTS.QA}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: query,
                top_k: 3
            })
        });

        if (response.ok) {
            const data = await response.json();
            displayQAResults(data);
        } else {
            throw new Error(`API Error: ${response.status}`);
        }
    } catch (error) {
        console.warn('QA API not available, using fallback:', error);
        // Fallback QA response
        setTimeout(() => {
            displayFallbackQA(query);
        }, 1000);
    }
}

function displayQAResults(data) {
    const resultsDiv = document.getElementById('searchResults');
    
    let html = `
        <div class="qa-results">
            <div class="qa-header">
                <h3>🤖 RAG Answer</h3>
                <p><strong>Question:</strong> "${data.question}"</p>
            </div>
            <div class="qa-answer">
                <h4>Answer:</h4>
                <p class="answer-text">${data.answer}</p>
            </div>
            <div class="qa-sources">
                <h4>📚 Sources Used:</h4>
                <div class="sources-grid">
    `;

    data.sources.forEach((source, index) => {
        const similarityPercent = Math.round(source.score * 100);
        html += `
            <div class="source-card">
                <div class="source-header">
                    <span class="source-id">${source.document_id}</span>
                    <span class="source-similarity">${similarityPercent}% relevant</span>
                </div>
                <p class="source-text">${source.document}</p>
            </div>
        `;
    });

    html += `
                </div>
            </div>
            <div class="qa-context">
                <h4>📖 Context Used:</h4>
                <p class="context-text">${data.context_used}</p>
            </div>
        </div>
    `;
    
    resultsDiv.innerHTML = html;
}

function displayFallbackQA(query) {
    const resultsDiv = document.getElementById('searchResults');
    
    // Simple fallback QA
    const answers = {
        'machine learning': 'Machine learning is a subset of artificial intelligence that focuses on algorithms that can learn from data.',
        'deep learning': 'Deep learning uses multiple layers of neural networks to model complex patterns in data.',
        'python': 'Python is a versatile programming language widely used in data science, web development, and automation.',
        'vector search': 'Vector similarity search enables finding semantically similar documents using embedding representations.'
    };

    let answer = 'I found some relevant information but need more context to provide a complete answer.';
    for (const [key, value] of Object.entries(answers)) {
        if (query.toLowerCase().includes(key)) {
            answer = value;
            break;
        }
    }

    resultsDiv.innerHTML = `
        <div class="qa-results">
            <div class="qa-header">
                <h3>🤖 Demo Answer</h3>
                <p><strong>Question:</strong> "${query}"</p>
                <p><em>Note: This is a demo response. Connect your backend API for real RAG answers.</em></p>
            </div>
            <div class="qa-answer">
                <h4>Answer:</h4>
                <p class="answer-text">${answer}</p>
            </div>
        </div>
    `;
}

// Add QA button functionality
function toggleMode() {
    const searchBtn = document.querySelector('.search-btn');
    const isSearchMode = searchBtn.textContent.includes('Search');
    
    if (isSearchMode) {
        searchBtn.textContent = '🤖 Ask Question (RAG)';
        searchBtn.onclick = performQA;
        document.getElementById('searchInput').placeholder = 'Ask a question (e.g., "What is machine learning?")';
    } else {
        searchBtn.textContent = '🔍 Search Documents';
        searchBtn.onclick = performSearch;
        document.getElementById('searchInput').placeholder = 'Enter your search query (e.g., "machine learning algorithms")';
    }
}
