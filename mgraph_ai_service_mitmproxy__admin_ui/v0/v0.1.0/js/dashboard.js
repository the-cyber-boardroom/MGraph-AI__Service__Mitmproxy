// Dashboard Main Application
// Orchestrates the dashboard page components and data

document.addEventListener('DOMContentLoaded', () => {
    // Initialize components
    const statsGrid = document.getElementById('stats-grid');
    const navLinks = document.getElementById('nav-links');
    const hostName = document.getElementById('host-name');
    const timestamp = document.getElementById('timestamp');

    // Get request context
    const context = window.apiClient.getRequestContext();
    
    // Update host name
    hostName.textContent = context.host;
    
    // Update timestamp
    const now = new Date();
    timestamp.textContent = now.toISOString().replace('T', ' ').split('.')[0];

    // Mock stats data (in production, this would come from API)
    // The Python service will inject this data or we can fetch it
    const stats = {
        total_requests: 0,
        total_responses: 0,
        total_bytes_processed: 0,
        content_modifications: 0
    };

    // Get cookies
    const cookies = window.apiClient.getProxyCookies();
    const cookieCount = Object.keys(cookies).length;

    // Create Proxy Statistics Card
    const proxyStatsCard = document.createElement('stats-card');
    proxyStatsCard.setData('📊 Proxy Statistics', [
        { label: 'Total Requests', value: stats.total_requests },
        { label: 'Total Responses', value: stats.total_responses },
        { label: 'Bytes Processed', value: stats.total_bytes_processed.toLocaleString() },
        { label: 'Content Modifications', value: stats.content_modifications }
    ]);
    statsGrid.appendChild(proxyStatsCard);

    // Create Cookie Status Card
    const cookieStatsCard = document.createElement('stats-card');
    const cookieStats = [
        { label: 'Active Proxy Cookies', value: cookieCount }
    ];
    
    // Format cookie list
    if (cookieCount > 0) {
        Object.entries(cookies).forEach(([name, value]) => {
            cookieStats.push({ 
                label: name, 
                value: `<code>${value}</code>` 
            });
        });
    }
    
    cookieStatsCard.setData('🍪 Cookie Status', cookieStats);
    statsGrid.appendChild(cookieStatsCard);

    // Create Current Request Card
    const requestCard = document.createElement('stats-card');
    requestCard.setData('🌐 Current Request', [
        { label: 'Host', value: context.host },
        { label: 'Method', value: 'GET' },
        { label: 'Path', value: context.path }
    ]);
    statsGrid.appendChild(requestCard);

    // Create navigation links
    const navLinksComponent = document.createElement('navigation-links');
    navLinksComponent.setData([
        {
            href: './cookies.html',
            text: 'Cookie Management',
            badge: `${cookieCount} active`,
            badgeType: 'info'
        },
        {
            href: './mitm-proxy/site-info',
            text: 'Site Information',
            badge: 'Coming Soon',
            badgeType: 'success'
        },
        {
            href: './mitm-proxy/stats',
            text: 'Detailed Statistics',
            badge: 'Coming Soon',
            badgeType: 'success'
        },
        {
            href: './mitm-proxy/settings',
            text: 'Proxy Settings',
            badge: 'Coming Soon',
            badgeType: 'success'
        }
    ]);
    navLinks.appendChild(navLinksComponent);
});
