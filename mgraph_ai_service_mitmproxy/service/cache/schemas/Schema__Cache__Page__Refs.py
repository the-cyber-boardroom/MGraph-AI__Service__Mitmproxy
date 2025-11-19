from osbot_utils.type_safe.Type_Safe                                                          import Type_Safe
from osbot_utils.type_safe.primitives.domains.cryptography.safe_str.Safe_Str__Cache_Hash      import Safe_Str__Cache_Hash
from osbot_utils.type_safe.primitives.domains.identifiers.Random_Guid                         import Random_Guid
from mgraph_ai_service_mitmproxy.service.cache.schemas.safe_str.Safe_Str__Proxy__Cache_Key    import Safe_Str__Proxy__Cache_Key
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Json__Field_Path import Safe_Str__Json__Field_Path


class Schema__Cache__Page__Refs(Type_Safe):
    cache_id        : Random_Guid                    = None
    cache_key       : Safe_Str__Proxy__Cache_Key     = None
    cache_hash      : Safe_Str__Cache_Hash           = None
    json_field_path : Safe_Str__Json__Field_Path     = None
