from unittest                                                                        import TestCase
from mgraph_ai_service_mitmproxy.service.proxy.Proxy__Headers__Service               import Proxy__Headers__Service
from mgraph_ai_service_mitmproxy.schemas.proxy.Schema__Proxy__Response_Data          import Schema__Proxy__Response_Data

class test_Proxy__Headers__Service(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.service = Proxy__Headers__Service()

    def test__init__(self):                                        # Test initialization
        assert type(self.service) is Proxy__Headers__Service
        assert self.service.service_version == "1.0.0"
        assert self.service.service_name == "mgraph-proxy"

    def test_get_standard_headers(self):                           # Test standard header generation
        with Schema__Proxy__Response_Data() as response_data:
            response_data.request = {
                'host': 'example.com',
                'path': '/test/path'
            }
            response_data.debug_params = {}
            response_data.response = {}
            response_data.stats = {}
            response_data.version = 'v1.0.0'

            headers = self.service.get_standard_headers(
                response_data,
                request_id="test-123"
            )

            assert headers["X-Proxy-Service"] == "mgraph-proxy"
            assert headers["X-Proxy-Version"] == "1.0.0"
            assert headers["X-Request-ID"] == "test-123"
            assert "X-Processed-At" in headers
            assert headers["X-Original-Host"] == "example.com"
            assert headers["X-Original-Path"] == "/test/path"

    def test_get_standard_headers__without_request_id(self):       # Test without request ID
        with Schema__Proxy__Response_Data() as response_data:
            response_data.request = {'host': 'example.com'}
            response_data.debug_params = {}
            response_data.response = {}
            response_data.stats = {}
            response_data.version = 'v1.0.0'

            headers = self.service.get_standard_headers(response_data)

            assert "X-Request-ID" not in headers
            assert headers["X-Proxy-Service"] == "mgraph-proxy"

    def test_get_debug_headers(self):                              # Test debug header generation
        with Schema__Proxy__Response_Data() as response_data:
            response_data.request = {}
            response_data.debug_params = {
                'show': 'url-to-html',
                'debug': 'true'
            }
            response_data.response = {}
            response_data.stats = {}
            response_data.version = 'v1.0.0'

            headers = self.service.get_debug_headers(response_data)

            assert headers["X-Debug-Mode"] == "active"
            assert "show=url-to-html" in headers["X-Debug-Params"]
            assert "debug=true" in headers["X-Debug-Params"]

    def test_get_debug_headers__no_debug_params(self):             # Test without debug params
        with Schema__Proxy__Response_Data() as response_data:
            response_data.request = {}
            response_data.debug_params = {}
            response_data.response = {}
            response_data.stats = {}
            response_data.version = 'v1.0.0'

            headers = self.service.get_debug_headers(response_data)

            assert headers == {}

    def test_get_cache_headers__no_cache(self):                    # Test no-cache headers
        headers = self.service.get_cache_headers(no_cache=True)

        assert "Cache-Control" in headers
        assert "no-store" in headers["Cache-Control"]
        assert "no-cache" in headers["Cache-Control"]
        assert headers["Pragma"] == "no-cache"
        assert headers["Expires"] == "0"

    def test_get_cache_headers__allow_cache(self):                 # Test allow cache
        headers = self.service.get_cache_headers(no_cache=False)

        assert headers == {}

    def test_get_content_headers(self):                            # Test content headers
        headers = self.service.get_content_headers(
            content_type="text/html; charset=utf-8",
            content_length=1234
        )

        assert headers["Content-Type"] == "text/html; charset=utf-8"
        assert headers["Content-Length"] == "1234"