"""
Heavy-Light Decomposition (HLD)

Time Complexity:
- Decomposition: O(n)
- Path Query/Update: O(log² n) with segment tree
- Point Update: O(log n) with segment tree

Space Complexity: O(n)

Use Cases:
- Answering min/max/sum queries on tree paths
- Updating values on tree paths
- LCA (Lowest Common Ancestor) queries with path info

Key Insight:
- Decompose tree into heavy paths (heavy child = child with most vertices in subtree)
- Each vertex has exactly one heavy child
- Tree has O(log n) heavy paths from root to any node
- Use segment tree to query along paths
"""

from typing import List, Optional, Tuple
from collections import defaultdict


class SegmentTree:
    """Segment tree for range min/max/sum queries."""

    def __init__(self, arr: List[int]):
        self.n = len(arr)
        self.tree = [0] * (4 * self.n)
        if self.n > 0:
            self._build(arr, 0, 0, self.n - 1)

    def _build(self, arr: List[int], node: int, start: int, end: int) -> None:
        """Build segment tree recursively."""
        if start == end:
            self.tree[node] = arr[start]
        else:
            mid = (start + end) // 2
            self._build(arr, 2 * node + 1, start, mid)
            self._build(arr, 2 * node + 2, mid + 1, end)
            self.tree[node] = max(self.tree[2 * node + 1], self.tree[2 * node + 2])

    def update(self, idx: int, val: int) -> None:
        """Update element at index idx to val."""
        self._update(0, 0, self.n - 1, idx, val)

    def _update(self, node: int, start: int, end: int, idx: int, val: int) -> None:
        if start == end:
            self.tree[node] = val
        else:
            mid = (start + end) // 2
            if idx <= mid:
                self._update(2 * node + 1, start, mid, idx, val)
            else:
                self._update(2 * node + 2, mid + 1, end, idx, val)
            self.tree[node] = max(self.tree[2 * node + 1], self.tree[2 * node + 2])

    def query(self, l: int, r: int) -> int:
        """Query max in range [l, r]."""
        if l > r or self.n == 0:
            return 0
        return self._query(0, 0, self.n - 1, l, r)

    def _query(self, node: int, start: int, end: int, l: int, r: int) -> int:
        if r < start or end < l:
            return 0
        if l <= start and end <= r:
            return self.tree[node]
        mid = (start + end) // 2
        left_max = self._query(2 * node + 1, start, mid, l, r)
        right_max = self._query(2 * node + 2, mid + 1, end, l, r)
        return max(left_max, right_max)


class HeavyLightDecomposition:
    """Heavy-Light Decomposition for tree path queries."""

    def __init__(self, n: int, edges: List[Tuple[int, int]], values: List[int]):
        """
        Initialize HLD.

        Args:
            n: Number of vertices (0 to n-1)
            edges: List of (u, v) edges (undirected)
            values: List of vertex values
        """
        self.n = n
        self.values = values.copy()
        self.adj: List[List[int]] = [[] for _ in range(n)]

        for u, v in edges:
            self.adj[u].append(v)
            self.adj[v].append(u)

        # HLD arrays
        self.parent = [-1] * n
        self.depth = [0] * n
        self.subtree_size = [0] * n
        self.heavy_child = [-1] * n
        self.chain_id = [-1] * n
        self.pos_in_chain = [-1] * n
        self.chain_head = [-1] * n

        self.chain_nodes: List[List[int]] = []
        self.seg_trees: List[SegmentTree] = []

        if n > 0:
            self._dfs1(0, -1, 0)
            self._dfs2(0, 0)

    def _dfs1(self, u: int, p: int, d: int) -> None:
        """First DFS: compute subtree sizes and find heavy children."""
        self.parent[u] = p
        self.depth[u] = d
        self.subtree_size[u] = 1

        for v in self.adj[u]:
            if v != p:
                self._dfs1(v, u, d + 1)
                self.subtree_size[u] += self.subtree_size[v]

                if self.heavy_child[u] == -1 or \
                   self.subtree_size[v] > self.subtree_size[self.heavy_child[u]]:
                    self.heavy_child[u] = v

    def _dfs2(self, u: int, chain_id: int) -> None:
        """Second DFS: assign chain IDs and positions."""
        self.chain_id[u] = chain_id

        if chain_id >= len(self.chain_nodes):
            self.chain_nodes.append([])
            self.chain_head.append(-1)

        if len(self.chain_nodes[chain_id]) == 0:
            self.chain_head[chain_id] = u

        self.pos_in_chain[u] = len(self.chain_nodes[chain_id])
        self.chain_nodes[chain_id].append(u)

        if self.heavy_child[u] != -1:
            self._dfs2(self.heavy_child[u], chain_id)

        for v in self.adj[u]:
            if v != self.parent[u] and v != self.heavy_child[u]:
                self._dfs2(v, len(self.chain_nodes))

    def _build_segment_trees(self) -> None:
        """Build segment trees for each chain."""
        self.seg_trees = []
        for chain in self.chain_nodes:
            chain_values = [self.values[u] for u in chain]
            self.seg_trees.append(SegmentTree(chain_values))

    def update(self, u: int, val: int) -> None:
        """Update value at vertex u."""
        self.values[u] = val
        self._build_segment_trees()

    def query_path(self, u: int, v: int) -> int:
        """Query max value on path from u to v."""
        if not self.seg_trees:
            self._build_segment_trees()

        result = 0

        # Bring u and v to same level
        while self.depth[u] > self.depth[v]:
            result = max(result, self._query_up(u))
            u = self.parent[u]
        while self.depth[v] > self.depth[u]:
            result = max(result, self._query_up(v))
            v = self.parent[v]

        # Move both up simultaneously
        while u != v:
            result = max(result, self._query_up(u), self._query_up(v))
            u = self.parent[u]
            v = self.parent[v]

        result = max(result, self.values[u])
        return result

    def _query_up(self, u: int) -> int:
        """Query from u to head of its chain."""
        chain_id = self.chain_id[u]
        start = self.pos_in_chain[self.chain_head[chain_id]]
        end = self.pos_in_chain[u]
        return self.seg_trees[chain_id].query(start, end)


if __name__ == "__main__":
    # Example: Tree with path queries
    #     0
    #    / \
    #   1   2
    #  / \
    # 3   4

    n = 5
    edges = [(0, 1), (0, 2), (1, 3), (1, 4)]
    values = [10, 20, 30, 40, 50]

    hld = HeavyLightDecomposition(n, edges, values)

    print("Path 3->4 max value:", hld.query_path(3, 4))  # 3->1->4, values: 40, 20, 50
    print("Path 3->2 max value:", hld.query_path(3, 2))  # 3->1->0->2, values: 40, 20, 10, 30
    print("Path 4->2 max value:", hld.query_path(4, 2))  # 4->1->0->2, values: 50, 20, 10, 30

    hld.update(1, 100)
    print("After update(1, 100):")
    print("Path 3->4 max value:", hld.query_path(3, 4))  # 40, 100, 50
