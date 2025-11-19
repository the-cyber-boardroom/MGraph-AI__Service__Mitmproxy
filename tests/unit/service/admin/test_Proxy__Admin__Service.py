from unittest                                                                   import TestCase
from mgraph_ai_service_mitmproxy.service.admin.Proxy__Admin__Service            import Proxy__Admin__Service
from mgraph_ai_service_mitmproxy.service.proxy.Proxy__Cookie__Service           import Proxy__Cookie__Service
from mgraph_ai_service_mitmproxy.service.proxy.Proxy__Stats__Service            import Proxy__Stats__Service
from mgraph_ai_service_mitmproxy.schemas.proxy.Schema__Proxy__Stats             import Schema__Proxy__Stats
from mgraph_ai_service_mitmproxy.schemas.proxy.Schema__Proxy__Request_Data      import Schema__Proxy__Request_Data
from pathlib                                                                    import Path
import json


class test_Proxy__Admin__Service(TestCase):

    def setUp(self):                                                            # Setup test fixtures
        self.stats_service  = Proxy__Stats__Service(stats=Schema__Proxy__Stats())
        self.cookie_service = Proxy__Cookie__Service()
        self.admin_service  = Proxy__Admin__Service(cookie_service = self.cookie_service,
                                                     stats_service  = self.stats_service ).setup()

    def test__init__(self):                                                     # Test service initialization
        assert type(self.admin_service)                is Proxy__Admin__Service
        assert type(self.admin_service.cookie_service) is Proxy__Cookie__Service
        assert type(self.admin_service.stats_service)  is Proxy__Stats__Service
        assert self.admin_service.current_version       == "v0.1.1"
        assert isinstance(self.admin_service.admin_ui_root, Path)

    def test__is_admin_path(self):                                              # Test admin path detection
        # Positive cases
        assert self.admin_service.is_admin_path('/mitm-proxy'              )  is True
        assert self.admin_service.is_admin_path('/mitm-proxy/'             )  is True
        assert self.admin_service.is_admin_path('/mitm-proxy/v0/v0.1.0'    )  is True
        assert self.admin_service.is_admin_path('/mitm-proxy/admin-ui.json') is True

        # Negative cases
        assert self.admin_service.is_admin_path('/'            )        is False
        assert self.admin_service.is_admin_path('/regular/path')        is False
        assert self.admin_service.is_admin_path('/api/endpoint')        is False
        assert self.admin_service.is_admin_path('/mitm-prox'   )        is False  # Typo
        assert self.admin_service.is_admin_path('mitm-proxy'   )        is False  # Missing leading slash

    def test__redirect_to_latest(self):                                         # Test root redirect
        result = self.admin_service.redirect_to_latest()

        assert type(result)               is dict
        assert result['status_code']      == 302
        assert 'Location'                 in result['headers']
        assert result['headers']['Location'] == f"/mitm-proxy/v0/{self.admin_service.current_version}/index.html"
        assert 'text/html'                in result['headers']['content-type']
        assert 'meta http-equiv="refresh"' in result['body']

    def test__handle_admin_request__root(self):                                 # Test root path redirect
        request_data = Schema__Proxy__Request_Data(method       = 'GET'             ,
                                                    host         = 'test.example.com',
                                                    path         = '/mitm-proxy'     ,
                                                    headers      = {}                ,
                                                    stats        = {}                ,
                                                    version      = 'v1.0.0'          )

        result = self.admin_service.handle_admin_request(request_data)

        assert result is not None
        assert result['status_code'] == 302                                     # Redirect

    def test__handle_admin_request__root_with_slash(self):                      # Test root path with trailing slash
        request_data = Schema__Proxy__Request_Data(method       = 'GET'             ,
                                                    host         = 'test.example.com',
                                                    path         = '/mitm-proxy/'    ,
                                                    headers      = {}                ,
                                                    stats        = {}                ,
                                                    version      = 'v1.0.0'          )

        result = self.admin_service.handle_admin_request(request_data)

        assert result is not None
        assert result['status_code'] == 302                                     # Redirect

    def test__handle_admin_request__json_api(self):                             # Test JSON API endpoint
        request_data = Schema__Proxy__Request_Data(method       = 'GET'                   ,
                                                    host         = 'test.example.com'      ,
                                                    path         = '/mitm-proxy/admin-ui.json',
                                                    headers      = {}                      ,
                                                    stats        = {}                      ,
                                                    version      = 'v1.0.0'                )

        result = self.admin_service.handle_admin_request(request_data)

        assert result is not None
        assert result['status_code']  == 200
        assert 'application/json'     in result['headers']['content-type']
        assert 'no-cache'             in result['headers']['cache-control']

        # Parse and validate JSON response
        data = json.loads(result['body'])
        assert 'stats'                in data
        assert 'cookies'              in data
        assert 'request'              in data
        assert 'server'               in data
        assert 'timestamp'            in data

    def test__handle_admin_request__static_file(self):                          # Test static file path
        request_data = Schema__Proxy__Request_Data(method       = 'GET'                              ,
                                                   host         = 'test.example.com'                ,
                                                   path         = '/mitm-proxy/v0/v0.1.0/index.html',
                                                   headers      = {}                                ,
                                                   stats        = {}                                ,
                                                   version      = 'v1.0.0'                          )

        result = self.admin_service.handle_admin_request(request_data)

        assert result                is not None
        assert result['status_code'] == 200

    def test__handle_admin_request__non_admin_path(self):                         # Test non-admin path returns None
        request_data = Schema__Proxy__Request_Data(method       = 'GET'             ,
                                                    host         = 'test.example.com',
                                                    path         = '/api/data'       ,
                                                    headers      = {}                ,
                                                    stats        = {}                ,
                                                    version      = 'v1.0.0'          )

        result = self.admin_service.handle_admin_request(request_data)

        assert result is None                                                   # Non-admin paths return None

    def test__serve_admin_data(self):                                             # Test JSON API data structure
        self.stats_service.stats.total_requests       = 42
        self.stats_service.stats.total_responses      = 40
        self.stats_service.stats.total_bytes_processed = 123456

        request_data = Schema__Proxy__Request_Data(
            method       = 'GET'                   ,
            host         = 'example.com'           ,
            path         = '/mitm-proxy/admin-ui.json',
            headers      = { 'Cookie': 'mitm-show=url-to-html-xxx; mitm-debug=true'},
            stats        = {}                      ,
            version      = 'v1.0.0'                )

        result = self.admin_service.serve_admin_data(request_data)

        assert result['status_code']  == 200
        assert 'application/json'     in result['headers']['content-type']

        data = json.loads(result['body'])

        # Verify stats
        assert data['stats']['total_requests']        == 42
        assert data['stats']['total_responses']       == 40
        assert data['stats']['total_bytes_processed'] == 123456

        # Verify cookies
        assert 'cookies'              in data
        assert 'active'               in data['cookies']
        assert 'count'                in data['cookies']
        assert 'summary'              in data['cookies']
        assert data['cookies']['count'] == 2                                    # mitm-show and mitm-debug

        # Verify request info
        assert data['request']['host']   == 'example.com'
        assert data['request']['path']   == '/mitm-proxy/admin-ui.json'
        assert data['request']['method'] == 'GET'

        # Verify server info
        assert data['server']['version']            == '1.0.0'
        assert data['server']['current_ui_version'] == self.admin_service.current_version

        # Verify timestamp
        assert 'timestamp'            in data
        assert data['timestamp'].endswith('Z')                                  # ISO format with Z

    def test__serve_404__with_custom_404(self):                                # Test 404 page
        result = self.admin_service.serve_404('/mitm-proxy/nonexistent')

        assert result['status_code']  == 404
        assert 'text/html'            in result['headers']['content-type']
        assert '404'                  in result['body']
        #assert '/mitm-proxy/nonexistent' in result['body']
        assert 'Not Found'            in result['body']

    def test__get_content_type(self):                                           # Test content type mapping
        assert self.admin_service.get_content_type('.html') == 'text/html; charset=utf-8'
        assert self.admin_service.get_content_type('.css')  == 'text/css; charset=utf-8'
        assert self.admin_service.get_content_type('.js')   == 'application/javascript; charset=utf-8'
        assert self.admin_service.get_content_type('.json') == 'application/json; charset=utf-8'
        assert self.admin_service.get_content_type('.png')  == 'image/png'
        assert self.admin_service.get_content_type('.jpg')  == 'image/jpeg'
        assert self.admin_service.get_content_type('.jpeg') == 'image/jpeg'
        assert self.admin_service.get_content_type('.gif')  == 'image/gif'
        assert self.admin_service.get_content_type('.svg')  == 'image/svg+xml'
        assert self.admin_service.get_content_type('.ico')  == 'image/x-icon'
        assert self.admin_service.get_content_type('.txt')  == 'text/plain; charset=utf-8'
        assert self.admin_service.get_content_type('.md')   == 'text/markdown; charset=utf-8'
        assert self.admin_service.get_content_type('.xyz')  == 'application/octet-stream'  # Unknown type

    def test__serve_static_file__security(self):                                  # Test path traversal security
        # Attempt path traversal
        result = self.admin_service.serve_static_file('/mitm-proxy/../../../etc/passwd')

        assert result['status_code'] == 404                                     # Security check prevents access

    def test__serve_static_file__nonexistent(self):                               # Test nonexistent file
        result = self.admin_service.serve_static_file('/mitm-proxy/nonexistent.html')

        assert result['status_code'] == 404

    def test__multiple_cookie_types(self):                                      # Test JSON API with multiple cookies
        request_data = Schema__Proxy__Request_Data(
            method       = 'GET'                   ,
            host         = 'example.com'           ,
            path         = '/mitm-proxy/admin-ui.json',
            headers      = { 'Cookie': 'mitm-show=url-to-html-xxx; mitm-inject=debug-panel; mitm-rating=0.5' },
            stats        = {}                      ,
            version      = 'v1.0.0'                )

        result = self.admin_service.serve_admin_data(request_data)
        data = json.loads(result['body'])

        assert data['cookies']['count'] == 3
        assert 'mitm-show'              in data['cookies']['active']
        assert 'mitm-inject'            in data['cookies']['active']
        assert 'mitm-rating'            in data['cookies']['active']

    def test__no_cookies(self):                                                 # Test JSON API with no cookies
        request_data = Schema__Proxy__Request_Data(method       = 'GET'                   ,
                                                    host         = 'example.com'           ,
                                                    path         = '/mitm-proxy/admin-ui.json',
                                                    headers      = {}                      ,
                                                    stats        = {}                      ,
                                                    version      = 'v1.0.0'                )

        result = self.admin_service.serve_admin_data(request_data)
        data = json.loads(result['body'])

        assert data['cookies']['count']  == 0
        assert data['cookies']['active'] == {}

    def test__version_consistency(self):                                        # Test version information
        # Verify version used in redirect
        redirect = self.admin_service.redirect_to_latest()
        assert f'v0/{self.admin_service.current_version}' in redirect['headers']['Location']

        # Verify version in JSON API
        request_data = Schema__Proxy__Request_Data(method       = 'GET'                   ,
                                                    host         = 'example.com'           ,
                                                    path         = '/mitm-proxy/admin-ui.json',
                                                    headers      = {}                      ,
                                                    stats        = {}                      ,
                                                    version      = 'v1.0.0'                )

        result = self.admin_service.serve_admin_data(request_data)
        data = json.loads(result['body'])

        assert data['server']['current_ui_version'] == self.admin_service.current_version

    def test__stats_incrementation_not_affected(self):                          # Test stats service still works independently
        initial_requests = self.stats_service.stats.total_requests

        # Request admin data
        request_data = Schema__Proxy__Request_Data(method       = 'GET'                   ,
                                                    host         = 'example.com'           ,
                                                    path         = '/mitm-proxy/admin-ui.json',
                                                    headers      = {}                      ,
                                                    stats        = {}                      ,
                                                    version      = 'v1.0.0'                )

        self.admin_service.serve_admin_data(request_data)

        assert self.stats_service.stats.total_requests == initial_requests          # Stats should not auto-increment from admin data serving

        self.stats_service.increment_request(host='example.com', path='/test')      # But manual increment should still work
        assert self.stats_service.stats.total_requests == initial_requests + 1

    def test__response_headers(self):                                           # Test response headers are correct
        # Test redirect headers
        redirect = self.admin_service.redirect_to_latest()
        assert 'Location'     in redirect['headers']
        assert 'content-type' in redirect['headers']

        # Test JSON API headers
        request_data = Schema__Proxy__Request_Data(method       = 'GET'                   ,
                                                    host         = 'example.com'           ,
                                                    path         = '/mitm-proxy/admin-ui.json',
                                                    headers      = {}                      ,
                                                    stats        = {}                      ,
                                                    version      = 'v1.0.0'                )

        json_result = self.admin_service.serve_admin_data(request_data)
        assert 'content-type'  in json_result['headers']
        assert 'cache-control' in json_result['headers']
        assert json_result['headers']['cache-control'] == 'no-cache'            # Dev mode, no caching