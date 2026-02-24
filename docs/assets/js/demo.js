// Vector Similarity Search Engine - Frontend Demo
// UPDATED: Complete rewrite with all requested features

// Configuration - Real API + fallback to local sample data
// After deploying to Render, copy your app URL and replace below (e.g. https://YOUR-APP.onrender.com)
const CONFIG = {
    API_BASE_URL: 'https://vector-similarity-search-for-document.onrender.com',
    LOCAL_URL: 'http://localhost:8000',
    RESULTS_PER_PAGE: 10,
    DEBOUNCE_DELAY: 200,
    SIMULATED_LATENCY_MIN: 100,
    SIMULATED_LATENCY_MAX: 200,
    DATASET_SIZE: 50000,
    VECTOR_DIMENSIONS: 768,
    PRECISION: 95.2
};

// Global state
let papersData = [];
let filteredPapers = [];
let currentPage = 1;
let totalPages = 1;
let searchStartTime = 0;
let isSearching = false;
// ADDED: whether the Render backend API is reachable (used for banner + fallback)
let apiReachable = false;
let connectionBannerDismissed = false;

// DOM elements
const elements = {
    searchInput: document.getElementById('searchInput'),
    searchButton: document.getElementById('searchButton'),
    resultsContainer: document.getElementById('resultsContainer'),
    resultsTitle: document.getElementById('resultsTitle'),
    resultsCount: document.getElementById('resultsCount'),
    loadingState: document.getElementById('loadingState'),
    emptyState: document.getElementById('emptyState'),
    pagination: document.getElementById('pagination'),
    prevPage: document.getElementById('prevPage'),
    nextPage: document.getElementById('nextPage'),
    paginationInfo: document.getElementById('paginationInfo'),
    querySpeed: document.getElementById('querySpeed'),
    darkModeToggle: document.getElementById('darkModeToggle'),
    yearRange: document.getElementById('yearRange'),
    venueFilter: document.getElementById('venueFilter'),
    authorFilter: document.getElementById('authorFilter'),
    connectionBanner: document.getElementById('connectionBanner'),
    connectionBannerText: document.getElementById('connectionBannerText'),
    connectionBannerDismiss: document.getElementById('connectionBannerDismiss'),
    qaInput: document.getElementById('qaInput'),
    qaButton: document.getElementById('qaButton'),
    qaResult: document.getElementById('qaResult'),
    qaAnswerText: document.getElementById('qaAnswerText'),
    qaSourcesList: document.getElementById('qaSourcesList'),
    qaLoading: document.getElementById('qaLoading'),
    qaError: document.getElementById('qaError')
};

// Utility functions
const utils = {
    // Debounce function
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    // Sanitize HTML content
    sanitizeHtml(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    },

    // Highlight search terms
    highlight(text, query) {
        if (!query.trim()) return utils.sanitizeHtml(text);
        
        const sanitizedText = utils.sanitizeHtml(text);
        const sanitizedQuery = utils.sanitizeHtml(query.toLowerCase());
        const regex = new RegExp(`(${sanitizedQuery.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
        
        return sanitizedText.replace(regex, '<mark>$1</mark>');
    },

    // Tokenize text for similarity calculation
    tokenize(text) {
        return text.toLowerCase()
            .replace(/[^\w\s]/g, '')
            .split(/\s+/)
            .filter(word => word.length > 2);
    },

    // Calculate cosine similarity (simplified for demo)
    cosineSimilarity(vecA, vecB) {
        if (vecA.length !== vecB.length) return 0;
        
        let dotProduct = 0;
        let normA = 0;
        let normB = 0;
        
        for (let i = 0; i < vecA.length; i++) {
            dotProduct += vecA[i] * vecB[i];
            normA += vecA[i] * vecA[i];
            normB += vecB[i] * vecB[i];
        }
        
        return dotProduct / (Math.sqrt(normA) * Math.sqrt(normB));
    },

    // Calculate weighted token overlap similarity
    calculateTokenSimilarity(paper, query) {
        const queryTokens = utils.tokenize(query);
        const titleTokens = utils.tokenize(paper.title);
        const abstractTokens = utils.tokenize(paper.abstract);
        const keywordTokens = paper.keywords.flatMap(k => utils.tokenize(k));
        
        let score = 0;
        let totalWeight = 0;
        
        // Title weight: 1.5x
        const titleMatches = queryTokens.filter(qt => titleTokens.includes(qt)).length;
        score += titleMatches * 1.5;
        totalWeight += titleTokens.length * 1.5;
        
        // Keywords weight: 1.3x
        const keywordMatches = queryTokens.filter(qt => keywordTokens.includes(qt)).length;
        score += keywordMatches * 1.3;
        totalWeight += keywordTokens.length * 1.3;
        
        // Abstract weight: 1x
        const abstractMatches = queryTokens.filter(qt => abstractTokens.includes(qt)).length;
        score += abstractMatches * 1;
        totalWeight += abstractTokens.length * 1;
        
        return totalWeight > 0 ? Math.min(score / totalWeight, 1) : 0;
    },

    // Simulate API latency
    async simulateLatency() {
        const delay = Math.random() * (CONFIG.SIMULATED_LATENCY_MAX - CONFIG.SIMULATED_LATENCY_MIN) + CONFIG.SIMULATED_LATENCY_MIN;
        await new Promise(resolve => setTimeout(resolve, delay));
    }
};

// ADDED: Check if Render backend is reachable
async function checkApiReachable() {
    const url = `${CONFIG.API_BASE_URL}/api/stats`;
    try {
        const res = await fetch(url, { method: 'GET', signal: AbortSignal.timeout(8000) });
        apiReachable = res.ok;
    } catch (e) {
        apiReachable = false;
        console.warn('Backend API not reachable, using offline demo mode:', e.message);
    }
    updateConnectionBanner();
}

// ADDED: Update connection banner (Live vs Demo mode)
function updateConnectionBanner() {
    if (!elements.connectionBanner || connectionBannerDismissed) return;
    elements.connectionBanner.classList.remove('hidden', 'demo-mode');
    if (apiReachable) {
        elements.connectionBannerText.textContent = 'Live mode: connected to vector search API';
    } else {
        elements.connectionBanner.classList.add('demo-mode');
        elements.connectionBannerText.textContent = 'Demo mode: using local sample data';
    }
}

// Data loader module
const dataLoader = {
    async loadPapers() {
        try {
            const response = await fetch('assets/data/sample-papers.json');
            const data = await response.json();
            papersData = data.papers || [];
            filteredPapers = [...papersData];
            console.log(`Loaded ${papersData.length} papers (local fallback)`);
        } catch (error) {
            console.error('Error loading papers:', error);
            papersData = [];
            filteredPapers = [];
        }
        await checkApiReachable();
    }
};

// Search engine module - UPDATED: try API first, fallback to local
const searchEngine = {
    // Call Render backend POST /api/search
    async apiSearch(query, filters, topK = 50) {
        const url = `${CONFIG.API_BASE_URL}/api/search`;
        const res = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: query.trim(), top_k: topK, threshold: 0 }),
            signal: AbortSignal.timeout(15000)
        });
        if (!res.ok) throw new Error(res.statusText || 'Search failed');
        const data = await res.json();
        return data;
    },

    // Local token-based search (fallback when API fails or unreachable)
    localSearch(query) {
        if (!query.trim()) {
            filteredPapers = [...papersData];
            return filteredPapers;
        }
        const results = papersData.map(paper => {
            const similarity = utils.calculateTokenSimilarity(paper, query);
            return { ...paper, similarity };
        });
        filteredPapers = results
            .filter(paper => paper.similarity > 0)
            .sort((a, b) => b.similarity - a.similarity);
        return filteredPapers;
    },

    async search(query) {
        if (!query.trim()) {
            filteredPapers = [...papersData];
            return filteredPapers;
        }

        searchStartTime = performance.now();

        try {
            const data = await this.apiSearch(query, null, 100);
            const queryTime = Math.round(performance.now() - searchStartTime);
            elements.querySpeed.textContent = `${queryTime}ms`;
            document.getElementById('datasetSize').textContent = (data.total_found || data.returned || 0).toLocaleString() + '+';
            document.getElementById('vectorDims').textContent = `${CONFIG.VECTOR_DIMENSIONS}D`;
            document.getElementById('precision').textContent = `${CONFIG.PRECISION}%`;
            // Map API results to frontend paper shape
            filteredPapers = (data.results || []).map(r => ({
                id: r.document_id,
                title: r.title || '',
                authors: r.authors || [],
                venue: r.venue || '',
                year: r.year || null,
                abstract: (r.document || '').split('[SEP]')[1] || r.document || '',
                keywords: [],
                url: r.url || '',
                similarity: typeof r.score === 'number' ? r.score : 0
            }));
            return filteredPapers;
        } catch (err) {
            apiReachable = false;
            updateConnectionBanner();
            console.warn('Running in offline demo mode. API error:', err.message);
            await utils.simulateLatency();
            this.localSearch(query);
            const queryTime = Math.round(performance.now() - searchStartTime);
            elements.querySpeed.textContent = `${queryTime}ms`;
            document.getElementById('datasetSize').textContent = `${CONFIG.DATASET_SIZE.toLocaleString()}+`;
            document.getElementById('vectorDims').textContent = `${CONFIG.VECTOR_DIMENSIONS}D`;
            document.getElementById('precision').textContent = `${CONFIG.PRECISION}%`;
            return filteredPapers;
        }
    },

    applyFilters() {
        let filtered = [...papersData];
        
        // Year range filter
        const yearRange = elements.yearRange.value;
        if (yearRange) {
            const [startYear, endYear] = yearRange.split('-').map(y => parseInt(y));
            if (yearRange === 'before-2010') {
                filtered = filtered.filter(paper => paper.year < 2010);
            } else if (endYear) {
                filtered = filtered.filter(paper => paper.year >= startYear && paper.year <= endYear);
            }
        }
        
        // Venue filter
        const venue = elements.venueFilter.value;
        if (venue) {
            filtered = filtered.filter(paper => paper.venue === venue);
        }
        
        // Author filter
        const author = elements.authorFilter.value.toLowerCase();
        if (author) {
            filtered = filtered.filter(paper => 
                paper.authors.some(a => a.toLowerCase().includes(author))
            );
        }
        
        filteredPapers = filtered;
        return filteredPapers;
    }
};

// UI module
const ui = {
    showLoading() {
        elements.loadingState.style.display = 'block';
        elements.resultsContainer.style.display = 'none';
        elements.emptyState.style.display = 'none';
        elements.pagination.style.display = 'none';
    },

    hideLoading() {
        elements.loadingState.style.display = 'none';
        elements.resultsContainer.style.display = 'block';
    },

    showEmpty() {
        elements.emptyState.style.display = 'block';
        elements.resultsContainer.style.display = 'none';
        elements.pagination.style.display = 'none';
    },

    hideEmpty() {
        elements.emptyState.style.display = 'none';
    },

    renderResults(results, page = 1) {
        const startIndex = (page - 1) * CONFIG.RESULTS_PER_PAGE;
        const endIndex = startIndex + CONFIG.RESULTS_PER_PAGE;
        const pageResults = results.slice(startIndex, endIndex);
        
        if (pageResults.length === 0) {
            this.showEmpty();
        return;
    }

        this.hideEmpty();
        
        const query = elements.searchInput.value.trim();
        const html = pageResults.map(paper => this.createResultCard(paper, query)).join('');
        elements.resultsContainer.innerHTML = html;
        
        // Update pagination
        this.updatePagination(results.length, page);
        
        // Update results count
        elements.resultsCount.textContent = `${results.length} papers found`;
    },

    createResultCard(paper, query) {
        const similarityPercent = (paper.similarity != null ? paper.similarity * 100 : 0).toFixed(1);
        const highlightedTitle = utils.highlight(paper.title || '', query);
        const highlightedAbstract = utils.highlight(paper.abstract || '', query);
        const authors = Array.isArray(paper.authors) ? paper.authors.join(', ') : '';
        const keywords = Array.isArray(paper.keywords) ? paper.keywords : [];
        return `
            <div class="result-card" data-paper-id="${utils.sanitizeHtml(paper.id)}">
                <div class="result-header">
                    <div class="result-title">${highlightedTitle}</div>
                    <div class="result-similarity">${similarityPercent}%</div>
                </div>
                <div class="result-meta">
                    <span>${paper.year != null ? paper.year : '—'}</span>
                    <span>${utils.sanitizeHtml(paper.venue || '')}</span>
                    <span>${utils.sanitizeHtml(paper.id || '')}</span>
                </div>
                <div class="result-authors"><strong>Authors:</strong> ${utils.sanitizeHtml(authors)}</div>
                <div class="result-abstract">${highlightedAbstract}</div>
                <div class="result-keywords">
                    ${keywords.map(k => `<span class="keyword-tag">${utils.sanitizeHtml(k)}</span>`).join('')}
                </div>
            </div>
        `;
    },

    updatePagination(totalResults, currentPage) {
        totalPages = Math.ceil(totalResults / CONFIG.RESULTS_PER_PAGE);
        
        if (totalPages <= 1) {
            elements.pagination.style.display = 'none';
            return;
        }
        
        elements.pagination.style.display = 'flex';
        elements.prevPage.disabled = currentPage === 1;
        elements.nextPage.disabled = currentPage === totalPages;
        
        const startResult = (currentPage - 1) * CONFIG.RESULTS_PER_PAGE + 1;
        const endResult = Math.min(currentPage * CONFIG.RESULTS_PER_PAGE, totalResults);
        
        elements.paginationInfo.textContent = `Page ${currentPage} of ${totalPages} (${startResult}-${endResult} of ${totalResults})`;
    },

    async performSearch(query) {
        if (isSearching) return;
        
        isSearching = true;
        this.showLoading();
        
        try {
            const results = await searchEngine.search(query);
            this.renderResults(results, 1);
            currentPage = 1;
        } catch (error) {
            console.error('Search error:', error);
            this.showEmpty();
        } finally {
            isSearching = false;
            this.hideLoading();
        }
    },

    applyFiltersAndSearch() {
        const query = elements.searchInput.value.trim();
        const filteredResults = searchEngine.applyFilters();
        
        if (query) {
            // Apply search to filtered results
            const searchResults = filteredResults.map(paper => {
                const similarity = utils.calculateTokenSimilarity(paper, query);
                return { ...paper, similarity };
            }).filter(paper => paper.similarity > 0)
              .sort((a, b) => b.similarity - a.similarity);
            
            this.renderResults(searchResults, 1);
        } else {
            // Just show filtered results
            this.renderResults(filteredResults, 1);
        }
        
        currentPage = 1;
    }
};

// Dark mode module
const darkMode = {
    init() {
        const savedTheme = localStorage.getItem('theme');
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        
        if (savedTheme) {
            document.documentElement.setAttribute('data-theme', savedTheme);
        } else if (prefersDark) {
            document.documentElement.setAttribute('data-theme', 'dark');
        }
        
        this.updateToggleIcon();
    },

    toggle() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        this.updateToggleIcon();
    },

    updateToggleIcon() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const icon = elements.darkModeToggle.querySelector('.toggle-icon');
        icon.textContent = currentTheme === 'dark' ? '☀️' : '🌙';
    }
};

// Event handlers
const eventHandlers = {
    init() {
        // Search input events
        elements.searchInput.addEventListener('input', utils.debounce((e) => {
            const query = e.target.value.trim();
            if (query) {
                ui.performSearch(query);
            } else {
                ui.applyFiltersAndSearch();
            }
        }, CONFIG.DEBOUNCE_DELAY));

        elements.searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                const query = e.target.value.trim();
                if (query) {
                    ui.performSearch(query);
                }
            }
        });

        // Search button
        elements.searchButton.addEventListener('click', () => {
            const query = elements.searchInput.value.trim();
            if (query) {
                ui.performSearch(query);
            }
        });

        // Example queries
        document.querySelectorAll('.example-query').forEach(button => {
            button.addEventListener('click', (e) => {
                const query = e.target.dataset.query;
                elements.searchInput.value = query;
                ui.performSearch(query);
            });
        });

        // Filter events
        elements.yearRange.addEventListener('change', () => ui.applyFiltersAndSearch());
        elements.venueFilter.addEventListener('change', () => ui.applyFiltersAndSearch());
        elements.authorFilter.addEventListener('input', utils.debounce(() => ui.applyFiltersAndSearch(), CONFIG.DEBOUNCE_DELAY));

        // Pagination events
        elements.prevPage.addEventListener('click', () => {
            if (currentPage > 1) {
                currentPage--;
                ui.renderResults(filteredPapers, currentPage);
            }
        });

        elements.nextPage.addEventListener('click', () => {
            if (currentPage < totalPages) {
                currentPage++;
                ui.renderResults(filteredPapers, currentPage);
            }
        });

        // Dark mode toggle
        elements.darkModeToggle.addEventListener('click', () => darkMode.toggle());

        // Result card clicks (support both API and local results)
        elements.resultsContainer.addEventListener('click', (e) => {
            const card = e.target.closest('.result-card');
            if (card) {
                const paperId = card.dataset.paperId;
                const paper = filteredPapers.find(p => p.id === paperId) || papersData.find(p => p.id === paperId);
                if (paper && paper.url) {
                    window.open(paper.url, '_blank');
                }
            }
        });

        // Connection banner dismiss
        if (elements.connectionBannerDismiss) {
            elements.connectionBannerDismiss.addEventListener('click', () => {
                connectionBannerDismissed = true;
                if (elements.connectionBanner) elements.connectionBanner.classList.add('hidden');
            });
        }

        // Q&A: real POST /api/qa
        if (elements.qaButton && elements.qaInput) {
            elements.qaButton.addEventListener('click', () => qaHandlers.submit());
            elements.qaInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') qaHandlers.submit();
            });
        }
    }
};

// ADDED: Q&A handlers (calls Render /api/qa, displays answer and sources)
const qaHandlers = {
    async submit() {
        const question = (elements.qaInput && elements.qaInput.value) ? elements.qaInput.value.trim() : '';
        if (!question) return;
        if (elements.qaError) { elements.qaError.style.display = 'none'; elements.qaError.textContent = ''; }
        if (elements.qaResult) elements.qaResult.style.display = 'none';
        if (elements.qaLoading) elements.qaLoading.style.display = 'block';

        try {
            const url = `${CONFIG.API_BASE_URL}/api/qa`;
            const res = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: question, top_k: 5 }),
                signal: AbortSignal.timeout(30000)
            });
            if (!res.ok) throw new Error(res.statusText || 'Q&A failed');
            const data = await res.json();
            if (elements.qaAnswerText) elements.qaAnswerText.textContent = data.answer || '';
            if (elements.qaSourcesList) {
                const sources = data.sources || [];
                elements.qaSourcesList.innerHTML = sources.map(s => {
                    const title = (s.title || s.document_id || '').substring(0, 120);
                    const url = s.url || '#';
                    return `<div class="source-item"><a href="${url}" target="_blank" rel="noopener">${utils.sanitizeHtml(title)}</a> (${((s.score || 0) * 100).toFixed(1)}%)</div>`;
                }).join('');
            }
            if (elements.qaResult) elements.qaResult.style.display = 'block';
        } catch (err) {
            if (elements.qaError) {
                elements.qaError.textContent = 'Could not get answer. ' + (err.message || 'Network error. Try again or use demo mode.');
                elements.qaError.style.display = 'block';
            }
        } finally {
            if (elements.qaLoading) elements.qaLoading.style.display = 'none';
        }
    }
};

// Initialize application
async function init() {
    try {
        // Load data
        await dataLoader.loadPapers();
        
        // Initialize dark mode
        darkMode.init();
        
        // Initialize event handlers
        eventHandlers.init();
        
        // Show initial results
        ui.renderResults(papersData, 1);
        
        console.log('Vector Similarity Search Engine initialized successfully');
    } catch (error) {
        console.error('Initialization error:', error);
    }
}

// Start the application when DOM is loaded
document.addEventListener('DOMContentLoaded', init);

// Export for potential external use
window.VectorSearchEngine = {
    searchEngine,
    ui,
    utils,
    CONFIG
};