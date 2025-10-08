from osbot_utils.type_safe.Type_Safe                                                 import Type_Safe
from mgraph_ai_service_mitmproxy.schemas.proxy.Schema__CORS__Config                  import Schema__CORS__Config
from mgraph_ai_service_mitmproxy.schemas.proxy.Schema__Proxy__Response_Data          import Schema__Proxy__Response_Data
from typing                                                                          import Dict

class Proxy__CORS__Service(Type_Safe):                           # CORS header management service
    cors_config: Schema__CORS__Config                            # CORS configuration

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Initialize with default config if not provided
        if not self.cors_config:
            self.cors_config = Schema__CORS__Config()

    def should_add_cors_headers(self, response_data: Schema__Proxy__Response_Data  # Check if CORS needed
                               ) -> bool:                        # Whether to add CORS
        """Determine if CORS headers should be added"""
        if not self.cors_config.enabled:
            return False

        # Always add CORS headers for cross-origin requests
        # In a real implementation, you'd check the Origin header
        return True

    def get_cors_headers_for_request(self,                       # Get CORS headers for request
                                    response_data: Schema__Proxy__Response_Data
                                    ) -> Dict[str, str]:         # CORS headers
        """Get CORS headers appropriate for this request"""
        if not self.should_add_cors_headers(response_data):
            return {}

        # Get origin from request headers if available
        request_headers = response_data.request.get('headers', {})
        origin = request_headers.get('origin') or request_headers.get('Origin')

        return self.cors_config.get_cors_headers(request_origin=origin)

    def handle_preflight_request(self,                           # Handle OPTIONS preflight
                                response_data: Schema__Proxy__Response_Data
                                ) -> Dict[str, str]:             # Preflight response headers
        """Generate headers for CORS preflight (OPTIONS) request"""
        method = response_data.request.get('method', 'GET')

        if not self.cors_config.is_preflight_request(method):
            return {}

        # Get standard CORS headers
        headers = self.get_cors_headers_for_request(response_data)

        # Add additional preflight-specific headers if needed
        headers["Content-Length"] = "0"

        return headers

    def is_preflight_request(self, response_data: Schema__Proxy__Response_Data  # Check if preflight
                            ) -> bool:                           # Is preflight
        """Check if this is a CORS preflight request"""
        method = response_data.request.get('method', 'GET')
        return self.cors_config.is_preflight_request(method)