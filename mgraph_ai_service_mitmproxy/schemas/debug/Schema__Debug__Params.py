from osbot_utils.type_safe.Type_Safe  import Type_Safe
from typing                           import Dict, List, Optional

class Schema__Debug__Params(Type_Safe):                          # Parsed debug parameters
    raw_params      : Dict[str, str]                             # Raw debug parameters from query
    show_value      : Optional[str]           = None             # Value of 'show' parameter
    inject_value    : Optional[str]           = None             # Value of 'inject' parameter
    replace_value   : Optional[str]           = None             # Value of 'replace' parameter
    debug_enabled   : bool                    = False            # Whether debug mode is on
    inject_debug    : bool                    = False            # Whether inject_debug is on

    @classmethod
    def from_query_params(cls, query_params: Dict[str, str]      # Parse from query parameters
                         ):                                      # Debug params object
        """Parse debug parameters from query string"""
        debug_params = {}

        # Known debug parameter keys
        debug_keys = ['show', 'inject', 'replace', 'debug', 'inject_debug']

        # Extract debug parameters
        for key in debug_keys:
            if key in query_params:
                debug_params[key] = query_params[key]

        # Create schema
        return cls(
            raw_params      = debug_params,
            show_value      = debug_params.get('show'),
            inject_value    = debug_params.get('inject'),
            replace_value   = debug_params.get('replace'),
            debug_enabled   = debug_params.get('debug') == 'true',
            inject_debug    = debug_params.get('inject_debug') == 'true'
        )

    def has_debug_params(self) -> bool:                          # Check if any debug params
        """Check if any debug parameters are present"""
        return len(self.raw_params) > 0

    def has_show_command(self) -> bool:                          # Check if has show command
        """Check if show command is present"""
        return self.show_value is not None

    def has_inject_command(self) -> bool:                        # Check if has inject command
        """Check if inject command is present"""
        return self.inject_value is not None

    def has_replace_command(self) -> bool:                       # Check if has replace command
        """Check if replace command is present"""
        return self.replace_value is not None

    def is_debug_mode(self) -> bool:                             # Check if debug mode active
        """Check if debug mode is active"""
        return self.debug_enabled or self.inject_debug

    def get_debug_command_names(self) -> List[str]:              # Get list of command names
        """Get list of debug command names present"""
        commands = []
        if self.show_value:
            commands.append('show')
        if self.inject_value:
            commands.append('inject')
        if self.replace_value:
            commands.append('replace')
        if self.debug_enabled:
            commands.append('debug')
        if self.inject_debug:
            commands.append('inject_debug')
        return commands

    def to_dict(self) -> Dict[str, str]:                         # Convert to dict
        """Convert to dictionary for response data"""
        return self.raw_params.copy()