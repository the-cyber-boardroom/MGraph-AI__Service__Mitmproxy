from enum import Enum

class Enum__Debug__Command_Type(Enum):
    """Types of debug commands that can be executed"""
    show    = 'show'      # Display internal data (response-data, WCF commands)
    inject  = 'inject'    # Inject content into response (debug-panel, debug-banner)
    replace = 'replace'   # Replace text in response
    debug   = 'debug'     # Enable debug mode (shows banner)

    @classmethod
    def from_param_name(cls, param_name: str):                   # Get command type from parameter name
        """Convert a debug parameter name to command type"""
        param_name_lower = param_name.lower()

        for command_type in cls:
            if command_type.value == param_name_lower:
                return command_type

        # Handle special cases
        if param_name_lower == 'inject_debug':
            return cls.inject

        return None