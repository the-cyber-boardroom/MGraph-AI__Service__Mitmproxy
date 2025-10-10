// Event Handlers
// Handles all form events (submit, change, clear)

class CookieFormEventHandlers {
    constructor(component, messageHandler) {
        this.component = component;
        this.messageHandler = messageHandler;
    }
    
    // Handle form submission
    handleSubmit(e) {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const name = formData.get('cookieName');
        const value = formData.get('cookieValue');
        
        if (name && value) {
            // Set the cookie
            window.apiClient.setCookie(name, value);
            
            // Show success message
            this.messageHandler.success('Cookie set successfully! ✅');
            
            // Reset form
            e.target.reset();
            this.component.querySelector('#cookieValue').value = '';
            this.component.querySelector('#helpText').textContent = 'Select a cookie to configure';
        }
    }
    
    // Handle cookie selection change
    handleCookieChange(e, cookieDefinitions) {
        const selectedCookie = cookieDefinitions.find(
            def => def.name === e.target.value
        );
        
        const valueContainer = this.component.querySelector('#valueInputContainer');
        const helpText = this.component.querySelector('#helpText');
        
        if (!selectedCookie) {
            valueContainer.innerHTML = FormBuilder.buildInput(null);
            helpText.textContent = 'Select a cookie to configure';
            return;
        }
        
        // Update help text
        helpText.textContent = selectedCookie.description;
        
        // Build appropriate input
        const inputHTML = FormBuilder.buildInput(selectedCookie);
        valueContainer.innerHTML = inputHTML;
    }
    
    // Handle clear all button
    handleClearAll() {
        if (confirm('Are you sure you want to clear all proxy cookies?')) {
            window.apiClient.clearAllProxyCookies();
            this.messageHandler.success('All proxy cookies cleared! 🧹');
        }
    }
}
