/**
 * API Client with Global 401 Interceptor
 * =======================================
 * Production-grade fetch wrapper that handles:
 * - Automatic auth token injection
 * - Global 401 (Unauthorized) interception
 * - Zombie session cleanup
 * - Concurrent request handling
 * - Token refresh (future: JWT refresh token flow)
 */

(function (window) {
    'use strict';

    // =========================================================================
    // CONFIGURATION
    // =========================================================================

    const API_CONFIG = {
        baseUrl: window.location.hostname === 'localhost'
            ? 'http://localhost:5000/api'
            : window.location.origin + '/api',
        timeout: 30000,
        retryOn401: false  // Set true if implementing refresh token flow
    };

    // =========================================================================
    // AUTH STATE MANAGEMENT
    // =========================================================================

    /**
     * Get the current auth token from localStorage
     * Checks role-specific tokens first, then falls back to generic
     */
    function getAuthToken() {
        const role = localStorage.getItem('currentRole');

        // Role-specific tokens (implemented earlier)
        if (role === 'candidate') {
            return localStorage.getItem('candidate_token');
        } else if (role === 'recruiter' || role === 'company') {
            return localStorage.getItem('recruiter_token');
        } else if (role === 'admin') {
            return localStorage.getItem('admin_token');
        }

        // Fallback to generic token (legacy support)
        return localStorage.getItem('authToken');
    }

    /**
     * Clear ALL auth-related data from localStorage
     * Called when session is invalid (401)
     */
    function clearAuthState() {
        console.warn('🔒 Clearing auth state due to invalid session');

        // Clear role-specific tokens
        localStorage.removeItem('candidate_token');
        localStorage.removeItem('recruiter_token');
        localStorage.removeItem('admin_token');

        // Clear legacy/generic tokens
        localStorage.removeItem('authToken');
        localStorage.removeItem('token');

        // Clear user data
        localStorage.removeItem('currentUser');
        localStorage.removeItem('currentRole');
        localStorage.removeItem('user');

        // Reset in-memory state if globals exist
        if (typeof window.authToken !== 'undefined') window.authToken = null;
        if (typeof window.currentUser !== 'undefined') window.currentUser = null;
        if (typeof window.currentRole !== 'undefined') window.currentRole = null;
    }

    /**
     * Redirect to login page after session cleanup
     */
    function redirectToLogin(reason) {
        console.warn(`🔄 Redirecting to login: ${reason}`);

        // Show notification if function exists
        if (typeof window.showNotification === 'function') {
            window.showNotification(
                'Your session has expired. Please log in again.',
                'warning'
            );
        }

        // Use existing showRoleSelection if available, else redirect
        if (typeof window.showRoleSelection === 'function') {
            window.showRoleSelection();
        } else {
            // Fallback: redirect to index or login page
            window.location.href = '/';
        }
    }

    // =========================================================================
    // 401 INTERCEPTOR - Core Logic
    // =========================================================================

    // Track if we're already handling a 401 to prevent redirect loops
    let isHandling401 = false;

    /**
     * Handle 401 Unauthorized response
     * Cleans up session and redirects to login
     */
    function handle401Response(url) {
        if (isHandling401) {
            console.log('Already handling 401, skipping...');
            return;
        }

        isHandling401 = true;

        console.error(`🚫 401 Unauthorized: ${url}`);
        console.error('Session invalid - cleaning up zombie session');

        // Clear all auth state
        clearAuthState();

        // Small delay to allow concurrent requests to complete
        setTimeout(() => {
            redirectToLogin('Session expired or invalid');
            isHandling401 = false;
        }, 100);
    }

    // =========================================================================
    // FETCH WRAPPER - Production API Client
    // =========================================================================

    /**
     * Enhanced fetch with automatic auth and 401 handling
     * 
     * @param {string} endpoint - API endpoint (with or without leading /)
     * @param {object} options - Fetch options (method, body, headers, etc.)
     * @returns {Promise<Response>} - Fetch response
     */
    async function apiFetch(endpoint, options = {}) {
        // Build full URL
        const url = endpoint.startsWith('http')
            ? endpoint
            : `${API_CONFIG.baseUrl}${endpoint.startsWith('/') ? '' : '/'}${endpoint}`;

        // Get current auth token
        const token = getAuthToken();

        // Merge headers
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        // Add auth header if token exists
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        // Build final options
        const fetchOptions = {
            ...options,
            headers
        };

        try {
            const response = await fetch(url, fetchOptions);

            // =============================================
            // GLOBAL 401 INTERCEPTOR
            // =============================================
            if (response.status === 401) {
                handle401Response(url);

                // Return a rejected promise with auth error
                return Promise.reject({
                    status: 401,
                    message: 'Session expired',
                    isAuthError: true
                });
            }

            return response;

        } catch (error) {
            // Network errors
            console.error('API fetch error:', error);
            throw error;
        }
    }

    /**
     * Convenience methods for common HTTP verbs
     */
    const api = {
        /**
         * Base URL for direct access
         */
        baseUrl: API_CONFIG.baseUrl,

        /**
         * GET request
         */
        get: async function (endpoint, options = {}) {
            return apiFetch(endpoint, { ...options, method: 'GET' });
        },

        /**
         * POST request with JSON body
         */
        post: async function (endpoint, data, options = {}) {
            return apiFetch(endpoint, {
                ...options,
                method: 'POST',
                body: JSON.stringify(data)
            });
        },

        /**
         * PUT request with JSON body
         */
        put: async function (endpoint, data, options = {}) {
            return apiFetch(endpoint, {
                ...options,
                method: 'PUT',
                body: JSON.stringify(data)
            });
        },

        /**
         * DELETE request
         */
        delete: async function (endpoint, options = {}) {
            return apiFetch(endpoint, { ...options, method: 'DELETE' });
        },

        /**
         * POST with FormData (for file uploads)
         * Does NOT set Content-Type (browser sets it with boundary)
         */
        postForm: async function (endpoint, formData, options = {}) {
            const token = getAuthToken();
            const headers = { ...options.headers };

            if (token) {
                headers['Authorization'] = `Bearer ${token}`;
            }

            const url = `${API_CONFIG.baseUrl}${endpoint.startsWith('/') ? '' : '/'}${endpoint}`;

            const response = await fetch(url, {
                method: 'POST',
                body: formData,
                headers
            });

            if (response.status === 401) {
                handle401Response(url);
                return Promise.reject({ status: 401, isAuthError: true });
            }

            return response;
        },

        /**
         * Raw fetch with 401 handling (for custom requests)
         */
        fetch: apiFetch,

        /**
         * Utility: Parse JSON response with error handling
         */
        parseJSON: async function (response) {
            try {
                return await response.json();
            } catch (e) {
                console.error('JSON parse error:', e);
                return null;
            }
        },

        /**
         * Utility: Check if error is auth-related
         */
        isAuthError: function (error) {
            return error && (error.isAuthError || error.status === 401);
        },

        /**
         * Manual logout (for logout button)
         */
        logout: function () {
            clearAuthState();
            redirectToLogin('User logged out');
        },

        /**
         * Check if user is authenticated
         */
        isAuthenticated: function () {
            return !!getAuthToken();
        }
    };

    // =========================================================================
    // GLOBAL INJECTION - Override native fetch for legacy code
    // =========================================================================

    // Store original fetch
    const originalFetch = window.fetch;

    /**
     * Override global fetch to add 401 handling
     * This catches ALL fetch calls, including those not using our api object
     */
    window.fetch = async function (url, options = {}) {
        const response = await originalFetch.call(window, url, options);

        // Only intercept 401 for our API calls
        const isOurAPI = typeof url === 'string' && (
            url.includes('/api/') ||
            url.includes(API_CONFIG.baseUrl)
        );

        // CRITICAL: Do NOT intercept 401 on auth endpoints
        // These endpoints use 401 for normal auth failures (wrong password, etc.)
        const isAuthEndpoint = typeof url === 'string' && (
            url.includes('/auth/login') ||
            url.includes('/auth/register') ||
            url.includes('/auth/forgot-password') ||
            url.includes('/auth/reset-password')
        );

        if (isOurAPI && !isAuthEndpoint && response.status === 401) {
            handle401Response(url);
        }

        return response;
    };

    // =========================================================================
    // EXPORT
    // =========================================================================

    // Make available globally
    window.api = api;
    window.apiFetch = apiFetch;
    window.clearAuthState = clearAuthState;

    console.log('✅ API Client initialized with global 401 interceptor');

})(window);
