from osbot_utils.type_safe.Type_Safe import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_UInt import Safe_UInt
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Version import Safe_Str__Version
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Id import Safe_Str__Id
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Url import Safe_Str__Url


class Schema__Cache_Service_Info(Type_Safe):                 # Information about the cache service
    base_url        : Safe_Str__Url                          # Cache service base URL
    storage_mode    : Safe_Str__Id           = "unknown"     # Storage backend (s3, local, etc)
    ttl_hours       : Safe_UInt              = 0             # Time-to-live in hours
    s3_bucket       : Safe_Str__Id           = None          # S3 bucket if using S3
    version         : Safe_Str__Version      = None          # Service version
    is_reachable    : bool                   = False         # Whether service is reachable

