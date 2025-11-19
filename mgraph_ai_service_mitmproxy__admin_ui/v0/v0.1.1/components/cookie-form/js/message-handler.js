// Message Handler
// Displays success/error messages to the user

class MessageHandler {
    constructor(messageElement) {
        this.messageElement = messageElement;
    }
    
    show(text, type = 'success') {
        if (!this.messageElement) return;
        
        this.messageElement.textContent = text;
        this.messageElement.className = `form-message ${type}`;
        this.messageElement.style.display = 'block';
        
        // Auto-hide after 3 seconds
        setTimeout(() => {
            this.hide();
        }, 3000);
    }
    
    hide() {
        if (this.messageElement) {
            this.messageElement.style.display = 'none';
        }
    }
    
    success(text) {
        this.show(text, 'success');
    }
    
    error(text) {
        this.show(text, 'error');
    }
}
