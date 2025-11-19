from typing                                                                                                 import Dict, List
from osbot_utils.type_safe.Type_Safe                                                                        import Type_Safe
from osbot_utils.type_safe.primitives.domains.cryptography.safe_str.Safe_Str__Hash                          import Safe_Str__Hash
from osbot_aws.aws.comprehend.schemas.safe_str.Safe_Str__AWS_Comprehend__Text                               import Safe_Str__Comprehend__Text
from mgraph_ai_service_mitmproxy.schemas.semantic_text.client.Schema__Classification__Criterion_Filter      import Schema__Classification__Criterion_Filter
from mgraph_ai_service_mitmproxy.schemas.semantic_text.client.enums.Enum__Classification__Logic_Operator    import Enum__Classification__Logic_Operator
from mgraph_ai_service_mitmproxy.schemas.semantic_text.client.enums.Enum__Text__Transformation__Engine_Mode import Enum__Text__Transformation__Engine_Mode
from mgraph_ai_service_mitmproxy.schemas.semantic_text.client.enums.Enum__Text__Transformation__Mode        import Enum__Text__Transformation__Mode


class Schema__Semantic_Text__Transformation__Request(Type_Safe):                             # Text transformation request with multi-criteria sentiment filtering

    # Core Data
    hash_mapping            : Dict[Safe_Str__Hash, Safe_Str__Comprehend__Text]                                                      # Hash → original text mapping from HTML Service

    # Phase 1: Classification & Selection
    engine_mode             : Enum__Text__Transformation__Engine_Mode       = Enum__Text__Transformation__Engine_Mode.TEXT_HASH     # Engine to use for classification ({} = transform all)
    criterion_filters       : List[Schema__Classification__Criterion_Filter]                                                        # Filters to apply ({} = transform all)
    logic_operator          : Enum__Classification__Logic_Operator          = Enum__Classification__Logic_Operator.AND              # How to combine filters (AND/OR)

    # Phase 2: Transformation
    transformation_mode     : Enum__Text__Transformation__Mode              = Enum__Text__Transformation__Mode.XXX                  # Transformation mode to apply
