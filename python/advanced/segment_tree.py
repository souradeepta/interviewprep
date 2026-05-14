"""
Segment Tree
=============
A full binary tree that answers range queries and point updates in O(log n).
This implementation supports range-sum queries; comments show how to adapt
it for range-min and range-max.

Internal representation: 1-indexed array of size 4*n.
    - Node at index i has children at 2*i (left) and 2*i+1 (right).
    - Node 1 covers the full array [0, n-1].

Complexities:
    - build:         O(n)
    - query(l, r):   O(log n)
    - update(i, v):  O(log n)
    - Space:         O(n)

Adapting for other queries:
    - Range min: replace `a + b` in _merge with `min(a, b)`, identity → ∞
    - Range max: replace with `max(a, b)`, identity → -∞
    - Range GCD: replace with `math.gcd(a, b)`, identity → 0
"""

from __future__ import annotations
from typing import List, Callable, Optional
import math


class SegmentTree:
    """
    Segment Tree backed by a flat array.

    Parameters
    ----------
    data : list of int/float
        The source array to build from.
    func : callable, optional
        Merge function for two children. Default is sum.
        Pass `min` or `max` to build a range-min or range-max tree.
    identity : int/float, optional
        Identity element for *func* (0 for sum, math.inf for min, etc.).
    """

    def __init__(
        self,
        data: List[int],
        func: Callable[[int, int], int] = lambda a, b: a + b,
        identity: int = 0,
    ) -> None:
        self._n = len(data)
        self._func = func
        self._identity = identity
        self._tree: List[int] = [identity] * (4 * self._n)
        if self._n:
            self._build(data, 1, 0, self._n - 1)

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def _build(self, data: List[int], node: int, start: int, end: int) -> None:
        """
        Recursively build the segment tree.

        Time:  O(n)
        """
        if start == end:
            self._tree[node] = data[start]
            return
        mid = (start + end) // 2
        self._build(data, 2 * node, start, mid)
        self._build(data, 2 * node + 1, mid + 1, end)
        self._tree[node] = self._func(self._tree[2 * node], self._tree[2 * node + 1])

    # ------------------------------------------------------------------
    # Point update
    # ------------------------------------------------------------------

    def update(self, i: int, val: int) -> None:
        """
        Set arr[i] = *val* and propagate the change up the tree.

        Time:  O(log n)
        """
        if not (0 <= i < self._n):
            raise IndexError(f"Index {i} out of range [0, {self._n - 1}]")
        self._update(1, 0, self._n - 1, i, val)

    def _update(
        self, node: int, start: int, end: int, i: int, val: int
    ) -> None:
        if start == end:
            self._tree[node] = val
            return
        mid = (start + end) // 2
        if i <= mid:
            self._update(2 * node, start, mid, i, val)
        else:
            self._update(2 * node + 1, mid + 1, end, i, val)
        self._tree[node] = self._func(self._tree[2 * node], self._tree[2 * node + 1])

    # ------------------------------------------------------------------
    # Range query
    # ------------------------------------------------------------------

    def query(self, l: int, r: int) -> int:
        """
        Apply *func* over the range arr[l..r] (inclusive, 0-indexed).

        Time:  O(log n)

        Examples:
            sum query: tree.query(2, 5)  → sum of arr[2..5]
            min query: use func=min when building
        """
        if not (0 <= l <= r < self._n):
            raise IndexError(f"Range [{l}, {r}] out of bounds [0, {self._n - 1}]")
        return self._query(1, 0, self._n - 1, l, r)

    def _query(
        self, node: int, start: int, end: int, l: int, r: int
    ) -> int:
        if r < start or end < l:
            # Range completely outside — return identity.
            return self._identity
        if l <= start and end <= r:
            # Range completely inside — return node value.
            return self._tree[node]
        # Partial overlap — recurse on both children.
        mid = (start + end) // 2
        left_val = self._query(2 * node, start, mid, l, r)
        right_val = self._query(2 * node + 1, mid + 1, end, l, r)
        return self._func(left_val, right_val)

    # ------------------------------------------------------------------
    # String representation
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        """Print non-identity internal nodes for inspection."""
        n = self._n
        lines = [f"SegmentTree(n={n}, func={self._func.__name__ if hasattr(self._func, '__name__') else 'custom'})"]
        # Print meaningful portion of the tree array (indices 1..4n).
        meaningful = [
            (i, v) for i, v in enumerate(self._tree[1 : 4 * n + 1], start=1)
            if v != self._identity
        ]
        for idx, val in meaningful:
            lines.append(f"  tree[{idx}] = {val}")
        return "\n".join(lines)


# ----------------------------------------------------------------------
# Adapters for convenience
# ----------------------------------------------------------------------

class RangeMinTree(SegmentTree):
    """Segment tree for range-minimum queries."""

    def __init__(self, data: List[int]) -> None:
        super().__init__(data, func=min, identity=math.inf)


class RangeMaxTree(SegmentTree):
    """Segment tree for range-maximum queries."""

    def __init__(self, data: List[int]) -> None:
        super().__init__(data, func=max, identity=-math.inf)


# ----------------------------------------------------------------------
# Demo
# ----------------------------------------------------------------------

if __name__ == "__main__":
    arr = [1, 3, 5, 7, 9, 11]
    print("=== Segment Tree (Sum) ===")
    print("Array:", arr)

    st = SegmentTree(arr)
    print("Sum [0,5]:", st.query(0, 5))   # 36
    print("Sum [1,3]:", st.query(1, 3))   # 15
    print("Sum [2,4]:", st.query(2, 4))   # 21

    st.update(3, 2)  # arr[3] = 2 (was 7)
    print("\nAfter update(3, 2):")
    print("Sum [1,3]:", st.query(1, 3))   # 10

    print()
    print("=== Segment Tree (Min) ===")
    rmin = RangeMinTree(arr)
    print("Min [0,5]:", rmin.query(0, 5))  # 1
    print("Min [2,5]:", rmin.query(2, 5))  # 5

    print()
    print("=== Segment Tree (Max) ===")
    rmax = RangeMaxTree(arr)
    print("Max [0,5]:", rmax.query(0, 5))  # 11
    print("Max [1,4]:", rmax.query(1, 4))  # 9
