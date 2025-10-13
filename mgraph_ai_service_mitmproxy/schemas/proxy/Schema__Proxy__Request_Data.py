from typing                                                                          import Dict, Optional, Any
from osbot_utils.type_safe.Type_Safe                                                 import Type_Safe
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Version      import Safe_Str__Version
from mgraph_ai_service_mitmproxy.schemas.Safe_Str__HTTP__Host                        import Safe_Str__HTTP__Host
from mgraph_ai_service_mitmproxy.schemas.Safe_Str__HTTP__Method                      import Safe_Str__HTTP__Method


class Schema__Proxy__Request_Data(Type_Safe):                        # Incoming request from mitmproxy
    method        : Safe_Str__HTTP__Method                           # HTTP method (GET, POST, etc)
    host          : Safe_Str__HTTP__Host                             # Target host
    path          : str                                              # Request path     # todo: replaced with Safe_Str__*
    original_path : Optional[str] = None                             # Deprecated: kept for backward compatibility
    headers       : Dict[str, str]                                   # Request headers (includes Cookie header)
    stats         : Dict[str, Any]                                   # Request statistics
    version       : Safe_Str__Version                                # Interceptor version