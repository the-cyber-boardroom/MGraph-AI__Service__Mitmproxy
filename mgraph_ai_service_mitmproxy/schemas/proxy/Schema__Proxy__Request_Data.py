from typing                                                                          import Dict, Optional, Any
from osbot_utils.type_safe.Type_Safe                                                 import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Id      import Safe_Str__Id
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Version      import Safe_Str__Version
from mgraph_ai_service_mitmproxy.schemas.Safe_Str__HTTP_Method                       import Safe_Str__HTTP_Method


class Schema__Proxy__Request_Data(Type_Safe):                        # Incoming request from mitmproxy
    method        : Safe_Str__HTTP_Method                            # HTTP method (GET, POST, etc)
    host          : Safe_Str__Id                                     # Target host
    path          : str                                              # Request path
    original_path : Optional[str] = None                             # Deprecated: kept for backward compatibility
    debug_params  : Dict[str, str]                                   # Empty from interceptor - populated from cookies
    headers       : Dict[str, str]                                   # Request headers (includes Cookie header)
    stats         : Dict[str, Any]                                   # Request statistics
    version       : Safe_Str__Version                                # Interceptor version