/**
 * Dark Mode Manager - Handles theme switching and persistence
 * Features: Theme toggle, persistent storage, smooth transitions, color management
 */

class DarkModeManager {
    constructor() {
        this.isDarkMode = this.loadPreference();
        this.cssVariables = {
            light: {
                '--bg-primary': '#ffffff',
                '--bg-secondary': '#f5f5f5',
                '--bg-tertiary': '#fafafa',
                '--text-primary': '#333333',
                '--text-secondary': '#666666',
                '--text-tertiary': '#999999',
                '--border-color': '#dddddd',
                '--border-light': '#eeeeee',
                '--shadow-light': 'rgba(0, 0, 0, 0.05)',
                '--shadow-medium': 'rgba(0, 0, 0, 0.1)',
                '--shadow-dark': 'rgba(0, 0, 0, 0.15)',
                '--input-bg': '#ffffff',
                '--input-border': '#dddddd',
                '--input-focus': '#4ecdc4',
                '--table-bg': '#ffffff',
                '--table-border': '#eeeeee',
                '--table-hover': '#f9f9f9',
                '--section-bg': 'linear-gradient(135deg, #f5f5f5 0%, #ffffff 100%)',
                '--modal-bg': '#ffffff',
                '--card-bg': '#ffffff',
                '--gradient-primary': 'linear-gradient(135deg, #4ecdc4 0%, #44b0a8 100%)',
                '--gradient-secondary': 'linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%)',
                '--gradient-tertiary': 'linear-gradient(135deg, #95e1d3 0%, #7dd4c3 100%)',
                '--scrollbar-track': '#f1f1f1',
                '--scrollbar-thumb': '#c1c1c1'
            },
            dark: {
                '--bg-primary': '#1a1a1a',
                '--bg-secondary': '#2d2d2d',
                '--bg-tertiary': '#3a3a3a',
                '--text-primary': '#e8e8e8',
                '--text-secondary': '#b8b8b8',
                '--text-tertiary': '#888888',
                '--border-color': '#404040',
                '--border-light': '#333333',
                '--shadow-light': 'rgba(0, 0, 0, 0.3)',
                '--shadow-medium': 'rgba(0, 0, 0, 0.5)',
                '--shadow-dark': 'rgba(0, 0, 0, 0.7)',
                '--input-bg': '#2d2d2d',
                '--input-border': '#404040',
                '--input-focus': '#4ecdc4',
                '--table-bg': '#2d2d2d',
                '--table-border': '#3a3a3a',
                '--table-hover': '#353535',
                '--section-bg': 'linear-gradient(135deg, #1f1f1f 0%, #2a2a2a 100%)',
                '--modal-bg': '#2d2d2d',
                '--card-bg': '#242424',
                '--gradient-primary': 'linear-gradient(135deg, #4ecdc4 0%, #44b0a8 100%)',
                '--gradient-secondary': 'linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%)',
                '--gradient-tertiary': 'linear-gradient(135deg, #95e1d3 0%, #7dd4c3 100%)',
                '--scrollbar-track': '#2d2d2d',
                '--scrollbar-thumb': '#555555'
            }
        };
    }

    /**
     * Load theme preference from localStorage
     */
    loadPreference() {
        const stored = localStorage.getItem('themePreference');
        if (stored) {
            return stored === 'dark';
        }

        // Check system preference
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            return true;
        }

        return false;
    }

    /**
     * Save theme preference to localStorage
     */
    savePreference() {
        localStorage.setItem('themePreference', this.isDarkMode ? 'dark' : 'light');
    }

    /**
     * Toggle dark mode
     */
    toggle() {
        this.isDarkMode = !this.isDarkMode;
        this.apply();
        this.savePreference();
        this.notifyChange();
    }

    /**
     * Apply theme to document
     */
    apply() {
        const root = document.documentElement;
        const theme = this.isDarkMode ? 'dark' : 'light';
        const variables = this.cssVariables[theme];

        Object.keys(variables).forEach(key => {
            root.style.setProperty(key, variables[key]);
        });

        document.documentElement.setAttribute('data-theme', theme);
        document.body.classList.toggle('dark-mode', this.isDarkMode);

        // Update theme color meta tag
        const metaThemeColor = document.querySelector('meta[name="theme-color"]');
        if (metaThemeColor) {
            metaThemeColor.setAttribute('content', this.isDarkMode ? '#1a1a1a' : '#ffffff');
        }
    }

    /**
     * Notify components of theme change
     */
    notifyChange() {
        window.dispatchEvent(new CustomEvent('themeChange', {
            detail: { isDarkMode: this.isDarkMode }
        }));
    }

    /**
     * Get current theme name
     */
    getThemeName() {
        return this.isDarkMode ? 'dark' : 'light';
    }

    /**
     * Get theme colors
     */
    getColors() {
        return this.cssVariables[this.isDarkMode ? 'dark' : 'light'];
    }

    /**
     * Check if dark mode is active
     */
    isDark() {
        return this.isDarkMode;
    }
}

// Global dark mode instance
const darkModeManager = new DarkModeManager();

/**
 * Initialize dark mode CSS variables
 */
function initDarkModeStyles() {
    const style = document.createElement('style');
    style.textContent = `
        :root {
            /* Light mode defaults */
            --bg-primary: #ffffff;
            --bg-secondary: #f5f5f5;
            --bg-tertiary: #fafafa;
            --text-primary: #333333;
            --text-secondary: #666666;
            --text-tertiary: #999999;
            --border-color: #dddddd;
            --border-light: #eeeeee;
            --shadow-light: rgba(0, 0, 0, 0.05);
            --shadow-medium: rgba(0, 0, 0, 0.1);
            --shadow-dark: rgba(0, 0, 0, 0.15);
            --input-bg: #ffffff;
            --input-border: #dddddd;
            --input-focus: #4ecdc4;
            --table-bg: #ffffff;
            --table-border: #eeeeee;
            --table-hover: #f9f9f9;
            --section-bg: linear-gradient(135deg, #f5f5f5 0%, #ffffff 100%);
            --modal-bg: #ffffff;
            --card-bg: #ffffff;
            --gradient-primary: linear-gradient(135deg, #4ecdc4 0%, #44b0a8 100%);
            --gradient-secondary: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
            --gradient-tertiary: linear-gradient(135deg, #95e1d3 0%, #7dd4c3 100%);
            --scrollbar-track: #f1f1f1;
            --scrollbar-thumb: #c1c1c1;
        }

        /* Dark mode variables */
        html[data-theme="dark"] {
            --bg-primary: #1a1a1a;
            --bg-secondary: #2d2d2d;
            --bg-tertiary: #3a3a3a;
            --text-primary: #e8e8e8;
            --text-secondary: #b8b8b8;
            --text-tertiary: #888888;
            --border-color: #404040;
            --border-light: #333333;
            --shadow-light: rgba(0, 0, 0, 0.3);
            --shadow-medium: rgba(0, 0, 0, 0.5);
            --shadow-dark: rgba(0, 0, 0, 0.7);
            --input-bg: #2d2d2d;
            --input-border: #404040;
            --input-focus: #4ecdc4;
            --table-bg: #2d2d2d;
            --table-border: #3a3a3a;
            --table-hover: #353535;
            --section-bg: linear-gradient(135deg, #1f1f1f 0%, #2a2a2a 100%);
            --modal-bg: #2d2d2d;
            --card-bg: #242424;
        }

        * {
            transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease;
        }

        html {
            background-color: var(--bg-primary);
            color: var(--text-primary);
        }

        body {
            background-color: var(--bg-primary);
            color: var(--text-primary);
        }

        /* Navigation & Header */
        nav {
            background: var(--bg-secondary) !important;
            border-bottom: 1px solid var(--border-color) !important;
        }

        /* Main sections */
        .section {
            background: var(--section-bg) !important;
            color: var(--text-primary);
        }

        /* Forms & Inputs */
        input[type="text"],
        input[type="email"],
        input[type="password"],
        input[type="number"],
        input[type="date"],
        input[type="file"],
        select,
        textarea {
            background-color: var(--input-bg) !important;
            border-color: var(--input-border) !important;
            color: var(--text-primary) !important;
        }

        input[type="text"]:focus,
        input[type="email"]:focus,
        input[type="password"]:focus,
        input[type="number"]:focus,
        input[type="date"]:focus,
        input[type="file"]:focus,
        select:focus,
        textarea:focus {
            border-color: var(--input-focus) !important;
            outline: none;
            box-shadow: 0 0 0 3px rgba(78, 205, 196, 0.1) !important;
        }

        /* Tables */
        table {
            background-color: var(--table-bg) !important;
            color: var(--text-primary);
        }

        table thead {
            background-color: var(--bg-secondary) !important;
            color: var(--text-primary);
        }

        table tbody tr {
            border-color: var(--table-border) !important;
        }

        table tbody tr:hover {
            background-color: var(--table-hover) !important;
        }

        table td, table th {
            border-color: var(--table-border) !important;
            color: var(--text-primary);
        }

        /* Cards & Containers */
        .card, .stat-card, .comparison-card {
            background-color: var(--card-bg) !important;
            color: var(--text-primary);
            border-color: var(--border-color) !important;
        }

        .stat-card {
            box-shadow: 0 2px 8px var(--shadow-light) !important;
        }

        .stat-card:hover {
            box-shadow: 0 4px 12px rgba(78, 205, 196, 0.2) !important;
        }

        /* Modals */
        .modal {
            background-color: rgba(0, 0, 0, 0.7) !important;
        }

        .modal-content {
            background-color: var(--modal-bg) !important;
            color: var(--text-primary);
        }

        /* Tabs */
        .tab {
            color: var(--text-secondary);
            border-color: transparent;
        }

        .tab.active {
            color: var(--text-primary);
            border-bottom-color: #4ecdc4;
        }

        /* Buttons */
        .btn {
            border-color: var(--border-color) !important;
            color: var(--text-primary) !important;
        }

        .btn-primary {
            background: var(--gradient-primary) !important;
            color: white !important;
        }

        .btn-secondary {
            background-color: var(--bg-secondary) !important;
            color: var(--text-primary) !important;
            border-color: var(--border-color) !important;
        }

        .btn-danger {
            background: #ef4444 !important;
            color: white !important;
        }

        .btn-info {
            background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%) !important;
            color: white !important;
        }

        /* Search inputs */
        .search-input {
            background-color: var(--input-bg) !important;
            border-color: var(--input-border) !important;
            color: var(--text-primary) !important;
        }

        .search-input:focus {
            border-color: var(--input-focus) !important;
            box-shadow: 0 0 0 3px rgba(78, 205, 196, 0.1) !important;
        }

        .search-clear-btn {
            background-color: var(--bg-secondary) !important;
            color: var(--text-primary) !important;
        }

        .search-clear-btn:hover {
            background-color: var(--bg-tertiary) !important;
        }

        /* Toast notifications */
        .toast {
            background-color: var(--card-bg) !important;
            color: var(--text-primary) !important;
            box-shadow: 0 4px 12px var(--shadow-medium) !important;
        }

        .toast.success {
            background-color: rgba(34, 197, 94, 0.9) !important;
            color: white !important;
        }

        .toast.error {
            background-color: rgba(239, 68, 68, 0.9) !important;
            color: white !important;
        }

        .toast.warning {
            background-color: rgba(245, 158, 11, 0.9) !important;
            color: white !important;
        }

        .toast.info {
            background-color: rgba(14, 165, 233, 0.9) !important;
            color: white !important;
        }

        /* Charts container */
        .chart-container {
            background-color: var(--card-bg) !important;
            box-shadow: 0 2px 8px var(--shadow-light) !important;
        }

        /* Empty state */
        .empty-state {
            background-color: var(--bg-secondary) !important;
            color: var(--text-secondary) !important;
        }

        /* Loading overlay */
        .loading-overlay {
            background-color: rgba(0, 0, 0, 0.6) !important;
        }

        .spinner {
            border-color: rgba(78, 205, 196, 0.2) !important;
            border-top-color: #4ecdc4 !important;
        }

        /* Scrollbar */
        ::-webkit-scrollbar {
            width: 10px;
            height: 10px;
        }

        ::-webkit-scrollbar-track {
            background: var(--scrollbar-track);
        }

        ::-webkit-scrollbar-thumb {
            background: var(--scrollbar-thumb);
            border-radius: 5px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: #888;
        }

        /* Dark mode toggle button */
        .theme-toggle-btn {
            background-color: var(--bg-secondary) !important;
            color: var(--text-primary) !important;
            border: 1px solid var(--border-color) !important;
            padding: 8px 12px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 1rem;
            display: flex;
            align-items: center;
            gap: 8px;
            transition: all 0.3s ease;
        }

        .theme-toggle-btn:hover {
            background-color: var(--bg-tertiary) !important;
            transform: scale(1.05);
        }

        .theme-toggle-btn:active {
            transform: scale(0.95);
        }

        /* Links */
        a {
            color: #4ecdc4;
        }

        a:visited {
            color: #44b0a8;
        }

        /* Placeholder text */
        input::placeholder,
        textarea::placeholder {
            color: var(--text-tertiary) !important;
        }

        /* Statistics report */
        .statistics-report {
            background-color: var(--bg-secondary) !important;
            color: var(--text-primary);
        }

        .distribution-section,
        .averages-section {
            background-color: var(--card-bg) !important;
            color: var(--text-primary);
        }

        .grade-bar {
            background-color: var(--bg-tertiary) !important;
        }

        .average-item {
            background-color: var(--bg-tertiary) !important;
            color: var(--text-primary);
        }

        .grade-distribution {
            color: var(--text-primary);
        }

        /* Advanced filters */
        .advanced-filters {
            background: linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(0, 200, 255, 0.05) 100%) !important;
            border-color: rgba(0, 212, 255, 0.3) !important;
        }

        .advanced-filters h4 {
            color: var(--text-primary) !important;
        }

        .advanced-filters label {
            color: var(--text-secondary) !important;
        }

        /* Form groups */
        .form-row {
            color: var(--text-primary);
        }

        .form-group label {
            color: var(--text-primary);
        }

        /* Horizontal rule */
        hr {
            border-color: var(--border-color) !important;
        }

        /* Badges */
        .grade-badge {
            color: white !important;
        }

        /* Smooth transitions */
        * {
            transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease;
        }

        @media (max-width: 768px) {
            .theme-toggle-btn {
                font-size: 0.9rem;
                padding: 6px 10px;
            }
        }
    `;
    document.head.appendChild(style);
}

// Initialize dark mode styles and apply preference
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        initDarkModeStyles();
        darkModeManager.apply();
    });
} else {
    initDarkModeStyles();
    darkModeManager.apply();
}

/**
 * Update chart colors based on theme
 */
function updateChartColorsForTheme() {
    window.addEventListener('themeChange', () => {
        // If you have charts on page, update their colors
        if (window.chartsManager && window.chartsManager.charts) {
            Object.keys(window.chartsManager.charts).forEach(key => {
                if (window.chartsManager.charts[key]) {
                    window.chartsManager.charts[key].destroy();
                }
            });
            window.chartsManager.charts = {};
        }

        // Reload analytics if on that tab
        const advAnalyticsTab = document.getElementById('advancedAnalytics');
        if (advAnalyticsTab && advAnalyticsTab.style.display !== 'none') {
            if (window.loadAdvancedAnalytics) {
                window.loadAdvancedAnalytics();
            }
        }
    });
}

// Initialize chart color updates
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', updateChartColorsForTheme);
} else {
    updateChartColorsForTheme();
}
