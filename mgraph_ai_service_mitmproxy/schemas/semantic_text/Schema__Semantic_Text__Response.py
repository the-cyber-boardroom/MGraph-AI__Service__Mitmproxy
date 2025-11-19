# from typing                                                                                            import Dict, Optional
# from osbot_utils.type_safe.Type_Safe                                                                   import Type_Safe
# from osbot_utils.type_safe.primitives.core.Safe_UInt                                                   import Safe_UInt
# from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text                           import Safe_Str__Text
# from osbot_utils.type_safe.primitives.domains.cryptography.safe_str.Safe_Str__Hash                     import Safe_Str__Hash
# from osbot_aws.aws.comprehend.schemas.safe_str.Safe_Str__AWS_Comprehend__Text                          import Safe_Str__Comprehend__Text
# from mgraph_ai_service_mitmproxy.schemas.semantic_text.client.enums.Enum__Text__Transformation__Mode   import Enum__Text__Transformation__Mode
#
#
# class Schema__Text__Transformation__Response(Type_Safe):                        # Text transformation response to Mitmproxy
#     transformed_mapping     : Dict[Safe_Str__Hash, Safe_Str__Comprehend__Text]  # Modified hash → text mapping
#     transformation_mode     : Enum__Text__Transformation__Mode                  # Transformation mode applied
#     success                 : bool                                              # Whether transformation succeeded
#     total_hashes            : Safe_UInt                                         # Total number of hashes in input
#     transformed_hashes      : Safe_UInt                                         # Number of hashes that were transformed
#     error_message           : Optional[Safe_Str__Text]   = None                 # Error message if failed