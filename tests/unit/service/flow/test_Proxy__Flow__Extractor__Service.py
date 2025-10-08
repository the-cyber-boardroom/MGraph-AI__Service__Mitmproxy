from unittest                                                                 import TestCase
from unittest.mock                                                            import Mock
from mgraph_ai_service_mitmproxy.service.flow.Proxy__Flow__Extractor__Service import Proxy__Flow__Extractor__Service


class test_Proxy__Flow__Extractor__Service(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.service = Proxy__Flow__Extractor__Service()

    def test__init__(self):                                      # Test initialization
        assert type(self.service) is Proxy__Flow__Extractor__Service
        assert self.service.request_service is not None

    def test_extract_request_data(self):                         # Test request extraction
        # Create mock flow
        mock_flow = Mock()
        mock_flow.request.method = 'GET'
        mock_flow.request.host = 'example.com'
        mock_flow.request.port = 443
        mock_flow.request.path = '/test'
        mock_flow.request.scheme = 'https'
        mock_flow.request.headers = {'User-Agent': 'Test'}
        mock_flow.request.query_string = b'key=value'

        # Extract
        request_data = self.service.extract_request_data(mock_flow)

        assert request_data['method'] == 'GET'
        assert request_data['host'] == 'example.com'
        assert request_data['path'] == '/test'
        assert request_data['query_params'] == {'key': 'value'}

    def test_extract_debug_params(self):                         # Test debug param extraction
        # Create mock flow
        mock_flow = Mock()
        mock_flow.request.method = 'GET'
        mock_flow.request.host = 'example.com'
        mock_flow.request.port = 443
        mock_flow.request.path = '/test'
        mock_flow.request.scheme = 'https'
        mock_flow.request.headers = {}
        mock_flow.request.query_string = b'show=url-to-html&page=1'

        # Extract
        debug_params = self.service.extract_debug_params(mock_flow)

        assert debug_params == {'show': 'url-to-html'}
        assert 'page' not in debug_params

    def test_extract_response_data(self):                        # Test response extraction
        # Create mock flow
        mock_flow = Mock()
        mock_flow.response.status_code = 200
        mock_flow.response.headers = {'content-type': 'text/html'}
        mock_flow.response.content = b'<html>Test</html>'

        # Extract
        response_data = self.service.extract_response_data(mock_flow)

        assert response_data['status_code'] == 200
        assert response_data['content_type'] == 'text/html'
        assert response_data['body'] == '<html>Test</html>'

    def test_extract_from_flow__success(self):                  # Test complete extraction
        # Create mock flow
        mock_flow = Mock()
        mock_flow.id = 'flow-123'
        mock_flow.request.method = 'GET'
        mock_flow.request.host = 'example.com'
        mock_flow.request.port = 443
        mock_flow.request.path = '/test'
        mock_flow.request.scheme = 'https'
        mock_flow.request.headers = {}
        mock_flow.request.query_string = b'debug=true'
        mock_flow.response.status_code = 200
        mock_flow.response.headers = {'content-type': 'text/html'}
        mock_flow.response.content = b'Test'

        # Extract
        result = self.service.extract_from_flow(mock_flow)

        assert type(result) is Schema__Flow__Extraction_Result
        assert result.extraction_success is True
        assert result.flow_id == 'flow-123'
        assert result.has_error() is False
        assert result.response_data.debug_params == {'debug': 'true'}

    def test_extract_from_flow__no_query_string(self):          # Test without query string
        # Create mock flow
        mock_flow = Mock()
        mock_flow.request.method = 'GET'
        mock_flow.request.host = 'example.com'
        mock_flow.request.port = 443
        mock_flow.request.path = '/test'
        mock_flow.request.scheme = 'https'
        mock_flow.request.headers = {}
        mock_flow.request.query_string = None
        mock_flow.response.status_code = 200
        mock_flow.response.headers = {}
        mock_flow.response.content = b''

        # Extract
        result = self.service.extract_from_flow(mock_flow)

        assert result.extraction_success is True
        assert result.response_data.debug_params == {}

    def test_has_debug_commands__true(self):                    # Test debug command detection
        # Create mock flow
        mock_flow = Mock()
        mock_flow.request.query_string = b'show=url-to-html'

        # Check
        has_debug = self.service.has_debug_commands(mock_flow)

        assert has_debug is True

    def test_has_debug_commands__false(self):                   # Test no debug commands
        # Create mock flow
        mock_flow = Mock()
        mock_flow.request.query_string = b'page=1'

        # Check
        has_debug = self.service.has_debug_commands(mock_flow)

        assert has_debug is False

    def test_has_debug_commands__no_query(self):                # Test with no query
        # Create mock flow
        mock_flow = Mock()
        mock_flow.request.query_string = None

        # Check
        has_debug = self.service.has_debug_commands(mock_flow)

        assert has_debug is False