from osbot_aws.aws.comprehend.schemas.safe_str.Safe_Str__AWS_Comprehend__Text       import Safe_Str__Comprehend__Text
from osbot_utils.type_safe.primitives.domains.cryptography.safe_str.Safe_Str__Hash  import Safe_Str__Hash
from osbot_utils.type_safe.type_safe_core.collections.Type_Safe__Dict               import Type_Safe__Dict

class Safe_Dict__Hash__To__Text(Type_Safe__Dict):
    expected_key_type   = Safe_Str__Hash
    expected_value_type = Safe_Str__Comprehend__Text

