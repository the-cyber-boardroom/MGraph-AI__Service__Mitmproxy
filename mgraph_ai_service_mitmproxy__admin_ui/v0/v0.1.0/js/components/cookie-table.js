// Cookie Table Web Component
// Displays active proxy cookies in a table format

class CookieTable extends HTMLElement {
    constructor() {
        super();
        this.state = {
            cookies: {}
        };
    }

    connectedCallback() {
        this.render();
    }

    setData(cookies) {
        this.state.cookies = cookies || {};
        this.render();
    }

    render() {
        const { cookies } = this.state;
        
        if (Object.keys(cookies).length === 0) {
            this.innerHTML = '<div class="empty-state">No proxy cookies are currently active</div>';
            return;
        }

        const rows = Object.entries(cookies).map(([name, value]) => `
            <tr>
                <td><strong>${name}</strong></td>
                <td class="cookie-value">${value}</td>
            </tr>
        `).join('');

        this.innerHTML = `
            <table class="cookie-table">
                <thead>
                    <tr>
                        <th>Cookie Name</th>
                        <th>Value</th>
                    </tr>
                </thead>
                <tbody>
                    ${rows}
                </tbody>
            </table>
        `;
    }
}

// Register the custom element
customElements.define('cookie-table', CookieTable);
