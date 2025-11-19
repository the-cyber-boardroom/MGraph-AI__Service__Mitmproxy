from unittest                                                                      import TestCase
from osbot_utils.testing.__                                                        import __, __SKIP__
from osbot_utils.testing.Temp_Env_Vars                                             import Temp_Env_Vars
from osbot_utils.type_safe.Type_Safe                                               import Type_Safe
from osbot_utils.utils.Objects                                                     import base_classes
from osbot_utils.type_safe.primitives.core.Safe_Float                              import Safe_Float
from mgraph_ai_service_mitmproxy.service.html.HTML__Service__Client                import HTML__Service__Client
from mgraph_ai_service_mitmproxy.schemas.html.Schema__HTML__Service__Request       import Schema__HTML__Service__Request
from mgraph_ai_service_mitmproxy.schemas.html.Enum__HTML__Transformation_Mode      import Enum__HTML__Transformation_Mode
from mgraph_ai_service_mitmproxy.service.consts.consts__html_service               import (DEFAULT__HTML_SERVICE__BASE_URL,
                                                                                           DEFAULT__HTML_SERVICE__TIMEOUT)
from tests.unit.Mitmproxy_Service__Fast_API__Test_Objs                             import get__html_service__fast_api_server


class test_HTML__Service__Client(TestCase):

    @classmethod
    def setUpClass(cls):                                                             # ONE-TIME setup: start local HTML service and create stateless client
        with get__html_service__fast_api_server() as _:
            cls.fast_api_server = _.fast_api_server
            cls.base_url        = _.server_url
            cls.client          = HTML__Service__Client(base_url=_.server_url)                   # Configure to use local server

        cls.fast_api_server.start()                                                 # Start server

    @classmethod
    def tearDownClass(cls):                                                         # Stop server
        cls.fast_api_server.stop()

    def test__init__(self):                                                         # Test auto-initialization
        with HTML__Service__Client() as _:
            assert type(_)         is HTML__Service__Client
            assert base_classes(_) == [Type_Safe, object]
            assert _.base_url      == DEFAULT__HTML_SERVICE__BASE_URL
            assert type(_.timeout) is Safe_Float
            assert _.timeout       == DEFAULT__HTML_SERVICE__TIMEOUT

    def test_setup__with_env_var(self):                                             # Test setup with environment variable
        env_vars = {'AUTH__TARGET_SERVER__HTML_SERVICE__BASE_URL': 'https://custom.html.service'}
        with Temp_Env_Vars(env_vars=env_vars):
            with HTML__Service__Client() as _:
                _.setup()
                assert _.base_url == 'https://custom.html.service'

    def test_setup__without_env_var(self):                                          # Test setup without environment variable
        with HTML__Service__Client() as _:
            _.setup()
            assert _.base_url == DEFAULT__HTML_SERVICE__BASE_URL                    # Falls back to default

    def test_get_auth_headers__with_credentials(self):                              # Test auth headers with credentials
        env_vars = {'AUTH__TARGET_SERVER__HTML_SERVICE__KEY_NAME' : 'X-API-Key'    ,
                    'AUTH__TARGET_SERVER__HTML_SERVICE__KEY_VALUE': 'test-key-123' }
        with Temp_Env_Vars(env_vars=env_vars):
            with HTML__Service__Client() as _:
                headers = _.get_auth_headers()

                assert type(headers)           is dict
                assert headers['Content-Type'] == 'application/json'
                assert headers['X-API-Key']    == 'test-key-123'

    def test_get_auth_headers__without_credentials(self):                           # Test auth headers without credentials
        with HTML__Service__Client() as _:
            headers = _.get_auth_headers()

            assert type(headers)           is dict
            assert headers['Content-Type'] == 'application/json'
            assert 'X-API-Key' not in headers                                       # No auth key if not configured

    def test_transform_html__roundtrip(self):                                       # Test HTML roundtrip transformation
        original_html = "<html><head><title>Test</title></head><body><p>Content</p></body></html>"

        request  = Schema__HTML__Service__Request(html                = original_html                                    ,
                                                  transformation_mode = Enum__HTML__Transformation_Mode.ROUNDTRIP)
        response = self.client.transform_html(request)

        assert response.status_code == 200
        assert response.success     is True
        assert response.obj()       == __( error_message       = None                                                 ,
                                           status_code         = 200                                                  ,
                                           content_type        = 'text/html; charset=utf-8'                           ,
                                           body                = ('<!DOCTYPE html>\n'
                                                                  '<html>\n'
                                                                  '    <head>\n'
                                                                  '        <title>Test</title>\n'
                                                                  '    </head>\n'
                                                                  '    <body>\n'
                                                                  '        <p>Content</p>\n'
                                                                  '    </body>\n'
                                                                  '</html>'                                        ),
                                           headers             = __( date                = __SKIP__                   ,
                                                                     server              = 'uvicorn'                  ,
                                                                     content_length      = '128'                      ,
                                                                     content_type        = 'text/html; charset=utf-8' ,
                                                                     fast_api_request_id = __SKIP__                   ),
                                           success             = True                                                 )


    def test__bug__transform_html__dict_mode(self):                                       # Test dict transformation (returns JSON)
        request = Schema__HTML__Service__Request(html                = "<html><body>test</body></html>"         ,
                                                 transformation_mode = Enum__HTML__Transformation_Mode.DICT)

        response = self.client.transform_html(request)

        assert response.status_code == 200
        assert response.success     is True

        assert response.obj() == __( error_message       = None                                                  ,
                                     status_code         = 200                                                   ,
                                     content_type        = 'text/plain; charset=utf-8'                           ,
                                     body                = 'html\n    └── body\n        └── TEXT: test'          ,          # todo: BUG this is the tree_view output , not the dict
                                     headers             = __( date                = __SKIP__                   ,
                                                               server              = 'uvicorn'                  ,
                                                               content_length      = '52'                       ,
                                                               content_type        = 'text/plain; charset=utf-8',
                                                               fast_api_request_id = __SKIP__                   ),
                                     success             = True                                                  )


    def test_transform_html__xxx_mode(self):                                        # Test XXX privacy mask transformation
        request = Schema__HTML__Service__Request(html                = "<html><body>secret text</body></html>" ,
                                                 transformation_mode = Enum__HTML__Transformation_Mode.XXX)

        response = self.client.transform_html(request)

        assert response.status_code == 200
        assert response.success     is True

        assert response.obj() == __( error_message       = None                                                  ,
                                     status_code         = 200                                                   ,
                                     content_type        = 'text/html; charset=utf-8'                            ,
                                     body                = ('<!DOCTYPE html>\n'
                                                            '<html>\n'
                                                            '    <body>xxxxxx xxxx</body>\n'
                                                            '</html>')                                         ,
                                     headers             = __( date                = __SKIP__                   ,
                                                               server              = 'uvicorn'                  ,
                                                               content_length      = '60'                       ,
                                                               content_type        = 'text/html; charset=utf-8' ,
                                                               fast_api_request_id = __SKIP__                   ),
                                     success             = True                                                  )


    def test_transform_html__invalid_mode(self):                                    # Test transformation with invalid mode
        request = Schema__HTML__Service__Request(html                = "<html>test</html>"                ,
                                                 transformation_mode = Enum__HTML__Transformation_Mode.OFF)
        response = self.client.transform_html(request)

        assert response.status_code          == 400
        assert response.success              is False
        assert "invalid transformation mode" in response.error_message.lower()
        assert response.obj()                == __(error_message = 'Invalid transformation mode: '
                                                                   'Enum__HTML__Transformation_Mode.OFF' ,
                                                   status_code   = 400                                    ,
                                                   content_type  = 'text/plain'                           ,
                                                   body          = ''                                     ,
                                                   headers       = __()                                   ,
                                                   success       = False                                  )

    def test_transform_html__complex_html(self):                                    # Test with complex HTML structure
        complex_html = """
        <html>
            <head>
                <title>Complex Test</title>
                <style>body { color: red; }</style>
            </head>
            <body>
                <div class="container">
                    <h1>Title</h1>
                    <p>Paragraph with <strong>bold</strong> text</p>
                    <ul>
                        <li>Item 1</li>
                        <li>Item 2</li>
                    </ul>
                </div>
            </body>
        </html>"""

        request = Schema__HTML__Service__Request(html                = complex_html                                     ,
                                                 transformation_mode = Enum__HTML__Transformation_Mode.HASHES)

        response = self.client.transform_html(request)

        assert response.status_code == 200
        assert response.success     is True
        assert '<html>' in response.body
        assert 'text/html' in response.content_type

        assert response.obj() == __( error_message       = None                                                  ,
                                     status_code         = 200                                                   ,
                                     content_type        = 'text/html; charset=utf-8'                            ,
                                     body                = ('<!DOCTYPE html>\n'
                                                            '<html>\n'
                                                            '    <head>\n'
                                                            '        <title>10ae08b150</title>\n'
                                                            '        <style>body { color: red; }</style>\n'
                                                            '    </head>\n'
                                                            '    <body>\n'
                                                            '        <div class="container">\n'
                                                            '            <h1>b78a322350</h1>\n'
                                                            '            <p>47b74c884c<strong>69dcab4a73</strong>ea1f576750</p>\n'
                                                            '            <ul>\n'
                                                            '                <li>f59e6f3afd</li>\n'
                                                            '                <li>9eda28f018</li>\n'
                                                            '            </ul>\n'
                                                            '        </div>\n'
                                                            '    </body>\n'
                                                            '</html>')                                         ,
                                     headers             = __( date                = __SKIP__                   ,
                                                               server              = 'uvicorn'                  ,
                                                               content_length      = '408'                      ,
                                                               content_type        = 'text/html; charset=utf-8' ,
                                                               fast_api_request_id = __SKIP__                   ),
                                     success             = True                                                  )


    def test_transform_html__empty_html(self):                                      # Test with empty HTML
        request = Schema__HTML__Service__Request(html                = ""                                               ,
                                                 transformation_mode = Enum__HTML__Transformation_Mode.HASHES)

        response = self.client.transform_html(request)

        assert response.status_code == 400                                          # Service should handle gracefully
        assert response.success     is False

        assert response.obj() == __( error_message       = None                                                  ,
                                     status_code         = 400                                                   ,
                                     content_type        = 'application/json'                                    ,
                                     body                = ('{\n'
                                                            '  "detail": "ValueError: Parameter \'html_dict\' is not optional but got None"\n'
                                                            '}')                                                 ,
                                     headers             = __( date                = __SKIP__                   ,
                                                               server              = 'uvicorn'                  ,
                                                               content_length      = '75'                       ,
                                                               content_type        = 'application/json'         ,
                                                               fast_api_request_id = __SKIP__                   ),
                                     success             = False                                                 )



    def test_transform_html__malformed_html(self):                                  # Test with malformed HTML
        request = Schema__HTML__Service__Request(html                = "<html><body><p>Unclosed paragraph</body></html>" ,
                                                 transformation_mode = Enum__HTML__Transformation_Mode.HASHES)

        response = self.client.transform_html(request)

        assert response.status_code == 200                                          # Parser should handle gracefully
        assert response.success     is True

        assert response.obj() == __( error_message       = None                                                  ,
                                     status_code         = 200                                                   ,
                                     content_type        = 'text/html; charset=utf-8'                            ,
                                     body                = ('<!DOCTYPE html>\n'
                                                            '<html>\n'
                                                            '    <body>\n'
                                                            '        <p>3bc7818faf</p>\n'               # fixed the malformed paragraph
                                                            '    </body>\n'
                                                            '</html>')                                         ,
                                     headers             = __( date                = __SKIP__                   ,
                                                               server              = 'uvicorn'                  ,
                                                               content_length      = '80'                       ,
                                                               content_type        = 'text/html; charset=utf-8' ,
                                                               fast_api_request_id = __SKIP__                   ),
                                     success             = True                                                  )


    def test_transform_html__base_url_configuration(self):                          # Test that client uses configured base_url
        assert self.client.base_url == self.base_url                                # Should point to local server
        assert self.base_url.startswith('http://')                                  # Local server uses HTTP

    def test_transform_html__timeout_configuration(self):                           # Test timeout is properly set
        assert type(self.client.timeout) is Safe_Float
        assert float(self.client.timeout) > 0                                       # Has valid timeout

    def test_client_with_different_modes(self):                                     # Test client works with multiple transformation modes
        html = "<html><body><p>Test paragraph</p></body></html>"

        modes_to_test = [Enum__HTML__Transformation_Mode.HASHES    ,
                         Enum__HTML__Transformation_Mode.XXX       ,
                         Enum__HTML__Transformation_Mode.ROUNDTRIP ,
                         Enum__HTML__Transformation_Mode.DICT      ]

        for mode in modes_to_test:
            request = Schema__HTML__Service__Request(html                = html,
                                                     transformation_mode = mode)

            response = self.client.transform_html(request)

            assert response.status_code == 200                                      # All valid modes should succeed
            assert response.success     is True
            assert response.body != ""                                              # Should return content

    def test__bug__server_health_check(self):                                             # Verify local server is running and accessible
        import requests
        health_url = f"{self.base_url}/info/health"

        response   = requests.get(health_url)
        assert response.status_code == 200
        assert response.json() == {'status': 'ok'}                                  # Standard health check response