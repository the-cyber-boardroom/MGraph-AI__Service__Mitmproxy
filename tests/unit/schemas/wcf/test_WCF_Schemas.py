from unittest                                                            import TestCase
from mgraph_ai_service_mitmproxy.schemas.proxy.Enum__WCF__Command_Type   import Enum__WCF__Command_Type
from mgraph_ai_service_mitmproxy.schemas.proxy.Enum__WCF__Content_Type   import Enum__WCF__Content_Type
from mgraph_ai_service_mitmproxy.schemas.wcf.Schema__WCF__Request        import Schema__WCF__Request
from mgraph_ai_service_mitmproxy.schemas.wcf.Schema__WCF__Response       import Schema__WCF__Response


class test_WCF_Schemas(TestCase):

    def test_enum__wcf__command_type__from_show_param(self):  # Test command type parsing
        # Direct mapping
        assert Enum__WCF__Command_Type.from_show_param('url-to-html'    ) == Enum__WCF__Command_Type.url_to_html
        assert Enum__WCF__Command_Type.from_show_param('url-to-html-xxx') == Enum__WCF__Command_Type.url_to_html_xxx
        assert Enum__WCF__Command_Type.from_show_param('url-to-ratings' ) == Enum__WCF__Command_Type.url_to_ratings

        # Special case with parameter
        assert Enum__WCF__Command_Type.from_show_param('url-to-html-min-rating:0.5') == Enum__WCF__Command_Type.url_to_html_min_rating
        assert Enum__WCF__Command_Type.from_show_param('url-to-html-min-rating'    ) == Enum__WCF__Command_Type.url_to_html_min_rating

        # Unknown command
        assert Enum__WCF__Command_Type.from_show_param('unknown-command') is None

    def test_enum__wcf__command_type__is_wcf_command(self):   # Test WCF command detection
        # Valid WCF commands
        assert Enum__WCF__Command_Type.is_wcf_command('url-to-html') is True
        assert Enum__WCF__Command_Type.is_wcf_command('url-to-html-xxx') is True
        assert Enum__WCF__Command_Type.is_wcf_command('url-to-html-min-rating:0.5') is True
        assert Enum__WCF__Command_Type.is_wcf_command('url-to-ratings') is True

        # Non-WCF commands
        assert Enum__WCF__Command_Type.is_wcf_command('response-data') is False
        assert Enum__WCF__Command_Type.is_wcf_command('debug-panel') is False

    def test_enum__wcf__content_type__from_header(self):       # Test content type parsing
        # HTML
        assert Enum__WCF__Content_Type.from_header('text/html; charset=utf-8') == Enum__WCF__Content_Type.text_html
        assert Enum__WCF__Content_Type.from_header('text/html') == Enum__WCF__Content_Type.text_html

        # Plain text
        assert Enum__WCF__Content_Type.from_header('text/plain; charset=utf-8') == Enum__WCF__Content_Type.text_plain
        assert Enum__WCF__Content_Type.from_header('text/plain') == Enum__WCF__Content_Type.text_plain

        # JSON
        assert Enum__WCF__Content_Type.from_header('application/json') == Enum__WCF__Content_Type.application_json

        # Unknown
        assert Enum__WCF__Content_Type.from_header('image/png') == Enum__WCF__Content_Type.unknown
        assert Enum__WCF__Content_Type.from_header('') == Enum__WCF__Content_Type.unknown
        assert Enum__WCF__Content_Type.from_header(None) == Enum__WCF__Content_Type.unknown

    def test_schema__wcf__request__construct_url(self):        # Test URL construction
        with Schema__WCF__Request() as request:
            request.command_type = Enum__WCF__Command_Type.url_to_html
            request.target_url   = "https://example.com"

            url = request.construct_wcf_url()

            assert 'https://dev.web-content-filtering.mgraph.ai/html-graphs/url-to-html/' in url
            assert 'url=https://example.com' in url

    def test_schema__wcf__request__construct_url_with_rating(self):  # Test URL with rating
        with Schema__WCF__Request() as request:
            request.command_type = Enum__WCF__Command_Type.url_to_html_min_rating
            request.target_url   = "https://example.com"
            request.rating       = 0.5

            url = request.construct_wcf_url()

            assert 'rating=0.5' in url

    def test_schema__wcf__request__construct_url_with_model(self):    # Test URL with model
        with Schema__WCF__Request() as request:
            request.command_type = Enum__WCF__Command_Type.url_to_ratings
            request.target_url   = "https://example.com"
            request.model_to_use = "google/gemini-2.0-flash-lite-001"

            url = request.construct_wcf_url()

            assert 'model_to_use=google/gemini-2.0-flash-lite-001' in url

    def test_schema__wcf__request__get_auth_headers(self):     # Test auth headers
        with Schema__WCF__Request() as request:

            headers = request.get_auth_headers()

            assert type(headers) == dict

    def test_schema__wcf__response__is_html(self):              # Test HTML detection
        with Schema__WCF__Response() as response:
            response.status_code = 200
            response.content_type = Enum__WCF__Content_Type.text_html
            response.body = "<html></html>"

            assert response.is_html() is True
            assert response.is_json() is False
            assert response.is_plain_text() is False

    def test_schema__wcf__response__is_json(self):              # Test JSON detection
        with Schema__WCF__Response() as response:
            response.status_code = 200
            response.content_type = Enum__WCF__Content_Type.application_json
            response.body = '{"key": "value"}'

            assert response.is_html() is False
            assert response.is_json() is True
            assert response.is_plain_text() is False

    def test_schema__wcf__response__can_override_response(self):  # Test override check
        # Success case
        with Schema__WCF__Response() as response:
            response.status_code = 200
            response.content_type = Enum__WCF__Content_Type.text_html
            response.body = "<html></html>"
            response.success = True

            assert response.can_override_response() is True

        # Empty body
        with Schema__WCF__Response() as response:
            response.status_code = 200
            response.success = True
            response.body = ""

            assert response.can_override_response() is False

        # Failed request
        with Schema__WCF__Response() as response:
            response.status_code = 500
            response.success = False
            response.body = "error"

            assert response.can_override_response() is False