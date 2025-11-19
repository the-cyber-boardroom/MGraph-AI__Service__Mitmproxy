// Top Navigation Component
// Shared navigation banner for all admin pages

class TopNav extends HTMLElement {
    constructor() {
        super();
        this.currentPath = window.location.pathname;
        this.templateURL = './components/top-nav/top-nav.html';
        this.styleURL    = './components/top-nav/top-nav.css';
    }

    async connectedCallback() {
        await this.loadStyles();
        await this.loadTemplate();
        this.setActiveLink();
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

    setActiveLink() {
        const links = this.querySelectorAll('.nav-links a');
        links.forEach(link => {
            const page = link.getAttribute('data-page');
            if (this.currentPath.includes(page)) {
                link.classList.add('active');
            }
        });
    }
}

customElements.define('top-nav', TopNav);