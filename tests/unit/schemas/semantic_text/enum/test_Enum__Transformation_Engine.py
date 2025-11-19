from unittest                                                                            import TestCase
from mgraph_ai_service_mitmproxy.schemas.semantic_text.enums.Enum__Transformation_Engine import Enum__Transformation_Engine


class test_Enum__Transformation_Engine(TestCase):

    def test__enum_values(self):                                                                    # Test all enum values exist
        assert Enum__Transformation_Engine.AWS_COMPREHEND.value == "aws-comprehend"
        assert Enum__Transformation_Engine.TEXT_HASH.value      == "text-hash"
        assert Enum__Transformation_Engine.RANDOM.value         == "random"

    def test__enum_membership(self):                                                                # Test enum membership
        assert Enum__Transformation_Engine.TEXT_HASH      in Enum__Transformation_Engine
        assert Enum__Transformation_Engine.AWS_COMPREHEND in Enum__Transformation_Engine
        assert Enum__Transformation_Engine.RANDOM         in Enum__Transformation_Engine

    def test__enum_iteration(self):                                                                 # Test iterating over all engines
        all_engines = list(Enum__Transformation_Engine)
        
        assert len(all_engines) == 3
        assert Enum__Transformation_Engine.AWS_COMPREHEND in all_engines
        assert Enum__Transformation_Engine.TEXT_HASH      in all_engines
        assert Enum__Transformation_Engine.RANDOM         in all_engines
