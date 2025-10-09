from unittest                                                                    import TestCase
from mgraph_ai_service_mitmproxy.service.admin.Proxy__Admin__Service            import Proxy__Admin__Service
from mgraph_ai_service_mitmproxy.service.proxy.Proxy__Cookie__Service           import Proxy__Cookie__Service
from mgraph_ai_service_mitmproxy.service.proxy.Proxy__Stats__Service            import Proxy__Stats__Service
from mgraph_ai_service_mitmproxy.schemas.proxy.Schema__Proxy__Stats             import Schema__Proxy__Stats
from mgraph_ai_service_mitmproxy.schemas.proxy.Schema__Proxy__Request_Data      import Schema__Proxy__Request_Data


class test_Proxy__Admin__Service(TestCase):

    def setUp(self):                                                            # Setup test fixtures
        self.stats_service  = Proxy__Stats__Service(stats=Schema__Proxy__Stats())
        self.cookie_service = Proxy__Cookie__Service()
        self.admin_service  = Proxy__Admin__Service(cookie_service = self.cookie_service,
                                                     stats_service  = self.stats_service )

    def test__init__(self):                                                     # Test service initialization
        assert type(self.admin_service)                is Proxy__Admin__Service
        assert type(self.admin_service.cookie_service) is Proxy__Cookie__Service
        assert type(self.admin_service.stats_service)  is Proxy__Stats__Service

    def test__is_admin_path(self):                                              # Test admin path detection
        # Positive cases
        assert self.admin_service.is_admin_path('/mitm-proxy')          is True
        assert self.admin_service.is_admin_path('/mitm-proxy/')         is True
        assert self.admin_service.is_admin_path('/mitm-proxy/cookies')  is True
        assert self.admin_service.is_admin_path('/mitm-proxy/settings') is True

        # Negative cases
        assert self.admin_service.is_admin_path('/')                    is False
        assert self.admin_service.is_admin_path('/regular/path')        is False
        assert self.admin_service.is_admin_path('/api/endpoint')        is False
        assert self.admin_service.is_admin_path('/mitm-prox')           is False  # Typo
        assert self.admin_service.is_admin_path('mitm-proxy')           is False  # Missing leading slash

    def test__get_admin_endpoint(self):                                         # Test endpoint extraction
        # Valid endpoints
        assert self.admin_service.get_admin_endpoint('/mitm-proxy')          == 'index'
        assert self.admin_service.get_admin_endpoint('/mitm-proxy/')         == 'index'
        assert self.admin_service.get_admin_endpoint('/mitm-proxy/cookies')  == 'cookies'
        assert self.admin_service.get_admin_endpoint('/mitm-proxy/settings') == 'settings'

        # Trailing slash handling
        assert self.admin_service.get_admin_endpoint('/mitm-proxy/cookies/') == 'cookies'

        # Invalid paths
        assert self.admin_service.get_admin_endpoint('/regular/path')        is None
        assert self.admin_service.get_admin_endpoint('/')                    is None

    def test__generate_dashboard_page__basic(self):                            # Test dashboard generation
        request_data = Schema__Proxy__Request_Data(method       = 'GET'             ,
                                                    host         = 'test.example.com',
                                                    path         = '/mitm-proxy/'    ,
                                                    headers      = {}                ,
                                                    debug_params = {}                ,
                                                    stats        = {}                ,
                                                    version      = '1.0.0'           )

        html = self.admin_service.generate_dashboard_page(request_data)

        assert type(html)                is str
        assert len(html)                 > 0
        assert 'Dashboard'               in html
        assert 'test.example.com'        in html
        assert 'DOCTYPE html'            in html
        assert 'Proxy Statistics'        in html
        assert 'Cookie Status'           in html
        assert 'Current Request'         in html

    def test__generate_dashboard_page__with_stats(self):                       # Test dashboard with statistics
        # Add some stats
        self.stats_service.stats.total_requests       = 42
        self.stats_service.stats.total_responses      = 40
        self.stats_service.stats.total_bytes_processed = 123456

        request_data = Schema__Proxy__Request_Data(method       = 'GET'             ,
                                                    host         = 'example.com'     ,
                                                    path         = '/mitm-proxy/'    ,
                                                    headers      = {}                ,
                                                    debug_params = {}                ,
                                                    stats        = {}                ,
                                                    version      = '1.0.0'           )

        html = self.admin_service.generate_dashboard_page(request_data)

        assert '42'     in html  # total_requests
        assert '40'     in html  # total_responses
        assert '123,456' in html  # bytes formatted with commas

    def test__generate_dashboard_page__with_cookies(self):                     # Test dashboard with active cookies
        request_data = Schema__Proxy__Request_Data(
            method       = 'GET'             ,
            host         = 'example.com'     ,
            path         = '/mitm-proxy/'    ,
            headers      = {
                'Cookie': 'mitm-show=url-to-html-xxx; mitm-debug=true'
            },
            debug_params = {}                ,
            stats        = {}                ,
            version      = '1.0.0'           )

        html = self.admin_service.generate_dashboard_page(request_data)

        assert 'mitm-show'       in html
        assert 'url-to-html-xxx' in html
        assert 'mitm-debug'      in html
        assert 'true'            in html

    def test__generate_cookies_page__basic(self):                              # Test cookie page generation
        request_data = Schema__Proxy__Request_Data(method       = 'GET'             ,
                                                    host         = 'example.com'     ,
                                                    path         = '/mitm-proxy/cookies',
                                                    headers      = {}                ,
                                                    debug_params = {}                ,
                                                    stats        = {}                ,
                                                    version      = '1.0.0'           )

        html = self.admin_service.generate_cookies_page(request_data)

        assert type(html)                  is str
        assert len(html)                   > 0
        assert 'Cookie Management'         in html
        assert 'example.com'               in html
        assert 'Set New Proxy Cookie'      in html
        assert 'Available Cookie Controls' in html
        assert 'mitm-show'                 in html
        assert 'mitm-inject'               in html
        assert 'mitm-debug'                in html

    def test__generate_cookies_page__with_active_cookies(self):                # Test cookie page with active cookies
        request_data = Schema__Proxy__Request_Data(
            method       = 'GET'                 ,
            host         = 'example.com'         ,
            path         = '/mitm-proxy/cookies' ,
            headers      = {
                'Cookie': 'mitm-show=url-to-html-xxx; mitm-rating=0.5; mitm-cache=true'
            },
            debug_params = {}                    ,
            stats        = {}                    ,
            version      = '1.0.0'               )

        html = self.admin_service.generate_cookies_page(request_data)

        # Check for active cookies in table
        assert 'mitm-show'       in html
        assert 'url-to-html-xxx' in html
        assert 'mitm-rating'     in html
        assert '0.5'             in html
        assert 'mitm-cache'      in html
        assert 'true'            in html

        # Should show active cookies table, not empty state
        assert 'No proxy cookies are currently active' not in html

    def test__generate_cookies_page__empty_state(self):                        # Test cookie page with no cookies
        request_data = Schema__Proxy__Request_Data(method       = 'GET'                 ,
                                                    host         = 'example.com'         ,
                                                    path         = '/mitm-proxy/cookies' ,
                                                    headers      = {}                    ,
                                                    debug_params = {}                    ,
                                                    stats        = {}                    ,
                                                    version      = '1.0.0'               )

        html = self.admin_service.generate_cookies_page(request_data)

        assert 'No proxy cookies are currently active' in html

    def test__generate_404_page(self):                                          # Test 404 page generation
        request_data = Schema__Proxy__Request_Data(method       = 'GET'             ,
                                                    host         = 'example.com'     ,
                                                    path         = '/mitm-proxy/invalid',
                                                    headers      = {}                ,
                                                    debug_params = {}                ,
                                                    stats        = {}                ,
                                                    version      = '1.0.0'           )

        result = self.admin_service.generate_404_page(request_data, 'invalid')

        assert type(result)                is dict
        assert result['status_code']       == 404
        assert 'text/html'                 in result['headers']['Content-Type']
        assert 'X-Admin-Page'              in result['headers']
        assert result['headers']['X-Admin-Page'] == 'error-404'

        body = result['body']
        assert '404'                       in body
        assert 'Admin Page Not Found'      in body
        assert '/invalid'                  in body
        assert 'example.com'               in body

    def test__generate_admin_page__index(self):                                # Test admin page routing to index
        request_data = Schema__Proxy__Request_Data(method       = 'GET'             ,
                                                    host         = 'example.com'     ,
                                                    path         = '/mitm-proxy/'    ,
                                                    headers      = {}                ,
                                                    debug_params = {}                ,
                                                    stats        = {}                ,
                                                    version      = '1.0.0'           )

        result = self.admin_service.generate_admin_page(request_data, 'index')

        assert type(result)                is dict
        assert result['status_code']       == 200
        assert 'text/html'                 in result['headers']['Content-Type']
        assert result['headers']['X-Admin-Page'] == 'index'
        assert 'Dashboard'                 in result['body']

    def test__generate_admin_page__cookies(self):                              # Test admin page routing to cookies
        request_data = Schema__Proxy__Request_Data(method       = 'GET'                 ,
                                                    host         = 'example.com'         ,
                                                    path         = '/mitm-proxy/cookies' ,
                                                    headers      = {}                    ,
                                                    debug_params = {}                    ,
                                                    stats        = {}                    ,
                                                    version      = '1.0.0'               )

        result = self.admin_service.generate_admin_page(request_data, 'cookies')

        assert result['status_code']             == 200
        assert result['headers']['X-Admin-Page'] == 'cookies'
        assert 'Cookie Management'               in result['body']

    def test__generate_admin_page__invalid_endpoint(self):                     # Test admin page with invalid endpoint
        request_data = Schema__Proxy__Request_Data(method       = 'GET'             ,
                                                    host         = 'example.com'     ,
                                                    path         = '/mitm-proxy/invalid',
                                                    headers      = {}                ,
                                                    debug_params = {}                ,
                                                    stats        = {}                ,
                                                    version      = '1.0.0'           )

        result = self.admin_service.generate_admin_page(request_data, 'invalid')

        assert result['status_code']             == 404
        assert result['headers']['X-Admin-Page'] == 'error-404'
        assert '404'                             in result['body']

    def test__format_cookie_list__empty(self):                                 # Test cookie list formatting with no cookies
        html = self.admin_service._format_cookie_list({})

        assert 'No proxy cookies active' in html
        assert type(html)                is str

    def test__format_cookie_list__with_cookies(self):                          # Test cookie list formatting with cookies
        cookies = {
            'mitm-show'  : 'url-to-html-xxx',
            'mitm-debug' : 'true',
            'mitm-rating': '0.5'
        }

        html = self.admin_service._format_cookie_list(cookies)

        assert 'mitm-show'       in html
        assert 'url-to-html-xxx' in html
        assert 'mitm-debug'      in html
        assert 'true'            in html
        assert 'mitm-rating'     in html
        assert '0.5'             in html
        assert '<code>'          in html  # Cookie values should be in code tags

    def test__format_active_cookies_table__empty(self):                        # Test cookies table formatting with no cookies
        html = self.admin_service._format_active_cookies_table({})

        assert 'No proxy cookies are currently active' in html
        assert 'empty-state'                           in html

    def test__format_active_cookies_table__with_cookies(self):                 # Test cookies table formatting with cookies
        cookies = {
            'mitm-show'  : 'url-to-html-xxx',
            'mitm-inject': 'debug-panel'
        }

        html = self.admin_service._format_active_cookies_table(cookies)

        assert '<table'          in html
        assert 'cookie-table'    in html
        assert 'mitm-show'       in html
        assert 'url-to-html-xxx' in html
        assert 'mitm-inject'     in html
        assert 'debug-panel'     in html
        assert '<thead>'         in html
        assert '<tbody>'         in html

    def test__dashboard_navigation_links(self):                                # Test dashboard contains navigation links
        request_data = Schema__Proxy__Request_Data(method       = 'GET'             ,
                                                    host         = 'example.com'     ,
                                                    path         = '/mitm-proxy/'    ,
                                                    headers      = {}                ,
                                                    debug_params = {}                ,
                                                    stats        = {}                ,
                                                    version      = '1.0.0'           )

        html = self.admin_service.generate_dashboard_page(request_data)

        assert '/mitm-proxy/cookies'    in html
        assert 'Cookie Management'      in html
        assert '/mitm-proxy/site-info'  in html
        assert '/mitm-proxy/stats'      in html
        assert '/mitm-proxy/settings'   in html

    def test__cookies_page_back_link(self):                                    # Test cookies page has back link
        request_data = Schema__Proxy__Request_Data(method       = 'GET'                 ,
                                                    host         = 'example.com'         ,
                                                    path         = '/mitm-proxy/cookies' ,
                                                    headers      = {}                    ,
                                                    debug_params = {}                    ,
                                                    stats        = {}                    ,
                                                    version      = '1.0.0'               )

        html = self.admin_service.generate_cookies_page(request_data)

        assert '/mitm-proxy/'            in html
        assert 'Back to Dashboard'       in html
        assert 'back-link'               in html

    def test__html_structure_valid(self):                                      # Test generated HTML has valid structure
        request_data = Schema__Proxy__Request_Data(method       = 'GET'             ,
                                                    host         = 'example.com'     ,
                                                    path         = '/mitm-proxy/'    ,
                                                    headers      = {}                ,
                                                    debug_params = {}                ,
                                                    stats        = {}                ,
                                                    version      = '1.0.0'           )

        html = self.admin_service.generate_dashboard_page(request_data)

        # Check HTML structure
        assert '<!DOCTYPE html>'         in html
        assert '<html'                   in html
        assert '</html>'                 in html
        assert '<head>'                  in html
        assert '</head>'                 in html
        assert '<body>'                  in html
        assert '</body>'                 in html
        assert '<meta charset="UTF-8">'  in html
        assert '<meta name="viewport"'   in html
        assert '<title>'                 in html
        assert '<style>'                 in html
        assert '</style>'                in html

    def test__css_included(self):                                              # Test pages include CSS styling
        request_data = Schema__Proxy__Request_Data(method       = 'GET'             ,
                                                    host         = 'example.com'     ,
                                                    path         = '/mitm-proxy/'    ,
                                                    headers      = {}                ,
                                                    debug_params = {}                ,
                                                    stats        = {}                ,
                                                    version      = '1.0.0'           )

        html = self.admin_service.generate_dashboard_page(request_data)

        # Check for CSS classes
        assert 'container'               in html
        assert 'header'                  in html
        assert 'card'                    in html
        assert 'card-title'              in html
        assert 'gradient'                in html  # Purple gradient background

    def test__javascript_included_in_cookies_page(self):                       # Test cookies page includes JavaScript
        request_data = Schema__Proxy__Request_Data(method       = 'GET'                 ,
                                                    host         = 'example.com'         ,
                                                    path         = '/mitm-proxy/cookies' ,
                                                    headers      = {}                    ,
                                                    debug_params = {}                    ,
                                                    stats        = {}                    ,
                                                    version      = '1.0.0'               )

        html = self.admin_service.generate_cookies_page(request_data)

        assert '<script>'                in html
        assert '</script>'               in html
        assert 'document.cookie'         in html
        assert 'addEventListener'        in html
        assert 'cookieForm'              in html

    def test__multiple_hosts(self):                                            # Test admin pages work for different hosts
        hosts = ['example.com', 'google.com', 'github.com', 'api.service.com']

        for host in hosts:
            request_data = Schema__Proxy__Request_Data(method       = 'GET'             ,
                                                        host         = host              ,
                                                        path         = '/mitm-proxy/'    ,
                                                        headers      = {}                ,
                                                        debug_params = {}                ,
                                                        stats        = {}                ,
                                                        version      = '1.0.0'           )

            html = self.admin_service.generate_dashboard_page(request_data)

            assert host                  in html
            assert 'Dashboard'           in html
            assert len(html)             > 0

    def test__stats_incrementation_not_affected(self):                         # Test stats service still works independently
        initial_requests = self.stats_service.stats.total_requests

        # Generate admin page
        request_data = Schema__Proxy__Request_Data(method       = 'GET'             ,
                                                    host         = 'example.com'     ,
                                                    path         = '/mitm-proxy/'    ,
                                                    headers      = {}                ,
                                                    debug_params = {}                ,
                                                    stats        = {}                ,
                                                    version      = '1.0.0'           )

        self.admin_service.generate_dashboard_page(request_data)

        # Stats should not auto-increment from admin page generation
        assert self.stats_service.stats.total_requests == initial_requests

        # But manual increment should still work
        self.stats_service.increment_request(host='example.com', path='/test')
        assert self.stats_service.stats.total_requests == initial_requests + 1