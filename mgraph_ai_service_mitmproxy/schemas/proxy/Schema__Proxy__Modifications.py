from osbot_utils.type_safe.Type_Safe                                         import Type_Safe
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text import Safe_Str__Text
from mgraph_ai_service_mitmproxy.schemas.Safe_UInt__HTTP_Status              import Safe_UInt__HTTP_Status
from typing                                                                  import Dict, List, Any, Optional


class Schema__Proxy__Modifications(Type_Safe):                              # Modifications to apply
    headers_to_add    : Dict[str, str]                                      # Headers to add
    headers_to_remove : List[str]                                           # Headers to remove
    cached_response   : Dict                                                # Allow direct response to proxy
    block_request     : bool            = False                             # Whether to block request
    block_status      : Safe_UInt__HTTP_Status = 403                        # Status code if blocked
    block_message     : Safe_Str__Text          = "Blocked by proxy"        # Block message
    include_stats     : bool            = False                             # Include stats in response
    stats             : Dict[str, Any]                                      # Statistics to include
    modified_body     : Optional[str]   = None                              # Modified body content (if any)
    override_response : bool            = False                             # Whether to completely override response
    override_status   : Optional[int]   = None                              # Override status code
    override_content_type : Optional[str] = None                            # Override content type