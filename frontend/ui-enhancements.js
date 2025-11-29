/**
 * UI Enhancements Integration
 * Enhances existing functions with loading states, empty states, and toast notifications
 */

// Enhanced fetch wrapper for all API calls
const originalFetch = window.fetch;
window.fetch = function(url, options = {}) {
    // Check if this is an API call
    const isAPICall = url.includes('/api/') || url.startsWith(API_URL);
    
    // Apply enhanced UI only for explicit showLoading flag
    const enhanceUI = options.showLoading !== false && isAPICall;
    
    if (enhanceUI && window.uiUtils) {
        window.uiUtils.loading.show(options.loadingMessage || 'Loading...');
    }
    
    return originalFetch(url, options)
        .then(response => {
            if (enhanceUI && window.uiUtils) {
                window.uiUtils.loading.hide();
            }
            return response;
        })
        .catch(error => {
            if (enhanceUI && window.uiUtils) {
                window.uiUtils.loading.hide();
            }
            throw error;
        });
};

// Enhanced notification function - replaces old showNotification
if (typeof showNotification !== 'undefined') {
    const oldShowNotification = showNotification;
    window.showNotification = function(message, type = 'info', duration = 5000) {
        if (window.uiUtils && window.uiUtils.toast) {
            window.uiUtils.toast.show(message, type, '', duration);
        } else {
            oldShowNotification(message, type, duration);
        }
    };
}

// Add empty state helper for job lists
function displayJobsWithEmptyState(container, jobs, renderFunc) {
    if (!container) return;
    
    if (!jobs || jobs.length === 0) {
        if (window.uiUtils) {
            window.uiUtils.showEmptyState(container.id, {
                icon: '💼',
                title: 'No Jobs Found',
                description: 'There are no jobs available at the moment. Check back soon!',
                actionText: null
            });
        } else {
            container.innerHTML = '<div class="empty-state">No jobs available at the moment.</div>';
        }
        return;
    }
    
    renderFunc(jobs);
}

// Add empty state helper for applications
function displayApplicationsWithEmptyState(container, applications, renderFunc) {
    if (!container) return;
    
    if (!applications || applications.length === 0) {
        if (window.uiUtils) {
            window.uiUtils.showEmptyState(container.id, {
                icon: '📋',
                title: 'No Applications Yet',
                description: 'You haven\'t applied to any jobs yet. Browse available jobs to get started!',
                actionText: 'Browse Jobs',
                actionOnClick: 'switchCandidateTab(\'browse\')'
            });
        } else {
            container.innerHTML = '<div class="empty-state">No applications yet.</div>';
        }
        return;
    }
    
    renderFunc(applications);
}

// Add empty state helper for quizzes
function displayQuizzesWithEmptyState(container, quizzes, renderFunc) {
    if (!container) return;
    
    if (!quizzes || quizzes.length === 0) {
        if (window.uiUtils) {
            window.uiUtils.showEmptyState(container.id, {
                icon: '📝',
                title: 'No Assessments Available',
                description: 'There are no assessments assigned to you at this time.',
                actionText: null
            });
        } else {
            container.innerHTML = '<div class="empty-state">No assessments available.</div>';
        }
        return;
    }
    
    renderFunc(quizzes);
}

// Add loading skeleton for job cards
function showJobsLoadingSkeleton(containerId) {
    if (window.uiUtils) {
        window.uiUtils.showSkeletonLoader(containerId, 'card', 6);
    } else {
        const container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = '<div class="loading">Loading...</div>';
        }
    }
}

// Add loading skeleton for tables
function showTableLoadingSkeleton(containerId, rows = 5) {
    if (window.uiUtils) {
        window.uiUtils.showSkeletonLoader(containerId, 'table', rows);
    } else {
        const container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = '<div class="loading">Loading...</div>';
        }
    }
}

// Enhance form submissions with loading and feedback
function enhanceFormSubmit(formElement, submitHandler) {
    if (!formElement) return;
    
    formElement.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const submitBtn = formElement.querySelector('button[type="submit"]');
        const originalText = submitBtn ? submitBtn.textContent : '';
        
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.textContent = 'Processing...';
        }
        
        try {
            const result = await submitHandler(e);
            
            if (result && result.success !== false) {
                if (window.uiUtils) {
                    window.uiUtils.toast.success(result.message || 'Operation completed successfully');
                } else {
                    showNotification(result.message || 'Success', 'success');
                }
            }
        } catch (error) {
            if (window.uiUtils) {
                window.uiUtils.toast.error(error.message || 'An error occurred');
            } else {
                showNotification(error.message || 'Error', 'error');
            }
        } finally {
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
            }
        }
    });
}

// Add confirmation dialog for delete actions
async function confirmDelete(itemName, deleteHandler) {
    if (window.uiUtils && window.uiUtils.confirmDialog) {
        const confirmed = await window.uiUtils.confirmDialog(
            `Are you sure you want to delete "${itemName}"? This action cannot be undone.`,
            'Confirm Delete'
        );
        
        if (confirmed) {
            try {
                await deleteHandler();
                window.uiUtils.toast.success(`"${itemName}" deleted successfully`);
                return true;
            } catch (error) {
                window.uiUtils.toast.error(`Failed to delete "${itemName}"`);
                return false;
            }
        }
        return false;
    } else {
        // Fallback to native confirm
        if (confirm(`Are you sure you want to delete "${itemName}"?`)) {
            try {
                await deleteHandler();
                showNotification(`"${itemName}" deleted successfully`, 'success');
                return true;
            } catch (error) {
                showNotification(`Failed to delete "${itemName}"`, 'error');
                return false;
            }
        }
        return false;
    }
}

// Add smooth page transitions
function showPageWithTransition(pageId) {
    const pages = document.querySelectorAll('.page');
    pages.forEach(page => {
        page.style.opacity = '0';
        page.style.display = 'none';
    });
    
    const targetPage = document.getElementById(pageId);
    if (targetPage) {
        targetPage.style.display = 'block';
        setTimeout(() => {
            targetPage.style.opacity = '1';
            targetPage.style.transition = 'opacity 0.3s ease-in-out';
        }, 10);
    }
}

// Enhanced error handling for API calls
async function apiCall(url, options = {}) {
    try {
        const response = await fetch(url, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': authToken ? `Bearer ${authToken}` : '',
                ...options.headers
            }
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error || errorData.message || `HTTP ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        
        if (window.uiUtils) {
            window.uiUtils.toast.error(error.message || 'An error occurred');
        } else {
            showNotification(error.message || 'An error occurred', 'error');
        }
        
        throw error;
    }
}

// Add ripple effects to all buttons on page load
function addRippleEffectsToButtons() {
    if (!window.uiUtils) return;
    
    document.querySelectorAll('button:not(.no-ripple), .btn:not(.no-ripple)').forEach(button => {
        if (!button.classList.contains('ripple')) {
            button.classList.add('ripple');
        }
    });
}

// Initialize enhancements on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        addRippleEffectsToButtons();
        
        // Add keyboard shortcuts
        if (window.uiUtils && window.uiUtils.keyboard) {
            // Global shortcuts
            window.uiUtils.keyboard.register('ctrl+/', () => {
                const searchInput = document.querySelector('input[type="search"], input[placeholder*="Search"]');
                if (searchInput) searchInput.focus();
            }, 'Focus search');
            
            window.uiUtils.keyboard.register('escape', () => {
                const modal = document.querySelector('.modal.active');
                if (modal) {
                    const closeBtn = modal.querySelector('.modal-close, [data-close]');
                    if (closeBtn) closeBtn.click();
                }
            }, 'Close modal');
        }
    });
} else {
    addRippleEffectsToButtons();
}

// Export enhanced utilities
window.enhancedUI = {
    displayJobsWithEmptyState,
    displayApplicationsWithEmptyState,
    displayQuizzesWithEmptyState,
    showJobsLoadingSkeleton,
    showTableLoadingSkeleton,
    enhanceFormSubmit,
    confirmDelete,
    showPageWithTransition,
    apiCall
};

console.log('✨ UI Enhancements loaded successfully');
