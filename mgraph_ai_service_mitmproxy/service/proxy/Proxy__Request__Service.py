from osbot_utils.type_safe.Type_Safe                                        import Type_Safe
from mgraph_ai_service_mitmproxy.schemas.proxy.Schema__Proxy__Request_Data  import Schema__Proxy__Request_Data
from mgraph_ai_service_mitmproxy.schemas.proxy.Schema__Proxy__Modifications import Schema__Proxy__Modifications
from mgraph_ai_service_mitmproxy.service.proxy.Proxy__Stats__Service        import Proxy__Stats__Service
from mgraph_ai_service_mitmproxy.service.proxy.Proxy__Content__Service      import Proxy__Content__Service
from mgraph_ai_service_mitmproxy.utils.Version                              import version__mgraph_ai_service_mitmproxy
from datetime                                                               import datetime
import json

class Proxy__Request__Service(Type_Safe):                            # Request processing orchestration
    stats_service   : Proxy__Stats__Service                          # Statistics tracking
    content_service : Proxy__Content__Service                        # Content processing

    def process_request(self, request_data : Schema__Proxy__Request_Data  # Process incoming request
                        ) -> Schema__Proxy__Modifications:
        # Update statistics
        self.stats_service.increment_request(
            host = request_data.host,
            path = request_data.path
        )

        # Create response with modifications
        modifications = Schema__Proxy__Modifications()

        # Check for cached response (e.g., cache_test cookie)
        cached_response = self.content_service.check_cached_response(
            request_data   = request_data,
            total_requests = self.stats_service.stats.total_requests
        )

        if cached_response:
            modifications.cached_response = cached_response
            print(f"      🎯   Returning CACHED response for cache_test")
            return modifications

        # Add custom headers
        modifications.headers_to_add = {
            "x-mgraph-proxy"          : "v1.0"                                   ,
            "x-request-id"            : f"req-{self.stats_service.stats.total_requests}",
            "x-processed-by"          : "FastAPI-Proxy"                          ,
            "x-processed-at"          : datetime.utcnow().isoformat()            ,
            "x-stats-total-requests"  : str(self.stats_service.stats.total_requests),
            #"x-stats-unique-hosts"    : str(len(self.stats_service.stats.hosts_seen)),
            "y-version-service"       : version__mgraph_ai_service_mitmproxy     ,
            "y-version-interceptor"   : request_data.version                     ,
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