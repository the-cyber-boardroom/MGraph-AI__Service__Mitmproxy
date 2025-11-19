// API Data Viewer Component
// Displays formatted JSON data from /mitm-proxy/admin-ui.json

class APIDataViewer extends HTMLElement {
    constructor() {
        super();
        this.templateURL = './components/api-data-viewer/api-data-viewer.html';
        this.styleURL    = './components/api-data-viewer/api-data-viewer.css';
        this.state = {
            data: null,
            loading: true,
            error: null
        };
    }

    async connectedCallback() {
        await this.loadStyles();
        await this.loadTemplate();
        await this.loadData();
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

    async loadData() {
        this.setState({ loading: true, error: null });
        
        try {
            const data = await window.apiClient.fetchAPIData();
            this.setState({ data, loading: false });
        } catch (error) {
            this.setState({ error: error.message, loading: false });
        }
    }

    setState(newState) {
        this.state = { ...this.state, ...newState };
        this.render();
    }

    async refresh() {
        await this.loadData();
    }

    formatValue(value) {
        if (value === null) return '<span class="null">null</span>';
        if (typeof value === 'boolean') return `<span class="boolean">${value}</span>`;
        if (typeof value === 'number') return `<span class="number">${value}</span>`;
        if (typeof value === 'string') return `<span class="string">"${value}"</span>`;
        return value;
    }

    renderObject(obj, level = 0) {
        const entries = Object.entries(obj);
        
        if (entries.length === 0) return '{}';
        
        const items = entries.map(([key, value]) => {
            if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
                return `
                    <div class="json-line" style="margin-left: ${level * 20}px">
                        <span class="json-key">"${key}"</span>: {
                        ${this.renderObject(value, level + 1)}
                        <div style="margin-left: ${level * 20}px">}</div>
                    </div>
                `;
            } else if (Array.isArray(value)) {
                return `
                    <div class="json-line" style="margin-left: ${level * 20}px">
                        <span class="json-key">"${key}"</span>: [${value.map(v => this.formatValue(v)).join(', ')}]
                    </div>
                `;
            } else {
                return `
                    <div class="json-line" style="margin-left: ${level * 20}px">
                        <span class="json-key">"${key}"</span>: ${this.formatValue(value)}
                    </div>
                `;
            }
        }).join('');
        
        return items;
    }

    render() {
        const { data, loading, error } = this.state;
        const container = this.querySelector('.api-data-container');
        
        if (!container) return;
        
        if (loading) {
            container.innerHTML = `
                <div class="loading-state">
                    <div class="spinner"></div>
                    <p>Loading API data...</p>
                </div>
            `;
            return;
        }
        
        if (error) {
            container.innerHTML = `
                <div class="error-state">
                    <h3>❌ Failed to Load Data</h3>
                    <p>${error}</p>
                    <button class="btn btn-primary" id="retryBtn">Retry</button>
                </div>
            `;
            
            this.querySelector('#retryBtn').addEventListener('click', () => this.refresh());
            return;
        }
        
        container.innerHTML = `
            <div class="data-header">
                <div>
                    <h3>📊 Live API Data</h3>
                    <p class="timestamp">Last updated: ${new Date(data.timestamp).toLocaleString()}</p>
                </div>
                <button class="btn btn-refresh" id="refreshBtn">🔄 Refresh</button>
            </div>
            
            <div class="data-sections">
                <div class="data-section">
                    <h4>📈 Statistics</h4>
                    <div class="json-display">
                        ${this.renderObject(data.stats)}
                    </div>
                </div>
                
                <div class="data-section">
                    <h4>🍪 Cookie Summary</h4>
                    <div class="json-display">
                        ${this.renderObject(data.cookies)}
                    </div>
                </div>
                
                <div class="data-section">
                    <h4>🌐 Request Information</h4>
                    <div class="json-display">
                        ${this.renderObject(data.request)}
                    </div>
                </div>
                
                <div class="data-section">
                    <h4>⚙️ Server Information</h4>
                    <div class="json-display">
                        ${this.renderObject(data.server)}
                    </div>
                </div>
            </div>
            
            <div class="data-section">
                <h4>📄 Raw JSON</h4>
                <div class="raw-json">
                    <pre><code>${JSON.stringify(data, null, 2)}</code></pre>
                </div>
            </div>
        `;
        
        const refreshBtn = this.querySelector('#refreshBtn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refresh());
        }
    }
}

customElements.define('api-data-viewer', APIDataViewer);
