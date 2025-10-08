from unittest                                                                import TestCase
from mgraph_ai_service_mitmproxy.schemas.Schema__CORS__Config                import Schema__CORS__Config
from mgraph_ai_service_mitmproxy.service.proxy.Proxy__CORS__Service          import Proxy__CORS__Service
from mgraph_ai_service_mitmproxy.schemas.proxy.Schema__Proxy__Response_Data  import Schema__Proxy__Response_Data

class test_CORS_Schema_And_Service(TestCase):

    def test_schema__cors__config__defaults(self):                # Test default configuration
        with Schema__CORS__Config() as config:
            assert config.enabled           is True
            assert config.allowed_origins   == ["*"]
            assert "GET"                    in config.allowed_methods
            assert "POST"                   in config.allowed_methods
            assert config.allow_credentials is True
            assert config.max_age           == 3600

    def test_schema__cors__config__get_cors_headers(self):        # Test CORS header generation
        with Schema__CORS__Config() as config:
            headers = config.get_cors_headers()

            assert headers["Access-Control-Allow-Origin"] == "*"
            assert "GET" in headers["Access-Control-Allow-Methods"]
            assert headers["Access-Control-Allow-Credentials"] == "true"
            assert "3600" in headers["Access-Control-Max-Age"]

    def test_schema__cors__config__get_cors_headers_with_origin(self):  # Test with specific origin
        with Schema__CORS__Config() as config:
            config.allowed_origins = ["https://example.com"]

            headers = config.get_cors_headers(request_origin="https://example.com")

            assert headers["Access-Control-Allow-Origin"] == "https://example.com"

    def test_schema__cors__config__is_preflight_request(self):    # Test preflight detection
        with Schema__CORS__Config() as config:
            assert config.is_preflight_request("OPTIONS") is True
            assert config.is_preflight_request("options") is True
            assert config.is_preflight_request("GET") is False
            assert config.is_preflight_request("POST") is False

    def test_schema__cors__config__disabled(self):                # Test disabled CORS
        with Schema__CORS__Config() as config:
            config.enabled = False

            headers = config.get_cors_headers()

            assert headers == {}

    def test_proxy__cors__service__init(self):                    # Test service initialization
        service = Proxy__CORS__Service()

        assert type(service)                is Proxy__CORS__Service
        assert type(service.cors_config)    is Schema__CORS__Config
        assert service.cors_config          is not None
        assert service.cors_config.enabled  is True

    def test_proxy__cors__service__should_add_cors_headers(self):  # Test CORS header check
        service = Proxy__CORS__Service()

        with Schema__Proxy__Response_Data() as response_data:
            response_data.request = {'method': 'GET'}
            response_data.debug_params = {}
            response_data.response = {}
            response_data.stats = {}
            response_data.version = 'v1.0.0'

            assert service.should_add_cors_headers(response_data) is True

    def test_proxy__cors__service__get_cors_headers_for_request(self):  # Test header generation
        service = Proxy__CORS__Service()

        with Schema__Proxy__Response_Data() as response_data:
            response_data.request = { 'method': 'GET',
                                      'headers': {'origin': 'https://example.com'}  }
            response_data.debug_params = {}
            response_data.response = {}
            response_data.stats = {}
            response_data.version = 'v1.0.0'

            headers = service.get_cors_headers_for_request(response_data)

            assert "Access-Control-Allow-Origin" in headers
            assert "Access-Control-Allow-Methods" in headers

    def test_proxy__cors__service__is_preflight_request(self):    # Test preflight detection
        service = Proxy__CORS__Service()

        # OPTIONS request
        with Schema__Proxy__Response_Data() as response_data:
            response_data.request = {'method': 'OPTIONS'}
            response_data.debug_params = {}
            response_data.response = {}
            response_data.stats = {}
            response_data.version = 'v1.0.0'

            assert service.is_preflight_request(response_data) is True

        # GET request
        with Schema__Proxy__Response_Data() as response_data:
            response_data.request = {'method': 'GET'}
            response_data.debug_params = {}
            response_data.response = {}
            response_data.stats = {}
            response_data.version = 'v1.0.0'

            assert service.is_preflight_request(response_data) is False

    def test_proxy__cors__service__handle_preflight_request(self):  # Test preflight handling
        service = Proxy__CORS__Service()

        with Schema__Proxy__Response_Data() as response_data:
            response_data.request = {'method': 'OPTIONS'}
            response_data.debug_params = {}
            response_data.response = {}
            response_data.stats = {}
            response_data.version = 'v1.0.0'

            headers = service.handle_preflight_request(response_data)

            assert "Access-Control-Allow-Origin" in headers
            assert headers["Content-Length"] == "0"