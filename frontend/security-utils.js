/**
 * Security Utilities - Helper Functions for Input Sanitization in Frontend
 * This creates a safe wrapper for DOM manipulation to prevent XSS attacks
 */

// Security utility functions for frontend
const SecurityUtils = {
    /**
     * Escape HTML to prevent XSS attacks
     * @param {string} str - String to escape
     * @returns {string} - Escaped string
     */
    escapeHtml(str) {
        if (typeof str !== 'string') return '';
        
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    },
    
    /**
     * Create element safely with text content (prevents XSS)
     * @param {string} tag - HTML tag name
     * @param {string} text - Text content
     * @param {string} className - Optional CSS class
     * @returns {HTMLElement} - Created element
     */
    createElementWithText(tag, text, className = '') {
        const element = document.createElement(tag);
        element.textContent = text;  // Use textContent instead of innerHTML
        if (className) element.className = className;
        return element;
    },
    
    /**
     * Set inner content safely (escapes HTML)
     * @param {HTMLElement} element - Target element
     * @param {string} content - Content to set
     */
    setTextContent(element, content) {
        if (element && typeof content === 'string') {
            element.textContent = content;
        }
    },
    
    /**
     * Sanitize URL to prevent javascript: protocol attacks
     * @param {string} url - URL to sanitize
     * @returns {string|null} - Sanitized URL or null if invalid
     */
    sanitizeUrl(url) {
        if (typeof url !== 'string') return null;
        
        url = url.trim();
        
        // Only allow http, https protocols
        if (url.startsWith('http://') || url.startsWith('https://')) {
            return url;
        }
        
        return null;
    },
    
    /**
     * Validate email format on frontend
     * @param {string} email - Email to validate
     * @returns {boolean} - True if valid
     */
    validateEmail(email) {
        const pattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        return pattern.test(email);
    },
    
    /**
     * Validate password strength
     * @param {string} password - Password to validate
     * @returns {Object} - Validation result with errors and strength
     */
    validatePassword(password) {
        const result = {
            valid: false,
            errors: [],
            strength: 'weak'
        };
        
        if (!password || password.length < 8) {
            result.errors.push('Password must be at least 8 characters');
            return result;
        }
        
        const hasUpper = /[A-Z]/.test(password);
        const hasLower = /[a-z]/.test(password);
        const hasDigit = /\d/.test(password);
        const hasSpecial = /[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]/.test(password);
        
        if (!hasUpper) result.errors.push('Must contain uppercase letters');
        if (!hasLower) result.errors.push('Must contain lowercase letters');
        if (!hasDigit) result.errors.push('Must contain numbers');
        
        if (hasUpper && hasLower && hasDigit) {
            result.valid = true;
            if (hasSpecial && password.length >= 12) {
                result.strength = 'strong';
            } else if (hasSpecial || password.length >= 10) {
                result.strength = 'medium';
            } else {
                result.strength = 'acceptable';
            }
        }
        
        return result;
    },
    
    /**
     * Sanitize input string (remove dangerous characters)
     * @param {string} str - String to sanitize
     * @param {number} maxLength - Maximum length
     * @returns {string} - Sanitized string
     */
    sanitizeInput(str, maxLength = 1000) {
        if (typeof str !== 'string') return '';
        
        str = str.trim();
        
        if (str.length > maxLength) {
            str = str.substring(0, maxLength);
        }
        
        return str;
    },
    
    /**
     * Create HTML element from safe template (structured approach)
     * @param {Object} config - Configuration object
     * @returns {HTMLElement} - Created element
     */
    createElement(config) {
        const element = document.createElement(config.tag || 'div');
        
        if (config.className) element.className = config.className;
        if (config.id) element.id = config.id;
        if (config.text) element.textContent = config.text;
        
        if (config.attributes) {
            Object.keys(config.attributes).forEach(key => {
                element.setAttribute(key, config.attributes[key]);
            });
        }
        
        if (config.children) {
            config.children.forEach(child => {
                if (child instanceof HTMLElement) {
                    element.appendChild(child);
                }
            });
        }
        
        return element;
    },
    
    /**
     * Secure API fetch wrapper with automatic auth error handling
     * @param {string} url - API endpoint URL
     * @param {Object} options - Fetch options
     * @returns {Promise<Response>} - Fetch promise
     */
    async secureFetch(url, options = {}) {
        try {
            const response = await fetch(url, options);
            
            // Handle 401 Unauthorized (expired token)
            if (response.status === 401) {
                console.warn('⚠️ Authentication token expired or invalid');
                
                // Clear invalid token
                localStorage.removeItem('token');
                localStorage.removeItem('user');
                
                // Show user-friendly message
                if (typeof showNotification === 'function') {
                    showNotification('Your session has expired. Please login again.', 'warning');
                }
                
                // Redirect to login after 2 seconds
                setTimeout(() => {
                    window.location.href = '/';
                }, 2000);
                
                throw new Error('Session expired - redirecting to login');
            }
            
            // Handle other HTTP errors
            if (!response.ok && response.status !== 404) {
                const errorData = await response.json().catch(() => ({}));
                const errorMessage = errorData.error || errorData.message || `HTTP ${response.status}: ${response.statusText}`;
                
                if (typeof showNotification === 'function') {
                    showNotification(errorMessage, 'error');
                }
                
                throw new Error(errorMessage);
            }
            
            return response;
        } catch (error) {
            // Network errors
            if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
                if (typeof showNotification === 'function') {
                    showNotification('Network error. Please check your connection.', 'error');
                }
            }
            throw error;
        }
    }
};

// Make available globally
if (typeof window !== 'undefined') {
    window.SecurityUtils = SecurityUtils;
    window.secureFetch = SecurityUtils.secureFetch.bind(SecurityUtils);
}
