import requests
from typing                                                                         import Dict
from fastapi                                                                        import FastAPI
from mgraph_ai_service_semantic_text.fast_api.Semantic_Text__Service__Fast_API      import Semantic_Text__Service__Fast_API
from osbot_fast_api.utils.Fast_API_Server                                           import Fast_API_Server
from osbot_fast_api_serverless.fast_api.Serverless__Fast_API__Config                import Serverless__Fast_API__Config
from osbot_utils.testing.__                                                         import __
from osbot_utils.testing.__helpers                                                  import obj
from osbot_utils.type_safe.Type_Safe                                                import Type_Safe
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path   import Safe_Str__File__Path
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Url            import Safe_Str__Url
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                      import type_safe
from osbot_utils.utils.Http                                                         import url_join_safe


class Local_Server__Semantic_Text__Service(Type_Safe):
    config          : Serverless__Fast_API__Config           = None                                     # FastAPI config (no API key)
    fast_api_server : Fast_API_Server                        = None                                     # FastAPI server wrapper
    app             : FastAPI                                = None                                     # Underlying FastAPI app
    server_url      : Safe_Str__Url                          = None                                     # Root server URL (without trailing /)
    service         : Semantic_Text__Service__Fast_API       = None


    def setup(self):
        self.config = Serverless__Fast_API__Config(enable_api_key=False)                                # Create config without API key
        service_type = self.__annotations__.get('service')                                              # this contains the type of the current service
        with service_type(config=self.config) as _:
            self.service = _
            _.setup()
            self.app = _.app()
            self.fast_api_server = Fast_API_Server(app=self.app)
            self.server_url      = self.fast_api_server.url().rstrip("/")

        return self

    def start(self):
        self.fast_api_server.start()
        return self

    def stop(self):
        self.fast_api_server.stop()
        return self

    def running(self) -> bool:
        return self.fast_api_server.running

    @type_safe
    def requests__get(self, path: Safe_Str__File__Path) -> Dict:
        url = url_join_safe(self.server_url, path)
        return requests.get(url).json()

    @type_safe
    def requests__post(self, path: Safe_Str__File__Path, json_data: Dict) -> Dict:
        url = url_join_safe(self.server_url, path)
        return requests.post(url=url, json=json_data).json()

    @type_safe
    def requests__get__obj(self, path: Safe_Str__File__Path) -> __:
        json = self.requests__get(path)
        return obj(json)

    def open_api__obj(self):
        return self.requests__get__obj('/openapi.json')

local_server_semantic_text_service = Local_Server__Semantic_Text__Service().setup()     # one off initialisation