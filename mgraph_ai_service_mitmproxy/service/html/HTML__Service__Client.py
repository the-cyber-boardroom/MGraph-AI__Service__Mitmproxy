import requests
import json
from osbot_utils.type_safe.Type_Safe                                                    import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_Float                                   import Safe_Float
from osbot_utils.utils.Env                                                              import get_env
from mgraph_ai_service_mitmproxy.schemas.html.Schema__HTML__Service__Request            import Schema__HTML__Service__Request
from mgraph_ai_service_mitmproxy.schemas.html.Schema__HTML__Service__Response           import Schema__HTML__Service__Response
from mgraph_ai_service_mitmproxy.schemas.html.Schema__Hashes__To__Html__Request         import Schema__Hashes__To__Html__Request
from mgraph_ai_service_mitmproxy.schemas.html.Schema__Html__To__Dict__Hashes__Request   import Schema__Html__To__Dict__Hashes__Request
from mgraph_ai_service_mitmproxy.schemas.html.Schema__Html__To__Dict__Hashes__Response  import Schema__Html__To__Dict__Hashes__Response
from mgraph_ai_service_mitmproxy.service.consts.consts__html_service                    import (ENV_VAR__AUTH__TARGET_SERVER__HTML_SERVICE__BASE_URL ,
                                                                                                ENV_VAR__AUTH__TARGET_SERVER__HTML_SERVICE__KEY_NAME ,
                                                                                                ENV_VAR__AUTH__TARGET_SERVER__HTML_SERVICE__KEY_VALUE,
                                                                                                DEFAULT__HTML_SERVICE__BASE_URL                      ,
                                                                                                DEFAULT__HTML_SERVICE__TIMEOUT                       )


class HTML__Service__Client(Type_Safe):                                                    # HTTP client for HTML Service API
    base_url : str        = DEFAULT__HTML_SERVICE__BASE_URL                                # HTML Service base URL
    timeout  : Safe_Float = Safe_Float(DEFAULT__HTML_SERVICE__TIMEOUT)                     # Request timeout in seconds

    def setup(self) -> 'HTML__Service__Client':                                            # Setup client with configuration from environment variables
        base_url_env = get_env(ENV_VAR__AUTH__TARGET_SERVER__HTML_SERVICE__BASE_URL)
        if base_url_env:
            self.base_url = base_url_env
        return self

    def get_auth_headers(self) -> dict:                                                    # Get authentication headers from environment
        key_name  = get_env(ENV_VAR__AUTH__TARGET_SERVER__HTML_SERVICE__KEY_NAME)
        key_value = get_env(ENV_VAR__AUTH__TARGET_SERVER__HTML_SERVICE__KEY_VALUE)

        headers = {"Content-Type": "application/json"}

        if key_name and key_value:
            headers[key_name] = key_value

        return headers

    def transform_html(self,                                                               # Call HTML Service to transform HTML content
                            request: Schema__HTML__Service__Request                        # Transform HTML using specified mode
                       ) -> Schema__HTML__Service__Response:                               # Transformation response
        endpoint_path = request.transformation_mode.to_endpoint_path()

        if not endpoint_path:
            return Schema__HTML__Service__Response(status_code   = 400                                                          ,
                                                   content_type  = "text/plain"                                                 ,
                                                   body          = ""                                                           ,
                                                   headers       = {}                                                           ,
                                                   success       = False                                                        ,
                                                   error_message = f"Invalid transformation mode: {request.transformation_mode}")

        url     = f"{self.base_url}{endpoint_path}"
        headers = self.get_auth_headers()
        payload = request.to_json_payload()

        try:
            response = requests.post(url     = url                 ,
                                     headers = headers             ,
                                     json    = payload             ,
                                     timeout = float(self.timeout) )

            content_type = response.headers.get('content-type', 'text/plain')

            if 'application/json' in content_type:                                          # Handle JSON response
                try:
                    body = json.dumps(response.json(), indent=2)
                except:
                    body = response.content.decode('utf-8')
            else:
                body = response.content.decode('utf-8')

            return Schema__HTML__Service__Response(status_code   = response.status_code   ,
                                                   content_type  = content_type           ,
                                                   body          = body                   ,
                                                   headers       = dict(response.headers) ,
                                                   success       = response.status_code == 200)

        except requests.Timeout as e:
            return Schema__HTML__Service__Response(status_code   = 504                                 ,
                                                   content_type  = "text/plain"                        ,
                                                   body          = ""                                  ,
                                                   headers       = {}                                  ,
                                                   success       = False                               ,
                                                   error_message = f"HTML Service timeout: {str(e)}")

        except requests.RequestException as e:
            return Schema__HTML__Service__Response(status_code   = 502                                      ,
                                                   content_type  = "text/plain"                             ,
                                                   body          = ""                                       ,
                                                   headers       = {}                                       ,
                                                   success       = False                                    ,
                                                   error_message = f"HTML Service request failed: {str(e)}")

        except Exception as e:
            return Schema__HTML__Service__Response(status_code   = 500                                 ,
                                                   content_type  = "text/plain"                        ,
                                                   body          = ""                                  ,
                                                   headers       = {}                                  ,
                                                   success       = False                               ,
                                                   error_message = f"Unexpected error: {str(e)}")


    def get_dict_hashes(self, request: Schema__Html__To__Dict__Hashes__Request) -> Schema__Html__To__Dict__Hashes__Response:    # Call HTML Service to get hash mapping
        endpoint_path = "/html/to/dict/hashes"
        url           = f"{self.base_url}{endpoint_path}"
        headers       = self.get_auth_headers()
        payload       = request.json()

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=float(self.timeout))

            if response.status_code == 200:
                data = response.json()
                return Schema__Html__To__Dict__Hashes__Response(**data)
            else:
                return Schema__Html__To__Dict__Hashes__Response(
                    html_dict={},
                    hash_mapping={},
                    node_count=0,
                    max_depth=0,
                    total_text_hashes=0,
                    max_depth_reached=False
                )
        except Exception as e:
            print(f"Error calling get_dict_hashes: {e}")
            return Schema__Html__To__Dict__Hashes__Response(
                html_dict={},
                hash_mapping={},
                node_count=0,
                max_depth=0,
                total_text_hashes=0,
                max_depth_reached=False
            )


    def reconstruct_from_hashes(self, request: Schema__Hashes__To__Html__Request) -> Schema__HTML__Service__Response:
        """Call HTML Service to reconstruct HTML from hashes"""
        endpoint_path = "/hashes/to/html"
        url = f"{self.base_url}{endpoint_path}"
        headers = self.get_auth_headers()
        payload = request.json()

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=float(self.timeout))

            content_type = response.headers.get('content-type', 'text/html')
            body = response.content.decode('utf-8') if response.status_code == 200 else ""

            return Schema__HTML__Service__Response(
                status_code=response.status_code,
                content_type=content_type,
                body=body,
                headers=dict(response.headers),
                success=response.status_code == 200
            )
        except Exception as e:
            return Schema__HTML__Service__Response(
                status_code=500,
                content_type="text/plain",
                body="",
                headers={},
                success=False,
                error_message=f"Error reconstructing HTML: {str(e)}"
            )