// Smart Cookie Form Component
// Main component that orchestrates all cookie form functionality

class CookieForm extends HTMLElement {
    constructor() {
        super();
        this.templateURL = './components/cookie-form/html/cookie-form.html';
        this.styleURL    = './components/cookie-form/css/cookie-form.css';
    }

    async connectedCallback() {
        await this.loadDependencies();
        await this.loadStyles();
        await this.loadTemplate();
        this.initialize();
    }

    async loadDependencies() {
        // Load all JavaScript dependencies
        const scripts = [ './components/cookie-form/js/cookie-definitions.js',
                          './components/cookie-form/js/form-builder.js'      ,
                          './components/cookie-form/js/message-handler.js'   ,
                          './components/cookie-form/js/event-handlers.js'    ];
        
        for (const src of scripts) {
            await this.loadScript(src);
        }
    }

    async loadScript(src) {
        return new Promise((resolve, reject) => {
            // Check if script already loaded
            if (document.querySelector(`script[src="${src}"]`)) {
                resolve();
                return;
            }
            
            const script = document.createElement('script');
            script.src = src;
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
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

    initialize() {
        // Initialize message handler
        const messageEl = this.querySelector('.form-message');
        this.messageHandler = new MessageHandler(messageEl);
        
        // Initialize event handlers
        this.eventHandlers = new CookieFormEventHandlers(this, this.messageHandler);
        
        // Populate cookie options
        this.populateCookieOptions();
        
        // Attach event listeners
        this.attachEventListeners();
    }

    populateCookieOptions() {
        const cookieNameSelect = this.querySelector('#cookieName');
        COOKIE_DEFINITIONS.forEach(def => {
            const option = document.createElement('option');
            option.value = def.name;
            option.textContent = def.name;
            cookieNameSelect.appendChild(option);
        });
    }

    attachEventListeners() {
        const form = this.querySelector('#cookieForm');
        const cookieNameSelect = this.querySelector('#cookieName');
        const clearAllBtn = this.querySelector('#clearAllBtn');
        
        form.addEventListener('submit', (e) => this.eventHandlers.handleSubmit(e));
        cookieNameSelect.addEventListener('change', (e) => 
            this.eventHandlers.handleCookieChange(e, COOKIE_DEFINITIONS)
        );
        clearAllBtn.addEventListener('click', () => this.eventHandlers.handleClearAll());
    }
}

customElements.define('cookie-form', CookieForm);
