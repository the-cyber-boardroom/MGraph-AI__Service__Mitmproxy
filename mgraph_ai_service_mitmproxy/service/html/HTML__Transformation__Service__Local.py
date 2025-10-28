import random
from typing import Dict
from osbot_utils.type_safe.Type_Safe import Type_Safe
from osbot_utils.type_safe.primitives.domains.cryptography.safe_str.Safe_Str__Hash import Safe_Str__Hash


class HTML__Transformation__Service__Local(Type_Safe):
    """
    Local HTML transformations using the hash-based system.

    This leverages the existing HTML Service infrastructure:
    1. /html/to/dict/hashes - Extract hash mapping
    2. Randomly select which hashes to mask
    3. /hashes/to/html - Reconstruct with masked hashes
    """

    randomness_percentage: float = 0.5  # 50% of text nodes will be masked

    def transform_xxx_random_via_hashes(self,
                                       html_dict: dict,
                                       hash_mapping: Dict[Safe_Str__Hash, str]
                                      ) -> Dict[Safe_Str__Hash, str]:
        """
        Randomly mask text nodes by modifying hash mapping.

        Args:
            html_dict: HTML structure (not modified, just passed through)
            hash_mapping: Dict of { hash: "original text" }

        Returns:
            Modified hash mapping with random masking
        """
        if not hash_mapping:
            return hash_mapping

        # Get all hashes
        all_hashes = list(hash_mapping.keys())

        # Randomly select which hashes to mask
        num_to_mask = int(len(all_hashes) * self.randomness_percentage)
        hashes_to_mask = random.sample(all_hashes, num_to_mask)

        # Create new mapping with masked values
        modified_mapping = {}
        for hash_key, original_text in hash_mapping.items():
            if hash_key in hashes_to_mask:
                # Mask this hash: replace with 'x' characters
                modified_mapping[hash_key] = self._mask_text(original_text)
            else:
                # Keep original text
                modified_mapping[hash_key] = original_text

        return modified_mapping

    def _mask_text(self, text: str) -> str:
        """
        Replace text with 'x' characters (preserving length).

        Strategy: Keep structure visible but mask content
        - Alphanumeric → 'x'
        - Whitespace → ' '
        - Punctuation → original
        """
        result = []
        for char in text:
            if char.isalnum():
                result.append('x')
            elif char.isspace():
                result.append(' ')
            else:
                result.append(char)  # Keep punctuation for readability

        return ''.join(result)