// Cookies Page Main Application
// Handles cookie management functionality

document.addEventListener('DOMContentLoaded', () => {
    // Initialize components
    const hostName = document.getElementById('host-name');
    const activeCookiesContainer = document.getElementById('active-cookies-container');
    const cookieControlsList = document.getElementById('cookie-controls-list');
    const cookieForm = document.getElementById('cookieForm');
    const cookieNameSelect = document.getElementById('cookieName');
    const cookieValueInput = document.getElementById('cookieValue');
    const helpText = document.getElementById('helpText');
    const clearAllBtn = document.getElementById('clearAllBtn');

    // Get request context
    const context = window.apiClient.getRequestContext();
    hostName.textContent = context.host;

    // Cookie definitions
    const cookieDefinitions = [
        {
            name: 'mitm-show',
            description: 'Control content display (url-to-html, url-to-html-xxx, url-to-ratings, response-data)',
            helpText: 'Examples: url-to-html, url-to-html-xxx, url-to-ratings, response-data'
        },
        {
            name: 'mitm-inject',
            description: 'Inject debug content (debug-panel, debug-banner)',
            helpText: 'Examples: debug-panel, debug-banner'
        },
        {
            name: 'mitm-replace',
            description: 'Replace text (format: old:new)',
            helpText: 'Format: oldtext:newtext'
        },
        {
            name: 'mitm-debug',
            description: 'Enable debug mode (true/false)',
            helpText: 'Values: true or false'
        },
        {
            name: 'mitm-rating',
            description: 'Set minimum rating for filtering (e.g., 0.5)',
            helpText: 'Example: 0.5 (minimum rating threshold)'
        },
        {
            name: 'mitm-model',
            description: 'Override WCF model to use',
            helpText: 'Example: google/gemini-2.0-flash-lite-001'
        },
        {
            name: 'mitm-cache',
            description: 'Enable response caching (true/false)',
            helpText: 'Values: true or false'
        }
    ];

    // Populate cookie definitions list
    cookieDefinitions.forEach(def => {
        const li = document.createElement('li');
        li.innerHTML = `<span class="code">${def.name}</span> - ${def.description}`;
        cookieControlsList.appendChild(li);
    });

    // Populate cookie select dropdown
    cookieDefinitions.forEach(def => {
        const option = document.createElement('option');
        option.value = def.name;
        option.textContent = def.name;
        cookieNameSelect.appendChild(option);
    });

    // Display active cookies
    const activeCookies = window.apiClient.getProxyCookies();
    const cookieTable = document.createElement('cookie-table');
    cookieTable.setData(activeCookies);
    activeCookiesContainer.appendChild(cookieTable);

    // Update help text when cookie selection changes
    cookieNameSelect.addEventListener('change', () => {
        const selectedCookie = cookieDefinitions.find(
            def => def.name === cookieNameSelect.value
        );
        
        if (selectedCookie) {
            helpText.textContent = selectedCookie.helpText;
        } else {
            helpText.textContent = 'Select a cookie to see suggested values';
        }
    });

    // Handle form submission
    cookieForm.addEventListener('submit', (e) => {
        e.preventDefault();
        
        const name = cookieNameSelect.value;
        const value = cookieValueInput.value;
        
        if (name && value) {
            // Set the cookie
            window.apiClient.setCookie(name, value);
            
            // Reload to cookies page to show updated state
            window.location.reload();
        }
    });

    // Handle clear all cookies button
    clearAllBtn.addEventListener('click', () => {
        if (confirm('Are you sure you want to clear all proxy cookies?')) {
            window.apiClient.clearAllProxyCookies();
            window.location.reload();
        }
    });
});
