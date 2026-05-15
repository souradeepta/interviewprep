"""
Advanced Algorithms for SDE Interview Preparation
==================================================

Comprehensive implementations of 25+ advanced algorithms across:
- Dynamic Programming (advanced techniques)
- Graph Algorithms (flow, matching, 2-SAT)
- String Algorithms
- Computational Geometry
- Tree Algorithms

Each algorithm includes:
- Clear, interview-ready implementation
- Time/space complexity analysis
- Working demo examples
"""

from typing import List, Tuple, Dict, Set, Callable
from collections import defaultdict, deque
import heapq
import math


# ============================================================================
# DYNAMIC PROGRAMMING - ADVANCED
# ============================================================================

class ConvexHullTrick:
    """
    Convex Hull Trick (CHT) - Optimize DP transitions O(n²) → O(n log n)

    Used when DP recurrence has form: dp[i] = min/max(dp[j] + cost(j,i))
    where cost functions form a convex hull.

    Example: Minimize dp[i] = min(dp[j] + (j-i)²) for all j < i

    Time: O(n log n)
    Space: O(n)
    """

    def __init__(self):
        self.lines = []  # (slope, intercept, j_index)

    def bad_intersection(self, l1: Tuple, l2: Tuple, l3: Tuple) -> bool:
        """Check if l2 is removed by intersection of l1 and l3."""
        (m1, b1, _), (m2, b2, _), (m3, b3, _) = l1, l2, l3
        # Intersection point x = (b2-b1)/(m1-m2) and (b3-b2)/(m2-m3)
        # l2 is bad if (b3-b2)/(m2-m3) <= (b2-b1)/(m1-m2)
        return (b3 - b2) * (m1 - m2) <= (b2 - b1) * (m2 - m3)

    def add_line(self, slope: float, intercept: float, j: int):
        """Add line y = slope*x + intercept with source index j."""
        new_line = (slope, intercept, j)

        while len(self.lines) >= 2 and self.bad_intersection(
            self.lines[-2], self.lines[-1], new_line
        ):
            self.lines.pop()

        self.lines.append(new_line)

    def query(self, x: float) -> Tuple[float, int]:
        """Query minimum value at x. Returns (min_value, source_j_index)."""
        if not self.lines:
            return float('inf'), -1

        # Binary search to find the best line
        left, right = 0, len(self.lines) - 1
        while left < right:
            mid = (left + right) // 2
            m1, b1, _ = self.lines[mid]
            m2, b2, _ = self.lines[mid + 1]
            if m1 * x + b1 > m2 * x + b2:
                left = mid + 1
            else:
                right = mid

        m, b, j = self.lines[left]
        return m * x + b, j

    @staticmethod
    def solve_example():
        """Example: Find min cost where dp[i] = min(dp[j] + (j-i)²) for j < i."""
        n = 5
        dp = [0] * (n + 1)
        cht = ConvexHullTrick()

        for i in range(1, n + 1):
            # Add previous dp as line: y = 2*j*x - j² + dp[j] where x = i
            if i > 1:
                j = i - 1
                cht.add_line(2 * j, -j * j + dp[j], j)

            if i == 1:
                dp[i] = 0
            else:
                min_val, _ = cht.query(float(i))
                dp[i] = min_val + i * i

        return dp


class DigitDP:
    """
    Digit Dynamic Programming - Count/find extremum problems on digits

    Examples:
    - Count numbers in range [0, N] with specific digit properties
    - Find maximum/minimum number with constraints

    Time: O(log N * state_space)
    Space: O(state_space)
    """

    @staticmethod
    def count_numbers_with_digit_property(n: int, property_check: Callable) -> int:
        """
        Count numbers in [0, n] satisfying property_check.
        property_check(num) -> bool
        """
        s = str(n)
        memo = {}

        def dp(pos: int, tight: bool, started: bool, num: int) -> int:
            """
            pos: current digit position
            tight: can only go up to digit s[pos] if True
            started: have we placed a non-zero digit
            num: current number formed
            """
            if pos == len(s):
                return 1 if (not started or property_check(num)) else 0

            state = (pos, tight, started, num)
            if state in memo:
                return memo[state]

            limit = int(s[pos]) if tight else 9
            count = 0

            for digit in range(0, limit + 1):
                new_num = num * 10 + digit if started or digit > 0 else 0
                new_started = started or (digit > 0)
                new_tight = tight and (digit == limit)
                count += dp(pos + 1, new_tight, new_started, new_num)

            memo[state] = count
            return count

        return dp(0, True, False, 0)

    @staticmethod
    def count_numbers_no_consecutive_ones(n: int) -> int:
        """Count numbers in [0, n] with no consecutive 1s in binary."""
        s = bin(n)[2:]
        memo = {}

        def dp(pos: int, tight: bool, prev_one: bool) -> int:
            if pos == len(s):
                return 1

            state = (pos, tight, prev_one)
            if state in memo:
                return memo[state]

            limit = int(s[pos]) if tight else 1
            count = 0

            for digit in range(0, limit + 1):
                # Can't place 1 if previous was 1
                if digit == 1 and prev_one:
                    continue
                new_tight = tight and (digit == limit)
                count += dp(pos + 1, new_tight, digit == 1)

            memo[state] = count
            return count

        return dp(0, True, False)


class TreeDP:
    """
    Tree DP - Dynamic Programming on tree structures

    Example: Paint nodes to maximize edges between different colors

    Time: O(n)
    Space: O(n)
    """

    @staticmethod
    def tree_coloring_dp(adj: List[List[int]], k: int) -> int:
        """
        Find maximum edges with different colors using k colors.
        Returns maximum number of edges with different color endpoints.
        """
        n = len(adj)
        dp = [[0] * k for _ in range(n)]

        def dfs(u: int, parent: int, color: int) -> int:
            """dp[u][c] = best answer in subtree of u if u has color c."""
            best = 0
            for v in adj[u]:
                if v == parent:
                    continue
                # Try all colors for child
                for child_color in range(k):
                    if child_color == color:
                        # Same color: no edge bonus
                        edge_bonus = 0
                    else:
                        # Different color: +1 edge
                        edge_bonus = 1

                    child_val = dfs(v, u, child_color)
                    best = max(best, child_val + edge_bonus)

            dp[u][color] = best
            return best

        # Try all colors for root
        result = 0
        for root_color in range(k):
            result = max(result, dfs(0, -1, root_color))

        return result

    @staticmethod
    def tree_maximum_independent_set(adj: List[List[int]]) -> int:
        """Find maximum independent set on a tree (no two adjacent nodes)."""
        n = len(adj)
        dp_include = [0] * n
        dp_exclude = [0] * n

        def dfs(u: int, parent: int):
            dp_include[u] = 1
            dp_exclude[u] = 0

            for v in adj[u]:
                if v == parent:
                    continue
                dfs(v, u)
                # Include u: can't include children
                dp_include[u] += dp_exclude[v]
                # Exclude u: can include or exclude children
                dp_exclude[u] += max(dp_include[v], dp_exclude[v])

        dfs(0, -1)
        return max(dp_include[0], dp_exclude[0])


class KnuthYaoOptimization:
    """
    Knuth-Yao Optimization - Optimize DP via quadrangle inequality.

    Reduces O(n²) DP to O(n log n) when cost function satisfies
    quadrangle inequality.

    Example: Optimal BST, matrix chain multiplication variants

    Time: O(n log n)
    Space: O(n)
    """

    @staticmethod
    def optimal_bst_cost(keys: List[float], freq: List[float]) -> float:
        """
        Simplified optimal BST cost computation.
        Usually O(n³) → O(n²) with Knuth-Yao
        """
        n = len(keys)
        # dp[i][j] = cost of BST with keys i..j
        dp = [[0] * n for _ in range(n)]
        split = [[i for i in range(n)] for _ in range(n)]

        for length in range(1, n + 1):
            for i in range(n - length + 1):
                j = i + length - 1
                dp[i][j] = float('inf')

                # Search in range suggested by quadrangle inequality
                start = split[i][j - 1] if j > i else i
                end = split[i + 1][j] if i < j else j

                for k in range(start, end + 1):
                    if k > j:
                        break
                    if k < i:
                        continue

                    cost = (dp[i][k - 1] if k > i else 0) + \
                           (dp[k + 1][j] if k < j else 0) + \
                           sum(freq[i:j + 1])

                    if cost < dp[i][j]:
                        dp[i][j] = cost
                        split[i][j] = k

        return dp[0][n - 1]


class SOS_DP:
    """
    Sum Over Subsets (SOS) DP - O(n * 2^n) subset enumeration.

    Computes: dp[mask] = sum of f[submask] for all submasks of mask
    in O(n * 2^n) instead of O(3^n) naive approach.

    Time: O(n * 2^n)
    Space: O(2^n)
    """

    @staticmethod
    def subset_sum_convolution(a: List[int], b: List[int]) -> List[int]:
        """
        Compute: result[mask] = sum(a[s1] * b[s2]) where s1|s2 = mask
        """
        n = len(a)
        max_mask = 1 << n

        # Forward SOS transform on both arrays
        dp_a = a[:]
        dp_b = b[:]

        # Transform a
        for i in range(n):
            for mask in range(max_mask):
                if mask & (1 << i):
                    dp_a[mask] += dp_a[mask ^ (1 << i)]

        # Transform b
        for i in range(n):
            for mask in range(max_mask):
                if mask & (1 << i):
                    dp_b[mask] += dp_b[mask ^ (1 << i)]

        # Pointwise multiplication
        result = [dp_a[mask] * dp_b[mask] for mask in range(max_mask)]

        # Inverse transform
        for i in range(n):
            for mask in range(max_mask):
                if mask & (1 << i):
                    result[mask] -= result[mask ^ (1 << i)]

        return result

    @staticmethod
    def sos_sum(arr: List[int]) -> List[int]:
        """
        Transform: dp[mask] = sum(arr[submask]) for all submasks
        """
        n = len(arr)
        max_mask = 1 << n
        dp = arr[:]

        for i in range(n):
            for mask in range(max_mask):
                if mask & (1 << i):
                    dp[mask] += dp[mask ^ (1 << i)]

        return dp


# ============================================================================
# GRAPH ALGORITHMS - ADVANCED
# ============================================================================

class MaxFlowFordFulkerson:
    """
    Maximum Flow - Ford-Fulkerson with DFS

    Time: O(E * max_flow) - can be slow with bad edge weights
    Space: O(V + E)
    """

    def __init__(self, vertices: int):
        self.V = vertices
        self.graph = defaultdict(lambda: defaultdict(int))

    def add_edge(self, u: int, v: int, capacity: int):
        """Add edge with given capacity."""
        self.graph[u][v] += capacity

    def _dfs(self, source: int, sink: int, visited: Set, min_cap: int) -> int:
        """Find augmenting path using DFS and return bottleneck capacity."""
        if source == sink:
            return min_cap

        visited.add(source)

        for neighbor in self.graph[source]:
            if neighbor not in visited and self.graph[source][neighbor] > 0:
                flow = self._dfs(neighbor, sink, visited,
                                min(min_cap, self.graph[source][neighbor]))

                if flow > 0:
                    self.graph[source][neighbor] -= flow
                    self.graph[neighbor][source] += flow
                    return flow

        return 0

    def max_flow(self, source: int, sink: int) -> int:
        """Compute maximum flow from source to sink."""
        max_flow_value = 0

        while True:
            visited = set()
            flow = self._dfs(source, sink, visited, float('inf'))
            if flow == 0:
                break
            max_flow_value += flow

        return max_flow_value


class MaxFlowDinic:
    """
    Maximum Flow - Dinic's Algorithm

    More efficient than Ford-Fulkerson using level graph + blocking flow.

    Time: O(V² * E)
    Space: O(V + E)
    """

    def __init__(self, vertices: int):
        self.V = vertices
        self.graph = [[] for _ in range(vertices)]
        self.edges = []

    def add_edge(self, u: int, v: int, capacity: int):
        """Add edge with capacity."""
        self.graph[u].append(len(self.edges))
        self.edges.append([v, capacity, len(self.graph[v])])
        self.graph[v].append(len(self.edges))
        self.edges.append([u, 0, len(self.graph[u]) - 1])

    def _bfs(self, source: int, sink: int) -> List[int]:
        """Build level graph."""
        level = [-1] * self.V
        level[source] = 0
        queue = deque([source])

        while queue:
            u = queue.popleft()
            for idx in self.graph[u]:
                v, cap, _ = self.edges[idx]
                if level[v] == -1 and cap > 0:
                    level[v] = level[u] + 1
                    queue.append(v)

        return level

    def _dfs(self, u: int, sink: int, flow: int, level: List[int],
             iter_: List[int]) -> int:
        """DFS for blocking flow."""
        if u == sink:
            return flow

        while iter_[u] < len(self.graph[u]):
            idx = self.graph[u][iter_[u]]
            v, cap, rev_idx = self.edges[idx]

            if level[u] < level[v] and cap > 0:
                pushed = self._dfs(v, sink, min(flow, cap), level, iter_)
                if pushed > 0:
                    self.edges[idx][1] -= pushed
                    self.edges[self.graph[v][rev_idx]][1] += pushed
                    return pushed

            iter_[u] += 1

        return 0

    def max_flow(self, source: int, sink: int) -> int:
        """Compute maximum flow."""
        total_flow = 0

        while True:
            level = self._bfs(source, sink)
            if level[sink] == -1:
                break

            iter_ = [0] * self.V
            while True:
                flow = self._dfs(source, sink, float('inf'), level, iter_)
                if flow == 0:
                    break
                total_flow += flow

        return total_flow


class MinCostMaxFlow:
    """
    Minimum Cost Maximum Flow - Successive Shortest Paths

    Time: O(V * E * log V) with Dijkstra
    Space: O(V + E)
    """

    def __init__(self, vertices: int):
        self.V = vertices
        self.edges = []
        self.graph = [[] for _ in range(vertices)]

    def add_edge(self, u: int, v: int, capacity: int, cost: int):
        """Add edge with capacity and cost."""
        self.graph[u].append(len(self.edges))
        self.edges.append([v, capacity, cost])
        self.graph[v].append(len(self.edges))
        self.edges.append([u, 0, -cost])

    def min_cost_max_flow(self, source: int, sink: int) -> Tuple[int, int]:
        """Returns (max_flow, min_cost)."""
        max_flow = 0
        total_cost = 0
        h = [0] * self.V

        while True:
            # Find shortest path using Dijkstra with potentials
            dist = [float('inf')] * self.V
            dist[source] = 0
            parent = [-1] * self.V
            parent_edge = [-1] * self.V
            heap = [(0, source)]

            while heap:
                d, u = heapq.heappop(heap)
                if d > dist[u]:
                    continue

                for idx in self.graph[u]:
                    v, cap, cost = self.edges[idx]
                    if cap > 0 and dist[u] + cost + h[u] - h[v] < dist[v]:
                        dist[v] = dist[u] + cost + h[u] - h[v]
                        parent[v] = u
                        parent_edge[v] = idx
                        heapq.heappush(heap, (dist[v], v))

            if dist[sink] == float('inf'):
                break

            # Update potentials
            for v in range(self.V):
                if dist[v] != float('inf'):
                    h[v] += dist[v]

            # Find bottleneck capacity
            flow = float('inf')
            v = sink
            while v != source:
                idx = parent_edge[v]
                flow = min(flow, self.edges[idx][1])
                v = parent[v]

            # Push flow along path
            v = sink
            while v != source:
                idx = parent_edge[v]
                self.edges[idx][1] -= flow
                rev_idx = idx ^ 1
                self.edges[rev_idx][1] += flow
                total_cost += flow * self.edges[idx][2]
                v = parent[v]

            max_flow += flow

        return max_flow, total_cost


class BipartiteMatchingAugmenting:
    """
    Bipartite Matching - Augmenting Paths Method (Hungarian-like)

    Find maximum matching in bipartite graph.

    Time: O(V * E)
    Space: O(V)
    """

    def __init__(self, left_size: int, right_size: int):
        self.left = left_size
        self.right = right_size
        self.graph = [[] for _ in range(left_size)]

    def add_edge(self, u: int, v: int):
        """Add edge from left node u to right node v."""
        self.graph[u].append(v)

    def _dfs(self, u: int, match_r: List[int], match_l: List[int],
             visited: List[bool]) -> bool:
        """DFS to find augmenting path."""
        for v in self.graph[u]:
            if visited[v]:
                continue
            visited[v] = True

            if match_r[v] == -1 or self._dfs(match_r[v], match_r, match_l, visited):
                match_r[v] = u
                match_l[u] = v
                return True

        return False

    def max_matching(self) -> int:
        """Find maximum matching."""
        match_l = [-1] * self.left
        match_r = [-1] * self.right
        matching = 0

        for u in range(self.left):
            visited = [False] * self.right
            if self._dfs(u, match_r, match_l, visited):
                matching += 1

        return matching


class BipartiteMatchingHopcroftKarp:
    """
    Hopcroft-Karp Algorithm for Maximum Bipartite Matching

    Time: O(E * sqrt(V))
    Space: O(V)
    """

    def __init__(self, left_size: int, right_size: int):
        self.left = left_size
        self.right = right_size
        self.graph = [[] for _ in range(left_size)]
        self.match_l = [-1] * left_size
        self.match_r = [-1] * right_size
        self.dist = [0] * left_size

    def add_edge(self, u: int, v: int):
        """Add edge from left to right."""
        self.graph[u].append(v)

    def _bfs(self) -> bool:
        """BFS to assign distances."""
        queue = deque()
        for u in range(self.left):
            if self.match_l[u] == -1:
                self.dist[u] = 0
                queue.append(u)
            else:
                self.dist[u] = float('inf')

        self.dist_nil = float('inf')

        while queue:
            u = queue.popleft()
            if self.dist[u] < self.dist_nil:
                for v in self.graph[u]:
                    u_match = self.match_r[v]
                    if u_match == -1:
                        self.dist_nil = self.dist[u] + 1
                    elif self.dist[u_match] == float('inf'):
                        self.dist[u_match] = self.dist[u] + 1
                        queue.append(u_match)

        return self.dist_nil != float('inf')

    def _dfs(self, u: int) -> bool:
        """DFS to find augmenting path."""
        if u != -1:
            for v in self.graph[u]:
                u_match = self.match_r[v]
                if (u_match == -1 and self.dist[u] + 1 == self.dist_nil) or \
                   (u_match != -1 and self.dist[u] + 1 == self.dist[u_match] and
                    self._dfs(u_match)):
                    self.match_r[v] = u
                    self.match_l[u] = v
                    return True
            self.dist[u] = float('inf')
            return False
        return True

    def max_matching(self) -> int:
        """Find maximum matching using Hopcroft-Karp."""
        matching = 0
        while self._bfs():
            for u in range(self.left):
                if self.match_l[u] == -1 and self._dfs(u):
                    matching += 1
        return matching


class TwoSAT:
    """
    2-SAT - Satisfiability Problem Solver using SCC

    Determines if a 2-CNF formula is satisfiable and finds assignment.

    Time: O(V + E)
    Space: O(V + E)
    """

    def __init__(self, variables: int):
        self.n = variables
        self.graph = [[] for _ in range(2 * variables)]
        self.rev_graph = [[] for _ in range(2 * variables)]

    def add_clause(self, a: int, neg_a: bool, b: int, neg_b: bool):
        """
        Add clause (a OR b).
        If neg_a=True, clause is (NOT a OR b).
        """
        # (a OR b) = (NOT a -> b) AND (NOT b -> a)
        a_node = 2 * a + (1 if neg_a else 0)
        not_a_node = 2 * a + (0 if neg_a else 1)
        b_node = 2 * b + (1 if neg_b else 0)
        not_b_node = 2 * b + (0 if neg_b else 1)

        self.graph[not_a_node].append(b_node)
        self.graph[not_b_node].append(a_node)
        self.rev_graph[b_node].append(not_a_node)
        self.rev_graph[a_node].append(not_b_node)

    def _kosaraju_scc(self):
        """Find SCCs using Kosaraju's algorithm."""
        visited = [False] * (2 * self.n)
        order = []

        def dfs1(v: int):
            visited[v] = True
            for u in self.graph[v]:
                if not visited[u]:
                    dfs1(u)
            order.append(v)

        for i in range(2 * self.n):
            if not visited[i]:
                dfs1(i)

        visited = [False] * (2 * self.n)
        scc_id = [-1] * (2 * self.n)
        scc_count = [0]

        def dfs2(v: int):
            visited[v] = True
            scc_id[v] = scc_count[0]
            for u in self.rev_graph[v]:
                if not visited[u]:
                    dfs2(u)

        for v in reversed(order):
            if not visited[v]:
                dfs2(v)
                scc_count[0] += 1

        return scc_id

    def is_satisfiable(self) -> Tuple[bool, List[bool]]:
        """Check if formula is satisfiable. Returns (is_sat, assignment)."""
        scc_id = self._kosaraju_scc()

        # Variable i is satisfiable if SCC(i) != SCC(NOT i)
        for i in range(self.n):
            if scc_id[2 * i] == scc_id[2 * i + 1]:
                return False, []

        # Build assignment: pick the one with larger SCC id
        assignment = [scc_id[2 * i + 1] > scc_id[2 * i] for i in range(self.n)]
        return True, assignment


class ArticulationPointsBridges:
    """
    Articulation Points & Bridges - Find cut vertices and edges

    Time: O(V + E)
    Space: O(V + E)
    """

    def __init__(self, vertices: int):
        self.V = vertices
        self.graph = [[] for _ in range(vertices)]
        self.visited = [False] * vertices
        self.disc = [0] * vertices
        self.low = [0] * vertices
        self.parent = [-1] * vertices
        self.time = [0]
        self.articulation_points = set()
        self.bridges = []

    def add_edge(self, u: int, v: int):
        """Add undirected edge."""
        self.graph[u].append(v)
        self.graph[v].append(u)

    def _dfs(self, u: int):
        """DFS to find articulation points and bridges."""
        self.visited[u] = True
        self.disc[u] = self.low[u] = self.time[0]
        self.time[0] += 1
        children = 0

        for v in self.graph[u]:
            if not self.visited[v]:
                children += 1
                self.parent[v] = u
                self._dfs(v)
                self.low[u] = min(self.low[u], self.low[v])

                # Check if u is articulation point
                if (self.parent[u] == -1 and children > 1) or \
                   (self.parent[u] != -1 and self.low[v] >= self.disc[u]):
                    self.articulation_points.add(u)

                # Check if u-v is a bridge
                if self.low[v] > self.disc[u]:
                    self.bridges.append((u, v))

            elif v != self.parent[u]:
                self.low[u] = min(self.low[u], self.disc[v])

    def find(self) -> Tuple[Set[int], List[Tuple[int, int]]]:
        """Find and return articulation points and bridges."""
        for i in range(self.V):
            if not self.visited[i]:
                self._dfs(i)

        return self.articulation_points, self.bridges


class VertexConnectivity:
    """
    Vertex Connectivity - Find minimum vertex cut

    Time: O(V² * flow)
    Space: O(V + E)
    """

    @staticmethod
    def min_vertex_cut(adj: List[List[int]]) -> int:
        """
        Find minimum number of vertices to remove to disconnect graph.
        Uses max flow approach with vertex splitting.
        """
        n = len(adj)
        if n <= 2:
            return 0

        # Build flow network with vertex splitting
        flow_graph = MaxFlowDinic(2 * n)

        for u in range(n):
            # Split vertex: in-edge to out-edge
            flow_graph.add_edge(2 * u, 2 * u + 1, 1)

            for v in adj[u]:
                if u != v:
                    # Edge from u_out to v_in
                    flow_graph.add_edge(2 * u + 1, 2 * v, float('inf'))

        # Find min cut from 0_out to 1_in
        return flow_graph.max_flow(1, 2)


class TransitiveClosure:
    """
    Transitive Closure - Floyd-Warshall for Reachability

    Compute reachability matrix: closure[i][j] = True if j reachable from i

    Time: O(V³)
    Space: O(V²)
    """

    @staticmethod
    def compute_closure(adj: List[List[int]]) -> List[List[bool]]:
        """Compute transitive closure of adjacency list."""
        n = len(adj)
        closure = [[False] * n for _ in range(n)]

        # Initialize with direct edges
        for u in range(n):
            closure[u][u] = True
            for v in adj[u]:
                closure[u][v] = True

        # Floyd-Warshall for reachability
        for k in range(n):
            for i in range(n):
                for j in range(n):
                    closure[i][j] = closure[i][j] or (closure[i][k] and closure[k][j])

        return closure


# ============================================================================
# STRING ALGORITHMS - ADVANCED
# ============================================================================

class BoyerMoore:
    """
    Boyer-Moore String Matching - Efficient pattern search

    Time: O(n/m) best case, O(nm) worst case (but usually fast in practice)
    Space: O(σ) where σ is alphabet size
    """

    def __init__(self, pattern: str):
        self.pattern = pattern
        self.m = len(pattern)
        self.bad_char = self._build_bad_char_table()

    def _build_bad_char_table(self) -> Dict[str, int]:
        """Build bad character table: rightmost occurrence of each char."""
        table = {}
        for i, char in enumerate(self.pattern):
            table[char] = i
        return table

    def search(self, text: str) -> List[int]:
        """Find all occurrences of pattern in text using only bad character shift."""
        n = len(text)
        matches = []
        i = 0

        while i <= n - self.m:
            j = self.m - 1

            # Compare from right to left
            while j >= 0 and text[i + j] == self.pattern[j]:
                j -= 1

            if j < 0:
                # Pattern found
                matches.append(i)
                i += 1
            else:
                # Mismatch: shift using bad character rule
                # bad_char[ch] is the rightmost position of ch in pattern
                bad_char_pos = self.bad_char.get(text[i + j], -1)
                # Shift by at least 1, or by the distance from mismatch
                shift = max(1, j - bad_char_pos)
                i += shift

        return matches


class AhoCorasick:
    """
    Aho-Corasick Automaton - Multi-pattern Matching

    Find all occurrences of multiple patterns efficiently.

    Time: O(n + z) where n = text length, z = number of matches
    Space: O(m * σ) where m = sum of pattern lengths, σ = alphabet
    """

    def __init__(self):
        self.trie = {}
        self.go_to = [{}]
        self.fail = [0]
        self.output = [[]]
        self.node_count = 1

    def add_pattern(self, pattern: str):
        """Add pattern to automaton."""
        node = 0
        for char in pattern:
            if char not in self.go_to[node]:
                self.go_to[node][char] = self.node_count
                self.go_to.append({})
                self.fail.append(0)
                self.output.append([])
                self.node_count += 1
            node = self.go_to[node][char]
        self.output[node].append(pattern)

    def build(self):
        """Build failure links."""
        queue = deque()

        for char in self.go_to[0]:
            queue.append(self.go_to[0][char])

        while queue:
            state = queue.popleft()

            for char in self.go_to[state]:
                next_state = self.go_to[state][char]
                queue.append(next_state)

                fail = self.fail[state]
                while fail > 0 and char not in self.go_to[fail]:
                    fail = self.fail[fail]

                self.fail[next_state] = self.go_to[fail].get(char, 0)
                self.output[next_state].extend(self.output[self.fail[next_state]])

    def search(self, text: str) -> List[Tuple[int, str]]:
        """Find all pattern occurrences."""
        matches = []
        state = 0

        for i, char in enumerate(text):
            while state > 0 and char not in self.go_to[state]:
                state = self.fail[state]

            state = self.go_to[state].get(char, 0)
            for pattern in self.output[state]:
                matches.append((i - len(pattern) + 1, pattern))

        return matches


class SuffixArray:
    """
    Suffix Array with LCP Array - String Indexing

    Build suffix array and LCP array for pattern searching and analysis.

    Time: O(n log² n) with simple sorting, O(n) with advanced methods
    Space: O(n)
    """

    def __init__(self, text: str):
        self.text = text + '$'
        self.n = len(self.text)
        self.sa = self._build_suffix_array()
        self.lcp = self._build_lcp_array()

    def _build_suffix_array(self) -> List[int]:
        """Build suffix array using simple sorting."""
        suffixes = [(self.text[i:], i) for i in range(self.n)]
        suffixes.sort()
        return [idx for _, idx in suffixes]

    def _build_lcp_array(self) -> List[int]:
        """Build LCP (Longest Common Prefix) array."""
        n = self.n
        lcp = [0] * n
        rank = [0] * n

        for i, sa_idx in enumerate(self.sa):
            rank[sa_idx] = i

        h = 0
        for i in range(n):
            if rank[i] > 0:
                j = self.sa[rank[i] - 1]
                while i + h < n and j + h < n and self.text[i + h] == self.text[j + h]:
                    h += 1
                lcp[rank[i]] = h
                if h > 0:
                    h -= 1

        return lcp

    def pattern_search(self, pattern: str) -> List[int]:
        """Find all occurrences of pattern."""
        matches = []
        left, right = 0, self.n - 1

        # Binary search for leftmost occurrence
        while left < right:
            mid = (left + right) // 2
            suffix = self.text[self.sa[mid]:]
            if suffix < pattern:
                left = mid + 1
            else:
                right = mid

        # Collect all matches
        while left < self.n:
            suffix = self.text[self.sa[left]:]
            if not suffix.startswith(pattern):
                break
            matches.append(self.sa[left])
            left += 1

        return sorted(matches)


class Manacher:
    """
    Manacher's Algorithm - Find longest palindromic substring

    Time: O(n)
    Space: O(n)
    """

    @staticmethod
    def longest_palindrome(s: str) -> str:
        """Find longest palindromic substring using Manacher's algorithm."""
        if not s:
            return ""

        # Expand string with separators: "abc" -> "#a#b#c#"
        expanded = '#'.join('^{}$'.format(s))
        n = len(expanded)
        p = [0] * n
        center = 0
        right = 0

        for i in range(1, n - 1):
            mirror = 2 * center - i

            if i < right:
                p[i] = min(right - i, p[mirror])

            # Expand around center
            while expanded[i + p[i] + 1] == expanded[i - p[i] - 1]:
                p[i] += 1

            if i + p[i] > right:
                center, right = i, i + p[i]

        # Find the longest palindrome
        max_len, center_idx = 0, 0
        for i in range(1, n - 1):
            if p[i] > max_len:
                max_len = p[i]
                center_idx = i

        # Extract original string
        start = (center_idx - max_len) // 2
        return s[start:start + max_len]


class ZAlgorithm:
    """
    Z-Algorithm - Pattern matching with prefix function

    Time: O(n + m)
    Space: O(n + m)
    """

    @staticmethod
    def compute_z_array(s: str) -> List[int]:
        """Compute Z-array where z[i] = length of longest substring starting at i matching prefix."""
        n = len(s)
        z = [0] * n
        z[0] = n
        l, r = 0, 0

        for i in range(1, n):
            if i > r:
                l, r = i, i
                while r < n and s[r - l] == s[r]:
                    r += 1
                z[i] = r - l
                r -= 1
            else:
                k = i - l
                if z[k] < r - i + 1:
                    z[i] = z[k]
                else:
                    l = i
                    while r < n and s[r - l] == s[r]:
                        r += 1
                    z[i] = r - l
                    r -= 1

        return z

    @staticmethod
    def pattern_search(pattern: str, text: str) -> List[int]:
        """Find pattern in text using Z-algorithm."""
        combined = pattern + '$' + text
        z = ZAlgorithm.compute_z_array(combined)
        matches = []

        for i in range(len(pattern) + 1, len(combined)):
            if z[i] == len(pattern):
                matches.append(i - len(pattern) - 1)

        return matches


# ============================================================================
# COMPUTATIONAL GEOMETRY
# ============================================================================

class ConvexHullGrahamScan:
    """
    Convex Hull - Graham Scan Algorithm

    Time: O(n log n)
    Space: O(n)
    """

    @staticmethod
    def _cross_product(o: Tuple[float, float], a: Tuple[float, float],
                       b: Tuple[float, float]) -> float:
        """Compute cross product of vectors OA and OB."""
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    @staticmethod
    def convex_hull(points: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        """Compute convex hull using Graham Scan."""
        points = sorted(set(points))
        if len(points) <= 1:
            return points

        # Build lower hull
        lower = []
        for p in points:
            while len(lower) >= 2 and ConvexHullGrahamScan._cross_product(
                lower[-2], lower[-1], p) <= 0:
                lower.pop()
            lower.append(p)

        # Build upper hull
        upper = []
        for p in reversed(points):
            while len(upper) >= 2 and ConvexHullGrahamScan._cross_product(
                upper[-2], upper[-1], p) <= 0:
                upper.pop()
            upper.append(p)

        return lower[:-1] + upper[:-1]


class ConvexHullAndrewChain:
    """
    Convex Hull - Andrew's Monotone Chain Algorithm

    Time: O(n log n)
    Space: O(n)
    """

    @staticmethod
    def _cross_product(o: Tuple[float, float], a: Tuple[float, float],
                       b: Tuple[float, float]) -> float:
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    @staticmethod
    def convex_hull(points: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        """Compute convex hull using Andrew's Monotone Chain."""
        points = sorted(set(points))

        if len(points) <= 2:
            return points

        def build_half_hull(point_list):
            hull = []
            for p in point_list:
                while len(hull) >= 2 and \
                      ConvexHullAndrewChain._cross_product(hull[-2], hull[-1], p) <= 0:
                    hull.pop()
                hull.append(p)
            return hull

        lower = build_half_hull(points)
        upper = build_half_hull(reversed(points))

        return lower[:-1] + upper[:-1]


class ClosestPair:
    """
    Closest Pair of Points - Divide & Conquer

    Time: O(n log n)
    Space: O(n)
    """

    @staticmethod
    def _distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        """Euclidean distance."""
        return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

    @staticmethod
    def _closest_brute_force(points: List[Tuple[float, float]]) -> float:
        """Find closest pair in small set by brute force."""
        min_dist = float('inf')
        for i in range(len(points)):
            for j in range(i + 1, len(points)):
                min_dist = min(min_dist, ClosestPair._distance(points[i], points[j]))
        return min_dist

    @staticmethod
    def closest_pair(points: List[Tuple[float, float]]) -> float:
        """Find minimum distance between any two points."""

        def divide_conquer(px, py):
            n = len(px)
            if n <= 3:
                return ClosestPair._closest_brute_force(px)

            mid = n // 2
            midpoint = px[mid]

            pyl = [p for p in py if p[0] <= midpoint[0]]
            pyr = [p for p in py if p[0] > midpoint[0]]

            dl = divide_conquer(px[:mid], pyl)
            dr = divide_conquer(px[mid:], pyr)

            d = min(dl, dr)

            # Check points near dividing line
            strip = [p for p in py if abs(p[0] - midpoint[0]) < d]
            for i in range(len(strip)):
                for j in range(i + 1, min(i + 7, len(strip))):
                    d = min(d, ClosestPair._distance(strip[i], strip[j]))

            return d

        px = sorted(points, key=lambda p: p[0])
        py = sorted(points, key=lambda p: p[1])
        return divide_conquer(px, py)


class LineIntersection:
    """
    Line Segment Intersection Detection

    Check if two line segments intersect.

    Time: O(1)
    Space: O(1)
    """

    @staticmethod
    def _orientation(p: Tuple[float, float], q: Tuple[float, float],
                     r: Tuple[float, float]) -> int:
        """Find orientation of ordered triplet (p, q, r).
        Returns: 0 if collinear, 1 if clockwise, 2 if counterclockwise
        """
        val = (q[1] - p[1]) * (r[0] - q[0]) - (q[0] - p[0]) * (r[1] - q[1])
        if val == 0:
            return 0
        return 1 if val > 0 else 2

    @staticmethod
    def _on_segment(p: Tuple[float, float], q: Tuple[float, float],
                    r: Tuple[float, float]) -> bool:
        """Check if point q lies on segment pr (given collinearity)."""
        return (min(p[0], r[0]) <= q[0] <= max(p[0], r[0]) and
                min(p[1], r[1]) <= q[1] <= max(p[1], r[1]))

    @staticmethod
    def segments_intersect(p1: Tuple[float, float], q1: Tuple[float, float],
                          p2: Tuple[float, float], q2: Tuple[float, float]) -> bool:
        """Check if segment p1q1 and p2q2 intersect."""
        o1 = LineIntersection._orientation(p1, q1, p2)
        o2 = LineIntersection._orientation(p1, q1, q2)
        o3 = LineIntersection._orientation(p2, q2, p1)
        o4 = LineIntersection._orientation(p2, q2, q1)

        # General case
        if o1 != o2 and o3 != o4:
            return True

        # Special cases for collinear points
        if o1 == 0 and LineIntersection._on_segment(p1, p2, q1):
            return True
        if o2 == 0 and LineIntersection._on_segment(p1, q2, q1):
            return True
        if o3 == 0 and LineIntersection._on_segment(p2, p1, q2):
            return True
        if o4 == 0 and LineIntersection._on_segment(p2, q1, q2):
            return True

        return False


class PointInPolygon:
    """
    Point-in-Polygon - Ray Casting Algorithm

    Time: O(n)
    Space: O(1)
    """

    @staticmethod
    def point_in_polygon(point: Tuple[float, float],
                        polygon: List[Tuple[float, float]]) -> bool:
        """Check if point is inside polygon using ray casting."""
        x, y = point
        n = len(polygon)
        inside = False

        p1x, p1y = polygon[0]
        for i in range(1, n + 1):
            p2x, p2y = polygon[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y

        return inside


# ============================================================================
# TREE ALGORITHMS
# ============================================================================

class HeavyLightDecomposition:
    """
    Heavy-Light Decomposition - Path queries on trees

    Decompose tree into heavy and light chains for efficient path queries.

    Time: O(n log n) preprocessing, O(log² n) per query
    Space: O(n)
    """

    def __init__(self, n: int, adj: List[List[int]]):
        self.n = n
        self.adj = adj
        self.parent = [-1] * n
        self.depth = [0] * n
        self.size = [0] * n
        self.heavy_child = [-1] * n
        self.chain_head = [0] * n
        self.position = [0] * n
        self.chains = []

        self._dfs1(0, -1)
        self._dfs2(0, -1, 0)

    def _dfs1(self, u: int, p: int):
        """First DFS: compute subtree sizes and find heavy children."""
        self.parent[u] = p
        self.size[u] = 1
        max_size = -1

        for v in self.adj[u]:
            if v != p:
                self.depth[v] = self.depth[u] + 1
                self._dfs1(v, u)
                self.size[u] += self.size[v]

                if self.size[v] > max_size:
                    max_size = self.size[v]
                    self.heavy_child[u] = v

    def _dfs2(self, u: int, p: int, chain_id: int):
        """Second DFS: assign chain positions."""
        self.chain_head[u] = chain_id

        # Ensure chain_id has enough space
        while chain_id >= len(self.chains):
            self.chains.append([])

        pos = len(self.chains[chain_id])
        self.chains[chain_id].append(u)
        self.position[u] = pos

        # Continue heavy child on same chain
        if self.heavy_child[u] != -1:
            self._dfs2(self.heavy_child[u], u, chain_id)

        # Light children start new chains
        for v in self.adj[u]:
            if v != p and v != self.heavy_child[u]:
                self._dfs2(v, u, len(self.chains))

    def get_path(self, u: int, v: int) -> List[int]:
        """Get path from u to v."""
        path = []

        while self.chain_head[u] != self.chain_head[v]:
            if self.depth[self.chain_head[u]] > self.depth[self.chain_head[v]]:
                # Move u up
                chain_id = self.chain_head[u]
                path.extend(self.chains[chain_id][:self.position[u] + 1])
                u = self.parent[self.chain_head[u]]
            else:
                # Move v up
                chain_id = self.chain_head[v]
                path.extend(reversed(self.chains[chain_id][:self.position[v] + 1]))
                v = self.parent[self.chain_head[v]]

        # Both on same chain
        if self.position[u] <= self.position[v]:
            path.extend(self.chains[self.chain_head[u]][self.position[u]:self.position[v] + 1])
        else:
            path.extend(reversed(self.chains[self.chain_head[u]][self.position[v]:self.position[u] + 1]))

        return path


class SquareRootDecomposition:
    """
    Square Root Decomposition - Range query/update optimization

    Decompose array into sqrt(n) blocks for O(sqrt(n)) queries/updates.

    Time: O(sqrt(n)) per query/update
    Space: O(n)
    """

    def __init__(self, arr: List[int]):
        self.arr = arr
        self.n = len(arr)
        self.block_size = int(math.sqrt(self.n)) + 1
        self.blocks = [0] * ((self.n + self.block_size - 1) // self.block_size)
        self._build()

    def _build(self):
        """Build block sums."""
        for i in range(self.n):
            block_id = i // self.block_size
            self.blocks[block_id] += self.arr[i]

    def update(self, idx: int, value: int):
        """Update arr[idx] to new value."""
        block_id = idx // self.block_size
        self.blocks[block_id] -= self.arr[idx]
        self.arr[idx] = value
        self.blocks[block_id] += value

    def range_sum(self, left: int, right: int) -> int:
        """Query sum in range [left, right]."""
        result = 0

        while left <= right:
            block_id = left // self.block_size
            # If we can cover the whole block, add block sum
            if left % self.block_size == 0 and left + self.block_size - 1 <= right:
                result += self.blocks[block_id]
                left += self.block_size
            else:
                result += self.arr[left]
                left += 1

        return result


class MosAlgorithm:
    """
    Mo's Algorithm - Offline range query optimization

    For offline queries, reorder them to minimize total pointer movement.

    Time: O((n + q) * sqrt(n))
    Space: O(n + q)
    """

    def __init__(self, arr: List[int], queries: List[Tuple[int, int]]):
        self.arr = arr
        self.queries = queries
        self.block_size = int(math.sqrt(len(arr))) + 1

    def solve(self, process_query: Callable) -> List:
        """
        Solve queries using Mo's algorithm.
        process_query(l, r) should return answer for range [l, r].
        """
        # Sort queries by block
        indexed_queries = [(i, l, r) for i, (l, r) in enumerate(self.queries)]
        indexed_queries.sort(key=lambda x: (x[1] // self.block_size, x[2]))

        results = [0] * len(self.queries)
        current_l = 0
        current_r = -1

        for idx, l, r in indexed_queries:
            # Expand/contract window
            while current_r < r:
                current_r += 1
                # Add arr[current_r]
            while current_r > r:
                # Remove arr[current_r]
                current_r -= 1
            while current_l < l:
                # Remove arr[current_l]
                current_l += 1
            while current_l > l:
                current_l -= 1
                # Add arr[current_l]

            results[idx] = process_query(current_l, current_r)

        return results


# ============================================================================
# MISCELLANEOUS ADVANCED ALGORITHMS
# ============================================================================

class BoyerMooreVoting:
    """
    Boyer-Moore Majority Vote Algorithm - Find majority element(s)

    Find element(s) appearing more than n/k times in array.

    Time: O(n)
    Space: O(k)
    """

    @staticmethod
    def find_majority_element(arr: List[int]) -> List[int]:
        """Find all elements appearing more than n/2 times."""
        if not arr:
            return []

        candidate = None
        count = 0

        # Phase 1: Find candidate
        for num in arr:
            if count == 0:
                candidate = num
                count = 1
            elif num == candidate:
                count += 1
            else:
                count -= 1

        # Phase 2: Verify candidate
        count = 0
        for num in arr:
            if num == candidate:
                count += 1

        if count > len(arr) // 2:
            return [candidate]
        return []

    @staticmethod
    def find_top_k_frequent(arr: List[int], k: int) -> List[int]:
        """Find all k elements appearing more than n/(k+1) times."""
        if not arr or k == 0:
            return []

        # Phase 1: Find up to k candidates
        candidates = {}
        count_arr = {}

        for num in arr:
            if num in candidates:
                count_arr[num] += 1
            elif len(candidates) < k:
                candidates[num] = True
                count_arr[num] = 1
            else:
                # Reduce all counts by 1
                for c in list(candidates.keys()):
                    count_arr[c] -= 1
                    if count_arr[c] == 0:
                        del candidates[c]
                        del count_arr[c]

                count_arr[num] = 1
                candidates[num] = True

        # Phase 2: Verify candidates
        result = []
        threshold = len(arr) // (k + 1)

        for candidate in candidates:
            count = sum(1 for num in arr if num == candidate)
            if count > threshold:
                result.append(candidate)

        return result


class QuickSelect:
    """
    QuickSelect - Find k-th smallest element in O(n) average time

    Time: O(n) average, O(n²) worst case
    Space: O(log n) with randomization
    """

    @staticmethod
    def quickselect(arr: List[int], k: int) -> int:
        """Find k-th smallest element (0-indexed)."""

        def partition(left: int, right: int, pivot_idx: int) -> int:
            pivot_value = arr[pivot_idx]
            arr[pivot_idx], arr[right] = arr[right], arr[pivot_idx]
            store_idx = left

            for i in range(left, right):
                if arr[i] < pivot_value:
                    arr[i], arr[store_idx] = arr[store_idx], arr[i]
                    store_idx += 1

            arr[right], arr[store_idx] = arr[store_idx], arr[right]
            return store_idx

        def select(left: int, right: int, k_idx: int) -> int:
            if left == right:
                return arr[left]

            pivot_idx = left + (right - left) // 2
            pivot_idx = partition(left, right, pivot_idx)

            if k_idx == pivot_idx:
                return arr[k_idx]
            elif k_idx < pivot_idx:
                return select(left, pivot_idx - 1, k_idx)
            else:
                return select(pivot_idx + 1, right, k_idx)

        return select(0, len(arr) - 1, k)


class HuffmanCoding:
    """
    Huffman Coding - Optimal prefix-free code generation

    Time: O(n log n)
    Space: O(n)
    """

    class Node:
        def __init__(self, char=None, freq=0, left=None, right=None):
            self.char = char
            self.freq = freq
            self.left = left
            self.right = right

        def __lt__(self, other):
            return self.freq < other.freq

    @staticmethod
    def build_codes(frequencies: Dict[str, int]) -> Dict[str, str]:
        """Build Huffman codes from character frequencies."""
        if not frequencies:
            return {}

        heap = [HuffmanCoding.Node(char=char, freq=freq)
                for char, freq in frequencies.items()]
        heapq.heapify(heap)

        while len(heap) > 1:
            left = heapq.heappop(heap)
            right = heapq.heappop(heap)

            parent = HuffmanCoding.Node(
                char=None,
                freq=left.freq + right.freq,
                left=left,
                right=right
            )
            heapq.heappush(heap, parent)

        root = heap[0]
        codes = {}

        def generate_codes(node: HuffmanCoding.Node, code: str):
            if node.char is not None:
                codes[node.char] = code if code else '0'
                return
            generate_codes(node.left, code + '0')
            generate_codes(node.right, code + '1')

        generate_codes(root, '')
        return codes


class ActivitySelection:
    """
    Activity Selection / Interval Scheduling - Greedy Optimal

    Select maximum non-overlapping activities using greedy approach.

    Time: O(n log n)
    Space: O(n)
    """

    @staticmethod
    def max_activities(activities: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """
        Select maximum non-overlapping activities.
        activities: list of (start_time, end_time) tuples
        """
        # Sort by end time
        sorted_activities = sorted(activities, key=lambda x: x[1])

        selected = []
        last_end = -1

        for start, end in sorted_activities:
            if start >= last_end:
                selected.append((start, end))
                last_end = end

        return selected


# ============================================================================
# DEMO / TESTING
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("ADVANCED ALGORITHMS DEMO")
    print("=" * 70)

    # 1. Convex Hull Trick
    print("\n1. CONVEX HULL TRICK")
    print("-" * 70)
    ConvexHullTrick.solve_example()
    print("✓ CHT example solved")

    # 2. Digit DP
    print("\n2. DIGIT DP - Count numbers with specific properties")
    print("-" * 70)
    count = DigitDP.count_numbers_no_consecutive_ones(15)
    print(f"Numbers in [0, 15] with no consecutive 1s in binary: {count}")

    # 3. Max Flow Dinic
    print("\n3. MAX FLOW - Dinic's Algorithm")
    print("-" * 70)
    flow = MaxFlowDinic(6)
    flow.add_edge(0, 1, 16)
    flow.add_edge(0, 2, 13)
    flow.add_edge(1, 2, 10)
    flow.add_edge(1, 3, 12)
    flow.add_edge(2, 1, 9)
    flow.add_edge(2, 4, 14)
    flow.add_edge(3, 2, 9)
    flow.add_edge(3, 5, 20)
    flow.add_edge(4, 3, 7)
    flow.add_edge(4, 5, 4)
    max_flow_value = flow.max_flow(0, 5)
    print(f"Maximum flow from 0 to 5: {max_flow_value}")

    # 4. 2-SAT
    print("\n4. 2-SAT")
    print("-" * 70)
    sat = TwoSAT(3)
    sat.add_clause(0, False, 1, False)  # (x0 OR x1)
    sat.add_clause(1, False, 2, False)  # (x1 OR x2)
    sat.add_clause(2, True, 0, True)    # (NOT x2 OR NOT x0)
    is_sat, assignment = sat.is_satisfiable()
    print(f"Is satisfiable: {is_sat}")
    if is_sat:
        print(f"Assignment: {assignment}")

    # 5. Boyer-Moore
    print("\n5. BOYER-MOORE STRING MATCHING")
    print("-" * 70)
    bm = BoyerMoore("PATTERN")
    text = "THIS IS A PATTERN MATCHING PATTERN ALGORITHM"
    matches = bm.search(text)
    print(f"Text: {text}")
    print(f"Pattern: PATTERN")
    print(f"Matches at positions: {matches}")

    # 6. Aho-Corasick
    print("\n6. AHO-CORASICK MULTI-PATTERN MATCHING")
    print("-" * 70)
    ac = AhoCorasick()
    ac.add_pattern("he")
    ac.add_pattern("she")
    ac.add_pattern("his")
    ac.add_pattern("hers")
    ac.build()
    text = "ushers"
    matches = ac.search(text)
    print(f"Text: {text}")
    print(f"Patterns found: {[(pos, pat) for pos, pat in matches]}")

    # 7. Convex Hull
    print("\n7. CONVEX HULL - Graham Scan")
    print("-" * 70)
    points = [(0, 0), (1, 1), (2, 2), (0, 2), (2, 0), (1, 0.5)]
    hull = ConvexHullGrahamScan.convex_hull(points)
    print(f"Points: {points}")
    print(f"Convex hull: {hull}")

    # 8. Closest Pair
    print("\n8. CLOSEST PAIR")
    print("-" * 70)
    points = [(2, 3), (12, 30), (40, 50), (5, 1), (12, 10)]
    min_dist = ClosestPair.closest_pair(points)
    print(f"Points: {points}")
    print(f"Minimum distance: {min_dist:.4f}")

    # 9. Heavy-Light Decomposition
    print("\n9. HEAVY-LIGHT DECOMPOSITION")
    print("-" * 70)
    adj = [
        [1, 2],      # 0 -> 1, 2
        [0, 3, 4],   # 1 -> 0, 3, 4
        [0],         # 2 -> 0
        [1],         # 3 -> 1
        [1]          # 4 -> 1
    ]
    hld = HeavyLightDecomposition(5, adj)
    path = hld.get_path(3, 4)
    print(f"Path from 3 to 4: {path}")

    # 10. Square Root Decomposition
    print("\n10. SQUARE ROOT DECOMPOSITION")
    print("-" * 70)
    arr = [1, 3, 5, 7, 9, 11]
    sqrt_decomp = SquareRootDecomposition(arr)
    print(f"Array: {arr}")
    print(f"Range sum [1, 4]: {sqrt_decomp.range_sum(1, 4)}")
    sqrt_decomp.update(2, 10)
    print(f"After update arr[2] = 10")
    print(f"Range sum [1, 4]: {sqrt_decomp.range_sum(1, 4)}")

    # 11. Activity Selection
    print("\n11. ACTIVITY SELECTION")
    print("-" * 70)
    activities = [(1, 3), (2, 4), (3, 5), (4, 6), (5, 7), (6, 8)]
    selected = ActivitySelection.max_activities(activities)
    print(f"Activities: {activities}")
    print(f"Maximum non-overlapping: {selected}")

    # 12. BOYER-MOORE MAJORITY VOTE
    print("\n12. BOYER-MOORE MAJORITY VOTE ALGORITHM")
    print("-" * 70)
    arr = [3, 3, 4, 2, 4, 4, 2, 4, 4]
    majority = BoyerMooreVoting.find_majority_element(arr)
    print(f"Array: {arr}")
    print(f"Majority element (>n/2): {majority}")
    top_k = BoyerMooreVoting.find_top_k_frequent([1, 1, 1, 2, 2, 3], k=2)
    print(f"Top k=2 frequent (>n/3): {top_k}")

    # 13. QuickSelect
    print("\n13. QUICKSELECT - Find k-th smallest")
    print("-" * 70)
    arr = [3, 2, 1, 5, 4]
    k = 2
    result = QuickSelect.quickselect(arr[:], k)
    print(f"Array: {[3, 2, 1, 5, 4]}")
    print(f"{k}-th smallest element (0-indexed): {result}")

    # 14. Huffman Coding
    print("\n14. HUFFMAN CODING")
    print("-" * 70)
    frequencies = {'a': 5, 'b': 9, 'c': 12, 'd': 13, 'e': 16, 'f': 45}
    codes = HuffmanCoding.build_codes(frequencies)
    print(f"Frequencies: {frequencies}")
    print(f"Huffman codes: {codes}")

    # 15. Z-Algorithm
    print("\n15. Z-ALGORITHM")
    print("-" * 70)
    pattern = "aab"
    text = "aabaaab"
    combined = pattern + "$" + text
    z_array = ZAlgorithm.compute_z_array(combined)
    matches = ZAlgorithm.pattern_search(pattern, text)
    print(f"Pattern: {pattern}")
    print(f"Text: {text}")
    print(f"Matches at: {matches}")

    print("\n" + "=" * 70)
    print("All demos completed successfully!")
    print("=" * 70)
