from osbot_utils.type_safe.Type_Safe                                                 import Type_Safe
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Version      import Safe_Str__Version
from typing                                                                          import Dict, Any

class Schema__Proxy__Response_Data(Type_Safe):                       # Incoming response from mitmproxy
    request       : Dict[str, Any]                                   # Original request info (includes headers with Cookie)
    response      : Dict[str, Any]                                   # Response details
    stats         : Dict[str, Any]                                   # Response statistics
    version       : Safe_Str__Version                                # Interceptor version