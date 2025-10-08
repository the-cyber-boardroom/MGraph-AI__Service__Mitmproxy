from unittest                                                                  import TestCase
from unittest.mock                                                             import Mock

from mgraph_ai_service_mitmproxy.schemas.flow.Schema__Flow__Application_Result import Schema__Flow__Application_Result
from mgraph_ai_service_mitmproxy.schemas.flow.Schema__Flow__Extraction_Result  import Schema__Flow__Extraction_Result
from mgraph_ai_service_mitmproxy.service.flow.Proxy__Flow__Adapter__Service    import Proxy__Flow__Adapter__Service


class test_Proxy__Flow__Adapter__Service(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.service = Proxy__Flow__Adapter__Service()

    def test__init__(self):                                      # Test initialization
        with self.service as _:
            assert type(_) is Proxy__Flow__Adapter__Service
            assert _.extractor_service is not None
            assert _.applicator_service is not None
            assert _.response_service is not None

    def test_process_flow__success(self):                       # Test successful flow processing
        # Create mock flow
        mock_flow = Mock()
        mock_flow.id = 'test-flow'
        mock_flow.request.method = 'GET'
        mock_flow.request.host = 'example.com'
        mock_flow.request.port = 443
        mock_flow.request.path = '/test'
        mock_flow.request.scheme = 'https'
        mock_flow.request.headers = {}
        mock_flow.request.query_string = None
        mock_flow.response.status_code = 200
        mock_flow.response.headers = {'content-type': 'text/html'}
        mock_flow.response.content = b'Test'

        # Process
        extraction_result, application_result = self.service.process_flow(mock_flow)

        assert type(extraction_result) is Schema__Flow__Extraction_Result
        assert type(application_result) is Schema__Flow__Application_Result
        assert extraction_result.extraction_success is True
        assert application_result.application_success is True

    def test_process_flow__with_debug(self):                    # Test with debug commands
        # Create mock flow with debug
        mock_flow = Mock()
        mock_flow.request.method = 'GET'
        mock_flow.request.host = 'example.com'
        mock_flow.request.port = 443
        mock_flow.request.path = '/test'
        mock_flow.request.scheme = 'https'
        mock_flow.request.headers = {}
        mock_flow.request.query_string = b'debug=true'
        mock_flow.response.status_code = 200
        mock_flow.response.headers = {'content-type': 'text/html'}
        mock_flow.response.content = b'<html><body>Test</body></html>'

        # Process
        extraction_result, application_result = self.service.process_flow(mock_flow)

        assert extraction_result.response_data.debug_params == {'debug': 'true'}
        # Debug mode should modify content
        assert application_result.application_success is True

    def test_should_process_flow__true(self):                   # Test flow processing check
        # Create mock flow with debug
        mock_flow = Mock()
        mock_flow.request.query_string = b'show=url-to-html'

        should_process = self.service.should_process_flow(mock_flow)

        assert should_process is True

    def test_should_process_flow__false(self):                  # Test no processing needed
        # Create mock flow without debug
        mock_flow = Mock()
        mock_flow.request.query_string = b'page=1'

        should_process = self.service.should_process_flow(mock_flow)

        assert should_process is False

    def test_extract_only(self):                                # Test extraction without processing
        # Create mock flow
        mock_flow = Mock()
        mock_flow.request.method = 'GET'
        mock_flow.request.host = 'example.com'
        mock_flow.request.port = 443
        mock_flow.request.path = '/test'
        mock_flow.request.scheme = 'https'
        mock_flow.request.headers = {}
        mock_flow.request.query_string = b'key=value'
        mock_flow.response.status_code = 200
        mock_flow.response.headers = {}
        mock_flow.response.content = b''

        # Extract only
        result = self.service.extract_only(mock_flow)

        assert type(result) is Schema__Flow__Extraction_Result
        assert result.extraction_success is True

    def test_get_processing_summary(self):                      # Test summary generation
        # Create mock results
        with Schema__Flow__Extraction_Result() as ext_result:
            from mgraph_ai_service_mitmproxy.schemas.proxy.Schema__Proxy__Response_Data import Schema__Proxy__Response_Data
            ext_result.response_data = Schema__Proxy__Response_Data(
                request={}, debug_params={}, response={}, stats={}, version='v1.0.0'
            )
            ext_result.extraction_success = True
            ext_result.flow_id = 'test-123'

        with Schema__Flow__Application_Result() as app_result:
            app_result.application_success = True
            app_result.flow_id = 'test-123'

        # Get summary
        summary = self.service.get_processing_summary(ext_result, app_result)

        assert 'extraction' in summary
        assert 'application' in summary
        assert summary['flow_id'] == 'test-123'
        assert summary['overall_success'] is True