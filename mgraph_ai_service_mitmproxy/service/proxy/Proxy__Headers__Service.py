from osbot_utils.type_safe.Type_Safe                                                 import Type_Safe
from mgraph_ai_service_mitmproxy.schemas.proxy.Schema__Proxy__Response_Data          import Schema__Proxy__Response_Data
from datetime                                                                        import datetime
from typing                                                                          import Dict

class Proxy__Headers__Service(Type_Safe):                        # Standard response headers service
    service_version : str = "1.0.0"                              # Service version
    service_name    : str = "mgraph-proxy"                       # Service name

    def get_standard_headers(self,                               # Get standard response headers
                            response_data : Schema__Proxy__Response_Data,
                            request_id    : str = None           # Optional request ID
                            ) -> Dict[str, str]:                 # Standard headers
        """Generate standard headers for all responses"""
        headers = {}

        # Service identification
        headers["X-Proxy-Service"] = self.service_name
        headers["X-Proxy-Version"] = self.service_version

        # Request tracking
        if request_id:
            headers["X-Request-ID"] = request_id

        # Timestamp
        headers["X-Processed-At"] = datetime.utcnow().isoformat() + "Z"

        # Original request info
        if 'host' in response_data.request:
            headers["X-Original-Host"] = response_data.request['host']

        if 'path' in response_data.request:
            headers["X-Original-Path"] = response_data.request['path']

        return headers

    def get_debug_headers(self,                                  # Get debug-specific headers
                         response_data : Schema__Proxy__Response_Data
                         ) -> Dict[str, str]:                    # Debug headers
        """Generate debug headers when debug mode is active"""
        headers = {}

        debug_params = response_data.debug_params
        if not debug_params:
            return headers

        # Add debug mode indicator
        headers["X-Debug-Mode"] = "active"

        # Add debug parameters as header
        debug_params_str = ";".join([f"{k}={v}" for k, v in debug_params.items()])
        headers["X-Debug-Params"] = debug_params_str

        return headers

    def get_cache_headers(self,                                  # Get cache control headers
                         no_cache : bool = False                 # Whether to disable caching
                         ) -> Dict[str, str]:                    # Cache headers
        """Generate cache control headers"""
        if no_cache:
            return {
                "Cache-Control": "no-store, no-cache, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        return {}

    def get_content_headers(self,                                # Get content-related headers
                           content_type : str,                   # Content type
                           content_length : int                  # Content length in bytes
                           ) -> Dict[str, str]:                  # Content headers
        """Generate content-related headers"""
        return {
            "Content-Type": content_type,
            "Content-Length": str(content_length)
        }