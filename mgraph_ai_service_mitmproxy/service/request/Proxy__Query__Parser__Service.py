from osbot_utils.type_safe.Type_Safe    import Type_Safe
from urllib.parse                       import parse_qs, urlparse
from typing                             import Dict

class Proxy__Query__Parser__Service(Type_Safe):                  # Query string parsing service

    def parse_query_string(self, query_string: str               # Parse query string to dict
                          ) -> Dict[str, str]:                   # Parsed parameters
        """Parse query string into dictionary of parameters"""
        if not query_string:
            return {}

        # Remove leading '?' if present
        if query_string.startswith('?'):
            query_string = query_string[1:]

        # Parse query string
        parsed = parse_qs(query_string, keep_blank_values=True)

        # Convert lists to single values (take first value)
        result = {}
        for key, values in parsed.items():
            if values:
                result[key] = values[0]
            else:
                result[key] = ""

        return result

    def parse_url_query(self, url: str                           # Parse query from full URL
                       ) -> Dict[str, str]:                      # Parsed parameters
        """Parse query parameters from a full URL"""
        parsed_url = urlparse(url)
        return self.parse_query_string(parsed_url.query)

    def extract_debug_params(self, query_params: Dict[str, str]  # Extract debug parameters
                            ) -> Dict[str, str]:                 # Debug parameters only
        """Extract only debug-related parameters from query params"""
        debug_keys = ['show', 'inject', 'replace', 'debug', 'inject_debug']

        debug_params = {}
        for key in debug_keys:
            if key in query_params:
                debug_params[key] = query_params[key]

        return debug_params

    def has_debug_params(self, query_params: Dict[str, str]      # Check if has debug params
                        ) -> bool:                               # Has debug params
        """Check if query parameters contain any debug parameters"""
        debug_keys = ['show', 'inject', 'replace', 'debug', 'inject_debug']
        return any(key in query_params for key in debug_keys)

    def build_query_string(self, params: Dict[str, str]          # Build query string from dict
                          ) -> str:                              # Query string
        """Build query string from dictionary of parameters"""
        if not params:
            return ""

        # Build query string
        parts = []
        for key, value in params.items():
            if value:
                parts.append(f"{key}={value}")
            else:
                parts.append(key)

        return "&".join(parts)