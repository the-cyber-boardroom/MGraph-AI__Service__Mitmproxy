import json
from unittest                                                                        import TestCase
from mgraph_ai_service_mitmproxy.service.proxy.Proxy__JSON__Service                  import Proxy__JSON__Service

class test_Proxy__JSON__Service(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.service = Proxy__JSON__Service()

    def test__init__(self):                                        # Test initialization
        assert type(self.service) is Proxy__JSON__Service



    def test_create_debug_json_response(self):                     # Test debug response creation
        response_data = { 'request': {'method': 'GET', 'path': '/test'},
                          'response': {'status': 200} }

        result = self.service.create_debug_json_response(response_data)

        assert result is not None

        # Verify it's valid JSON
        parsed = json.loads(result)
        assert parsed['request']['method'] == 'GET'
        assert parsed['response']['status'] == 200