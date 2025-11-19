from unittest                                                                                                      import TestCase
from osbot_utils.testing.__                                                                                        import __
from osbot_utils.type_safe.Type_Safe                                                                               import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_Float                                                              import Safe_Float
from osbot_utils.type_safe.type_safe_core.collections.Type_Safe__Dict                                              import Type_Safe__Dict
from osbot_utils.type_safe.type_safe_core.collections.Type_Safe__List                                              import Type_Safe__List
from osbot_utils.utils.Objects                                                                                     import base_classes
from mgraph_ai_service_mitmproxy.schemas.semantic_text.client.Schema__Semantic_Text__Transformation__Request       import Schema__Semantic_Text__Transformation__Request
from mgraph_ai_service_mitmproxy.schemas.semantic_text.client.Schema__Classification__Criterion_Filter             import Schema__Classification__Criterion_Filter
from mgraph_ai_service_mitmproxy.schemas.semantic_text.client.enums.Enum__Text__Transformation__Engine_Mode        import Enum__Text__Transformation__Engine_Mode
from mgraph_ai_service_mitmproxy.schemas.semantic_text.client.enums.Enum__Text__Transformation__Mode               import Enum__Text__Transformation__Mode
from mgraph_ai_service_mitmproxy.schemas.semantic_text.client.enums.Enum__Classification__Logic_Operator           import Enum__Classification__Logic_Operator
from mgraph_ai_service_mitmproxy.schemas.semantic_text.client.enums.Enum__Text__Classification__Criteria           import Enum__Text__Classification__Criteria
from mgraph_ai_service_mitmproxy.schemas.semantic_text.client.enums.Enum__Classification__Filter_Mode              import Enum__Classification__Filter_Mode
from mgraph_ai_service_mitmproxy.service.semantic_text.Semantic_Text__Transformation__Request                      import Semantic_Text__Transformation__Request


class test_Semantic_Text__Transformation__Request(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        # Define shared test data
        cls.test_threshold_high   = Safe_Float(0.8)
        cls.test_threshold_medium = Safe_Float(0.6)
        cls.test_threshold_low    = Safe_Float(0.3)

    # ═══════════════════════════════════════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                                                         # Test auto-initialization of builder
        with Semantic_Text__Transformation__Request() as _:
            assert type(_)         is Semantic_Text__Transformation__Request
            assert base_classes(_) == [Type_Safe, object]

            # Verify data field is auto-initialized
            assert type(_.data) is Schema__Semantic_Text__Transformation__Request

            # Verify default values from schema
            assert _.data.engine_mode         == Enum__Text__Transformation__Engine_Mode.TEXT_HASH
            assert _.data.transformation_mode == Enum__Text__Transformation__Mode.XXX
            assert _.data.logic_operator      == Enum__Classification__Logic_Operator.AND
            assert _.data.criterion_filters   == []
            assert _.data.hash_mapping        == {}

    def test__init__data_field_auto_initialization(self):                                                           # Test that data field creates Schema instance
        with Semantic_Text__Transformation__Request() as _:                                                         # The data field should be a valid Schema instance
            assert type(_.data.hash_mapping)        is Type_Safe__Dict
            assert type(_.data.criterion_filters)   is Type_Safe__List
            assert type(_.data.engine_mode)         is Enum__Text__Transformation__Engine_Mode
            assert type(_.data.transformation_mode) is Enum__Text__Transformation__Mode
            assert type(_.data.logic_operator)      is Enum__Classification__Logic_Operator

    # ═══════════════════════════════════════════════════════════════════════════════════════════════════════════
    # Core Builder Methods Tests
    # ═══════════════════════════════════════════════════════════════════════════════════════════════════════════

    def test__set_engine_mode(self):                                                                                # Test setting engine mode
        with Semantic_Text__Transformation__Request() as _:
            result = _.set_engine_mode(Enum__Text__Transformation__Engine_Mode.AWS_COMPREHEND)
            assert result             is _                                                                                      # Verify fluent interface (returns self)
            assert _.data.engine_mode == Enum__Text__Transformation__Engine_Mode.AWS_COMPREHEND                     # Verify value was set

    def test__set_transformation_mode(self):                                                                        # Test setting transformation mode
        with Semantic_Text__Transformation__Request() as _:
            result = _.set_transformation_mode(Enum__Text__Transformation__Mode.HASHES)

            assert result is _
            assert _.data.transformation_mode == Enum__Text__Transformation__Mode.HASHES

    def test__set_logic_operator(self):                                                                             # Test setting logic operator
        with Semantic_Text__Transformation__Request() as _:
            result = _.set_logic_operator(Enum__Classification__Logic_Operator.OR)

            assert result is _
            assert _.data.logic_operator == Enum__Classification__Logic_Operator.OR

    # ═══════════════════════════════════════════════════════════════════════════════════════════════════════════
    # Filter Management Tests
    # ═══════════════════════════════════════════════════════════════════════════════════════════════════════════

    def test__add_filter(self):                                                                                     # Test adding a single filter
        with Semantic_Text__Transformation__Request() as _:
            result = _.add_filter(criterion    = Enum__Text__Classification__Criteria.POSITIVE,
                                 filter_mode  = Enum__Classification__Filter_Mode.ABOVE  ,
                                 threshold    = Safe_Float(0.7)                          )

            assert result is _                                                                                      # Fluent interface
            assert len(_.data.criterion_filters) == 1

            # Verify filter properties
            filter_obj = _.data.criterion_filters[0]
            assert type(filter_obj) is Schema__Classification__Criterion_Filter
            assert filter_obj.criterion   == Enum__Text__Classification__Criteria.POSITIVE
            assert filter_obj.filter_mode == Enum__Classification__Filter_Mode.ABOVE
            assert filter_obj.threshold   == Safe_Float(0.7)

    def test__add_filter__multiple_filters(self):                                                                   # Test adding multiple filters sequentially
        with Semantic_Text__Transformation__Request() as _:
            _.add_filter(Enum__Text__Classification__Criteria.POSITIVE,
                        Enum__Classification__Filter_Mode.ABOVE,
                        Safe_Float(0.7))
            _.add_filter(Enum__Text__Classification__Criteria.NEGATIVE,
                        Enum__Classification__Filter_Mode.BELOW,
                        Safe_Float(0.2))

            assert len(_.data.criterion_filters) == 2
            assert _.data.criterion_filters[0].criterion == Enum__Text__Classification__Criteria.POSITIVE
            assert _.data.criterion_filters[1].criterion == Enum__Text__Classification__Criteria.NEGATIVE

    def test__clear_filters(self):                                                                                  # Test clearing all filters
        with Semantic_Text__Transformation__Request() as _:
            _.add_filter(Enum__Text__Classification__Criteria.POSITIVE,
                        Enum__Classification__Filter_Mode.ABOVE,
                        Safe_Float(0.7))
            _.add_filter(Enum__Text__Classification__Criteria.NEGATIVE,
                        Enum__Classification__Filter_Mode.ABOVE,
                        Safe_Float(0.7))

            assert len(_.data.criterion_filters) == 2

            result = _.clear_filters()

            assert result is _                                                                                      # Fluent interface
            assert len(_.data.criterion_filters) == 0

    def test__set_filters(self):                                                                                    # Test replacing filters with new list
        with Semantic_Text__Transformation__Request() as _:
            # Add initial filters
            _.add_filter(Enum__Text__Classification__Criteria.POSITIVE,
                        Enum__Classification__Filter_Mode.ABOVE,
                        Safe_Float(0.7))

            # Create new filter list
            new_filters = [
                Schema__Classification__Criterion_Filter(
                    criterion    = Enum__Text__Classification__Criteria.NEGATIVE,
                    filter_mode  = Enum__Classification__Filter_Mode.BELOW,
                    threshold    = Safe_Float(0.3)
                )
            ]

            result = _.set_filters(new_filters)

            assert result is _
            assert len(_.data.criterion_filters) == 1
            assert _.data.criterion_filters[0].criterion == Enum__Text__Classification__Criteria.NEGATIVE

    # ═══════════════════════════════════════════════════════════════════════════════════════════════════════════
    # Common Use Case Helper Tests
    # ═══════════════════════════════════════════════════════════════════════════════════════════════════════════

    def test__filter_positive_above(self):                                                                          # Test filtering for positive sentiment
        with Semantic_Text__Transformation__Request() as _:
            result = _.filter_positive_above(Safe_Float(0.8))

            assert result is _
            assert len(_.data.criterion_filters) == 1
            assert _.data.criterion_filters[0].criterion   == Enum__Text__Classification__Criteria.POSITIVE
            assert _.data.criterion_filters[0].filter_mode == Enum__Classification__Filter_Mode.ABOVE
            assert _.data.criterion_filters[0].threshold   == Safe_Float(0.8)

    def test__filter_positive_above__default_threshold(self):                                                       # Test default threshold value
        with Semantic_Text__Transformation__Request() as _:
            _.filter_positive_above()

            assert _.data.criterion_filters[0].threshold == Safe_Float(0.7)                                         # Default from method signature

    def test__filter_negative_above(self):                                                                          # Test filtering for negative sentiment
        with Semantic_Text__Transformation__Request() as _:
            _.filter_negative_above(Safe_Float(0.75))

            assert len(_.data.criterion_filters) == 1
            assert _.data.criterion_filters[0].criterion   == Enum__Text__Classification__Criteria.NEGATIVE
            assert _.data.criterion_filters[0].filter_mode == Enum__Classification__Filter_Mode.ABOVE
            assert _.data.criterion_filters[0].threshold   == Safe_Float(0.75)

    def test__filter_neutral_above(self):                                                                           # Test filtering for neutral content
        with Semantic_Text__Transformation__Request() as _:
            _.filter_neutral_above(Safe_Float(0.65))

            assert _.data.criterion_filters[0].criterion   == Enum__Text__Classification__Criteria.NEUTRAL
            assert _.data.criterion_filters[0].threshold   == Safe_Float(0.65)

    def test__filter_mixed_above(self):                                                                             # Test filtering for mixed sentiment
        with Semantic_Text__Transformation__Request() as _:
            _.filter_mixed_above(Safe_Float(0.5))

            assert _.data.criterion_filters[0].criterion   == Enum__Text__Classification__Criteria.MIXED
            assert _.data.criterion_filters[0].threshold   == Safe_Float(0.5)

    def test__filter_negative_below(self):                                                                          # Test filtering for low negative content
        with Semantic_Text__Transformation__Request() as _:
            _.filter_negative_below(Safe_Float(0.15))

            assert _.data.criterion_filters[0].criterion   == Enum__Text__Classification__Criteria.NEGATIVE
            assert _.data.criterion_filters[0].filter_mode == Enum__Classification__Filter_Mode.BELOW
            assert _.data.criterion_filters[0].threshold   == Safe_Float(0.15)

    def test__filter_positive_below(self):                                                                          # Test filtering for low positive content
        with Semantic_Text__Transformation__Request() as _:
            _.filter_positive_below(Safe_Float(0.25))

            assert _.data.criterion_filters[0].criterion   == Enum__Text__Classification__Criteria.POSITIVE
            assert _.data.criterion_filters[0].filter_mode == Enum__Classification__Filter_Mode.BELOW
            assert _.data.criterion_filters[0].threshold   == Safe_Float(0.25)

    # ═══════════════════════════════════════════════════════════════════════════════════════════════════════════
    # Composite Pattern Tests
    # ═══════════════════════════════════════════════════════════════════════════════════════════════════════════

    def test__filter_purely_positive(self):                                                                         # Test purely positive filter (high pos, low neg)
        with Semantic_Text__Transformation__Request() as _:
            result = _.filter_purely_positive(positive_threshold = Safe_Float(0.8),
                                             negative_threshold = Safe_Float(0.05))

            assert result is _
            assert _.data.logic_operator == Enum__Classification__Logic_Operator.AND
            assert len(_.data.criterion_filters) == 2

            # Verify first filter (positive above)
            assert _.data.criterion_filters[0].criterion   == Enum__Text__Classification__Criteria.POSITIVE
            assert _.data.criterion_filters[0].filter_mode == Enum__Classification__Filter_Mode.ABOVE
            assert _.data.criterion_filters[0].threshold   == Safe_Float(0.8)

            # Verify second filter (negative below)
            assert _.data.criterion_filters[1].criterion   == Enum__Text__Classification__Criteria.NEGATIVE
            assert _.data.criterion_filters[1].filter_mode == Enum__Classification__Filter_Mode.BELOW
            assert _.data.criterion_filters[1].threshold   == Safe_Float(0.05)

    def test__filter_purely_positive__default_thresholds(self):                                                     # Test default threshold values
        with Semantic_Text__Transformation__Request() as _:
            _.filter_purely_positive()

            assert _.data.criterion_filters[0].threshold == Safe_Float(0.7)                                         # Default positive threshold
            assert _.data.criterion_filters[1].threshold == Safe_Float(0.1)                                         # Default negative threshold

    def test__filter_purely_negative(self):                                                                         # Test purely negative filter (high neg, low pos)
        with Semantic_Text__Transformation__Request() as _:
            result = _.filter_purely_negative(negative_threshold = Safe_Float(0.85),
                                             positive_threshold = Safe_Float(0.08))

            assert result is _
            assert _.data.logic_operator == Enum__Classification__Logic_Operator.AND
            assert len(_.data.criterion_filters) == 2

            # Verify filters
            assert _.data.criterion_filters[0].criterion   == Enum__Text__Classification__Criteria.NEGATIVE
            assert _.data.criterion_filters[0].filter_mode == Enum__Classification__Filter_Mode.ABOVE
            assert _.data.criterion_filters[0].threshold   == Safe_Float(0.85)

            assert _.data.criterion_filters[1].criterion   == Enum__Text__Classification__Criteria.POSITIVE
            assert _.data.criterion_filters[1].filter_mode == Enum__Classification__Filter_Mode.BELOW
            assert _.data.criterion_filters[1].threshold   == Safe_Float(0.08)

    def test__filter_any_extreme(self):                                                                             # Test any extreme sentiment filter (pos OR neg)
        with Semantic_Text__Transformation__Request() as _:
            result = _.filter_any_extreme(Safe_Float(0.9))

            assert result is _
            assert _.data.logic_operator == Enum__Classification__Logic_Operator.OR
            assert len(_.data.criterion_filters) == 2

            # Both filters use same threshold
            assert _.data.criterion_filters[0].criterion   == Enum__Text__Classification__Criteria.POSITIVE
            assert _.data.criterion_filters[0].filter_mode == Enum__Classification__Filter_Mode.ABOVE
            assert _.data.criterion_filters[0].threshold   == Safe_Float(0.9)

            assert _.data.criterion_filters[1].criterion   == Enum__Text__Classification__Criteria.NEGATIVE
            assert _.data.criterion_filters[1].filter_mode == Enum__Classification__Filter_Mode.ABOVE
            assert _.data.criterion_filters[1].threshold   == Safe_Float(0.9)

    def test__filter_any_extreme__default_threshold(self):                                                          # Test default extreme threshold
        with Semantic_Text__Transformation__Request() as _:
            _.filter_any_extreme()

            assert _.data.criterion_filters[0].threshold == Safe_Float(0.8)
            assert _.data.criterion_filters[1].threshold == Safe_Float(0.8)

    # ═══════════════════════════════════════════════════════════════════════════════════════════════════════════
    # Transformation Mode Helper Tests
    # ═══════════════════════════════════════════════════════════════════════════════════════════════════════════

    def test__mask_with_x(self):                                                                                    # Test xxx transformation helper
        with Semantic_Text__Transformation__Request() as _:
            result = _.mask_with_x()

            assert result is _
            assert _.data.transformation_mode == Enum__Text__Transformation__Mode.XXX

    def test__show_hashes(self):                                                                                    # Test hashes transformation helper
        with Semantic_Text__Transformation__Request() as _:
            result = _.show_hashes()

            assert result is _
            assert _.data.transformation_mode == Enum__Text__Transformation__Mode.HASHES

    def test__group_by_size(self):                                                                                  # Test abcde-by-size transformation helper
        with Semantic_Text__Transformation__Request() as _:
            result = _.group_by_size()

            assert result is _
            assert _.data.transformation_mode == Enum__Text__Transformation__Mode.ABCDE_BY_SIZE

    # ═══════════════════════════════════════════════════════════════════════════════════════════════════════════
    # Engine Mode Helper Tests
    # ═══════════════════════════════════════════════════════════════════════════════════════════════════════════

    def test__use_aws_comprehend(self):                                                                             # Test AWS Comprehend engine helper
        with Semantic_Text__Transformation__Request() as _:
            result = _.use_aws_comprehend()

            assert result is _
            assert _.data.engine_mode == Enum__Text__Transformation__Engine_Mode.AWS_COMPREHEND

    def test__use_text_hash(self):                                                                                  # Test text_hash engine helper
        with Semantic_Text__Transformation__Request() as _:
            result = _.use_text_hash()

            assert result is _
            assert _.data.engine_mode == Enum__Text__Transformation__Engine_Mode.TEXT_HASH

    def test__use_random(self):                                                                                     # Test random engine helper
        with Semantic_Text__Transformation__Request() as _:
            result = _.use_random()

            assert result is _
            assert _.data.engine_mode == Enum__Text__Transformation__Engine_Mode.RANDOM

    # ═══════════════════════════════════════════════════════════════════════════════════════════════════════════
    # Utility Method Tests
    # ═══════════════════════════════════════════════════════════════════════════════════════════════════════════

    def test__has_filters__no_filters(self):                                                                        # Test has_filters with no filters
        with Semantic_Text__Transformation__Request() as _:
            assert _.has_filters() is False

    def test__has_filters__with_filters(self):                                                                      # Test has_filters with filters added
        with Semantic_Text__Transformation__Request() as _:
            _.filter_positive_above()

            assert _.has_filters() is True

    def test__filter_count__empty(self):                                                                            # Test filter_count with no filters
        with Semantic_Text__Transformation__Request() as _:
            assert _.filter_count() == 0

    def test__filter_count__multiple(self):                                                                         # Test filter_count with multiple filters
        with Semantic_Text__Transformation__Request() as _:
            _.filter_positive_above()
            _.filter_negative_below()
            _.filter_neutral_above()

            assert _.filter_count() == 3

    # ═══════════════════════════════════════════════════════════════════════════════════════════════════════════
    # Fluent Interface / Method Chaining Tests
    # ═══════════════════════════════════════════════════════════════════════════════════════════════════════════

    def test__fluent_interface__simple_chain(self):                                                                 # Test basic method chaining
        with Semantic_Text__Transformation__Request() as _:
            result = (_.filter_negative_above(Safe_Float(0.7))
                       .mask_with_x()
                       .use_text_hash())

            # All methods return self
            assert result is _

            # Verify all settings applied
            assert len(_.data.criterion_filters) == 1
            assert _.data.transformation_mode == Enum__Text__Transformation__Mode.XXX
            assert _.data.engine_mode == Enum__Text__Transformation__Engine_Mode.TEXT_HASH

    def test__fluent_interface__complex_chain(self):                                                                # Test complex method chaining
        with Semantic_Text__Transformation__Request() as _:
            result = (_.filter_purely_positive(Safe_Float(0.8), Safe_Float(0.05))
                       .show_hashes()
                       .use_aws_comprehend())

            assert result is _
            assert len(_.data.criterion_filters) == 2
            assert _.data.logic_operator == Enum__Classification__Logic_Operator.AND
            assert _.data.transformation_mode == Enum__Text__Transformation__Mode.HASHES
            assert _.data.engine_mode == Enum__Text__Transformation__Engine_Mode.AWS_COMPREHEND

    def test__fluent_interface__with_clear(self):                                                                   # Test chaining with clear_filters
        with Semantic_Text__Transformation__Request() as _:
            result = (_.filter_positive_above()
                       .filter_negative_above()
                       .clear_filters()
                       .filter_neutral_above())

            assert result is _
            assert len(_.data.criterion_filters) == 1
            assert _.data.criterion_filters[0].criterion == Enum__Text__Classification__Criteria.NEUTRAL

    # ═══════════════════════════════════════════════════════════════════════════════════════════════════════════
    # Integration Tests - Real-world Usage Patterns
    # ═══════════════════════════════════════════════════════════════════════════════════════════════════════════

    def test__usage_pattern__mask_negative_content(self):                                                           # Usage: Mask negative content with xxx
        with Semantic_Text__Transformation__Request() as _:
            (_.filter_negative_above(Safe_Float(0.7))
               .mask_with_x()
               .use_text_hash())

            # Verify configuration matches use case
            assert _.data.criterion_filters[0].criterion == Enum__Text__Classification__Criteria.NEGATIVE
            assert _.data.transformation_mode == Enum__Text__Transformation__Mode.XXX
            assert _.data.engine_mode == Enum__Text__Transformation__Engine_Mode.TEXT_HASH

    def test__usage_pattern__show_hashes_for_extremes(self):                                                        # Usage: Show hash IDs for extreme sentiments
        with Semantic_Text__Transformation__Request() as _:
            (_.filter_any_extreme(Safe_Float(0.85))
               .show_hashes()
               .use_aws_comprehend())

            assert _.data.logic_operator == Enum__Classification__Logic_Operator.OR
            assert len(_.data.criterion_filters) == 2
            assert _.data.transformation_mode == Enum__Text__Transformation__Mode.HASHES

    def test__usage_pattern__group_neutral_by_size(self):                                                           # Usage: Group neutral content by text length
        with Semantic_Text__Transformation__Request() as _:
            (_.filter_neutral_above(Safe_Float(0.6))
               .group_by_size())

            assert _.data.criterion_filters[0].criterion == Enum__Text__Classification__Criteria.NEUTRAL
            assert _.data.transformation_mode == Enum__Text__Transformation__Mode.ABCDE_BY_SIZE

    def test__usage_pattern__purely_positive_with_hashes(self):                                                     # Usage: Find purely positive content and show hashes
        with Semantic_Text__Transformation__Request() as _:
            (_.filter_purely_positive(Safe_Float(0.8), Safe_Float(0.05))
               .show_hashes()
               .use_text_hash())

            assert _.data.logic_operator == Enum__Classification__Logic_Operator.AND
            assert len(_.data.criterion_filters) == 2
            assert _.data.transformation_mode == Enum__Text__Transformation__Mode.HASHES
            assert _.data.engine_mode == Enum__Text__Transformation__Engine_Mode.TEXT_HASH

    # ═══════════════════════════════════════════════════════════════════════════════════════════════════════════
    # .obj() Validation Tests
    # ═══════════════════════════════════════════════════════════════════════════════════════════════════════════

    def test__obj__default_state(self):                                                                             # Test .obj() with default initialization
        with Semantic_Text__Transformation__Request() as _:
            assert _.data.obj() == __(hash_mapping        = __()        ,                                          # Default state verification
                                      engine_mode         = 'text_hash' ,
                                      criterion_filters   = []          ,
                                      logic_operator      = 'and'       ,
                                      transformation_mode = 'xxx'       )

            assert _.data.obj() == __(hash_mapping        = __()        ,
                                      engine_mode         = Enum__Text__Transformation__Engine_Mode.TEXT_HASH ,
                                      criterion_filters   = []                                                ,
                                      logic_operator      = Enum__Classification__Logic_Operator.AND          ,
                                      transformation_mode = Enum__Text__Transformation__Mode.XXX              )

    def test__obj__with_filters(self):                                                                              # Test .obj() after adding filters
        with Semantic_Text__Transformation__Request() as _:
            _.filter_positive_above(Safe_Float(0.7))

            # Verify using .contains() for partial matching
            assert _.data.obj().contains(__(engine_mode         = 'text_hash',
                                            transformation_mode = 'xxx'      ,
                                            logic_operator      = 'and'      ))

            # Verify filter count
            assert len(_.data.criterion_filters) == 1

    def test__obj__complete_configuration(self):                                                                    # Test .obj() with full configuration
        with Semantic_Text__Transformation__Request() as _:
            (_.filter_purely_negative(Safe_Float(0.8), Safe_Float(0.1))
               .mask_with_x()
               .use_aws_comprehend())

            # Verify all settings
            obj_data = _.data.obj()
            assert obj_data.engine_mode         == Enum__Text__Transformation__Engine_Mode.AWS_COMPREHEND
            assert obj_data.transformation_mode == Enum__Text__Transformation__Mode.XXX
            assert obj_data.logic_operator      == Enum__Classification__Logic_Operator.AND
            assert len(obj_data.criterion_filters) == 2

    # ═══════════════════════════════════════════════════════════════════════════════════════════════════════════
    # Edge Cases and Validation Tests
    # ═══════════════════════════════════════════════════════════════════════════════════════════════════════════

    def test__edge_case__multiple_filter_modifications(self):                                                       # Test modifying filters multiple times
        with Semantic_Text__Transformation__Request() as _:
            _.filter_positive_above()
            _.filter_negative_above()
            assert _.filter_count() == 2

            _.clear_filters()
            assert _.filter_count() == 0

            _.filter_neutral_above()
            assert _.filter_count() == 1

    def test__edge_case__overwrite_engine_mode(self):                                                               # Test changing engine mode multiple times
        with Semantic_Text__Transformation__Request() as _:
            _.use_aws_comprehend()
            assert _.data.engine_mode == Enum__Text__Transformation__Engine_Mode.AWS_COMPREHEND

            _.use_text_hash()
            assert _.data.engine_mode == Enum__Text__Transformation__Engine_Mode.TEXT_HASH

            _.use_random()
            assert _.data.engine_mode == Enum__Text__Transformation__Engine_Mode.RANDOM

    def test__edge_case__overwrite_transformation_mode(self):                                                       # Test changing transformation mode multiple times
        with Semantic_Text__Transformation__Request() as _:
            _.mask_with_x()
            assert _.data.transformation_mode == Enum__Text__Transformation__Mode.XXX

            _.show_hashes()
            assert _.data.transformation_mode == Enum__Text__Transformation__Mode.HASHES

            _.group_by_size()
            assert _.data.transformation_mode == Enum__Text__Transformation__Mode.ABCDE_BY_SIZE

    def test__edge_case__logic_operator_changes(self):                                                              # Test changing logic operator affects behavior
        with Semantic_Text__Transformation__Request() as _:
            _.filter_positive_above()
            _.filter_negative_above()

            _.set_logic_operator(Enum__Classification__Logic_Operator.AND)
            assert _.data.logic_operator == Enum__Classification__Logic_Operator.AND

            _.set_logic_operator(Enum__Classification__Logic_Operator.OR)
            assert _.data.logic_operator == Enum__Classification__Logic_Operator.OR

    # ═══════════════════════════════════════════════════════════════════════════════════════════════════════════
    # Serialization Tests
    # ═══════════════════════════════════════════════════════════════════════════════════════════════════════════

    def test__serialization__data_to_json(self):                                                                    # Test that builder data serializes to JSON
        with Semantic_Text__Transformation__Request() as _:
            _.filter_positive_above(Safe_Float(0.7)).mask_with_x()

            json_data = _.data.json()

            # Verify JSON structure
            assert 'hash_mapping'        in json_data
            assert 'engine_mode'         in json_data
            assert 'criterion_filters'   in json_data
            assert 'logic_operator'      in json_data
            assert 'transformation_mode' in json_data

            # Verify enum serialization
            assert json_data['engine_mode']         == 'text_hash'
            assert json_data['transformation_mode'] == 'xxx'
            assert json_data['logic_operator']      == 'and'

    def test__serialization__roundtrip(self):                                                                       # Test JSON serialization and deserialization
        with Semantic_Text__Transformation__Request() as _:
            _.filter_purely_positive(Safe_Float(0.8), Safe_Float(0.1)).show_hashes()

            # Serialize
            json_data = _.data.json()

            # Deserialize
            restored = Schema__Semantic_Text__Transformation__Request.from_json(json_data)

            # Verify roundtrip preserves state
            assert restored.engine_mode         == _.data.engine_mode
            assert restored.transformation_mode == _.data.transformation_mode
            assert restored.logic_operator      == _.data.logic_operator
            assert len(restored.criterion_filters) == len(_.data.criterion_filters)