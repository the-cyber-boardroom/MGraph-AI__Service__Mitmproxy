from osbot_utils.type_safe.Type_Safe                                                 import Type_Safe
from mgraph_ai_service_mitmproxy.schemas.proxy.Schema__Proxy__Request_Data           import Schema__Proxy__Request_Data
from mgraph_ai_service_mitmproxy.schemas.proxy.Schema__Proxy__Response_Data          import Schema__Proxy__Response_Data
from mgraph_ai_service_mitmproxy.schemas.proxy.Schema__Proxy__Modifications          import Schema__Proxy__Modifications
from mgraph_ai_service_mitmproxy.service.proxy.Proxy__Response__Service              import Proxy__Response__Service
from mgraph_ai_service_mitmproxy.service.proxy.Proxy__Stats__Service                 import Proxy__Stats__Service
from mgraph_ai_service_mitmproxy.service.proxy.Proxy__Request__Service               import Proxy__Request__Service
from mgraph_ai_service_mitmproxy.service.admin.Proxy__Admin__Service                 import Proxy__Admin__Service
from typing                                                                          import Dict, Any

class Proxy__Service(Type_Safe):                                     # Main proxy service orchestration
    stats_service    : Proxy__Stats__Service                          # Statistics tracking
    request_service  : Proxy__Request__Service                        # Request processing
    response_service : Proxy__Response__Service                       # Response processing
    admin_service    : Proxy__Admin__Service                          # Admin page generation

    def process_request(self, request_data : Schema__Proxy__Request_Data  # Process incoming request
                        ) -> Schema__Proxy__Modifications:
        return self.request_service.process_request(request_data)

    def process_response(self, response_data : Schema__Proxy__Response_Data  # Process incoming response
                         ) -> Schema__Proxy__Modifications:
        processing_result = self.response_service.process_response(response_data)           # Convert processing result to modifications
        return processing_result.modifications

    def get_stats(self) -> Dict[str, Any]:                           # Get current statistics
        return self.stats_service.get_stats()

    def reset_stats(self) -> Dict[str, Any]:                         # Reset statistics
        return self.stats_service.reset_stats()