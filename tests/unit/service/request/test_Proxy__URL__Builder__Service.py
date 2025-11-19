from unittest                                                                 import TestCase
from mgraph_ai_service_mitmproxy.service.request.Proxy__URL__Builder__Service import Proxy__URL__Builder__Service


class test_Proxy__URL__Builder__Service(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.service = Proxy__URL__Builder__Service()

    def test__init__(self):                                        # Test initialization
        assert type(self.service) is Proxy__URL__Builder__Service

    def test_build_url__https_standard_port(self):                # Test HTTPS with standard port
        url = self.service.build_url(
            scheme = 'https',
            host = 'example.com',
            port = 443,
            path = '/api/test'
        )

        assert url == 'https://example.com/api/test'
        assert ':443' not in url  # Standard port omitted

    def test_build_url__https_custom_port(self):                  # Test HTTPS with custom port
        url = self.service.build_url(
            scheme = 'https',
            host = 'example.com',
            port = 8443,
            path = '/api/test'
        )

        assert url == 'https://example.com:8443/api/test'

    def test_build_url__http_standard_port(self):                 # Test HTTP with standard port
        url = self.service.build_url(
            scheme = 'http',
            host = 'example.com',
            port = 80,
            path = '/test'
        )

        assert url == 'http://example.com/test'
        assert ':80' not in url  # Standard port omitted

    def test_build_url__http_custom_port(self):                   # Test HTTP with custom port
        url = self.service.build_url(
            scheme = 'http',
            host = 'localhost',
            port = 8080,
            path = '/test'
        )

        assert url == 'http://localhost:8080/test'

    def test_build_url__with_query_params(self):                  # Test with query parameters
        url = self.service.build_url(
            scheme = 'https',
            host = 'example.com',
            port = 443,
            path = '/search',
            query_params = {'q': 'test', 'page': '1'}
        )

        assert url.startswith('https://example.com/search?')
        assert 'q=test' in url
        assert 'page=1' in url

    def test_build_url__path_without_leading_slash(self):         # Test path normalization
        url = self.service.build_url(
            scheme = 'https',
            host = 'example.com',
            port = 443,
            path = 'api/test'  # No leading slash
        )

        assert url == 'https://example.com/api/test'

    def test_build_pretty_url(self):                              # Test pretty URL (no query)
        url = self.service.build_pretty_url(
            scheme = 'https',
            host = 'example.com',
            port = 443,
            path = '/api/test'
        )

        assert url == 'https://example.com/api/test'
        assert '?' not in url

    def test_extract_base_url__with_query(self):                  # Test base URL extraction
        full_url = 'https://example.com/test?key=value'
        base_url = self.service.extract_base_url(full_url)

        assert base_url == 'https://example.com/test'

    def test_extract_base_url__without_query(self):               # Test extraction without query
        full_url = 'https://example.com/test'
        base_url = self.service.extract_base_url(full_url)

        assert base_url == 'https://example.com/test'

    def test_is_standard_port__https(self):                       # Test standard port check HTTPS
        assert self.service.is_standard_port('https', 443) is True
        assert self.service.is_standard_port('https', 8443) is False

    def test_is_standard_port__http(self):                        # Test standard port check HTTP
        assert self.service.is_standard_port('http', 80) is True
        assert self.service.is_standard_port('http', 8080) is False