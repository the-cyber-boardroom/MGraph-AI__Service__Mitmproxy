from unittest                                                                        import TestCase
from mgraph_ai_service_mitmproxy.service.proxy.Proxy__HTML__Service                  import Proxy__HTML__Service
from mgraph_ai_service_mitmproxy.schemas.proxy.Schema__HTML__Injection               import Schema__HTML__Injection

class test_Proxy__HTML__Service(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.service = Proxy__HTML__Service()

    def test__init__(self):                                        # Test initialization
        assert type(self.service) is Proxy__HTML__Service

    def test_create_debug_banner(self):                            # Test banner creation
        debug_params = {'show': 'url-to-html', 'debug': 'true'}
        request_path = '/test/path'

        banner = self.service.create_debug_banner(debug_params, request_path)

        assert '🔧 DEBUG MODE' in banner
        assert '/test/path' in banner
        assert 'Params:' in banner

    def test_create_debug_panel(self):                             # Test panel creation
        request_info = {'method': 'GET', 'path': '/test'}
        response_info = {'headers': {'content-type': 'text/html'}}
        debug_params = {'debug': 'true'}

        panel = self.service.create_debug_panel(request_info, response_info, debug_params)

        assert '🔧 Debug Panel' in panel
        assert 'Request Info' in panel
        assert 'Response Headers' in panel
        assert 'Debug Params' in panel

    def test_inject_into_html__banner_after_body(self):            # Test banner injection after body
        html = '<html><body><h1>Test</h1></body></html>'

        with Schema__HTML__Injection() as injection:
            injection.inject_banner = True
            injection.banner_content = '<div>DEBUG BANNER</div>'

            result = self.service.inject_into_html(html, injection)

            assert result is not None
            assert 'DEBUG BANNER' in result
            assert result.index('DEBUG BANNER') < result.index('<h1>Test</h1>')
            assert injection.injection_applied is True

    def test_inject_into_html__panel_before_body_close(self):      # Test panel injection before body close
        html = '<html><body><h1>Test</h1></body></html>'

        with Schema__HTML__Injection() as injection:
            injection.inject_panel = True
            injection.panel_content = '<div>DEBUG PANEL</div>'

            result = self.service.inject_into_html(html, injection)

            assert result is not None
            assert 'DEBUG PANEL' in result
            assert result.index('DEBUG PANEL') > result.index('<h1>Test</h1>')
            assert injection.injection_applied is True

    def test_inject_into_html__both_banner_and_panel(self):        # Test both injections
        html = '<html><body><h1>Test</h1></body></html>'

        with Schema__HTML__Injection() as injection:
            injection.inject_banner = True
            injection.banner_content = '<div>BANNER</div>'
            injection.inject_panel = True
            injection.panel_content = '<div>PANEL</div>'

            result = self.service.inject_into_html(html, injection)

            assert result is not None
            assert 'BANNER' in result
            assert 'PANEL' in result
            assert injection.injection_applied is True

    def test_inject_into_html__no_injections(self):                # Test with no injections configured
        html = '<html><body><h1>Test</h1></body></html>'

        with Schema__HTML__Injection() as injection:
            result = self.service.inject_into_html(html, injection)

            assert result is None
            assert injection.injection_applied is False

    def test_apply_text_replacement(self):                         # Test text replacement
        content = 'Hello world, this is a test'

        result = self.service.apply_text_replacement(content, 'world', 'REPLACED')

        assert result is not None
        assert '[REPLACED]' in result
        assert 'world' not in result

    def test_apply_text_replacement__not_found(self):              # Test replacement with missing text
        content = 'Hello world'

        result = self.service.apply_text_replacement(content, 'missing', 'REPLACED')

        assert result is None

    def test_is_html_content(self):                                # Test HTML content detection
        assert self.service.is_html_content('text/html') is True
        assert self.service.is_html_content('text/html; charset=utf-8') is True
        assert self.service.is_html_content('application/json') is False
        assert self.service.is_html_content('') is False

    def test_is_json_content(self):                                # Test JSON content detection
        assert self.service.is_json_content('application/json') is True
        assert self.service.is_json_content('text/html') is False

    def test_is_text_content(self):                                # Test text content detection
        assert self.service.is_text_content('text/plain') is True
        assert self.service.is_text_content('text/html') is False