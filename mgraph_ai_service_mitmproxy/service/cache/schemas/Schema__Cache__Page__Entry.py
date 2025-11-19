from osbot_utils.type_safe.Type_Safe                                                       import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.safe_int.Timestamp_Now           import Timestamp_Now
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Url                   import Safe_Str__Url
from osbot_utils.type_safe.primitives.core.Safe_UInt                                       import Safe_UInt
from mgraph_ai_service_mitmproxy.schemas.Safe_Str__HTTP__Host                              import Safe_Str__HTTP__Host
from mgraph_ai_service_mitmproxy.service.cache.schemas.safe_str.Safe_Str__Proxy__Cache_Key import Safe_Str__Proxy__Cache_Key


class Schema__Cache__Page__Entry(Type_Safe):            # Main cache entry for a page
    url            : Safe_Str__Url                      # Original URL
    cache_key      : Safe_Str__Proxy__Cache_Key         # Hierarchical cache_key
    domain         : Safe_Str__HTTP__Host               # Extracted domain
    path           : str                                # URL path
    created_at     : Timestamp_Now                      #
    last_accessed  : Timestamp_Now                      # todo, see if this the best place to store this value (i.e this might be better saved in data files inside this cache_id)
    access_count   : Safe_UInt                          # Number of times accessed