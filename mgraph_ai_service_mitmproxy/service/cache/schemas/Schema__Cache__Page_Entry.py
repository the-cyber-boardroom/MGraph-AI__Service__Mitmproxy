from osbot_utils.type_safe.Type_Safe                                        import Type_Safe
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Url    import Safe_Str__Url
from osbot_utils.type_safe.primitives.core.Safe_UInt                        import Safe_UInt
from mgraph_ai_service_mitmproxy.schemas.Safe_Str__HTTP__Host               import Safe_Str__HTTP__Host


class Schema__Cache__Page_Entry(Type_Safe):                             # Main cache entry for a page
    url            : Safe_Str__Url                                      # Original URL
    cache_key      : str                                                # Hierarchical cache_key
    domain         : Safe_Str__HTTP__Host                               # Extracted domain
    path           : str                                                # URL path
    created_at     : str                                                # ISO timestamp
    last_accessed  : str                                                # ISO timestamp
    access_count   : Safe_UInt                      = Safe_UInt(0)      # Number of times accessed