from osbot_utils.type_safe.Type_Safe                                                 import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_UInt                                 import Safe_UInt


class Schema__Proxy__Stats(Type_Safe):                               # Proxy statistics tracking
    total_requests        : Safe_UInt                                # Total requests processed
    total_responses       : Safe_UInt                                # Total responses processed
    #hosts_seen            : Set[Safe_Str__Id]                        # Unique hosts encountered
    #paths_seen            : Set[str]                                 # Unique paths encountered
    total_bytes_processed : Safe_UInt                                # Total bytes of content processed
    content_modifications : Safe_UInt                                # Number of content modifications