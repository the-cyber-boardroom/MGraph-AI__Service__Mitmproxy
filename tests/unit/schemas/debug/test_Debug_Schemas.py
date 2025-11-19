from unittest                                                            import TestCase
from mgraph_ai_service_mitmproxy.schemas.debug.Enum__Debug__Command_Type import Enum__Debug__Command_Type
from mgraph_ai_service_mitmproxy.schemas.debug.Enum__Show__Command_Type  import Enum__Show__Command_Type
from mgraph_ai_service_mitmproxy.schemas.debug.Schema__Debug__Command    import Schema__Debug__Command


class test_Debug_Schemas(TestCase):

    def test_enum__debug__command_type__from_param_name(self):   # Test command type parsing
        assert Enum__Debug__Command_Type.from_param_name('show') == Enum__Debug__Command_Type.show
        assert Enum__Debug__Command_Type.from_param_name('inject') == Enum__Debug__Command_Type.inject
        assert Enum__Debug__Command_Type.from_param_name('replace') == Enum__Debug__Command_Type.replace
        assert Enum__Debug__Command_Type.from_param_name('debug') == Enum__Debug__Command_Type.debug

        # Special case
        assert Enum__Debug__Command_Type.from_param_name('inject_debug') == Enum__Debug__Command_Type.inject

        # Unknown
        assert Enum__Debug__Command_Type.from_param_name('unknown') is None

    def test_enum__show__command_type__from_show_value(self):    # Test show type parsing
        # WCF commands
        assert Enum__Show__Command_Type.from_show_value('url-to-html') == Enum__Show__Command_Type.wcf_command
        assert Enum__Show__Command_Type.from_show_value('url-to-html-xxx') == Enum__Show__Command_Type.wcf_command
        assert Enum__Show__Command_Type.from_show_value('url-to-ratings') == Enum__Show__Command_Type.wcf_command

        # Response data
        assert Enum__Show__Command_Type.from_show_value('response-data') == Enum__Show__Command_Type.response_data

        # Unknown
        assert Enum__Show__Command_Type.from_show_value('unknown-command') == Enum__Show__Command_Type.unknown
        assert Enum__Show__Command_Type.from_show_value('') == Enum__Show__Command_Type.unknown

    def test_schema__debug__command__is_methods(self):            # Test command type checking
        # Show command
        with Schema__Debug__Command() as cmd:
            cmd.command_type = Enum__Debug__Command_Type.show
            cmd.command_value = "response-data"

            assert cmd.is_show_command() is True
            assert cmd.is_inject_command() is False
            assert cmd.is_replace_command() is False
            assert cmd.is_debug_mode() is False

        # Inject command
        with Schema__Debug__Command() as cmd:
            cmd.command_type = Enum__Debug__Command_Type.inject
            cmd.command_value = "debug-panel"

            assert cmd.is_show_command() is False
            assert cmd.is_inject_command() is True

        # Replace command
        with Schema__Debug__Command() as cmd:
            cmd.command_type = Enum__Debug__Command_Type.replace
            cmd.command_value = "old:new"

            assert cmd.is_replace_command() is True

    def test_schema__debug__command__wcf_show_command(self):      # Test WCF show command detection
        with Schema__Debug__Command() as cmd:
            cmd.command_type = Enum__Debug__Command_Type.show
            cmd.command_value = "url-to-html"
            cmd.show_type = Enum__Show__Command_Type.wcf_command

            assert cmd.is_wcf_show_command() is True
            assert cmd.is_response_data_show_command() is False

    def test_schema__debug__command__response_data_show(self):    # Test response-data show detection
        with Schema__Debug__Command() as cmd:
            cmd.command_type = Enum__Debug__Command_Type.show
            cmd.command_value = "response-data"
            cmd.show_type = Enum__Show__Command_Type.response_data

            assert cmd.is_wcf_show_command() is False
            assert cmd.is_response_data_show_command() is True

    def test_schema__debug__command__from_debug_params(self):     # Test parsing from debug params
        debug_params = {
            'show': 'url-to-html',
            'inject': 'debug-panel',
            'replace': 'old:new',
            'debug': 'true'
        }

        commands = Schema__Debug__Command.from_debug_params(debug_params)

        assert len(commands) == 4

        # Check that we have all command types
        command_types = [cmd.command_type for cmd in commands]
        assert Enum__Debug__Command_Type.show       in command_types
        assert Enum__Debug__Command_Type.inject     in command_types
        assert Enum__Debug__Command_Type.replace    in command_types
        assert Enum__Debug__Command_Type.debug      in command_types

    def test_schema__debug__command__from_debug_params_with_show_type(self):  # Test show type detection
        debug_params = { 'show': 'url-to-html-xxx'}

        commands = Schema__Debug__Command.from_debug_params(debug_params)

        assert len(commands) == 1
        assert commands[0].command_type == Enum__Debug__Command_Type.show
        assert commands[0].show_type == Enum__Show__Command_Type.wcf_command