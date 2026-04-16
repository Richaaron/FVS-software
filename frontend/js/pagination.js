/**
 * Pagination Manager - Handles client-side pagination for large datasets
 * Features: Page navigation, item limit configuration, state management
 */

class PaginationManager {
    constructor(options = {}) {
        this.currentPage = 1;
        this.itemsPerPage = options.itemsPerPage || 10;
        this.totalItems = 0;
        this.totalPages = 0;
        this.data = [];
        this.maxPageButtons = 5;
    }

    /**
     * Set the data and calculate pagination
     */
    setData(data, itemsPerPage = null) {
        if (itemsPerPage) {
            this.itemsPerPage = itemsPerPage;
        }
        this.data = data || [];
        this.totalItems = this.data.length;
        this.totalPages = Math.ceil(this.totalItems / this.itemsPerPage);
        
        // Reset to page 1 if current page exceeds total pages
        if (this.currentPage > this.totalPages && this.totalPages > 0) {
            this.currentPage = 1;
        }
    }

    /**
     * Get data for current page
     */
    getCurrentPageData() {
        if (!this.data || this.data.length === 0) {
            return [];
        }
        const start = (this.currentPage - 1) * this.itemsPerPage;
        const end = start + this.itemsPerPage;
        return this.data.slice(start, end);
    }

    /**
     * Go to specific page
     */
    goToPage(pageNumber) {
        const page = Math.max(1, Math.min(pageNumber, this.totalPages));
        if (page !== this.currentPage) {
            this.currentPage = page;
            return true;
        }
        return false;
    }

    /**
     * Go to next page
     */
    nextPage() {
        if (this.currentPage < this.totalPages) {
            this.currentPage++;
            return true;
        }
        return false;
    }

    /**
     * Go to previous page
     */
    prevPage() {
        if (this.currentPage > 1) {
            this.currentPage--;
            return true;
        }
        return false;
    }

    /**
     * Get pagination info
     */
    getInfo() {
        return {
            currentPage: this.currentPage,
            totalPages: this.totalPages,
            totalItems: this.totalItems,
            itemsPerPage: this.itemsPerPage,
            hasNextPage: this.currentPage < this.totalPages,
            hasPrevPage: this.currentPage > 1,
            startIndex: (this.currentPage - 1) * this.itemsPerPage + 1,
            endIndex: Math.min(this.currentPage * this.itemsPerPage, this.totalItems)
        };
    }

    /**
     * Get array of page numbers to display
     */
    getPageNumbers() {
        const pages = [];
        const info = this.getInfo();
        const half = Math.floor(this.maxPageButtons / 2);
        
        let startPage = Math.max(1, info.currentPage - half);
        let endPage = Math.min(info.totalPages, startPage + this.maxPageButtons - 1);
        
        // Adjust start if we're near the end
        if (endPage - startPage < this.maxPageButtons - 1) {
            startPage = Math.max(1, endPage - this.maxPageButtons + 1);
        }
        
        for (let i = startPage; i <= endPage; i++) {
            pages.push(i);
        }
        
        return pages;
    }

    /**
     * Render pagination controls HTML
     */
    render(containerId, onPageChange = null) {
        const container = document.getElementById(containerId);
        if (!container || this.totalPages <= 1) {
            return;
        }

        const info = this.getInfo();
        const pageNumbers = this.getPageNumbers();
        
        let html = `
            <div class="pagination-container">
                <div class="pagination-info">
                    <span>Showing ${info.startIndex} to ${info.endIndex} of ${info.totalItems} items</span>
                </div>
                
                <div class="pagination-controls">
                    <button 
                        class="pagination-btn ${!info.hasPrevPage ? 'disabled' : ''}" 
                        onclick="${onPageChange ? `${onPageChange}(${this.currentPage - 1})` : 'paginationManager.handlePageChange(this.previousPage())'}"
                        ${!info.hasPrevPage ? 'disabled' : ''}>
                        ← Previous
                    </button>
                    
                    <div class="pagination-pages">
        `;
        
        // First page button
        if (pageNumbers[0] > 1) {
            html += `<button class="pagination-page" onclick="paginationManager.goToPage(1); paginationManager.render('${containerId}');">1</button>`;
            if (pageNumbers[0] > 2) {
                html += `<span class="pagination-ellipsis">...</span>`;
            }
        }
        
        // Page number buttons
        pageNumbers.forEach(pageNum => {
            html += `<button 
                class="pagination-page ${pageNum === this.currentPage ? 'active' : ''}" 
                onclick="paginationManager.goToPage(${pageNum}); paginationManager.render('${containerId}');"
                ${pageNum === this.currentPage ? 'disabled' : ''}>
                ${pageNum}
            </button>`;
        });
        
        // Last page button
        if (pageNumbers[pageNumbers.length - 1] < this.totalPages) {
            if (pageNumbers[pageNumbers.length - 1] < this.totalPages - 1) {
                html += `<span class="pagination-ellipsis">...</span>`;
            }
            html += `<button class="pagination-page" onclick="paginationManager.goToPage(${this.totalPages}); paginationManager.render('${containerId}');">${this.totalPages}</button>`;
        }
        
        html += `
                    </div>
                    
                    <button 
                        class="pagination-btn ${!info.hasNextPage ? 'disabled' : ''}" 
                        onclick="paginationManager.nextPage(); paginationManager.render('${containerId}');"
                        ${!info.hasNextPage ? 'disabled' : ''}>
                        Next →
                    </button>
                </div>
                
                <div class="pagination-size">
                    <label for="itemsPerPage">Items per page:</label>
                    <select id="itemsPerPage" onchange="paginationManager.changeItemsPerPage(this.value); paginationManager.render('${containerId}');">
                        <option value="5" ${this.itemsPerPage === 5 ? 'selected' : ''}>5</option>
                        <option value="10" ${this.itemsPerPage === 10 ? 'selected' : ''}>10</option>
                        <option value="25" ${this.itemsPerPage === 25 ? 'selected' : ''}>25</option>
                        <option value="50" ${this.itemsPerPage === 50 ? 'selected' : ''}>50</option>
                        <option value="100" ${this.itemsPerPage === 100 ? 'selected' : ''}>100</option>
                    </select>
                </div>
            </div>
        `;
        
        container.innerHTML = html;
    }

    /**
     * Change items per page
     */
    changeItemsPerPage(newValue) {
        this.itemsPerPage = parseInt(newValue);
        this.totalPages = Math.ceil(this.totalItems / this.itemsPerPage);
        this.currentPage = 1;
    }

    /**
     * Handle page change event
     */
    handlePageChange(success) {
        if (success) {
            window.dispatchEvent(new CustomEvent('paginationChanged', {
                detail: { page: this.currentPage, data: this.getCurrentPageData() }
            }));
        }
    }
}

// Global pagination manager instance
const paginationManager = new PaginationManager({ itemsPerPage: 10 });

/**
 * Add CSS styles for pagination
 */
function initPaginationStyles() {
    const style = document.createElement('style');
    style.textContent = `
        .pagination-container {
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 1.5rem;
            padding: 1.5rem;
            background: linear-gradient(135deg, rgba(78, 205, 196, 0.05) 0%, rgba(102, 126, 234, 0.05) 100%);
            border-radius: 12px;
            margin-top: 1.5rem;
            border: 1px solid rgba(78, 205, 196, 0.2);
        }

        .pagination-info {
            font-size: 0.95rem;
            color: #666;
            font-weight: 500;
        }

        .pagination-controls {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            flex-wrap: wrap;
        }

        .pagination-btn {
            padding: 0.6rem 1.2rem;
            background: linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%);
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
            font-size: 0.9rem;
            transition: all 0.3s ease;
            box-shadow: 0 2px 8px rgba(78, 205, 196, 0.3);
        }

        .pagination-btn:hover:not(.disabled) {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(78, 205, 196, 0.5);
        }

        .pagination-btn.disabled {
            background: #ccc;
            cursor: not-allowed;
            opacity: 0.5;
        }

        .pagination-pages {
            display: flex;
            gap: 0.5rem;
            flex-wrap: wrap;
            align-items: center;
        }

        .pagination-page {
            min-width: 36px;
            height: 36px;
            padding: 0.4rem 0.8rem;
            background: white;
            border: 1px solid #ddd;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 500;
            color: #333;
            transition: all 0.3s ease;
        }

        .pagination-page:hover:not(.active):not(:disabled) {
            background: #f5f5f5;
            border-color: #4ecdc4;
            color: #4ecdc4;
        }

        .pagination-page.active {
            background: linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%);
            color: white;
            border-color: #4ecdc4;
            box-shadow: 0 2px 8px rgba(78, 205, 196, 0.4);
        }

        .pagination-page:disabled {
            cursor: default;
        }

        .pagination-ellipsis {
            color: #999;
            padding: 0 0.4rem;
            font-weight: 600;
        }

        .pagination-size {
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }

        .pagination-size label {
            font-size: 0.9rem;
            color: #666;
            font-weight: 500;
        }

        .pagination-size select {
            padding: 0.6rem 0.8rem;
            border: 1px solid #ddd;
            border-radius: 6px;
            background: white;
            color: #333;
            cursor: pointer;
            font-size: 0.9rem;
            transition: all 0.3s ease;
        }

        .pagination-size select:hover,
        .pagination-size select:focus {
            border-color: #4ecdc4;
            outline: none;
            box-shadow: 0 0 0 3px rgba(78, 205, 196, 0.1);
        }

        /* Responsive design */
        @media (max-width: 768px) {
            .pagination-container {
                gap: 1rem;
                padding: 1rem;
            }

            .pagination-controls {
                gap: 0.5rem;
            }

            .pagination-page {
                min-width: 32px;
                height: 32px;
                font-size: 0.85rem;
                padding: 0.3rem 0.6rem;
            }

            .pagination-btn {
                padding: 0.5rem 0.8rem;
                font-size: 0.8rem;
            }

            .pagination-info {
                font-size: 0.85rem;
                width: 100%;
                text-align: center;
                order: -1;
            }
        }

        @media (max-width: 480px) {
            .pagination-container {
                flex-direction: column;
                gap: 0.75rem;
            }

            .pagination-pages {
                justify-content: center;
            }

            .pagination-controls {
                justify-content: center;
                width: 100%;
            }

            .pagination-size {
                width: 100%;
                justify-content: center;
            }
        }
    `;
    document.head.appendChild(style);
}

// Initialize pagination styles when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initPaginationStyles);
} else {
    initPaginationStyles();
}
