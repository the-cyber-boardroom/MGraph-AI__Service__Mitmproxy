from osbot_utils.type_safe.Type_Safe                                        import Type_Safe
from mgraph_ai_service_mitmproxy.schemas.proxy.Schema__Proxy__Request_Data  import Schema__Proxy__Request_Data
from mgraph_ai_service_mitmproxy.schemas.proxy.Schema__Proxy__Modifications import Schema__Proxy__Modifications
from mgraph_ai_service_mitmproxy.service.proxy.Proxy__Stats__Service        import Proxy__Stats__Service
from mgraph_ai_service_mitmproxy.service.proxy.Proxy__Content__Service      import Proxy__Content__Service
from mgraph_ai_service_mitmproxy.service.proxy.Proxy__Cookie__Service       import Proxy__Cookie__Service
from mgraph_ai_service_mitmproxy.service.admin.Proxy__Admin__Service        import Proxy__Admin__Service
from mgraph_ai_service_mitmproxy.utils.Version                              import version__mgraph_ai_service_mitmproxy
from datetime                                                               import datetime
import json

class Proxy__Request__Service(Type_Safe):                            # Request processing orchestration
    stats_service   : Proxy__Stats__Service                          # Statistics tracking
    content_service : Proxy__Content__Service                        # Content processing
    cookie_service  : Proxy__Cookie__Service                         # Cookie-based control
    admin_service   : Proxy__Admin__Service      = None              # Admin page generation

    def setup(self):
        self.admin_service = Proxy__Admin__Service ().setup()
        return self

    def process_request(self, request_data : Schema__Proxy__Request_Data  # Process incoming request
                        ) -> Schema__Proxy__Modifications:

        if self.admin_service.is_admin_path(request_data.path):             # CHECK FOR ADMIN PATHS FIRST (before any other processing)
            return self.handle_admin_request(request_data)

        # Update statistics
        self.stats_service.increment_request(host = request_data.host,
                                             path = request_data.path)

        modifications = Schema__Proxy__Modifications()                              # Create response with modifications

        # Check for cached response using cookies
        #if self.cookie_service.is_cache_enabled(request_data.headers):
        cached_response = self.content_service.check_cached_response(request_data   = request_data,
                                                                     total_requests = self.stats_service.stats.total_requests)
        if cached_response:
            modifications.cached_response = cached_response
            print(f"      🎯   Returning CACHED response (enabled via mitm-cache cookie)")
            return modifications

        # Add custom headers
        modifications.headers_to_add = { "x-mgraph-proxy"          : "v1.0"                                          ,
                                         "x-request-id"            : f"req-{self.stats_service.stats.total_requests}",
                                         "x-processed-by"          : "FastAPI-Proxy"                                 ,
                                         "x-processed-at"          : datetime.utcnow().isoformat()                   ,
                                         "x-stats-total-requests"  : str(self.stats_service.stats.total_requests)    ,
                                         "y-version-service"       : version__mgraph_ai_service_mitmproxy            ,
                                         "y-version-interceptor"   : request_data.version                            }

        debug_params = self.cookie_service.convert_to_debug_params(request_data.headers)           # Extract cookie-based debug params and merge with path-based params

        if self.cookie_service.has_any_proxy_cookies(request_data.headers):                                     # Add cookie summary to headers if any proxy cookies present
            cookie_summary = self.cookie_service.get_cookie_summary(request_data.headers)
            modifications.headers_to_add["x-proxy-cookies"] = json.dumps(cookie_summary)

        modifications.headers_to_add["x-debug-params"] = json.dumps(debug_params)

        if "/blocked" in request_data.path:                                                             # Block certain paths
            modifications.block_request = True
            modifications.block_message = f"Path {request_data.path} is blocked by policy"

        for header in request_data.headers:                                                             # Remove sensitive headers
            if any(sensitive in header for sensitive in ["Secret", "Private", "Token"]):
                modifications.headers_to_remove.append(header)

        return modifications

    def handle_admin_request(self,request_data : Schema__Proxy__Request_Data    # Admin request data
                             ) -> Schema__Proxy__Modifications:                 # Modifications with cached response
        modifications   = Schema__Proxy__Modifications()
        cached_response = self.admin_service.handle_admin_request(request_data)
        if cached_response:
            modifications.cached_response = cached_response
            #print(f"      🔧   Returning ADMIN PAGE: {endpoint}")
        return modifications