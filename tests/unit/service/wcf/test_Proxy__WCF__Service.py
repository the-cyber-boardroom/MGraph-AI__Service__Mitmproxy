import pytest
from unittest                                                           import TestCase
from osbot_utils.testing.__                                             import __, __SKIP__
from osbot_utils.utils.Env                                              import in_github_action
from mgraph_ai_service_mitmproxy.schemas.proxy.Enum__WCF__Command_Type  import Enum__WCF__Command_Type
from mgraph_ai_service_mitmproxy.schemas.proxy.Enum__WCF__Content_Type  import Enum__WCF__Content_Type
from mgraph_ai_service_mitmproxy.schemas.wcf.Schema__WCF__Request       import Schema__WCF__Request
from mgraph_ai_service_mitmproxy.schemas.wcf.Schema__WCF__Response      import Schema__WCF__Response
from mgraph_ai_service_mitmproxy.service.wcf.Proxy__WCF__Service        import Proxy__WCF__Service


class test_Proxy__WCF__Service(TestCase):

    @classmethod
    def setUpClass(cls):
        if in_github_action():
            pytest.skip("Skipping on github action because the server is not stopping and after all tests pass, the gh action hangs")
        cls.service = Proxy__WCF__Service().setup()
        if Schema__WCF__Request().get_auth_headers() == {}:
            pytest.skip("Skipping theses tests because WCF__Request auth is not available")

    def test__init__(self):                                      # Test initialization
        with self.service as _:
            assert type(_) is Proxy__WCF__Service
            assert _.wcf_base_url == "https://dev.web-content-filtering.mgraph.ai"
            assert _.timeout == 90.0

    def test_create_request(self):                               # Test request creation
        with self.service.create_request(command_type = Enum__WCF__Command_Type.url_to_html,
                                         target_url   = "https://example.com"              ) as request:
            assert type(request) is Schema__WCF__Request
            assert request.command_type == Enum__WCF__Command_Type.url_to_html
            assert request.target_url == "https://example.com"
            assert request.rating is None
            assert request.model_to_use is None

    def test_create_request_with_rating(self):                   # Test request with rating
        with self.service.create_request(command_type = Enum__WCF__Command_Type.url_to_html_min_rating,
                                         target_url   = "https://example.com",
                                         rating       = 0.5 ) as request:
            assert request.rating == 0.5

    def test_create_request_with_model(self):                    # Test request with model
        with self.service.create_request(command_type = Enum__WCF__Command_Type.url_to_ratings,
                                         target_url   = "https://example.com",
                                         model_to_use = "google/gemini-2.0-flash-lite-001") as request:
            assert request.model_to_use == "google/gemini-2.0-flash-lite-001"

    def test_make_request__success_html(self, ):         # Test successful HTML request
        # # Mock HTTP response
        # mock_response = Mock()
        # mock_response.status_code = 200
        # mock_response.headers = {'content-type': 'text/html; charset=utf-8'}
        # mock_response.content = b'<html><body>Test</body></html>'
        # mock_get.return_value = mock_response

        # Create request
        with self.service.create_request(
            command_type = Enum__WCF__Command_Type.url_to_html,
            target_url   = "https://example.com"
        ) as wcf_request:
            # Make request
            with self.service.make_request(wcf_request) as response:
                assert response.status_code == 200
                assert response.content_type == Enum__WCF__Content_Type.text_html
                assert response.body.index("<title>Example Domain</title>") > 30
                assert response.success is True
                assert response.error_message is None

    def test_make_request__success_json(self):         # Test successful JSON request

        # Create request
        with self.service.create_request(command_type = Enum__WCF__Command_Type.url_to_text_nodes,
                                         target_url   = "https://example.com"               ) as wcf_request:

            with self.service.make_request(wcf_request) as response:

                assert type(response) is Schema__WCF__Response

                assert response.obj() == __(success       = True              ,
                                            error_message = None              ,
                                            status_code   = 200               ,
                                            content_type  = 'application/json',
                                            body          = __SKIP__          ,
                                            headers       = __SKIP__          )


                assert response.status_code  == 200
                assert response.content_type == Enum__WCF__Content_Type.application_json
                assert response.is_json()    is True
                assert response.success      is True

    def test_make_request__success_json__url_to_lines(self):         # Test successful JSON request

        # Create request
        with self.service.create_request(command_type = Enum__WCF__Command_Type.url_to_lines,
                                         target_url   = "https://example.com"               ) as wcf_request:

            with self.service.make_request(wcf_request) as response:

                assert type(response) is Schema__WCF__Response

                assert response.obj() == __(success       = True    ,
                                            error_message = None    ,
                                            status_code   = 200     ,
                                            content_type  = __SKIP__,
                                            headers       = __SKIP__,
                                            body          = __SKIP__)


                assert response.status_code     == 200
                assert response.content_type    == Enum__WCF__Content_Type.text_plain
                assert response.is_json()       is False
                assert response.success         is True


    def test_process_show_command__not_wcf_command(self):        # Test non-WCF command
        result = self.service.process_show_command(show_value = "response-data"      ,
                                                   target_url = "https://example.com")

        assert result is None


    def test_process_show_command__url_to_html(self):                       # Test url-to-html command
        with self.service.process_show_command(show_value = "url-to-html"        ,
                                               target_url = "https://example.com") as response:
            assert response is not None
            assert response.success is True
            assert response.is_html() is True


    def test_process_show_command__min_rating(self):   # Test min-rating command
        pytest.skip("need a better target urls, since example.com and httpbin are not being very reliable")
        with self.service.process_show_command(show_value = "url-to-html-min-rating:0.7",
                                               target_url = "https://example.com"       ) as response:
            assert response         is not None

            assert response.success is True
            assert type(response)   is Schema__WCF__Response
            assert response.obj() == __(success       = True                        ,
                                        error_message = None                        ,
                                        status_code   = 200                         ,
                                        content_type  = 'text/html; charset=utf-8'  ,
                                        body          = __SKIP__                    ,
                                        headers       = __SKIP__                    )

            # Verify rating was added to URL
            # call_args = mock_get.call_args
            # called_url = call_args[1]['url']
            # assert 'rating=0.7' in called_url or '&rating=0.7' in called_url