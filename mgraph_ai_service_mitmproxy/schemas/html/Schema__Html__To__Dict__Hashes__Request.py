from osbot_utils.type_safe.Type_Safe import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_UInt import Safe_UInt


class Schema__Html__To__Dict__Hashes__Request(Type_Safe):
    """
    Request schema for converting HTML to dict with hash mapping.

    This calls the HTML Service endpoint: POST /html/to/dict/hashes

    The response provides:
    - html_dict: Structured representation of HTML
    - hash_mapping: Dict of { hash: "original text" }
    """
    html      : str       = ""            # Source HTML content to process
    max_depth : Safe_UInt = Safe_UInt(256)  # Maximum tree depth to traverse

    def to_json_payload(self) -> dict:
        """Convert to JSON payload for HTML Service API"""
        return {
            "html": self.html,
            "max_depth": int(self.max_depth)
        }