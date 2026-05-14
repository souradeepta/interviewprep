"""
Graph Algorithms
================
Implementations of classical graph algorithms for SDE interview preparation.

Each function includes:
- Docstring with algorithm description and complexity
- Concrete usage example via __main__

Graph representation convention (unless stated otherwise):
    graph: dict[node, list[tuple[neighbor, weight]]]
    e.g.  {'A': [('B', 1), ('C', 4)], 'B': [('C', 2)], 'C': []}
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
