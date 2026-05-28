# Graph Algorithms — Advanced

**Level:** L5
**Time to read:** ~30 min

Dijkstra, Bellman-Ford, A*, Floyd-Warshall, and Minimum Spanning Trees (Kruskal + Prim). These appear in L5+ interviews and system design discussions on routing, network topology, and cost optimization.

> Prerequisites: BFS/DFS fundamentals — see `docs/05-algorithms/graphs/`.

---

## Comparative Trade-off Table

| Algorithm | Use case | Time | Space | Negative weights? | All pairs? |
|-----------|---------|------|-------|------------------|----------|
| Dijkstra | Single-source shortest path, non-negative weights | O((V+E) log V) | O(V) | No | No |
| Bellman-Ford | Single-source, negative weights OK | O(VE) | O(V) | Yes (detects neg cycle) | No |
| A* | Single-target with domain heuristic | O(b^d) | O(b^d) | No | No |
| Floyd-Warshall | All-pairs shortest path | O(V³) | O(V²) | Yes | Yes |
| Kruskal (MST) | Minimum spanning tree, sparse graphs | O(E log E) | O(V) | N/A (costs) | N/A |
| Prim (MST) | Minimum spanning tree, dense graphs | O(E log V) | O(V) | N/A (costs) | N/A |

**b** = branching factor, **d** = depth to goal (A* worst case).

### Decision Framework

```
Single source shortest path?
  Weights all non-negative?
    YES → Dijkstra: O((V+E) log V), fastest for sparse graphs
    NO  → Bellman-Ford: O(VE), handles negative edges + detects cycles

Need to go to a specific target with spatial intuition?
  → A* with admissible heuristic (e.g., Euclidean distance)

All-pairs shortest path?
  Graph is small (V ≤ 500)?
    YES → Floyd-Warshall: O(V³) simple DP
    NO  → Run Dijkstra from every node: O(V × (V+E) log V)

Minimum spanning tree?
  Sparse graph (E ≈ V)?
    YES → Kruskal: sort edges O(E log E), union-find per edge
  Dense graph (E ≈ V²)?
    YES → Prim with min-heap: O(E log V), similar to Dijkstra
```

---

## Algorithm Implementations

### Dijkstra's Algorithm

Greedy: always expand the unvisited node with smallest known distance. Uses a min-heap (priority queue) to select the next node in O(log V). Cannot handle negative edges — a shorter path might be discovered later but the greedy choice has already committed.

**Complexity:** Time O((V+E) log V) | Space O(V)

```python
import heapq

def dijkstra(graph, start):
    """
    graph: dict of node → list of (neighbor, weight)
    Returns: dist dict with shortest distance from start to every node
    """
    dist = {node: float('inf') for node in graph}
    dist[start] = 0
    heap = [(0, start)]    # (distance, node)
    
    while heap:
        d, node = heapq.heappop(heap)
        if d > dist[node]:
            continue       # Stale entry — skip (lazy deletion)
        for neighbor, weight in graph[node]:
            new_dist = d + weight
            if new_dist < dist[neighbor]:
                dist[neighbor] = new_dist
                heapq.heappush(heap, (new_dist, neighbor))
    
    return dist

def dijkstra_with_path(graph, start, end):
    """Returns (distance, path) from start to end."""
    dist = {node: float('inf') for node in graph}
    dist[start] = 0
    prev = {node: None for node in graph}
    heap = [(0, start)]
    
    while heap:
        d, node = heapq.heappop(heap)
        if node == end:
            break
        if d > dist[node]:
            continue
        for neighbor, weight in graph[node]:
            new_dist = d + weight
            if new_dist < dist[neighbor]:
                dist[neighbor] = new_dist
                prev[neighbor] = node
                heapq.heappush(heap, (new_dist, neighbor))
    
    # Reconstruct path
    path, curr = [], end
    while curr is not None:
        path.append(curr)
        curr = prev[curr]
    return dist[end], path[::-1]
```

**Lazy deletion pattern:** Instead of updating heap entries (complex), push new (dist, node) pairs and skip stale ones with `if d > dist[node]: continue`.

---

### Bellman-Ford

Relax ALL edges V-1 times. After V-1 iterations, shortest paths are found (assuming no negative cycles — any path can have at most V-1 edges). Run one more iteration: if any edge still relaxes, a negative cycle exists.

**Complexity:** Time O(VE) | Space O(V)

```python
def bellman_ford(edges, num_nodes, start):
    """
    edges: list of (u, v, weight)
    Returns: (dist dict, has_negative_cycle bool)
    """
    dist = {i: float('inf') for i in range(num_nodes)}
    dist[start] = 0
    
    # Relax all edges V-1 times
    for _ in range(num_nodes - 1):
        for u, v, w in edges:
            if dist[u] != float('inf') and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
    
    # Check for negative cycle (Vth relaxation)
    for u, v, w in edges:
        if dist[u] != float('inf') and dist[u] + w < dist[v]:
            return dist, True   # Negative cycle detected
    
    return dist, False

# SPFA (Shortest Path Faster Algorithm) — Bellman-Ford with BFS queue optimization
# Average O(kE) where k << V, but worst case still O(VE)
from collections import deque

def spfa(graph, start, num_nodes):
    dist = [float('inf')] * num_nodes
    dist[start] = 0
    in_queue = [False] * num_nodes
    count = [0] * num_nodes   # Track relaxation count per node
    queue = deque([start])
    in_queue[start] = True
    
    while queue:
        node = queue.popleft()
        in_queue[node] = False
        for neighbor, weight in graph[node]:
            if dist[node] + weight < dist[neighbor]:
                dist[neighbor] = dist[node] + weight
                count[neighbor] += 1
                if count[neighbor] >= num_nodes:
                    return None   # Negative cycle
                if not in_queue[neighbor]:
                    queue.append(neighbor)
                    in_queue[neighbor] = True
    return dist
```

---

### Floyd-Warshall

Dynamic programming over all pairs (i, j) with intermediate nodes 0..k. `dp[i][j][k]` = shortest path from i to j using only nodes {0..k} as intermediates. Reduce to 2D by updating in-place.

**Complexity:** Time O(V³) | Space O(V²)

```python
def floyd_warshall(num_nodes, edges):
    """
    Returns dist[i][j] = shortest path from i to j (inf if unreachable).
    """
    INF = float('inf')
    dist = [[INF] * num_nodes for _ in range(num_nodes)]
    
    for i in range(num_nodes):
        dist[i][i] = 0
    
    for u, v, w in edges:
        dist[u][v] = min(dist[u][v], w)   # Handle parallel edges
    
    for k in range(num_nodes):            # Intermediate node
        for i in range(num_nodes):        # Source
            for j in range(num_nodes):    # Destination
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
    
    # Check negative cycles: dist[i][i] < 0 means i is on a negative cycle
    for i in range(num_nodes):
        if dist[i][i] < 0:
            return None   # Negative cycle exists
    
    return dist
```

---

### Kruskal's MST (with Disjoint Set Union)

Sort all edges by weight. Greedily add the cheapest edge that connects two different components (use DSU to check). Produces minimum spanning tree for connected graph.

**Complexity:** Time O(E log E) dominated by sort | Space O(V) for DSU

```python
class DSU:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n
    
    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])   # Path compression
        return self.parent[x]
    
    def union(self, x, y):
        px, py = self.find(x), self.find(y)
        if px == py:
            return False          # Already in same component
        if self.rank[px] < self.rank[py]:
            px, py = py, px
        self.parent[py] = px      # Union by rank
        if self.rank[px] == self.rank[py]:
            self.rank[px] += 1
        return True

def kruskal(num_nodes, edges):
    """
    edges: list of (weight, u, v)
    Returns: (mst_cost, mst_edges)
    """
    edges.sort()                  # Sort by weight
    dsu = DSU(num_nodes)
    mst_cost = 0
    mst_edges = []
    
    for weight, u, v in edges:
        if dsu.union(u, v):
            mst_cost += weight
            mst_edges.append((u, v, weight))
            if len(mst_edges) == num_nodes - 1:
                break             # MST complete (V-1 edges)
    
    return mst_cost, mst_edges
```

---

### Prim's MST

Grows MST greedily from a starting node. Like Dijkstra but instead of distance from source, tracks minimum edge cost to add each node to the MST. Better than Kruskal for dense graphs.

**Complexity:** Time O(E log V) with min-heap | Space O(V)

```python
import heapq

def prim(graph, start=0):
    """
    graph: dict of node → list of (neighbor, weight)
    Returns: total MST cost
    """
    visited = set()
    heap = [(0, start)]          # (edge_weight, node)
    total_cost = 0
    
    while heap and len(visited) < len(graph):
        cost, node = heapq.heappop(heap)
        if node in visited:
            continue
        visited.add(node)
        total_cost += cost
        for neighbor, weight in graph[node]:
            if neighbor not in visited:
                heapq.heappush(heap, (weight, neighbor))
    
    return total_cost
```

**Prim on complete graph (coordinate-based):**
```python
def prim_coordinates(points):
    """MST on complete graph where edge weight = Manhattan distance."""
    n = len(points)
    visited = set()
    heap = [(0, 0)]   # (cost, node_index)
    total = 0
    
    while len(visited) < n:
        cost, i = heapq.heappop(heap)
        if i in visited:
            continue
        visited.add(i)
        total += cost
        for j in range(n):
            if j not in visited:
                dist = abs(points[i][0] - points[j][0]) + abs(points[i][1] - points[j][1])
                heapq.heappush(heap, (dist, j))
    
    return total
```

---

## Worked Problems

### Problem 1: Network Delay Time (LeetCode #743)

**Clarifying Questions:**
- Directed or undirected graph? → Directed
- Can there be multiple edges between same nodes? → Yes
- What is n (number of nodes)? → Up to 100 (labeled 1..n)
- Return -1 if some node unreachable? → Yes

**Brute Force:** Bellman-Ford — O(VE), works but slower than needed.

**Optimization:** Dijkstra from source k — O((V+E) log V). Answer = max distance in dist dict (time for signal to reach all nodes).

**Edge Cases:**
- n=1 → return 0 (already at the only node)
- Some node unreachable → return -1
- Multiple edges: pick minimum weight for initial dist setup

**Code:**
```python
import heapq
from collections import defaultdict

def networkDelayTime(times, n, k):
    graph = defaultdict(list)
    for u, v, w in times:
        graph[u].append((v, w))
    
    dist = {i: float('inf') for i in range(1, n + 1)}
    dist[k] = 0
    heap = [(0, k)]
    
    while heap:
        d, node = heapq.heappop(heap)
        if d > dist[node]:
            continue
        for neighbor, weight in graph[node]:
            new_dist = d + weight
            if new_dist < dist[neighbor]:
                dist[neighbor] = new_dist
                heapq.heappush(heap, (new_dist, neighbor))
    
    max_dist = max(dist.values())
    return max_dist if max_dist < float('inf') else -1
```

**Time:** O((V+E) log V) | **Space:** O(V+E)

**Follow-ups:**
- What if edges are undirected? → Add edge in both directions
- What if some nodes have no outgoing edges? → Still correct; they stay in dist but never push to heap
- What about negative edge weights? → Use Bellman-Ford instead

---

### Problem 2: Find the City With the Smallest Number of Neighbors at a Threshold Distance (LeetCode #1334)

**Clarifying Questions:**
- Threshold applies to total path cost, not hops? → Yes, path weight ≤ distanceThreshold
- Ties broken by highest city number? → Yes (return largest index among ties)
- Graph is undirected and weighted? → Yes

**Brute Force:** BFS/DFS from each city — incorrect for weighted graphs.

**Optimization:** Floyd-Warshall for all-pairs shortest paths, then count reachable cities per node. V ≤ 100, so O(V³) = 10⁶ operations — fast enough.

**Edge Cases:**
- All cities unreachable from each other → every city has 0 reachable cities, return last city
- distanceThreshold = 0 → no city reachable except itself (which doesn't count)

**Code (Floyd-Warshall):**
```python
def findTheCity(n, edges, distanceThreshold):
    INF = float('inf')
    dist = [[INF] * n for _ in range(n)]
    for i in range(n):
        dist[i][i] = 0
    for u, v, w in edges:
        dist[u][v] = w
        dist[v][u] = w   # Undirected
    
    # Floyd-Warshall
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
    
    best_city = -1
    min_reachable = n + 1
    
    for city in range(n):
        reachable = sum(1 for j in range(n) if j != city and dist[city][j] <= distanceThreshold)
        if reachable <= min_reachable:   # <= takes higher city number on tie
            min_reachable = reachable
            best_city = city
    
    return best_city
```

**Time:** O(V³ + V²) = O(V³) | **Space:** O(V²)

**Follow-ups:**
- If V were 10,000? → Run Dijkstra from each node: O(V(V+E) log V), better than Floyd-Warshall's O(V³)
- Find the city that minimizes max distance to all others? → Dijkstra from each, take max instead of count

---

### Problem 3: Min Cost to Connect All Points (LeetCode #1584)

**Clarifying Questions:**
- Cost = Manhattan distance between any two points? → Yes
- Connect ALL points (MST, not just some)? → Yes
- Points have distinct coordinates? → Yes
- Number of points up to? → 1000

**Brute Force:** List all n² edges, run Kruskal — O(n² log n).

**Optimization:** Prim's with lazy heap — O(n² log n) same asymptotic but better constant for dense graphs. No need to pre-build explicit edge list.

**Edge Cases:**
- Single point → return 0
- Two points → return their Manhattan distance

**Code (Prim's on complete graph):**
```python
import heapq

def minCostConnectPoints(points):
    n = len(points)
    if n == 1:
        return 0
    
    visited = set()
    heap = [(0, 0)]   # (cost, index)
    total = 0
    
    while len(visited) < n:
        cost, i = heapq.heappop(heap)
        if i in visited:
            continue
        visited.add(i)
        total += cost
        
        for j in range(n):
            if j not in visited:
                dist = abs(points[i][0] - points[j][0]) + abs(points[i][1] - points[j][1])
                heapq.heappush(heap, (dist, j))
    
    return total
```

**Kruskal alternative (explicit edge list):**
```python
def minCostConnectPoints_kruskal(points):
    n = len(points)
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            dist = abs(points[i][0] - points[j][0]) + abs(points[i][1] - points[j][1])
            edges.append((dist, i, j))
    
    edges.sort()
    dsu = DSU(n)
    total = 0
    edges_used = 0
    
    for dist, i, j in edges:
        if dsu.union(i, j):
            total += dist
            edges_used += 1
            if edges_used == n - 1:
                break
    return total
```

**Time:** O(n² log n) both approaches | **Space:** O(n²) Kruskal, O(n) Prim heap

**Follow-ups:**
- What if Euclidean distance instead of Manhattan? → Same algorithm, different distance function
- What if you only need to connect k out of n points cheaply? → Minimum spanning forest problem
- Can Prim's be made O(n²) for complete graphs? → Yes, with array-based (not heap-based) implementation

---

## Common Mistakes

**1. Using Dijkstra with negative edge weights**
```python
# Dijkstra gives wrong answers with negative edges:
# graph: A→B=1, A→C=10, B→C=-12
# Dijkstra: A→C=10 (sets dist[C]=10, never re-examines)
# Correct: A→B→C = 1 + (-12) = -11 (Bellman-Ford finds this)

# Rule: if any edge weight < 0 → use Bellman-Ford (or SPFA)
```

**2. Not checking for negative cycles in Bellman-Ford**
```python
# After V-1 relaxations, run one more pass
# If any edge still relaxes → negative cycle (path gets shorter forever)
for u, v, w in edges:
    if dist[u] + w < dist[v]:
        return "NEGATIVE CYCLE"   # Don't return dist; it's meaningless
```

**3. Kruskal: forgetting to check if edge creates a cycle**
```python
# BAD: Add all edges sorted by weight
for w, u, v in sorted_edges:
    mst_cost += w   # Wrong: doesn't check if u, v already connected

# GOOD: Only add edge if it connects two different components
for w, u, v in sorted_edges:
    if dsu.union(u, v):         # Returns False if same component
        mst_cost += w
```

**4. Prim vs Kruskal choice on dense vs sparse**
- Dense graph (E ≈ V²): Prim with binary heap = O(E log V) = O(V² log V)
- Sparse graph (E ≈ V): Kruskal = O(E log E) = O(V log V) — faster
- In interviews: Prim is easier to implement (similar to Dijkstra). Kruskal requires DSU.

**5. Floyd-Warshall initialization error**
```python
# BAD: Initialize with 0 (wrong for non-self paths)
dist = [[0] * n for _ in range(n)]

# GOOD: Initialize with inf, then set diagonal to 0
dist = [[float('inf')] * n for _ in range(n)]
for i in range(n):
    dist[i][i] = 0
```

**6. Floyd-Warshall: loop order matters**
```python
# MUST be: k (intermediate) outermost, then i and j
# Swapping order gives wrong results
for k in range(n):        # Intermediate node — OUTERMOST
    for i in range(n):    # Source
        for j in range(n):# Destination
            ...
```

**7. Dijkstra: forgetting to skip stale heap entries**
```python
# Without this check, stale entries cause re-processing
d, node = heapq.heappop(heap)
if d > dist[node]:
    continue    # This entry is outdated — skip it
```

---

## Interview Q&A

**Q1: Why can't Dijkstra handle negative edge weights?**
Dijkstra's greedy assumption is that once a node is popped from the heap, its distance is finalized. With negative edges, a path through a not-yet-processed node might yield a shorter route to an already-finalized node. The algorithm never revisits finalized nodes, so it misses these shorter paths. Bellman-Ford handles this by relaxing all edges V-1 times, always reconsidering.

**Q2: What is the practical difference between Dijkstra and A*?**
A* adds a heuristic h(n) — an estimate of remaining distance to goal. The priority function becomes f(n) = g(n) + h(n), where g(n) is actual cost from source. With an admissible heuristic (never overestimates), A* is optimal and explores fewer nodes than Dijkstra. Without a heuristic (h=0), A* reduces to Dijkstra. Used in game pathfinding and GPS navigation.

**Q3: When would you choose Floyd-Warshall over running Dijkstra from every node?**
Floyd-Warshall: simpler code (3 nested loops), handles negative edges (without negative cycles), O(V³) and O(V²) space. Run Dijkstra V times: better when V is large (say > 500) and edges are sparse, gives O(V × (V+E) log V) which beats O(V³) when E << V². If graph has negative edges, Bellman-Ford must be run V times instead.

**Q4: What's the difference between MST and shortest path?**
MST connects all nodes with minimum total edge weight (no specific source/destination). Shortest path finds minimum cost route between two specific nodes. An MST edge is not necessarily on the shortest path between its endpoints — the MST is global, shortest path is local. Example: in a 3-node triangle with weights 1, 2, 3, the MST uses edges of weight 1 and 2, but shortest path from node 1 to node 3 might use weight 1+2=3 vs direct edge of weight 3.

**Q5: How does Kruskal's DSU achieve near-O(1) per operation?**
DSU with path compression + union by rank achieves O(α(n)) per operation, where α is the inverse Ackermann function — practically constant (≤ 5 for any n < 10⁸⁰). Path compression flattens the tree during `find`. Union by rank keeps tree height O(log n). Together, n operations cost O(n × α(n)) ≈ O(n).

**Q6: Design a real-time navigation system — which algorithm?**
Dijkstra for static road networks. A* with Euclidean/haversine distance heuristic for faster single-target queries. In practice (Google Maps, Waze): hierarchical approaches — precompute shortcuts on highways (Contraction Hierarchies), enabling queries in milliseconds on 100M+ node graphs. For traffic updates: incremental Dijkstra or D* Lite (dynamic replanning).

**Q7: What if Dijkstra gives TLE on a dense graph?**
Dense graph (E ≈ V²): heap-based Dijkstra is O(V² log V). Switch to array-based Dijkstra O(V²) — skip the heap, instead scan all unvisited nodes for minimum distance. For V ≤ 1000 (≤ 10⁶ cells), array scan is faster than heap push/pop overhead. This is also why Prim with array beats Prim with heap on dense graphs.
