/**
 * Animation Utilities for Dashboard Statistics
 * Provides count-up animations for numbers and other visual effects
 */

class AnimationManager {
    /**
     * Animate a number count-up effect
     * @param {HTMLElement} element - Element to animate
     * @param {number} targetNumber - Target number to count up to
     * @param {number} duration - Duration in milliseconds (default: 1000ms)
     * @param {string} format - Optional format function
     */
    static animateNumber(element, targetNumber, duration = 1000, format = null) {
        if (!element) return;

        const startNumber = 0;
        const startTime = performance.now();

        const easeOutQuad = (t) => t * (2 - t);

        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const easeProgress = easeOutQuad(progress);

            const current = Math.floor(startNumber + (targetNumber - startNumber) * easeProgress);

            if (format && typeof format === 'function') {
                element.textContent = format(current);
            } else {
                element.textContent = current.toLocaleString();
            }

            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };

        requestAnimationFrame(animate);
    }

    /**
     * Animate opacity change
     * @param {HTMLElement} element - Element to animate
     * @param {number} fromOpacity - Starting opacity (0-1)
     * @param {number} toOpacity - Ending opacity (0-1)
     * @param {number} duration - Duration in milliseconds
     */
    static fadeInOut(element, fromOpacity, toOpacity, duration = 500) {
        if (!element) return;

        const startTime = performance.now();

        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);

            element.style.opacity = fromOpacity + (toOpacity - fromOpacity) * progress;

            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };

        requestAnimationFrame(animate);
    }

    /**
     * Animate a progress bar fill
     * @param {HTMLElement} element - Progress bar element
     * @param {number} percentage - Target percentage (0-100)
     * @param {number} duration - Duration in milliseconds
     */
    static animateProgressBar(element, percentage, duration = 800) {
        if (!element) return;

        const startTime = performance.now();
        const startPercentage = 0;

        const easeOutCubic = (t) => 1 - Math.pow(1 - t, 3);

        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const easeProgress = easeOutCubic(progress);

            const current = startPercentage + (percentage - startPercentage) * easeProgress;

            element.style.width = current + '%';
            if (element.querySelector('.progress-text')) {
                element.querySelector('.progress-text').textContent = Math.floor(current) + '%';
            }

            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };

        requestAnimationFrame(animate);
    }

    /**
     * Animate scale transformation (pop effect)
     * @param {HTMLElement} element - Element to animate
     * @param {number} fromScale - Starting scale
     * @param {number} toScale - Ending scale
     * @param {number} duration - Duration in milliseconds
     */
    static scaleAnimate(element, fromScale, toScale, duration = 500) {
        if (!element) return;

        const startTime = performance.now();

        const easeOutBack = (t) => {
            const c1 = 1.70158;
            const c3 = c1 + 1;
            return c3 * t * t * t - c1 * t * t;
        };

        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const easeProgress = easeOutBack(progress);

            const current = fromScale + (toScale - fromScale) * easeProgress;
            element.style.transform = `scale(${current})`;

            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };

        requestAnimationFrame(animate);
    }

    /**
     * Rotate animation (spinning effect)
     * @param {HTMLElement} element - Element to animate
     * @param {number} duration - Duration in milliseconds
     * @param {number} rotations - Number of full rotations
     */
    static rotateAnimate(element, duration = 2000, rotations = 1) {
        if (!element) return;

        const startTime = performance.now();

        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = (elapsed / duration) % 1;

            element.style.transform = `rotate(${progress * 360 * rotations}deg)`;

            if (elapsed < duration) {
                requestAnimationFrame(animate);
            }
        };

        requestAnimationFrame(animate);
    }

    /**
     * Pulse animation (opacity pulsing)
     * @param {HTMLElement} element - Element to animate
     * @param {number} duration - Duration in milliseconds
     */
    static pulseAnimate(element, duration = 2000) {
        if (!element) return;

        const startTime = performance.now();

        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = (elapsed / duration) % 1;
            
            // Sine wave for smooth pulsing
            const opacity = 0.5 + 0.5 * Math.sin(progress * Math.PI * 2);

            element.style.opacity = opacity;
            requestAnimationFrame(animate);
        };

        requestAnimationFrame(animate);
    }

    /**
     * Slide in animation
     * @param {HTMLElement} element - Element to animate
     * @param {string} direction - 'left', 'right', 'up', 'down'
     * @param {number} distance - Distance in pixels
     * @param {number} duration - Duration in milliseconds
     */
    static slideIn(element, direction, distance, duration = 600) {
        if (!element) return;

        const startTime = performance.now();

        const translateMap = {
            'left': { start: -distance, end: 0, axis: 'X' },
            'right': { start: distance, end: 0, axis: 'X' },
            'up': { start: distance, end: 0, axis: 'Y' },
            'down': { start: -distance, end: 0, axis: 'Y' }
        };

        const { start, end, axis } = translateMap[direction] || { start: -distance, end: 0, axis: 'X' };

        const easeOutCubic = (t) => 1 - Math.pow(1 - t, 3);

        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const easeProgress = easeOutCubic(progress);

            const current = start + (end - start) * easeProgress;

            element.style.transform = `translate${axis}(${current}px)`;
            element.style.opacity = progress;

            if (progress < 1) {
                requestAnimationFrame(animate);
            } else {
                element.style.transform = `translate${axis}(0)`;
                element.style.opacity = 1;
            }
        };

        requestAnimationFrame(animate);
    }

    /**
     * Bounce animation
     * @param {HTMLElement} element - Element to animate
     * @param {number} bounceHeight - Height in pixels
     * @param {number} duration - Duration in milliseconds
     * @param {number} bounces - Number of bounces
     */
    static bounceAnimate(element, bounceHeight, duration = 1000, bounces = 3) {
        if (!element) return;

        const startTime = performance.now();

        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = (elapsed / duration) % 1;
            
            // Calculate bounce using sine wave
            let bounceProgress = progress * bounces * Math.PI;
            let offset = Math.abs(Math.sin(bounceProgress)) * bounceHeight;

            // Dampen over time
            const dampening = 1 - (Math.floor(progress * bounces) / bounces);
            offset *= dampening;

            element.style.transform = `translateY(-${offset}px)`;

            if (elapsed < duration) {
                requestAnimationFrame(animate);
            } else {
                element.style.transform = 'translateY(0)';
            }
        };

        requestAnimationFrame(animate);
    }

    /**
     * Shake animation (useful for errors)
     * @param {HTMLElement} element - Element to animate
     * @param {number} intensity - Shake intensity in pixels
     * @param {number} duration - Duration in milliseconds
     */
    static shakeAnimate(element, intensity = 5, duration = 300) {
        if (!element) return;

        const startTime = performance.now();

        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);

            if (progress < 1) {
                const randomX = (Math.random() - 0.5) * intensity;
                const randomY = (Math.random() - 0.5) * intensity;

                element.style.transform = `translate(${randomX}px, ${randomY}px)`;
                requestAnimationFrame(animate);
            } else {
                element.style.transform = 'translate(0, 0)';
            }
        };

        requestAnimationFrame(animate);
    }

    /**
     * Glow effect (multiple shadows)
     * @param {HTMLElement} element - Element to animate
     * @param {string} color - Glow color (CSS color)
     * @param {number} maxIntensity - Max glow intensity
     * @param {number} duration - Duration in milliseconds
     */
    static glowAnimate(element, color = '#00d4ff', maxIntensity = 20, duration = 2000) {
        if (!element) return;

        const startTime = performance.now();

        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = (elapsed / duration) % 1;
            
            // Sine wave for smooth glowing
            const intensity = maxIntensity + maxIntensity * Math.sin(progress * Math.PI * 2);

            element.style.boxShadow = `0 0 ${intensity}px ${color}, 0 0 ${intensity * 0.5}px ${color}`;
            requestAnimationFrame(animate);
        };

        requestAnimationFrame(animate);
    }
}

// Export for use
window.AnimationManager = AnimationManager;
