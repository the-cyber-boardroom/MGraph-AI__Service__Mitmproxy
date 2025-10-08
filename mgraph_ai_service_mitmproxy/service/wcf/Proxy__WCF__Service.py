import requests
import json
from osbot_utils.type_safe.Type_Safe                                        import Type_Safe
from mgraph_ai_service_mitmproxy.schemas.proxy.Enum__WCF__Command_Type      import Enum__WCF__Command_Type
from mgraph_ai_service_mitmproxy.schemas.proxy.Enum__WCF__Content_Type      import Enum__WCF__Content_Type
from typing                                                                 import Optional
from mgraph_ai_service_mitmproxy.schemas.wcf.Schema__WCF__Request           import Schema__WCF__Request
from mgraph_ai_service_mitmproxy.schemas.wcf.Schema__WCF__Response          import Schema__WCF__Response


class Proxy__WCF__Service(Type_Safe):                        # WCF service integration
    wcf_base_url : str = "https://dev.web-content-filtering.mgraph.ai"  # WCF service base URL
    timeout      : int = 30                                  # Request timeout in seconds

    def create_request(self,
                       command_type : Enum__WCF__Command_Type,  # Type of WCF command
                       target_url   : str,                   # URL to process
                       rating       : Optional[float] = None,  # Optional rating parameter
                       model_to_use : Optional[str] = None   # Optional model override
                       ) -> Schema__WCF__Request:            # WCF request object
        """Create a WCF request with authentication from environment"""
        return Schema__WCF__Request(command_type       = command_type,
                                    target_url         = target_url,
                                    rating             = rating,
                                    model_to_use       = model_to_use,
                                    #auth_header_name   = get_env(ENV_VAR__WCF_SERVICE__AUTH__API_KEY__NAME, ""),
                                    #auth_header_value  = get_env(ENV_VAR__WCF_SERVICE__AUTH__API_KEY__VALUE, ""),
                                    wcf_base_url       = self.wcf_base_url                                      )

    def make_request(self, wcf_request: Schema__WCF__Request    # Execute WCF service request and return response
                      ) -> Schema__WCF__Response:

        try:
            url     = wcf_request.construct_wcf_url()                                           # Construct URL and headers
            headers = wcf_request.get_auth_headers()

            print(f"🌐 WCF Request: {url}")

            response = requests.get(url     = url         ,                                     # Make HTTP request
                                    headers = headers     ,
                                    timeout = self.timeout)


            content_type_header = response.headers.get('content-type', '')                      # Parse content type
            content_type        = Enum__WCF__Content_Type.from_header(content_type_header)

            if content_type == Enum__WCF__Content_Type.application_json:                        # Decode body based on content type
                try:
                    body = json.dumps(response.json(), indent=2)
                except:
                    body = response.content.decode('utf-8')
            else:
                body = response.content.decode('utf-8')

            # Create response object
            return Schema__WCF__Response(status_code  = response.status_code       ,
                                         content_type = content_type               ,
                                         body         = body                       ,
                                         headers      = dict(response.headers)     ,
                                         success      = response.status_code == 200)

        except requests.Timeout as e:
            return Schema__WCF__Response(
                status_code   = 504,
                content_type  = Enum__WCF__Content_Type.text_plain,
                body          = "",
                headers       = {},
                success       = False,
                error_message = f"WCF request timeout: {str(e)}"
            )

        except requests.RequestException as e:
            return Schema__WCF__Response(
                status_code   = 502,
                content_type  = Enum__WCF__Content_Type.text_plain,
                body          = "",
                headers       = {},
                success       = False,
                error_message = f"WCF request failed: {str(e)}"
            )

        except Exception as e:
            return Schema__WCF__Response(
                status_code   = 500,
                content_type  = Enum__WCF__Content_Type.text_plain,
                body          = "",
                headers       = {},
                success       = False,
                error_message = f"Unexpected error: {str(e)}"
            )

    # Process a 'show' debug command that requires WCF
    def process_show_command(self, show_value : str,                 # Value of show debug parameter
                                   target_url : str                  # URL from original request
                              ) -> Optional[Schema__WCF__Response]:  # WCF response or None

        if not Enum__WCF__Command_Type.is_wcf_command(show_value):   # Check if this is a WCF command
            return None

        command_type = Enum__WCF__Command_Type.from_show_param(show_value)      # Parse command type
        if not command_type:
            return None

        # Handle special cases
        rating       = None
        model_to_use = None

        if show_value.startswith('url-to-html-min-rating'):         # Extract rating from url-to-html-min-rating:0.5
            if ':' in show_value:
                try:
                    rating = float(show_value.split(':')[1])
                except:
                    rating = 0.5                                    # Default rating
            else:
                rating = 0.5

            target_url += f"&rating={rating}"                       # Append rating to target URL

        if show_value == 'url-to-ratings':                          # Handle url-to-ratings with special model
            model_to_use = "google/gemini-2.0-flash-lite-001"

        # Create and execute request
        wcf_request = self.create_request(command_type = command_type   ,
                                          target_url   = target_url     ,
                                          rating       = rating         ,
                                          model_to_use = model_to_use   )

        return self.make_request(wcf_request)