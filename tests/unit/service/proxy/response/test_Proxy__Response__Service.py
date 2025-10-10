from unittest                                                                       import TestCase

import pytest
from osbot_utils.utils.Misc                                                         import list_set
from osbot_utils.utils.Objects                                                      import base_classes, __
from mgraph_ai_service_mitmproxy.service.proxy.response.Proxy__Response__Service    import Proxy__Response__Service
from mgraph_ai_service_mitmproxy.service.proxy.Proxy__Debug__Service                import Proxy__Debug__Service
from mgraph_ai_service_mitmproxy.service.proxy.Proxy__Stats__Service                import Proxy__Stats__Service
from mgraph_ai_service_mitmproxy.service.proxy.Proxy__CORS__Service                 import Proxy__CORS__Service
from mgraph_ai_service_mitmproxy.service.proxy.Proxy__Headers__Service              import Proxy__Headers__Service
from mgraph_ai_service_mitmproxy.service.proxy.Proxy__Cookie__Service               import Proxy__Cookie__Service
from mgraph_ai_service_mitmproxy.service.proxy.Proxy__HTML__Service                 import Proxy__HTML__Service
from mgraph_ai_service_mitmproxy.service.proxy.Proxy__JSON__Service                 import Proxy__JSON__Service
from mgraph_ai_service_mitmproxy.service.wcf.Proxy__WCF__Service                    import Proxy__WCF__Service
from mgraph_ai_service_mitmproxy.schemas.proxy.Schema__Proxy__Response_Data         import Schema__Proxy__Response_Data
from mgraph_ai_service_mitmproxy.schemas.proxy.Schema__Response__Processing_Result  import Schema__Response__Processing_Result
from mgraph_ai_service_mitmproxy.schemas.proxy.Schema__Proxy__Stats                 import Schema__Proxy__Stats
from mgraph_ai_service_mitmproxy.schemas.Schema__CORS__Config                       import Schema__CORS__Config


class test_Proxy__Response__Service(TestCase):

    @classmethod
    def setUpClass(cls):
        wcf_service     = Proxy__WCF__Service()                                               # WCF service
        html_service    = Proxy__HTML__Service()                                              # HTML service
        json_service    = Proxy__JSON__Service()                                              # JSON service
        cls.debug_service   = Proxy__Debug__Service(wcf_service  = wcf_service  ,
                                                     html_service = html_service ,
                                                     json_service = json_service )
        cls.stats_service   = Proxy__Stats__Service(stats=Schema__Proxy__Stats())
        cls.cors_service    = Proxy__CORS__Service(cors_config=Schema__CORS__Config())
        cls.headers_service = Proxy__Headers__Service()
        cls.cookie_service  = Proxy__Cookie__Service()

        cls.service = Proxy__Response__Service(debug_service   = cls.debug_service  ,
                                               stats_service   = cls.stats_service  ,
                                               cors_service    = cls.cors_service   ,
                                               headers_service = cls.headers_service,
                                               cookie_service  = cls.cookie_service )

        cls.test_response_basic = Schema__Proxy__Response_Data(                              # Basic response
            request      = {'method': 'GET', 'host': 'example.com', 'path': '/test', 'headers': {}},
            debug_params = {},
            response     = {'status_code': 200, 'content_type': 'text/html', 'body': '<html></html>', 'headers': {}},
            stats        = {},
            version      = 'v1.0.0'
        )

        cls.test_response_with_cookies = Schema__Proxy__Response_Data(                       # Response with cookies
            request      = {
                'method'  : 'GET',
                'host'    : 'example.com',
                'path'    : '/test',
                'headers' : {'cookie': 'mitm-show=response-data; mitm-debug=true'}
            },
            debug_params = {},                                                                 # Will be filled from cookies
            response     = {'status_code': 200, 'content_type': 'text/html', 'body': '<html></html>', 'headers': {}},
            stats        = {},
            version      = 'v1.0.0'
        )

    def setUp(self):                                                                          # Reset stats before each test
        self.stats_service.stats = Schema__Proxy__Stats()

    def test__init__(self):                                                                    # Test auto-initialization of Proxy__Response__Service
        with Proxy__Response__Service() as _:
            assert type(_)         is Proxy__Response__Service
            assert base_classes(_) == [Proxy__Response__Service.__bases__[0], object]

            assert type(_.debug_service)   is Proxy__Debug__Service
            assert type(_.stats_service)   is Proxy__Stats__Service
            assert type(_.cors_service)    is Proxy__CORS__Service
            assert type(_.headers_service) is Proxy__Headers__Service
            assert type(_.cookie_service)  is Proxy__Cookie__Service

    def test_generate_request_id(self):                                                       # Test request ID generation
        with self.service as _:
            id1 = _.generate_request_id()
            id2 = _.generate_request_id()

            assert id1.startswith('req-')
            assert id2.startswith('req-')
            assert id1 != id2                                                                  # IDs are unique
            assert len(id1) > 10                                                               # Has hex suffix

    def test_process_response(self):                                                          # Test basic response processing
        with self.service as _:
            result = _.process_response(self.test_response_basic)

            assert type(result) is Schema__Response__Processing_Result
            assert result.final_status_code    == 200
            assert result.final_content_type   == 'text/html'
            assert result.final_body          == '<html></html>'
            assert result.debug_mode_active   is False
            assert result.content_was_modified is False
            assert result.response_overridden  is False

    def test_process_response__increments_stats(self):                                        # Test stats are incremented
        initial_count = self.stats_service.stats.total_responses

        with self.service as _:
            _.process_response(self.test_response_basic)

            assert self.stats_service.stats.total_responses == initial_count + 1

    def test_process_response__standard_headers_added(self):                                  # Test standard headers are added
        with self.service as _:
            result = _.process_response(self.test_response_basic)

            assert 'x-proxy-service' in result.final_headers
            assert 'x-proxy-version' in result.final_headers
            assert 'x-request-id'    in result.final_headers
            assert 'x-processed-at'  in result.final_headers

    def test_process_response__with_cookies(self):                                            # Test processing with cookie-based debug params
        with self.service as _:
            result = _.process_response(self.test_response_with_cookies)

            assert 'x-proxy-cookie-summary' in result.final_headers                           # Cookie summary added
            assert result.debug_mode_active is True                                            # Debug mode from cookie

    def test_process_response__cookie_to_debug_params(self):                                  # Test cookies converted to debug_params
        with self.service as _:
            result = _.process_response(self.test_response_with_cookies)

            assert 'x-debug-mode' in result.final_headers                                     # Debug mode detected

    def test_process_response__cors_headers(self):                                            # Test CORS headers added
        with self.service as _:
            result = _.process_response(self.test_response_basic)

            assert 'access-control-allow-origin' in result.final_headers

    def test_process_response__content_length_header(self):                                   # Test content-length header
        with self.service as _:
            result = _.process_response(self.test_response_basic)

            assert 'content-length' in result.final_headers
            assert int(result.final_headers['content-length']) == len(result.final_body.encode('utf-8'))

    def test_process_response__content_type_header(self):                                     # Test content-type header
        with self.service as _:
            result = _.process_response(self.test_response_basic)

            assert 'content-type' in result.final_headers
            assert result.final_headers['content-type'] == 'text/html'

    def test_process_response__original_headers_preserved(self):                              # Test original response headers preserved
        response_with_headers = Schema__Proxy__Response_Data(
            request      = {'method': 'GET', 'host': 'example.com', 'path': '/test', 'headers': {}},
            debug_params = {},
            response     = {
                'status_code'  : 200,
                'content_type' : 'text/html',
                'body'         : '<html></html>',
                'headers'      : {'x-custom-header': 'custom-value', 'Server': 'nginx'}
            },
            stats        = {},
            version      = 'v1.0.0'
        )

        with self.service as _:
            result = _.process_response(response_with_headers)

            assert 'x-custom-header' in result.final_headers
            assert result.final_headers['x-custom-header'] == 'custom-value'

    def test_process_response__no_cache_headers_for_debug(self):                              # Test no-cache headers in debug mode
        response_with_debug = Schema__Proxy__Response_Data(
            request      = {'method': 'GET', 'host': 'example.com', 'path': '/test', 'headers': {}},
            debug_params = {'debug': 'true'},                                                  # Debug mode
            response     = {'status_code': 200, 'content_type': 'text/html', 'body': '<html></html>', 'headers': {}},
            stats        = {},
            version      = 'v1.0.0'
        )

        with self.service as _:
            result = _.process_response(response_with_debug)

            assert 'cache-control' in result.final_headers
            assert 'no-store' in result.final_headers['cache-control']

    def test_build_final_headers(self):                                                       # Test final headers building
        from mgraph_ai_service_mitmproxy.schemas.proxy.Schema__Proxy__Modifications import Schema__Proxy__Modifications

        modifications                   = Schema__Proxy__Modifications()
        modifications.headers_to_add    = {'x-custom': 'value'}
        modifications.headers_to_remove = ['x-remove-this']

        response_data = Schema__Proxy__Response_Data(
            request      = {'method': 'GET', 'host': 'example.com', 'path': '/test', 'headers': {}},
            debug_params = {},
            response     = { 'status_code'  : 200,
                             'content_type' : 'text/html',
                             'body'         : '<html></html>',
                             'headers'      : {'x-remove-this': 'should-be-removed', 'x-keep': 'keep-me'}},
            stats        = {},
            version      = 'v1.0.0'
        )

        with self.service as _:
            final_headers = _.build_final_headers(response_data  = response_data,
                                                  modifications  = modifications,
                                                  content_type   = 'text/html'  ,
                                                  content_length = 13           )

            assert 'x-custom'      in final_headers
            assert 'x-keep'        in final_headers
            assert 'x-remove-this' not in final_headers                                       # Removed
            assert 'content-type'   in final_headers
            assert 'content-length' in final_headers

    def test__preflight_request_handling(self):                                                # Test CORS preflight OPTIONS request
        preflight_response = Schema__Proxy__Response_Data(
            request      = {'method': 'OPTIONS', 'host': 'example.com', 'path': '/test', 'headers': {}},
            debug_params = {},
            response     = {'status_code': 200, 'content_type': 'text/plain', 'body': '', 'headers': {}},
            stats        = {},
            version      = 'v1.0.0'
        )

        with self.service as _:
            result = _.process_response(preflight_response)

            assert result.final_status_code == 204                                             # No Content for preflight
            assert result.final_body == ''
            assert 'access-control-allow-methods' in result.final_headers

    def test__error_result_creation(self):                                                     # Test error result creation
        response_data = self.test_response_basic

        with self.service as _:
            error_result = _._create_error_result(response_data, "Test error message")

            assert type(error_result) is Schema__Response__Processing_Result
            assert error_result.final_status_code == 500
            assert error_result.final_content_type == 'text/plain'
            assert 'Test error message' in error_result.final_body
            assert error_result.processing_error == "Test error message"
            assert 'X-Processing-Error' in error_result.final_headers

    def test__cookie_priority_over_existing_debug_params(self):                                # Test cookies override existing debug_params
        response_mixed = Schema__Proxy__Response_Data(
            request      = {
                'method'  : 'GET',
                'host'    : 'example.com',
                'path'    : '/test',
                'headers' : {'cookie': 'mitm-show=url-to-html'}                               # Cookie value
            },
            debug_params = {'show': 'url-to-text'},                                           # Query param value
            response     = {'status_code': 200, 'content_type': 'text/html', 'body': '<html></html>', 'headers': {}},
            stats        = {},
            version      = 'v1.0.0'
        )

        with self.service as _:
            result = _.process_response(response_mixed)

            # After processing, response_data.debug_params should have cookie value
            assert response_mixed.debug_params['show'] == 'url-to-html'                       # Cookie wins

    def test__multiple_cookies_processed(self):                                                # Test multiple proxy cookies processed together
        pytest.skip("needs fixing after adding cache support (also find a better side than example.com since that is not being very stable)")
        response_multi = Schema__Proxy__Response_Data(
            request      = {
                'method'  : 'GET',
                'host'    : 'example.com',
                'path'    : '/test',
                'headers' : {
                    'cookie': 'mitm-show=url-to-html; mitm-inject=debug-panel; '
                             'mitm-debug=true; mitm-rating=0.5'
                }
            },
            debug_params = {},
            response     = {'status_code': 200, 'content_type': 'text/html', 'body': '<html></html>', 'headers': {}},
            stats        = {},
            version      = 'v1.0.0'
        )

        with self.service as _:
            result = _.process_response(response_multi)

            assert 'x-proxy-cookie-summary' in result.final_headers                           # Cookie summary present
            assert result.debug_mode_active is True                                            # Debug from cookie

    def test__empty_response_body(self):                                                       # Test processing empty response body
        response_empty = Schema__Proxy__Response_Data(
            request      = {'method': 'GET', 'host': 'example.com', 'path': '/test', 'headers': {}},
            debug_params = {},
            response     = {'status_code': 204, 'content_type': 'text/plain', 'body': '', 'headers': {}},
            stats        = {},
            version      = 'v1.0.0'
        )

        with self.service as _:
            result = _.process_response(response_empty)
            assert list_set(result.final_headers) == ['access-control-allow-credentials',
                                                      'access-control-allow-headers',
                                                      'access-control-allow-methods',
                                                      'access-control-allow-origin',
                                                      'access-control-expose-headers',
                                                      'access-control-max-age',
                                                      'content-length',
                                                      'content-type',
                                                      'x-original-host',
                                                      'x-original-path',
                                                      'x-processed-at',
                                                      'x-proxy-service',
                                                      'x-proxy-version',
                                                      'x-request-id']
            assert result.final_body == ''
            assert result.final_status_code == 204
            assert result.final_headers['content-length'] == '0'

    def test__large_response_body(self):                                                       # Test processing large response body
        large_body = 'x' * 100000                                                              # 100KB body
        response_large = Schema__Proxy__Response_Data(
            request      = {'method': 'GET', 'host': 'example.com', 'path': '/test', 'headers': {}},
            debug_params = {},
            response     = {'status_code': 200, 'content_type': 'text/plain', 'body': large_body, 'headers': {}},
            stats        = {},
            version      = 'v1.0.0'
        )

        with self.service as _:
            result = _.process_response(response_large)

            assert result.final_body == large_body
            assert len(result.final_body) == 100000
            assert self.stats_service.stats.total_bytes_processed == 100000

    def test__json_response(self):                                                             # Test JSON response processing
        response_json = Schema__Proxy__Response_Data(
            request      = {'method': 'GET', 'host': 'api.example.com', 'path': '/data', 'headers': {}},
            debug_params = {},
            response     = {
                'status_code'  : 200,
                'content_type' : 'application/json',
                'body'         : '{"key": "value"}',
                'headers'      : {}
            },
            stats        = {},
            version      = 'v1.0.0'
        )

        with self.service as _:
            result = _.process_response(response_json)

            assert result.final_content_type == 'application/json'
            assert result.final_body == '{"key": "value"}'

    def test__processing_result_summary(self):                                                # Test processing result summary
        with self.service as _:
            result = _.process_response(self.test_response_basic)

            summary = result.get_summary()

            assert 'status_code'  in summary
            assert 'content_type' in summary
            assert 'body_size'    in summary
            assert 'headers_added' in summary
            assert 'debug_mode'   in summary
            assert 'modified'     in summary
            assert 'overridden'   in summary
            assert 'error'        in summary

    def test__debug_headers_added_when_debug_mode(self):                                      # Test debug headers added in debug mode
        response_debug = Schema__Proxy__Response_Data(
            request      = { 'method'  : 'GET',
                             'host'    : 'example.com',
                             'path'    : '/test',
                             'headers' : {'cookie': 'mitm-debug=true'} },
            debug_params = {},
            response     = {'status_code': 200, 'content_type': 'text/html', 'body': '<html></html>', 'headers': {}},
            stats        = {},
            version      = 'v1.0.0'
        )

        with self.service as _:
            result = _.process_response(response_debug)

            assert 'x-debug-mode' in result.final_headers
            assert result.final_headers['x-debug-mode'] == 'active'

    def test__timestamp_in_headers(self):                                                      # Test timestamp format in headers
        with self.service as _:
            result = _.process_response(self.test_response_basic)

            assert 'x-processed-at' in result.final_headers
            timestamp = result.final_headers['x-processed-at']
            assert 'T' in timestamp                                                            # ISO format
            assert timestamp.endswith('Z')                                                     # UTC indicator