from typing                                                                                            import Dict, Optional
from mgraph_ai_service_mitmproxy.schemas.html.safe_dict.Safe_Dict__Hash__To__Text                      import Safe_Dict__Hash__To__Text
from osbot_utils.type_safe.Type_Safe                                                                   import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_UInt                                                   import Safe_UInt
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text                           import Safe_Str__Text
from mgraph_ai_service_mitmproxy.schemas.semantic_text.client.enums.Enum__Text__Transformation__Mode   import Enum__Text__Transformation__Mode


class Schema__Semantic_Text__Transformation__Response(Type_Safe):               # Text transformation response to Mitmproxy
    transformed_mapping     : Safe_Dict__Hash__To__Text                         # Modified hash → text mapping
    transformation_mode     : Enum__Text__Transformation__Mode                  # Transformation mode applied
    success                 : bool                                              # Whether transformation succeeded
    total_hashes            : Safe_UInt                                         # Total number of hashes in input
    transformed_hashes      : Safe_UInt                                         # Number of hashes that were transformed
    error_message           : Optional[Safe_Str__Text]   = None                 # Error message if failed