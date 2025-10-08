from unittest                                                                   import TestCase
from unittest.mock                                                              import patch, Mock
from mgraph_ai_service_mitmproxy.schemas.proxy.enums.Enum__WCF__Command_Type    import Enum__WCF__Command_Type
from mgraph_ai_service_mitmproxy.schemas.proxy.enums.Enum__WCF__Content_Type    import Enum__WCF__Content_Type
from mgraph_ai_service_mitmproxy.schemas.wcf.Schema__WCF__Request               import Schema__WCF__Request
from mgraph_ai_service_mitmproxy.service.wcf.Proxy__WCF__Service                import Proxy__WCF__Service


class test_Proxy__WCF__Service(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.service = Proxy__WCF__Service()

    def test__init__(self):                                      # Test initialization
        with self.service as _:
            assert type(_) is Proxy__WCF__Service
            assert _.wcf_base_url == "https://dev.web-content-filtering.mgraph.ai"
            assert _.timeout == 30

    def test_create_request(self):                               # Test request creation
        with self.service.create_request(command_type = Enum__WCF__Command_Type.url_to_html,
                                         target_url   = "https://example.com"              ) as request:
            assert type(request) is Schema__WCF__Request
            assert request.command_type == Enum__WCF__Command_Type.url_to_html
            assert request.target_url == "https://example.com"
            assert request.rating is None
            assert request.model_to_use is None

    def test_create_request_with_rating(self):                   # Test request with rating
        with self.service.create_request(
            command_type = Enum__WCF__Command_Type.url_to_html_min_rating,
            target_url   = "https://example.com",
            rating       = 0.5
        ) as request:
            assert request.rating == 0.5

    def test_create_request_with_model(self):                    # Test request with model
        with self.service.create_request(
            command_type = Enum__WCF__Command_Type.url_to_ratings,
            target_url   = "https://example.com",
            model_to_use = "google/gemini-2.0-flash-lite-001"
        ) as request:
            assert request.model_to_use == "google/gemini-2.0-flash-lite-001"

    @patch('mgraph_ai_service_mitmproxy.service.proxy.Proxy__WCF__Service.requests.get')
    def test_make_request__success_html(self, mock_get):         # Test successful HTML request
        # Mock HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'text/html; charset=utf-8'}
        mock_response.content = b'<html><body>Test</body></html>'
        mock_get.return_value = mock_response

        # Create request
        with self.service.create_request(
            command_type = Enum__WCF__Command_Type.url_to_html,
            target_url   = "https://example.com"
        ) as wcf_request:
            # Make request
            with self.service.make_request(wcf_request) as response:
                assert response.status_code == 200
                assert response.content_type == Enum__WCF__Content_Type.text_html
                assert response.body == '<html><body>Test</body></html>'
                assert response.success is True
                assert response.error_message is None

    @patch('mgraph_ai_service_mitmproxy.service.proxy.Proxy__WCF__Service.requests.get')
    def test_make_request__success_json(self, mock_get):         # Test successful JSON request
        # Mock HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'application/json'}
        mock_response.json.return_value = {'key': 'value'}
        mock_response.content = b'{"key": "value"}'
        mock_get.return_value = mock_response

        # Create request
        with self.service.create_request(
            command_type = Enum__WCF__Command_Type.url_to_json,
            target_url   = "https://example.com"
        ) as wcf_request:
            # Make request
            with self.service.make_request(wcf_request) as response:
                assert response.status_code == 200
                assert response.content_type == Enum__WCF__Content_Type.application_json
                assert response.is_json() is True
                assert response.success is True

    @patch('mgraph_ai_service_mitmproxy.service.proxy.Proxy__WCF__Service.requests.get')
    def test_make_request__timeout(self, mock_get):              # Test timeout handling
        import requests
        mock_get.side_effect = requests.Timeout("Connection timeout")

        # Create request
        with self.service.create_request(
            command_type = Enum__WCF__Command_Type.url_to_html,
            target_url   = "https://example.com"
        ) as wcf_request:
            # Make request
            with self.service.make_request(wcf_request) as response:
                assert response.status_code == 504
                assert response.success is False
                assert "timeout" in response.error_message.lower()

    @patch('mgraph_ai_service_mitmproxy.service.proxy.Proxy__WCF__Service.requests.get')
    def test_make_request__request_exception(self, mock_get):    # Test request exception
        import requests
        mock_get.side_effect = requests.RequestException("Network error")

        # Create request
        with self.service.create_request(
            command_type = Enum__WCF__Command_Type.url_to_html,
            target_url   = "https://example.com"
        ) as wcf_request:
            # Make request
            with self.service.make_request(wcf_request) as response:
                assert response.status_code == 502
                assert response.success is False
                assert "failed" in response.error_message.lower()

    def test_process_show_command__not_wcf_command(self):        # Test non-WCF command
        result = self.service.process_show_command(
            show_value = "response-data",
            target_url = "https://example.com"
        )

        assert result is None

    @patch('mgraph_ai_service_mitmproxy.service.proxy.Proxy__WCF__Service.requests.get')
    def test_process_show_command__url_to_html(self, mock_get):  # Test url-to-html command
        # Mock HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'text/html; charset=utf-8'}
        mock_response.content = b'<html>Processed</html>'
        mock_get.return_value = mock_response

        with self.service.process_show_command(
            show_value = "url-to-html",
            target_url = "https://example.com"
        ) as response:
            assert response is not None
            assert response.success is True
            assert response.is_html() is True

    @patch('mgraph_ai_service_mitmproxy.service.proxy.Proxy__WCF__Service.requests.get')
    def test_process_show_command__min_rating(self, mock_get):   # Test min-rating command
        # Mock HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'text/html; charset=utf-8'}
        mock_response.content = b'<html>Filtered</html>'
        mock_get.return_value = mock_response

        with self.service.process_show_command(
            show_value = "url-to-html-min-rating:0.7",
            target_url = "https://example.com"
        ) as response:
            assert response is not None
            assert response.success is True

            # Verify rating was added to URL
            call_args = mock_get.call_args
            called_url = call_args[1]['url']
            assert 'rating=0.7' in called_url or '&rating=0.7' in called_url

    @patch('mgraph_ai_service_mitmproxy.service.proxy.Proxy__WCF__Service.requests.get')
    def test_process_show_command__ratings_with_model(self, mock_get):  # Test ratings command
        # Mock HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'application/json'}
        mock_response.json.return_value = {'ratings': []}
        mock_response.content = b'{"ratings": []}'
        mock_get.return_value = mock_response

        with self.service.process_show_command(
            show_value = "url-to-ratings",
            target_url = "https://example.com"
        ) as response:
            assert response is not None
            assert response.success is True

            # Verify model was added to URL
            call_args = mock_get.call_args
            called_url = call_args[1]['url']
            assert 'model_to_use=google/gemini-2.0-flash-lite-001' in called_url