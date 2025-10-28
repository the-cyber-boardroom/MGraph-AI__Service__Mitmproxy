import random
from typing import Dict
from osbot_utils.type_safe.Type_Safe import Type_Safe
from osbot_utils.type_safe.primitives.domains.cryptography.safe_str.Safe_Str__Hash import Safe_Str__Hash
from osbot_utils.utils.Dev import pprint

from mgraph_ai_service_mitmproxy.service.html.Text__Grouping__Service import Text__Grouping__Service


class HTML__Transformation__Service__Local(Type_Safe):
    """
    Local HTML transformations using the hash-based system.

    This leverages the existing HTML Service infrastructure:
    1. /html/to/dict/hashes - Extract hash mapping
    2. Randomly select which hashes to transform (LOCAL)
    3. /hashes/to/html - Reconstruct with transformed hashes

    Supports:
    - xxx-random: Randomly mask 50% of text nodes with 'x'
    - hashes-random: Randomly replace 50% of text with their hash values
    """

    randomness_percentage: float = 0.5  # Default: 50% of text nodes will be transformed

    def transform_xxx_random_via_hashes(self,
                                       html_dict: dict,
                                       hash_mapping: Dict[Safe_Str__Hash, str]
                                      ) -> Dict[Safe_Str__Hash, str]:
        """
        Randomly mask text nodes with 'x' characters.

        Strategy:
        1. Randomly select X% of hashes (based on randomness_percentage)
        2. For selected hashes: replace text with 'x' characters
        3. For unselected hashes: keep original text

        Example:
            Input:  { "abc123": "Hello", "def456": "World" }
            Output: { "abc123": "xxxxx", "def456": "World" }
        """
        if not hash_mapping:
            return hash_mapping

        # Get all hashes and randomly select which to mask
        selected_hashes = self._randomly_select_hashes(hash_mapping)

        # Create new mapping with masked values
        modified_mapping = {}
        for hash_key, original_text in hash_mapping.items():
            if hash_key in selected_hashes:
                modified_mapping[hash_key] = self._mask_text(original_text)
            else:
                modified_mapping[hash_key] = original_text

        return modified_mapping

    def transform_hashes_random_via_hashes(self,
                                          html_dict: dict,
                                          hash_mapping: Dict[Safe_Str__Hash, str]
                                         ) -> Dict[Safe_Str__Hash, str]:
        """
        🆕 Randomly replace text with hash values.

        This shows the actual hash for randomly selected text nodes,
        useful for debugging and understanding the hash system.

        Strategy:
        1. Randomly select X% of hashes (based on randomness_percentage)
        2. For selected hashes: replace text with the hash value itself
        3. For unselected hashes: keep original text

        Example:
            Input:  { "abc123": "Hello", "def456": "World" }
            Output: { "abc123": "abc123", "def456": "World" }
                    (Shows hash instead of text)

        Args:
            html_dict: HTML structure (not modified, just passed through)
            hash_mapping: Dict of { hash: "original text" }

        Returns:
            Modified hash mapping with hash values replacing selected text
        """
        if not hash_mapping:
            return hash_mapping

        # for key,value, in hash_mapping.items():
        #     print(f'{key:20} : {value}')


        # Get all hashes and randomly select which to show as hashes
        selected_hashes = self._randomly_select_hashes(hash_mapping)

        # Create new mapping with hash values for selected items
        modified_mapping = {}
        for hash_key, original_text in hash_mapping.items():
            if hash_key in selected_hashes:
                # Replace text with the hash value itself
                modified_mapping[hash_key] = str(hash_key)
            else:
                # Keep original text
                modified_mapping[hash_key] = original_text

        return modified_mapping

    def _randomly_select_hashes(self,
                               hash_mapping: Dict[Safe_Str__Hash, str]
                              ) -> list:
        """
        Helper to randomly select hashes for transformation.

        Args:
            hash_mapping: Full hash mapping

        Returns:
            List of randomly selected hash keys
        """
        all_hashes = list(hash_mapping.keys())

        if not all_hashes:
            return []

        # Calculate how many to select
        num_to_select = max(1, int(len(all_hashes) * self.randomness_percentage))

        # Randomly select
        return random.sample(all_hashes, min(num_to_select, len(all_hashes)))

    def _mask_text(self, text: str) -> str:
        """
        Replace text with 'x' characters while preserving structure.

        Examples:
            "Hello"        → "xxxxx"
            "Hello World"  → "xxxxx xxxxx"
            "Hello, World!" → "xxxxx, xxxxx!"
        """
        if not text:
            return text

        result = []
        for char in text:
            if char.isalnum():
                result.append('x')
            elif char.isspace():
                result.append(' ')  # Keep whitespace for word boundaries
            else:
                result.append(char)  # Keep punctuation for readability

        return ''.join(result)

    def transform_abcde_by_size_via_hashes(self,html_dict: dict,
                                                hash_mapping: Dict[Safe_Str__Hash, str]
                                              ) -> Dict[Safe_Str__Hash, str]:
            if not hash_mapping:
                return hash_mapping

            # Create grouping service
            grouping_service = Text__Grouping__Service(num_groups=5)

            # Group hashes by text length
            groups = grouping_service.group_by_length(hash_mapping)

            # Create modified mapping with group letters
            modified_mapping = {}

            # for group_index, hashes in groups.items():
            #     print(group_index, len(hashes))

            for group_index, hashes in groups.items():
                # Get letter for this group (0='a', 1='b', etc.)
                group_letter = grouping_service.get_group_letter(group_index)

                # Replace all texts in this group with the letter
                for hash_key in hashes:
                    #modified_mapping[hash_key] = group_letter
                    original_text = hash_mapping[hash_key]
                    modified_mapping[hash_key] = self._replace_with_letter(original_text, group_letter)

            return modified_mapping

    def _replace_with_letter(self, text: str, letter: str) -> str:
        """
        Replace text with repeated letter while preserving structure.

        Same pattern as _mask_text but uses the group letter instead of 'x'.

        Examples:
            "Hello", 'a'        → "aaaaa"
            "Hello World", 'b'  → "bbbbb bbbbb"
            "Hello, World!", 'c' → "ccccc, ccccc!"

        Args:
            text: Original text to replace
            letter: Group letter to use (a, b, c, d, e, etc.)

        Returns:
            Text replaced with letter, preserving structure
        """
        if not text:
            return text

        result = []
        for char in text:
            if char.isalnum():
                result.append(letter)
            elif char.isspace():
                result.append(' ')  # Keep whitespace for word boundaries
            else:
                result.append(char)  # Keep punctuation for readability

        return ''.join(result)