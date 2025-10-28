// Enhanced API Client Service
// Handles communication with the proxy backend and real-time data

class APIClient {
    constructor() {
        this.baseURL = window.location.origin;
        this.apiDataEndpoint = '/mitm-proxy/admin-ui.json';
    }

    // Get current request context from URL or headers
    getRequestContext() {
        const params = new URLSearchParams(window.location.search);
        return {
            host: params.get('host') || window.location.hostname,
            path: params.get('path') || window.location.pathname
        };
    }

    // Fetch real API data from the server
    async fetchAPIData() {
        try {
            const response = await fetch(this.apiDataEndpoint);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Failed to fetch API data:', error);
            throw error;
        }
    }

    // Parse cookies from document.cookie
    parseCookies() {
        const cookies = {};
        document.cookie.split(';').forEach(cookie => {
            const [name, ...value] = cookie.split('=');
            if (name && value.length > 0) {
                cookies[name.trim()] = value.join('=').trim();
            }
        });
        return cookies;
    }

    // Get proxy cookies (mitm-* prefix)
    getProxyCookies() {
        const allCookies = this.parseCookies();
        const proxyCookies = {};
        
        Object.entries(allCookies).forEach(([name, value]) => {
            if (name.startsWith('mitm-')) {
                proxyCookies[name] = value;
            }
        });
        
        return proxyCookies;
    }

    // Set a cookie without page reload
    setCookie(name, value, maxAge = 360000) {
        document.cookie = `${name}=${value}; path=/; max-age=${maxAge}; samesite=Lax`;
        
        // Emit event for real-time updates
        this.emit('cookie-changed', { name, value });
    }

    // Clear a specific cookie without page reload
    clearCookie(name) {
        document.cookie = `${name}=; path=/; max-age=0`;
        
        // Emit event for real-time updates
        this.emit('cookie-deleted', { name });
    }

    // Clear all proxy cookies
    clearAllProxyCookies() {
        const proxyCookies = this.getProxyCookies();
        Object.keys(proxyCookies).forEach(name => {
            this.clearCookie(name);
        });
        
        // Emit event for real-time updates
        this.emit('cookies-cleared', {});
    }

    // Emit custom event for cross-component communication
    emit(eventName, detail) {
        window.dispatchEvent(new CustomEvent(eventName, { detail }));
    }

    // Listen for custom events
    on(eventName, handler) {
        window.addEventListener(eventName, handler);
    }

    // Remove event listener
    off(eventName, handler) {
        window.removeEventListener(eventName, handler);
    }
}

// Create global API client instance
window.apiClient = new APIClient();
