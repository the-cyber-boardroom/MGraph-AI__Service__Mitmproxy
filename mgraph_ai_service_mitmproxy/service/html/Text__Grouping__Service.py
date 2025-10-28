from typing import Dict, List
from osbot_utils.type_safe.Type_Safe import Type_Safe
from osbot_utils.type_safe.primitives.domains.cryptography.safe_str.Safe_Str__Hash import Safe_Str__Hash


class Text__Grouping__Service(Type_Safe):
    """
    Service for grouping text hashes by various criteria.

    This enables batch processing of similar text nodes, dramatically reducing
    the number of LLM calls needed for classification/transformation.

    Example: Instead of 100 individual decisions, group into 5 buckets and make 5 decisions.

    Current grouping strategies:
    - by_length: Group texts by length ranges (0-10, 11-50, 51-100, etc.)
    """

    num_groups: int = 5  # Default: 5 groups

    def group_by_length(self,
                       hash_mapping: Dict[Safe_Str__Hash, str]
                      ) -> Dict[int, List[Safe_Str__Hash]]:
        """
        Group hashes by text length into N equal-sized buckets.

        Strategy:
        1. Get all text lengths
        2. Calculate length ranges (percentiles)
        3. Assign each hash to a bucket (0, 1, 2, 3, 4)

        Example with 5 groups:
        - Group 0: Very short (0-10 chars) - whitespace, connectors
        - Group 1: Short (11-30 chars) - menu items, short labels
        - Group 2: Medium (31-80 chars) - titles, short sentences
        - Group 3: Long (81-200 chars) - paragraphs, descriptions
        - Group 4: Very long (200+ chars) - full content blocks

        Args:
            hash_mapping: Dict of { hash: "text content" }

        Returns:
            Dict of { group_index: [list of hashes in that group] }

        Example:
            Input:  { "abc": "Hi", "def": "Hello World", "ghi": "A long paragraph..." }
            Output: { 0: ["abc"], 1: ["def"], 3: ["ghi"] }
        """
        if not hash_mapping:
            return {}

        # Step 1: Get all lengths and sort them
        length_to_hashes = {}
        for hash_key, text in hash_mapping.items():
            length = len(text)
            if length not in length_to_hashes:
                length_to_hashes[length] = []
            length_to_hashes[length].append(hash_key)

        # Get sorted unique lengths
        sorted_lengths = sorted(length_to_hashes.keys())

        if not sorted_lengths:
            return {}

        # Step 2: Calculate length ranges using percentiles
        min_length = sorted_lengths[0]
        max_length = sorted_lengths[-1]

        # Handle edge case: all texts same length
        if min_length == max_length:
            return {0: list(hash_mapping.keys())}

        # Calculate bucket boundaries
        range_size = (max_length - min_length) / self.num_groups

        # Step 3: Assign hashes to groups
        groups = {i: [] for i in range(self.num_groups)}

        for length in sorted_lengths:
            # Calculate which group this length belongs to
            if length == max_length:
                group_index = self.num_groups - 1  # Last group
            else:
                group_index = min(
                    int((length - min_length) / range_size),
                    self.num_groups - 1
                )

            # Add all hashes of this length to the group
            groups[group_index].extend(length_to_hashes[length])

        # Remove empty groups
        return {k: v for k, v in groups.items() if v}

    def get_group_stats(self,
                       hash_mapping: Dict[Safe_Str__Hash, str],
                       groups: Dict[int, List[Safe_Str__Hash]]
                      ) -> Dict[int, dict]:
        """
        Get statistics about each group.

        Useful for understanding the grouping distribution and debugging.

        Returns:
            Dict of { group_index: { "count": N, "min_length": X, "max_length": Y, "avg_length": Z } }
        """
        stats = {}

        for group_idx, hashes in groups.items():
            lengths = [len(hash_mapping[h]) for h in hashes]

            stats[group_idx] = {
                "count": len(hashes),
                "min_length": min(lengths) if lengths else 0,
                "max_length": max(lengths) if lengths else 0,
                "avg_length": sum(lengths) / len(lengths) if lengths else 0,
                "sample_texts": [hash_mapping[h][:50] + "..." if len(hash_mapping[h]) > 50 else hash_mapping[h]
                               for h in hashes[:3]]  # First 3 as samples
            }

        return stats

    def get_group_letter(self, group_index: int) -> str:
        """
        Convert group index to letter (0='a', 1='b', etc.)

        Args:
            group_index: Group number (0-based)

        Returns:
            Single letter (a-z, then aa, ab, etc. for >26 groups)
        """
        if group_index < 26:
            return chr(ord('a') + group_index)
        else:
            # For more than 26 groups: aa, ab, ac, etc.
            first = chr(ord('a') + (group_index // 26) - 1)
            second = chr(ord('a') + (group_index % 26))
            return first + second

    # ============================================================================
    # Future Grouping Strategies (Commented for now)
    # ============================================================================

    # def group_by_semantic_similarity(self,
    #                                 hash_mapping: Dict[Safe_Str__Hash, str],
    #                                 embeddings_model: str = "text-embedding-3-small"
    #                                ) -> Dict[int, List[Safe_Str__Hash]]:
    #     """
    #     Group texts by semantic similarity using embeddings + clustering.
    #
    #     Strategy:
    #     1. Get embeddings for all texts
    #     2. Use K-means clustering to group similar content
    #     3. Return clusters as groups
    #
    #     This would group:
    #     - All navigation items together
    #     - All headers together
    #     - All content paragraphs together
    #     """
    #     pass

    # def group_by_content_type(self,
    #                          hash_mapping: Dict[Safe_Str__Hash, str]
    #                         ) -> Dict[str, List[Safe_Str__Hash]]:
    #     """
    #     Group by content type using heuristics.
    #
    #     Categories:
    #     - whitespace: Only \n, spaces
    #     - navigation: Short, common nav words
    #     - headers: Title case, medium length
    #     - content: Longer paragraphs
    #     - metadata: Version strings, technical text
    #     """
    #     pass

    # def group_by_html_context(self,
    #                          html_dict: dict,
    #                          hash_mapping: Dict[Safe_Str__Hash, str]
    #                         ) -> Dict[str, List[Safe_Str__Hash]]:
    #     """
    #     Group by position in HTML structure.
    #
    #     Categories:
    #     - header: In <header>, <nav>, <h1-h6>
    #     - main: In <main>, <article>
    #     - sidebar: In <aside>
    #     - footer: In <footer>
    #     """
    #     pass