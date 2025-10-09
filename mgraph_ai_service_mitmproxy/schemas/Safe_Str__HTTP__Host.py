import re
from osbot_utils.type_safe.primitives.core.Safe_Str import Safe_Str

TYPE_SAFE_STR__HTTP_HOST__REGEX      = re.compile(r'[^a-zA-Z0-9.\-]')  # Allow dots!
TYPE_SAFE_STR__HTTP_HOST__MAX_LENGTH = 253  # RFC 1035 max hostname length

# todo: refactor to OSBot_Utils

class Safe_Str__HTTP__Host(Safe_Str):       # Safe string for HTTP hostnames - preserves dots for DNS structure
    regex            = TYPE_SAFE_STR__HTTP_HOST__REGEX
    max_length       = TYPE_SAFE_STR__HTTP_HOST__MAX_LENGTH
    trim_whitespace  = True