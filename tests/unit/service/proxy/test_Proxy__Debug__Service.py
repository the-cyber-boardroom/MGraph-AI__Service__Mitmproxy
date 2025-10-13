import pytest
from unittest                                                               import TestCase
from osbot_utils.testing.__                                                 import __, __SKIP__
from osbot_utils.utils.Env                                                  import in_github_action, load_dotenv
from mgraph_ai_service_mitmproxy.schemas.debug.Enum__Debug__Command_Type    import Enum__Debug__Command_Type
from mgraph_ai_service_mitmproxy.schemas.debug.Enum__Show__Command_Type     import Enum__Show__Command_Type
from mgraph_ai_service_mitmproxy.schemas.debug.Schema__Debug__Command       import Schema__Debug__Command
from mgraph_ai_service_mitmproxy.schemas.proxy.Schema__Proxy__Response_Data import Schema__Proxy__Response_Data
from mgraph_ai_service_mitmproxy.schemas.proxy.Schema__Proxy__Modifications import Schema__Proxy__Modifications
from mgraph_ai_service_mitmproxy.service.proxy.Proxy__Debug__Service        import Proxy__Debug__Service


class test_Proxy__Debug__Service(TestCase):

    @classmethod
    def setUpClass(cls):
        load_dotenv()
        cls.service = Proxy__Debug__Service().setup()

    def test__init__(self):                                        # Test initialization
        with self.service as _:
            assert type(_) is Proxy__Debug__Service
            assert _.wcf_service is not None
            assert _.html_service is not None
            assert _.json_service is not None

    def test_parse_debug_commands(self):                           # Test command parsing
        debug_params = { 'show': 'url-to-html'  ,
                         'inject': 'debug-panel',
                         'debug': 'true'        }

        commands = self.service.parse_debug_commands(debug_params)

        assert len(commands) == 3
        assert all(isinstance(cmd, Schema__Debug__Command) for cmd in commands)

    def test_process_show_command__wcf_command(self):    # Test WCF show command
        if in_github_action():
            pytest.skip("Skipping in GH actions because WCF credentials are not setup there")
        # Create command
        with Schema__Debug__Command() as command:
            command.command_type  = Enum__Debug__Command_Type.show
            command.command_value = 'url-to-html'
            command.show_type     = Enum__Show__Command_Type.wcf_command

        # Create response data
        with Schema__Proxy__Response_Data() as response_data:
            response_data.request       = {'url': 'https://example.com'}
            response_data.debug_params  = {'show': 'url-to-html'}
            response_data.response      = {}
            response_data.stats         = {}
            response_data.version       = 'v1.0.0'

        # Process command

        result = self.service.process_show_command(command, response_data)

        assert type(result) is Schema__Proxy__Modifications

        assert result.obj() == __( block_request         = False             ,
                                   block_status          = 403               ,
                                   block_message         = 'Blocked by proxy',
                                   include_stats         = False             ,
                                   modified_body         = __SKIP__          ,
                                   override_response     = True              ,
                                   override_status       = 200,
                                   override_content_type ='text/html; charset=utf-8',
                                   headers_to_add        =__SKIP__,
                                   headers_to_remove     = [],
                                   cached_response       = __(),
                                   stats                 = __())
        assert result is not None
        assert result.override_response is True
        assert result.modified_body.index('<title>Example Domain</title>') > 30

    def test_process_show_command__response_data(self):            # Test response-data show command
        # Create command
        with Schema__Debug__Command() as command:
            command.command_type  = Enum__Debug__Command_Type.show
            command.command_value = 'response-data'
            command.show_type     = Enum__Show__Command_Type.response_data
            #command.is_wcf_show_command  = Mock(return_value=False)
            #command.is_response_data_show_command = Mock(return_value=True)

        # Create response data
        with Schema__Proxy__Response_Data() as response_data:
            response_data.request       = {'method': 'GET', 'path': '/test'}
            response_data.debug_params  = {'show': 'response-data'}
            response_data.response      = {'status_code': 200}
            response_data.stats         = {}
            response_data.version       = 'v1.0.0'

        # Process command
        result = self.service.process_show_command(command, response_data)

        assert type(result)                 is Schema__Proxy__Modifications
        assert result                       is not None
        assert result.override_response     is True
        assert result.override_status       == 200
        assert result.override_content_type == 'application/json'
        assert 'response-data'              in result.headers_to_add.get('x-debug-show', '')

    def test_process_inject_command__debug_panel(self):            # Test debug panel injection
        # Create command
        with Schema__Debug__Command() as command:
            command.command_type = Enum__Debug__Command_Type.inject
            command.command_value = 'debug-panel'

        # Create response data
        with Schema__Proxy__Response_Data() as response_data:
            response_data.request = {'method': 'GET'}
            response_data.debug_params = {'inject': 'debug-panel'}
            response_data.response = {'headers': {}}
            response_data.stats = {}
            response_data.version = 'v1.0.0'

        # Process command
        result = self.service.process_inject_command(command, response_data)

        assert result is not None
        assert result.inject_panel is True
        assert result.panel_content is not None
        assert '🔧 Debug Panel' in result.panel_content

    def test_process_debug_mode(self):                             # Test debug mode banner
        # Create response data
        with Schema__Proxy__Response_Data() as response_data:
            response_data.request = {'path': '/test'}
            response_data.debug_params = {'debug': 'true'}
            response_data.response = {}
            response_data.stats = {}
            response_data.version = 'v1.0.0'

        # Process debug mode
        result = self.service.process_debug_mode(response_data)

        assert result is not None
        assert result.inject_banner is True
        assert result.banner_content is not None
        assert '🔧 DEBUG MODE' in result.banner_content

    def test_process_replace_command(self):                        # Test replace command
        # Create command
        with Schema__Debug__Command() as command:
            command.command_type = Enum__Debug__Command_Type.replace
            command.command_value = 'old:new'

        # Process command
        result = self.service.process_replace_command(command)

        assert result is not None
        assert result == ('old', 'new')

    def test_process_replace_command__invalid_format(self):        # Test replace with invalid format
        # Create command
        with Schema__Debug__Command() as command:
            command.command_type = Enum__Debug__Command_Type.replace
            command.command_value = 'no-colon'

        # Process command
        result = self.service.process_replace_command(command)

        assert result is None

    def test_process_debug_commands__html_with_banner(self):       # Test HTML with debug banner
        # Create response data
        with Schema__Proxy__Response_Data() as response_data:
            response_data.request       = { 'path': '/test' }
            response_data.debug_params  = { 'debug': 'true' }
            response_data.response      = { 'content_type': 'text/html',
                                            'body': '<html><body><h1>Test</h1></body></html>'}
            response_data.stats = {}
            response_data.version = 'v1.0.0'

        # Create modifications
        with Schema__Proxy__Modifications() as modifications:
            # Process commands
            self.service.process_debug_commands(response_data, modifications)

            assert modifications.modified_body is not None
            assert '🔧 DEBUG MODE' in modifications.modified_body
            assert '<h1>Test</h1>' in modifications.modified_body
            assert modifications.headers_to_add.get('X-Debug-Banner-Injected') == 'true'

    def test_process_debug_commands__json_with_debug(self):        # Test JSON with debug fields
        # Create response data
        with Schema__Proxy__Response_Data() as response_data:
            response_data.request = {'path': '/api/test'}
            response_data.debug_params = {'inject_debug': 'true'}
            response_data.response     = {  'content_type': 'application/json',
                                            'body': '{"key": "value"}'  }
            response_data.stats = {}
            response_data.version = 'v1.0.0'

        # Create modifications
        with Schema__Proxy__Modifications() as modifications:
            # Process commands
            self.service.process_debug_commands(response_data, modifications)

            assert modifications.modified_body is not None
            assert '_debug_params' in modifications.modified_body
            assert '_debug_injected' in modifications.modified_body

    def test_process_debug_commands__no_body(self):                # Test with no body content
        # Create response data
        with Schema__Proxy__Response_Data() as response_data:
            response_data.request = {'path': '/test'}
            response_data.debug_params = {'debug': 'true'}
            response_data.response = {
                'content_type': 'text/html',
                'body': ''
            }
            response_data.stats = {}
            response_data.version = 'v1.0.0'

        # Create modifications
        with Schema__Proxy__Modifications() as modifications:
            # Process commands
            self.service.process_debug_commands(response_data, modifications)

            # Should not modify anything with no body
            assert modifications.modified_body is None