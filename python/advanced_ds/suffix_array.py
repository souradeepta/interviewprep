"""
Suffix Array with LCP (Longest Common Prefix) Array

Time Complexity:
- Construction: O(n log n) with O(log n) space for sorting
- Pattern Search: O(m log n) where m = pattern length
- LCP Array: O(n) via Kasai's algorithm

Space Complexity: O(n)

Use Cases:
- Substring search (more space-efficient than suffix tree)
- Finding all occurrences of a pattern
- Finding longest repeated substring
- Computing longest common substring
- Approximate string matching

Key Insight:
- Sort all suffixes of the string
- Binary search to find pattern ranges
- LCP array helps in analysis: LCP[i] = longest common prefix of SA[i] and SA[i+1]
- Kasai's algorithm computes LCP in O(n) time
- More cache-friendly than suffix tree
"""

from typing import List, Tuple


class SuffixArray:
    """Suffix array with LCP array using Kasai's algorithm."""

    def __init__(self, text: str):
        """
        Build suffix array and LCP array.

        Args:
            text: Input string
        """
        self.text = text
        self.n = len(text)
        self.sa = []  # Suffix array
        self.lcp = []  # LCP array
        self.rank = []  # Rank array for LCP computation

        if self.n == 0:
            return

        self._build_suffix_array()
        self._build_lcp_array()

    def _build_suffix_array(self) -> None:
        """Build suffix array using simple O(n log² n) approach."""
        # Create pairs of (suffix, original_index)
        suffixes = []
        for i in range(self.n):
            suffixes.append((self.text[i:], i))

        # Sort suffixes
        suffixes.sort()

        # Extract sorted indices
        self.sa = [idx for _, idx in suffixes]

    def _build_lcp_array(self) -> None:
        """Build LCP array using Kasai's algorithm in O(n)."""
        self.rank = [0] * self.n
        for i, sa_idx in enumerate(self.sa):
            self.rank[sa_idx] = i

        self.lcp = [0] * (self.n - 1)
        h = 0

        for i in range(self.n):
            if self.rank[i] > 0:
                j = self.sa[self.rank[i] - 1]
                while i + h < self.n and j + h < self.n and \
                      self.text[i + h] == self.text[j + h]:
                    h += 1

                self.lcp[self.rank[i] - 1] = h

                if h > 0:
                    h -= 1

    def find_pattern(self, pattern: str) -> List[int]:
        """
        Find all occurrences of pattern in text.

        Returns:
            List of starting positions
        """
        if pattern == "" or self.n == 0:
            return []

        # Binary search for pattern in suffix array
        left, right = 0, self.n - 1
        matches = []

        # Find leftmost position where pattern could start
        while left <= right:
            mid = (left + right) // 2
            suffix = self.text[self.sa[mid]:]

            if suffix.startswith(pattern):
                matches.append(self.sa[mid])
                right = mid - 1
            elif pattern < suffix[:len(pattern)]:
                right = mid - 1
            else:
                left = mid + 1

        # Find all matching suffixes
        if matches:
            left = self.sa.index(matches[0])
            for i in range(left + 1, self.n):
                suffix = self.text[self.sa[i]:]
                if suffix.startswith(pattern):
                    matches.append(self.sa[i])
                else:
                    break

        return sorted(matches)

    def longest_repeated_substring(self) -> str:
        """Find longest substring that appears at least twice."""
        if self.n == 0:
            return ""

        max_lcp = 0
        max_idx = -1

        for i, lcp_val in enumerate(self.lcp):
            if lcp_val > max_lcp:
                max_lcp = lcp_val
                max_idx = i

        if max_idx == -1:
            return ""

        start = self.sa[max_idx]
        return self.text[start:start + max_lcp]

    def get_suffix_array(self) -> List[int]:
        """Get the suffix array."""
        return self.sa.copy()

    def get_lcp_array(self) -> List[int]:
        """Get the LCP array."""
        return self.lcp.copy()


if __name__ == "__main__":
    # Example 1: Basic suffix array
    print("=== Example 1: Suffix Array ===")
    text = "banana"
    sa = SuffixArray(text)

    print(f"Text: '{text}'")
    print(f"Suffix Array: {sa.get_suffix_array()}")
    print(f"LCP Array: {sa.get_lcp_array()}")

    print("\nSuffixes in sorted order:")
    for idx in sa.get_suffix_array():
        print(f"  {idx:2d}: {text[idx:]}")

    # Example 2: Pattern finding
    print("\n=== Example 2: Pattern Finding ===")
    text2 = "mississippi"
    sa2 = SuffixArray(text2)

    patterns = ["is", "si", "pp", "mis"]
    print(f"Text: '{text2}'")
    for pattern in patterns:
        positions = sa2.find_pattern(pattern)
        print(f"Pattern '{pattern}': positions {positions}")

    # Example 3: Longest repeated substring
    print("\n=== Example 3: Longest Repeated Substring ===")
    text3 = "abracadabra"
    sa3 = SuffixArray(text3)

    lrs = sa3.longest_repeated_substring()
    print(f"Text: '{text3}'")
    print(f"Longest repeated substring: '{lrs}'")

    text4 = "aabaabaab"
    sa4 = SuffixArray(text4)
    lrs2 = sa4.longest_repeated_substring()
    print(f"\nText: '{text4}'")
    print(f"Longest repeated substring: '{lrs2}'")
