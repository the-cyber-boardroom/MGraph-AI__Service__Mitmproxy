from osbot_utils.type_safe.Type_Safe                                                                     import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_Float                                                    import Safe_Float
from mgraph_ai_service_mitmproxy.schemas.semantic_text.client.enums.Enum__Classification__Filter_Mode    import Enum__Classification__Filter_Mode
from mgraph_ai_service_mitmproxy.schemas.semantic_text.client.enums.Enum__Text__Classification__Criteria import Enum__Text__Classification__Criteria


class Schema__Classification__Criterion_Filter(Type_Safe):                     # Single criterion filter condition for multi-criteria filtering
    criterion       : Enum__Text__Classification__Criteria                     # Criterion to filter by (positive/negative/neutral/mixed)
    filter_mode     : Enum__Classification__Filter_Mode                        # How to compare ratings (above/below)
    threshold       : Safe_Float                                               # Primary threshold value for filtering
