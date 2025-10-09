from unittest                                                                    import TestCase
from mgraph_ai_service_mitmproxy.service.proxy.Proxy__Request__Service          import Proxy__Request__Service
from mgraph_ai_service_mitmproxy.service.proxy.Proxy__Stats__Service            import Proxy__Stats__Service
from mgraph_ai_service_mitmproxy.service.proxy.Proxy__Content__Service          import Proxy__Content__Service
from mgraph_ai_service_mitmproxy.service.proxy.Proxy__Cookie__Service           import Proxy__Cookie__Service
from mgraph_ai_service_mitmproxy.service.admin.Proxy__Admin__Service            import Proxy__Admin__Service
from mgraph_ai_service_mitmproxy.schemas.proxy.Schema__Proxy__Stats             import Schema__Proxy__Stats
from mgraph_ai_service_mitmproxy.schemas.proxy.Schema__Proxy__Request_Data      import Schema__Proxy__Request_Data
from mgraph_ai_service_mitmproxy.schemas.proxy.Schema__Proxy__Modifications     import Schema__Proxy__Modifications


class Test_Proxy__Request__Service__Admin_Integration(TestCase):

    def setUp(self):                                                            # Setup test fixtures
        self.stats_service   = Proxy__Stats__Service(stats=Schema__Proxy__Stats())
        self.content_service = Proxy__Content__Service()
        self.cookie_service  = Proxy__Cookie__Service()
        self.admin_service   = Proxy__Admin__Service(cookie_service = self.cookie_service,
                                                      stats_service  = self.stats_service )

        self.request_service = Proxy__Request__Service(stats_service   = self.stats_service  ,
                                                        content_service = self.content_service,
                                                        cookie_service  = self.cookie_service ,
                                                        admin_service   = self.admin_service  )

    def test__init__(self):                                                     # Test service initialization
        assert type(self.request_service)                is Proxy__Request__Service
        assert type(self.request_service.stats_service)  is Proxy__Stats__Service
        assert type(self.request_service.admin_service)  is Proxy__Admin__Service

    def test__process_request__regular_path(self):                             # Test regular path processing
        request_data = Schema__Proxy__Request_Data(method       = 'GET'             ,
                                                    host         = 'example.com'     ,
                                                    path         = '/regular/path'   ,
                                                    headers      = {}                ,
                                                    debug_params = {}                ,
                                                    stats        = {}                ,
                                                    version      = '1.0.0'           )

        modifications = self.request_service.process_request(request_data)

        assert type(modifications)                 is Schema__Proxy__Modifications
        assert modifications.cached_response       == {}  # No cached response for regular paths
        assert 'x-mgraph-proxy'                    in modifications.headers_to_add
        assert self.stats_service.stats.total_requests == 1  # Stats incremented

    def test__process_request__admin_path_index(self):                         # Test admin dashboard path
        request_data = Schema__Proxy__Request_Data(method       = 'GET'             ,
                                                    host         = 'example.com'     ,
                                                    path         = '/mitm-proxy/'    ,
                                                    headers      = {}                ,
                                                    debug_params = {}                ,
                                                    stats        = {}                ,
                                                    version      = '1.0.0'           )

        modifications = self.request_service.process_request(request_data)

        assert type(modifications)                     is Schema__Proxy__Modifications
        assert modifications.cached_response           != {}  # Has cached response
        assert modifications.cached_response['status_code'] == 200
        assert 'text/html'                             in modifications.cached_response['headers']['Content-Type']
        assert 'Dashboard'                             in modifications.cached_response['body']
        assert self.stats_service.stats.total_requests == 0  # Stats NOT incremented for admin paths

    def test__process_request__admin_path_cookies(self):                       # Test admin cookies path
        request_data = Schema__Proxy__Request_Data(method       = 'GET'                 ,
                                                    host         = 'example.com'         ,
                                                    path         = '/mitm-proxy/cookies' ,
                                                    headers      = {}                    ,
                                                    debug_params = {}                    ,
                                                    stats        = {}                    ,
                                                    version      = '1.0.0'               )

        modifications = self.request_service.process_request(request_data)

        assert modifications.cached_response           != {}
        assert modifications.cached_response['status_code'] == 200
        assert 'Cookie Management'                     in modifications.cached_response['body']

    def test__process_request__admin_path_invalid(self):                       # Test invalid admin path returns 404
        request_data = Schema__Proxy__Request_Data(method       = 'GET'             ,
                                                    host         = 'example.com'     ,
                                                    path         = '/mitm-proxy/invalid',
                                                    headers      = {}                ,
                                                    debug_params = {}                ,
                                                    stats        = {}                ,
                                                    version      = '1.0.0'           )

        modifications = self.request_service.process_request(request_data)

        assert modifications.cached_response['status_code'] == 404
        assert '404'                                   in modifications.cached_response['body']

    def test__admin_path_early_detection(self):                                # Test admin paths detected before stats
        initial_requests = self.stats_service.stats.total_requests

        # Process admin path
        admin_request = Schema__Proxy__Request_Data(method       = 'GET'             ,
                                                     host         = 'example.com'     ,
                                                     path         = '/mitm-proxy/'    ,
                                                     headers      = {}                ,
                                                     debug_params = {}                ,
                                                     stats        = {}                ,
                                                     version      = '1.0.0'           )

        self.request_service.process_request(admin_request)

        # Stats should NOT increment for admin paths
        assert self.stats_service.stats.total_requests == initial_requests

        # Process regular path
        regular_request = Schema__Proxy__Request_Data(method       = 'GET'             ,
                                                       host         = 'example.com'     ,
                                                       path         = '/regular/path'   ,
                                                       headers      = {}                ,
                                                       debug_params = {}                ,
                                                       stats        = {}                ,
                                                       version      = '1.0.0'           )

        self.request_service.process_request(regular_request)

        # Stats SHOULD increment for regular paths
        assert self.stats_service.stats.total_requests == initial_requests + 1

    def test__admin_path_with_cookies(self):                                   # Test admin path with active cookies
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

        modifications = self.request_service.process_request(request_data)

        body = modifications.cached_response['body']

        assert 'mitm-show'       in body
        assert 'url-to-html-xxx' in body
        assert 'mitm-debug'      in body

    def test__admin_path_shows_current_stats(self):                            # Test admin page shows current statistics
        # Add some stats
        self.stats_service.stats.total_requests       = 100
        self.stats_service.stats.total_responses      = 95
        self.stats_service.stats.total_bytes_processed = 1000000

        request_data = Schema__Proxy__Request_Data(method       = 'GET'             ,
                                                    host         = 'example.com'     ,
                                                    path         = '/mitm-proxy/'    ,
                                                    headers      = {}                ,
                                                    debug_params = {}                ,
                                                    stats        = {}                ,
                                                    version      = '1.0.0'           )

        modifications = self.request_service.process_request(request_data)

        body = modifications.cached_response['body']

        assert '100'       in body  # total_requests
        assert '95'        in body  # total_responses
        assert '1,000,000' in body  # bytes formatted

    def test__admin_path_different_hosts(self):                                # Test admin pages work for multiple hosts
        hosts = ['example.com', 'test.com', 'api.service.io']

        for host in hosts:
            request_data = Schema__Proxy__Request_Data(method       = 'GET'             ,
                                                        host         = host              ,
                                                        path         = '/mitm-proxy/'    ,
                                                        headers      = {}                ,
                                                        debug_params = {}                ,
                                                        stats        = {}                ,
                                                        version      = '1.0.0'           )

            modifications = self.request_service.process_request(request_data)

            body = modifications.cached_response['body']

            assert host        in body
            assert 'Dashboard' in body

    def test__regular_path_with_debug_cookies(self):                           # Test regular path processing with debug cookies
        request_data = Schema__Proxy__Request_Data(
            method       = 'GET'             ,
            host         = 'example.com'     ,
            path         = '/api/data'       ,
            headers      = {
                'Cookie': 'mitm-debug=true'
            },
            debug_params = {}                ,
            stats        = {}                ,
            version      = '1.0.0'           )

        modifications = self.request_service.process_request(request_data)

        # Regular path should NOT return cached response
        assert modifications.cached_response == {}

        # But should process debug cookies
        assert 'x-debug-params' in modifications.headers_to_add

    def test__admin_path_no_upstream_call(self):                               # Test admin paths return immediately
        request_data = Schema__Proxy__Request_Data(method       = 'GET'             ,
                                                    host         = 'example.com'     ,
                                                    path         = '/mitm-proxy/'    ,
                                                    headers      = {}                ,
                                                    debug_params = {}                ,
                                                    stats        = {}                ,
                                                    version      = '1.0.0'           )

        modifications = self.request_service.process_request(request_data)

        # Should have cached_response set (means no upstream call)
        assert modifications.cached_response != {}
        assert modifications.cached_response['status_code'] == 200

        # Should not set other modification flags
        assert modifications.block_request is False

    def test__handle_admin_request__directly(self):                            # Test _handle_admin_request internal method
        request_data = Schema__Proxy__Request_Data(method       = 'GET'             ,
                                                    host         = 'example.com'     ,
                                                    path         = '/mitm-proxy/'    ,
                                                    headers      = {}                ,
                                                    debug_params = {}                ,
                                                    stats        = {}                ,
                                                    version      = '1.0.0'           )

        modifications = self.request_service._handle_admin_request(request_data)

        assert type(modifications)                     is Schema__Proxy__Modifications
        assert modifications.cached_response           != {}
        assert modifications.cached_response['status_code'] == 200

    def test__admin_path_case_variations(self):                                # Test admin path with different cases
        paths = [
            '/mitm-proxy',
            '/mitm-proxy/',
            '/mitm-proxy/cookies',
            '/mitm-proxy/cookies/',
        ]

        for path in paths:
            request_data = Schema__Proxy__Request_Data(method       = 'GET'             ,
                                                        host         = 'example.com'     ,
                                                        path         = path              ,
                                                        headers      = {}                ,
                                                        debug_params = {}                ,
                                                        stats        = {}                ,
                                                        version      = '1.0.0'           )

            modifications = self.request_service.process_request(request_data)

            # All should return cached response (admin page)
            assert modifications.cached_response != {}
            assert modifications.cached_response['status_code'] in [200, 404]

    def test__regular_and_admin_path_isolation(self):                          # Test admin and regular paths don't interfere
        # Process regular path first
        regular_request = Schema__Proxy__Request_Data(method       = 'GET'             ,
                                                       host         = 'example.com'     ,
                                                       path         = '/api/endpoint'   ,
                                                       headers      = {}                ,
                                                       debug_params = {}                ,
                                                       stats        = {}                ,
                                                       version      = '1.0.0'           )

        regular_mods = self.request_service.process_request(regular_request)

        assert regular_mods.cached_response == {}
        assert self.stats_service.stats.total_requests == 1

        # Process admin path
        admin_request = Schema__Proxy__Request_Data(method       = 'GET'             ,
                                                     host         = 'example.com'     ,
                                                     path         = '/mitm-proxy/'    ,
                                                     headers      = {}                ,
                                                     debug_params = {}                ,
                                                     stats        = {}                ,
                                                     version      = '1.0.0'           )

        admin_mods = self.request_service.process_request(admin_request)

        assert admin_mods.cached_response != {}
        assert self.stats_service.stats.total_requests == 1  # Still 1, admin didn't increment

        # Process another regular path
        regular_request2 = Schema__Proxy__Request_Data(method       = 'GET'             ,
                                                        host         = 'example.com'     ,
                                                        path         = '/another/path'   ,
                                                        headers      = {}                ,
                                                        debug_params = {}                ,
                                                        stats        = {}                ,
                                                        version      = '1.0.0'           )

        regular_mods2 = self.request_service.process_request(regular_request2)

        assert regular_mods2.cached_response == {}
        assert self.stats_service.stats.total_requests == 2  # Incremented again

    def test__blocked_path_still_processed(self):                              # Test blocked paths still work normally
        request_data = Schema__Proxy__Request_Data(method       = 'GET'             ,
                                                    host         = 'example.com'     ,
                                                    path         = '/blocked/path'   ,
                                                    headers      = {}                ,
                                                    debug_params = {}                ,
                                                    stats        = {}                ,
                                                    version      = '1.0.0'           )

        modifications = self.request_service.process_request(request_data)

        # Blocked path should be blocked
        assert modifications.block_request   is True
        assert 'blocked by policy'           in modifications.block_message

        # Admin paths should NOT be blocked
        admin_request = Schema__Proxy__Request_Data(method       = 'GET'             ,
                                                     host         = 'example.com'     ,
                                                     path         = '/mitm-proxy/'    ,
                                                     headers      = {}                ,
                                                     debug_params = {}                ,
                                                     stats        = {}                ,
                                                     version      = '1.0.0'           )

        admin_mods = self.request_service.process_request(admin_request)

        assert admin_mods.block_request is False
        assert admin_mods.cached_response != {}

    def test__admin_headers_present(self):                                     # Test admin pages include proper headers
        request_data = Schema__Proxy__Request_Data(method       = 'GET'             ,
                                                    host         = 'example.com'     ,
                                                    path         = '/mitm-proxy/'    ,
                                                    headers      = {}                ,
                                                    debug_params = {}                ,
                                                    stats        = {}                ,
                                                    version      = '1.0.0'           )

        modifications = self.request_service.process_request(request_data)

        headers = modifications.cached_response['headers']

        assert 'Content-Type'    in headers
        assert 'X-Admin-Page'    in headers
        assert 'X-Generated-At'  in headers
        assert headers['X-Admin-Page'] == 'index'

    def test__cookie_management_page_headers(self):                            # Test cookie page has correct headers
        request_data = Schema__Proxy__Request_Data(method       = 'GET'                 ,
                                                    host         = 'example.com'         ,
                                                    path         = '/mitm-proxy/cookies' ,
                                                    headers      = {}                    ,
                                                    debug_params = {}                    ,
                                                    stats        = {}                    ,
                                                    version      = '1.0.0'               )

        modifications = self.request_service.process_request(request_data)

        headers = modifications.cached_response['headers']

        assert headers['X-Admin-Page'] == 'cookies'
        assert 'text/html'             in headers['Content-Type']