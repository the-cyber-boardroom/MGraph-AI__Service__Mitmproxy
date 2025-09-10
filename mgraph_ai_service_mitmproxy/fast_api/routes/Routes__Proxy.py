from typing                                               import Dict, List, Any, Set, Optional
from datetime                                             import datetime
import json
from mgraph_ai_service_mitmproxy.utils.Version            import version__mgraph_ai_service_mitmproxy
from osbot_fast_api.api.routes.Fast_API__Routes           import Fast_API__Routes
from osbot_fast_api.utils.Version import version__osbot_fast_api
from osbot_utils.type_safe.Type_Safe                      import Type_Safe
from osbot_utils.type_safe.primitives.safe_str.Safe_Str   import Safe_Str
from osbot_utils.type_safe.primitives.safe_str.git.Safe_Str__Version import Safe_Str__Version
from osbot_utils.type_safe.primitives.safe_uint.Safe_UInt import Safe_UInt
from osbot_utils.utils.Dev import pprint

TAG__ROUTES_PROXY                  = 'proxy'
ROUTES_PATHS__PROXY                = [ f'/{TAG__ROUTES_PROXY}/process-request'  ,
                                       f'/{TAG__ROUTES_PROXY}/process-response' ,
                                       f'/{TAG__ROUTES_PROXY}/get-proxy-stats'  ,
                                       f'/{TAG__ROUTES_PROXY}/reset-proxy-stats']

# Domain-specific Safe types for proxy data
class Safe_Str__HTTP_Method(Safe_Str):                                        # HTTP method validation
    max_length = 10

class Safe_Str__Host(Safe_Str):                                           # Host/domain validation
    max_length = 255

class Safe_Str__Path(Safe_Str):                                           # URL path validation
    max_length = 2048

class Safe_UInt__HTTP_Status(Safe_UInt):                                  # HTTP status codes
    min_value = 100
    max_value = 599

# Request/Response schemas using Type_Safe
class Schema__Proxy__Request_Data(Type_Safe):                             # Incoming request from mitmproxy
    method        : Safe_Str__HTTP_Method                                 # HTTP method (GET, POST, etc)
    host          : Safe_Str__Host                                        # Target host
    path          : Safe_Str__Path                                        # Request path
    original_path : Optional[str] = None                                  # Original path with debug params
    debug_params  : Dict[str, str]                                        # Debug parameters extracted
    headers       : Dict[str, str]                                        # Request headers
    stats         : Dict[str, Any]                                        # Request statistics
    version       : Safe_Str__Version                                     # Interceptor version

class Schema__Proxy__Response_Data(Type_Safe):                            # Incoming response from mitmproxy
    request       : Dict[str, Any]                                        # Original request info
    debug_params  : Dict[str, str]                                        # Debug parameters from request
    response      : Dict[str, Any]                                        # Response details
    stats         : Dict[str, Any]                                        # Response statistics
    version       : Safe_Str__Version                                     # Interceptor version

class Schema__Proxy__Modifications(Type_Safe):                            # Modifications to apply
    headers_to_add    : Dict[str, str]                                    # Headers to add
    headers_to_remove : List[str]                                         # Headers to remove
    block_request     : bool            = False                           # Whether to block request
    block_status      : Safe_UInt__HTTP_Status = 403                      # Status code if blocked
    block_message     : Safe_Str        = "Blocked by proxy"              # Block message
    include_stats     : bool            = False                           # Include stats in response
    stats             : Dict[str, Any]                                    # Statistics to include
    modified_body     : Optional[str]   = None                            # Modified body content (if any)
    override_response : bool            = False                           # Whether to completely override response
    override_status   : Optional[int]   = None                            # Override status code
    override_content_type : Optional[str] = None                          # Override content type


class Routes__Proxy(Fast_API__Routes):                                    # FastAPI routes for proxy control
    tag : str = TAG__ROUTES_PROXY

    # In-memory stats tracking (in production, use Redis or similar)
    total_requests  : Safe_UInt                                         # Total requests processed
    total_responses : Safe_UInt                                         # Total responses processed
    hosts_seen      : set                                               # Unique hosts encountered
    paths_seen      : set                                               # Unique paths encountered
    total_bytes_processed : int = 0                                     # Total bytes of content processed
    content_modifications : int = 0                                     # Number of content modifications

    def process_debug_commands(self,
                          response_data: Schema__Proxy__Response_Data,
                          modifications: Schema__Proxy__Modifications) -> None:
        """
        Process debug commands that can modify the response
        ALL content modifications happen here in FastAPI, not in the interceptor
        """
        debug_params = response_data.debug_params

        if not debug_params:
            return

        content_type = response_data.response.get("content_type", "")
        body_content = response_data.response.get("body", "")

        # Handle 'show' command - display internal data structures
        if 'show' in debug_params:
            show_value = debug_params['show']

            if show_value == 'response-data':
                # Return the entire response_data as JSON
                response_json = response_data.json()
                modifications.override_response = True
                modifications.override_status = 200
                modifications.override_content_type = "application/json"
                modifications.modified_body = json.dumps(response_json, indent=2)
                modifications.headers_to_add["x-debug-show"] = "response-data"
                return  # Early return - we're replacing everything

            # ... other show commands ...

        # Handle 'inject' commands for HTML content
        if body_content and "text/html" in content_type:
            # Start with original body
            modified_body = body_content

            # Apply debug banner if requested
            if debug_params.get('inject_debug') == 'true' or debug_params.get('debug') == 'true':
                debug_banner = f"""
                <div style="position:fixed;top:0;left:0;right:0;background:#ff0;color:#000;padding:10px;z-index:999999;font-family:monospace;border-bottom:2px solid #f00">
                    🔧 DEBUG MODE | Params: {json.dumps(debug_params)} | Path: {response_data.request.get('path')}
                </div>
                """

                if "</body>" in modified_body:
                    modified_body = modified_body.replace("</body>", f"{debug_banner}</body>")
                elif "<body" in modified_body:
                    import re
                    modified_body = re.sub(r'(<body[^>]*>)', r'\1' + debug_banner, modified_body, count=1)

                modifications.headers_to_add["X-Debug-Banner-Injected"] = "true"

            # Apply debug panel if requested
            if debug_params.get('inject') == 'debug-panel':
                debug_panel = f"""
                <div id="debug-panel" style="position:fixed;bottom:0;left:0;right:0;background:#222;color:#0f0;padding:20px;max-height:300px;overflow:auto;font-family:monospace;z-index:999999">
                    <h3 style="color:#0f0;margin:0 0 10px 0">🔧 Debug Panel</h3>
                    <details>
                        <summary>Request Info</summary>
                        <pre style="color:#0f0">{json.dumps(response_data.request, indent=2)}</pre>
                    </details>
                    <details>
                        <summary>Response Headers</summary>
                        <pre style="color:#0f0">{json.dumps(response_data.response.get("headers", {}), indent=2)}</pre>
                    </details>
                    <details>
                        <summary>Debug Params</summary>
                        <pre style="color:#0f0">{json.dumps(debug_params, indent=2)}</pre>
                    </details>
                    <button onclick="document.getElementById('debug-panel').style.display='none'" style="position:absolute;top:10px;right:10px">X</button>
                </div>
                """

                if "</body>" in modified_body:
                    modified_body = modified_body.replace("</body>", f"{debug_panel}</body>")

                modifications.headers_to_add["X-Debug-Panel-Injected"] = "true"

            # Apply replacements if requested
            if 'replace' in debug_params:
                replace_value = debug_params['replace']
                if ':' in replace_value:
                    old_text, new_text = replace_value.split(':', 1)
                    new_text = f'[{new_text}]'
                    if old_text in modified_body:
                        modified_body = modified_body.replace(old_text, new_text)
                        modifications.headers_to_add["X-Debug-Replace"] = f"{old_text} -> {new_text}"

            # If body was modified, update it
            if modified_body != body_content:
                modifications.modified_body = modified_body
                self.content_modifications += 1

        # Handle text/plain content modifications
        elif body_content and "text/plain" in content_type:
            modified_body = body_content

            # Add debug header/footer for plain text
            if debug_params.get('debug') == 'true':
                modified_body = f"[DEBUG MODE - Params: {debug_params}]\n\n{modified_body}\n\n[END DEBUG]"
                modifications.modified_body = modified_body
                self.content_modifications += 1

        # Handle JSON content modifications
        elif body_content and "application/json" in content_type:
            if debug_params.get('inject_debug') == 'true':
                try:
                    json_data = json.loads(body_content)
                    json_data["_debug_params"] = debug_params
                    json_data["_debug_timestamp"] = datetime.utcnow().isoformat()
                    modifications.modified_body = json.dumps(json_data, indent=2)
                    self.content_modifications += 1
                except:
                    pass  # If JSON parsing fails, don't modify

    def process_request(self, request_data: Schema__Proxy__Request_Data   # Incoming request data
                       ) -> Schema__Proxy__Modifications:                 # Modifications to apply
        self.total_requests += 1
        self.hosts_seen.add(request_data.host)
        self.paths_seen.add(request_data.path)

        # Create response with modifications
        modifications = Schema__Proxy__Modifications()

        # Add custom headers
        modifications.headers_to_add = {
            "x-mgraph-proxy"          : "v1.0"                              ,
            "x-request-id"            : f"req-{self.total_requests}"        ,
            "x-processed-by"          : "FastAPI-Proxy"                     ,
            "x-processed-at"          : datetime.utcnow().isoformat()       ,
            "x-stats-total-requests"  : str(self.total_requests)            ,
            "x-stats-unique-hosts"    : str(len(self.hosts_seen))           ,
            "y-version-service"       : version__mgraph_ai_service_mitmproxy,
            "y-version-interceptor"   : request_data.version                ,
        }

        # Add debug params to headers if present
        if request_data.debug_params:
            modifications.headers_to_add["x-debug-params"] = json.dumps(request_data.debug_params)

        # Block certain paths
        if "/blocked" in request_data.path:
            modifications.block_request = True
            modifications.block_message = f"Path {request_data.path} is blocked by policy"

        # Remove sensitive headers
        for header in request_data.headers:
            if any(sensitive in header for sensitive in ["Secret", "Private", "Token"]):
                modifications.headers_to_remove.append(header)

        return modifications

    def process_response(self, response_data: Schema__Proxy__Response_Data
                    ) -> Schema__Proxy__Modifications:
        self.total_responses += 1

        # Create response with modifications
        modifications = Schema__Proxy__Modifications()

        # Get body info for stats
        body_content = response_data.response.get("body")
        body_size    = response_data.response.get("body_size", 0)
        content_type = response_data.response.get("content_type", "")

        # Update stats if body present
        if body_content:
            self.total_bytes_processed += body_size

        # Always add standard headers (moved up before debug commands)
        modifications.headers_to_add.update({
            "x-mgraph-proxy"              : "v1.0"                              ,
            "x-response-id"               : f"resp-{self.total_responses}"      ,
            "x-proxy-stats-requests"      : str(self.total_requests)            ,
            "x-proxy-stats-responses"     : str(self.total_responses)           ,
            "x-proxy-stats-hosts"         : str(len(self.hosts_seen))           ,
            "y-proxy-content-type"        : content_type                        ,
            "y-proxy-received-bytes"      : str(body_size)                      ,
            "y-version-mitmproxy-service" : version__mgraph_ai_service_mitmproxy,
            "y-version-osbot-fast-api"    : version__osbot_fast_api             ,
            "y-version-interceptor"       : response_data.version               ,
        })

        # Add debug params to response headers if present
        if response_data.debug_params:
            modifications.headers_to_add["x-debug-params-active"] = json.dumps(response_data.debug_params)

        # Process debug commands (may override response)
        self.process_debug_commands(response_data, modifications)

        # If debug command wants to override the entire response, return now
        if modifications.override_response:
            self.content_modifications += 1
            return modifications

        # Regular processing continues here for non-overridden responses
        # Add content processing headers
        if body_content:
            modifications.headers_to_add["x-content-processed"] = "true"
            modifications.headers_to_add["x-content-size"] = str(body_size)
            modifications.headers_to_add["x-content-type-received"] = content_type

        # Calculate and include stats
        stats = {
            "total_requests"       : self.total_requests                               ,
            "total_responses"      : self.total_responses                              ,
            "unique_hosts"         : len(self.hosts_seen)                              ,
            "unique_paths"         : len(self.paths_seen)                              ,
            "headers_received"     : len(response_data.response.get("headers", {}))    ,
            "original_status"      : response_data.response.get("status_code")         ,
            "content_received"     : body_content is not None                          ,
            "content_size"         : body_size                                         ,
            "content_type"         : content_type                                      ,
            "total_bytes_processed": self.total_bytes_processed                        ,
            "content_modifications": self.content_modifications
        }

        modifications.headers_to_add["x-proxy-stats-headers-count"] = str(stats["headers_received"])

        # Add CORS headers for specific hosts
        if "httpbin.org" in response_data.request.get("host", ""):
            modifications.headers_to_add["access-control-allow-origin"]  = "*"
            modifications.headers_to_add["access-control-allow-methods"] = "GET, POST, OPTIONS"

        # Include detailed stats
        modifications.include_stats = True
        modifications.stats         = stats

        return modifications

    def get_proxy_stats(self) -> Dict:                                    # Get current proxy statistics
        return {
            "total_requests"       : self.total_requests        ,
            "total_responses"      : self.total_responses       ,
            "unique_hosts"         : list(self.hosts_seen)      ,
            "unique_paths"         : list(self.paths_seen)      ,
            "hosts_count"          : len(self.hosts_seen)       ,
            "paths_count"          : len(self.paths_seen)       ,
            "total_bytes_processed": self.total_bytes_processed ,
            "content_modifications": self.content_modifications
        }

    def reset_proxy_stats(self) -> Dict:                                  # Reset proxy statistics
        old_stats = self.get_proxy_stats()

        self.total_requests  = 0
        self.total_responses = 0
        self.total_bytes_processed = 0
        self.content_modifications = 0
        self.hosts_seen.clear()
        self.paths_seen.clear()

        return {
            "message"        : "Stats reset successfully" ,
            "previous_stats" : old_stats
        }

    def setup_routes(self):                                                # Configure FastAPI routes
        self.add_route_post(self.process_request   )
        self.add_route_post(self.process_response  )
        self.add_route_get (self.get_proxy_stats   )
        self.add_route_post(self.reset_proxy_stats )