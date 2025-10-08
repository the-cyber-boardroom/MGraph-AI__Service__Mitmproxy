from unittest                                                                        import TestCase
import json
from mgraph_ai_service_mitmproxy.service.proxy.Proxy__JSON__Service                  import Proxy__JSON__Service

class test_Proxy__JSON__Service(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.service = Proxy__JSON__Service()

    def test__init__(self):                                        # Test initialization
        assert type(self.service) is Proxy__JSON__Service

    def test_inject_debug_fields(self):                            # Test debug field injection
        original_json = '{"key": "value", "number": 42}'
        debug_params = {'show': 'url-to-html', 'debug': 'true'}

        result = self.service.inject_debug_fields(original_json, debug_params)

        assert result is not None

        # Parse result to verify
        result_data = json.loads(result)
        assert result_data['key'] == 'value'
        assert result_data['number'] == 42
        assert result_data['_debug_params'] == debug_params
        assert '_debug_timestamp' in result_data
        assert result_data['_debug_injected'] is True

    def test_inject_debug_fields__invalid_json(self):              # Test with invalid JSON
        invalid_json = 'not valid json {'
        debug_params = {'debug': 'true'}

        result = self.service.inject_debug_fields(invalid_json, debug_params)

        assert result is None

    def test_inject_debug_fields__empty_json(self):                # Test with empty object
        empty_json = '{}'
        debug_params = {'debug': 'true'}

        result = self.service.inject_debug_fields(empty_json, debug_params)

        assert result is not None
        result_data = json.loads(result)
        assert result_data['_debug_params'] == debug_params
        assert result_data['_debug_injected'] is True

    def test_create_debug_json_response(self):                     # Test debug response creation
        response_data = {
            'request': {'method': 'GET', 'path': '/test'},
            'response': {'status': 200},
            'debug_params': {'show': 'response-data'}
        }

        result = self.service.create_debug_json_response(response_data)

        assert result is not None

        # Verify it's valid JSON
        parsed = json.loads(result)
        assert parsed['request']['method'] == 'GET'
        assert parsed['response']['status'] == 200