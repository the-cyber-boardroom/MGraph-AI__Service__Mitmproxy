from unittest                                                           import TestCase
from mgraph_ai_service_mitmproxy.schemas.debug.Schema__Debug__Params    import Schema__Debug__Params
from mgraph_ai_service_mitmproxy.schemas.proxy.Schema__Request__Info    import Schema__Request__Info

class test_Request_Schemas(TestCase):

    def test_schema__request__info__basic(self):                 # Test basic request info
        with Schema__Request__Info() as info:
            info.method = 'GET'
            info.host = 'example.com'
            info.port = 443
            info.path = '/api/test'
            info.url = 'https://example.com/api/test'
            info.scheme = 'https'
            info.headers = {'content-type': 'application/json'}
            info.query_params = {'key': 'value'}

            assert info.method == 'GET'
            assert info.host == 'example.com'
            assert info.is_https() is True
            assert info.is_get() is True
            assert info.has_query_params() is True

    def test_schema__request__info__is_methods(self):            # Test HTTP method checks
        with Schema__Request__Info() as info:
            info.method = 'GET'
            info.host = 'example.com'
            info.path = '/'
            info.url = 'https://example.com'
            info.headers = {}
            info.query_params = {}

            assert info.is_get() is True
            assert info.is_post() is False
            assert info.is_options() is False

        with Schema__Request__Info() as info:
            info.method = 'POST'
            info.host = 'example.com'
            info.path = '/'
            info.url = 'https://example.com'
            info.headers = {}
            info.query_params = {}

            assert info.is_get() is False
            assert info.is_post() is True

        with Schema__Request__Info() as info:
            info.method = 'OPTIONS'
            info.host = 'example.com'
            info.path = '/'
            info.url = 'https://example.com'
            info.headers = {}
            info.query_params = {}

            assert info.is_options() is True

    def test_schema__request__info__get_header(self):            # Test header retrieval
        with Schema__Request__Info() as info:
            info.method = 'GET'
            info.host = 'example.com'
            info.path = '/'
            info.url = 'https://example.com'
            info.headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'Test/1.0'
            }
            info.query_params = {}

            # Case-insensitive lookup
            assert info.get_header('content-type') == 'application/json'
            assert info.get_header('Content-Type') == 'application/json'
            assert info.get_header('user-agent') == 'Test/1.0'
            assert info.get_header('missing') is None

    def test_schema__request__info__to_dict(self):               # Test dict conversion
        with Schema__Request__Info() as info:
            info.method = 'GET'
            info.host = 'example.com'
            info.port = 443
            info.path = '/test'
            info.url = 'https://example.com/test'
            info.scheme = 'https'
            info.headers = {'key': 'value'}
            info.query_params = {'q': 'search'}

            data = info.to_dict()

            assert data['method'] == 'GET'
            assert data['host'] == 'example.com'
            assert data['port'] == 443
            assert data['path'] == '/test'
            assert data['url'] == 'https://example.com/test'
            assert data['scheme'] == 'https'
            assert data['headers'] == {'key': 'value'}
            assert data['query_params'] == {'q': 'search'}

    def test_schema__debug__params__from_query(self):            # Test parsing from query
        query_params = {
            'show': 'url-to-html',
            'debug': 'true',
            'inject': 'debug-panel',
            'other': 'value'
        }

        debug_params = Schema__Debug__Params.from_query_params(query_params)

        assert debug_params.show_value == 'url-to-html'
        assert debug_params.debug_enabled is True
        assert debug_params.inject_value == 'debug-panel'
        assert debug_params.replace_value is None
        assert 'other' not in debug_params.raw_params

    def test_schema__debug__params__has_methods(self):           # Test has_* methods
        query_params = {
            'show': 'response-data',
            'inject': 'debug-panel'
        }

        debug_params = Schema__Debug__Params.from_query_params(query_params)

        assert debug_params.has_debug_params() is True
        assert debug_params.has_show_command() is True
        assert debug_params.has_inject_command() is True
        assert debug_params.has_replace_command() is False
        assert debug_params.is_debug_mode() is False

    def test_schema__debug__params__debug_mode(self):            # Test debug mode detection
        # Test debug=true
        params1 = Schema__Debug__Params.from_query_params({'debug': 'true'})
        assert params1.is_debug_mode() is True

        # Test inject_debug=true
        params2 = Schema__Debug__Params.from_query_params({'inject_debug': 'true'})
        assert params2.is_debug_mode() is True

        # Test both false
        params3 = Schema__Debug__Params.from_query_params({'show': 'test'})
        assert params3.is_debug_mode() is False

    def test_schema__debug__params__get_command_names(self):     # Test command name listing
        query_params = {
            'show': 'url-to-html',
            'debug': 'true',
            'replace': 'old:new'
        }

        debug_params = Schema__Debug__Params.from_query_params(query_params)
        commands = debug_params.get_debug_command_names()

        assert 'show' in commands
        assert 'debug' in commands
        assert 'replace' in commands
        assert 'inject' not in commands
        assert len(commands) == 3

    def test_schema__debug__params__to_dict(self):               # Test dict conversion
        query_params = {
            'show': 'url-to-html',
            'debug': 'true'
        }

        debug_params = Schema__Debug__Params.from_query_params(query_params)
        data = debug_params.to_dict()

        assert data == {'show': 'url-to-html', 'debug': 'true'}

    def test_schema__debug__params__empty(self):                 # Test with no debug params
        debug_params = Schema__Debug__Params.from_query_params({})

        assert debug_params.has_debug_params() is False
        assert debug_params.has_show_command() is False
        assert debug_params.get_debug_command_names() == []