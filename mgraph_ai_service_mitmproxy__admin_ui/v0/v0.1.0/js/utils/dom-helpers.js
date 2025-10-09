// DOM Helper Utilities
// Common DOM manipulation and helper functions

const DOMHelpers = {
    // Safely query selector
    $(selector, parent = document) {
        return parent.querySelector(selector);
    },

    // Query all matching elements
    $$(selector, parent = document) {
        return Array.from(parent.querySelectorAll(selector));
    },

    // Create element with attributes and children
    createElement(tag, attributes = {}, children = []) {
        const el = document.createElement(tag);
        
        // Set attributes
        Object.entries(attributes).forEach(([key, value]) => {
            if (key === 'className') {
                el.className = value;
            } else if (key === 'dataset') {
                Object.entries(value).forEach(([dataKey, dataValue]) => {
                    el.dataset[dataKey] = dataValue;
                });
            } else if (key.startsWith('on') && typeof value === 'function') {
                el.addEventListener(key.substring(2).toLowerCase(), value);
            } else {
                el.setAttribute(key, value);
            }
        });
        
        // Append children
        children.forEach(child => {
            if (typeof child === 'string') {
                el.appendChild(document.createTextNode(child));
            } else if (child instanceof HTMLElement) {
                el.appendChild(child);
            }
        });
        
        return el;
    },

    // Format number with thousands separator
    formatNumber(num) {
        return num.toLocaleString();
    },

    // Format bytes to human-readable
    formatBytes(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
    },

    // Debounce function calls
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    // Show/hide loading state
    setLoading(element, isLoading) {
        if (isLoading) {
            element.classList.add('loading');
        } else {
            element.classList.remove('loading');
        }
    }
};

// Export to window for global access
window.DOMHelpers = DOMHelpers;
