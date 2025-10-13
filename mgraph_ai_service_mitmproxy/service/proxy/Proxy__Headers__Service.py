from osbot_utils.type_safe.Type_Safe                                                 import Type_Safe
from mgraph_ai_service_mitmproxy.schemas.proxy.Schema__Proxy__Response_Data          import Schema__Proxy__Response_Data
from datetime                                                                        import datetime
from typing                                                                          import Dict

class Proxy__Headers__Service(Type_Safe):                        # Standard response headers service
    service_version : str = "1.0.0"                              # Service version
    service_name    : str = "mgraph-proxy"                       # Service name

    def get_standard_headers(self, response_data : Schema__Proxy__Response_Data,        # Generate standard headers for all responses - lowercase for HTTP/2 compatibility
                                   request_id    : str = None                           # Optional request ID
                              ) -> Dict[str, str]:                                      # Standard headers

        headers = {}

        headers["x-proxy-service"] = self.service_name                                  # Service identification (lowercase for HTTP/2)
        headers["x-proxy-version"] = self.service_version

        if request_id:                                                                  # Request tracking
            headers["x-request-id"] = request_id                                        # todo: review if we should not be setting this request id here

        # Timestamp
        headers["x-processed-at"] = datetime.utcnow().isoformat() + "Z"

        # Original request info
        if 'host' in response_data.request:
            headers["x-original-host"] = response_data.request['host']

        if 'path' in response_data.request:
            headers["x-original-path"] = response_data.request['path']

        return headers

    # def get_debug_headers(self, response_data : Schema__Proxy__Response_Data               # Get debug-specific headers
    #                      ) -> Dict[str, str]:                    # Debug headers
    #     """Generate debug headers when debug mode is active - lowercase for HTTP/2"""
    #     headers = {}
    #
    #     debug_params = response_data.debug_params
    #     if not debug_params:
    #         return headers
    #
    #     # Add debug mode indicator (lowercase)
    #     headers["x-debug-mode"] = "active"
    #
    #     # Add debug parameters as header (lowercase)
    #     debug_params_str = ";".join([f"{k}={v}" for k, v in debug_params.items()])
    #     headers["x-debug-params"] = debug_params_str
    #
    #     return headers

    def get_cache_headers(self,                                  # Get cache control headers
                         no_cache : bool = False                 # Whether to disable caching
                         ) -> Dict[str, str]:                    # Cache headers
        """Generate cache control headers - lowercase for HTTP/2"""
        if no_cache:
            return {
                "cache-control": "no-store, no-cache, must-revalidate",
                "pragma": "no-cache",
                "expires": "0"
            }
        return {}

    def get_content_headers(self,                                # Get content-related headers
                           content_type : str,                   # Content type
                           content_length : int                  # Content length in bytes
                           ) -> Dict[str, str]:                  # Content headers
        """Generate content-related headers - lowercase for HTTP/2"""
        return {
            "content-type": content_type,
            "content-length": str(content_length)
        }