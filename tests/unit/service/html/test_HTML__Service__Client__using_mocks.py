from unittest                                                                      import TestCase
from unittest.mock                                                                 import patch, Mock
from osbot_utils.testing.__                                                        import __
from osbot_utils.type_safe.Type_Safe import Type_Safe
from osbot_utils.utils.Objects                                                     import base_classes
from osbot_utils.type_safe.primitives.core.Safe_Float                              import Safe_Float
from mgraph_ai_service_mitmproxy.service.html.HTML__Service__Client                import HTML__Service__Client
from mgraph_ai_service_mitmproxy.schemas.html.Schema__HTML__Service__Request       import Schema__HTML__Service__Request
from mgraph_ai_service_mitmproxy.schemas.html.Schema__HTML__Service__Response      import Schema__HTML__Service__Response
from mgraph_ai_service_mitmproxy.schemas.html.Enum__HTML__Transformation_Mode      import Enum__HTML__Transformation_Mode
from mgraph_ai_service_mitmproxy.service.consts.consts__html_service               import (DEFAULT__HTML_SERVICE__BASE_URL,
                                                                                           DEFAULT__HTML_SERVICE__TIMEOUT)

class test_HTML__Service__Client__using_mocks(TestCase):

    def test__init__(self):                                                         # Test auto-initialization
        with HTML__Service__Client() as _:
            assert type(_)         is HTML__Service__Client
            assert base_classes(_) == [Type_Safe, object]
            assert _.base_url      == DEFAULT__HTML_SERVICE__BASE_URL
            assert type(_.timeout) is Safe_Float
            assert _.timeout       == DEFAULT__HTML_SERVICE__TIMEOUT

    @patch.dict('os.environ', {'AUTH__TARGET_SERVER__HTML_SERVICE__BASE_URL': 'https://custom.html.service'})
    def test_setup__with_env_var(self):                                             # Test setup with environment variable
        with HTML__Service__Client() as _:
            _.setup()
            assert _.base_url == 'https://custom.html.service'

    def test_setup__without_env_var(self):                                          # Test setup without environment variable
        with HTML__Service__Client() as _:
            _.setup()
            assert _.base_url == DEFAULT__HTML_SERVICE__BASE_URL                    # Falls back to default

    @patch.dict('os.environ', { 'AUTH__TARGET_SERVER__HTML_SERVICE__KEY_NAME': 'X-API-Key'      ,
                                'AUTH__TARGET_SERVER__HTML_SERVICE__KEY_VALUE': 'test-key-123'} )
    def test_get_auth_headers__with_credentials(self):                              # Test auth headers with credentials
        with HTML__Service__Client() as _:
            headers = _.get_auth_headers()

            assert type(headers)       is dict
            assert headers['Content-Type'] == 'application/json'
            assert headers['X-API-Key']    == 'test-key-123'

    def test_get_auth_headers__without_credentials(self):                           # Test auth headers without credentials
        with HTML__Service__Client() as _:
            headers = _.get_auth_headers()

            assert type(headers)           is dict
            assert headers['Content-Type'] == 'application/json'
            assert 'X-API-Key' not in headers                                       # No auth key if not configured

    @patch('mgraph_ai_service_mitmproxy.service.html.HTML__Service__Client.requests.post')
    def test_transform_html__success(self, mock_post):                              # Test successful transformation
        mock_response           = Mock()
        mock_response.status_code = 200
        mock_response.headers   = {'content-type': 'text/html'}
        mock_response.content   = b'<html>transformed</html>'
        mock_post.return_value  = mock_response

        with HTML__Service__Client() as _:
            request = Schema__HTML__Service__Request(
                html                = "<html>original</html>"                     ,
                transformation_mode = Enum__HTML__Transformation_Mode.HASHES
            )

            response = _.transform_html(request)

            assert type(response)     is Schema__HTML__Service__Response
            assert response.status_code == 200
            assert response.body        == '<html>transformed</html>'
            assert response.success     is True
            assert response.error_message is None
            assert request .obj() == __(html                = '<html>original</html>'        ,
                                        transformation_mode = 'hashes'                       )
            assert response.obj() == __(error_message       = None                           ,
                                        status_code         = 200                            ,
                                        content_type        = 'text/html'                    ,
                                        body                = '<html>transformed</html>'     ,
                                        headers             = __(content_type = 'text/html') ,
                                        success             = True                           )


    @patch('mgraph_ai_service_mitmproxy.service.html.HTML__Service__Client.requests.post')
    def test_transform_html__json_response(self, mock_post):                        # Test transformation with JSON response
        mock_response             = Mock()
        mock_response.status_code = 200
        mock_response.headers     = {'content-type': 'application/json'}
        mock_response.json        = Mock(return_value={"key": "value"})
        mock_post.return_value    = mock_response

        with HTML__Service__Client() as _:
            request = Schema__HTML__Service__Request(html                = "<html>test</html>"                 ,
                                                     transformation_mode = Enum__HTML__Transformation_Mode.DICT)

            response = _.transform_html(request)

            assert response.status_code == 200
            assert '"key"'              in response.body                                         # JSON should be formatted
            assert response.success     is True
            assert request.obj()        == __(html               = '<html>test</html>'        ,
                                              transformation_mode = 'dict'                     )

            assert response.obj()       == __(error_message = None                             ,
                                              status_code  = 200                               ,
                                              content_type = 'application/json'               ,
                                              body         = '{\n  "key": "value"\n}'         ,
                                              headers      = __(content_type = 'application/json') ,
                                              success      = True                              )

    @patch('mgraph_ai_service_mitmproxy.service.html.HTML__Service__Client.requests.post')
    def test_transform_html__timeout(self, mock_post):                              # Test transformation timeout
        import requests
        mock_post.side_effect = requests.Timeout("Connection timeout")

        with HTML__Service__Client() as _:
            request = Schema__HTML__Service__Request(html                = "<html>test</html>"                       ,
                                                     transformation_mode = Enum__HTML__Transformation_Mode.XXX)

            response = _.transform_html(request)

            assert response.status_code == 504
            assert response.success     is False
            assert "timeout" in response.error_message.lower()
            assert response.obj() == __(error_message = 'HTML Service timeout: Connection timeout' ,
                                        status_code  = 504                                           ,
                                        content_type = 'text/plain'                                 ,
                                        body         = ''                                            ,
                                        headers      = __()                                          ,
                                        success      = False                                         )


    @patch('mgraph_ai_service_mitmproxy.service.html.HTML__Service__Client.requests.post')
    def test_transform_html__request_exception(self, mock_post):                    # Test transformation with request exception
        import requests
        mock_post.side_effect = requests.RequestException("Connection error")

        with HTML__Service__Client() as _:
            request = Schema__HTML__Service__Request(html                = "<html>test</html>"                       ,
                                                     transformation_mode = Enum__HTML__Transformation_Mode.HASHES)

            response = _.transform_html(request)

            assert response.status_code == 502
            assert response.success     is False
            assert "failed" in response.error_message.lower()
            assert response.obj() == __(error_message = 'HTML Service request failed: Connection error' ,
                                        status_code   = 502                                              ,
                                        content_type  = 'text/plain'                                     ,
                                        body          = ''                                               ,
                                        headers       = __()                                             ,
                                        success       = False                                            )


    @patch('mgraph_ai_service_mitmproxy.service.html.HTML__Service__Client.requests.post')
    def test_transform_html__generic_exception(self, mock_post):                    # Test transformation with generic exception
        mock_post.side_effect = Exception("Unexpected error")

        with HTML__Service__Client() as _:
            request = Schema__HTML__Service__Request(html                = "<html>test</html>"                       ,
                                                     transformation_mode = Enum__HTML__Transformation_Mode.ROUNDTRIP)

            response = _.transform_html(request)

            assert response.status_code == 500
            assert response.success     is False
            assert "unexpected" in response.error_message.lower()

    def test_transform_html__invalid_mode(self):                                    # Test transformation with invalid mode
        with HTML__Service__Client() as _:
            request = Schema__HTML__Service__Request(html                = "<html>test</html>"                       ,
                                                     transformation_mode = Enum__HTML__Transformation_Mode.OFF)

            response = _.transform_html(request)

            assert response.status_code == 400
            assert response.success     is False
            assert "invalid transformation mode" in response.error_message.lower()
            assert response.obj() == __(error_message = 'Invalid transformation mode: '
                                                        'Enum__HTML__Transformation_Mode.OFF' ,
                                         status_code  = 400                                     ,
                                         content_type = 'text/plain'                            ,
                                         body         = ''                                      ,
                                         headers      = __()                                    ,
                                         success      = False                                   )


    @patch('mgraph_ai_service_mitmproxy.service.html.HTML__Service__Client.requests.post')
    def test_transform_html__correct_endpoint_called(self, mock_post):              # Test correct endpoint construction
        mock_response             = Mock()
        mock_response.status_code = 200
        mock_response.headers     = {'content-type': 'text/html'}
        mock_response.content     = b'<html>test</html>'
        mock_post.return_value    = mock_response

        with HTML__Service__Client() as _:
            request = Schema__HTML__Service__Request(html                = "<html>original</html>"                     ,
                                                     transformation_mode = Enum__HTML__Transformation_Mode.HASHES)

            response = _.transform_html(request)

            # Verify correct URL was called
            call_args  = mock_post.call_args
            called_url = call_args[1]['url']
            assert called_url == f"{DEFAULT__HTML_SERVICE__BASE_URL}/html/to/html/hashes"
            assert response.obj() == __(error_message = None                           ,
                                        status_code  = 200                             ,
                                        content_type = 'text/html'                    ,
                                        body         = '<html>test</html>'            ,
                                        headers      = __(content_type = 'text/html') ,
                                        success      = True                            )


    @patch('mgraph_ai_service_mitmproxy.service.html.HTML__Service__Client.requests.post')
    def test_transform_html__correct_payload_sent(self, mock_post):                 # Test correct payload structure
        mock_response             = Mock()
        mock_response.status_code = 200
        mock_response.headers     = {'content-type': 'text/html'}
        mock_response.content     = b'<html>test</html>'
        mock_post.return_value    = mock_response

        html_content = "<html><body>Original Content</body></html>"

        with HTML__Service__Client() as _:
            request = Schema__HTML__Service__Request(html                = html_content                              ,
                                                     transformation_mode = Enum__HTML__Transformation_Mode.XXX)

            _.transform_html(request)

            # Verify correct payload was sent
            call_args = mock_post.call_args
            payload   = call_args[1]['json']
            assert payload == {"html": html_content}