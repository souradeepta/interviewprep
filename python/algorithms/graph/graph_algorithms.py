"""
Comprehensive Graph Algorithms for SDE Interviews
=================================================

This module implements the most important graph algorithms tested in technical
interviews. Each algorithm includes time/space complexity, detailed explanation,
and practical guidance on when to apply it.

GRAPH THEORY FUNDAMENTALS:

Graph Representation:
    Adjacency List (used here): {node: [(neighbor, weight), ...]}
    Example: {'A': [('B', 1), ('C', 4)], 'B': [('C', 2)], 'C': []}

    Space: O(V + E) where V = nodes, E = edges
    Lookup edge (A→B): O(degree(A)) = O(V) worst case

    Adjacency Matrix: 2D array where matrix[i][j] = weight
    Space: O(V²)
    Lookup edge: O(1)
    → Use for dense graphs (many edges), adjacency list for sparse

Graph Properties:
    Directed vs Undirected: edges have direction or not
    Weighted vs Unweighted: edges have costs or all cost 1
    Cyclic vs Acyclic: contains cycles or not (DAGs are acyclic)
    Connected vs Disconnected: all nodes reachable or not

ALGORITHM CLASSIFICATION:

CATEGORY 1: Shortest Path (Single Source)
──────────────────────────────────────────
1. Dijkstra's Algorithm
   - When: Non-negative edge weights, single source
   - Time: O((V + E) log V) with binary heap
   - Returns: shortest distance and predecessor path
   - Limitation: Fails with negative weights

2. Bellman-Ford Algorithm
   - When: Negative edge weights allowed (but no negative cycles)
   - Time: O(V * E), slower than Dijkstra
   - Returns: shortest distances, detects negative cycles
   - Advantage: Handles negative edges unlike Dijkstra

CATEGORY 2: Shortest Path (All Pairs)
──────────────────────────────────────
3. Floyd-Warshall
   - When: Need shortest paths between ALL node pairs
   - Time: O(V³)
   - Space: O(V²)
   - Handles: Negative edges (no negative cycles)
   - Use case: Small graphs (V < 500); dense graphs

CATEGORY 3: Traversal
──────────────────────
4. Depth-First Search (DFS)
   - When: Visit all reachable nodes, find cycles, topological sort
   - Time: O(V + E)
   - Space: O(V) call stack / O(V) visited set
   - Variants: Recursive (clean) vs iterative (avoid stack overflow)

5. Breadth-First Search (BFS)
   - When: Find shortest path in unweighted graph, level-order traversal
   - Time: O(V + E)
   - Space: O(V) queue
   - Property: Guarantees shortest path in unweighted graphs

CATEGORY 4: Minimum Spanning Tree
──────────────────────────────────
6. Kruskal's Algorithm
   - When: Find MST (subset of edges with minimum total weight)
   - Time: O(E log E) sorting + O(E α(V)) union-find
   - Approach: Sort edges by weight, greedily add edges (union-find prevents cycles)
   - Space: O(V + E)

7. Prim's Algorithm
   - When: Find MST, similar to Dijkstra
   - Time: O(E log V) with binary heap
   - Approach: Start with one node, greedily expand to closest unvisited
   - Space: O(V + E)

CATEGORY 5: Topological Sorting
────────────────────────────────
8. Topological Sort (DFS-based)
   - When: Process tasks with dependencies, order jobs
   - Time: O(V + E)
   - Precondition: Graph must be a DAG (Directed Acyclic Graph)
   - Returns: Valid topological ordering (not unique)
   - Application: Build systems, job scheduling, course prerequisites

CATEGORY 6: Connectivity
────────────────────────
9. Union-Find (Disjoint Set Union)
   - When: Check connectivity, find connected components
   - Time: Nearly O(1) with path compression (O(α(n)) amortized)
   - Space: O(V)
   - Application: Detect cycles in undirected graphs, Kruskal's algorithm

10. Connected Components
    - When: Find all separate components in undirected graph
    - Time: O(V + E) using DFS/BFS
    - Space: O(V)
    - Application: Network analysis, image processing

CATEGORY 7: Special Graph Types
────────────────────────────────
11. Bipartite Graph Check
    - When: Check if graph can be 2-colored
    - Time: O(V + E) BFS/DFS with coloring
    - Space: O(V)
    - Application: Matching problems, odd-cycle detection

INTERVIEW QUESTION PATTERNS:

PATTERN 1: "Find shortest path from A to B"
    If unweighted → BFS (guarantees shortest)
    If weighted, non-negative → Dijkstra
    If weighted, with negatives → Bellman-Ford or DP

PATTERN 2: "What nodes are reachable from X?"
    DFS or BFS from X, count visited nodes
    Could also ask connected components (multiple sources)

PATTERN 3: "Process tasks in dependency order"
    Topological sort (tasks = nodes, dependencies = edges)
    Check for cycles (would make ordering impossible)

PATTERN 4: "Find minimum cost spanning tree"
    Kruskal (sort edges) or Prim (build from nodes)
    Use union-find to detect cycles (Kruskal) or visited set (Prim)

PATTERN 5: "Is graph bipartite?"
    2-color BFS/DFS; if any conflict found → not bipartite

COMMON MISTAKES:

❌ Using Dijkstra with negative weights (gives wrong answer)
❌ BFS on weighted graph expecting shortest path (only works unweighted)
❌ Topological sort without checking DAG property
❌ Not checking graph connectivity before algorithms needing connected graphs
❌ Confusing MST (minimum spanning TREE) with shortest path (different problems)

GRAPH ALGORITHM SELECTION GUIDE:

Question                          → Algorithm          → Time
─────────────────────────────────────────────────────────────
Shortest path A→B?                → Dijkstra            → O((V+E)logV)
Shortest path ALL pairs?          → Floyd-Warshall     → O(V³)
Visit all reachable?              → DFS/BFS            → O(V+E)
Task ordering?                    → Topological sort   → O(V+E)
Minimum spanning tree?            → Kruskal/Prim       → O(ElogE)/O(ElogV)
Check connectivity?               → Union-Find/DFS     → O(α(n))/O(V+E)
Find components?                  → DFS/BFS multi-src  → O(V+E)
Is bipartite?                     → 2-color BFS        → O(V+E)
Detect cycle (directed)?          → DFS colors         → O(V+E)
Detect cycle (undirected)?        → Union-Find         → O(Eα(n))

Graph Representation Recommendation:
    Sparse graph (E << V²) → Adjacency list (space efficient)
    Dense graph (E ≈ V²) → Adjacency matrix (fast lookups)
    This repository uses adjacency list; convert if needed

IMPLEMENTATION NOTES:

Graph convention used throughout:
    graph: dict[node, list[tuple[neighbor, weight]]]
    Example: {'A': [('B', 1), ('C', 4)], 'B': [('C', 2)], 'C': []}

    For unweighted graphs, weight is typically 1:
        graph: dict[node, list[neighbor]]
        Can convert: {u: [(v, 1) for v in neighbors]}

Time/Space complexity always given for each algorithm.
See individual function docstrings for detailed implementation notes.

REFERENCES:
    - Introduction to Algorithms (Cormen et al.) - comprehensive treatment
    - Algorithm Design Manual (Skiena) - practical focus
    - LeetCode graph problems - real interview patterns
"""

import heapq
from collections import defaultdict, deque
from typing import Any, Optional


# ---------------------------------------------------------------------------
# 1. Dijkstra's Algorithm
# ---------------------------------------------------------------------------

def dijkstra(graph: dict, start: Any) -> tuple[dict, dict]:
    """Single-source shortest paths for graphs with non-negative edge weights.

    Uses a binary min-heap (priority queue) to greedily expand the
    closest unvisited node.

    Parameters
    ----------
    graph : dict
        Adjacency list: {node: [(neighbor, weight), ...]}
        All weights must be >= 0.
    start : Any
        Source node.

    Returns
    -------
    dist : dict
        Shortest distance from *start* to every reachable node.
        Unreachable nodes are absent from the dict.
    pred : dict
        Predecessor map for path reconstruction.
        pred[v] = u means the shortest path to v goes through u.

    Complexity
    ----------
    Time  : O((V + E) log V)  with a binary heap
    Space : O(V + E)
    """
    dist: dict = {start: 0}
    pred: dict = {start: None}
    # heap entries: (distance, node)
    heap = [(0, start)]

    while heap:
        d, u = heapq.heappop(heap)
        if d > dist.get(u, float("inf")):
            continue  # stale entry
        for v, w in graph.get(u, []):
            nd = d + w
            if nd < dist.get(v, float("inf")):
                dist[v] = nd
                pred[v] = u
                heapq.heappush(heap, (nd, v))

    return dist, pred


def reconstruct_path(pred: dict, start: Any, end: Any) -> list:
    """Helper: reconstruct shortest path using predecessor map."""
    path = []
    cur = end
    while cur is not None:
        path.append(cur)
        cur = pred.get(cur)
        if cur == start:
            path.append(start)
            break
        if cur is None:
            return []  # no path
    return path[::-1]


# ---------------------------------------------------------------------------
# 2. Bellman-Ford Algorithm
# ---------------------------------------------------------------------------

def bellman_ford(graph: dict, start: Any) -> tuple[dict, bool]:
    """Single-source shortest paths; handles negative-weight edges.

    Relaxes every edge V-1 times.  A further relaxation pass detects
    negative-weight cycles reachable from *start*.

    Parameters
    ----------
    graph : dict
        Adjacency list: {node: [(neighbor, weight), ...]}
        Negative weights are allowed; negative *cycles* are detected.
    start : Any
        Source node.

    Returns
    -------
    dist : dict
        Shortest distances from *start*.  May be -inf for nodes
        reachable through a negative cycle.
    has_negative_cycle : bool
        True iff a negative-weight cycle reachable from *start* exists.

    Complexity
    ----------
    Time  : O(V * E)
    Space : O(V)
    """
    # Collect all nodes
    nodes = set(graph.keys())
    for neighbors in graph.values():
        for v, _ in neighbors:
            nodes.add(v)

    dist = {n: float("inf") for n in nodes}
    dist[start] = 0

    edges = []
    for u, neighbors in graph.items():
        for v, w in neighbors:
            edges.append((u, v, w))

    # Relax V-1 times
    for _ in range(len(nodes) - 1):
        updated = False
        for u, v, w in edges:
            if dist[u] != float("inf") and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                updated = True
        if not updated:
            break

    # Detect negative cycles (one more pass)
    has_negative_cycle = False
    for u, v, w in edges:
        if dist[u] != float("inf") and dist[u] + w < dist[v]:
            has_negative_cycle = True
            break

    return dist, has_negative_cycle


# ---------------------------------------------------------------------------
# 3. Floyd-Warshall Algorithm
# ---------------------------------------------------------------------------

def floyd_warshall(adj_matrix: list[list[float]]) -> list[list[float]]:
    """All-pairs shortest paths via dynamic programming.

    Parameters
    ----------
    adj_matrix : list[list[float]]
        N x N matrix where adj_matrix[i][j] is the direct edge weight
        from i to j.  Use float('inf') for no direct edge.
        adj_matrix[i][i] should be 0.

    Returns
    -------
    dist : list[list[float]]
        N x N matrix of shortest distances between all pairs.
        A negative value on the diagonal indicates a negative cycle.

    Complexity
    ----------
    Time  : O(N^3)
    Space : O(N^2)
    """
    n = len(adj_matrix)
    dist = [row[:] for row in adj_matrix]  # deep copy

    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]

    return dist


# ---------------------------------------------------------------------------
# 4. Kruskal's MST (Union-Find)
# ---------------------------------------------------------------------------

class _UnionFind:
    """Weighted Union-Find with path compression."""

    def __init__(self, nodes):
        self.parent = {n: n for n in nodes}
        self.rank = {n: 0 for n in nodes}

    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]  # path halving
            x = self.parent[x]
        return x

    def union(self, x, y) -> bool:
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False
        if self.rank[rx] < self.rank[ry]:
            rx, ry = ry, rx
        self.parent[ry] = rx
        if self.rank[rx] == self.rank[ry]:
            self.rank[rx] += 1
        return True


def kruskal_mst(vertices: list, edges: list[tuple]) -> tuple[float, list]:
    """Minimum Spanning Tree via Kruskal's algorithm.

    Parameters
    ----------
    vertices : list
        All vertex identifiers.
    edges : list[tuple]
        Edges as (weight, u, v).  Need not be sorted beforehand.

    Returns
    -------
    total_weight : float
        Sum of MST edge weights.
    mst_edges : list[tuple]
        Edges included in the MST as (weight, u, v).

    Complexity
    ----------
    Time  : O(E log E)  dominated by sorting
    Space : O(V)
    """
    uf = _UnionFind(vertices)
    mst_edges = []
    total_weight = 0

    for w, u, v in sorted(edges):
        if uf.union(u, v):
            mst_edges.append((w, u, v))
            total_weight += w
            if len(mst_edges) == len(vertices) - 1:
                break  # MST complete

    return total_weight, mst_edges


# ---------------------------------------------------------------------------
# 5. Prim's MST (min-heap)
# ---------------------------------------------------------------------------

def prim_mst(graph: dict, start: Any) -> tuple[float, list]:
    """Minimum Spanning Tree via Prim's algorithm.

    Parameters
    ----------
    graph : dict
        Adjacency list: {node: [(neighbor, weight), ...]}
        Must represent an undirected graph (edges appear in both
        directions).
    start : Any
        Starting node.

    Returns
    -------
    total_weight : float
        Total weight of the MST.
    mst_edges : list[tuple]
        Edges in the MST as (u, v, weight).

    Complexity
    ----------
    Time  : O((V + E) log V)
    Space : O(V + E)
    """
    visited = set()
    mst_edges = []
    total_weight = 0
    # heap: (weight, from_node, to_node)
    heap = [(0, start, start)]

    while heap:
        w, u, v = heapq.heappop(heap)
        if v in visited:
            continue
        visited.add(v)
        if u != v:  # skip the seed edge
            mst_edges.append((u, v, w))
            total_weight += w
        for neighbor, weight in graph.get(v, []):
            if neighbor not in visited:
                heapq.heappush(heap, (weight, v, neighbor))

    return total_weight, mst_edges


# ---------------------------------------------------------------------------
# 6. Tarjan's Strongly Connected Components
# ---------------------------------------------------------------------------

def tarjan_scc(graph: dict) -> list[list]:
    """Strongly Connected Components via Tarjan's algorithm.

    Uses DFS with a discovery timestamp and a low-link value to
    identify SCC roots, then pops the stack to emit each SCC.

    Parameters
    ----------
    graph : dict
        Directed adjacency list: {node: [neighbor, ...]}

    Returns
    -------
    sccs : list[list]
        List of SCCs.  Each SCC is a list of nodes.
        Returned in reverse topological order of the condensation DAG.

    Complexity
    ----------
    Time  : O(V + E)
    Space : O(V)
    """
    index_counter = [0]
    stack = []
    on_stack = set()
    index = {}
    low_link = {}
    sccs = []

    nodes = set(graph.keys())
    for neighbors in graph.values():
        nodes.update(neighbors)

    def strongconnect(v):
        index[v] = low_link[v] = index_counter[0]
        index_counter[0] += 1
        stack.append(v)
        on_stack.add(v)

        for w in graph.get(v, []):
            if w not in index:
                strongconnect(w)
                low_link[v] = min(low_link[v], low_link[w])
            elif w in on_stack:
                low_link[v] = min(low_link[v], index[w])

        # v is a root of an SCC
        if low_link[v] == index[v]:
            scc = []
            while True:
                w = stack.pop()
                on_stack.discard(w)
                scc.append(w)
                if w == v:
                    break
            sccs.append(scc)

    import sys
    old_limit = sys.getrecursionlimit()
    sys.setrecursionlimit(max(old_limit, len(nodes) + 100))
    try:
        for node in nodes:
            if node not in index:
                strongconnect(node)
    finally:
        sys.setrecursionlimit(old_limit)

    return sccs


# ---------------------------------------------------------------------------
# 7. Topological Sort — Kahn's BFS Algorithm
# ---------------------------------------------------------------------------

def topological_sort_kahn(graph: dict) -> tuple[list, bool]:
    """Topological ordering of a directed graph using Kahn's algorithm.

    Parameters
    ----------
    graph : dict
        Directed adjacency list: {node: [neighbor, ...]}
        All nodes (including sinks) must appear as keys.

    Returns
    -------
    order : list
        Topologically sorted nodes.  Empty if a cycle is detected.
    has_cycle : bool
        True iff the graph contains at least one directed cycle.

    Complexity
    ----------
    Time  : O(V + E)
    Space : O(V)
    """
    in_degree: dict = defaultdict(int)
    nodes = set(graph.keys())

    for u, neighbors in graph.items():
        for v in neighbors:
            in_degree[v] += 1
            nodes.add(v)

    queue = deque(n for n in nodes if in_degree[n] == 0)
    order = []

    while queue:
        u = queue.popleft()
        order.append(u)
        for v in graph.get(u, []):
            in_degree[v] -= 1
            if in_degree[v] == 0:
                queue.append(v)

    has_cycle = len(order) != len(nodes)
    return order, has_cycle


# ---------------------------------------------------------------------------
# 8. A* Search on a 2-D Grid
# ---------------------------------------------------------------------------

def astar(
    grid: list[list[int]],
    start: tuple[int, int],
    end: tuple[int, int],
) -> tuple[float, list[tuple[int, int]]]:
    """A* pathfinding on a 2-D grid with Manhattan distance heuristic.

    Parameters
    ----------
    grid : list[list[int]]
        2-D grid where 0 = passable, 1 = blocked.
    start : tuple[int, int]
        (row, col) of the start cell.
    end : tuple[int, int]
        (row, col) of the goal cell.

    Returns
    -------
    cost : float
        Shortest path cost (step count).  float('inf') if no path.
    path : list[tuple[int, int]]
        Ordered list of cells from *start* to *end* inclusive.
        Empty list if no path exists.

    Complexity
    ----------
    Time  : O(V log V)  where V = rows * cols
    Space : O(V)
    """
    rows, cols = len(grid), len(grid[0])

    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    g_score: dict = {start: 0}
    f_score = {start: heuristic(start, end)}
    came_from: dict = {}
    # heap: (f_score, node)
    heap = [(f_score[start], start)]
    closed: set = set()

    while heap:
        _, current = heapq.heappop(heap)
        if current == end:
            # Reconstruct path
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path.reverse()
            return g_score[end], path

        if current in closed:
            continue
        closed.add(current)

        r, c = current
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            neighbor = (nr, nc)
            if not (0 <= nr < rows and 0 <= nc < cols):
                continue
            if grid[nr][nc] == 1:
                continue
            if neighbor in closed:
                continue
            tentative_g = g_score[current] + 1
            if tentative_g < g_score.get(neighbor, float("inf")):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f = tentative_g + heuristic(neighbor, end)
                f_score[neighbor] = f
                heapq.heappush(heap, (f, neighbor))

    return float("inf"), []


# ============================================================================
# SECTION 2: TREE DATA STRUCTURE & TREE DP
# ============================================================================

class TreeNode:
    """Binary tree node for tree algorithms."""
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def lca(root: TreeNode, p: TreeNode, q: TreeNode) -> TreeNode:
    """
    Lowest Common Ancestor of two nodes (assuming both exist in tree).

    Time: O(n) single traversal, O(log n) balanced BST property
    Space: O(h) where h = height (recursion stack)

    Use when: Tree path queries, distance calculation, common ancestor problems
    Interview tip: Show recursive solution vs iterative with parent pointers
    """
    if not root or root == p or root == q:
        return root

    left = lca(root.left, p, q)
    right = lca(root.right, p, q)

    if left and right:
        return root  # Both found on different sides
    return left if left else right  # Both on same side


def path_sum(root: TreeNode, target_sum: int) -> bool:
    """
    Check if any root-to-leaf path sums to target.

    Time: O(n) worst-case, O(log n) early termination possible
    Space: O(h) recursion depth

    Use when: Path validation, constraint checking
    Interview tip: Explain both recursive and iterative approaches
    """
    def dfs(node, remaining):
        if not node:
            return False

        remaining -= node.val

        if not node.left and not node.right:
            return remaining == 0

        return dfs(node.left, remaining) or dfs(node.right, remaining)

    return dfs(root, target_sum)


def all_paths_sum(root: TreeNode) -> list[list[int]]:
    """
    Find all root-to-leaf paths (returning list of paths).

    Time: O(n * h) where h is height (copy path per leaf)
    Space: O(h) recursion + output space

    Use when: All paths needed, backtracking on tree, path reconstruction
    Interview tip: Distinguish from single path - need to track all branches
    """
    result = []

    def dfs(node, path):
        if not node:
            return

        path.append(node.val)

        if not node.left and not node.right:
            result.append(path[:])
        else:
            dfs(node.left, path)
            dfs(node.right, path)

        path.pop()

    dfs(root, [])
    return result


def tree_diameter(root: TreeNode) -> int:
    """
    Longest path in tree (diameter = longest path between any two nodes).

    Time: O(n) single DFS
    Space: O(h) recursion depth

    Use when: Tree analysis, path properties, constraint satisfaction
    Interview tip: Explain why we need to return height and track global max
    """
    max_diameter = [0]

    def dfs(node):
        if not node:
            return 0

        left_height = dfs(node.left)
        right_height = dfs(node.right)

        # Diameter through this node
        max_diameter[0] = max(max_diameter[0], left_height + right_height)

        return max(left_height, right_height) + 1

    dfs(root)
    return max_diameter[0]


def rob_tree(root: TreeNode) -> int:
    """
    House Robber III: max sum non-adjacent nodes (tree version).

    Can't rob node if robbing any of its children.

    Time: O(n) single DFS
    Space: O(h) recursion

    Use when: Constraint optimization on trees, state-dependent DP
    Interview tip: Return tuple (rob_this, dont_rob_this) for clarity
    """
    def dfs(node):
        if not node:
            return (0, 0)  # (rob, dont_rob)

        left_rob, left_no_rob = dfs(node.left)
        right_rob, right_no_rob = dfs(node.right)

        # Rob current: can't rob children
        rob_current = node.val + left_no_rob + right_no_rob

        # Don't rob current: can choose to rob or not rob each child
        dont_rob = max(left_rob, left_no_rob) + max(right_rob, right_no_rob)

        return (rob_current, dont_rob)

    return max(dfs(root))


def build_tree_preorder_inorder(preorder: list[int], inorder: list[int]) -> TreeNode:
    """
    Build tree from preorder and inorder traversals.

    Preorder: root, left, right
    Inorder: left, root, right

    Time: O(n²) simple, O(n) with hashmap
    Space: O(n) for result tree

    Use when: Tree reconstruction, traversal combination problems
    Interview tip: Explain role of each traversal (preorder gives root, inorder gives split)
    """
    if not preorder or not inorder:
        return None

    inorder_map = {val: i for i, val in enumerate(inorder)}

    def build(pre_start, pre_end, in_start, in_end):
        if pre_start > pre_end:
            return None

        root_val = preorder[pre_start]
        root = TreeNode(root_val)

        root_idx = inorder_map[root_val]
        left_size = root_idx - in_start

        root.left = build(pre_start + 1, pre_start + left_size, in_start, root_idx - 1)
        root.right = build(pre_start + left_size + 1, pre_end, root_idx + 1, in_end)

        return root

    return build(0, len(preorder) - 1, 0, len(inorder) - 1)


def serialize_tree(root: TreeNode) -> str:
    """
    Serialize tree to string (preorder with markers).

    Use null marker to indicate missing children.

    Time: O(n)
    Space: O(n) for result string

    Use when: Tree encoding, persistence, transmission
    Interview tip: Explain why preorder works (root first, can reconstruct without inorder)
    """
    result = []

    def preorder(node):
        if not node:
            result.append('null')
            return

        result.append(str(node.val))
        preorder(node.left)
        preorder(node.right)

    preorder(root)
    return ','.join(result)


def deserialize_tree(data: str) -> TreeNode:
    """
    Deserialize string to tree (reverse of serialize_tree).

    Time: O(n)
    Space: O(n) for tree

    Use when: Tree decoding, reconstruction from string
    Interview tip: Use iterator to track position in preorder sequence
    """
    nodes = data.split(',')
    iterator = iter(nodes)

    def build():
        val = next(iterator)
        if val == 'null':
            return None

        root = TreeNode(int(val))
        root.left = build()
        root.right = build()
        return root

    return build()


# ============================================================================
# SECTION 3: ADVANCED GRAPH TRAVERSALS
# ============================================================================
# DFS/BFS patterns with variations for different problem types.

def count_islands(grid: list[list[str]]) -> int:
    """
    Count distinct islands (connected 1s).

    Time: O(m·n) visit each cell once
    Space: O(m·n) for visited set

    Use when: Connected component counting, region identification
    Interview tip: Compare DFS (stack overflow risk), BFS (queue), Union-Find
    """
    if not grid:
        return 0

    visited = set()
    count = 0

    def dfs(i, j):
        if i < 0 or i >= len(grid) or j < 0 or j >= len(grid[0]):
            return
        if (i, j) in visited or grid[i][j] == '0':
            return

        visited.add((i, j))
        dfs(i+1, j)
        dfs(i-1, j)
        dfs(i, j+1)
        dfs(i, j-1)

    for i in range(len(grid)):
        for j in range(len(grid[0])):
            if grid[i][j] == '1' and (i, j) not in visited:
                dfs(i, j)
                count += 1

    return count


def is_bipartite(graph: list[list[int]]) -> bool:
    """
    Check if graph is bipartite (2-colorable).

    Time: O(v + e)
    Space: O(v)

    Use when: Bipartite matching preprocessing, 2-coloring problems
    Interview tip: Explain DFS coloring vs BFS coloring trade-offs
    """
    color = {}

    def dfs(node, c):
        color[node] = c
        for neighbor in graph[node]:
            if neighbor in color:
                if color[neighbor] == c:
                    return False
            else:
                if not dfs(neighbor, 1 - c):
                    return False
        return True

    for i in range(len(graph)):
        if i not in color:
            if not dfs(i, 0):
                return False

    return True


def has_cycle_directed(graph: list[list[int]]) -> bool:
    """
    Detect cycle in directed graph using DFS coloring.

    Colors: 0=white (unvisited), 1=gray (visiting), 2=black (done)
    Cycle exists if we reach a gray node.

    Time: O(v + e)
    Space: O(v)

    Use when: Topological sort verification, dependency analysis
    Interview tip: Explain why we need 3 states (white/gray/black)
    """
    color = [0] * len(graph)  # 0: white, 1: gray, 2: black

    def dfs(node):
        if color[node] == 1:
            return True  # Back edge found
        if color[node] == 2:
            return False  # Already processed

        color[node] = 1  # Mark as visiting

        for neighbor in graph[node]:
            if dfs(neighbor):
                return True

        color[node] = 2  # Mark as done
        return False

    for i in range(len(graph)):
        if color[i] == 0:
            if dfs(i):
                return True

    return False


def has_cycle_undirected(n: int, edges: list[list[int]]) -> bool:
    """
    Detect cycle in undirected graph using DFS.

    Time: O(v + e)
    Space: O(v)

    Use when: Tree verification (acyclic graph), connectivity analysis
    Interview tip: Contrast with directed version - need to track parent
    """
    graph = [[] for _ in range(n)]
    for u, v in edges:
        graph[u].append(v)
        graph[v].append(u)

    visited = set()

    def dfs(node, parent):
        visited.add(node)
        for neighbor in graph[node]:
            if neighbor == parent:
                continue
            if neighbor in visited:
                return True
            if dfs(neighbor, node):
                return True
        return False

    for i in range(n):
        if i not in visited:
            if dfs(i, -1):
                return True

    return False


# ---------------------------------------------------------------------------
# __main__ demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("GRAPH ALGORITHMS DEMO")
    print("=" * 60)

    # ---- Dijkstra ----
    print("\n--- Dijkstra ---")
    g = {
        "A": [("B", 1), ("C", 4)],
        "B": [("C", 2), ("D", 5)],
        "C": [("D", 1)],
        "D": [],
    }
    dist, pred = dijkstra(g, "A")
    print(f"Distances from A: {dist}")
    print(f"Path A->D: {reconstruct_path(pred, 'A', 'D')}")

    # ---- Bellman-Ford ----
    print("\n--- Bellman-Ford ---")
    g_bf = {
        "A": [("B", 1), ("C", 4)],
        "B": [("C", -3), ("D", 2)],
        "C": [("D", 3)],
        "D": [],
    }
    dist_bf, neg_cycle = bellman_ford(g_bf, "A")
    print(f"Distances: {dist_bf}")
    print(f"Negative cycle: {neg_cycle}")

    # Negative cycle example
    g_neg = {
        "A": [("B", 1)],
        "B": [("C", -2)],
        "C": [("A", -1)],
    }
    _, neg = bellman_ford(g_neg, "A")
    print(f"Negative cycle detected (should be True): {neg}")

    # ---- Floyd-Warshall ----
    print("\n--- Floyd-Warshall ---")
    INF = float("inf")
    matrix = [
        [0,   3,   INF, 7  ],
        [8,   0,   2,   INF],
        [5,   INF, 0,   1  ],
        [2,   INF, INF, 0  ],
    ]
    fw = floyd_warshall(matrix)
    print("All-pairs shortest distances:")
    for row in fw:
        print(" ", [f"{x:5.0f}" if x != INF else "  inf" for x in row])

    # ---- Kruskal ----
    print("\n--- Kruskal MST ---")
    vertices = [0, 1, 2, 3, 4]
    edges = [
        (10, 0, 1), (6, 0, 2), (5, 0, 3),
        (15, 1, 4), (4, 2, 3), (2, 3, 4),
    ]
    total, mst = kruskal_mst(vertices, edges)
    print(f"MST total weight: {total}")
    print(f"MST edges: {mst}")

    # ---- Prim ----
    print("\n--- Prim MST ---")
    ug = {
        0: [(1, 10), (2, 6), (3, 5)],
        1: [(0, 10), (4, 15)],
        2: [(0, 6), (3, 4)],
        3: [(0, 5), (2, 4), (4, 2)],
        4: [(1, 15), (3, 2)],
    }
    total_p, mst_p = prim_mst(ug, 0)
    print(f"MST total weight: {total_p}")
    print(f"MST edges: {mst_p}")

    # ---- Tarjan SCC ----
    print("\n--- Tarjan SCC ---")
    dg = {
        0: [1],
        1: [2],
        2: [0, 3],
        3: [4],
        4: [5],
        5: [3],
    }
    sccs = tarjan_scc(dg)
    print(f"SCCs: {sccs}")

    # ---- Kahn Topological Sort ----
    print("\n--- Kahn Topological Sort ---")
    dag = {
        5: [2, 0],
        4: [0, 1],
        2: [3],
        3: [1],
        0: [],
        1: [],
    }
    order, cycle = topological_sort_kahn(dag)
    print(f"Topological order: {order}  (cycle={cycle})")

    # Cyclic graph
    cyclic = {0: [1], 1: [2], 2: [0]}
    _, has_cycle = topological_sort_kahn(cyclic)
    print(f"Cycle detected (should be True): {has_cycle}")

    # ---- A* ----
    print("\n--- A* Grid Search ---")
    grid = [
        [0, 0, 0, 0, 0],
        [1, 1, 0, 1, 0],
        [0, 0, 0, 0, 0],
        [0, 1, 1, 1, 0],
        [0, 0, 0, 0, 0],
    ]
    cost, path = astar(grid, (0, 0), (4, 4))
    print(f"Cost: {cost}")
    print(f"Path: {path}")
