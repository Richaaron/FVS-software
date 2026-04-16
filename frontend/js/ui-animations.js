/**
 * UI Animations Manager - Enhanced animations for forms, tables, modals, and transitions
 * Integrates with AnimationManager for comprehensive animation support
 */

class UIAnimationsManager {
    constructor() {
        this.animatedElements = new Set();
        this.isAnimating = new Map();
        this.observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };
    }

    /**
     * Initialize intersection observer for scroll animations
     */
    initScrollAnimations() {
        if (!window.IntersectionObserver) return;

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting && !this.animatedElements.has(entry.target)) {
                    this.animatedElements.add(entry.target);
                    this.applyScrollAnimation(entry.target);
                }
            });
        }, this.observerOptions);

        // Observe all cards and stat elements
        document.querySelectorAll('.stat-card, .card, .comparison-card, .chart-container').forEach(el => {
            observer.observe(el);
        });

        // Observe table rows
        document.querySelectorAll('table tbody tr').forEach(el => {
            observer.observe(el);
        });
    }

    /**
     * Apply animation to element when it comes into view
     */
    applyScrollAnimation(element) {
        const classList = element.className;
        
        if (classList.includes('stat-card') || classList.includes('card')) {
            // Cards: scale in with slight bounce
            element.style.opacity = '0';
            element.style.transform = 'scale(0.8) translateY(20px)';
            element.style.transition = 'all 0.6s cubic-bezier(0.34, 1.56, 0.64, 1)';
            
            setTimeout(() => {
                element.style.opacity = '1';
                element.style.transform = 'scale(1) translateY(0)';
            }, 50);
        } else if (classList.includes('chart-container')) {
            // Charts: fade in from below
            element.style.opacity = '0';
            element.style.transform = 'translateY(30px)';
            element.style.transition = 'all 0.8s ease-out';
            
            setTimeout(() => {
                element.style.opacity = '1';
                element.style.transform = 'translateY(0)';
            }, 50);
        } else if (element.tagName === 'TR') {
            // Table rows: slide in from left with staggered delay
            element.style.opacity = '0';
            element.style.transform = 'translateX(-30px)';
            element.style.transition = 'all 0.5s ease-out';
            
            const delay = Array.from(element.parentElement.children).indexOf(element) * 50;
            setTimeout(() => {
                element.style.opacity = '1';
                element.style.transform = 'translateX(0)';
            }, delay);
        }
    }

    /**
     * Animate form submission
     */
    animateFormSubmit(formElement) {
        if (this.isAnimating.get(formElement)) return;

        this.isAnimating.set(formElement, true);

        // Find submit button and animate it
        const submitBtn = formElement.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.style.transition = 'all 0.3s ease';
            submitBtn.style.opacity = '0.7';
            submitBtn.style.transform = 'scale(0.95)';

            setTimeout(() => {
                submitBtn.style.opacity = '1';
                submitBtn.style.transform = 'scale(1)';
            }, 150);
        }

        // Animate form elements
        formElement.querySelectorAll('input, select, textarea').forEach((el, index) => {
            el.style.transition = 'all 0.3s ease';
            el.style.opacity = '0.7';
            
            setTimeout(() => {
                el.style.opacity = '1';
            }, index * 50);
        });

        setTimeout(() => {
            this.isAnimating.set(formElement, false);
        }, 500);
    }

    /**
     * Animate modal opening
     */
    animateModalOpen(modalElement) {
        modalElement.style.display = 'flex';
        modalElement.style.opacity = '0';
        modalElement.style.transition = 'opacity 0.3s ease';

        // Animate backdrop
        setTimeout(() => {
            modalElement.style.opacity = '1';
        }, 10);

        // Animate modal content
        const modalContent = modalElement.querySelector('.modal-content');
        if (modalContent) {
            modalContent.style.transform = 'scale(0.9) translateY(-30px)';
            modalContent.style.opacity = '0';
            modalContent.style.transition = 'all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1)';

            setTimeout(() => {
                modalContent.style.transform = 'scale(1) translateY(0)';
                modalContent.style.opacity = '1';
            }, 100);
        }
    }

    /**
     * Animate modal closing
     */
    animateModalClose(modalElement) {
        const modalContent = modalElement.querySelector('.modal-content');
        if (modalContent) {
            modalContent.style.transition = 'all 0.3s ease';
            modalContent.style.transform = 'scale(0.9) translateY(-30px)';
            modalContent.style.opacity = '0';
        }

        modalElement.style.transition = 'opacity 0.3s ease';
        modalElement.style.opacity = '0';

        setTimeout(() => {
            modalElement.style.display = 'none';
            // Reset styles
            if (modalContent) {
                modalContent.style.transform = 'scale(0.9) translateY(-30px)';
                modalContent.style.opacity = '0';
            }
        }, 300);
    }

    /**
     * Animate button click (ripple effect)
     */
    animateButtonClick(button) {
        const ripple = document.createElement('span');
        ripple.style.position = 'absolute';
        ripple.style.borderRadius = '50%';
        ripple.style.backgroundColor = 'rgba(255, 255, 255, 0.5)';
        ripple.style.pointerEvents = 'none';

        const rect = button.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = event.clientX - rect.left - size / 2;
        const y = event.clientY - rect.top - size / 2;

        ripple.style.width = ripple.style.height = size + 'px';
        ripple.style.left = x + 'px';
        ripple.style.top = y + 'px';

        button.style.position = 'relative';
        button.style.overflow = 'hidden';
        button.appendChild(ripple);

        ripple.style.animation = 'ripple-animation 0.6s ease-out';
        setTimeout(() => ripple.remove(), 600);
    }

    /**
     * Animate table row addition
     */
    animateNewTableRow(rowElement) {
        rowElement.style.opacity = '0';
        rowElement.style.transform = 'translateX(-40px)';
        rowElement.style.transition = 'all 0.5s ease-out';

        setTimeout(() => {
            rowElement.style.opacity = '1';
            rowElement.style.transform = 'translateX(0)';
        }, 10);

        // Add highlight animation
        setTimeout(() => {
            rowElement.style.backgroundColor = 'rgba(78, 205, 196, 0.1)';
            rowElement.style.transition = 'background-color 1s ease-out';
        }, 100);

        setTimeout(() => {
            rowElement.style.backgroundColor = '';
        }, 1100);
    }

    /**
     * Animate table row deletion
     */
    animateRowDelete(rowElement, callback) {
        rowElement.style.transition = 'all 0.3s ease';
        rowElement.style.opacity = '0';
        rowElement.style.transform = 'translateX(40px)';

        setTimeout(() => {
            rowElement.remove();
            if (callback) callback();
        }, 300);
    }

    /**
     * Animate section transitions
     */
    animateSectionChange(oldSection, newSection) {
        if (oldSection) {
            oldSection.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
            oldSection.style.opacity = '0';
            oldSection.style.transform = 'translateY(20px)';
        }

        newSection.style.display = 'block';
        newSection.style.opacity = '0';
        newSection.style.transform = 'translateY(20px)';
        newSection.style.transition = 'opacity 0.4s ease, transform 0.4s ease';

        setTimeout(() => {
            newSection.style.opacity = '1';
            newSection.style.transform = 'translateY(0)';
        }, 10);

        if (oldSection) {
            setTimeout(() => {
                oldSection.style.display = 'none';
            }, 300);
        }
    }

    /**
     * Animate element highlight (flash)
     */
    animateHighlight(element) {
        element.style.transition = 'background-color 0.5s ease';
        element.style.backgroundColor = 'rgba(78, 205, 196, 0.3)';

        setTimeout(() => {
            element.style.backgroundColor = '';
        }, 500);
    }

    /**
     * Animate loading state
     */
    animateLoadingStart(button) {
        button.style.transition = 'all 0.3s ease';
        button.disabled = true;
        button.style.opacity = '0.6';
        
        // Change text if provided
        const originalText = button.textContent;
        button.textContent = button.getAttribute('data-loading-text') || 'Loading...';
        button.setAttribute('data-original-text', originalText);
    }

    /**
     * Animate loading state completion
     */
    animateLoadingEnd(button) {
        button.style.transition = 'all 0.3s ease';
        button.disabled = false;
        button.style.opacity = '1';

        const originalText = button.getAttribute('data-original-text') || button.textContent;
        button.textContent = originalText;
    }

    /**
     * Animate success feedback (checkmark animation)
     */
    animateSuccess(element) {
        element.style.transition = 'all 0.3s ease';
        element.style.transform = 'scale(1.05)';
        element.style.backgroundColor = 'rgba(34, 197, 94, 0.1)';

        setTimeout(() => {
            element.style.transform = 'scale(1)';
        }, 200);

        setTimeout(() => {
            element.style.backgroundColor = '';
        }, 1000);
    }

    /**
     * Animate error shake
     */
    animateError(element) {
        element.style.animation = 'shake-animation 0.5s ease-in-out';

        setTimeout(() => {
            element.style.animation = '';
        }, 500);
    }

    /**
     * Animate counter/number updates
     */
    animateNumberUpdate(element, oldValue, newValue) {
        element.style.transition = 'all 0.3s ease';
        element.style.transform = 'scale(1.1)';
        element.style.color = '#4ecdc4';

        setTimeout(() => {
            element.textContent = newValue;
            element.style.transform = 'scale(1)';
            element.style.color = '';
        }, 150);
    }

    /**
     * Setup form animations globally
     */
    setupFormAnimations() {
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', (e) => {
                this.animateFormSubmit(form);
            });
        });
    }

    /**
     * Setup button click animations globally
     */
    setupButtonAnimations() {
        document.querySelectorAll('button').forEach(btn => {
            btn.addEventListener('click', (e) => {
                if (e.offsetX && e.offsetY) {
                    this.animateButtonClick(btn);
                }
            });
        });
    }

    /**
     * Setup modal animations globally
     */
    setupModalAnimations() {
        document.addEventListener('click', (e) => {
            // Handle modal open
            if (e.target.classList.contains('modal-open')) {
                const modalId = e.target.getAttribute('data-modal');
                const modal = document.getElementById(modalId);
                if (modal) {
                    this.animateModalOpen(modal);
                }
            }

            // Handle modal close
            if (e.target.classList.contains('modal-close') || e.target.classList.contains('modal-overlay')) {
                const modal = e.target.closest('.modal');
                if (modal) {
                    this.animateModalClose(modal);
                }
            }
        });
    }

    /**
     * Setup section/tab animations globally
     */
    setupSectionAnimations() {
        document.querySelectorAll('[data-section]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const sectionId = btn.getAttribute('data-section');
                const newSection = document.getElementById(sectionId);
                
                if (newSection) {
                    const oldSection = document.querySelector('.section.active');
                    if (oldSection) {
                        oldSection.classList.remove('active');
                    }
                    newSection.classList.add('active');
                    this.animateSectionChange(oldSection, newSection);
                }
            });
        });
    }

    /**
     * Initialize all animations
     */
    initialize() {
        // Inject ripple animation keyframe
        if (!document.getElementById('ui-animations-styles')) {
            const style = document.createElement('style');
            style.id = 'ui-animations-styles';
            style.textContent = `
                @keyframes ripple-animation {
                    0% {
                        transform: scale(0);
                        opacity: 1;
                    }
                    100% {
                        transform: scale(4);
                        opacity: 0;
                    }
                }

                @keyframes shake-animation {
                    0%, 100% { transform: translateX(0); }
                    10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
                    20%, 40%, 60%, 80% { transform: translateX(5px); }
                }

                @keyframes slideInDown {
                    from {
                        opacity: 0;
                        transform: translateY(-30px);
                    }
                    to {
                        opacity: 1;
                        transform: translateY(0);
                    }
                }

                @keyframes slideInUp {
                    from {
                        opacity: 0;
                        transform: translateY(30px);
                    }
                    to {
                        opacity: 1;
                        transform: translateY(0);
                    }
                }

                @keyframes fadeInScale {
                    from {
                        opacity: 0;
                        transform: scale(0.95);
                    }
                    to {
                        opacity: 1;
                        transform: scale(1);
                    }
                }

                /* Apply animations to common elements */
                .stat-card {
                    animation: fadeInScale 0.6s ease-out backwards;
                }

                .card {
                    animation: fadeInScale 0.6s ease-out backwards;
                }

                .modal {
                    animation: fadeIn 0.3s ease;
                }

                .modal-content {
                    animation: slideInDown 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
                }

                table tbody tr {
                    animation: slideInUp 0.5s ease-out backwards;
                }

                table tbody tr:nth-child(1) { animation-delay: 0ms; }
                table tbody tr:nth-child(2) { animation-delay: 50ms; }
                table tbody tr:nth-child(3) { animation-delay: 100ms; }
                table tbody tr:nth-child(4) { animation-delay: 150ms; }
                table tbody tr:nth-child(5) { animation-delay: 200ms; }
                table tbody tr:nth-child(n+6) { animation-delay: 250ms; }

                .section {
                    animation: fadeInScale 0.4s ease-out backwards;
                }

                .alert {
                    animation: slideInDown 0.4s ease-out;
                }

                .toast {
                    animation: slideInRight 0.3s ease-out;
                }

                .loading-overlay {
                    animation: fadeIn 0.3s ease-out;
                }

                button {
                    position: relative;
                    transition: all 0.3s ease;
                }

                button:active {
                    transform: scale(0.98);
                }
            `;
            document.head.appendChild(style);
        }

        // Initialize all animation systems
        this.initScrollAnimations();
        this.setupFormAnimations();
        this.setupButtonAnimations();
        this.setupModalAnimations();
        this.setupSectionAnimations();
    }
}

// Global UI animations instance
const uiAnimationsManager = new UIAnimationsManager();

// Initialize on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        uiAnimationsManager.initialize();
    });
} else {
    uiAnimationsManager.initialize();
}

/**
 * Helper function to easily animate new rows
 */
window.animateNewRow = function(rowElement) {
    uiAnimationsManager.animateNewTableRow(rowElement);
};

/**
 * Helper function to easily delete rows with animation
 */
window.animateDeleteRow = function(rowElement, callback) {
    uiAnimationsManager.animateRowDelete(rowElement, callback);
};

/**
 * Helper function to show loading state
 */
window.showButtonLoading = function(button) {
    uiAnimationsManager.animateLoadingStart(button);
};

/**
 * Helper function to hide loading state
 */
window.hideButtonLoading = function(button) {
    uiAnimationsManager.animateLoadingEnd(button);
};

/**
 * Helper function to highlight element
 */
window.highlightElement = function(element) {
    uiAnimationsManager.animateHighlight(element);
};

/**
 * Helper function to shake element on error
 */
window.shakeElement = function(element) {
    uiAnimationsManager.animateError(element);
};
