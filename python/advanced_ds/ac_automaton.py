"""
Aho-Corasick Automaton (AC Automaton)

Time Complexity:
- Construction: O(m * k) where m = total length of all patterns, k = alphabet size
- Searching: O(n + z) where n = text length, z = number of matches
- Space Complexity: O(m * k)

Use Cases:
- Multi-pattern string matching (finding multiple patterns in text)
- Substring search
- Spam detection (multiple bad words)
- DNA sequence searching
- Dictionary lookup

Key Insight:
- Build trie of all patterns
- Compute failure function (like KMP) for each node
- Use failure links to skip mismatches efficiently
- Process text in single pass finding all pattern occurrences
"""

from typing import List, Tuple, Dict, Optional
from collections import deque, defaultdict


class AhoCorasickAutomaton:
    """Multi-pattern string matching using Aho-Corasick algorithm."""

    class Node:
        """Trie node with failure link."""

        def __init__(self):
            self.children = {}
            self.failure = None
            self.output = []  # Pattern IDs that end at this node

    def __init__(self):
        self.root = self.Node()
        self.patterns = []  # Store patterns for reference

    def add_pattern(self, pattern: str) -> None:
        """Add a pattern to the automaton."""
        node = self.root
        for char in pattern:
            if char not in node.children:
                node.children[char] = self.Node()
            node = node.children[char]

        # Store pattern ID at the end node
        pattern_id = len(self.patterns)
        self.patterns.append(pattern)
        node.output.append(pattern_id)

    def build(self) -> None:
        """Build failure function using BFS."""
        queue = deque()

        # Set failure link for root children to root
        self.root.failure = self.root
        for child in self.root.children.values():
            child.failure = self.root
            queue.append(child)

        # BFS to compute failure links
        while queue:
            node = queue.popleft()

            for char, child in node.children.items():
                # Find failure node that has this character
                failure_node = node.failure

                while failure_node != self.root and char not in failure_node.children:
                    failure_node = failure_node.failure

                if char in failure_node.children and failure_node.children[char] != child:
                    child.failure = failure_node.children[char]
                else:
                    child.failure = self.root

                # Add patterns from failure node's output
                child.output.extend(child.failure.output)
                queue.append(child)

    def search(self, text: str) -> List[Tuple[int, str]]:
        """
        Search for all patterns in text.

        Returns:
            List of (position, pattern) tuples where pattern is found
        """
        matches = []
        node = self.root

        for i, char in enumerate(text):
            # Follow failure links until we find a match or reach root
            while node != self.root and char not in node.children:
                node = node.failure

            if char in node.children:
                node = node.children[char]
            else:
                node = self.root

            # Report all patterns that match at this position
            for pattern_id in node.output:
                pattern = self.patterns[pattern_id]
                matches.append((i - len(pattern) + 1, pattern))

        return matches

    def search_with_ids(self, text: str) -> List[Tuple[int, int]]:
        """
        Search for all patterns in text.

        Returns:
            List of (position, pattern_id) tuples
        """
        matches = []
        node = self.root

        for i, char in enumerate(text):
            while node != self.root and char not in node.children:
                node = node.failure

            if char in node.children:
                node = node.children[char]
            else:
                node = self.root

            for pattern_id in node.output:
                pattern = self.patterns[pattern_id]
                matches.append((i - len(pattern) + 1, pattern_id))

        return matches


if __name__ == "__main__":
    # Example 1: Basic pattern matching
    print("=== Example 1: Basic Pattern Matching ===")
    automaton = AhoCorasickAutomaton()

    patterns = ["he", "she", "his", "hers"]
    for pattern in patterns:
        automaton.add_pattern(pattern)

    automaton.build()

    text = "ushers"
    matches = automaton.search(text)
    print(f"Text: '{text}'")
    print(f"Patterns: {patterns}")
    print(f"Matches: {matches}")

    # Example 2: More complex text
    print("\n=== Example 2: Complex Text ===")
    automaton2 = AhoCorasickAutomaton()

    patterns2 = ["cat", "car", "card", "care", "careful"]
    for pattern in patterns2:
        automaton2.add_pattern(pattern)

    automaton2.build()

    text2 = "a cat caring carefully with a card"
    matches2 = automaton2.search(text2)
    print(f"Text: '{text2}'")
    print(f"Patterns: {patterns2}")
    print(f"Matches: {matches2}")

    # Example 3: Overlapping patterns
    print("\n=== Example 3: Overlapping Patterns ===")
    automaton3 = AhoCorasickAutomaton()

    patterns3 = ["ab", "ba", "aaab", "abab", "baa"]
    for pattern in patterns3:
        automaton3.add_pattern(pattern)

    automaton3.build()

    text3 = "aabaab"
    matches3 = automaton3.search(text3)
    print(f"Text: '{text3}'")
    print(f"Patterns: {patterns3}")
    print(f"Matches (sorted by position): {sorted(matches3)}")
