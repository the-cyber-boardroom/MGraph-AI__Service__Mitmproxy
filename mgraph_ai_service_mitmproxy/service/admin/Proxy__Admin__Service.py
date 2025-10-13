import mgraph_ai_service_mitmproxy__admin_ui
from osbot_utils.type_safe.Type_Safe                                                                      import Type_Safe
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path                         import Safe_Str__File__Path
from osbot_utils.type_safe.primitives.domains.http.safe_str.Safe_Str__Http__Content_Type                  import Safe_Str__Http__Content_Type
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Version                           import Safe_Str__Version
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text                              import Safe_Str__Text
from pathlib                                                                                              import Path
from datetime                                                                                             import datetime
from typing                                                                                               import Dict, Optional
from mgraph_ai_service_mitmproxy.service.proxy.Proxy__Cookie__Service                                     import Proxy__Cookie__Service
from mgraph_ai_service_mitmproxy.service.proxy.Proxy__Stats__Service                                      import Proxy__Stats__Service


class Proxy__Admin__Service(Type_Safe):                                                                    # Admin UI static file server + JSON API
    cookie_service  : Proxy__Cookie__Service
    stats_service   : Proxy__Stats__Service
    current_version : Safe_Str__Version = Safe_Str__Version("v0.1.1")                                                           # Latest version
    admin_ui_root   : Path


    def setup(self):
        self.admin_ui_root = Path(mgraph_ai_service_mitmproxy__admin_ui.path)
        return self

    def is_admin_path(self, path: Safe_Str__File__Path) -> bool:                                          # Check if path is admin endpoint
        return str(path).startswith('/mitm-proxy')

    def handle_admin_request(self, request_data) -> Optional[Dict]:                                       # Main entry point: route admin requests
        path = request_data.path
        try:
            if path == '/mitm-proxy' or path == '/mitm-proxy/':                                               # Root redirect
                return self.redirect_to_latest()

            if path == '/mitm-proxy/admin-ui.json':                                                           # JSON API endpoint
                return self.serve_admin_data(request_data)

            if path.startswith('/mitm-proxy/'):                                                               # Static file serving
                return self.serve_static_file(path)
        except Exception as exception:
            print(exception)

        return None

    def redirect_to_latest(self) -> Dict:                                                                 # Redirect to latest version's index page
        redirect_url = Safe_Str__File__Path(f"/mitm-proxy/v0/{self.current_version}/index.html")            # todo: refactor to Safe_Str__Url__Path

        return { "status_code" : 302                                                                     ,
                 "body"        : f'<html><head><meta http-equiv="refresh" content="0; url={redirect_url}"></head></html>',
                 "headers"     : { "Location"     : str(redirect_url)                                    ,
                                   "content-type" : "text/html; charset=utf-8"                           }}

    def serve_static_file(self, path: Safe_Str__File__Path) -> Optional[Dict]:                           # Serve static files from admin_ui directory
        relative_path = Safe_Str__File__Path(str(path)[len('/mitm-proxy/'):])                            # Remove /mitm-proxy prefix
        file_path     = self.admin_ui_root / str(relative_path)                                           # Build full file path

        try:
            file_path = file_path.resolve()                                                               # Security check
            if not str(file_path).startswith(str(self.admin_ui_root.resolve())):
                return self.serve_404(path)
        except:
            return self.serve_404(path)

        if not file_path.exists() or not file_path.is_file():                                             # Check if file exists
            return self.serve_404(path)

        try:
            content = file_path.read_text(encoding='utf-8')                                               # Read file content
        except:
            try:
                content = file_path.read_bytes()                                                          # Fallback to binary
            except:
                return self.serve_404(path)

        content_type = self.get_content_type(file_path.suffix)                                            # Determine content type

        return { "status_code" : 200                                                                     ,
                 "body"        : content                                                                 ,
                 "headers"     : { "content-type"  : str(content_type)                                   ,
                                   "cache-control" : "no-cache"                                          }}  # Dev mode, no caching

    def serve_admin_data(self, request_data) -> Dict:                                                     # JSON API endpoint for admin UI
        stats          = self.stats_service.get_stats()
        cookies        = self.cookie_service.get_proxy_cookies(request_data.headers)
        cookie_summary = self.cookie_service.get_cookie_summary(request_data.headers)

        data = { "stats"     : stats                                                                     ,
                 "cookies"   : { "active"  : cookies                                                     ,
                                 "count"   : len(cookies)                                                ,
                                 "summary" : cookie_summary                                              },
                 "request"   : { "host"    : request_data.host                                           ,
                                 "path"    : request_data.path                                           ,
                                 "method"  : request_data.method                                         ,
                                 "headers" : dict(request_data.headers)                                  },
                 "server"    : { "version"            : "1.0.0"                                          ,
                                 "current_ui_version" : str(self.current_version)                        },
                 "timestamp" : datetime.utcnow().isoformat() + "Z"                                       }

        import json
        return { "status_code" : 200                                                                     ,
                 "body"        : json.dumps(data, indent=2)                                              ,
                 "headers"     : { "content-type"  : "application/json; charset=utf-8"                   ,
                                   "cache-control" : "no-cache"                                          }}

    def serve_404(self, path: Safe_Str__File__Path) -> Dict:                                             # Serve 404 for missing files
        custom_404_path = self.admin_ui_root / "v0" / str(self.current_version) / "404.html"

        if custom_404_path.exists():
            content = custom_404_path.read_text(encoding='utf-8')
        else:
            content = f"""<!DOCTYPE html>
<html>
<head><title>404 Not Found</title></head>
<body>
    <h1>404 - Not Found</h1>
    <p>The requested path <code>{path}</code> was not found.</p>
    <a href="/mitm-proxy">← Back to Dashboard</a>
</body>
</html>"""

        return { "status_code" : 404                                                                     ,
                 "body"        : content                                                                 ,
                 "headers"     : { "content-type" : "text/html; charset=utf-8"                           }}

    def get_content_type(self, suffix: Safe_Str__Text) -> Safe_Str__Http__Content_Type:                  # Map file extensions to content types
        content_types = { '.html' : 'text/html; charset=utf-8'                                           ,
                          '.css'  : 'text/css; charset=utf-8'                                            ,
                          '.js'   : 'application/javascript; charset=utf-8'                              ,
                          '.json' : 'application/json; charset=utf-8'                                    ,
                          '.png'  : 'image/png'                                                          ,
                          '.jpg'  : 'image/jpeg'                                                         ,
                          '.jpeg' : 'image/jpeg'                                                         ,
                          '.gif'  : 'image/gif'                                                          ,
                          '.svg'  : 'image/svg+xml'                                                      ,
                          '.ico'  : 'image/x-icon'                                                       ,
                          '.txt'  : 'text/plain; charset=utf-8'                                          ,
                          '.md'   : 'text/markdown; charset=utf-8'                                       }

        return Safe_Str__Http__Content_Type(content_types.get(str(suffix).lower(), 'application/octet-stream'))