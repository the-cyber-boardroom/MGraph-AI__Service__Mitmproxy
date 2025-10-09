// Navigation Links Component
// Displays admin navigation links with badges

class NavigationLinks extends HTMLElement {
    constructor() {
        super();
        this.state = {
            links: []
        };
    }

    connectedCallback() {
        this.render();
    }

    setData(links) {
        this.state.links = links;
        this.render();
    }

    render() {
        const { links } = this.state;
        
        const linksHTML = links.map(link => {
            const badgeHTML = link.badge ? 
                `<span class="badge badge-${link.badgeType || 'info'}">${link.badge}</span>` : '';
            
            return `
                <li>
                    <a href="${link.href}">
                        ${link.text}
                        ${badgeHTML}
                    </a>
                </li>
            `;
        }).join('');

        this.innerHTML = `
            <ul class="link-list">
                ${linksHTML}
            </ul>
        `;
    }
}

// Register the custom element
customElements.define('navigation-links', NavigationLinks);
