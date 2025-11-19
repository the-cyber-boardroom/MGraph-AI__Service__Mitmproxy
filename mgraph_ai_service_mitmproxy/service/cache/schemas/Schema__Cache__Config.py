from osbot_utils.type_safe.Type_Safe                                                 import Type_Safe
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Url             import Safe_Str__Url
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Id      import Safe_Str__Id
from osbot_utils.type_safe.primitives.core.Safe_UInt                                 import Safe_UInt
from mgraph_ai_service_cache_client.schemas.cache.enums.Enum__Cache__Store__Strategy import Enum__Cache__Store__Strategy


class Schema__Cache__Config(Type_Safe):                                                             # Cache service configuration
    enabled          : bool                         = True                                          # Whether caching is enabled
    base_url         : Safe_Str__Url                = Safe_Str__Url("https://cache.dev.mgraph.ai")  # Cache service URL
    api_key          : str                          = ""                                            # API key for authentication
    api_key_header   : str                          = "X-API-Key"                                   # Header name for API key
    namespace        : Safe_Str__Id                 = Safe_Str__Id("wcf-results")                   # Cache namespace
    timeout          : Safe_UInt                    = Safe_UInt(30)                                 # Request timeout in seconds

    # Storage strategy - UPDATED to KEY_BASED for semantic cache_key support
    strategy         : Enum__Cache__Store__Strategy = Enum__Cache__Store__Strategy.KEY_BASED        # Cache storage strategy

    # Data file versioning
    data_file_id     : str                          = "latest"                                      # Data file identifier

    # Feature flags
    cache_metadata   : bool                         = True                                          # Whether to cache WCF metadata
    track_stats      : bool                         = True                                          # Whether to track cache statistics