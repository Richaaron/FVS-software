/**
 * Loading State Management
 * Provides utilities for showing/hiding loading indicators and spinners
 */

class LoadingManager {
    constructor() {
        this.activeLoaders = new Set();
        this.initializeStyles();
    }

    initializeStyles() {
        if (!document.getElementById('loading-styles')) {
            const style = document.createElement('style');
            style.id = 'loading-styles';
            style.textContent = `
                /* Spinner animations */
                @keyframes spin {
                    0% {
                        transform: rotate(0deg);
                    }
                    100% {
                        transform: rotate(360deg);
                    }
                }

                @keyframes pulse-grow {
                    0%, 100% {
                        transform: scale(1);
                        opacity: 1;
                    }
                    50% {
                        transform: scale(1.1);
                        opacity: 0.8;
                    }
                }

                @keyframes skeleton-loading {
                    0% {
                        background-position: -1000px 0;
                    }
                    100% {
                        background-position: 1000px 0;
                    }
                }

                /* Loading spinner */
                .loading-spinner {
                    width: 40px;
                    height: 40px;
                    border: 4px solid rgba(255, 255, 255, 0.3);
                    border-top: 4px solid white;
                    border-radius: 50%;
                    animation: spin 1s linear infinite;
                }

                .loading-spinner.small {
                    width: 24px;
                    height: 24px;
                    border: 3px solid rgba(255, 255, 255, 0.3);
                    border-top: 3px solid white;
                }

                .loading-spinner.large {
                    width: 60px;
                    height: 60px;
                    border: 5px solid rgba(255, 255, 255, 0.3);
                    border-top: 5px solid white;
                }

                /* Loading overlay */
                .loading-overlay {
                    position: fixed;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: rgba(10, 25, 41, 0.8);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    z-index: 9999;
                    backdrop-filter: blur(4px);
                }

                .loading-overlay.hidden {
                    display: none;
                }

                .loading-content {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    gap: 16px;
                    color: white;
                }

                .loading-text {
                    font-size: 16px;
                    font-weight: 500;
                    color: white;
                    margin-top: 8px;
                }

                /* Skeleton loaders */
                .skeleton {
                    background: linear-gradient(
                        90deg,
                        rgba(255, 255, 255, 0.1) 25%,
                        rgba(255, 255, 255, 0.2) 50%,
                        rgba(255, 255, 255, 0.1) 75%
                    );
                    background-size: 1000px 100%;
                    animation: skeleton-loading 1.5s infinite;
                    border-radius: 6px;
                }

                .skeleton-row {
                    display: flex;
                    gap: 12px;
                    margin-bottom: 12px;
                }

                .skeleton-cell {
                    flex: 1;
                    height: 16px;
                    background: linear-gradient(
                        90deg,
                        rgba(255, 255, 255, 0.1) 25%,
                        rgba(255, 255, 255, 0.2) 50%,
                        rgba(255, 255, 255, 0.1) 75%
                    );
                    background-size: 1000px 100%;
                    animation: skeleton-loading 1.5s infinite;
                    border-radius: 4px;
                }

                /* Loading button state */
                .btn-loading {
                    position: relative;
                    pointer-events: none;
                    opacity: 0.7;
                }

                .btn-loading::after {
                    content: '';
                    position: absolute;
                    right: 12px;
                    top: 50%;
                    transform: translateY(-50%);
                    width: 16px;
                    height: 16px;
                    border: 2px solid rgba(255, 255, 255, 0.3);
                    border-top: 2px solid white;
                    border-radius: 50%;
                    animation: spin 0.8s linear infinite;
                }

                /* Loading backdrop */
                .loading-backdrop {
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: rgba(0, 0, 0, 0.3);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    z-index: 100;
                    border-radius: inherit;
                }

                /* Small inline loader */
                .inline-loader {
                    display: inline-flex;
                    align-items: center;
                    gap: 8px;
                }

                .inline-loader .loading-spinner {
                    width: 20px;
                    height: 20px;
                    border: 2px solid rgba(255, 255, 255, 0.3);
                    border-top: 2px solid white;
                }

                /* Table row skeleton */
                .skeleton-table-row {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
                    gap: 12px;
                    padding: 12px;
                    background: rgba(255, 255, 255, 0.05);
                    border-radius: 6px;
                    margin-bottom: 8px;
                }

                .skeleton-table-row .skeleton-cell {
                    height: 20px;
                }

                /* Fade in for loaded content */
                @keyframes fadeInContent {
                    from {
                        opacity: 0;
                    }
                    to {
                        opacity: 1;
                    }
                }

                .fade-in-content {
                    animation: fadeInContent 0.3s ease-in;
                }
            `;
            document.head.appendChild(style);
        }
    }

    /**
     * Show global loading overlay with spinner
     * @param {string} message - Loading message to display
     * @param {boolean} cancelable - Whether to show cancel button
     * @returns {string} Loader ID
     */
    showOverlay(message = 'Loading...', cancelable = false) {
        const loaderId = `loader-${Date.now()}-${Math.random()}`;

        let overlay = document.getElementById('global-loading-overlay');
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.id = 'global-loading-overlay';
            overlay.className = 'loading-overlay hidden';
            document.body.appendChild(overlay);
        }

        overlay.innerHTML = `
            <div class="loading-content">
                <div class="loading-spinner"></div>
                <div class="loading-text">${this.escapeHtml(message)}</div>
                ${cancelable ? '<button class="btn btn-sm" onclick="loadingManager.hideOverlay()">Cancel</button>' : ''}
            </div>
        `;

        overlay.classList.remove('hidden');
        this.activeLoaders.add(loaderId);

        return loaderId;
    }

    /**
     * Hide global loading overlay
     */
    hideOverlay() {
        const overlay = document.getElementById('global-loading-overlay');
        if (overlay) {
            overlay.classList.add('hidden');
        }
        this.activeLoaders.clear();
    }

    /**
     * Show loading state on a specific element
     * @param {HTMLElement} element - Element to show loading in
     * @param {string} type - 'spinner' or 'skeleton'
     * @returns {string} Loader ID
     */
    showInElement(element, type = 'spinner') {
        if (!element) return null;

        const loaderId = `loader-${Date.now()}-${Math.random()}`;
        const originalContent = element.innerHTML;

        element.dataset.loaderId = loaderId;
        element.dataset.originalContent = originalContent;

        if (type === 'skeleton') {
            element.innerHTML = `
                <div class="skeleton-table-row">
                    <div class="skeleton-cell"></div>
                    <div class="skeleton-cell"></div>
                    <div class="skeleton-cell"></div>
                </div>
                <div class="skeleton-table-row">
                    <div class="skeleton-cell"></div>
                    <div class="skeleton-cell"></div>
                    <div class="skeleton-cell"></div>
                </div>
                <div class="skeleton-table-row">
                    <div class="skeleton-cell"></div>
                    <div class="skeleton-cell"></div>
                    <div class="skeleton-cell"></div>
                </div>
            `;
        } else {
            element.innerHTML = `
                <div class="loading-backdrop">
                    <div class="inline-loader">
                        <div class="loading-spinner small"></div>
                        <span>Loading...</span>
                    </div>
                </div>
            `;
        }

        this.activeLoaders.add(loaderId);
        return loaderId;
    }

    /**
     * Hide loading state on element
     * @param {HTMLElement} element - Element to restore
     */
    hideInElement(element) {
        if (!element) return;

        const loaderId = element.dataset.loaderId;
        const originalContent = element.dataset.originalContent;

        if (originalContent) {
            element.innerHTML = originalContent;
            element.classList.add('fade-in-content');
            setTimeout(() => element.classList.remove('fade-in-content'), 300);
        }

        if (loaderId) {
            this.activeLoaders.delete(loaderId);
            delete element.dataset.loaderId;
            delete element.dataset.originalContent;
        }
    }

    /**
     * Add loading state to button
     * @param {HTMLElement} button - Button element
     * @param {string} originalText - Original button text
     * @returns {string} Loader ID
     */
    showButton(button, originalText = 'Loading...') {
        const loaderId = `loader-${Date.now()}-${Math.random()}`;

        button.dataset.originalText = button.textContent;
        button.disabled = true;
        button.classList.add('btn-loading');
        button.textContent = originalText;

        this.activeLoaders.add(loaderId);
        return loaderId;
    }

    /**
     * Remove loading state from button
     * @param {HTMLElement} button - Button element
     */
    hideButton(button) {
        const originalText = button.dataset.originalText || 'Submit';
        button.textContent = originalText;
        button.disabled = false;
        button.classList.remove('btn-loading');

        delete button.dataset.originalText;
    }

    /**
     * Utility: Escape HTML string
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Check if any loaders are active
     * @returns {boolean}
     */
    isLoading() {
        return this.activeLoaders.size > 0;
    }

    /**
     * Clear all loaders
     */
    clearAll() {
        this.hideOverlay();
        this.activeLoaders.clear();
    }
}

// Create global loading manager instance
const loadingManager = new LoadingManager();
