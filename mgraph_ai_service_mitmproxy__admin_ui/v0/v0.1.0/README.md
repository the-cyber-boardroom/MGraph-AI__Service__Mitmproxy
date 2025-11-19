# Admin UI - Version 0.1

## Overview

This is the first iteration of the refactored MITM Proxy admin interface, following **Iterative Flow Development (IFD)** methodology.

## Key Features

✅ **Zero External Dependencies** - Pure HTML/CSS/JavaScript  
✅ **Web Components Architecture** - Modular, reusable components  
✅ **Event-Driven Communication** - Loose coupling between components  
✅ **Real Data Integration** - Uses actual cookies and browser APIs  
✅ **Production Ready** - Clean, maintainable code structure  

## Project Structure

```
v0.1/
├── index.html                    # Dashboard page
├── cookies.html                  # Cookie management page
├── 404.html                      # Error page
├── css/
│   ├── common.css               # Shared styles
│   ├── dashboard.css            # Dashboard-specific styles
│   └── cookies.css              # Cookies page styles
├── js/
│   ├── components/
│   │   ├── stats-card.js        # Statistics card component
│   │   ├── cookie-table.js      # Cookie table component
│   │   └── navigation.js        # Navigation links component
│   ├── services/
│   │   └── api-client.js        # API client service
│   ├── dashboard.js             # Dashboard page logic
│   └── cookies.js               # Cookies page logic
└── utils/
    └── dom-helpers.js           # DOM utility functions
```

## Components

### Stats Card (`stats-card`)
Displays a card with multiple statistics.

```javascript
const card = document.createElement('stats-card');
card.setData('Card Title', [
    { label: 'Stat 1', value: '100' },
    { label: 'Stat 2', value: '200' }
]);
```

### Cookie Table (`cookie-table`)
Displays active proxy cookies in table format.

```javascript
const table = document.createElement('cookie-table');
table.setData({
    'mitm-show': 'url-to-html',
    'mitm-debug': 'true'
});
```

### Navigation Links (`navigation-links`)
Displays admin navigation with badges.

```javascript
const nav = document.createElement('navigation-links');
nav.setData([
    { 
        href: '/page', 
        text: 'Link Text',
        badge: 'Badge Text',
        badgeType: 'info' 
    }
]);
```

## Services

### API Client
Handles cookie management and API communication.

```javascript
// Get proxy cookies
const cookies = window.apiClient.getProxyCookies();

// Set a cookie
window.apiClient.setCookie('mitm-show', 'url-to-html');

// Clear all proxy cookies
window.apiClient.clearAllProxyCookies();
```

## Integration with Python Backend

To serve these files from your FastAPI backend:

```python
from fastapi.staticfiles import StaticFiles

# Mount the admin UI
app.mount(
    "/mitm-proxy", 
    StaticFiles(directory="admin_ui/versions/v0.1", html=True), 
    name="admin"
)
```

Or update `Proxy__Admin__Service.py` to serve these HTML files instead of generating them inline.

## Browser Compatibility

- Modern browsers (Chrome, Firefox, Safari, Edge)
- Requires ES6+ support (Custom Elements)
- No polyfills needed for modern browsers

## Testing

Open in browser:
- Dashboard: `/mitm-proxy/` or `/mitm-proxy/index.html`
- Cookies: `/mitm-proxy/cookies.html`
- 404: `/mitm-proxy/nonexistent.html`

## Next Steps (v0.2)

Planned enhancements:
- [ ] Real-time stats updates via API
- [ ] WebSocket support for live data
- [ ] Cookie validation and error handling
- [ ] Export/import cookie configurations
- [ ] Dark mode theme

## IFD Principles Applied

✅ **UX-First Development** - Focus on user experience  
✅ **Real Data Integration** - Uses actual browser cookies  
✅ **Zero Dependencies** - Native web components only  
✅ **Progressive Enhancement** - Can be enhanced in future versions  
✅ **Version Independence** - Self-contained, no external dependencies  

---

**Created:** 2025-10-09  
**Methodology:** Iterative Flow Development (IFD)  
**Dependencies:** None (100% native web platform)
