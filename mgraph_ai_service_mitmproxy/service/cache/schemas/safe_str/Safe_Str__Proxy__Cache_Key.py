import re
from osbot_utils.type_safe.primitives.core.Safe_Str import Safe_Str

TYPE_SAFE_STR__URL__MAX_LENGTH = 1024
TYPE_SAFE_STR__URL__REGEX      = re.compile(r'[^a-zA-Z0-9_.\-/]')

class Safe_Str__Proxy__Cache_Key(Safe_Str):
    regex                      = TYPE_SAFE_STR__URL__REGEX
    max_length                 = TYPE_SAFE_STR__URL__MAX_LENGTH
    trim_whitespace            = True