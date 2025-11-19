from typing                                                                                                  import List
from osbot_utils.type_safe.Type_Safe                                                                         import Type_Safe
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                                               import type_safe
from osbot_utils.type_safe.primitives.core.Safe_Float                                                        import Safe_Float
from mgraph_ai_service_mitmproxy.schemas.semantic_text.client.Schema__Classification__Criterion_Filter       import Schema__Classification__Criterion_Filter
from mgraph_ai_service_mitmproxy.schemas.semantic_text.client.Schema__Semantic_Text__Transformation__Request import Schema__Semantic_Text__Transformation__Request
from mgraph_ai_service_mitmproxy.schemas.semantic_text.client.enums.Enum__Classification__Filter_Mode        import Enum__Classification__Filter_Mode
from mgraph_ai_service_mitmproxy.schemas.semantic_text.client.enums.Enum__Classification__Logic_Operator     import Enum__Classification__Logic_Operator
from mgraph_ai_service_mitmproxy.schemas.semantic_text.client.enums.Enum__Text__Classification__Criteria     import Enum__Text__Classification__Criteria
from mgraph_ai_service_mitmproxy.schemas.semantic_text.client.enums.Enum__Text__Transformation__Engine_Mode  import Enum__Text__Transformation__Engine_Mode
from mgraph_ai_service_mitmproxy.schemas.semantic_text.client.enums.Enum__Text__Transformation__Mode         import Enum__Text__Transformation__Mode


class Semantic_Text__Transformation__Request(Type_Safe):                                                                    # Builder for text transformation requests with fluent API
    
    data: Schema__Semantic_Text__Transformation__Request                                                                     # The underlying schema data (auto-initialized)
    
    # ═══════════════════════════════════════════════════════════════════════════════════════════════════════════
    # Core Builder Methods - Set fundamental properties
    # ═══════════════════════════════════════════════════════════════════════════════════════════════════════════
    
    @type_safe
    def set_engine_mode(self, engine_mode: Enum__Text__Transformation__Engine_Mode                                 # Set classification engine (aws_comprehend, text_hash, random)
                        ) -> 'Semantic_Text__Transformation__Request':                                                       # Returns self for chaining
        self.data.engine_mode = engine_mode
        return self
    
    @type_safe
    def set_transformation_mode(self, transformation_mode: Enum__Text__Transformation__Mode                        # Set visual transformation (xxx, hashes, abcde-by-size)
                                ) -> 'Semantic_Text__Transformation__Request':                                               # Returns self for chaining
        self.data.transformation_mode = transformation_mode
        return self
    
    @type_safe
    def set_logic_operator(self, logic_operator: Enum__Classification__Logic_Operator                              # Set how to combine filters (AND/OR)
                           ) -> 'Semantic_Text__Transformation__Request':                                                    # Returns self for chaining
        self.data.logic_operator = logic_operator
        return self
    
    # ═══════════════════════════════════════════════════════════════════════════════════════════════════════════
    # Filter Management - Add and configure sentiment filters
    # ═══════════════════════════════════════════════════════════════════════════════════════════════════════════
    
    @type_safe
    def add_filter(self, criterion    : Enum__Text__Classification__Criteria,                                      # Add a sentiment filter criterion
                         filter_mode  : Enum__Classification__Filter_Mode   ,
                         threshold    : Safe_Float
                   ) -> 'Semantic_Text__Transformation__Request':                                                            # Returns self for chaining
        filter_obj = Schema__Classification__Criterion_Filter(criterion    = criterion   ,
                                                              filter_mode  = filter_mode ,
                                                              threshold    = threshold   )
        self.data.criterion_filters.append(filter_obj)
        return self
    
    @type_safe
    def clear_filters(self) -> 'Semantic_Text__Transformation__Request':                                                    # Remove all filters (transform all hashes)
        self.data.criterion_filters.clear()
        return self
    
    @type_safe
    def set_filters(self, filters: List[Schema__Classification__Criterion_Filter]                                  # Replace all filters with new list
                    ) -> 'Semantic_Text__Transformation__Request':                                                           # Returns self for chaining
        self.data.criterion_filters.clear()
        self.data.criterion_filters.extend(filters)
        return self
    
    # ═══════════════════════════════════════════════════════════════════════════════════════════════════════════
    # Common Use Case Helpers - Pre-configured filter patterns
    # ═══════════════════════════════════════════════════════════════════════════════════════════════════════════
    
    @type_safe
    def filter_positive_above(self, threshold: Safe_Float = Safe_Float(0.7)                                        # Filter for highly positive sentiment
                              ) -> 'Semantic_Text__Transformation__Request':                                                 # Returns self for chaining
        return self.add_filter(criterion    = Enum__Text__Classification__Criteria.POSITIVE,
                              filter_mode   = Enum__Classification__Filter_Mode.ABOVE      ,
                              threshold     = threshold                                     )
    
    @type_safe
    def filter_negative_above(self, threshold: Safe_Float = Safe_Float(0.7)                                        # Filter for highly negative sentiment
                              ) -> 'Semantic_Text__Transformation__Request':                                                 # Returns self for chaining
        return self.add_filter(criterion    = Enum__Text__Classification__Criteria.NEGATIVE,
                              filter_mode  = Enum__Classification__Filter_Mode.ABOVE       ,
                              threshold    = threshold                                      )
    
    @type_safe
    def filter_neutral_above(self, threshold: Safe_Float = Safe_Float(0.6)                                         # Filter for neutral content
                             ) -> 'Semantic_Text__Transformation__Request':                                                  # Returns self for chaining
        return self.add_filter(criterion    = Enum__Text__Classification__Criteria.NEUTRAL,
                              filter_mode  = Enum__Classification__Filter_Mode.ABOVE      ,
                              threshold    = threshold                                     )
    
    @type_safe
    def filter_mixed_above(self, threshold: Safe_Float = Safe_Float(0.5)                                           # Filter for mixed sentiment
                           ) -> 'Semantic_Text__Transformation__Request':                                                    # Returns self for chaining
        return self.add_filter(criterion    = Enum__Text__Classification__Criteria.MIXED,
                              filter_mode  = Enum__Classification__Filter_Mode.ABOVE    ,
                              threshold    = threshold                                   )
    
    @type_safe
    def filter_negative_below(self, threshold: Safe_Float = Safe_Float(0.1)                                        # Filter for low negative content
                              ) -> 'Semantic_Text__Transformation__Request':                                                 # Returns self for chaining
        return self.add_filter(criterion    = Enum__Text__Classification__Criteria.NEGATIVE,
                              filter_mode  = Enum__Classification__Filter_Mode.BELOW      ,
                              threshold    = threshold                                     )
    
    @type_safe
    def filter_positive_below(self, threshold: Safe_Float = Safe_Float(0.3)                                        # Filter for low positive content
                              ) -> 'Semantic_Text__Transformation__Request':                                                 # Returns self for chaining
        return self.add_filter(criterion    = Enum__Text__Classification__Criteria.POSITIVE,
                              filter_mode  = Enum__Classification__Filter_Mode.BELOW      ,
                              threshold    = threshold                                     )
    
    # ═══════════════════════════════════════════════════════════════════════════════════════════════════════════
    # Composite Patterns - Common multi-filter scenarios
    # ═══════════════════════════════════════════════════════════════════════════════════════════════════════════
    
    @type_safe
    def filter_purely_positive(self, positive_threshold: Safe_Float = Safe_Float(0.7),                             # Filter for purely positive (high pos, low neg)
                                     negative_threshold: Safe_Float = Safe_Float(0.1)
                                ) -> 'Semantic_Text__Transformation__Request':                                               # Returns self for chaining
        self.set_logic_operator(Enum__Classification__Logic_Operator.AND)
        self.filter_positive_above(positive_threshold)
        self.filter_negative_below(negative_threshold)
        return self
    
    @type_safe
    def filter_purely_negative(self, negative_threshold: Safe_Float = Safe_Float(0.7),                             # Filter for purely negative (high neg, low pos)
                                     positive_threshold: Safe_Float = Safe_Float(0.1)
                                ) -> 'Semantic_Text__Transformation__Request':                                               # Returns self for chaining
        self.set_logic_operator(Enum__Classification__Logic_Operator.AND)
        self.filter_negative_above(negative_threshold)
        self.filter_positive_below(positive_threshold)
        return self
    
    @type_safe
    def filter_any_extreme(self, threshold: Safe_Float = Safe_Float(0.8)                                           # Filter for any extreme sentiment (pos OR neg)
                           ) -> 'Semantic_Text__Transformation__Request':                                                    # Returns self for chaining
        self.set_logic_operator(Enum__Classification__Logic_Operator.OR)
        self.filter_positive_above(threshold)
        self.filter_negative_above(threshold)
        return self
    
    # ═══════════════════════════════════════════════════════════════════════════════════════════════════════════
    # Transformation Mode Helpers - Set transformation with semantic names
    # ═══════════════════════════════════════════════════════════════════════════════════════════════════════════
    
    @type_safe
    def mask_with_x(self) -> 'Semantic_Text__Transformation__Request':                                                      # Mask text with 'xxx' (preserves punctuation)
        return self.set_transformation_mode(Enum__Text__Transformation__Mode.XXX)
    
    @type_safe
    def show_hashes(self) -> 'Semantic_Text__Transformation__Request':                                                      # Replace text with hash IDs
        return self.set_transformation_mode(Enum__Text__Transformation__Mode.HASHES)
    
    @type_safe
    def group_by_size(self) -> 'Semantic_Text__Transformation__Request':                                                    # Group by text length (a,b,c,d,e)
        return self.set_transformation_mode(Enum__Text__Transformation__Mode.ABCDE_BY_SIZE)
    
    # ═══════════════════════════════════════════════════════════════════════════════════════════════════════════
    # Engine Mode Helpers - Set classification engine with semantic names
    # ═══════════════════════════════════════════════════════════════════════════════════════════════════════════
    
    @type_safe
    def use_aws_comprehend(self) -> 'Semantic_Text__Transformation__Request':                                               # Use AWS Comprehend ML engine
        return self.set_engine_mode(Enum__Text__Transformation__Engine_Mode.AWS_COMPREHEND)
    
    @type_safe
    def use_text_hash(self) -> 'Semantic_Text__Transformation__Request':                                                    # Use deterministic hash-based engine
        return self.set_engine_mode(Enum__Text__Transformation__Engine_Mode.TEXT_HASH)
    
    @type_safe
    def use_random(self) -> 'Semantic_Text__Transformation__Request':                                                       # Use random engine (for testing)
        return self.set_engine_mode(Enum__Text__Transformation__Engine_Mode.RANDOM)
    
    # ═══════════════════════════════════════════════════════════════════════════════════════════════════════════
    # Utility Methods
    # ═══════════════════════════════════════════════════════════════════════════════════════════════════════════

    def has_filters(self) -> bool:                                                                                  # Check if any filters are configured
        return len(self.data.criterion_filters) > 0

    def filter_count(self) -> int:                                                                                  # Get number of configured filters
        return len(self.data.criterion_filters)