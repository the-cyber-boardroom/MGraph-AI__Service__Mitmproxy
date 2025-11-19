from osbot_aws.aws.comprehend.schemas.safe_str.Safe_Str__AWS_Comprehend__Text            import Safe_Str__Comprehend__Text
from osbot_utils.type_safe.Type_Safe                                                     import Type_Safe
from mgraph_ai_service_mitmproxy.schemas.semantic_text.enums.Enum__Transformation_Engine import Enum__Transformation_Engine


# todo: - add types definition to transformation_engine
#       - find a better class than Safe_Str__Comprehend__Text to represent the text (since by now we are a couple levels of separation of the AWS Comprehend call
#         that said, the 5k char limit that we have is introduced by AWS comprehend 
class Schema__Semantic_Text__Request(Type_Safe):                                               # Request schema for Semantic Text Service /text/transform endpoint
    text                   : Safe_Str__Comprehend__Text                                        # Text to transform
    transformation_engine  : Enum__Transformation_Engine                                        # Engine configuration