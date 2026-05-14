"""
Sparse Table — O(1) Range Minimum / Maximum Queries
=====================================================
A static data structure for answering range queries on an immutable array
in **O(1)** after an **O(n log n)** preprocessing step.

Core idea
---------
For each position i and each power-of-two length 2^j, precompute:

    table[j][i] = min (or max) of arr[i : i + 2^j]

Because min/max are **idempotent** (overlapping two ranges gives the same
result as the union), a query [l, r] of length len = r - l + 1 can be
answered by two possibly-overlapping windows of length 2^k where k = floor(log2(len)):

    query_min(l, r) = min( table[k][l], table[k][r - 2^k + 1] )

The two windows overlap but that's fine — min/max of overlapping ranges still
gives the correct answer for the full range.

Why O(1) query?
---------------
The query requires only:
  1. One integer log2 lookup (done via bit_length trick in O(1)).
  2. Two table lookups.
  3. One min/max call.
All three steps are O(1), giving an overall O(1) query.

Note: Sparse Table only supports **static** arrays (no updates). For dynamic
arrays, use a Segment Tree instead.

Time Complexity
---------------
| Operation      | Time        |
|----------------|-------------|
| build(arr)     | O(n log n)  |
| query_min(l,r) | O(1)        |
| query_max(l,r) | O(1)        |

Space Complexity
----------------
O(n log n) — the table stores O(n log n) values.

Supported query types (idempotent only)
---------------------------------------
- Range Minimum Query (RMQ) — implemented here as query_min
- Range Maximum Query      — implemented here as query_max
- Range GCD               — also idempotent (not implemented here)
- Range sum is NOT idempotent and cannot use this technique.
"""

import math
from typing import List, Optional


class SparseTable:
    """
    Sparse Table for O(1) range minimum and range maximum queries.

    Parameters
    ----------
    arr : list  Input array of comparable elements (immutable after build).

    Usage
    -----
    >>> st = SparseTable([2, 4, 3, 1, 6, 7, 8, 9, 1, 7])
    >>> st.query_min(0, 4)   # min of [2,4,3,1,6]
    1
    >>> st.query_max(2, 7)   # max of [3,1,6,7,8,9]
    9
    """

    def __init__(self, arr: Optional[List] = None) -> None:
        self.n: int = 0
        self.log2: List[int] = []   # precomputed floor(log2(i)) for i in [0..n]
        self._min_table: List[List] = []
        self._max_table: List[List] = []
        self._arr: List = []

        if arr is not None:
            self.build(arr)

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def build(self, arr: List) -> None:
        """
        Precompute the sparse table for arr.

        After this call the table supports O(1) range queries.

        Time:  O(n log n)
        Space: O(n log n)

        Parameters
        ----------
        arr : list of comparable elements (integers, floats, etc.)
        """
        if not arr:
            raise ValueError("Cannot build SparseTable on an empty array")

        self._arr = list(arr)
        self.n = len(arr)

        # Number of levels: LOG = floor(log2(n)) + 1
        LOG = self.n.bit_length()  # = floor(log2(n)) + 1 for n >= 1

        # Precompute floor(log2(i)) for i = 0 … n.
        # log2[0] and log2[1] = 0; log2[i] = log2[i//2] + 1 for i >= 2.
        self.log2 = [0] * (self.n + 1)
        for i in range(2, self.n + 1):
            self.log2[i] = self.log2[i // 2] + 1

        # Initialize tables with LOG levels, each of length n
        self._min_table = [[None] * self.n for _ in range(LOG)]
        self._max_table = [[None] * self.n for _ in range(LOG)]

        # Level 0: windows of length 2^0 = 1 — trivially the element itself
        for i in range(self.n):
            self._min_table[0][i] = arr[i]
            self._max_table[0][i] = arr[i]

        # Fill levels 1 … LOG-1 using recurrence:
        #   table[j][i] = min( table[j-1][i], table[j-1][i + 2^(j-1)] )
        # The window at level j has length 2^j = two windows of length 2^(j-1).
        for j in range(1, LOG):
            half = 1 << (j - 1)  # 2^(j-1)
            for i in range(self.n - (1 << j) + 1):
                self._min_table[j][i] = min(self._min_table[j - 1][i],
                                            self._min_table[j - 1][i + half])
                self._max_table[j][i] = max(self._max_table[j - 1][i],
                                            self._max_table[j - 1][i + half])

    # ------------------------------------------------------------------
    # Query helpers
    # ------------------------------------------------------------------

    def _validate_range(self, l: int, r: int) -> None:
        if self.n == 0:
            raise RuntimeError("SparseTable has not been built yet. Call build(arr) first.")
        if not (0 <= l <= r < self.n):
            raise IndexError(f"Invalid range [{l}, {r}] for array of size {self.n}")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def query_min(self, l: int, r: int):
        """
        Return the minimum value in arr[l..r] (inclusive).

        Algorithm:
            k = floor(log2(r - l + 1))
            return min(table[k][l], table[k][r - 2^k + 1])

        The two windows [l, l+2^k-1] and [r-2^k+1, r] together cover [l, r].
        Overlap is harmless because min is idempotent.

        Time: O(1)
        """
        self._validate_range(l, r)
        length = r - l + 1
        k = self.log2[length]           # floor(log2(length))
        window = 1 << k                 # 2^k
        return min(self._min_table[k][l],
                   self._min_table[k][r - window + 1])

    def query_max(self, l: int, r: int):
        """
        Return the maximum value in arr[l..r] (inclusive).

        Uses the same two-overlapping-windows trick as query_min.

        Time: O(1)
        """
        self._validate_range(l, r)
        length = r - l + 1
        k = self.log2[length]
        window = 1 << k
        return max(self._max_table[k][l],
                   self._max_table[k][r - window + 1])

    def query_range(self, l: int, r: int):
        """
        Convenience method: return (min, max) for arr[l..r] in O(1).
        """
        return self.query_min(l, r), self.query_max(l, r)

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        if self.n == 0:
            return "SparseTable(empty)"
        LOG = len(self._min_table)
        lines = [f"SparseTable(n={self.n}, levels={LOG})"]
        lines.append(f"Array:      {self._arr}")
        lines.append("Min table (level j covers windows of length 2^j):")
        for j in range(LOG):
            valid = [str(self._min_table[j][i]) for i in range(self.n - (1 << j) + 1)]
            lines.append(f"  Level {j} (len={1<<j:4}): {valid}")
        return "\n".join(lines)

    def __repr__(self) -> str:
        return f"SparseTable(n={self.n})"


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import time, random

    print("=" * 60)
    print("SPARSE TABLE DEMO")
    print("=" * 60)

    arr = [2, 4, 3, 1, 6, 7, 8, 9, 1, 7]
    print(f"\nArray: {arr}")
    print(f"Index:  {list(range(len(arr)))}")

    st = SparseTable(arr)
    print("\n" + str(st))

    # --- Range queries ---
    queries = [
        (0, 9), (0, 4), (2, 7), (3, 5), (0, 0), (4, 4), (1, 8),
    ]
    print("\nRange queries (all O(1)):")
    print(f"{'Query':12} {'Min':>6} {'Max':>6}  Brute-force check")
    print("-" * 46)
    for l, r in queries:
        got_min = st.query_min(l, r)
        got_max = st.query_max(l, r)
        expected_min = min(arr[l:r+1])
        expected_max = max(arr[l:r+1])
        match = "OK" if got_min == expected_min and got_max == expected_max else "FAIL"
        print(f"[{l}, {r}]        {got_min:>6} {got_max:>6}  {match}")

    # --- Exhaustive correctness check ---
    print("\nExhaustive correctness check (all O(n^2) queries):")
    n = len(arr)
    all_pass = True
    for l in range(n):
        for r in range(l, n):
            if st.query_min(l, r) != min(arr[l:r+1]):
                all_pass = False
                print(f"  FAIL min [{l},{r}]")
            if st.query_max(l, r) != max(arr[l:r+1]):
                all_pass = False
                print(f"  FAIL max [{l},{r}]")
    print(f"  All {n*(n+1)//2} queries correct: {all_pass}")

    # --- O(1) query benchmark ---
    print("\n--- O(1) query vs naive O(n) benchmark ---")
    N = 100_000
    big_arr = [random.randint(0, 10**6) for _ in range(N)]

    t0 = time.perf_counter()
    st_big = SparseTable(big_arr)
    build_time = time.perf_counter() - t0
    print(f"Build time for n={N:,}: {build_time*1000:.2f} ms  (O(n log n))")

    Q = 10_000
    query_pairs = [(random.randint(0, N-2), 0) for _ in range(Q)]
    query_pairs = [(l, random.randint(l, N-1)) for l, _ in query_pairs]

    t0 = time.perf_counter()
    for l, r in query_pairs:
        st_big.query_min(l, r)
    sparse_time = time.perf_counter() - t0

    t0 = time.perf_counter()
    for l, r in query_pairs:
        min(big_arr[l:r+1])
    naive_time = time.perf_counter() - t0

    print(f"Sparse Table — {Q:,} queries: {sparse_time*1000:.2f} ms  ({sparse_time/Q*1e6:.2f} µs avg)")
    print(f"Naive scan   — {Q:,} queries: {naive_time*1000:.2f} ms  ({naive_time/Q*1e6:.2f} µs avg)")
    print(f"Speedup: {naive_time/sparse_time:.1f}x")

    print("\nDone.")
