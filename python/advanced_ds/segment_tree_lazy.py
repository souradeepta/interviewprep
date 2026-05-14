"""
Segment Tree with Lazy Propagation

Time Complexity:
- Range Update: O(log n)
- Range Query: O(log n)
- Point Update: O(log n)
- Point Query: O(log n)

Space Complexity: O(n)

Use Cases:
- Range updates and range queries on arrays
- Range add operations with range sum queries
- Lazy evaluation to avoid redundant updates

Key Insight:
- Store lazy values at each node representing pending updates
- Push lazy updates down when needed during query/update
- Combine updates efficiently before propagating
"""

from typing import Callable, Optional


class LazySegmentTree:
    """Segment tree with lazy propagation for range updates and queries."""

    def __init__(self, arr):
        """
        Initialize lazy segment tree.

        Args:
            arr: Initial array of values
        """
        self.n = len(arr)
        self.tree = [0] * (4 * self.n)
        self.lazy = [0] * (4 * self.n)

        if self.n > 0:
            self._build(arr, 0, 0, self.n - 1)

    def _build(self, arr, node, start, end):
        """Build segment tree."""
        if start == end:
            self.tree[node] = arr[start]
        else:
            mid = (start + end) // 2
            self._build(arr, 2 * node + 1, start, mid)
            self._build(arr, 2 * node + 2, mid + 1, end)
            self.tree[node] = self.tree[2 * node + 1] + self.tree[2 * node + 2]

    def _push(self, node, start, end):
        """Push lazy values down to children."""
        if self.lazy[node] != 0:
            # Apply lazy value to current node
            self.tree[node] += self.lazy[node] * (end - start + 1)

            # Push to children if not leaf
            if start != end:
                self.lazy[2 * node + 1] += self.lazy[node]
                self.lazy[2 * node + 2] += self.lazy[node]

            self.lazy[node] = 0

    def _update_range(self, node, start, end, l, r, val):
        """Update range [l, r] by adding val."""
        self._push(node, start, end)

        if start > r or end < l:
            return

        if l <= start and end <= r:
            self.lazy[node] += val
            self._push(node, start, end)
            return

        mid = (start + end) // 2
        self._update_range(2 * node + 1, start, mid, l, r, val)
        self._update_range(2 * node + 2, mid + 1, end, l, r, val)

        self._push(2 * node + 1, start, mid)
        self._push(2 * node + 2, mid + 1, end)
        self.tree[node] = self.tree[2 * node + 1] + self.tree[2 * node + 2]

    def _query_range(self, node, start, end, l, r):
        """Query sum in range [l, r]."""
        if start > r or end < l:
            return 0

        self._push(node, start, end)

        if l <= start and end <= r:
            return self.tree[node]

        mid = (start + end) // 2
        left_sum = self._query_range(2 * node + 1, start, mid, l, r)
        right_sum = self._query_range(2 * node + 2, mid + 1, end, l, r)
        return left_sum + right_sum

    def update(self, l, r, val):
        """Add val to all elements in range [l, r]."""
        if self.n > 0:
            self._update_range(0, 0, self.n - 1, l, r, val)

    def query(self, l, r):
        """Query sum in range [l, r]."""
        if self.n == 0:
            return 0
        return self._query_range(0, 0, self.n - 1, l, r)

    def point_update(self, idx, val):
        """Update single point at index idx to val."""
        self.update(idx, idx, val - self.query(idx, idx))

    def point_query(self, idx):
        """Query value at index idx."""
        return self.query(idx, idx)


class SegmentTreeWithMaxMin:
    """Segment tree with lazy propagation for range min/max assignment."""

    def __init__(self, arr):
        """Initialize segment tree."""
        self.n = len(arr)
        self.tree_min = [float('inf')] * (4 * self.n)
        self.tree_max = [float('-inf')] * (4 * self.n)
        self.lazy = [None] * (4 * self.n)

        if self.n > 0:
            self._build(arr, 0, 0, self.n - 1)

    def _build(self, arr, node, start, end):
        """Build segment tree."""
        if start == end:
            self.tree_min[node] = arr[start]
            self.tree_max[node] = arr[start]
        else:
            mid = (start + end) // 2
            self._build(arr, 2 * node + 1, start, mid)
            self._build(arr, 2 * node + 2, mid + 1, end)
            self.tree_min[node] = min(self.tree_min[2 * node + 1], self.tree_min[2 * node + 2])
            self.tree_max[node] = max(self.tree_max[2 * node + 1], self.tree_max[2 * node + 2])

    def _push(self, node, start, end):
        """Push lazy value down."""
        if self.lazy[node] is not None:
            val = self.lazy[node]
            self.tree_min[node] = val
            self.tree_max[node] = val

            if start != end:
                self.lazy[2 * node + 1] = val
                self.lazy[2 * node + 2] = val

            self.lazy[node] = None

    def _update_range(self, node, start, end, l, r, val):
        """Assign val to range [l, r]."""
        self._push(node, start, end)

        if start > r or end < l:
            return

        if l <= start and end <= r:
            self.lazy[node] = val
            self._push(node, start, end)
            return

        mid = (start + end) // 2
        self._update_range(2 * node + 1, start, mid, l, r, val)
        self._update_range(2 * node + 2, mid + 1, end, l, r, val)

        self._push(2 * node + 1, start, mid)
        self._push(2 * node + 2, mid + 1, end)
        self.tree_min[node] = min(self.tree_min[2 * node + 1], self.tree_min[2 * node + 2])
        self.tree_max[node] = max(self.tree_max[2 * node + 1], self.tree_max[2 * node + 2])

    def _query_range(self, node, start, end, l, r, query_type):
        """Query min or max in range [l, r]."""
        if start > r or end < l:
            return float('inf') if query_type == 'min' else float('-inf')

        self._push(node, start, end)

        if l <= start and end <= r:
            return self.tree_min[node] if query_type == 'min' else self.tree_max[node]

        mid = (start + end) // 2
        left_res = self._query_range(2 * node + 1, start, mid, l, r, query_type)
        right_res = self._query_range(2 * node + 2, mid + 1, end, l, r, query_type)

        if query_type == 'min':
            return min(left_res, right_res)
        else:
            return max(left_res, right_res)

    def update(self, l, r, val):
        """Assign val to all elements in range [l, r]."""
        if self.n > 0:
            self._update_range(0, 0, self.n - 1, l, r, val)

    def query_min(self, l, r):
        """Query min in range [l, r]."""
        if self.n == 0:
            return float('inf')
        return self._query_range(0, 0, self.n - 1, l, r, 'min')

    def query_max(self, l, r):
        """Query max in range [l, r]."""
        if self.n == 0:
            return float('-inf')
        return self._query_range(0, 0, self.n - 1, l, r, 'max')


if __name__ == "__main__":
    # Test range sum with range add
    print("=== Range Sum Query with Range Add ===")
    arr = [1, 2, 3, 4, 5]
    seg_tree = LazySegmentTree(arr)

    print(f"Initial array: {arr}")
    print(f"Query [0, 4]: {seg_tree.query(0, 4)}")  # 15

    seg_tree.update(1, 3, 5)  # Add 5 to indices 1-3
    print(f"After add 5 to [1, 3]:")
    print(f"Query [0, 4]: {seg_tree.query(0, 4)}")  # 30
    print(f"Query [1, 3]: {seg_tree.query(1, 3)}")  # 24

    seg_tree.update(0, 2, -2)  # Add -2 to indices 0-2
    print(f"After add -2 to [0, 2]:")
    print(f"Query [0, 4]: {seg_tree.query(0, 4)}")  # 26
    print(f"Query [0, 2]: {seg_tree.query(0, 2)}")  # 8

    print("\n=== Range Min/Max with Range Assignment ===")
    arr2 = [3, 1, 4, 1, 5, 9, 2]
    seg_tree2 = SegmentTreeWithMaxMin(arr2)

    print(f"Initial array: {arr2}")
    print(f"Query min [0, 6]: {seg_tree2.query_min(0, 6)}")  # 1
    print(f"Query max [0, 6]: {seg_tree2.query_max(0, 6)}")  # 9

    seg_tree2.update(2, 4, 10)  # Assign 10 to indices 2-4
    print(f"After assign 10 to [2, 4]:")
    print(f"Query min [0, 6]: {seg_tree2.query_min(0, 6)}")  # 1
    print(f"Query max [2, 5]: {seg_tree2.query_max(2, 5)}")  # 10
