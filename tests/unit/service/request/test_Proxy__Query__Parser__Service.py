from unittest                                                                  import TestCase
from mgraph_ai_service_mitmproxy.service.request.Proxy__Query__Parser__Service import Proxy__Query__Parser__Service


class test_Proxy__Query__Parser__Service(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.service = Proxy__Query__Parser__Service()

    def test__init__(self):                                        # Test initialization
        assert type(self.service) is Proxy__Query__Parser__Service

    def test_parse_query_string__basic(self):                     # Test basic parsing
        query = "key1=value1&key2=value2"
        result = self.service.parse_query_string(query)

        assert result == {'key1': 'value1', 'key2': 'value2'}

    def test_parse_query_string__with_question_mark(self):        # Test with leading ?
        query = "?key=value"
        result = self.service.parse_query_string(query)

        assert result == {'key': 'value'}

    def test_parse_query_string__empty(self):                     # Test empty string
        result = self.service.parse_query_string("")

        assert result == {}

    def test_parse_query_string__no_value(self):                  # Test key with no value
        query = "key1&key2=value2"
        result = self.service.parse_query_string(query)

        assert 'key1' in result
        assert result['key2'] == 'value2'

    def test_parse_query_string__url_encoded(self):               # Test URL encoding
        query = "name=John%20Doe&email=test%40example.com"
        result = self.service.parse_query_string(query)

        assert result['name'] == 'John Doe'
        assert result['email'] == 'test@example.com'

    def test_parse_url_query(self):                               # Test parsing from full URL
        url = "https://example.com/path?key1=value1&key2=value2"
        result = self.service.parse_url_query(url)

        assert result == {'key1': 'value1', 'key2': 'value2'}

    def test_parse_url_query__no_query(self):                     # Test URL without query
        url = "https://example.com/path"
        result = self.service.parse_url_query(url)

        assert result == {}

    def test_extract_debug_params(self):                          # Test debug param extraction
        query_params = {
            'show': 'url-to-html',
            'debug': 'true',
            'other': 'value',
            'inject': 'debug-panel'
        }

        result = self.service.extract_debug_params(query_params)

        assert result == {
            'show': 'url-to-html',
            'debug': 'true',
            'inject': 'debug-panel'
        }
        assert 'other' not in result

    def test_extract_debug_params__no_debug(self):                # Test with no debug params
        query_params = {
            'search': 'test',
            'page': '1'
        }

        result = self.service.extract_debug_params(query_params)

        assert result == {}

    def test_has_debug_params__true(self):                        # Test debug param detection
        query_params = {'show': 'url-to-html', 'other': 'value'}

        assert self.service.has_debug_params(query_params) is True

    def test_has_debug_params__false(self):                       # Test no debug params
        query_params = {'search': 'test', 'page': '1'}

        assert self.service.has_debug_params(query_params) is False

    def test_build_query_string(self):                            # Test query string building
        params = {
            'key1': 'value1',
            'key2': 'value2'
        }

        result = self.service.build_query_string(params)

        # Order may vary, so check both parts
        assert 'key1=value1' in result
        assert 'key2=value2' in result
        assert '&' in result

    def test_build_query_string__empty(self):                     # Test empty params
        result = self.service.build_query_string({})

        assert result == ""

    def test_build_query_string__no_value(self):                  # Test param with no value
        params = {'key1': '', 'key2': 'value2'}

        result = self.service.build_query_string(params)

        assert 'key1' in result
        assert 'key2=value2' in result