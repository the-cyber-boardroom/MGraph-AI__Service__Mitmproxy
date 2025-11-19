from enum import Enum

class Enum__Show__Command_Type(Enum):
    """Types of 'show' commands"""
    response_data = 'response-data'  # Show complete response data as JSON
    wcf_command   = 'wcf-command'    # WCF url-to-* commands (handled by WCF service)
    unknown       = 'unknown'        # Unknown show command

    @classmethod
    def from_show_value(cls, show_value: str):                   # Parse show command type
        """Determine the type of show command from the value"""
        if not show_value:
            return cls.unknown

        # Check for WCF commands (url-to-*)
        if show_value.startswith('url-to'):
            return cls.wcf_command

        # Check for response-data
        if show_value == 'response-data':
            return cls.response_data

        return cls.unknown