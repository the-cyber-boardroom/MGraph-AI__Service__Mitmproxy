// Stats Card Web Component
// Displays a statistics card with multiple stat items

class StatsCard extends HTMLElement {
    constructor() {
        super();
        this.state = {
            title: '',
            stats: []
        };
    }

    connectedCallback() {
        this.render();
    }

    setData(title, stats) {
        this.state.title = title;
        this.state.stats = stats;
        this.render();
    }

    render() {
        const { title, stats } = this.state;
        
        const statsHTML = stats.map(stat => `
            <div class="stat">
                <span class="stat-label">${stat.label}</span>
                <span class="stat-value">${stat.value}</span>
            </div>
        `).join('');

        this.innerHTML = `
            <div class="card">
                <div class="card-title">${title}</div>
                ${statsHTML}
            </div>
        `;
    }
}

// Register the custom element
customElements.define('stats-card', StatsCard);
