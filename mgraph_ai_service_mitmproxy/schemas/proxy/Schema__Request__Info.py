from osbot_utils.type_safe.Type_Safe                                     import Type_Safe
from typing                                                              import Dict, Optional
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Url import Safe_Str__Url


class Schema__Request__Info(Type_Safe):                          # Parsed request information
    method          : str                                        # HTTP method (GET, POST, etc)
    host            : str                                        # Host header
    port            : int                     = 443              # Port number
    path            : str                                        # Request path
    url             : Safe_Str__Url                              # Full URL
    scheme          : str                     = "https"          # http or https
    headers         : Dict[str, str]                             # Request headers
    query_params    : Dict[str, str]                             # Query string parameters
    content_type    : Optional[str]           = None             # Content-Type header
    user_agent      : Optional[str]           = None             # User-Agent header
    origin          : Optional[str]           = None             # Origin header (for CORS)

    def is_https(self) -> bool:                                  # Check if HTTPS
        """Check if request is HTTPS"""
        return self.scheme == "https" or self.port == 443

    def is_get(self) -> bool:                                    # Check if GET request
        """Check if this is a GET request"""
        return self.method.upper() == "GET"

    def is_post(self) -> bool:                                   # Check if POST request
        """Check if this is a POST request"""
        return self.method.upper() == "POST"

    def is_options(self) -> bool:                                # Check if OPTIONS request
        """Check if this is an OPTIONS request (preflight)"""
        return self.method.upper() == "OPTIONS"

    def has_query_params(self) -> bool:                          # Check if has query params
        """Check if request has query parameters"""
        return len(self.query_params) > 0

    def get_header(self, header_name: str) -> Optional[str]:     # Get header value
        """Get header value (case-insensitive)"""
        header_lower = header_name.lower()
        for key, value in self.headers.items():
            if key.lower() == header_lower:
                return value
        return None

    def to_dict(self) -> Dict:                                   # Convert to dict for serialization
        """Convert to dictionary for response data"""
        return {
            'method': self.method,
            'host': self.host,
            'port': self.port,
            'path': self.path,
            'url': str(self.url),
            'scheme': self.scheme,
            'headers': self.headers.copy(),
            'query_params': self.query_params.copy()
        }