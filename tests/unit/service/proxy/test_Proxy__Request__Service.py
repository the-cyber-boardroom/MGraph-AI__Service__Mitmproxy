from unittest                                                                        import TestCase
from osbot_utils.utils.Objects                                                       import base_classes
from mgraph_ai_service_mitmproxy.service.proxy.Proxy__Request__Service               import Proxy__Request__Service
from mgraph_ai_service_mitmproxy.schemas.proxy.Schema__Proxy__Request_Data           import Schema__Proxy__Request_Data
from mgraph_ai_service_mitmproxy.schemas.proxy.Schema__Proxy__Modifications          import Schema__Proxy__Modifications

class test_Proxy__Request__Service(TestCase):

    @classmethod
    def setUpClass(cls):                                             # Setup once for all tests
        cls.service = Proxy__Request__Service()

    def test__init__(self):                                          # Test initialization
        with self.service as _:
            assert type(_)         is Proxy__Request__Service
            assert base_classes(_) == [Proxy__Request__Service.__bases__[0], object]
            assert _.stats_service   is not None
            assert _.content_service is not None

    def test_process_request(self):                                  # Test basic request processing
        with Schema__Proxy__Request_Data() as request:
            request.method  = "GET"
            request.host    = "example.com"
            request.path    = "/test/path"
            request.version = "v1.0.0"
            request.headers = {"User-Agent": "Test"}

            with self.service.process_request(request) as modifications:
                assert type(modifications) is Schema__Proxy__Modifications

                # Verify headers were added
                assert "x-mgraph-proxy"         in modifications.headers_to_add
                assert "x-request-id"           in modifications.headers_to_add
                assert "x-processed-by"         in modifications.headers_to_add
                assert "y-version-interceptor"  in modifications.headers_to_add

                # Verify stats were updated
                assert self.service.stats_service.stats.total_requests > 0

    def test_process_request__blocked_path(self):                    # Test path blocking
        with Schema__Proxy__Request_Data() as request:
            request.method  = "GET"
            request.host    = "example.com"
            request.path    = "/blocked/resource"
            request.version = "v1.0.0"

            with self.service.process_request(request) as modifications:
                assert modifications.block_request is True
                assert "blocked by policy" in modifications.block_message.lower()
                assert modifications.block_status == 403

    def test_process_request__cached_response(self):                 # Test cached response via cookie
        with Schema__Proxy__Request_Data() as request:
            request.method  = "GET"
            request.host    = "example.com"
            request.path    = "/test"
            request.version = "v1.0.0"
            request.headers = {"Cookie": "cache_test=true"}

            with self.service.process_request(request) as modifications:
                assert modifications.cached_response is not None
                assert modifications.cached_response != {}
                assert modifications.cached_response["status_code"] == 200
                assert "CACHED RESPONSE TEST" in modifications.cached_response["body"]

    def test_process_request__sensitive_headers(self):               # Test sensitive header removal
        with Schema__Proxy__Request_Data() as request:
            request.method  = "GET"
            request.host    = "example.com"
            request.path    = "/test"
            request.version = "v1.0.0"
            request.headers = {
                "User-Agent": "Test",
                "X-Secret-Token": "secret123",
                "X-Private-Key": "private456"
            }

            with self.service.process_request(request) as modifications:
                # Sensitive headers should be marked for removal
                assert len(modifications.headers_to_remove) > 0
                assert any("Secret" in h or "Private" in h
                          for h in modifications.headers_to_remove)