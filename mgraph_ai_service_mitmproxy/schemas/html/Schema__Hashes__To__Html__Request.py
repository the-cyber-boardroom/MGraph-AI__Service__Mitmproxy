from typing                                                                         import Dict
from osbot_aws.aws.comprehend.schemas.safe_str.Safe_Str__AWS_Comprehend__Text       import Safe_Str__Comprehend__Text
from osbot_utils.type_safe.Type_Safe                                                import Type_Safe
from osbot_utils.type_safe.primitives.domains.cryptography.safe_str.Safe_Str__Hash  import Safe_Str__Hash


class Schema__Hashes__To__Html__Request(Type_Safe):
    """
    Request schema for reconstructing HTML from hash mapping.

    This calls the HTML Service endpoint: POST /hashes/to/html

    Takes the html_dict structure and a modified hash_mapping to reconstruct HTML.
    """
    html_dict    : dict                                                    # HTML structure (from to__dict__hashes)
    hash_mapping : Dict[Safe_Str__Hash, Safe_Str__Comprehend__Text]        # Modified hash mapping (with masked values)

    def to_json_payload(self) -> dict:
        """Convert to JSON payload for HTML Service API"""
        # Convert Safe_Str__Hash keys to strings for JSON serialization
        hash_mapping_json = {}
        for hash_key, text_value in self.hash_mapping.items():
            hash_mapping_json[str(hash_key)] = text_value

        return {
            "html_dict": self.html_dict,
            "hash_mapping": hash_mapping_json
        }