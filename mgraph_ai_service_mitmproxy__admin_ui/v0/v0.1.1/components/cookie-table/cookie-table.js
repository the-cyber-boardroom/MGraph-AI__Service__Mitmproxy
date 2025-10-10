// Enhanced Cookie Table Component
// Displays active proxy cookies with delete functionality

class CookieTable extends HTMLElement {
    constructor() {
        super();
        this.templateURL = './components/cookie-table/cookie-table.html';
        this.styleURL    = './components/cookie-table/cookie-table.css';
        this.state = {
            cookies: {}
        };
    }

    async connectedCallback() {
        await this.loadStyles();
        await this.loadTemplate();
        this.render();
        this.setupEventListeners();
    }

    disconnectedCallback() {
        this.removeEventListeners();
    }

    async loadStyles() {
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = this.styleURL;
        document.head.appendChild(link);
    }

    async loadTemplate() {
        const response = await fetch(this.templateURL);
        const html     = await response.text();
        this.innerHTML = html;
    }

    setData(cookies) {
        this.state.cookies = cookies || {};
        this.render();
    }

    setupEventListeners() {
        this.boundCookieChangeHandler = () => this.refreshCookies();
        window.apiClient.on('cookie-changed', this.boundCookieChangeHandler);
        window.apiClient.on('cookie-deleted', this.boundCookieChangeHandler);
        window.apiClient.on('cookies-cleared', this.boundCookieChangeHandler);
    }

    removeEventListeners() {
        if (this.boundCookieChangeHandler) {
            window.apiClient.off('cookie-changed', this.boundCookieChangeHandler);
            window.apiClient.off('cookie-deleted', this.boundCookieChangeHandler);
            window.apiClient.off('cookies-cleared', this.boundCookieChangeHandler);
        }
    }

    refreshCookies() {
        const updatedCookies = window.apiClient.getProxyCookies();
        this.setData(updatedCookies);
    }

    deleteCookie(name) {
        if (confirm(`Are you sure you want to delete the cookie "${name}"?`)) {
            window.apiClient.clearCookie(name);
        }
    }

    render() {
        const { cookies } = this.state;
        const container = this.querySelector('.cookie-table-container');
        
        if (!container) return;
        
        if (Object.keys(cookies).length === 0) {
            container.innerHTML = '<div class="empty-state">No proxy cookies are currently active</div>';
            return;
        }

        const rows = Object.entries(cookies).map(([name, value]) => `
            <tr>
                <td><strong>${name}</strong></td>
                <td class="cookie-value">${value}</td>
                <td class="cookie-actions">
                    <button class="btn-delete" data-cookie="${name}" title="Delete this cookie">
                        🗑️ Delete
                    </button>
                </td>
            </tr>
        `).join('');

        container.innerHTML = `
            <table class="cookie-table">
                <thead>
                    <tr>
                        <th>Cookie Name</th>
                        <th>Value</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${rows}
                </tbody>
            </table>
        `;

        // Attach delete button handlers
        container.querySelectorAll('.btn-delete').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const cookieName = e.target.dataset.cookie;
                this.deleteCookie(cookieName);
            });
        });
    }
}

customElements.define('cookie-table', CookieTable);
