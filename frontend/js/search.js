/**
 * Search Manager - Handles real-time searching with debouncing
 * Features: Debounced search, filtering, highlighting, search history
 */

class SearchManager {
    constructor(debounceDelay = 300) {
        this.debounceDelay = debounceDelay;
        this.debounceTimers = {};
        this.searchHistory = [];
        this.maxHistoryItems = 5;
    }

    /**
     * Debounce a function
     */
    debounce(func, delay, id = 'default') {
        return (...args) => {
            // Clear existing timer for this ID
            if (this.debounceTimers[id]) {
                clearTimeout(this.debounceTimers[id]);
            }

            // Set new timer
            this.debounceTimers[id] = setTimeout(() => {
                func(...args);
                delete this.debounceTimers[id];
            }, delay);
        };
    }

    /**
     * Search and filter items by query
     */
    filterItems(items, query, searchFields) {
        if (!query || query.trim() === '') {
            return items;
        }

        const lowerQuery = query.toLowerCase().trim();
        
        return items.filter(item => {
            // Check if any of the search fields match the query
            return searchFields.some(field => {
                const value = this.getNestedValue(item, field);
                if (value === null || value === undefined) return false;
                return String(value).toLowerCase().includes(lowerQuery);
            });
        });
    }

    /**
     * Get nested object value by dot notation
     */
    getNestedValue(obj, path) {
        return path.split('.').reduce((current, prop) => {
            return current && current[prop] ? current[prop] : null;
        }, obj);
    }

    /**
     * Search students in real-time
     */
    searchStudents(allStudents, query, classes) {
        const searchFields = ['admission_number', 'full_name', 'parent_name', 'email'];
        const filtered = this.filterItems(allStudents, query, searchFields);

        return filtered.map(student => ({
            ...student,
            className: classes.find(c => c.id === student.class_id)?.name || 'N/A'
        }));
    }

    /**
     * Search teachers in real-time
     */
    searchTeachers(allTeachers, query) {
        const searchFields = ['staff_id', 'full_name', 'email', 'specialization'];
        return this.filterItems(allTeachers, query, searchFields);
    }

    /**
     * Search subjects in real-time
     */
    searchSubjects(allSubjects, query) {
        const searchFields = ['name', 'code', 'description'];
        return this.filterItems(allSubjects, query, searchFields);
    }

    /**
     * Search results in real-time
     */
    searchResults(allResults, query) {
        const searchFields = ['student_name', 'subject_name'];
        return this.filterItems(allResults, query, searchFields);
    }

    /**
     * Highlight search term in text
     */
    highlightText(text, query) {
        if (!query || query.trim() === '') {
            return text;
        }

        const regex = new RegExp(`(${query})`, 'gi');
        return String(text).replace(regex, '<mark>$1</mark>');
    }

    /**
     * Add to search history
     */
    addToHistory(query, category) {
        if (!query || query.trim() === '') return;

        const entry = {
            query: query.trim(),
            category: category,
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        };

        // Remove duplicate if exists
        this.searchHistory = this.searchHistory.filter(item => 
            !(item.query === entry.query && item.category === entry.category)
        );

        // Add to front
        this.searchHistory.unshift(entry);

        // Limit history
        this.searchHistory = this.searchHistory.slice(0, this.maxHistoryItems);

        // Save to localStorage
        localStorage.setItem('searchHistory', JSON.stringify(this.searchHistory));
    }

    /**
     * Get search history
     */
    getHistory() {
        const saved = localStorage.getItem('searchHistory');
        return saved ? JSON.parse(saved) : [];
    }

    /**
     * Clear search history
     */
    clearHistory() {
        this.searchHistory = [];
        localStorage.removeItem('searchHistory');
    }

    /**
     * Get search suggestions
     */
    getSuggestions(items, query, field) {
        if (!query || query.trim() === '') {
            return [];
        }

        const lowerQuery = query.toLowerCase().trim();
        const suggestions = new Set();

        items.forEach(item => {
            const value = this.getNestedValue(item, field);
            if (value && String(value).toLowerCase().includes(lowerQuery)) {
                suggestions.add(String(value));
            }
        });

        return Array.from(suggestions).slice(0, 5);
    }

    /**
     * Format search results count
     */
    formatResultCount(total, filtered) {
        if (filtered === total) {
            return `${total} items`;
        }
        return `${filtered} of ${total} items`;
    }
}

// Global search manager instance
const searchManager = new SearchManager(300); // 300ms debounce

/**
 * Add CSS styles for search functionality
 */
function initSearchStyles() {
    const style = document.createElement('style');
    style.textContent = `
        .search-input-wrapper {
            position: relative;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .search-input {
            flex: 1;
            padding: 0.75rem 1rem;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 0.95rem;
            transition: all 0.3s ease;
            background: white;
        }

        .search-input:focus {
            outline: none;
            border-color: #4ecdc4;
            box-shadow: 0 0 0 3px rgba(78, 205, 196, 0.1);
        }

        .search-input::placeholder {
            color: #999;
        }

        .search-clear-btn {
            padding: 0.5rem 0.75rem;
            background: #f0f0f0;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 1rem;
            transition: all 0.2s ease;
            display: none;
        }

        .search-clear-btn.visible {
            display: block;
        }

        .search-clear-btn:hover {
            background: #e0e0e0;
        }

        .search-results-info {
            font-size: 0.85rem;
            color: #666;
            font-weight: 500;
            display: inline-block;
            margin-left: 0.5rem;
            padding: 0.3rem 0.75rem;
            background: #f5f5f5;
            border-radius: 4px;
        }

        .search-history-container {
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: white;
            border: 1px solid #ddd;
            border-top: none;
            border-radius: 0 0 8px 8px;
            max-height: 250px;
            overflow-y: auto;
            z-index: 100;
            display: none;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }

        .search-history-container.visible {
            display: block;
        }

        .search-history-item {
            padding: 0.75rem 1rem;
            cursor: pointer;
            transition: all 0.2s ease;
            border-bottom: 1px solid #f0f0f0;
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-size: 0.9rem;
        }

        .search-history-item:hover {
            background: #f9f9f9;
            color: #4ecdc4;
        }

        .search-history-label {
            display: inline-block;
            font-size: 0.75rem;
            background: #4ecdc4;
            color: white;
            padding: 0.2rem 0.5rem;
            border-radius: 3px;
            margin-left: 0.5rem;
            font-weight: 600;
        }

        .search-history-time {
            font-size: 0.8rem;
            color: #999;
        }

        .no-results {
            padding: 1rem;
            text-align: center;
            color: #999;
            font-style: italic;
        }

        mark {
            background-color: #ffeb3b;
            padding: 0 2px;
            border-radius: 2px;
            font-weight: 600;
        }

        .search-highlight {
            animation: highlightPulse 0.5s ease;
        }

        @keyframes highlightPulse {
            0% {
                background-color: transparent;
            }
            50% {
                background-color: rgba(78, 205, 196, 0.2);
            }
            100% {
                background-color: transparent;
            }
        }

        /* Responsive design */
        @media (max-width: 768px) {
            .search-input {
                font-size: 0.9rem;
                padding: 0.6rem 0.8rem;
            }

            .search-results-info {
                display: none;
            }

            .search-history-container {
                max-height: 200px;
            }
        }

        @media (max-width: 480px) {
            .search-input-wrapper {
                flex-direction: column;
                gap: 0.75rem;
            }

            .search-input {
                width: 100%;
            }

            .search-clear-btn {
                width: 100%;
            }

            .search-history-item {
                flex-direction: column;
                align-items: flex-start;
            }

            .search-history-time {
                margin-top: 0.3rem;
            }
        }
    `;
    document.head.appendChild(style);
}

// Initialize search styles when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSearchStyles);
} else {
    initSearchStyles();
}

/**
 * Setup real-time search for an input element
 * @param {string} inputId - ID of search input element
 * @param {function} onSearch - Callback function when search is performed
 * @param {string} category - Category name for search history
 */
function setupRealTimeSearch(inputId, onSearch, category = 'search') {
    const input = document.getElementById(inputId);
    if (!input) return;

    // Create debounced search function
    const debouncedSearch = searchManager.debounce(() => {
        const query = input.value;
        if (query.trim()) {
            searchManager.addToHistory(query, category);
        }
        onSearch(query);
    }, searchManager.debounceDelay, inputId);

    // Setup input event listener
    input.addEventListener('input', (e) => {
        const query = e.target.value;
        
        // Show/hide clear button
        const clearBtn = input.nextElementSibling;
        if (clearBtn && clearBtn.classList.contains('search-clear-btn')) {
            if (query) {
                clearBtn.classList.add('visible');
            } else {
                clearBtn.classList.remove('visible');
            }
        }

        // Trigger debounced search
        debouncedSearch();
    });

    // Setup clear button if exists
    const nextElement = input.nextElementSibling;
    if (nextElement && nextElement.classList.contains('search-clear-btn')) {
        nextElement.addEventListener('click', () => {
            input.value = '';
            input.nextElementSibling.classList.remove('visible');
            input.focus();
            onSearch('');
        });
    }

    // Setup history suggestions on focus
    input.addEventListener('focus', () => {
        // Show history suggestions if input is empty
        if (!input.value) {
            showSearchSuggestions(inputId, category);
        }
    });

    input.addEventListener('blur', () => {
        // Hide suggestions after a short delay
        setTimeout(() => {
            const historyContainer = document.querySelector(`[data-history-for="${inputId}"]`);
            if (historyContainer) {
                historyContainer.classList.remove('visible');
            }
        }, 200);
    });
}

/**
 * Show search suggestions/history
 */
function showSearchSuggestions(inputId, category) {
    const input = document.getElementById(inputId);
    if (!input) return;

    let historyContainer = document.querySelector(`[data-history-for="${inputId}"]`);
    
    // Create container if doesn't exist
    if (!historyContainer) {
        historyContainer = document.createElement('div');
        historyContainer.className = 'search-history-container';
        historyContainer.setAttribute('data-history-for', inputId);
        input.parentElement.appendChild(historyContainer);
    }

    // Get history items for this category
    const allHistory = searchManager.getHistory();
    const categoryHistory = allHistory.filter(item => item.category === category);

    if (categoryHistory.length === 0) {
        historyContainer.innerHTML = '<div class="no-results">No search history</div>';
    } else {
        historyContainer.innerHTML = categoryHistory.map(item => `
            <div class="search-history-item" onclick="document.getElementById('${inputId}').value = '${item.query.replace(/'/g, "\\'")}'; document.getElementById('${inputId}').dispatchEvent(new Event('input'));">
                <div>
                    <span>${item.query}</span>
                    <span class="search-history-label">${item.category}</span>
                </div>
                <span class="search-history-time">${item.timestamp}</span>
            </div>
        `).join('');
    }

    historyContainer.classList.add('visible');
}
