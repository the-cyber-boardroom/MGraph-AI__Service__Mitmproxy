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
            response_data.response = {}
            response_data.stats = {}
            response_data.version = 'v1.0.0'

            headers = self.service.get_standard_headers(
                response_data,
                request_id="test-123"
            )

            assert headers["x-proxy-service"] == "mgraph-proxy"
            assert headers["x-proxy-version"] == "1.0.0"
            assert headers["x-request-id"] == "test-123"
            assert "x-processed-at" in headers
            assert headers["x-original-host"] == "example.com"
            assert headers["x-original-path"] == "/test/path"

    def test_get_standard_headers__without_request_id(self):       # Test without request ID
        with Schema__Proxy__Response_Data() as response_data:
            response_data.request = {'host': 'example.com'}
            response_data.response = {}
            response_data.stats = {}
            response_data.version = 'v1.0.0'

            headers = self.service.get_standard_headers(response_data)

            assert "x-request-id" not in headers
            assert headers["x-proxy-service"] == "mgraph-proxy"

    def test_get_cache_headers__no_cache(self):                    # Test no-cache headers
        headers = self.service.get_cache_headers(no_cache=True)

        assert "cache-control" in headers
        assert "no-store" in headers["cache-control"]
        assert "no-cache" in headers["cache-control"]
        assert headers["pragma" ] == "no-cache"
        assert headers["expires"] == "0"

    def test_get_cache_headers__allow_cache(self):                 # Test allow cache
        headers = self.service.get_cache_headers(no_cache=False)

        assert headers == {}

    def test_get_content_headers(self):                            # Test content headers
        headers = self.service.get_content_headers(
            content_type="text/html; charset=utf-8",
            content_length=1234
        )

        assert headers["content-type"] == "text/html; charset=utf-8"
        assert headers["content-length"] == "1234"