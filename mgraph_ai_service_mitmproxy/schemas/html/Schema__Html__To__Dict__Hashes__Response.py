from typing                                                                         import Dict
from osbot_aws.aws.comprehend.schemas.safe_str.Safe_Str__AWS_Comprehend__Text       import Safe_Str__Comprehend__Text
from osbot_utils.type_safe.Type_Safe                                                import Type_Safe
from osbot_utils.type_safe.primitives.domains.cryptography.safe_str.Safe_Str__Hash  import Safe_Str__Hash


class Schema__Html__To__Dict__Hashes__Response(Type_Safe):
    """
    Response schema from HTML Service endpoint: POST /html/to/dict/hashes

    Contains:
    - html_dict: Structured HTML representation
    - hash_mapping: Dict mapping hashes to their original text values
    - Metadata about the parsing (node count, depth, etc.)
    """
    html_dict         : dict                                                # Structured HTML representation
    hash_mapping      : Dict[Safe_Str__Hash, Safe_Str__Comprehend__Text]    # Hash → original text mapping
    node_count        : int                       = 0                       # Total nodes in tree
    max_depth         : int                       = 0                       # Maximum depth reached
    total_text_hashes : int                       = 0                       # Number of text nodes with hashes
    max_depth_reached : bool                      = False                   # Whether max_depth limit hit

    def is_successful(self) -> bool:
        """Check if the response contains valid data"""
        return bool(self.html_dict) and self.node_count > 0