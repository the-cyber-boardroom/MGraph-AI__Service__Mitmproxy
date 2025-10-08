from unittest                                                           import TestCase
from osbot_utils.testing.__                                             import __, __SKIP__
from mgraph_ai_service_mitmproxy.schemas.proxy.Enum__WCF__Command_Type  import Enum__WCF__Command_Type
from mgraph_ai_service_mitmproxy.schemas.proxy.Enum__WCF__Content_Type  import Enum__WCF__Content_Type
from mgraph_ai_service_mitmproxy.schemas.wcf.Schema__WCF__Request       import Schema__WCF__Request
from mgraph_ai_service_mitmproxy.schemas.wcf.Schema__WCF__Response      import Schema__WCF__Response
from mgraph_ai_service_mitmproxy.service.wcf.Proxy__WCF__Service        import Proxy__WCF__Service


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

                assert response.obj() == __(success=True,
                                            error_message=None,
                                            status_code=200,
                                            content_type='application/json',
                                            body='{\n'
                                                 '  "8753dff3c2": {\n'
                                                 '    "original_text": "Example Domain",\n'
                                                 '    "tag": "h1"\n'
                                                 '  },\n'
                                                 '  "187928c0c0": {\n'
                                                 '    "original_text": "This domain is for use in illustrative examples '
                                                 'in documents. You may use this\\n    domain in literature without '
                                                 'prior coordination or asking for permission.",\n'
                                                 '    "tag": "p"\n'
                                                 '  },\n'
                                                 '  "8c2cb83b0c": {\n'
                                                 '    "original_text": "More information...",\n'
                                                 '    "tag": "a"\n'
                                                 '  }\n'
                                                 '}',
                                            headers=__SKIP__)


                assert response.status_code == 200
                assert response.content_type == Enum__WCF__Content_Type.application_json
                assert response.is_json() is True
                assert response.success is True

    def test_make_request__success_json__url_to_lines(self):         # Test successful JSON request

        # Create request
        with self.service.create_request(command_type = Enum__WCF__Command_Type.url_to_lines,
                                         target_url   = "https://example.com"               ) as wcf_request:

            with self.service.make_request(wcf_request) as response:

                assert type(response) is Schema__WCF__Response

                assert response.obj() == __(success       = True,
                                            error_message = None,
                                            status_code   = 200,
                                            content_type  = 'text/plain; charset=utf-8',
                                            body          = 'html/n    ├── head\n'
                                                            '    │   ├── title\n'
                                                            '    │   │   └── TEXT: Example Domain\n'
                                                            '    │   ├── meta (charset="utf-8")\n'
                                                            '    │   ├── meta (http-equiv="Content-type" content="text/html; '
                                                            'charset=utf-8")\n'
                                                            '    │   ├── meta (name="viewport" content="width=device-width, '
                                                            'initial-scale=1")\n'
                                                            '    │   └── style (type="text/css")\n'
                                                            '    │       └── TEXT: body {\n'
                                                            '        background-color: #f0f0f2;\n'
                                                            '        margin: 0;\n'
                                                            '        padding: 0;\n'
                                                            '        font-family: -apple-system, system-ui, BlinkMacSystemFont, '
                                                            '"Segoe UI", "Open Sans", "Helvetica Neue", Helvetica, Arial, '
                                                            'sans-serif;\n'
                                                            '        \n'
                                                            '    }\n'
                                                            '    div {\n'
                                                            '        width: 600px;\n'
                                                            '        margin: 5em auto;\n'
                                                            '        padding: 2em;\n'
                                                            '        background-color: #fdfdff;\n'
                                                            '        border-radius: 0.5em;\n'
                                                            '        box-shadow: 2px 3px 7px 2px rgba(0,0,0,0.02);\n'
                                                            '    }\n'
                                                            '    a:link, a:visited {\n'
                                                            '        color: #38488f;\n'
                                                            '        text-decoration: none;\n'
                                                            '    }\n'
                                                            '    @media (max-width: 700px) {\n'
                                                            '        div {\n'
                                                            '            margin: 0 auto;\n'
                                                            '            width: auto;\n'
                                                            '        }\n'
                                                            '    }/n    └── body\n'
                                                            '        └── div\n'
                                                            '            ├── h1\n'
                                                            '            │   └── TEXT: Example Domain\n'
                                                            '            ├── p\n'
                                                            '            │   └── TEXT: This domain is for use in illustrative '
                                                            'examples in documents. You may use this\n'
                                                            '    domain in literature without prior coordination or asking for '
                                                            'permission.\n'
                                                            '            └── p\n'
                                                            '                └── a (href="https://www.iana.org/domains/example")\n'
                                                            '                    └── TEXT: More information...',
                                            headers=__SKIP__)


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