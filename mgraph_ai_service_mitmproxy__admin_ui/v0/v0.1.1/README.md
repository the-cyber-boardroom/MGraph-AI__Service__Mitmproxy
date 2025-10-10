# Admin UI - Version 0.1.1

## Overview

Version 0.1.1 is an iterative enhancement of v0.1.0, following **Iterative Flow Development (IFD)** methodology. This version focuses on improved navigation, real-time updates, and better user experience.

## What's New in v0.1.1

### ✨ New Features

1. **Top Navigation Banner**
   - Consistent navigation across all pages
   - Active page highlighting
   - Quick access to all admin sections

2. **API Data Viewer Page**
   - Live data from `/mitm-proxy/admin-ui.json`
   - Formatted JSON display with syntax highlighting
   - Real-time refresh capability
   - Organized by sections (Stats, Cookies, Request, Server)

3. **Enhanced Cookie Management**
   - Smart form inputs based on cookie type
   - No page reload required for cookie changes
   - Individual cookie deletion
   - Real-time cookie table updates
   - Better UX with dropdowns for predefined values

4. **Real Data Integration**
   - Dashboard loads actual stats from API
   - Dynamic host and timestamp display
   - Live cookie synchronization

### 🎯 Key Improvements

**Navigation**
- Unified top banner navigation component
- Active page state indication
- Seamless page transitions

**Cookie Management**
- Delete individual cookies without reload
- Smart form inputs (select dropdowns for mitm-show, mitm-debug, etc.)
- Real-time updates via event system
- Success/error messaging
- No more manual page reloads

**Architecture**
- Modular component structure
- Event-driven communication
- Shared API client service
- Better separation of concerns

## Project Structure

```
v0.1.1/
├── index.html                    # Dashboard page
├── cookies.html                  # Cookie management page
├── api-data.html                 # API data viewer page (NEW)
├── 404.html                      # Error page
├── README.md                     # This file
├── css/
│   ├── common.css               # Shared styles
│   ├── dashboard.css            # Dashboard-specific styles
│   ├── cookies.css              # Cookies page styles
│   └── error.css                # Error page styles
├── components/
│   ├── top-nav/                 # Navigation component (flat)
│   │   ├── top-nav.html
│   │   ├── top-nav.css
│   │   └── top-nav.js
│   ├── cookie-table/            # Cookie table component (flat)
│   │   ├── cookie-table.html
│   │   ├── cookie-table.css
│   │   └── cookie-table.js
│   ├── cookie-form/             # Cookie form component (modular)
│   │   ├── cookie-form.js       # Main orchestrator
│   │   ├── html/
│   │   │   └── cookie-form.html
│   │   ├── css/
│   │   │   └── cookie-form.css
│   │   └── js/
│   │       ├── cookie-definitions.js  # Cookie config data
│   │       ├── form-builder.js        # Dynamic form generation
│   │       ├── message-handler.js     # Success/error messages
│   │       └── event-handlers.js      # Event handling logic
│   └── api-data-viewer/         # API viewer component (flat)
│       ├── api-data-viewer.html
│       ├── api-data-viewer.css
│       └── api-data-viewer.js
└── js/
    └── services/
        └── api-client.js        # API client + event system
```

### Structure Philosophy

**Simple components** (top-nav, cookie-table, api-data-viewer):
- Flat structure with 3 files (HTML, CSS, JS)
- Perfect for components that rarely change
- Easy to understand and copy

**Complex components** (cookie-form):
- Organized with subfolders (html/, css/, js/)
- Multiple JS modules for different responsibilities
- Easy to update specific parts in future versions
- Ideal for components with frequent updates

## Components

### Component Architecture

v0.1.1 uses a **hybrid structure** - simple components use a flat structure, while complex components use subfolders for better organization.

### Top Navigation (`top-nav`)
Shared navigation banner across all pages.

**Structure**: Flat (3 files)
```
components/top-nav/
├── top-nav.html
├── top-nav.css
└── top-nav.js
```

```html
<top-nav></top-nav>
```

Features:
- Automatic active page detection
- Responsive design
- Gradient background matching site theme

### Cookie Table (`cookie-table`)
Enhanced table with real-time updates and delete functionality.

**Structure**: Flat (3 files)
```
components/cookie-table/
├── cookie-table.html
├── cookie-table.css
└── cookie-table.js
```

Usage:

```javascript
const table = document.getElementById('cookie-table');
table.setData(cookies); // Updates automatically on cookie changes
```

Features:
- Individual delete buttons
- Real-time synchronization
- Event-driven updates

### Cookie Form (`cookie-form`)
Smart form with dynamic input controls and modular architecture.

**Structure**: Modular (7 files organized in subfolders)
```
components/cookie-form/
├── cookie-form.js              # Main orchestrator
├── html/
│   └── cookie-form.html        # Form template
├── css/
│   └── cookie-form.css         # Form styles
└── js/
    ├── cookie-definitions.js   # Cookie configuration data
    ├── form-builder.js         # Dynamic form input generation
    ├── message-handler.js      # Success/error messaging
    └── event-handlers.js       # Event handling logic
```

**Why modular?** This component is complex and benefits from separation:
- **cookie-definitions.js** - Easy to add new cookies in v0.1.2
- **form-builder.js** - Easy to add new input types
- **message-handler.js** - Easy to customize messaging
- **event-handlers.js** - Easy to modify behavior

Usage:

```html
<cookie-form></cookie-form>
```

Features:
- Select dropdowns for predefined values (mitm-show, mitm-debug, etc.)
- Text inputs with placeholders
- Number inputs with min/max/step
- No page reload on submit
- Success/error messaging

### API Data Viewer (`api-data-viewer`)
Displays formatted JSON from `/mitm-proxy/admin-ui.json`.

**Structure**: Flat (3 files)
```
components/api-data-viewer/
├── api-data-viewer.html
├── api-data-viewer.css
└── api-data-viewer.js
```

Usage:

```html
<api-data-viewer></api-data-viewer>
```

Features:
- Syntax-highlighted JSON
- Organized by sections
- Refresh button
- Raw JSON view
- Loading and error states

## API Integration

### Fetching Real Data

The enhanced API client now fetches real data:

```javascript
const apiData = await window.apiClient.fetchAPIData();
// Returns: { stats, cookies, request, server, timestamp }
```

### Real-Time Cookie Updates

No page reloads needed:

```javascript
// Set cookie
window.apiClient.setCookie('mitm-show', 'url-to-html-xxx');
// Cookie table updates automatically

// Delete cookie
window.apiClient.clearCookie('mitm-show');
// Cookie table updates automatically

// Listen for changes
window.apiClient.on('cookie-changed', (e) => {
    console.log('Cookie changed:', e.detail);
});
```

## Usage

### Setting Cookies (Improved UX)

1. Navigate to Cookie Management page
2. Select cookie from dropdown (e.g., "mitm-show")
3. Form automatically shows appropriate input:
   - **mitm-show**: Dropdown with predefined options
   - **mitm-debug**: Dropdown (true/false)
   - **mitm-rating**: Number input (0-1, step 0.1)
   - **mitm-replace**: Text input (old:new format)
   - **mitm-model**: Text input with placeholder
4. Click "Set Cookie" - no reload needed!
5. See cookie appear in table immediately

### Deleting Cookies

1. Find cookie in "Currently Active Proxy Cookies" table
2. Click "🗑️ Delete" button next to cookie
3. Confirm deletion
4. Cookie disappears immediately - no reload!

### Viewing API Data

1. Navigate to "API Data" page from top nav
2. View formatted sections (Stats, Cookies, Request, Server)
3. Click "🔄 Refresh" to reload latest data
4. Scroll down to see raw JSON

## Browser Compatibility

- Modern browsers (Chrome, Firefox, Safari, Edge)
- Requires ES6+ support (async/await, Custom Elements)
- No polyfills needed for modern browsers

## IFD Principles Applied

✅ **Modular Components** - Each component is self-contained  
✅ **Event-Driven** - Real-time updates without page reloads  
✅ **Real Data From Day One** - Uses actual `/mitm-proxy/admin-ui.json`  
✅ **Progressive Enhancement** - Built on v0.1.0 foundation  
✅ **Zero Dependencies** - Pure native web platform  
✅ **Version Independence** - Completely self-contained  

## Migration from v0.1.0

To update from v0.1.0:

1. Copy entire `v0.1.1` folder
2. Update your backend to serve from `v0.1.1` directory
3. Ensure `/mitm-proxy/admin-ui.json` endpoint exists
4. All existing functionality preserved + new features

No breaking changes - v0.1.1 is fully backward compatible.

## Next Steps (v0.1.2 ideas)

Potential enhancements:
- [ ] WebSocket support for real-time stats
- [ ] Cookie templates (save/load configurations)
- [ ] Dark mode toggle
- [ ] Search/filter in API data viewer
- [ ] Export API data as JSON/CSV
- [ ] Cookie validation and warnings
- [ ] Request history viewer

## Development Time

**Estimated**: 2-3 hours  
**Complexity**: Medium (5 components + 3 pages)  
**Status**: Production ready

---

**Created:** 2025-10-10  
**Methodology:** Iterative Flow Development (IFD)  
**Dependencies:** None (100% native web platform)  
**Previous Version:** v0.1.0  
**Major Changes:** Top nav, API viewer, real-time cookie updates, smart forms