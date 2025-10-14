from typing                                                                 import Optional
from osbot_utils.type_safe.Type_Safe                                        import Type_Safe
from osbot_utils.utils.Json                                                 import json_to_str
from osbot_utils.utils.Misc                                                 import date_time_now
from mgraph_ai_service_mitmproxy.schemas.proxy.Enum__WCF__Command_Type      import Enum__WCF__Command_Type
from mgraph_ai_service_mitmproxy.schemas.proxy.Enum__WCF__Content_Type      import Enum__WCF__Content_Type
from mgraph_ai_service_mitmproxy.schemas.wcf.Schema__WCF__Response          import Schema__WCF__Response
from mgraph_ai_service_mitmproxy.service.cache.Proxy__Cache__Service        import Proxy__Cache__Service

class WCF__Cache__Integrator(Type_Safe):                                    # Integrates cache with WCF request/response cycle
    cache_service : Proxy__Cache__Service                                  # Cache service integration

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
            if content_type is Enum__WCF__Content_Type.application_json:
                cached_content = json_to_str(cached_content)
            return Schema__WCF__Response(status_code  = 200             ,
                                         content_type = content_type    ,
                                         body         = cached_content  ,
                                         headers      = {}              ,
                                         success      = True            )
        else:
            self.cache_service.increment_cache_miss()
            return None

    def store_wcf_response(self, target_url       : str,                           # Original target URL
                                 show_value       : str,                           # WCF command value
                                 wcf_response     : Schema__WCF__Response,         # WCF response to cache
                                 call_duration_ms : float                          # Duration of WCF call in milliseconds
                            ) -> None:                                             # Store WCF response in cache if successful


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
                    Enum__WCF__Command_Type.url_to_html_dict      : Enum__WCF__Content_Type.application_json ,
                    Enum__WCF__Command_Type.url_to_html_xxx       : Enum__WCF__Content_Type.text_html        ,
                    Enum__WCF__Command_Type.url_to_html_hashes    : Enum__WCF__Content_Type.text_html        ,
                    Enum__WCF__Command_Type.url_to_html_min_rating: Enum__WCF__Content_Type.text_html        ,
                    Enum__WCF__Command_Type.url_to_text           : Enum__WCF__Content_Type.text_plain       ,
                    Enum__WCF__Command_Type.url_to_text_nodes     : Enum__WCF__Content_Type.text_plain       ,
                    Enum__WCF__Command_Type.url_to_lines          : Enum__WCF__Content_Type.text_plain       ,
                    Enum__WCF__Command_Type.url_to_ratings        : Enum__WCF__Content_Type.application_json }
        return mapping.get(command_type, Enum__WCF__Content_Type.text_plain)