from osbot_fast_api.api.routes.Routes__Set_Cookie                 import Routes__Set_Cookie
from osbot_fast_api_serverless.fast_api.Serverless__Fast_API      import Serverless__Fast_API
from mgraph_ai_service_mitmproxy.config                           import FAST_API__TITLE
from mgraph_ai_service_mitmproxy.fast_api.routes.Routes__Cache    import Routes__Cache
from mgraph_ai_service_mitmproxy.fast_api.routes.Routes__Proxy    import Routes__Proxy
from mgraph_ai_service_mitmproxy.utils.Version                    import version__mgraph_ai_service_mitmproxy
from osbot_fast_api_serverless.fast_api.routes.Routes__Info       import Routes__Info


# Rename to Mitmproxy_Service__Fast_API
class Service__Fast_API(Serverless__Fast_API):


    def setup(self):
        with self.config as _:
            _.name           = FAST_API__TITLE
            _.version        =  version__mgraph_ai_service_mitmproxy
            _.enable_api_key = False

        return super().setup()


    def setup_routes(self):
        self.add_routes(Routes__Proxy     )
        self.add_routes(Routes__Cache     )
        self.add_routes(Routes__Info      )
        self.add_routes(Routes__Set_Cookie)



