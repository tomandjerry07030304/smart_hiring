/**
 * Modern UI Utilities
 * Enhanced notifications, loading states, and accessibility helpers
 */

// Toast Notification System
class ToastManager {
    constructor() {
        this.container = this.createContainer();
        this.toasts = [];
    }

    createContainer() {
        let container = document.querySelector('.toast-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'toast-container';
            document.body.appendChild(container);
        }
        return container;
    }

    show(message, type = 'info', title = '', duration = 5000) {
        const toast = this.createToast(message, type, title);
        this.container.appendChild(toast);
        this.toasts.push(toast);

        // Auto remove after duration
        if (duration > 0) {
            setTimeout(() => this.remove(toast), duration);
        }

        return toast;
    }

    createToast(message, type, title) {
        const toast = document.createElement('div');
        toast.className = `toast-notification ${type} smooth-appear`;

        const icons = {
            success: '✓',
            error: '✕',
            warning: '⚠',
            info: 'ℹ'
        };

        const titles = {
            success: title || 'Success',
            error: title || 'Error',
            warning: title || 'Warning',
            info: title || 'Info'
        };

        toast.innerHTML = `
            <div class="toast-icon">${icons[type] || icons.info}</div>
            <div class="toast-content">
                <div class="toast-title">${titles[type]}</div>
                <div class="toast-message">${message}</div>
            </div>
            <button class="toast-close" aria-label="Close notification">&times;</button>
            <div class="toast-progress">
                <div class="toast-progress-bar"></div>
            </div>
        `;

        // Close button handler
        const closeBtn = toast.querySelector('.toast-close');
        closeBtn.addEventListener('click', () => this.remove(toast));

        // Accessibility
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'polite');

        return toast;
    }

    remove(toast) {
        toast.classList.add('removing');
        setTimeout(() => {
            if (toast.parentElement) {
                toast.parentElement.removeChild(toast);
            }
            this.toasts = this.toasts.filter(t => t !== toast);
        }, 300);
    }

    success(message, title = 'Success') {
        return this.show(message, 'success', title);
    }

    error(message, title = 'Error') {
        return this.show(message, 'error', title);
    }

    warning(message, title = 'Warning') {
        return this.show(message, 'warning', title);
    }

    info(message, title = 'Info') {
        return this.show(message, 'info', title);
    }

    clearAll() {
        this.toasts.forEach(toast => this.remove(toast));
    }
}

// Global toast instance
const toast = new ToastManager();

// Loading Overlay Manager
class LoadingManager {
    constructor() {
        this.overlay = null;
        this.count = 0;
    }

    show(message = 'Loading...') {
        this.count++;
        
        if (!this.overlay) {
            this.overlay = document.createElement('div');
            this.overlay.className = 'loading-overlay';
            this.overlay.innerHTML = `
                <div style="text-align: center;">
                    <div class="spinner"></div>
                    <p style="color: white; margin-top: 16px; font-size: 16px;" id="loading-message">${message}</p>
                </div>
            `;
            document.body.appendChild(this.overlay);
        } else {
            const messageEl = this.overlay.querySelector('#loading-message');
            if (messageEl) messageEl.textContent = message;
        }
    }

    hide() {
        this.count = Math.max(0, this.count - 1);
        
        if (this.count === 0 && this.overlay) {
            this.overlay.remove();
            this.overlay = null;
        }
    }

    forceHide() {
        this.count = 0;
        if (this.overlay) {
            this.overlay.remove();
            this.overlay = null;
        }
    }
}

const loading = new LoadingManager();

// Skeleton Screen Generator
function createSkeletonCard() {
    return `
        <div class="skeleton-card">
            <div class="skeleton skeleton-header"></div>
            <div class="skeleton skeleton-text long"></div>
            <div class="skeleton skeleton-text medium"></div>
            <div class="skeleton skeleton-text short"></div>
        </div>
    `;
}

function createSkeletonTable(rows = 5) {
    let html = '';
    for (let i = 0; i < rows; i++) {
        html += `
            <div class="skeleton-table-row">
                <div class="skeleton skeleton-table-cell"></div>
                <div class="skeleton skeleton-table-cell"></div>
                <div class="skeleton skeleton-table-cell"></div>
                <div class="skeleton skeleton-table-cell"></div>
            </div>
        `;
    }
    return html;
}

function showSkeletonLoader(containerId, type = 'card', count = 3) {
    const container = document.getElementById(containerId);
    if (!container) return;

    let html = '';
    if (type === 'card') {
        for (let i = 0; i < count; i++) {
            html += createSkeletonCard();
        }
    } else if (type === 'table') {
        html = createSkeletonTable(count);
    }
    
    container.innerHTML = html;
}

// Empty State Generator
function showEmptyState(containerId, options = {}) {
    const {
        icon = '📭',
        title = 'No items found',
        description = 'There are no items to display at the moment.',
        actionText = null,
        actionHref = null,
        actionOnClick = null
    } = options;

    const container = document.getElementById(containerId);
    if (!container) return;

    let actionHtml = '';
    if (actionText) {
        if (actionHref) {
            actionHtml = `<a href="${actionHref}" class="empty-state-action">${actionText}</a>`;
        } else if (actionOnClick) {
            actionHtml = `<button class="empty-state-action" onclick="${actionOnClick}">${actionText}</button>`;
        }
    }

    container.innerHTML = `
        <div class="empty-state">
            <div class="empty-state-icon">${icon}</div>
            <div class="empty-state-title">${title}</div>
            <div class="empty-state-description">${description}</div>
            ${actionHtml}
        </div>
    `;
}

// Accessibility Helpers
function announceToScreenReader(message, priority = 'polite') {
    const announcement = document.createElement('div');
    announcement.setAttribute('role', 'status');
    announcement.setAttribute('aria-live', priority);
    announcement.className = 'sr-only';
    announcement.textContent = message;
    
    document.body.appendChild(announcement);
    
    setTimeout(() => {
        document.body.removeChild(announcement);
    }, 1000);
}

function trapFocus(element) {
    const focusableElements = element.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];

    element.addEventListener('keydown', function(e) {
        if (e.key === 'Tab') {
            if (e.shiftKey) {
                if (document.activeElement === firstElement) {
                    lastElement.focus();
                    e.preventDefault();
                }
            } else {
                if (document.activeElement === lastElement) {
                    firstElement.focus();
                    e.preventDefault();
                }
            }
        }
        
        if (e.key === 'Escape') {
            const closeBtn = element.querySelector('[data-close], .modal-close, .close');
            if (closeBtn) closeBtn.click();
        }
    });
}

// Ripple Effect
function addRippleEffect(button) {
    button.classList.add('ripple');
}

// Smooth Scroll
function smoothScrollTo(targetId, offset = 0) {
    const target = document.getElementById(targetId);
    if (!target) return;

    const targetPosition = target.getBoundingClientRect().top + window.pageYOffset - offset;
    
    window.scrollTo({
        top: targetPosition,
        behavior: 'smooth'
    });
}

// Debounce utility
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Throttle utility
function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Copy to Clipboard with feedback
async function copyToClipboard(text, successMessage = 'Copied to clipboard!') {
    try {
        await navigator.clipboard.writeText(text);
        toast.success(successMessage);
        return true;
    } catch (err) {
        toast.error('Failed to copy to clipboard');
        return false;
    }
}

// Confirm Dialog with custom styling
function confirmDialog(message, title = 'Confirm Action') {
    return new Promise((resolve) => {
        const dialog = document.createElement('div');
        dialog.className = 'modal active';
        dialog.innerHTML = `
            <div class="modal-content scale-in" style="max-width: 400px;">
                <h2 style="margin: 0 0 16px 0;">${title}</h2>
                <p style="color: #718096; margin-bottom: 24px;">${message}</p>
                <div style="display: flex; gap: 12px;">
                    <button class="btn-secondary" style="flex: 1;" data-action="cancel">Cancel</button>
                    <button class="btn-primary" style="flex: 1;" data-action="confirm">Confirm</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(dialog);
        
        const handleClick = (e) => {
            const action = e.target.getAttribute('data-action');
            if (action) {
                dialog.remove();
                resolve(action === 'confirm');
            }
        };
        
        dialog.addEventListener('click', handleClick);
        
        // Focus trap
        const modalContent = dialog.querySelector('.modal-content');
        trapFocus(modalContent);
        
        // Focus confirm button
        const confirmBtn = dialog.querySelector('[data-action="confirm"]');
        setTimeout(() => confirmBtn.focus(), 100);
    });
}

// Enhanced fetch with loading and error handling
async function fetchWithUI(url, options = {}) {
    const showLoading = options.showLoading !== false;
    const showSuccess = options.showSuccess !== false;
    const showError = options.showError !== false;
    
    if (showLoading) {
        loading.show(options.loadingMessage || 'Loading...');
    }
    
    try {
        const response = await fetch(url, options);
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error || `HTTP ${response.status}`);
        }
        
        const data = await response.json();
        
        if (showSuccess && options.successMessage) {
            toast.success(options.successMessage);
        }
        
        return { success: true, data };
        
    } catch (error) {
        if (showError) {
            toast.error(error.message || 'An error occurred');
        }
        return { success: false, error: error.message };
        
    } finally {
        if (showLoading) {
            loading.hide();
        }
    }
}

// Keyboard shortcuts manager
class KeyboardShortcuts {
    constructor() {
        this.shortcuts = new Map();
        this.init();
    }

    init() {
        document.addEventListener('keydown', (e) => {
            const key = this.getKeyString(e);
            const handler = this.shortcuts.get(key);
            
            if (handler) {
                e.preventDefault();
                handler(e);
            }
        });
    }

    getKeyString(e) {
        const parts = [];
        if (e.ctrlKey) parts.push('ctrl');
        if (e.altKey) parts.push('alt');
        if (e.shiftKey) parts.push('shift');
        if (e.metaKey) parts.push('meta');
        parts.push(e.key.toLowerCase());
        return parts.join('+');
    }

    register(keyCombo, handler, description = '') {
        this.shortcuts.set(keyCombo, handler);
    }

    unregister(keyCombo) {
        this.shortcuts.delete(keyCombo);
    }
}

const keyboard = new KeyboardShortcuts();

// Initialize accessibility features
function initAccessibility() {
    // Add skip to main content link
    const skipLink = document.createElement('a');
    skipLink.href = '#main-content';
    skipLink.className = 'skip-to-main';
    skipLink.textContent = 'Skip to main content';
    document.body.insertBefore(skipLink, document.body.firstChild);
    
    // Add main content ID if not exists
    const mainContent = document.querySelector('main, .main-content, [role="main"]');
    if (mainContent && !mainContent.id) {
        mainContent.id = 'main-content';
    }
    
    // Enhance buttons with ripple effect
    document.querySelectorAll('button, .btn').forEach(btn => {
        if (!btn.classList.contains('no-ripple')) {
            addRippleEffect(btn);
        }
    });
}

// Auto-initialize on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAccessibility);
} else {
    initAccessibility();
}

// Export utilities
window.uiUtils = {
    toast,
    loading,
    showSkeletonLoader,
    showEmptyState,
    announceToScreenReader,
    trapFocus,
    smoothScrollTo,
    debounce,
    throttle,
    copyToClipboard,
    confirmDialog,
    fetchWithUI,
    keyboard
};
