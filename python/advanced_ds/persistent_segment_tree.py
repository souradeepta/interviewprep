"""
Persistent Segment Tree (Structural Sharing)

Time Complexity:
- Update: O(log n) per version
- Query: O(log n) per query
- Space Complexity: O((n + m) * log n) where m = number of updates

Use Cases:
- Query array state at any previous version
- Historical queries on time-versioned data
- Undo/redo functionality
- Range queries with version history
- Counting distinct elements in range (via persistent data structures)

Key Insight:
- Use structural sharing to avoid duplicating entire trees per update
- Only create new nodes along the path modified during update
- Reuse unmodified subtrees from previous versions
- Allows O(log n) access to any previous version
"""

from typing import List, Optional, Tuple


class PersistentSegmentTree:
    """Persistent segment tree using structural sharing."""

    class Node:
        """Segment tree node with optional children."""

        def __init__(self, value: int = 0):
            self.value = value
            self.left = None
            self.right = None

        def copy(self):
            """Create a shallow copy of this node."""
            new_node = PersistentSegmentTree.Node(self.value)
            new_node.left = self.left
            new_node.right = self.right
            return new_node

    def __init__(self, arr: List[int]):
        """Initialize persistent segment tree."""
        self.n = len(arr)
        self.versions = []  # Store root of each version

        if self.n > 0:
            root = self._build(arr, 0, self.n - 1)
            self.versions.append(root)

    def _build(self, arr: List[int], start: int, end: int) -> Optional['PersistentSegmentTree.Node']:
        """Build initial tree."""
        if start == end:
            return self.Node(arr[start])

        mid = (start + end) // 2
        node = self.Node()
        node.left = self._build(arr, start, mid)
        node.right = self._build(arr, mid + 1, end)
        node.value = node.left.value + node.right.value
        return node

    def _update(self, node: Optional['PersistentSegmentTree.Node'], start: int, end: int,
                idx: int, val: int) -> Optional['PersistentSegmentTree.Node']:
        """Update with structural sharing."""
        if node is None:
            return None

        if start == end:
            # Create new leaf node
            return self.Node(val)

        # Copy current node
        new_node = node.copy()
        mid = (start + end) // 2

        if idx <= mid:
            # Update left subtree
            new_node.left = self._update(node.left, start, mid, idx, val)
        else:
            # Update right subtree
            new_node.right = self._update(node.right, mid + 1, end, idx, val)

        # Recompute value
        left_val = new_node.left.value if new_node.left else 0
        right_val = new_node.right.value if new_node.right else 0
        new_node.value = left_val + right_val

        return new_node

    def update(self, idx: int, val: int) -> int:
        """
        Create new version with update at index idx to val.

        Returns:
            Version number (0-indexed)
        """
        if not self.versions:
            return -1

        new_root = self._update(self.versions[-1], 0, self.n - 1, idx, val)
        self.versions.append(new_root)
        return len(self.versions) - 1

    def _query(self, node: Optional['PersistentSegmentTree.Node'], start: int, end: int,
               l: int, r: int) -> int:
        """Query sum in range [l, r]."""
        if node is None or start > r or end < l:
            return 0

        if l <= start and end <= r:
            return node.value

        mid = (start + end) // 2
        left_sum = self._query(node.left, start, mid, l, r)
        right_sum = self._query(node.right, mid + 1, end, l, r)
        return left_sum + right_sum

    def query(self, version: int, l: int, r: int) -> int:
        """
        Query sum in range [l, r] for a specific version.

        Args:
            version: Version number
            l: Left index (inclusive)
            r: Right index (inclusive)

        Returns:
            Sum of elements in range for that version
        """
        if version < 0 or version >= len(self.versions):
            return 0

        return self._query(self.versions[version], 0, self.n - 1, l, r)

    def point_query(self, version: int, idx: int) -> int:
        """Query value at index idx for a specific version."""
        return self.query(version, idx, idx)

    def get_num_versions(self) -> int:
        """Get number of versions."""
        return len(self.versions)


class PersistentSegmentTreeWithMax:
    """Persistent segment tree for range max queries."""

    class Node:
        """Segment tree node."""

        def __init__(self, value: int = float('-inf')):
            self.value = value
            self.left = None
            self.right = None

        def copy(self):
            """Create a shallow copy."""
            new_node = PersistentSegmentTreeWithMax.Node(self.value)
            new_node.left = self.left
            new_node.right = self.right
            return new_node

    def __init__(self, arr: List[int]):
        """Initialize persistent segment tree."""
        self.n = len(arr)
        self.versions = []

        if self.n > 0:
            root = self._build(arr, 0, self.n - 1)
            self.versions.append(root)

    def _build(self, arr: List[int], start: int, end: int) -> Optional['PersistentSegmentTreeWithMax.Node']:
        """Build initial tree."""
        if start == end:
            return self.Node(arr[start])

        mid = (start + end) // 2
        node = self.Node()
        node.left = self._build(arr, start, mid)
        node.right = self._build(arr, mid + 1, end)
        node.value = max(node.left.value, node.right.value)
        return node

    def _update(self, node: Optional['PersistentSegmentTreeWithMax.Node'], start: int, end: int,
                idx: int, val: int) -> Optional['PersistentSegmentTreeWithMax.Node']:
        """Update with structural sharing."""
        if node is None:
            return None

        if start == end:
            return self.Node(val)

        new_node = node.copy()
        mid = (start + end) // 2

        if idx <= mid:
            new_node.left = self._update(node.left, start, mid, idx, val)
        else:
            new_node.right = self._update(node.right, mid + 1, end, idx, val)

        left_val = new_node.left.value if new_node.left else float('-inf')
        right_val = new_node.right.value if new_node.right else float('-inf')
        new_node.value = max(left_val, right_val)

        return new_node

    def update(self, idx: int, val: int) -> int:
        """Create new version with update. Returns version number."""
        if not self.versions:
            return -1

        new_root = self._update(self.versions[-1], 0, self.n - 1, idx, val)
        self.versions.append(new_root)
        return len(self.versions) - 1

    def _query_max(self, node: Optional['PersistentSegmentTreeWithMax.Node'], start: int, end: int,
                   l: int, r: int) -> int:
        """Query max in range."""
        if node is None or start > r or end < l:
            return float('-inf')

        if l <= start and end <= r:
            return node.value

        mid = (start + end) // 2
        left_max = self._query_max(node.left, start, mid, l, r)
        right_max = self._query_max(node.right, mid + 1, end, l, r)
        return max(left_max, right_max)

    def query_max(self, version: int, l: int, r: int) -> int:
        """Query max in range [l, r] for specific version."""
        if version < 0 or version >= len(self.versions):
            return float('-inf')

        return self._query_max(self.versions[version], 0, self.n - 1, l, r)

    def get_num_versions(self) -> int:
        """Get number of versions."""
        return len(self.versions)


if __name__ == "__main__":
    # Example 1: Range sum with version history
    print("=== Range Sum with Version History ===")
    arr = [1, 2, 3, 4, 5]
    pst = PersistentSegmentTree(arr)

    print(f"Initial array: {arr}")
    print(f"Version 0, Query [0, 4]: {pst.query(0, 0, 4)}")  # 15

    v1 = pst.update(2, 10)  # Change arr[2] from 3 to 10
    print(f"\nAfter update(2, 10):")
    print(f"Version 0, Query [0, 4]: {pst.query(0, 0, 4)}")  # 15 (unchanged)
    print(f"Version {v1}, Query [0, 4]: {pst.query(v1, 0, 4)}")  # 22

    v2 = pst.update(0, 100)  # Change arr[0] from 1 to 100
    print(f"\nAfter update(0, 100):")
    print(f"Version 0, Query [0, 4]: {pst.query(0, 0, 4)}")  # 15 (unchanged)
    print(f"Version {v1}, Query [0, 4]: {pst.query(v1, 0, 4)}")  # 22 (unchanged)
    print(f"Version {v2}, Query [0, 4]: {pst.query(v2, 0, 4)}")  # 122

    # Example 2: Range max with version history
    print("\n=== Range Max with Version History ===")
    arr2 = [3, 1, 4, 1, 5, 9, 2, 6]
    pst2 = PersistentSegmentTreeWithMax(arr2)

    print(f"Initial array: {arr2}")
    print(f"Version 0, Query max [0, 7]: {pst2.query_max(0, 0, 7)}")  # 9

    v3 = pst2.update(1, 100)
    print(f"\nAfter update(1, 100):")
    print(f"Version 0, Query max [0, 7]: {pst2.query_max(0, 0, 7)}")  # 9
    print(f"Version {v3}, Query max [0, 7]: {pst2.query_max(v3, 0, 7)}")  # 100
    print(f"Version {v3}, Query max [0, 3]: {pst2.query_max(v3, 0, 3)}")  # 100
