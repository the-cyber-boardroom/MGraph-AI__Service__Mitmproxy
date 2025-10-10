import re
from http.cookies                                                               import SimpleCookie
from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from typing                                                                     import Dict, Optional, List
from osbot_utils.type_safe.primitives.core.Safe_Str                             import Safe_Str
from osbot_utils.type_safe.primitives.core.enums.Enum__Safe_Str__Regex_Mode     import Enum__Safe_Str__Regex_Mode
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text    import Safe_Str__Text
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                  import type_safe
from mgraph_ai_service_mitmproxy.schemas.proxy.Enum__WCF__Command_Type          import Enum__WCF__Command_Type

class Safe_Str__Cookie_Name(Safe_Str):                                          # Cookie names: alphanumeric, dots, underscores, hyphens
    max_length       = 256                                                      # Max cookie name length per RFC 6265
    regex            = re.compile(r'[^a-zA-Z0-9._-]')                           # Remove invalid cookie name characters
    regex_mode       = Enum__Safe_Str__Regex_Mode.REPLACE                       # Replace mode for sanitization
    replacement_char = '_'                                                      # Replace with underscore
    allow_empty      = False                                                    # Cookie names cannot be empty

class Safe_Str__Cookie_Value(Safe_Str):                                         # Cookie values: permissive but safe
    max_length       = 4096                                                     # Max cookie value length (browser limit)
    regex            = re.compile(r'[\x00-\x1F\x7F]')                           # Remove control characters only
    regex_mode       = Enum__Safe_Str__Regex_Mode.REPLACE                       # Replace mode for sanitization
    replacement_char = ''                                                       # Remove control chars entirely
    allow_empty      = True                                                     # Cookie values can be empty

class Schema__Cookie_Parser__Result(Type_Safe):                                 # Result of cookie header parsing
    cookies          : Dict[Safe_Str__Cookie_Name, Safe_Str__Cookie_Value]      # Parsed cookie name-value pairs
    parse_errors     : List[Safe_Str__Text]                                     # Any parsing errors encountered
    malformed_tokens : List[Safe_Str__Text]                                     # Tokens that couldn't be parsed

class Proxy__Cookie__Service(Type_Safe):                         # Cookie-based proxy control service
    """
    Service to parse and manage cookie-based proxy behavior control.

    Supported cookies:
    - mitm-show: Control what content to show (url-to-html, url-to-html-xxx, etc)
    - mitm-inject: Control what to inject (debug-panel, debug-banner)
    - mitm-replace: Text replacement (format: old:new)
    - mitm-debug: Enable debug mode (true/false)
    - mitm-rating: Set minimum rating for filtering (e.g., 0.5)
    - mitm-model: Override WCF model to use
    - mitm-cache: Enable response caching (true/false)
    """

    COOKIE_PREFIX = "mitm-"                                      # Prefix for all proxy control cookies

    # Cookie names
    COOKIE_SHOW    = "mitm-show"                                 # What to show (WCF commands)
    COOKIE_INJECT  = "mitm-inject"                               # What to inject (debug panels)
    COOKIE_REPLACE = "mitm-replace"                              # Text replacement
    COOKIE_DEBUG   = "mitm-debug"                                # Debug mode
    COOKIE_RATING  = "mitm-rating"                               # Minimum rating
    COOKIE_MODEL   = "mitm-model"                                # WCF model override
    COOKIE_CACHE   = "mitm-cache"                                # Cache responses

    def parse_cookies(self, headers: Dict[str, str]) -> Dict[str, str]: # Parse all cookies from request headers"""
        cookie_header = headers.get('cookie') or headers.get('Cookie')
        if not cookie_header:
            return {}

        parser_result = self.parse_cookies_from_header(cookie_header)
        return parser_result.cookies.json()                             # todo: change to return Schema__Cookie_Parser__Result instead of the json representation



    @type_safe
    def parse_cookies_from_header(self, cookie_header: str                 # Raw Cookie header value
                                   ) -> Schema__Cookie_Parser__Result:           # Parsed cookies and errors
        """
        Parse HTTP Cookie header with support for:
        - Malformed headers using commas instead of semicolons
        - JSON values containing braces and quotes
        - Escape sequences in quoted strings
        - Flag-like cookies without values

        Algorithm:
        1. Character-by-character scan tracking brace/quote depth
        2. Split on comma/semicolon only when depth is zero
        3. Extract name=value pairs from tokens
        4. Return sanitized Safe_Str types
        """
        parts           = []                                                     # Collected token strings
        cur             = []                                                     # Current token being built
        braces          = 0                                                      # Depth of { } nesting
        in_quote        = False                                                  # Inside " " quotes
        escape          = False                                                  # Next char is escaped

        for ch in cookie_header:                                                 # Character-by-character parsing
            if escape:                                                           # Previous char was backslash
                cur.append(ch)                                                   # Add escaped character literally
                escape = False
                continue

            if ch == '\\':                                                       # Escape sequence start
                cur.append(ch)                                                   # Preserve backslash
                escape = True
                continue

            if ch == '"':                                                        # Quote toggle
                in_quote = not in_quote                                          # Track quote state
                cur.append(ch)
                continue

            if ch == '{' and not in_quote:                                       # Open brace (not in string)
                braces += 1                                                      # Increase nesting depth
                cur.append(ch)
                continue

            if ch == '}' and not in_quote and braces > 0:                        # Close brace (not in string)
                braces -= 1                                                      # Decrease nesting depth
                cur.append(ch)
                continue

            if (ch == ';' or ch == ',') and braces == 0 and not in_quote:        # Separator at depth zero
                token = ''.join(cur).strip()                                     # Complete current token
                if token:
                    parts.append(token)
                cur = []                                                         # Start new token
                continue

            cur.append(ch)                                                       # Regular character

        last = ''.join(cur).strip()                                             # Final token after loop
        if last:
            parts.append(last)

        cookies         = {}                                                     # Result dictionary
        parse_errors    = []                                                     # Tokens that failed parsing
        malformed_tokens = []                                                    # Tokens without '=' separator

        for token in parts:                                                      # Process each token
            if '=' in token:                                                     # Standard name=value format
                name, value = token.split('=', 1)                                # Split on first equals only
                try:
                    safe_name  = Safe_Str__Cookie_Name(name.strip())            # Sanitize cookie name
                    safe_value = Safe_Str__Cookie_Value(value.strip())          # Sanitize cookie value
                    cookies[safe_name] = safe_value
                except Exception as e:
                    parse_errors.append(f"Error parsing '{token}': {str(e)}")
            else:                                                                # Flag cookie (no value)
                try:
                    safe_name = Safe_Str__Cookie_Name(token.strip())
                    cookies[safe_name] = Safe_Str__Cookie_Value('')             # Empty value for flags
                except Exception as e:
                    malformed_tokens.append(token)
                    parse_errors.append(f"Malformed token '{token}': {str(e)}")

        return Schema__Cookie_Parser__Result(cookies          = cookies         ,
                                             parse_errors     = parse_errors    ,
                                             malformed_tokens = malformed_tokens)



    def get_proxy_cookies(self, headers: Dict[str, str]          # Get only proxy control cookies
                         ) -> Dict[str, str]:                    # Proxy cookie name/value pairs
        """Extract only mitm-* cookies from request headers"""
        all_cookies = self.parse_cookies(headers)

        # Filter for proxy control cookies (mitm-*)
        proxy_cookies = {}
        for key, value in all_cookies.items():
            if key.startswith(self.COOKIE_PREFIX):
                proxy_cookies[key] = value
        return proxy_cookies

    def get_show_command(self, headers: Dict[str, str]           # Get show command from cookies
                        ) -> Optional[str]:                      # Show command value or None
        """Get the 'show' command from mitm-show cookie"""
        cookies = self.parse_cookies(headers)
        return cookies.get(self.COOKIE_SHOW)

    def get_inject_command(self, headers: Dict[str, str]         # Get inject command from cookies
                          ) -> Optional[str]:                    # Inject command value or None
        """Get the 'inject' command from mitm-inject cookie"""
        cookies = self.parse_cookies(headers)
        return cookies.get(self.COOKIE_INJECT)

    def get_replace_command(self, headers: Dict[str, str]        # Get replace command from cookies
                           ) -> Optional[str]:                   # Replace command value or None
        """Get the 'replace' command from mitm-replace cookie"""
        cookies = self.parse_cookies(headers)
        return cookies.get(self.COOKIE_REPLACE)

    def is_debug_enabled(self, headers: Dict[str, str]           # Check if debug mode enabled
                        ) -> bool:                               # Debug mode active
        """Check if debug mode is enabled via mitm-debug cookie"""
        cookies = self.parse_cookies(headers)
        debug_value = cookies.get(self.COOKIE_DEBUG, '').lower()
        return debug_value in ('true', '1', 'yes', 'on')

    def get_rating(self, headers: Dict[str, str]                 # Get rating from cookies
                  ) -> Optional[float]:                          # Rating value or None
        """Get minimum rating value from mitm-rating cookie"""
        cookies = self.parse_cookies(headers)
        rating_str = cookies.get(self.COOKIE_RATING)

        if rating_str:
            try:
                return float(rating_str)
            except ValueError:
                return None

        return None

    def get_model_override(self, headers: Dict[str, str]         # Get model override from cookies
                          ) -> Optional[str]:                    # Model name or None
        """Get WCF model override from mitm-model cookie"""
        cookies = self.parse_cookies(headers)
        return cookies.get(self.COOKIE_MODEL)

    def is_cache_enabled(self, headers: Dict[str, str]           # Check if cache enabled
                        ) -> bool:                               # Cache enabled
        """Check if response caching is enabled via mitm-cache cookie"""
        cookies = self.parse_cookies(headers)
        cache_value = cookies.get(self.COOKIE_CACHE, '').lower()
        return cache_value in ('true', '1', 'yes', 'on')

    def is_wcf_show_command(self, headers: Dict[str, str]        # Check if show command is WCF
                           ) -> bool:                            # Is WCF command
        """Check if the mitm-show cookie contains a WCF command"""
        show_value = self.get_show_command(headers)
        if not show_value:
            return False

        return Enum__WCF__Command_Type.is_wcf_command(show_value)

    def get_wcf_command_type(self, headers: Dict[str, str]       # Get WCF command type from cookies
                            ) -> Optional[Enum__WCF__Command_Type]:  # Command type or None
        """Parse WCF command type from mitm-show cookie"""
        show_value = self.get_show_command(headers)
        if not show_value:
            return None

        return Enum__WCF__Command_Type.from_show_param(show_value)

    def convert_to_debug_params(self, headers: Dict[str, str]    # Convert cookies to debug params format
                               ) -> Dict[str, str]:              # Debug params dict
        """
        Convert cookie-based controls to debug_params format
        for backward compatibility with existing code
        """
        debug_params = {}

        # Get show command
        show_value = self.get_show_command(headers)
        if show_value:
            debug_params['show'] = show_value

        # Get inject command
        inject_value = self.get_inject_command(headers)
        if inject_value:
            debug_params['inject'] = inject_value

        # Get replace command
        replace_value = self.get_replace_command(headers)
        if replace_value:
            debug_params['replace'] = replace_value

        # Get debug mode
        if self.is_debug_enabled(headers):
            debug_params['debug'] = 'true'

        return debug_params

    def get_cookie_summary(self, headers: Dict[str, str]         # Get summary of active cookies
                          ) -> Dict[str, any]:                   # Cookie summary
        """Get a summary of all active proxy control cookies"""
        return {
            'show_command'    : self.get_show_command(headers),
            'inject_command'  : self.get_inject_command(headers),
            'replace_command' : self.get_replace_command(headers),
            'debug_enabled'   : self.is_debug_enabled(headers),
            'rating'          : self.get_rating(headers),
            'model_override'  : self.get_model_override(headers),
            'cache_enabled'   : self.is_cache_enabled(headers),
            'is_wcf_command'  : self.is_wcf_show_command(headers),
            'all_proxy_cookies': self.get_proxy_cookies(headers)
        }

    def has_any_proxy_cookies(self, headers: Dict[str, str]      # Check if any proxy cookies present
                             ) -> bool:                          # Has proxy cookies
        """Check if request has any proxy control cookies"""
        proxy_cookies = self.get_proxy_cookies(headers)
        return len(proxy_cookies) > 0

    def validate_show_command(self, show_value: str              # Validate show command value
                             ) -> tuple[bool, Optional[str]]:    # (is_valid, error_message)
        """Validate that a show command value is recognized"""
        if not show_value:
            return (False, "Show command cannot be empty")

        # Check if it's a WCF command
        if Enum__WCF__Command_Type.is_wcf_command(show_value):
            command_type = Enum__WCF__Command_Type.from_show_param(show_value)
            if command_type:
                return (True, None)
            return (False, f"Invalid WCF command: {show_value}")

        # Check if it's response-data
        if show_value == 'response-data':
            return (True, None)

        return (False, f"Unknown show command: {show_value}")

    def create_cookie_header(self, cookie_name: str,             # Create Set-Cookie header value
                            cookie_value: str,
                            max_age: int = 3600,
                            path: str = "/"
                            ) -> str:                            # Set-Cookie header value
        """
        Create a Set-Cookie header value for setting proxy control cookies

        Example usage:
        headers["Set-Cookie"] = service.create_cookie_header("mitm-show", "url-to-html")
        """
        cookie = SimpleCookie()
        cookie[cookie_name] = cookie_value
        cookie[cookie_name]["path"] = path
        cookie[cookie_name]["max-age"] = max_age
        cookie[cookie_name]["samesite"] = "Lax"

        return cookie[cookie_name].OutputString()