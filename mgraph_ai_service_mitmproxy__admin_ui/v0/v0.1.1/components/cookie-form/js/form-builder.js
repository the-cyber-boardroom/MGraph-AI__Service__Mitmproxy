// Form Builder
// Handles dynamic form input generation based on cookie type

class FormBuilder {
    
    // Build select dropdown
    static buildSelectInput(definition) {
        const options = definition.options.map(opt => 
            `<option value="${opt.value}">${opt.label}</option>`
        ).join('');
        
        return `
            <select id="cookieValue" name="cookieValue" required>
                <option value="">-- Select Value --</option>
                ${options}
            </select>
        `;
    }
    
    // Build number input
    static buildNumberInput(definition) {
        return `
            <input type="number" 
                   id="cookieValue" 
                   name="cookieValue" 
                   placeholder="${definition.placeholder || ''}"
                   min="${definition.min || ''}"
                   max="${definition.max || ''}"
                   step="${definition.step || 'any'}"
                   required>
        `;
    }
    
    // Build text input
    static buildTextInput(definition) {
        return `
            <input type="text" 
                   id="cookieValue" 
                   name="cookieValue" 
                   placeholder="${definition.placeholder || 'Enter value...'}"
                   required>
        `;
    }
    
    // Build appropriate input based on type
    static buildInput(definition) {
        if (!definition) {
            return '<input type="text" id="cookieValue" name="cookieValue" placeholder="Enter value..." required>';
        }
        
        switch (definition.type) {
            case 'select':
                return this.buildSelectInput(definition);
            case 'number':
                return this.buildNumberInput(definition);
            case 'text':
            default:
                return this.buildTextInput(definition);
        }
    }
}
