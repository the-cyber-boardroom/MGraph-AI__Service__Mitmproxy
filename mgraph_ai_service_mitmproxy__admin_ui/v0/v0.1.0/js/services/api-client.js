// API Client Service
// Handles communication with the proxy backend

class APIClient {
    constructor() {
        this.baseURL = window.location.origin;
    }

    // Get current request context from URL or headers
    getRequestContext() {
        const params = new URLSearchParams(window.location.search);
        return {
            host: params.get('host') || window.location.hostname,
            path: params.get('path') || window.location.pathname
        };
    }

    // Parse cookies from document.cookie
    parseCookies() {
        const cookies = {};
        document.cookie.split(';').forEach(cookie => {
            const [name, ...value] = cookie.split('=');
            if (name && value) {
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

    // Set a cookie
    setCookie(name, value, maxAge = 3600) {
        document.cookie = `${name}=${value}; path=/; max-age=${maxAge}; samesite=Lax`;
    }

    // Clear a cookie
    clearCookie(name) {
        document.cookie = `${name}=; path=/; max-age=0`;
    }

    // Clear all proxy cookies
    clearAllProxyCookies() {
        const proxyCookies = this.getProxyCookies();
        Object.keys(proxyCookies).forEach(name => {
            this.clearCookie(name);
        });
    }

    // Emit custom event for cross-component communication
    emit(eventName, detail) {
        window.dispatchEvent(new CustomEvent(eventName, { detail }));
    }

    // Listen for custom events
    on(eventName, handler) {
        window.addEventListener(eventName, handler);
    }
}

// Create global API client instance
window.apiClient = new APIClient();
