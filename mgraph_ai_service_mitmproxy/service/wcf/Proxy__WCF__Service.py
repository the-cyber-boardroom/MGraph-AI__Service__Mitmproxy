import time
import requests
import json
from typing                                                                 import Optional
from osbot_utils.type_safe.Type_Safe                                        import Type_Safe
from osbot_utils.utils.Misc                                                 import date_time_now
from mgraph_ai_service_mitmproxy.schemas.proxy.Enum__WCF__Command_Type      import Enum__WCF__Command_Type
from mgraph_ai_service_mitmproxy.schemas.proxy.Enum__WCF__Content_Type      import Enum__WCF__Content_Type
from mgraph_ai_service_mitmproxy.schemas.wcf.Schema__WCF__Request           import Schema__WCF__Request
from mgraph_ai_service_mitmproxy.schemas.wcf.Schema__WCF__Response          import Schema__WCF__Response
from mgraph_ai_service_mitmproxy.service.cache.Proxy__Cache__Service        import Proxy__Cache__Service


class WCF__Request__Handler(Type_Safe):                                     # Handles WCF request creation and execution
    wcf_base_url : str = "https://dev.web-content-filtering.mgraph.ai"      # WCF service base URL
    timeout      : float = float(30)                                        # Request timeout in seconds

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

            response = requests.get(url     = url         ,                 # Make HTTP request
                                    headers = headers     ,
                                    timeout = self.timeout)

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


class WCF__Command__Processor(Type_Safe):                                   # Processes WCF show commands with special parameter handling

    def parse_show_command(self, show_value: str                            # Parse show value and extract command parameters
                           ) -> Optional[tuple]:                            # Returns (command_type, rating, model_to_use, modified_url_suffix) or None
        """Parse show command value and extract special parameters"""
        if not Enum__WCF__Command_Type.is_wcf_command(show_value):
            return None

        command_type = Enum__WCF__Command_Type.from_show_param(show_value)
        if not command_type:
            return None

        rating               = None
        model_to_use         = None
        modified_url_suffix  = ""

        if show_value.startswith('url-to-html-min-rating'):                 # Handle rating parameter
            if ':' in show_value:
                try:
                    rating = float(show_value.split(':')[1])
                except:
                    rating = 0.5
            else:
                rating = 0.5
            modified_url_suffix = f"&rating={rating}"

        if show_value == 'url-to-ratings':                                  # Handle special model override
            model_to_use = "google/gemini-2.0-flash-lite-001"               # todo: move to const

        return (command_type, rating, model_to_use, modified_url_suffix)    # todo: this should return a Type_Safe class


class WCF__Cache__Integrator(Type_Safe):                                    # Integrates cache with WCF request/response cycle
    cache_service : Optional[Proxy__Cache__Service]                         # Cache service integration

    def try_get_cached_response(self, target_url   : str,                        # Original target URL
                                      show_value   : str,                        # WCF command value
                                      command_type : Enum__WCF__Command_Type     # Parsed command type
                                 ) -> Optional[Schema__WCF__Response]:           # This will attempt to retrieve cached transformation response

        if not self.cache_service or not self.cache_service.cache_config.enabled:
            return None

        cached_content = self.cache_service.get_cached_transformation(target_url  = target_url ,
                                                                      wcf_command = show_value )

        if cached_content:
            self.cache_service.increment_cache_hit()
            content_type = self.get_content_type_for_command(command_type)
            return Schema__WCF__Response(status_code  = 200             ,
                                         content_type = content_type    ,
                                         body         = cached_content  ,
                                         headers      = {}              ,
                                         success      = True            )
        else:
            self.cache_service.increment_cache_miss()
            return None

    def store_wcf_response(self,
                          target_url       : str,                           # Original target URL
                          show_value       : str,                           # WCF command value
                          wcf_response     : Schema__WCF__Response,         # WCF response to cache
                          call_duration_ms : float                          # Duration of WCF call in milliseconds
                          ) -> None:                                        # Store successful response in cache
        """Store WCF response in cache if successful"""
        if not wcf_response or not wcf_response.success or not self.cache_service:
            return

        try:
            self.cache_service.store_transformation(
                target_url  = target_url,
                wcf_command = show_value,
                content     = wcf_response.body,
                metadata    = { "status_code"           : wcf_response.status_code          ,       # todo : change to Type_Safe object
                                "content_type"          : wcf_response.content_type.value   ,
                                "wcf_response_time_ms"  : call_duration_ms                  ,
                                "cached_at"             : date_time_now()                   ,      # todo change this to timestamp
                                "wcf_command"           : show_value                        }
            )
        except Exception as e:
            print(f"⚠️  Cache storage error (non-fatal): {e}")             # Log but don't fail the request

    def get_content_type_for_command(self, command_type: Enum__WCF__Command_Type  # Command type to map
                                      ) -> Enum__WCF__Content_Type:               # Map command type to content type

        mapping = { Enum__WCF__Command_Type.url_to_html           : Enum__WCF__Content_Type.text_html        ,
                    Enum__WCF__Command_Type.url_to_html_xxx       : Enum__WCF__Content_Type.text_html        ,
                    Enum__WCF__Command_Type.url_to_html_min_rating: Enum__WCF__Content_Type.text_html        ,
                    Enum__WCF__Command_Type.url_to_text           : Enum__WCF__Content_Type.text_plain       ,
                    Enum__WCF__Command_Type.url_to_text_nodes     : Enum__WCF__Content_Type.text_plain       ,
                    Enum__WCF__Command_Type.url_to_lines          : Enum__WCF__Content_Type.text_plain       ,
                    Enum__WCF__Command_Type.url_to_ratings        : Enum__WCF__Content_Type.application_json }
        return mapping.get(command_type, Enum__WCF__Content_Type.text_plain)


class Proxy__WCF__Service(Type_Safe):                                          # WCF service integration with cache support
    wcf_base_url     : str   = "https://dev.web-content-filtering.mgraph.ai"   # WCF service base URL
    timeout          : float = 30.0                                            # Request timeout in seconds
    cache_service    : Proxy__Cache__Service  = None                           # Cache integration

    request_handler  : WCF__Request__Handler                                   # Handles WCF requests
    command_processor: WCF__Command__Processor                                 # Processes show commands
    cache_integrator : WCF__Cache__Integrator                                  # Integrates cache

    def setup(self):
        self.request_handler   = WCF__Request__Handler(wcf_base_url = self.wcf_base_url,
                                                       timeout      = self.timeout     )
        self.command_processor = WCF__Command__Processor()
        self.cache_integrator  = WCF__Cache__Integrator(cache_service = self.cache_service)
        self.cache_service     = Proxy__Cache__Service().setup()
        return self

    def create_request(self, command_type : Enum__WCF__Command_Type,              # Type of WCF command
                             target_url   : str,                                  # URL to process
                             rating       : Optional[float] = None,               # Optional rating parameter
                             model_to_use : Optional[str] = None                  # Optional model override
                        ) -> Schema__WCF__Request:                               # WCF request object
        return self.request_handler.create_request(command_type = command_type  ,       # Create a WCF request with authentication from environment
                                                   target_url   = target_url    ,
                                                   rating       = rating        ,
                                                   model_to_use = model_to_use  )

    def make_request(self, wcf_request: Schema__WCF__Request                # Execute WCF service request and return response
                      ) -> Schema__WCF__Response:
        return self.request_handler.make_request(wcf_request)

    def process_show_command(self, show_value : str,                               # WCF show command value
                                   target_url : str                                # Target URL to process
                              ) -> Optional[Schema__WCF__Response]:                # Process WCF show command with cache integration"""

        parsed = self.command_processor.parse_show_command(show_value)      # Parse command and extract parameters
        if not parsed:
            return None

        command_type, rating, model_to_use, modified_url_suffix = parsed

        cached_response = self.cache_integrator.try_get_cached_response(target_url   = target_url  , # Check cache first
                                                                        show_value   = show_value  ,
                                                                        command_type = command_type)

        if cached_response:
            return cached_response

        start_time   = time.time()                                                      # Cache miss - call WCF service
        modified_url = target_url + modified_url_suffix

        wcf_request = self.create_request(command_type = command_type,
                                          target_url   = modified_url,
                                          rating       = rating,
                                          model_to_use = model_to_use)

        wcf_response      = self.make_request(wcf_request)
        call_duration_ms  = (time.time() - start_time) * 1000

        self.cache_integrator.store_wcf_response(                           # Store successful responses in cache
            target_url       = target_url,
            show_value       = show_value,
            wcf_response     = wcf_response,
            call_duration_ms = call_duration_ms
        )

        return wcf_response

    def _get_content_type_for_command(self,
                                      command_type: Enum__WCF__Command_Type # Command type to map
                                      ) -> Enum__WCF__Content_Type:         # Corresponding content type
        """Map command type to content type (delegated for backward compatibility)"""
        return self.cache_integrator.get_content_type_for_command(command_type)