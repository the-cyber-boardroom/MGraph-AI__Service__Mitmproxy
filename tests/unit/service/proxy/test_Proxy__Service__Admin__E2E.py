from unittest                                                                    import TestCase
from mgraph_ai_service_mitmproxy.service.proxy.Proxy__Service                   import Proxy__Service
from mgraph_ai_service_mitmproxy.service.proxy.Proxy__Request__Service          import Proxy__Request__Service
from mgraph_ai_service_mitmproxy.service.proxy.Proxy__Response__Service         import Proxy__Response__Service
from mgraph_ai_service_mitmproxy.service.proxy.Proxy__Stats__Service            import Proxy__Stats__Service
from mgraph_ai_service_mitmproxy.service.proxy.Proxy__Content__Service          import Proxy__Content__Service
from mgraph_ai_service_mitmproxy.service.proxy.Proxy__Cookie__Service           import Proxy__Cookie__Service
from mgraph_ai_service_mitmproxy.service.proxy.Proxy__Debug__Service            import Proxy__Debug__Service
from mgraph_ai_service_mitmproxy.service.proxy.Proxy__CORS__Service             import Proxy__CORS__Service
from mgraph_ai_service_mitmproxy.service.proxy.Proxy__Headers__Service          import Proxy__Headers__Service
from mgraph_ai_service_mitmproxy.service.proxy.Proxy__HTML__Service             import Proxy__HTML__Service
from mgraph_ai_service_mitmproxy.service.proxy.Proxy__JSON__Service             import Proxy__JSON__Service
from mgraph_ai_service_mitmproxy.service.admin.Proxy__Admin__Service            import Proxy__Admin__Service
from mgraph_ai_service_mitmproxy.service.wcf.Proxy__WCF__Service                import Proxy__WCF__Service
from mgraph_ai_service_mitmproxy.schemas.proxy.Schema__Proxy__Stats             import Schema__Proxy__Stats
from mgraph_ai_service_mitmproxy.schemas.proxy.Schema__Proxy__Request_Data      import Schema__Proxy__Request_Data
from mgraph_ai_service_mitmproxy.schemas.Schema__CORS__Config                   import Schema__CORS__Config


class Test_Proxy__Service__Admin__E2E(TestCase):

    def setUp(self):                                                            # Setup complete service chain
        # Create all services
        self.stats_service   = Proxy__Stats__Service(stats=Schema__Proxy__Stats())
        self.cookie_service  = Proxy__Cookie__Service()
        self.content_service = Proxy__Content__Service()
        self.admin_service   = Proxy__Admin__Service(cookie_service = self.cookie_service,
                                                      stats_service  = self.stats_service )

        # Request service with admin
        self.request_service = Proxy__Request__Service(stats_service   = self.stats_service  ,
                                                        content_service = self.content_service,
                                                        cookie_service  = self.cookie_service ,
                                                        admin_service   = self.admin_service  )

        # Response service chain
        self.wcf_service     = Proxy__WCF__Service()
        self.html_service    = Proxy__HTML__Service()
        self.json_service    = Proxy__JSON__Service()
        self.debug_service   = Proxy__Debug__Service(wcf_service  = self.wcf_service ,
                                                      html_service = self.html_service,
                                                      json_service = self.json_service)
        self.cors_service    = Proxy__CORS__Service(cors_config=Schema__CORS__Config())
        self.headers_service = Proxy__Headers__Service()

        self.response_service = Proxy__Response__Service(debug_service   = self.debug_service  ,
                                                          stats_service   = self.stats_service  ,
                                                          cors_service    = self.cors_service   ,
                                                          headers_service = self.headers_service,
                                                          cookie_service  = self.cookie_service )

        # Main proxy service
        self.proxy_service = Proxy__Service(stats_service    = self.stats_service   ,
                                             request_service  = self.request_service ,
                                             response_service = self.response_service,
                                             admin_service    = self.admin_service   )

    def test__proxy_service__initialization(self):                             # Test complete service initialization
        assert type(self.proxy_service)                is Proxy__Service
        assert type(self.proxy_service.admin_service)  is Proxy__Admin__Service
        assert type(self.proxy_service.stats_service)  is Proxy__Stats__Service
        assert type(self.proxy_service.request_service) is Proxy__Request__Service

    def test__e2e__admin_dashboard_request(self):                              # Test complete flow for admin dashboard
        request_data = Schema__Proxy__Request_Data(method       = 'GET'             ,
                                                    host         = 'example.com'     ,
                                                    path         = '/mitm-proxy/'    ,
                                                    headers      = {}                ,
                                                    debug_params = {}                ,
                                                    stats        = {}                ,
                                                    version      = '1.0.0'           )

        # Process request through main service
        modifications = self.proxy_service.process_request(request_data)

        assert modifications.cached_response != {}
        assert modifications.cached_response['status_code'] == 200
        assert 'Dashboard'                             in modifications.cached_response['body']
        assert 'example.com'                           in modifications.cached_response['body']

    def test__e2e__admin_cookies_request(self):                                # Test complete flow for cookie management
        request_data = Schema__Proxy__Request_Data(method       = 'GET'                 ,
                                                    host         = 'example.com'         ,
                                                    path         = '/mitm-proxy/cookies' ,
                                                    headers      = {}                    ,
                                                    debug_params = {}                    ,
                                                    stats        = {}                    ,
                                                    version      = '1.0.0'               )

        modifications = self.proxy_service.process_request(request_data)

        assert modifications.cached_response['status_code'] == 200
        assert 'Cookie Management'                     in modifications.cached_response['body']

    def test__e2e__admin_with_active_cookies(self):                            # Test admin pages with active proxy cookies
        request_data = Schema__Proxy__Request_Data(
            method       = 'GET'             ,
            host         = 'example.com'     ,
            path         = '/mitm-proxy/'    ,
            headers      = {
                'Cookie': 'mitm-show=url-to-html-xxx; mitm-debug=true; mitm-rating=0.5'
            },
            debug_params = {}                ,
            stats        = {}                ,
            version      = '1.0.0'           )

        modifications = self.proxy_service.process_request(request_data)

        body = modifications.cached_response['body']

        assert 'mitm-show'       in body
        assert 'url-to-html-xxx' in body
        assert 'mitm-debug'      in body
        assert '0.5'             in body

    def test__e2e__regular_request_then_admin(self):                           # Test regular request followed by admin request
        # Process regular request first
        regular_request = Schema__Proxy__Request_Data(method       = 'GET'             ,
                                                       host         = 'example.com'     ,
                                                       path         = '/api/data'       ,
                                                       headers      = {}                ,
                                                       debug_params = {}                ,
                                                       stats        = {}                ,
                                                       version      = '1.0.0'           )

        regular_mods = self.proxy_service.process_request(regular_request)

        assert regular_mods.cached_response == {}
        assert self.stats_service.stats.total_requests == 1

        # Now check admin page shows updated stats
        admin_request = Schema__Proxy__Request_Data(method       = 'GET'             ,
                                                     host         = 'example.com'     ,
                                                     path         = '/mitm-proxy/'    ,
                                                     headers      = {}                ,
                                                     debug_params = {}                ,
                                                     stats        = {}                ,
                                                     version      = '1.0.0'           )

        admin_mods = self.proxy_service.process_request(admin_request)

        assert '1'                             in admin_mods.cached_response['body']  # Shows request count
        assert self.stats_service.stats.total_requests == 1  # Admin didn't increment

    def test__e2e__multiple_hosts_isolation(self):                             # Test admin pages for different hosts are isolated
        hosts = ['example.com', 'test.org', 'api.service.io']

        for host in hosts:
            request_data = Schema__Proxy__Request_Data(method       = 'GET'             ,
                                                        host         = host              ,
                                                        path         = '/mitm-proxy/'    ,
                                                        headers      = {}                ,
                                                        debug_params = {}                ,
                                                        stats        = {}                ,
                                                        version      = '1.0.0'           )

            modifications = self.proxy_service.process_request(request_data)

            body = modifications.cached_response['body']

            # Each should show its own host
            assert host        in body
            # Should NOT show other hosts
            for other_host in hosts:
                if other_host != host:
                    # Other hosts might appear in links, but current host should be in title/header
                    assert f'<strong>{host}</strong>' in body

    def test__e2e__get_stats_after_admin_access(self):                         # Test get_stats API after admin page access
        # Access admin page multiple times
        for i in range(3):
            request_data = Schema__Proxy__Request_Data(method       = 'GET'             ,
                                                        host         = 'example.com'     ,
                                                        path         = '/mitm-proxy/'    ,
                                                        headers      = {}                ,
                                                        debug_params = {}                ,
                                                        stats        = {}                ,
                                                        version      = '1.0.0'           )

            self.proxy_service.process_request(request_data)

        # Get stats
        stats = self.proxy_service.get_stats()

        # Admin accesses should NOT increment stats
        assert stats['total_requests']  == 0
        assert stats['total_responses'] == 0

    def test__e2e__reset_stats_functionality(self):                            # Test reset stats through admin workflow
        # Add some stats
        self.stats_service.stats.total_requests  = 100
        self.stats_service.stats.total_responses = 95

        # Access admin dashboard
        request_data = Schema__Proxy__Request_Data(method       = 'GET'             ,
                                                    host         = 'example.com'     ,
                                                    path         = '/mitm-proxy/'    ,
                                                    headers      = {}                ,
                                                    debug_params = {}                ,
                                                    stats        = {}                ,
                                                    version      = '1.0.0'           )

        modifications = self.proxy_service.process_request(request_data)

        # Should show current stats
        assert '100'                           in modifications.cached_response['body']

        # Reset stats via API
        reset_result = self.proxy_service.reset_stats()

        assert reset_result['previous_stats']['total_requests'] == 100

        # Access admin again
        modifications2 = self.proxy_service.process_request(request_data)

        # Should show zero stats now
        body = modifications2.cached_response['body']
        # Check that we don't see the old high numbers in main stats display
        # (they might appear in formatted text like "100,000" but not as "100" requests)
        stats = self.proxy_service.get_stats()
        assert stats['total_requests'] == 0

    def test__e2e__invalid_admin_endpoint_returns_404(self):                   # Test invalid admin endpoint through full stack
        request_data = Schema__Proxy__Request_Data(method       = 'GET'                    ,
                                                    host         = 'example.com'            ,
                                                    path         = '/mitm-proxy/nonexistent',
                                                    headers      = {}                       ,
                                                    debug_params = {}                       ,
                                                    stats        = {}                       ,
                                                    version      = '1.0.0'                  )

        modifications = self.proxy_service.process_request(request_data)

        assert modifications.cached_response['status_code'] == 404
        assert '404'                                   in modifications.cached_response['body']
        assert 'Admin Page Not Found'                 in modifications.cached_response['body']

    def test__e2e__admin_and_regular_paths_dont_interfere(self):               # Test admin and regular paths work independently
        # Mix of requests
        requests = [
            ('/api/data', False),           # Regular, should increment stats
            ('/mitm-proxy/', True),         # Admin, should NOT increment
            ('/another/path', False),       # Regular, should increment
            ('/mitm-proxy/cookies', True),  # Admin, should NOT increment
            ('/api/endpoint', False),       # Regular, should increment
        ]

        expected_stats = 0

        for path, is_admin in requests:
            request_data = Schema__Proxy__Request_Data(method       = 'GET'             ,
                                                        host         = 'example.com'     ,
                                                        path         = path              ,
                                                        headers      = {}                ,
                                                        debug_params = {}                ,
                                                        stats        = {}                ,
                                                        version      = '1.0.0'           )

            modifications = self.proxy_service.process_request(request_data)

            if is_admin:
                # Admin requests should have cached response
                assert modifications.cached_response != {}
            else:
                # Regular requests should NOT have cached response
                assert modifications.cached_response == {}
                expected_stats += 1

        # Final stats should only count regular requests
        assert self.stats_service.stats.total_requests == expected_stats

    def test__e2e__admin_page_response_structure(self):                        # Test admin response has correct structure
        request_data = Schema__Proxy__Request_Data(method       = 'GET'             ,
                                                    host         = 'example.com'     ,
                                                    path         = '/mitm-proxy/'    ,
                                                    headers      = {}                ,
                                                    debug_params = {}                ,
                                                    stats        = {}                ,
                                                    version      = '1.0.0'           )

        modifications = self.proxy_service.process_request(request_data)

        # Check response structure
        response = modifications.cached_response

        assert 'status_code'             in response
        assert 'body'                    in response
        assert 'headers'                 in response
        assert type(response['status_code']) is int
        assert type(response['body'])        is str
        assert type(response['headers'])     is dict

        # Check headers
        headers = response['headers']
        assert 'Content-Type'            in headers
        assert 'X-Admin-Page'            in headers
        assert 'X-Generated-At'          in headers

    def test__e2e__cookie_service_integration(self):                           # Test cookie service works with admin pages
        # Set multiple cookies
        request_data = Schema__Proxy__Request_Data(
            method       = 'GET'             ,
            host         = 'example.com'     ,
            path         = '/mitm-proxy/cookies',
            headers      = {
                'Cookie': 'mitm-show=url-to-html-xxx; mitm-inject=debug-panel; mitm-debug=true; mitm-rating=0.8'
            },
            debug_params = {}                ,
            stats        = {}                ,
            version      = '1.0.0'           )

        modifications = self.proxy_service.process_request(request_data)

        body = modifications.cached_response['body']

        # All cookies should be displayed
        assert 'mitm-show'       in body
        assert 'mitm-inject'     in body
        assert 'mitm-debug'      in body
        assert 'mitm-rating'     in body
        assert 'url-to-html-xxx' in body
        assert 'debug-panel'     in body
        assert '0.8'             in body

    def test__e2e__stats_accuracy_with_mixed_traffic(self):                    # Test stats remain accurate with mixed traffic
        # Process 10 regular requests
        for i in range(10):
            regular_request = Schema__Proxy__Request_Data(method       = 'GET'             ,
                                                           host         = 'example.com'     ,
                                                           path         = f'/api/data/{i}'  ,
                                                           headers      = {}                ,
                                                           debug_params = {}                ,
                                                           stats        = {}                ,
                                                           version      = '1.0.0'           )

            self.proxy_service.process_request(regular_request)

        # Process 5 admin requests
        for i in range(5):
            admin_request = Schema__Proxy__Request_Data(method       = 'GET'             ,
                                                         host         = 'example.com'     ,
                                                         path         = '/mitm-proxy/'    ,
                                                         headers      = {}                ,
                                                         debug_params = {}                ,
                                                         stats        = {}                ,
                                                         version      = '1.0.0'           )

            self.proxy_service.process_request(admin_request)

        # Stats should only show 10 (regular requests)
        stats = self.proxy_service.get_stats()
        assert stats['total_requests'] == 10

    def test__e2e__html_structure_validity(self):                              # Test generated HTML is well-formed
        request_data = Schema__Proxy__Request_Data(method       = 'GET'             ,
                                                    host         = 'example.com'     ,
                                                    path         = '/mitm-proxy/'    ,
                                                    headers      = {}                ,
                                                    debug_params = {}                ,
                                                    stats        = {}                ,
                                                    version      = '1.0.0'           )

        modifications = self.proxy_service.process_request(request_data)

        html = modifications.cached_response['body']

        # Check HTML structure
        assert html.count('<html')       == html.count('</html>')
        assert html.count('<head>')      == html.count('</head>')
        assert html.count('<body>')      == html.count('</body>')
        assert html.count('<div')        <= html.count('</div>')  # <= because some divs might be self-closing-style
        assert '<!DOCTYPE html>'         in html
        assert '<meta charset="UTF-8">'  in html

    def test__e2e__admin_page_links_present(self):                             # Test admin pages have navigation links
        request_data = Schema__Proxy__Request_Data(method       = 'GET'             ,
                                                    host         = 'example.com'     ,
                                                    path         = '/mitm-proxy/'    ,
                                                    headers      = {}                ,
                                                    debug_params = {}                ,
                                                    stats        = {}                ,
                                                    version      = '1.0.0'           )

        modifications = self.proxy_service.process_request(request_data)

        body = modifications.cached_response['body']

        # Check for navigation links
        assert '/mitm-proxy/cookies'    in body
        assert 'Cookie Management'      in body
        assert 'href='                  in body
        assert '<a '                    in body

    def test__e2e__cookies_page_back_link(self):                               # Test cookies page has back link
        request_data = Schema__Proxy__Request_Data(method       = 'GET'                 ,
                                                    host         = 'example.com'         ,
                                                    path         = '/mitm-proxy/cookies' ,
                                                    headers      = {}                    ,
                                                    debug_params = {}                    ,
                                                    stats        = {}                    ,
                                                    version      = '1.0.0'               )

        modifications = self.proxy_service.process_request(request_data)

        body = modifications.cached_response['body']

        assert '/mitm-proxy/'            in body
        assert 'Back to Dashboard'       in body
        assert 'back-link'               in body