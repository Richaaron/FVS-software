/**
 * Toast Notification System
 * Provides user feedback for success, error, warning, and info messages
 */

class Toast {
    constructor() {
        this.toastContainer = this.createContainer();
        this.toasts = [];
    }

    createContainer() {
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 10000;
                display: flex;
                flex-direction: column;
                gap: 10px;
                pointer-events: none;
            `;
            document.body.appendChild(container);
        }
        return container;
    }

    show(message, type = 'info', duration = 3000) {
        const toastId = `toast-${Date.now()}-${Math.random()}`;
        const toast = document.createElement('div');
        toast.id = toastId;
        toast.className = `toast toast-${type}`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', type === 'error' ? 'assertive' : 'polite');

        // Determine icon based on type
        let icon = 'ℹ️';
        switch (type) {
            case 'success': icon = '✓'; break;
            case 'error': icon = '✕'; break;
            case 'warning': icon = '⚠'; break;
        }

        toast.innerHTML = `
            <div class="toast-content">
                <span class="toast-icon">${icon}</span>
                <span class="toast-message">${this.escapeHtml(message)}</span>
                <button class="toast-close" aria-label="Close notification">×</button>
            </div>
        `;

        // Style toast
        toast.style.cssText = `
            display: flex;
            align-items: center;
            padding: 12px 16px;
            border-radius: 6px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            animation: slideInRight 0.3s ease-out;
            pointer-events: all;
            min-width: 300px;
            max-width: 400px;
            word-wrap: break-word;
            font-weight: 500;
        `;

        // Type-specific styling
        const colors = {
            'success': { bg: '#4caf50', text: 'white', border: '#45a049' },
            'error': { bg: '#f44336', text: 'white', border: '#da190b' },
            'warning': { bg: '#ff9800', text: 'white', border: '#e68900' },
            'info': { bg: '#2196F3', text: 'white', border: '#0b7dda' }
        };

        const color = colors[type] || colors['info'];
        toast.style.backgroundColor = color.bg;
        toast.style.color = color.text;
        toast.style.borderLeft = `4px solid ${color.border}`;

        // Add styles to content
        const content = toast.querySelector('.toast-content');
        content.style.cssText = `
            display: flex;
            align-items: center;
            gap: 10px;
            width: 100%;
            justify-content: space-between;
        `;

        const icon_el = toast.querySelector('.toast-icon');
        icon_el.style.cssText = `
            font-size: 18px;
            flex-shrink: 0;
        `;

        const message_el = toast.querySelector('.toast-message');
        message_el.style.cssText = `
            flex: 1;
            text-align: left;
        `;

        const close_btn = toast.querySelector('.toast-close');
        close_btn.style.cssText = `
            background: none;
            border: none;
            color: inherit;
            font-size: 24px;
            cursor: pointer;
            padding: 0;
            margin: 0 -8px 0 8px;
            flex-shrink: 0;
            opacity: 0.7;
            transition: opacity 0.2s;
        `;

        close_btn.addEventListener('mouseover', () => close_btn.style.opacity = '1');
        close_btn.addEventListener('mouseout', () => close_btn.style.opacity = '0.7');
        close_btn.addEventListener('click', () => this.removeToast(toastId));

        this.toastContainer.appendChild(toast);
        this.toasts.push({ id: toastId, element: toast, timer: null });

        // Auto-remove after duration
        if (duration > 0) {
            const timer = setTimeout(() => this.removeToast(toastId), duration);
            const toastObj = this.toasts.find(t => t.id === toastId);
            if (toastObj) toastObj.timer = timer;
        }

        return toastId;
    }

    removeToast(toastId) {
        const index = this.toasts.findIndex(t => t.id === toastId);
        if (index !== -1) {
            const toast = this.toasts[index];
            clearTimeout(toast.timer);

            // Fade out animation
            toast.element.style.animation = 'slideOutRight 0.3s ease-in forwards';

            setTimeout(() => {
                if (toast.element.parentElement) {
                    toast.element.remove();
                }
                this.toasts.splice(index, 1);
            }, 300);
        }
    }

    success(message, duration = 3000) {
        return this.show(message, 'success', duration);
    }

    error(message, duration = 5000) {
        return this.show(message, 'error', duration);
    }

    warning(message, duration = 4000) {
        return this.show(message, 'warning', duration);
    }

    info(message, duration = 3000) {
        return this.show(message, 'info', duration);
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    clearAll() {
        this.toasts.forEach(toast => {
            clearTimeout(toast.timer);
            if (toast.element.parentElement) {
                toast.element.remove();
            }
        });
        this.toasts = [];
    }
}

// Create global toast instance
const toast = new Toast();

// Add CSS animations to document if not already present
function initToastStyles() {
    if (!document.getElementById('toast-styles')) {
        const style = document.createElement('style');
        style.id = 'toast-styles';
        style.textContent = `
            @keyframes slideInRight {
                from {
                    opacity: 0;
                    transform: translateX(100px);
                }
                to {
                    opacity: 1;
                    transform: translateX(0);
                }
            }

            @keyframes slideOutRight {
                from {
                    opacity: 1;
                    transform: translateX(0);
                }
                to {
                    opacity: 0;
                    transform: translateX(100px);
                }
            }

            .toast {
                animation: slideInRight 0.3s ease-out !important;
            }
        `;
        document.head.appendChild(style);
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initToastStyles);
} else {
    initToastStyles();
}
