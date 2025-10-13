from osbot_fast_api.api.routes.Fast_API__Routes                                      import Fast_API__Routes
from mgraph_ai_service_mitmproxy.schemas.proxy.Schema__Proxy__Request_Data           import Schema__Proxy__Request_Data
from mgraph_ai_service_mitmproxy.schemas.proxy.Schema__Proxy__Response_Data          import Schema__Proxy__Response_Data
from mgraph_ai_service_mitmproxy.schemas.proxy.Schema__Proxy__Modifications          import Schema__Proxy__Modifications
from mgraph_ai_service_mitmproxy.service.proxy.Proxy__Service                        import Proxy__Service
from typing                                                                          import Dict

TAG__ROUTES_PROXY                  = 'proxy'
ROUTES_PATHS__PROXY                = [ f'/{TAG__ROUTES_PROXY}/process-request'  ,
                                       f'/{TAG__ROUTES_PROXY}/process-response' ,
                                       f'/{TAG__ROUTES_PROXY}/get-proxy-stats'  ,
                                       f'/{TAG__ROUTES_PROXY}/reset-proxy-stats']

class Routes__Proxy(Fast_API__Routes):                               # FastAPI routes for proxy control
    tag : str = TAG__ROUTES_PROXY

    proxy_service : Proxy__Service = None                                   # Main proxy service

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.proxy_service = Proxy__Service().setup()

    def process_request(self, request_data : Schema__Proxy__Request_Data  # Incoming request data
                       ) -> Schema__Proxy__Modifications:            # Modifications to apply
        return self.proxy_service.process_request(request_data)

    def process_response(self, response_data : Schema__Proxy__Response_Data  # Incoming response data
                        ) -> Schema__Proxy__Modifications:           # Modifications to apply
        return self.proxy_service.process_response(response_data)

    def get_proxy_stats(self) -> Dict:                               # Get current proxy statistics
        return self.proxy_service.get_stats()

    def reset_proxy_stats(self) -> Dict:                             # Reset proxy statistics
        return self.proxy_service.reset_stats()

    def setup_routes(self):                                          # Configure FastAPI routes
        self.add_route_post(self.process_request   )
        self.add_route_post(self.process_response  )
        self.add_route_get (self.get_proxy_stats   )
        self.add_route_post(self.reset_proxy_stats )