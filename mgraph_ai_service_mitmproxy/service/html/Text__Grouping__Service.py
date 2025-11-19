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
        Group hashes by text length into N equal-sized buckets (by item count, not length range).

        Strategy:
        1. Sort all hashes by their text length
        2. Divide into N groups with equal number of items per group
        3. This ensures balanced groups for batch processing

        Example with 5 groups and 100 items:
        - Group 0: 20 shortest texts
        - Group 1: 20 next shortest texts
        - Group 2: 20 medium texts
        - Group 3: 20 next longest texts
        - Group 4: 20 longest texts

        Args:
            hash_mapping: Dict of { hash: "text content" }

        Returns:
            Dict of { group_index: [list of hashes in that group] }

        Example:
            Input:  100 hashes with various lengths
            Output: { 0: [20 hashes], 1: [20 hashes], 2: [20 hashes], 3: [20 hashes], 4: [20 hashes] }
        """
        if not hash_mapping:
            return {}

        # Step 1: Sort all hashes by text length
        hashes_by_length = sorted(
            hash_mapping.items(),
            key=lambda x: len(x[1])  # Sort by text length
        )

        total_items = len(hashes_by_length)

        # Handle edge case: fewer items than groups
        if total_items < self.num_groups:
            # Put each item in its own group
            return {i: [hashes_by_length[i][0]] for i in range(total_items)}

        # Step 2: Calculate items per group (as evenly as possible)
        base_size = total_items // self.num_groups
        remainder = total_items % self.num_groups

        # Step 3: Distribute hashes into groups
        groups = {i: [] for i in range(self.num_groups)}
        current_index = 0

        for group_idx in range(self.num_groups):
            # First 'remainder' groups get one extra item
            group_size = base_size + (1 if group_idx < remainder else 0)

            # Add hashes to this group
            for _ in range(group_size):
                if current_index < total_items:
                    hash_key, _ = hashes_by_length[current_index]
                    groups[group_idx].append(hash_key)
                    current_index += 1

        # Remove empty groups (shouldn't happen, but safety check)
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