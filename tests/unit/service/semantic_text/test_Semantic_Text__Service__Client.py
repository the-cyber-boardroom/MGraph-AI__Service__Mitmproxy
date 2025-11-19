from unittest                                                                                                      import TestCase
from mgraph_ai_service_mitmproxy.schemas.html.safe_dict.Safe_Dict__Hash__To__Text                                  import Safe_Dict__Hash__To__Text
from osbot_utils.testing.Temp_Env_Vars                                                                             import Temp_Env_Vars
from osbot_utils.testing.__                                                                                        import __
from osbot_utils.type_safe.Type_Safe                                                                               import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_Float                                                              import Safe_Float
from osbot_utils.type_safe.primitives.core.Safe_UInt                                                               import Safe_UInt
from osbot_utils.utils.Objects                                                                                     import base_classes
from mgraph_ai_service_mitmproxy.schemas.semantic_text.client.Schema__Semantic_Text__Transformation__Response      import Schema__Semantic_Text__Transformation__Response
from mgraph_ai_service_mitmproxy.schemas.semantic_text.client.Schema__Semantic_Text__Transformation__Request       import Schema__Semantic_Text__Transformation__Request
from mgraph_ai_service_mitmproxy.schemas.semantic_text.const__semantic_text                                        import ENV_VAR__AUTH__TARGET_SERVER__SEMANTIC_TEXT_SERVICE__BASE_URL
from mgraph_ai_service_mitmproxy.schemas.semantic_text.client.enums.Enum__Text__Transformation__Engine_Mode        import Enum__Text__Transformation__Engine_Mode
from mgraph_ai_service_mitmproxy.schemas.semantic_text.client.enums.Enum__Text__Transformation__Mode               import Enum__Text__Transformation__Mode
from mgraph_ai_service_mitmproxy.schemas.semantic_text.client.enums.Enum__Classification__Logic_Operator           import Enum__Classification__Logic_Operator
from mgraph_ai_service_mitmproxy.schemas.semantic_text.client.enums.Enum__Text__Classification__Criteria           import Enum__Text__Classification__Criteria
from mgraph_ai_service_mitmproxy.schemas.semantic_text.client.enums.Enum__Classification__Filter_Mode              import Enum__Classification__Filter_Mode
from mgraph_ai_service_mitmproxy.schemas.semantic_text.client.Schema__Classification__Criterion_Filter             import Schema__Classification__Criterion_Filter
from mgraph_ai_service_mitmproxy.service.semantic_text.Semantic_Text__Service__Client                              import Semantic_Text__Service__Client
from tests.unit.service.semantic_text.local_server.Local_Server__Semantic_Text__Service                            import local_server_semantic_text_service


class test_Semantic_Text__Service__Client(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        # Start local semantic text service for all tests
        with local_server_semantic_text_service as _:
            cls.service__semantic_text = _
            _.start()
            env_vars      = {ENV_VAR__AUTH__TARGET_SERVER__SEMANTIC_TEXT_SERVICE__BASE_URL: _.server_url}
            assert _.running() is True

        cls.temp_env_vars         = Temp_Env_Vars(env_vars=env_vars).set_vars()
        cls.client__semantic_text = Semantic_Text__Service__Client()

        # Define shared test data for reuse across tests
        cls.test_hash_single      = "aaa1234567"
        cls.test_text_single      = "Some Text"
        cls.test_hash_mapping     = {cls.test_hash_single: cls.test_text_single}

        cls.test_hash_multiple    = {"aaa1234567": "Positive text"      ,
                                      "bbb2345678": "Negative content"   ,
                                      "ccc3456789": "Neutral statement"  }

    @classmethod
    def tearDownClass(cls) -> None:
        with cls.service__semantic_text as _:
            _.stop()
            assert _.running() is False
        cls.temp_env_vars.restore_vars()

    # ═══════════════════════════════════════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                                                         # Test client initialization and type validation
        with self.client__semantic_text as _:
            assert type(_)              is Semantic_Text__Service__Client
            assert base_classes(_)      == [Type_Safe, object]                                                      # Type_Safe base class
            assert _.server_base_url()  == self.service__semantic_text.server_url

    def test__server_base_url(self):                                                                                # Test server URL configuration from env vars
        with self.client__semantic_text as _:
            server_url = _.server_base_url()
            assert server_url == self.service__semantic_text.server_url
            assert server_url.startswith('http')

            # Verify caching works (from @cache_on_self)
            assert _.server_base_url() is server_url                                                                # Same object reference

    def test__headers(self):                                                                               # Test authentication headers construction
        with self.client__semantic_text as _:
            headers = _.headers()
            assert type(headers)  is dict
            assert "content-type" in str(headers)
            assert _.headers()    is headers                                                               # Verify caching work, where same object reference

    # ═══════════════════════════════════════════════════════════════════════════════════════════════════════════
    # Transform Text - Basic Success Cases
    # ═══════════════════════════════════════════════════════════════════════════════════════════════════════════

    def test__transform_text__success__default_params(self):                                                        # Test default transformation (text_hash engine, xxx mode)
        request  = Schema__Semantic_Text__Transformation__Request(hash_mapping=self.test_hash_mapping)
        response = self.client__semantic_text.transform_text(request)

        with response as _:
            assert type(_) is Schema__Semantic_Text__Transformation__Response
            assert _.success             is True
            assert _.error_message       is None
            assert _.total_hashes        == 1
            assert _.transformed_hashes  == 1
            assert _.transformation_mode == 'xxx'

            assert self.test_hash_single in _.transformed_mapping                                                   # Verify transformed mapping structure
            assert _.transformed_mapping[self.test_hash_single] == 'xxxx xxxx'                                      # "Some Text" → "xxxx xxxx"

            assert response.obj() == __(error_message       = None  ,
                                        transformed_mapping = __(aaa1234567='xxxx xxxx'),
                                        transformation_mode = 'xxx' ,
                                        success             = True  ,
                                        total_hashes        = 1     ,
                                        transformed_hashes  = 1     )

    def test__transform_text__success__multiple_hashes(self):                                                       # Test transformation with multiple text entries
        request  = Schema__Semantic_Text__Transformation__Request(hash_mapping=self.test_hash_multiple)
        response = self.client__semantic_text.transform_text(request)

        with response as _:
            assert _.success            is True
            assert _.total_hashes       == 3
            assert _.transformed_hashes == 3
            assert len(_.transformed_mapping) == 3

            # All hashes should be transformed
            for hash_id in self.test_hash_multiple.keys():
                assert hash_id in _.transformed_mapping

            assert response.obj() == __(error_message       = None  ,
                                        transformed_mapping = __(aaa1234567='xxxxxxxx xxxx'     ,
                                                                 bbb2345678='xxxxxxxx xxxxxxx'  ,
                                                                 ccc3456789='xxxxxxx xxxxxxxxx'),
                                        transformation_mode = 'xxx' ,
                                        success             = True  ,
                                        total_hashes        = 3     ,
                                        transformed_hashes  = 3     )

    def test__transform_text__success__empty_mapping(self):                                                         # Test with empty hash mapping (edge case)
        request  = Schema__Semantic_Text__Transformation__Request(hash_mapping={})
        response = self.client__semantic_text.transform_text(request)

        with response as _:
            assert _.success             is True
            assert _.total_hashes        == 0
            assert _.transformed_hashes  == 0
            assert _.transformed_mapping == {}
            assert response.obj()        == __(error_message=None,
                                               transformed_mapping=__(),
                                               transformation_mode='xxx',
                                               success=True,
                                               total_hashes=0,
                                               transformed_hashes=0)

    # ═══════════════════════════════════════════════════════════════════════════════════════════════════════════
    # Transform Text - Transformation Modes
    # ═══════════════════════════════════════════════════════════════════════════════════════════════════════════

    def test__transform_text__mode_xxx(self):                                                                       # Test xxx transformation mode (character masking)
        request = Schema__Semantic_Text__Transformation__Request(hash_mapping        = self.test_hash_mapping              ,
                                                                 transformation_mode = Enum__Text__Transformation__Mode.XXX)
        response = self.client__semantic_text.transform_text(request)

        with response as _:
            assert _.success             is True
            assert _.transformation_mode == 'xxx'
            assert _.transformed_mapping[self.test_hash_single] == 'xxxx xxxx'                                      # Characters masked, space preserved
            assert response.obj()        == __(error_message=None,
                                               transformed_mapping=__(aaa1234567='xxxx xxxx'),
                                               transformation_mode='xxx',
                                               success=True,
                                               total_hashes=1,
                                               transformed_hashes=1)

    def test__transform_text__mode_hashes(self):                                                                    # Test hashes transformation mode (show hash IDs)
        request = Schema__Semantic_Text__Transformation__Request(hash_mapping        = self.test_hash_mapping,
                                                                 transformation_mode = Enum__Text__Transformation__Mode.HASHES)
        response = self.client__semantic_text.transform_text(request)

        with response as _:
            assert _.success             is True
            assert _.transformation_mode == 'hashes'
            assert _.transformed_mapping[self.test_hash_single] == self.test_hash_single                            # Text replaced with hash ID
            assert response.obj()        == __(error_message=None,
                                               transformed_mapping=__(aaa1234567='aaa1234567'),
                                               transformation_mode='hashes',
                                               success=True,
                                               total_hashes=1,
                                               transformed_hashes=1)

    def test__transform_text__mode_abcde_by_size(self):                                                             # Test abcde-by-size mode (length grouping)
        request = Schema__Semantic_Text__Transformation__Request(hash_mapping        = self.test_hash_multiple                       ,
                                                                 transformation_mode = Enum__Text__Transformation__Mode.ABCDE_BY_SIZE)
        response = self.client__semantic_text.transform_text(request)

        with response as _:
            assert _.success             is True
            assert _.transformation_mode == 'abcde-by-size'
            assert response.obj()        == __(error_message=None,
                                               transformed_mapping=__(aaa1234567='aaaaaaaa aaaa',
                                                                      bbb2345678='bbbbbbbb bbbbbbb',
                                                                      ccc3456789='ccccccc ccccccccc'),
                                               transformation_mode='abcde-by-size',
                                               success=True,
                                               total_hashes=3,
                                               transformed_hashes=3)

    # ═══════════════════════════════════════════════════════════════════════════════════════════════════════════
    # Transform Text - Engine Modes
    # ═══════════════════════════════════════════════════════════════════════════════════════════════════════════

    def test__transform_text__engine_text_hash(self):                                                               # Test deterministic text_hash engine
        request = Schema__Semantic_Text__Transformation__Request(hash_mapping = self.test_hash_mapping,
                                                                 engine_mode  = Enum__Text__Transformation__Engine_Mode.TEXT_HASH)
        response = self.client__semantic_text.transform_text(request)

        with response as _:
            assert _.success is True

            response2 = self.client__semantic_text.transform_text(request)              # Verify determinism - same input should give same output
            assert response.transformed_mapping == response2.transformed_mapping

            assert response.obj () == response2.obj ()
            assert response.json() == response2.json()

    def test__transform_text__engine_random(self):                                                                  # Test random engine (non-deterministic)
        request = Schema__Semantic_Text__Transformation__Request(hash_mapping = self.test_hash_mapping,
                                                                 engine_mode  = Enum__Text__Transformation__Engine_Mode.RANDOM)
        response = self.client__semantic_text.transform_text(request)

        with response as _:
            assert _.success      is True
            assert response.obj() == __(error_message=None,
                                        transformed_mapping=__(aaa1234567='xxxx xxxx'),
                                        transformation_mode='xxx',
                                        success=True,
                                        total_hashes=1,
                                        transformed_hashes=1)

    # ═══════════════════════════════════════════════════════════════════════════════════════════════════════════
    # Transform Text - With Filters
    # ═══════════════════════════════════════════════════════════════════════════════════════════════════════════

    def test__transform_text__with_single_filter(self):                                                             # Test transformation with single sentiment filter
        filter_criterion = Schema__Classification__Criterion_Filter(criterion    = Enum__Text__Classification__Criteria.NEGATIVE,
                                                                    filter_mode  = Enum__Classification__Filter_Mode.ABOVE      ,
                                                                    threshold    = Safe_Float(0.7)                              )

        request = Schema__Semantic_Text__Transformation__Request(hash_mapping      = self.test_hash_multiple,
                                                                 criterion_filters = [filter_criterion],
                                                                 logic_operator    = Enum__Classification__Logic_Operator.AND)
        response = self.client__semantic_text.transform_text(request)

        with response as _:
            assert _.success            is True
            assert _.total_hashes       == 3
            assert _.transformed_hashes <= _.total_hashes
            assert _.obj()              == __( error_message=None,
                                               transformed_mapping=__(aaa1234567='Positive text',
                                                                      bbb2345678='Negative content',
                                                                      ccc3456789='Neutral statement'),
                                               transformation_mode='xxx',
                                               success=True,
                                               total_hashes=3,
                                               transformed_hashes=0)

    def test__transform_text__with_multiple_filters_and_logic(self):                                                # Test multi-criteria filtering with AND logic
        filter_positive = Schema__Classification__Criterion_Filter(criterion    = Enum__Text__Classification__Criteria.POSITIVE,
                                                                   filter_mode  = Enum__Classification__Filter_Mode.ABOVE,
                                                                   threshold    = Safe_Float(0.2)
        )
        filter_negative = Schema__Classification__Criterion_Filter(criterion    = Enum__Text__Classification__Criteria.NEGATIVE,
                                                                   filter_mode  = Enum__Classification__Filter_Mode.BELOW   ,
                                                                   threshold    = Safe_Float(0.3)                           )

        request = Schema__Semantic_Text__Transformation__Request(hash_mapping      = self.test_hash_multiple,
                                                                 criterion_filters = [filter_positive, filter_negative],
                                                                 logic_operator    = Enum__Classification__Logic_Operator.AND)       # Both filters must match

        response = self.client__semantic_text.transform_text(request)

        with response as _:
            assert _.success      is True
            assert _.total_hashes == 3
            assert _.transformed_hashes <= _.total_hashes

            assert response.obj() == __(error_message=None,
                                        transformed_mapping=__(aaa1234567='Positive text'    ,
                                                               bbb2345678='Negative content' ,
                                                               ccc3456789='xxxxxxx xxxxxxxxx'),     # correct because this is the only mapping of the 3 that match
                                        transformation_mode='xxx',
                                        success=True,
                                        total_hashes=3,
                                        transformed_hashes=1)

    def test__transform_text__with_or_logic(self):                                                                  # Test multi-criteria filtering with OR logic
        filter_positive = Schema__Classification__Criterion_Filter(
            criterion    = Enum__Text__Classification__Criteria.POSITIVE,
            filter_mode  = Enum__Classification__Filter_Mode.ABOVE,
            threshold    = Safe_Float(0.3)
        )
        filter_negative = Schema__Classification__Criterion_Filter(
            criterion    = Enum__Text__Classification__Criteria.NEGATIVE,
            filter_mode  = Enum__Classification__Filter_Mode.ABOVE,
            threshold    = Safe_Float(0.3)
        )

        request = Schema__Semantic_Text__Transformation__Request(
            hash_mapping      = self.test_hash_multiple,
            criterion_filters = [filter_positive, filter_negative],
            logic_operator    = Enum__Classification__Logic_Operator.OR                                             # Either filter can match
        )
        response = self.client__semantic_text.transform_text(request)

        with response as _:
            assert _.success            is True
            assert _.total_hashes       == 3
            assert _.transformed_hashes <= _.total_hashes
            assert _.obj()              ==  __(error_message=None,
                                               transformed_mapping=__(aaa1234567='xxxxxxxx xxxx',
                                                                      bbb2345678='xxxxxxxx xxxxxxx',
                                                                      ccc3456789='Neutral statement'),
                                               transformation_mode='xxx',
                                               success=True,
                                               total_hashes=3,
                                               transformed_hashes=2)

    # ═══════════════════════════════════════════════════════════════════════════════════════════════════════════
    # Transform Text - .obj() Comprehensive Validation
    # ═══════════════════════════════════════════════════════════════════════════════════════════════════════════

    def test__transform_text__response_obj_validation(self):                                                        # Test complete response structure with .obj()
        request  = Schema__Semantic_Text__Transformation__Request(hash_mapping=self.test_hash_mapping)
        response = self.client__semantic_text.transform_text(request)

        # Use .obj() for comprehensive state validation
        assert response.obj() == __(error_message       = None                                     ,
                                    transformed_mapping = __(aaa1234567='xxxx xxxx')               ,
                                    transformation_mode = 'xxx'                                    ,
                                    success             = True                                     ,
                                    total_hashes        = 1                                        ,
                                    transformed_hashes  = 1                                        )

    def test__transform_text__response_type_validation(self):                                                       # Test response field types are correct
        request  = Schema__Semantic_Text__Transformation__Request(hash_mapping=self.test_hash_mapping)
        response = self.client__semantic_text.transform_text(request)

        with response as _:
            # Validate field types
            assert type(_.success)             is bool
            assert type(_.total_hashes)        is Safe_UInt
            assert type(_.transformed_hashes)  is Safe_UInt
            assert type(_.transformation_mode) is Enum__Text__Transformation__Mode
            assert type(_.transformed_mapping) is Safe_Dict__Hash__To__Text
            assert _.error_message is None or type(_.error_message) is str

    # ═══════════════════════════════════════════════════════════════════════════════════════════════════════════
    # Request Serialization Tests
    # ═══════════════════════════════════════════════════════════════════════════════════════════════════════════

    def test__transform_text__request_json_serialization(self):                                                     # Test request properly serializes to JSON
        request = Schema__Semantic_Text__Transformation__Request(
            hash_mapping        = self.test_hash_mapping,
            transformation_mode = Enum__Text__Transformation__Mode.XXX,
            engine_mode         = Enum__Text__Transformation__Engine_Mode.TEXT_HASH
        )

        json_data = request.json()

        # Verify JSON contains expected fields
        assert 'hash_mapping'            in json_data
        assert 'transformation_mode'     in json_data
        assert 'engine_mode'             in json_data
        assert json_data['hash_mapping'] == self.test_hash_mapping

        assert json_data                 == { 'criterion_filters'   : []                         ,
                                              'engine_mode'         : 'text_hash'                ,
                                              'hash_mapping'        : {'aaa1234567': 'Some Text'},
                                              'logic_operator'      : 'and'                      ,
                                              'transformation_mode' : 'xxx'                      }

    def test__transform_text__request_with_filters_serialization(self):                                             # Test request with filters serializes correctly
        filter_criterion = Schema__Classification__Criterion_Filter(
            criterion    = Enum__Text__Classification__Criteria.POSITIVE,
            filter_mode  = Enum__Classification__Filter_Mode.ABOVE,
            threshold    = Safe_Float(0.7)
        )

        request = Schema__Semantic_Text__Transformation__Request(
            hash_mapping      = self.test_hash_mapping,
            criterion_filters = [filter_criterion],
            logic_operator    = Enum__Classification__Logic_Operator.AND
        )

        json_data = request.json()

        # Verify filters are in JSON
        assert 'criterion_filters'                              in json_data
        assert len(json_data['criterion_filters'])              == 1
        assert json_data['criterion_filters'][0]['criterion']   == 'positive'
        assert json_data['criterion_filters'][0]['filter_mode'] == 'above'
        assert json_data['criterion_filters'][0]['threshold']   == 0.7

        assert json_data                                        == {'criterion_filters': [{'criterion': 'positive',
                                                                                            'filter_mode': 'above',
                                                                                            'threshold': 0.7}],
                                                                     'engine_mode': 'text_hash',
                                                                     'hash_mapping': {'aaa1234567': 'Some Text'},
                                                                     'logic_operator': 'and',
                                                                     'transformation_mode': 'xxx'}

    # ═══════════════════════════════════════════════════════════════════════════════════════════════════════════
    # Integration Tests - Real-world Scenarios
    # ═══════════════════════════════════════════════════════════════════════════════════════════════════════════

    def test__transform_text__scenario_mask_negative_content(self):                                                 # Scenario: Mask only negative content
        filter_negative = Schema__Classification__Criterion_Filter(
            criterion    = Enum__Text__Classification__Criteria.NEGATIVE,
            filter_mode  = Enum__Classification__Filter_Mode.ABOVE,
            threshold    = Safe_Float(0.7)
        )

        request = Schema__Semantic_Text__Transformation__Request(
            hash_mapping      = self.test_hash_multiple,
            criterion_filters = [filter_negative],
            transformation_mode = Enum__Text__Transformation__Mode.XXX,
            engine_mode       = Enum__Text__Transformation__Engine_Mode.TEXT_HASH
        )
        response = self.client__semantic_text.transform_text(request)

        with response as _:
            assert _.success             is True
            assert _.transformation_mode == 'xxx'
            assert _.total_hashes        == 3