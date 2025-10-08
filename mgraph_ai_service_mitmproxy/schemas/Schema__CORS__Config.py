from osbot_utils.type_safe.Type_Safe                                                 import Type_Safe
from typing                                                                          import List, Dict

class Schema__CORS__Config(Type_Safe):                           # CORS configuration
    enabled            : bool         = True                     # Whether CORS is enabled
    allowed_origins    : List[str]    = ["*"]                    # Allowed origins
    allowed_methods    : List[str]    = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]  # Allowed methods
    allowed_headers    : List[str]    = ["*"]                    # Allowed headers
    expose_headers     : List[str]    = ["Content-Length", "Content-Type"]  # Exposed headers
    allow_credentials  : bool         = True                     # Allow credentials
    max_age            : int          = 3600                     # Preflight cache duration

    def get_cors_headers(self, request_origin: str = None       # Get CORS headers
                        ) -> Dict[str, str]:                     # CORS headers dict
        """Generate CORS headers based on configuration"""
        if not self.enabled:
            return {}

        headers = {}

        # Determine origin to use
        if request_origin and self.allowed_origins != ["*"]:
            # Check if origin is in allowed list
            if request_origin in self.allowed_origins:
                headers["Access-Control-Allow-Origin"] = request_origin
        else:
            headers["Access-Control-Allow-Origin"] = "*"

        # Add other CORS headers
        headers["Access-Control-Allow-Methods"] = ", ".join(self.allowed_methods)
        headers["Access-Control-Allow-Headers"] = ", ".join(self.allowed_headers)
        headers["Access-Control-Expose-Headers"] = ", ".join(self.expose_headers)

        if self.allow_credentials:
            headers["Access-Control-Allow-Credentials"] = "true"

        headers["Access-Control-Max-Age"] = str(self.max_age)

        return headers

    def is_preflight_request(self, method: str) -> bool:         # Check if preflight request
        """Check if this is a CORS preflight request"""
        return method.upper() == "OPTIONS"