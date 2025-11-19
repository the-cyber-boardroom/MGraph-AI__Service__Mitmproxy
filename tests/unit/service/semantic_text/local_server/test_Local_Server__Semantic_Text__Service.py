from unittest                                                                                                 import TestCase
from fastapi                                                                                                  import FastAPI
from mgraph_ai_service_semantic_text.fast_api.Semantic_Text__Service__Fast_API                                import Semantic_Text__Service__Fast_API
from osbot_fast_api.utils.Fast_API_Server                                                                     import Fast_API_Server
from osbot_fast_api_serverless.fast_api.Serverless__Fast_API__Config                                          import Serverless__Fast_API__Config
from osbot_utils.testing.__                                                                                   import __
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Url                                      import Safe_Str__Url
from mgraph_ai_service_mitmproxy.schemas.semantic_text.client.Schema__Semantic_Text__Transformation__Response import Schema__Semantic_Text__Transformation__Response
from tests.unit.service.semantic_text.local_server.Local_Server__Semantic_Text__Service                       import Local_Server__Semantic_Text__Service


class test_Local_Server__Semantic_Text__Service(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with Local_Server__Semantic_Text__Service().setup() as _:
            cls.local_server_semantic_text_service = _
            _.start()

    @classmethod
    def tearDownClass(cls) -> None:
        with cls.local_server_semantic_text_service as _:
            assert _.stop()                   == _
            assert _.fast_api_server.running  is False


    def test_setup(self):
        with self.local_server_semantic_text_service as _:
            assert type(_                ) is Local_Server__Semantic_Text__Service
            assert type(_.config         ) is Serverless__Fast_API__Config
            assert type(_.fast_api_server) is Fast_API_Server
            assert type(_.app            ) is FastAPI
            assert type(_.server_url     ) is Safe_Str__Url
            assert type(_.service        ) is Semantic_Text__Service__Fast_API
            assert _.server_url            == f'http://127.0.0.1:{_.fast_api_server.port}'

    def test_start(self):
        with self.local_server_semantic_text_service as _:
            assert _.fast_api_server.running       is True
            assert _.requests__get('/info/health') == {'status': 'ok'}
            assert _.open_api__obj().info.title    == 'MGraph AI Service Semantic_Text'

    def test_transformation(self):
        with self.local_server_semantic_text_service as _:
            path          = "/text-transformation/transform/text_hash/xxx/positive/above/0"
            json_data     = {"hash_mapping": {"aaaaa12345": "Some text" }}
            response_json = _.requests__post(path=path, json_data=json_data)
            response      = Schema__Semantic_Text__Transformation__Response.from_json(response_json)
            assert response_json  == { 'transformed_mapping': {'aaaaa12345': 'xxxx xxxx'},
                                       'transformation_mode': 'xxx'                      ,
                                       'success'            : True                       ,
                                       'total_hashes'       : 1                          ,
                                       'transformed_hashes' : 1                          ,
                                       'error_message'      : None                       }
            assert type(response)  is Schema__Semantic_Text__Transformation__Response
            assert response.json() == response_json
            assert response.obj () == __(error_message       = None                      ,
                                         transformed_mapping = __(aaaaa12345='xxxx xxxx'),
                                         transformation_mode = 'xxx'                     ,
                                         success             = True                      ,
                                         total_hashes        = 1                         ,
                                         transformed_hashes  = 1                         )
