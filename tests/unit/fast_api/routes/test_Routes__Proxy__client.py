from unittest                                  import TestCase

from mgraph_ai_service_mitmproxy.fast_api.routes.Routes__Proxy import Schema__Proxy__Response_Data, Schema__Proxy__Modifications
from mgraph_ai_service_mitmproxy.utils.Version      import version__mgraph_ai_service_mitmproxy
from osbot_fast_api.utils.Version import version__osbot_fast_api
from osbot_utils.type_safe.type_safe_core.collections.Type_Safe__Dict import Type_Safe__Dict
from osbot_utils.utils.Dev import pprint
from tests.unit.Service__Fast_API__Test_Objs   import setup__service_fast_api_test_objs, TEST_API_KEY__NAME, TEST_API_KEY__VALUE


class test_Routes__Proxy__client(TestCase):
    @classmethod
    def setUpClass(cls):
        with setup__service_fast_api_test_objs() as _:
            cls.client = _.fast_api__client
            cls.client.headers[TEST_API_KEY__NAME] = TEST_API_KEY__VALUE

    def test_process_response(self):
        url = 'https://lite.cnn.com/aaa'  # 'https://www.bbc.co.uk/AAAA'
        url = 'https://theintercept.com/'
        show = 'url-to-ratings' # 'url-to-html-dict' , 'url-to-lines' 'url-to-html-xxx'
        #show = 'url-to-html-xxx'
        response_data = Schema__Proxy__Response_Data()
        response_data.request     ['url' ] = url
        response_data.debug_params['show'] = show
        response       = self.client.post('/proxy/process-response', json=response_data.json())
        response_data  = Schema__Proxy__Modifications.from_json(response.json())

        #print(response_data)
        #response_data.print()
        # headers_to_add = response_data.headers_to_add
        # assert type(headers_to_add)                          == Type_Safe__Dict
        # assert headers_to_add['y-version-mitmproxy-service'] == version__mgraph_ai_service_mitmproxy
        # assert headers_to_add['y-version-osbot-fast-api'   ] == version__osbot_fast_api
