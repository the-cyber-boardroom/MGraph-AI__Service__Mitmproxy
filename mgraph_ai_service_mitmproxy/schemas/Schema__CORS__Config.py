from osbot_utils.type_safe.Type_Safe     import Type_Safe
from typing                              import List, Dict

class Schema__CORS__Config(Type_Safe):                           # CORS configuration
    enabled            : bool         = True                     # Whether CORS is enabled
    allowed_origins    : List[str]    = None                     # Allowed origins
    allowed_methods    : List[str]    = None                     # Allowed methods
    allowed_headers    : List[str]    = None                     # Allowed headers
    expose_headers     : List[str]    = None                     # Exposed headers
    allow_credentials  : bool         = True                     # Allow credentials
    max_age            : int          = 3600                     # Preflight cache duration

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.allowed_origins  = ["*"]                                           # Allowed origins
        self.allowed_methods  = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]     # Allowed methods
        self.allowed_headers  = ["*"]                                           # Allowed headers
        self.expose_headers   = ["content-length", "content-type"]              # Exposed headers (lowercase)


    def get_cors_headers(self, request_origin: str = None       # Get CORS headers
                        ) -> Dict[str, str]:                     # CORS headers dict
        """Generate CORS headers based on configuration - lowercase for HTTP/2 compatibility"""
        if not self.enabled:
            return {}

        headers = {}

        # Determine origin to use
        if request_origin and self.allowed_origins != ["*"]:
            # Check if origin is in allowed list
            if request_origin in self.allowed_origins:
                headers["access-control-allow-origin"] = request_origin
        else:
            headers["access-control-allow-origin"] = "*"

        # Add other CORS headers (all lowercase for HTTP/2)
        headers["access-control-allow-methods"] = ", ".join(self.allowed_methods)
        headers["access-control-allow-headers"] = ", ".join(self.allowed_headers)
        headers["access-control-expose-headers"] = ", ".join(self.expose_headers)

        if self.allow_credentials:
            headers["access-control-allow-credentials"] = "true"

        headers["access-control-max-age"] = str(self.max_age)

        return headers

    def is_preflight_request(self, method: str) -> bool:         # Check if preflight request
        """Check if this is a CORS preflight request"""
        return method.upper() == "OPTIONS"