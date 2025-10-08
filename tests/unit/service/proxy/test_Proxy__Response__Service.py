from unittest                                                                        import TestCase
from unittest.mock                                                                   import Mock, patch
from mgraph_ai_service_mitmproxy.service.proxy.Proxy__Response__Service              import Proxy__Response__Service
from mgraph_ai_service_mitmproxy.schemas.proxy.Schema__Proxy__Response_Data          import Schema__Proxy__Response_Data
from mgraph_ai_service_mitmproxy.schemas.proxy.Schema__Response__Processing_Result   import Schema__Response__Processing_Result

class test_Proxy__Response__Service(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.service = Proxy__Response__Service()

    def test__init__(self):                                        # Test initialization
        with self.service as _:
            assert type(_) is Proxy__Response__Service
            assert _.debug_service is not None
            assert _.stats_service is not None
            assert _.cors_service is not None
            assert _.headers_service is not None

    def test_generate_request_id(self):                            # Test request ID generation
        request_id = self.service.generate_request_id()

        assert request_id.startswith("req-")
        assert len(request_id) > 4

    def test_process_response__regular(self):                      # Test regular response processing
        with Schema__Proxy__Response_Data() as response_data:
            response_data.request = {
                'method': 'GET',
                'host': 'example.com',
                'path': '/test'
            }
            response_data.debug_params = {}
            response_data.response = {
                'status_code': 200,
                'content_type': 'text/html',
                'body': '<html><body>Test</body></html>',
                'headers': {'content-type': 'text/html'}
            }
            response_data.stats = {}
            response_data.version = 'v1.0.0'

            result = self.service.process_response(response_data)

            assert type(result) is Schema__Response__Processing_Result
            assert result.final_status_code == 200
            assert result.final_content_type == 'text/html'
            assert 'Test' in result.final_body
            assert result.response_overridden is False
            assert result.content_was_modified is False
            assert "X-Proxy-Service" in result.final_headers

    def test_process_response__with_debug_mode(self):              # Test with debug mode
        with Schema__Proxy__Response_Data() as response_data:
            response_data.request = {
                'method': 'GET',
                'host': 'example.com',
                'path': '/test'
            }
            response_data.debug_params = {'debug': 'true'}
            response_data.response = {
                'status_code': 200,
                'content_type': 'text/html',
                'body': '<html><body>Test</body></html>',
                'headers': {}
            }
            response_data.stats = {}
            response_data.version = 'v1.0.0'

            result = self.service.process_response(response_data)

            assert result.debug_mode_active is True
            assert "X-Debug-Mode" in result.final_headers
            assert "🔧 DEBUG MODE" in result.final_body
            assert result.content_was_modified is True

    @patch.object(Proxy__Response__Service, 'debug_service')
    def test_process_response__with_override(self, mock_debug):    # Test with response override
        # Mock debug service to override response
        def mock_process(response_data, modifications):
            modifications.override_response = True
            modifications.override_status = 200
            modifications.override_content_type = 'application/json'
            modifications.modified_body = '{"overridden": true}'

        mock_debug.process_debug_commands = mock_process

        with Schema__Proxy__Response_Data() as response_data:
            response_data.request = {'method': 'GET'}
            response_data.debug_params = {'show': 'response-data'}
            response_data.response = {
                'status_code': 200,
                'content_type': 'text/html',
                'body': '<html>Original</html>',
                'headers': {}
            }
            response_data.stats = {}
            response_data.version = 'v1.0.0'

            result = self.service.process_response(response_data)

            assert result.response_overridden is True
            assert result.final_content_type == 'application/json'
            assert '{"overridden": true}' in result.final_body

    def test_process_response__preflight(self):                    # Test CORS preflight
        with Schema__Proxy__Response_Data() as response_data:
            response_data.request = {'method': 'OPTIONS'}
            response_data.debug_params = {}
            response_data.response = {
                'status_code': 200,
                'content_type': 'text/plain',
                'body': '',
                'headers': {}
            }
            response_data.stats = {}
            response_data.version = 'v1.0.0'

            result = self.service.process_response(response_data)

            assert result.final_status_code == 204
            assert result.final_body == ""
            assert "Access-Control-Allow-Origin" in result.final_headers

    def test_process_response__error_handling(self):               # Test error handling
        # Create invalid response data that will cause error
        with Schema__Proxy__Response_Data() as response_data:
            response_data.request = {}
            response_data.debug_params = {}
            response_data.response = None  # This will cause error
            response_data.stats = {}
            response_data.version = 'v1.0.0'

            result = self.service.process_response(response_data)

            assert result.has_error() is True
            assert result.final_status_code == 500
            assert "error" in result.final_body.lower()
            assert result.processing_error is not None

    def test_finalize_overridden_response(self):                   # Test override finalization
        with Schema__Proxy__Response_Data() as response_data:
            response_data.request = {}
            response_data.debug_params = {}
            response_data.response = {}
            response_data.stats = {}
            response_data.version = 'v1.0.0'

        from mgraph_ai_service_mitmproxy.schemas.proxy.Schema__Proxy__Modifications import Schema__Proxy__Modifications
        with Schema__Proxy__Modifications() as modifications:
            modifications.override_response = True
            modifications.override_status = 200
            modifications.override_content_type = 'text/plain'
            modifications.modified_body = 'Overridden content'

            result = self.service._finalize_overridden_response(
                response_data,
                modifications,
                "test-123"
            )

            assert result.response_overridden is True
            assert result.final_status_code == 200
            assert result.final_body == 'Overridden content'

    def test_build_final_headers(self):                            # Test header building
        with Schema__Proxy__Response_Data() as response_data:
            response_data.request = {}
            response_data.debug_params = {}
            response_data.response = {
                'headers': {'X-Original': 'value'}
            }
            response_data.stats = {}
            response_data.version = 'v1.0.0'

        from mgraph_ai_service_mitmproxy.schemas.proxy.Schema__Proxy__Modifications import Schema__Proxy__Modifications
        with Schema__Proxy__Modifications() as modifications:
            modifications.headers_to_add['X-Added'] = 'added-value'
            modifications.headers_to_remove.append('X-Original')

            headers = self.service._build_final_headers(
                response_data,
                modifications,
                'text/html',
                100
            )

            assert 'X-Added' in headers
            assert 'X-Original' not in headers
            assert headers['Content-Type'] == 'text/html'
            assert headers['Content-Length'] == '100'

    def test_response__processing_result__get_summary(self):       # Test result summary
        from mgraph_ai_service_mitmproxy.schemas.proxy.Schema__Proxy__Modifications import Schema__Proxy__Modifications

        with Schema__Response__Processing_Result() as result:
            result.modifications = Schema__Proxy__Modifications()
            result.final_status_code = 200
            result.final_content_type = 'text/html'
            result.final_body = 'Test content'
            result.final_headers = {'X-Test': 'value'}
            result.debug_mode_active = True
            result.content_was_modified = True
            result.response_overridden = False

            summary = result.get_summary()

            assert summary['status_code'] == 200
            assert summary['content_type'] == 'text/html'
            assert summary['body_size'] == len('Test content')
            assert summary['debug_mode'] is True
            assert summary['modified'] is True
            assert summary['overridden'] is False