// Configuration for API endpoints - Updated to use Render only
const API_CONFIG = {
    // Your deployed Render backend URL
    BASE_URL: 'https://vector-similarity-search-for-document.onrender.com',
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

// Global state
let currentMode = 'search'; // 'search' or 'qa'

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

// Search query function for demo buttons
function searchQuery(query) {
    document.getElementById('searchInput').value = query;
    performSearch();
}

// Main search function
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
                'Accept': 'application/json',
            },
            mode: 'cors',
            credentials: 'omit',
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

// Q&A function
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
                'Accept': 'application/json',
            },
            mode: 'cors',
            credentials: 'omit',
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
        console.warn('API not available, using fallback data:', error);
        // Fallback to demo data
        setTimeout(() => {
            displayFallbackQA(query);
        }, 1000);
    }
}

// Toggle between search and Q&A modes
function toggleMode() {
    const searchBtn = document.querySelector('.search-btn');
    const toggleBtn = document.querySelector('.toggle-btn');
    const searchInput = document.getElementById('searchInput');
    
    if (currentMode === 'search') {
        // Switch to Q&A mode
        currentMode = 'qa';
        searchBtn.textContent = '🤖 Ask Question (RAG)';
        searchBtn.onclick = performQA;
        toggleBtn.textContent = '🔍 Switch to Search';
        searchInput.placeholder = 'Ask a question (e.g., "What is machine learning?")';
    } else {
        // Switch to search mode
        currentMode = 'search';
        searchBtn.textContent = '🔍 Search Documents';
        searchBtn.onclick = performSearch;
        toggleBtn.textContent = '🤖 Switch to Q&A';
        searchInput.placeholder = 'Enter your research query (e.g., "deep learning for medical image analysis")';
    }
}

// Display API search results
function displayAPIResults(data) {
    const resultsDiv = document.getElementById('searchResults');
    
    if (!data.results || data.results.length === 0) {
        resultsDiv.innerHTML = `
            <div class="no-results">
                <h3>🔍 No Results Found</h3>
                <p>Try a different search query or check your spelling.</p>
            </div>
        `;
        return;
    }

    let html = `
        <div class="results-header">
            <h3>🔍 Search Results</h3>
            <p>Found ${data.total_found} relevant documents for "${data.query}"</p>
        </div>
        <div class="results-grid">
    `;

    data.results.forEach((result, index) => {
        const similarityPercent = Math.round(result.score * 100);
        const truncatedText = result.document.length > 150 ? result.document.substring(0, 150) + '...' : result.document;
        
        // Generate a mock title from the document content
        const title = generateDocumentTitle(result.document);
        const authors = generateDocumentAuthors(result.document_id);
        const venue = generateDocumentVenue(result.document_id);
        const year = generateDocumentYear(result.document_id);
        
        html += `
            <div class="result-card" onclick="expandResult(${index})">
                <div class="result-header">
                    <span class="result-number">#${index + 1}</span>
                    <span class="similarity-score">${similarityPercent}% match</span>
                    <span class="expand-icon">📖 Click to read full content</span>
                </div>
                <div class="result-content">
                    <h4 class="document-title">${title}</h4>
                    <div class="document-meta">
                        <span class="authors">👤 ${authors}</span>
                        <span class="venue">🏛️ ${venue}</span>
                        <span class="year">📅 ${year}</span>
                    </div>
                    <p class="result-text" id="text-${index}">${truncatedText}</p>
                    <div class="result-actions">
                        <button class="action-btn view-btn" onclick="event.stopPropagation(); viewFullDocument('${result.document_id}')">
                            📄 View Full Document
                        </button>
                        <button class="action-btn cite-btn" onclick="event.stopPropagation(); citeDocument('${result.document_id}', '${title}', '${authors}', '${year}')">
                            📋 Cite This Paper
                        </button>
                    </div>
                    <div class="result-meta">
                        <span class="document-id">Document ID: ${result.document_id}</span>
                        <span class="distance">Distance: ${result.distance.toFixed(4)}</span>
                    </div>
                </div>
                <div class="full-content" id="full-${index}" style="display: none;">
                    <div class="full-text">
                        <h4>📄 Full Document Content:</h4>
                        <div class="document-info">
                            <h5>${title}</h5>
                            <p><strong>Authors:</strong> ${authors}</p>
                            <p><strong>Venue:</strong> ${venue}</p>
                            <p><strong>Year:</strong> ${year}</p>
                        </div>
                        <div class="document-content">
                            <p>${result.document}</p>
                        </div>
                    </div>
                    <div class="full-actions">
                        <button class="action-btn view-btn" onclick="event.stopPropagation(); viewFullDocument('${result.document_id}')">
                            📄 View Full Document
                        </button>
                        <button class="action-btn cite-btn" onclick="event.stopPropagation(); citeDocument('${result.document_id}', '${title}', '${authors}', '${year}')">
                            📋 Cite This Paper
                        </button>
                        <button class="close-btn" onclick="event.stopPropagation(); collapseResult(${index})">✕ Close</button>
                    </div>
                </div>
            </div>
        `;
    });

    html += '</div>';
    resultsDiv.innerHTML = html;
}

// Display API Q&A results
function displayQAResults(data) {
    const resultsDiv = document.getElementById('searchResults');
    
    let html = `
        <div class="qa-results">
            <div class="qa-header">
                <h3>🤖 RAG Answer</h3>
                <p>Question: "${data.question}"</p>
            </div>
            <div class="qa-answer">
                <p>${data.answer}</p>
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
                    <span class="source-id">Source ${index + 1}</span>
                    <span class="source-similarity">${similarityPercent}% relevant</span>
                </div>
                <div class="source-text">${source.document}</div>
                <div class="source-meta">Document ID: ${source.document_id}</div>
            </div>
        `;
    });

    html += `
                </div>
            </div>
            <div class="qa-context">
                <h4>📖 Context Used:</h4>
                <div class="context-text">${data.context_used}</div>
            </div>
        </div>
    `;

    resultsDiv.innerHTML = html;
}

// Display fallback search results
function displayFallbackResults(query) {
    const resultsDiv = document.getElementById('searchResults');
    
    let html = `
        <div class="results-header">
            <h3>🔍 Search Results (Demo Mode)</h3>
            <p>Found ${fallbackPapers.length} relevant documents for "${query}"</p>
            <div class="demo-notice">
                <small>⚠️ Demo mode: Showing sample data. Backend API not available.</small>
            </div>
        </div>
        <div class="results-grid">
    `;

    fallbackPapers.forEach((paper, index) => {
        const similarityPercent = Math.round(paper.similarity * 100);
        html += `
            <div class="result-card">
                <div class="result-header">
                    <span class="result-number">#${index + 1}</span>
                    <span class="similarity-score">${similarityPercent}% match</span>
                </div>
                <div class="result-content">
                    <h4 class="result-title">${paper.title}</h4>
                    <p class="result-text">${paper.abstract}</p>
                    <div class="result-meta">
                        <span class="authors">Authors: ${paper.authors}</span>
                        <span class="year">Year: ${paper.year}</span>
                        <span class="venue">Venue: ${paper.venue}</span>
                    </div>
                    <div class="keywords">
                        ${paper.keywords.map(keyword => `<span class="keyword">${keyword}</span>`).join('')}
                    </div>
                </div>
            </div>
        `;
    });

    html += '</div>';
    resultsDiv.innerHTML = html;
}

// Display fallback Q&A results
function displayFallbackQA(query) {
    const resultsDiv = document.getElementById('searchResults');
    
    const demoAnswers = {
        'what is machine learning': 'Machine learning is a subset of artificial intelligence that focuses on algorithms that can learn from data without being explicitly programmed.',
        'what is deep learning': 'Deep learning uses multiple layers of neural networks to model complex patterns in data, inspired by the structure of the human brain.',
        'what is python': 'Python is a versatile programming language widely used in data science, web development, and automation due to its simplicity and powerful libraries.'
    };

    const answer = demoAnswers[query.toLowerCase()] || 'This is a demo answer. In a real system, this would be generated using RAG (Retrieval-Augmented Generation) with your indexed documents.';

    resultsDiv.innerHTML = `
        <div class="qa-results">
            <div class="qa-header">
                <h3>🤖 RAG Answer (Demo Mode)</h3>
                <p>Question: "${query}"</p>
                <div class="demo-notice">
                    <small>⚠️ Demo mode: Showing sample answer. Backend API not available.</small>
                </div>
            </div>
            <div class="qa-answer">
                <p>${answer}</p>
            </div>
            <div class="qa-sources">
                <h4>📚 Sample Sources:</h4>
                <div class="sources-grid">
                    <div class="source-card">
                        <div class="source-header">
                            <span class="source-id">Source 1</span>
                            <span class="source-similarity">95% relevant</span>
                        </div>
                        <div class="source-text">${fallbackPapers[0].abstract}</div>
                        <div class="source-meta">Document ID: doc_0</div>
                    </div>
                    <div class="source-card">
                        <div class="source-header">
                            <span class="source-id">Source 2</span>
                            <span class="source-similarity">88% relevant</span>
                        </div>
                        <div class="source-text">${fallbackPapers[1].abstract}</div>
                        <div class="source-meta">Document ID: doc_1</div>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// Helper functions to generate document metadata
function generateDocumentTitle(document) {
    // Extract first sentence or first 60 characters as title
    const firstSentence = document.split('.')[0];
    if (firstSentence.length > 60) {
        return firstSentence.substring(0, 60) + '...';
    }
    return firstSentence || 'Research Document';
}

function generateDocumentAuthors(documentId) {
    const authorMap = {
        'doc_0': 'Dr. Sarah Johnson',
        'doc_1': 'Prof. Michael Chen',
        'doc_2': 'Dr. Emily Rodriguez',
        'doc_3': 'Prof. David Kim',
        'doc_4': 'Dr. Lisa Wang',
        'doc_5': 'Prof. James Brown',
        'doc_6': 'Dr. Maria Garcia',
        'doc_7': 'Prof. Robert Taylor',
        'doc_8': 'Dr. Jennifer Lee',
        'doc_9': 'Prof. Christopher Davis'
    };
    return authorMap[documentId] || 'Research Team';
}

function generateDocumentVenue(documentId) {
    const venueMap = {
        'doc_0': 'Journal of Machine Learning',
        'doc_1': 'Nature AI Research',
        'doc_2': 'IEEE Transactions on AI',
        'doc_3': 'ACM Computing Surveys',
        'doc_4': 'Science Robotics',
        'doc_5': 'Neural Information Processing',
        'doc_6': 'International AI Conference',
        'doc_7': 'Machine Learning Review',
        'doc_8': 'AI & Society Journal',
        'doc_9': 'Computational Intelligence'
    };
    return venueMap[documentId] || 'Research Publication';
}

function generateDocumentYear(documentId) {
    const yearMap = {
        'doc_0': '2024',
        'doc_1': '2023',
        'doc_2': '2024',
        'doc_3': '2023',
        'doc_4': '2024',
        'doc_5': '2023',
        'doc_6': '2024',
        'doc_7': '2023',
        'doc_8': '2024',
        'doc_9': '2023'
    };
    return yearMap[documentId] || '2024';
}

// Action functions for document interaction
function viewFullDocument(documentId) {
    // In a real system, this would open the full document
    // For now, we'll show an alert with instructions
    alert(`📄 View Full Document\n\nDocument ID: ${documentId}\n\nIn a production system, this would:\n• Open the full research paper\n• Navigate to the publisher's website\n• Show PDF or HTML version\n• Allow downloading\n\nFor now, expand the result above to read the full content.`);
}

function citeDocument(documentId, title, authors, year) {
    const citation = `${authors} (${year}). "${title}". Retrieved from RAG Vector Search System.`;
    
    // Copy to clipboard
    navigator.clipboard.writeText(citation).then(() => {
        alert(`📋 Citation Copied to Clipboard!\n\n${citation}\n\nYou can now paste this citation in your research document.`);
    }).catch(() => {
        // Fallback if clipboard API fails
        const textArea = document.createElement('textarea');
        textArea.value = citation;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        alert(`📋 Citation Ready to Copy!\n\n${citation}\n\nCitation has been selected. Press Ctrl+C to copy.`);
    });
}

// Expand result function
function expandResult(index) {
    const fullContent = document.getElementById(`full-${index}`);
    const textElement = document.getElementById(`text-${index}`);
    
    if (fullContent.style.display === 'none') {
        fullContent.style.display = 'block';
        textElement.style.display = 'none';
    }
}

// Collapse result function
function collapseResult(index) {
    const fullContent = document.getElementById(`full-${index}`);
    const textElement = document.getElementById(`text-${index}`);
    
    fullContent.style.display = 'none';
    textElement.style.display = 'block';
}

// Initialize the page
document.addEventListener('DOMContentLoaded', function() {
    console.log('RAG System Frontend Loaded');
    console.log('API URL:', API_URL);
    console.log('Render Backend:', API_CONFIG.BASE_URL);
    console.log('Current Mode:', currentMode);
    
    // Set initial mode
    const searchBtn = document.querySelector('.search-btn');
    if (searchBtn) {
        searchBtn.onclick = performSearch;
    }
    
    // Add Enter key support for search input
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                if (currentMode === 'search') {
                    performSearch();
                } else {
                    performQA();
                }
            }
        });
    }
});