from osbot_utils.type_safe.Type_Safe                                     import Type_Safe
from typing                                                              import Dict, Optional
from mgraph_ai_service_mitmproxy.schemas.debug.Enum__Debug__Command_Type import Enum__Debug__Command_Type
from mgraph_ai_service_mitmproxy.schemas.debug.Enum__Show__Command_Type  import Enum__Show__Command_Type


class Schema__Debug__Command(Type_Safe):                         # Debug command data structure
    command_type  : Enum__Debug__Command_Type                    # Type of debug command
    command_value : str                                          # Value/parameter for command
    show_type     : Optional[Enum__Show__Command_Type] = None    # For show commands, the specific type

    def is_show_command(self) -> bool:                           # Check if this is a show command
        """Check if this is a 'show' command"""
        return self.command_type == Enum__Debug__Command_Type.show

    def is_inject_command(self) -> bool:                         # Check if this is an inject command
        """Check if this is an 'inject' command"""
        return self.command_type == Enum__Debug__Command_Type.inject

    def is_replace_command(self) -> bool:                        # Check if this is a replace command
        """Check if this is a 'replace' command"""
        return self.command_type == Enum__Debug__Command_Type.replace

    def is_debug_mode(self) -> bool:                             # Check if debug mode is enabled
        """Check if this enables debug mode"""
        return self.command_type == Enum__Debug__Command_Type.debug

    def is_wcf_show_command(self) -> bool:                       # Check if this is a show command that requires WCF
        return (self.is_show_command() and
                self.show_type == Enum__Show__Command_Type.wcf_command)

    def is_response_data_show_command(self) -> bool:             # Check if this shows response data
        """Check if this is a show command for response-data"""
        return (self.is_show_command() and
                self.show_type == Enum__Show__Command_Type.response_data)

    @classmethod
    def from_debug_params(cls, debug_params: Dict[str, str]):    # Create commands from debug params
        """Parse debug parameters and create debug command objects"""
        commands = []

        for param_name, param_value in debug_params.items():
            command_type = Enum__Debug__Command_Type.from_param_name(param_name)

            if command_type:
                command = cls(
                    command_type  = command_type,
                    command_value = param_value
                )

                # For show commands, determine the show type
                if command_type == Enum__Debug__Command_Type.show:
                    command.show_type = Enum__Show__Command_Type.from_show_value(param_value)

                commands.append(command)

        return commands