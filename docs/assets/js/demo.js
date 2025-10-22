// Vector Similarity Search Engine - Frontend Demo
// UPDATED: Complete rewrite with all requested features

// Configuration
const CONFIG = {
    API_BASE_URL: 'https://vector-similarity-search-for-document.onrender.com',
    LOCAL_URL: 'http://localhost:8000',
    RESULTS_PER_PAGE: 10,
    DEBOUNCE_DELAY: 200,
    SIMULATED_LATENCY_MIN: 100,
    SIMULATED_LATENCY_MAX: 200
};

// Global state
let papersData = [];
let filteredPapers = [];
let currentPage = 1;
let totalPages = 1;
let searchStartTime = 0;
let isSearching = false;

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
    authorFilter: document.getElementById('authorFilter')
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

// Data loader module
const dataLoader = {
    async loadPapers() {
        try {
            const response = await fetch('assets/data/sample-papers.json');
            const data = await response.json();
            papersData = data.papers;
            filteredPapers = [...papersData];
            console.log(`Loaded ${papersData.length} papers`);
        } catch (error) {
            console.error('Error loading papers:', error);
            papersData = [];
            filteredPapers = [];
        }
    }
};

// Search engine module
const searchEngine = {
    async search(query) {
        if (!query.trim()) {
            filteredPapers = [...papersData];
            return filteredPapers;
        }

        searchStartTime = performance.now();
        
        // Simulate API latency
        await utils.simulateLatency();
        
        // Calculate similarity scores
        const results = papersData.map(paper => {
            const similarity = utils.calculateTokenSimilarity(paper, query);
            return {
                ...paper,
                similarity: similarity
            };
        });

        // Sort by similarity (descending)
        filteredPapers = results
            .filter(paper => paper.similarity > 0)
            .sort((a, b) => b.similarity - a.similarity);

        // Update query speed metric
        const queryTime = Math.round(performance.now() - searchStartTime);
        elements.querySpeed.textContent = `${queryTime}ms`;

        return filteredPapers;
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
        const similarityPercent = (paper.similarity * 100).toFixed(1);
        const highlightedTitle = utils.highlight(paper.title, query);
        const highlightedAbstract = utils.highlight(paper.abstract, query);
        
        return `
            <div class="result-card" data-paper-id="${paper.id}">
                <div class="result-header">
                    <div class="result-title">${highlightedTitle}</div>
                    <div class="result-similarity">${similarityPercent}%</div>
                </div>
                
                <div class="result-meta">
                    <span>📅 ${paper.year}</span>
                    <span>🏛️ ${paper.venue}</span>
                    <span>📄 ${paper.id}</span>
                </div>
                
                <div class="result-authors">
                    <strong>Authors:</strong> ${paper.authors.join(', ')}
                </div>
                
                <div class="result-abstract">
                    ${highlightedAbstract}
                </div>
                
                <div class="result-keywords">
                    ${paper.keywords.map(keyword => 
                        `<span class="keyword-tag">${utils.sanitizeHtml(keyword)}</span>`
                    ).join('')}
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

        // Result card clicks
        elements.resultsContainer.addEventListener('click', (e) => {
            const card = e.target.closest('.result-card');
            if (card) {
                const paperId = card.dataset.paperId;
                const paper = papersData.find(p => p.id === paperId);
                if (paper && paper.url) {
                    window.open(paper.url, '_blank');
                }
            }
        });
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