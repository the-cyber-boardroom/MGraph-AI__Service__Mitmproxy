from osbot_utils.type_safe.Type_Safe                                                 import Type_Safe
from mgraph_ai_service_mitmproxy.schemas.proxy.Schema__Proxy__Request_Data           import Schema__Proxy__Request_Data
from mgraph_ai_service_mitmproxy.service.proxy.Proxy__Cookie__Service                import Proxy__Cookie__Service
from mgraph_ai_service_mitmproxy.service.proxy.Proxy__Stats__Service                 import Proxy__Stats__Service
from datetime                                                                        import datetime
from typing                                                                          import Dict, Optional


class Proxy__Admin__Service(Type_Safe):                          # Admin page generation service
    cookie_service : Proxy__Cookie__Service                      # Cookie parsing and management
    stats_service  : Proxy__Stats__Service                       # Statistics tracking

    def is_admin_path(self, path : str                           # Check if path is admin endpoint
                      ) -> bool:                                 # Is admin path
        return path.startswith('/mitm-proxy')

    def get_admin_endpoint(self, path : str                      # Extract admin endpoint name
                           ) -> Optional[str]:                   # Endpoint name or None
        if not self.is_admin_path(path):
            return None

        # Remove /mitm-proxy prefix
        endpoint = path[len('/mitm-proxy'):]

        # Remove leading slash and trailing slash
        endpoint = endpoint.strip('/')

        # Return 'index' for empty endpoint
        return endpoint if endpoint else 'index'

    def generate_admin_page(self,
                           request_data : Schema__Proxy__Request_Data,  # Request context
                           endpoint     : str                    # Admin endpoint name
                           ) -> Optional[Dict]:                  # Cached response dict or None
        endpoint_handlers = {
            'index'   : self.generate_dashboard_page,
            'cookies' : self.generate_cookies_page,
        }

        handler = endpoint_handlers.get(endpoint)
        if not handler:
            return self.generate_404_page(request_data, endpoint)

        html_content = handler(request_data)

        return {
            "status_code": 200,
            "body": html_content,
            "headers": {
                "content-type": "text/html; charset=utf-8",
                "x-admin-page": endpoint,
                "x-generated-at": datetime.utcnow().isoformat()
            }
        }

    def generate_dashboard_page(self,
                               request_data : Schema__Proxy__Request_Data  # Request context
                               ) -> str:                         # HTML content
        # Get current context
        host         = request_data.host
        path         = request_data.path
        stats        = self.stats_service.get_stats()
        cookies      = self.cookie_service.get_proxy_cookies(request_data.headers)
        cookie_count = len(cookies)

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MITM Proxy Dashboard - {host}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        .header {{
            background: white;
            border-radius: 10px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        h1 {{
            color: #667eea;
            font-size: 2em;
            margin-bottom: 10px;
        }}
        
        .subtitle {{
            color: #666;
            font-size: 1.1em;
        }}
        
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        
        .card {{
            background: white;
            border-radius: 10px;
            padding: 25px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }}
        
        .card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        }}
        
        .card-title {{
            font-size: 1.2em;
            color: #333;
            margin-bottom: 15px;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
        
        .stat {{
            display: flex;
            justify-content: space-between;
            margin: 10px 0;
            padding: 8px;
            background: #f7f7f7;
            border-radius: 5px;
        }}
        
        .stat-label {{
            color: #666;
            font-weight: 500;
        }}
        
        .stat-value {{
            color: #667eea;
            font-weight: bold;
        }}
        
        .nav-links {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        .nav-links h2 {{
            color: #667eea;
            margin-bottom: 15px;
        }}
        
        .link-list {{
            list-style: none;
        }}
        
        .link-list li {{
            margin: 10px 0;
        }}
        
        .link-list a {{
            color: #667eea;
            text-decoration: none;
            font-size: 1.1em;
            display: flex;
            align-items: center;
            padding: 10px;
            border-radius: 5px;
            transition: background 0.2s;
        }}
        
        .link-list a:hover {{
            background: #f0f0f0;
        }}
        
        .link-list a::before {{
            content: "→";
            margin-right: 10px;
            font-weight: bold;
        }}
        
        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: bold;
            margin-left: 10px;
        }}
        
        .badge-success {{
            background: #10b981;
            color: white;
        }}
        
        .badge-info {{
            background: #3b82f6;
            color: white;
        }}
        
        .badge-warning {{
            background: #f59e0b;
            color: white;
        }}
        
        .footer {{
            text-align: center;
            color: white;
            margin-top: 30px;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔧 MITM Proxy Dashboard</h1>
            <p class="subtitle">Managing proxy for: <strong>{host}</strong></p>
        </div>
        
        <div class="grid">
            <div class="card">
                <div class="card-title">📊 Proxy Statistics</div>
                <div class="stat">
                    <span class="stat-label">Total Requests</span>
                    <span class="stat-value">{stats.get('total_requests', 0)}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Total Responses</span>
                    <span class="stat-value">{stats.get('total_responses', 0)}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Bytes Processed</span>
                    <span class="stat-value">{stats.get('total_bytes_processed', 0):,}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Content Modifications</span>
                    <span class="stat-value">{stats.get('content_modifications', 0)}</span>
                </div>
            </div>
            
            <div class="card">
                <div class="card-title">🍪 Cookie Status</div>
                <div class="stat">
                    <span class="stat-label">Active Proxy Cookies</span>
                    <span class="stat-value">{cookie_count}</span>
                </div>
                <div style="margin-top: 15px;">
                    {self._format_cookie_list(cookies)}
                </div>
            </div>
            
            <div class="card">
                <div class="card-title">🌐 Current Request</div>
                <div class="stat">
                    <span class="stat-label">Host</span>
                    <span class="stat-value">{host}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Method</span>
                    <span class="stat-value">{request_data.method}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Path</span>
                    <span class="stat-value">{path}</span>
                </div>
            </div>
        </div>
        
        <div class="nav-links">
            <h2>🔗 Admin Pages</h2>
            <ul class="link-list">
                <li><a href="/mitm-proxy/cookies">Cookie Management <span class="badge badge-info">{cookie_count} active</span></a></li>
                <li><a href="/mitm-proxy/site-info">Site Information <span class="badge badge-success">Coming Soon</span></a></li>
                <li><a href="/mitm-proxy/stats">Detailed Statistics <span class="badge badge-success">Coming Soon</span></a></li>
                <li><a href="/mitm-proxy/settings">Proxy Settings <span class="badge badge-success">Coming Soon</span></a></li>
            </ul>
        </div>
        
        <div class="footer">
            <p>MITM Proxy Admin Interface | Generated at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</p>
        </div>
    </div>
</body>
</html>"""
        return html

    def generate_cookies_page(self,
                             request_data : Schema__Proxy__Request_Data  # Request context
                             ) -> str:                           # HTML content
        host    = request_data.host
        cookies = self.cookie_service.get_proxy_cookies(request_data.headers)

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cookie Management - {host}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        .header {{
            background: white;
            border-radius: 10px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        h1 {{
            color: #667eea;
            font-size: 2em;
            margin-bottom: 10px;
        }}
        
        .subtitle {{
            color: #666;
            font-size: 1.1em;
        }}
        
        .back-link {{
            display: inline-block;
            margin-bottom: 15px;
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
        }}
        
        .back-link:hover {{
            text-decoration: underline;
        }}
        
        .card {{
            background: white;
            border-radius: 10px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        .card-title {{
            font-size: 1.4em;
            color: #333;
            margin-bottom: 20px;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
        
        .cookie-table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }}
        
        .cookie-table th {{
            background: #667eea;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }}
        
        .cookie-table td {{
            padding: 12px;
            border-bottom: 1px solid #ddd;
        }}
        
        .cookie-table tr:hover {{
            background: #f7f7f7;
        }}
        
        .cookie-value {{
            font-family: 'Courier New', monospace;
            color: #764ba2;
            font-weight: 500;
        }}
        
        .empty-state {{
            text-align: center;
            padding: 40px;
            color: #999;
            font-size: 1.1em;
        }}
        
        .form-group {{
            margin-bottom: 20px;
        }}
        
        .form-group label {{
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 600;
        }}
        
        .form-group input,
        .form-group select {{
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 5px;
            font-size: 1em;
            transition: border-color 0.2s;
        }}
        
        .form-group input:focus,
        .form-group select:focus {{
            outline: none;
            border-color: #667eea;
        }}
        
        .form-row {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }}
        
        .btn {{
            padding: 12px 30px;
            border: none;
            border-radius: 5px;
            font-size: 1em;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        .btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }}
        
        .btn-primary {{
            background: #667eea;
            color: white;
        }}
        
        .btn-secondary {{
            background: #6c757d;
            color: white;
        }}
        
        .help-text {{
            font-size: 0.9em;
            color: #666;
            margin-top: 5px;
        }}
        
        .info-box {{
            background: #e7f3ff;
            border-left: 4px solid #3b82f6;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 5px;
        }}
        
        .info-box h3 {{
            color: #3b82f6;
            margin-bottom: 10px;
        }}
        
        .info-box ul {{
            margin-left: 20px;
        }}
        
        .info-box li {{
            margin: 5px 0;
            color: #333;
        }}
        
        .code {{
            background: #f5f5f5;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            color: #764ba2;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <a href="/mitm-proxy/" class="back-link">← Back to Dashboard</a>
            <h1>🍪 Cookie Management</h1>
            <p class="subtitle">Control proxy behavior via cookies for: <strong>{host}</strong></p>
        </div>
        
        <div class="card">
            <div class="card-title">Currently Active Proxy Cookies</div>
            {self._format_active_cookies_table(cookies)}
        </div>
        
        <div class="card">
            <div class="card-title">Set New Proxy Cookie</div>
            
            <div class="info-box">
                <h3>Available Cookie Controls</h3>
                <ul>
                    <li><span class="code">mitm-show</span> - Control content display (url-to-html, url-to-html-xxx, url-to-ratings, response-data)</li>
                    <li><span class="code">mitm-inject</span> - Inject debug content (debug-panel, debug-banner)</li>
                    <li><span class="code">mitm-replace</span> - Replace text (format: old:new)</li>
                    <li><span class="code">mitm-debug</span> - Enable debug mode (true/false)</li>
                    <li><span class="code">mitm-rating</span> - Set minimum rating for filtering (e.g., 0.5)</li>
                    <li><span class="code">mitm-model</span> - Override WCF model to use</li>
                    <li><span class="code">mitm-cache</span> - Enable response caching (true/false)</li>
                </ul>
            </div>
            
            <form id="cookieForm">
                <div class="form-row">
                    <div class="form-group">
                        <label for="cookieName">Cookie Name</label>
                        <select id="cookieName" name="cookieName" required>
                            <option value="">-- Select Cookie --</option>
                            <option value="mitm-show">mitm-show</option>
                            <option value="mitm-inject">mitm-inject</option>
                            <option value="mitm-replace">mitm-replace</option>
                            <option value="mitm-debug">mitm-debug</option>
                            <option value="mitm-rating">mitm-rating</option>
                            <option value="mitm-model">mitm-model</option>
                            <option value="mitm-cache">mitm-cache</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="cookieValue">Cookie Value</label>
                        <input type="text" id="cookieValue" name="cookieValue" 
                               placeholder="Enter value..." required>
                        <div class="help-text" id="helpText">Select a cookie to see suggested values</div>
                    </div>
                </div>
                
                <div class="form-group">
                    <button type="submit" class="btn btn-primary">Set Cookie & Reload</button>
                    <button type="button" class="btn btn-secondary" onclick="clearAllCookies()">Clear All Proxy Cookies</button>
                </div>
            </form>
        </div>
    </div>
    
    <script>
        const cookieHelp = {{
            'mitm-show': 'Examples: url-to-html, url-to-html-xxx, url-to-ratings, response-data',
            'mitm-inject': 'Examples: debug-panel, debug-banner',
            'mitm-replace': 'Format: oldtext:newtext',
            'mitm-debug': 'Values: true or false',
            'mitm-rating': 'Example: 0.5 (minimum rating threshold)',
            'mitm-model': 'Example: google/gemini-2.0-flash-lite-001',
            'mitm-cache': 'Values: true or false'
        }};
        
        document.getElementById('cookieName').addEventListener('change', function() {{
            const helpText = document.getElementById('helpText');
            helpText.textContent = cookieHelp[this.value] || 'Select a cookie to see suggested values';
        }});
        
        document.getElementById('cookieForm').addEventListener('submit', function(e) {{
            e.preventDefault();
            const name = document.getElementById('cookieName').value;
            const value = document.getElementById('cookieValue').value;
            
            // Set cookie
            document.cookie = name + '=' + value + '; path=/; max-age=3600';
            
            // Reload to parent page
            window.location.href = '/mitm-proxy/cookies';
        }});
        
        function clearAllCookies() {{
            const cookies = ['mitm-show', 'mitm-inject', 'mitm-replace', 'mitm-debug', 
                           'mitm-rating', 'mitm-model', 'mitm-cache'];
            
            cookies.forEach(cookie => {{
                document.cookie = cookie + '=; path=/; max-age=0';
            }});
            
            window.location.reload();
        }}
    </script>
</body>
</html>"""
        return html

    def generate_404_page(self,
                         request_data : Schema__Proxy__Request_Data,  # Request context
                         endpoint     : str                    # Requested endpoint
                         ) -> Dict:                            # Cached response dict
        host = request_data.host

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Page Not Found - {host}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }}
        
        .error-container {{
            background: white;
            border-radius: 10px;
            padding: 50px;
            text-align: center;
            max-width: 600px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        .error-code {{
            font-size: 6em;
            color: #667eea;
            font-weight: bold;
            margin: 0;
        }}
        
        h1 {{
            color: #333;
            margin: 20px 0;
        }}
        
        p {{
            color: #666;
            font-size: 1.1em;
            margin: 20px 0;
        }}
        
        .back-link {{
            display: inline-block;
            margin-top: 30px;
            padding: 12px 30px;
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            font-weight: 600;
            transition: transform 0.2s;
        }}
        
        .back-link:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }}
    </style>
</head>
<body>
    <div class="error-container">
        <div class="error-code">404</div>
        <h1>Admin Page Not Found</h1>
        <p>The admin endpoint <strong>/{endpoint}</strong> does not exist.</p>
        <a href="/mitm-proxy/" class="back-link">← Return to Dashboard</a>
    </div>
</body>
</html>"""

        return {
            "status_code": 404,
            "body": html,
            "headers": {
                "content-type": "text/html; charset=utf-8",
                "x-admin-page": "error-404"
            }
        }

    def _format_cookie_list(self, cookies : Dict[str, str]      # Format cookie list for dashboard
                            ) -> str:                            # HTML fragment
        if not cookies:
            return '<p style="color: #999; font-style: italic;">No proxy cookies active</p>'

        items = []
        for name, value in cookies.items():
            items.append(f'<div style="padding: 8px; background: #f7f7f7; border-radius: 5px; margin: 5px 0;">'
                        f'<strong>{name}:</strong> <code>{value}</code></div>')

        return '\n'.join(items)

    def _format_active_cookies_table(self, cookies : Dict[str, str]  # Format cookies as table
                                     ) -> str:                   # HTML fragment
        if not cookies:
            return '<div class="empty-state">No proxy cookies are currently active</div>'

        rows = []
        for name, value in cookies.items():
            rows.append(f'<tr><td><strong>{name}</strong></td><td class="cookie-value">{value}</td></tr>')

        return f'''<table class="cookie-table">
            <thead>
                <tr>
                    <th>Cookie Name</th>
                    <th>Value</th>
                </tr>
            </thead>
            <tbody>
                {''.join(rows)}
            </tbody>
        </table>'''