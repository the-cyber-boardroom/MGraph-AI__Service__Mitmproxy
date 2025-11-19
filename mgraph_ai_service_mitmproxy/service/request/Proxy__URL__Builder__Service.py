from osbot_utils.type_safe.Type_Safe   import Type_Safe
from typing                            import Dict

class Proxy__URL__Builder__Service(Type_Safe):                   # URL construction service

    def build_url(self,
                  scheme      : str,                             # http or https
                  host        : str,                             # hostname
                  port        : int,                             # port number
                  path        : str,                             # request path
                  query_params: Dict[str, str] = None            # query parameters
                  ) -> str:                                      # Complete URL
        """Build a complete URL from components"""
        # Start with scheme and host
        url = f"{scheme}://{host}"

        # Add port if not standard
        if (scheme == "https" and port != 443) or (scheme == "http" and port != 80):
            url += f":{port}"

        # Add path
        if not path.startswith('/'):
            path = '/' + path
        url += path

        # Add query string if present
        if query_params:
            query_parts = []
            for key, value in query_params.items():
                if value:
                    query_parts.append(f"{key}={value}")
                else:
                    query_parts.append(key)

            if query_parts:
                url += "?" + "&".join(query_parts)

        return url

    def build_pretty_url(self,
                        scheme      : str,                       # http or https
                        host        : str,                       # hostname
                        port        : int,                       # port number
                        path        : str                        # request path
                        ) -> str:                                # URL without query params
        """Build URL without query parameters (pretty URL)"""
        return self.build_url(scheme, host, port, path, None)

    def extract_base_url(self, full_url: str                     # Extract base URL
                        ) -> str:                                # Base URL (no query)
        """Extract base URL (scheme + host + port + path) without query"""
        if '?' in full_url:
            return full_url.split('?')[0]
        return full_url

    def is_standard_port(self, scheme: str, port: int            # Check if standard port
                        ) -> bool:                               # Is standard
        """Check if port is standard for the scheme"""
        if scheme == "https":
            return port == 443
        elif scheme == "http":
            return port == 80
        return False