import requests
import json
from typing                                                                 import Optional
from osbot_utils.type_safe.Type_Safe                                        import Type_Safe
from requests import ConnectTimeout

from mgraph_ai_service_mitmproxy.schemas.proxy.Enum__WCF__Command_Type      import Enum__WCF__Command_Type
from mgraph_ai_service_mitmproxy.schemas.proxy.Enum__WCF__Content_Type      import Enum__WCF__Content_Type
from mgraph_ai_service_mitmproxy.schemas.wcf.Schema__WCF__Request           import Schema__WCF__Request
from mgraph_ai_service_mitmproxy.schemas.wcf.Schema__WCF__Response          import Schema__WCF__Response
from mgraph_ai_service_mitmproxy.service.wcf.Proxy__WCF__Service            import DEFAULT__WCF__PROXY__TIMEOUT


class WCF__Request__Handler(Type_Safe):                                     # Handles WCF request creation and execution
    wcf_base_url : str = "https://dev.web-content-filtering.mgraph.ai"      # WCF service base URL
    timeout      : float = DEFAULT__WCF__PROXY__TIMEOUT                     # Request timeout in seconds

    def create_request(self, command_type : Enum__WCF__Command_Type,              # Type of WCF command
                             target_url   : str,                                  # URL to process
                             rating       : Optional[float] = None,               # Optional rating parameter
                             model_to_use : Optional[str] = None                  # Optional model override
                       ) -> Schema__WCF__Request:                           # WCF request object
        """Create a WCF request with authentication from environment"""
        return Schema__WCF__Request(command_type       = command_type,
                                    target_url         = target_url,
                                    rating             = rating,
                                    model_to_use       = model_to_use,
                                    wcf_base_url       = self.wcf_base_url)

    def make_request(self, wcf_request: Schema__WCF__Request                # Execute WCF service request and return response
                      ) -> Schema__WCF__Response:

        try:
            url     = wcf_request.construct_wcf_url()                       # Construct URL and headers
            headers = wcf_request.get_auth_headers()

            try:
                response = requests.get(url     = url         ,                 # Make HTTP request
                                        headers = headers     ,
                                        timeout = self.timeout)
            except ConnectTimeout as error:
                return Schema__WCF__Response(error_message = str(error.args[0]),
                                             status_code   = 408               ,  # HTTP: 408 Request Timeout
                                             success       = False             )

            content_type_header = response.headers.get('content-type', '')  # Parse content type
            content_type        = Enum__WCF__Content_Type.from_header(content_type_header)

            if content_type == Enum__WCF__Content_Type.application_json:    # Decode body based on content type
                try:
                    body = json.dumps(response.json(), indent=2)
                except:
                    body = response.content.decode('utf-8')
            else:
                body = response.content.decode('utf-8')

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