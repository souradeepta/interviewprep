# Graph

## Overview

A **Graph** G = (V, E) consists of a set of vertices (nodes) V and edges E connecting them. Graphs model relationships between entities. They are the most general data structure and underlie problems in networking, social graphs, dependency resolution, maps, and more.

**When to use:**
- Shortest path between two points (maps, routing)
- Cycle detection in dependencies
- Connected components (social networks, grid islands)
- Topological ordering (course prerequisites, build systems)
- Network flow / matching problems
- State-space search (BFS = shortest path in unweighted graph)

---

## Visualization

### Undirected Graph

```
  A ─────── B
  |  \   /  |
  |    X    |
  |  /   \  |
  C ─────── D

Adjacency List:
  A: [B, C, D]
  B: [A, C, D]
  C: [A, B, D]
  D: [A, B, C]
  (complete graph K4)
```

### Directed Graph (Digraph)

```
  A ──→ B ──→ D
  |     ↑     |
  ↓     |     ↓
  C ────┘     E

Adjacency List (directed):
  A: [B, C]
  B: [D]
  C: [B]
  D: [E]
  E: []

In-degree:   A=0, B=2, C=1, D=1, E=1
Out-degree:  A=2, B=1, C=1, D=1, E=0
```

### Weighted Graph

```
       4         2
  A ──────── B ────── D
  |          |        |
  | 1        | 3      | 5
  |          |        |
  C ─────────┘        E
       7
  (undirected, weights on edges)

Adjacency List with weights:
  A: [(B,4), (C,1)]
  B: [(A,4), (C,3), (D,2)]
  C: [(A,1), (B,3)]
  D: [(B,2), (E,5)]
  E: [(D,5)]
```

### Adjacency Matrix (4 nodes, undirected)

```
    A  B  C  D
A [ 0  1  1  1 ]
B [ 1  0  1  1 ]
C [ 1  1  0  1 ]
D [ 1  1  1  0 ]

matrix[i][j] = 1 if edge (i,j) exists
Symmetric for undirected graphs.
Dense graphs favor this; sparse graphs waste space.
```

### BFS Traversal (from A)

```
Graph:          BFS order starting from A:
  A─B           Queue: [A]
  |×|           Visit A → Queue: [B, C]
  C─D           Visit B → Queue: [C, D]
                Visit C → Queue: [D]  (D already in queue/visited)
                Visit D → done
Level 0: A
Level 1: B, C   (neighbors of A)
Level 2: D      (neighbor of B and C not yet visited)
BFS order: A → B → C → D
```

### DFS Traversal (from A)

```
Graph:          DFS order starting from A (iterative, stack):
  A─B           Stack: [A]
  |×|           Visit A → push neighbors: Stack: [B, C]
  C─D           Visit C → push neighbors: Stack: [B, D]
                Visit D → push neighbors: Stack: [B]  (A,C already visited)
                Visit B → done
DFS order (depends on order neighbors are added): A → C → D → B
```

### Topological Sort (DAG)

```
DAG (course prerequisites):
  Math ──→ Physics ──→ Lab
    \                 ↗
     ──→ CS ─────────

Topological order: [Math, Physics, CS, Lab]
  or               [Math, CS, Physics, Lab]
  (multiple valid orderings exist)

Kahn's algorithm (BFS):
  in-degree: Math=0, Physics=1, CS=1, Lab=2
  Start: nodes with in-degree 0 → [Math]
  Process Math → decrement neighbors → Physics(0), CS(0)
  Queue: [Physics, CS]  → and so on...
```

---

## Operations & Complexity

| Operation                    | Adjacency List | Adjacency Matrix |
|------------------------------|:--------------:|:----------------:|
| Space                        | O(V + E)       | O(V²)            |
| Add vertex                   | O(1)           | O(V²)            |
| Add edge                     | O(1)           | O(1)             |
| Remove edge                  | O(E)           | O(1)             |
| Check edge (u, v) exists     | O(degree(u))   | O(1)             |
| Get all neighbors of u       | O(degree(u))   | O(V)             |
| BFS / DFS                    | O(V + E)       | O(V²)            |
| Dijkstra (min heap)          | O((V+E) log V) | O(V² log V)      |
| Bellman-Ford                 | O(V·E)         | O(V³)            |
| Floyd-Warshall (all pairs)   | O(V³)          | O(V³)            |
| Topological Sort (Kahn's)    | O(V + E)       | O(V²)            |

> Use adjacency list for sparse graphs (E << V²). Use adjacency matrix when you need O(1) edge queries and the graph is dense.

---

## Key Properties / Invariants

1. **Directed vs Undirected**: Directed edges have orientation; undirected edges are bidirectional.
2. **Weighted vs Unweighted**: Edges may carry a cost/weight.
3. **Cyclic vs Acyclic**: A DAG (Directed Acyclic Graph) has no directed cycles; enables topological sort.
4. **Connected vs Disconnected**: A graph is connected if every vertex is reachable from every other.
5. **Simple graph**: No self-loops, no multi-edges (most interview problems assume this).
6. **Tree = connected acyclic undirected graph**: A tree with n nodes has exactly n-1 edges.
7. **Bipartite**: Vertices can be split into two groups; edges only go between groups (2-colorable).

---

## Common Interview Patterns

### Pattern 1: BFS for Shortest Path (Unweighted)
BFS level-by-level naturally gives shortest path in unweighted graphs.

```
def bfs_shortest(graph, start, end):
    from collections import deque
    queue = deque([(start, 0)])   # (node, distance)
    visited = {start}
    while queue:
        node, dist = queue.popleft()
        if node == end:
            return dist
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, dist + 1))
    return -1  # unreachable
```

### Pattern 2: DFS for Connected Components / Cycle Detection
Use DFS with a visited set. Each unvisited starting node begins a new component.

```
def count_components(n, edges):
    graph = defaultdict(list)
    for u, v in edges:
        graph[u].append(v); graph[v].append(u)
    visited, count = set(), 0
    def dfs(node):
        visited.add(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                dfs(neighbor)
    for i in range(n):
        if i not in visited:
            dfs(i); count += 1
    return count
```

### Pattern 3: Topological Sort (Kahn's BFS or DFS postorder)

```
# Kahn's algorithm
def topo_sort(n, prereqs):
    graph = defaultdict(list)
    in_degree = [0] * n
    for u, v in prereqs:
        graph[v].append(u)
        in_degree[u] += 1
    queue = deque(i for i in range(n) if in_degree[i] == 0)
    order = []
    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    return order if len(order) == n else []  # [] = cycle detected
```

### Pattern 4: Grid as Graph (BFS/DFS on 2D Grid)
Each cell is a node; edges go to 4 (or 8) adjacent cells.

```
DIRECTIONS = [(0,1),(0,-1),(1,0),(-1,0)]
def bfs_grid(grid, start):
    rows, cols = len(grid), len(grid[0])
    queue = deque([start])
    visited = {start}
    while queue:
        r, c = queue.popleft()
        for dr, dc in DIRECTIONS:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and (nr,nc) not in visited:
                visited.add((nr, nc))
                queue.append((nr, nc))
```

### Pattern 5: Dijkstra's Shortest Path (Weighted)
Use a min heap. Greedy: always expand the cheapest unvisited node.

```
def dijkstra(graph, src):
    dist = {node: float('inf') for node in graph}
    dist[src] = 0
    heap = [(0, src)]
    while heap:
        d, u = heappop(heap)
        if d > dist[u]: continue   # stale entry
        for v, w in graph[u]:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                heappush(heap, (dist[v], v))
    return dist
```

---

## Interview Tips

- **Build the graph first**: Many problems give edges as a list — always build adjacency list before BFS/DFS.
- **Visited set is crucial**: Forgetting visited leads to infinite loops on cyclic graphs.
- **DFS vs BFS**: BFS = shortest path (unweighted), DFS = connectivity/cycles/topological sort.
- **Grid problems ARE graph problems**: "Number of Islands" is just connected components via DFS/BFS.
- **Directed cycle detection**: Use DFS with three states: unvisited (0), in-stack (1), done (2). A back edge to an in-stack node = cycle.
- **Disconnected graphs**: Your BFS/DFS loop must iterate over ALL nodes, not just from a single source.
- **Negative weights**: Dijkstra fails; use Bellman-Ford. Negative cycles: no shortest path exists.
- **Bipartite check**: BFS with 2-coloring — if you try to give a node the same color as its neighbor, it's not bipartite.

---

## Example Problems

| Problem                                     | Pattern                              |
|---------------------------------------------|--------------------------------------|
| Number of Islands (LC 200)                  | DFS/BFS connected components on grid |
| Course Schedule II (LC 210)                 | Topological sort (Kahn's)            |
| Word Ladder (LC 127)                        | BFS shortest path                    |
| Clone Graph (LC 133)                        | DFS/BFS with hash map                |
| Network Delay Time (LC 743)                 | Dijkstra                             |

---

## Python Quick Reference

```python
from collections import defaultdict, deque
import heapq

# ── Build Graph ───────────────────────────────────────────────────────────────
def build_graph(n, edges, directed=False):
    graph = defaultdict(list)
    for u, v in edges:
        graph[u].append(v)
        if not directed:
            graph[v].append(u)
    return graph

# Build weighted graph
def build_weighted(n, edges, directed=False):
    graph = defaultdict(list)
    for u, v, w in edges:
        graph[u].append((v, w))
        if not directed:
            graph[v].append((u, w))
    return graph

# ── BFS ───────────────────────────────────────────────────────────────────────
def bfs(graph, start):
    visited = {start}
    queue = deque([start])
    order = []
    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    return order

# ── DFS (iterative) ───────────────────────────────────────────────────────────
def dfs(graph, start):
    visited = set()
    stack = [start]
    order = []
    while stack:
        node = stack.pop()
        if node in visited:
            continue
        visited.add(node)
        order.append(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                stack.append(neighbor)
    return order

# ── DFS (recursive) ───────────────────────────────────────────────────────────
def dfs_recursive(graph, node, visited=None):
    if visited is None:
        visited = set()
    visited.add(node)
    for neighbor in graph[node]:
        if neighbor not in visited:
            dfs_recursive(graph, neighbor, visited)
    return visited

# ── Cycle Detection (directed) ────────────────────────────────────────────────
def has_cycle(graph, n):
    # 0=unvisited, 1=in-stack, 2=done
    state = [0] * n
    def dfs(u):
        state[u] = 1
        for v in graph[u]:
            if state[v] == 1:    return True   # back edge → cycle
            if state[v] == 0 and dfs(v): return True
        state[u] = 2
        return False
    return any(dfs(i) for i in range(n) if state[i] == 0)

# ── Topological Sort (Kahn's) ─────────────────────────────────────────────────
def topo_sort(n, edges):
    graph = defaultdict(list)
    in_degree = [0] * n
    for u, v in edges:
        graph[u].append(v)
        in_degree[v] += 1
    queue = deque(i for i in range(n) if in_degree[i] == 0)
    order = []
    while queue:
        node = queue.popleft()
        order.append(node)
        for nb in graph[node]:
            in_degree[nb] -= 1
            if in_degree[nb] == 0:
                queue.append(nb)
    return order if len(order) == n else []  # empty = cycle

# ── Dijkstra ──────────────────────────────────────────────────────────────────
def dijkstra(graph, src, n):
    dist = [float('inf')] * n
    dist[src] = 0
    heap = [(0, src)]
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue
        for v, w in graph[u]:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                heapq.heappush(heap, (dist[v], v))
    return dist

# ── Bipartite Check ───────────────────────────────────────────────────────────
def is_bipartite(graph, n):
    color = [-1] * n
    for start in range(n):
        if color[start] != -1:
            continue
        queue = deque([start])
        color[start] = 0
        while queue:
            node = queue.popleft()
            for nb in graph[node]:
                if color[nb] == -1:
                    color[nb] = 1 - color[node]
                    queue.append(nb)
                elif color[nb] == color[node]:
                    return False
    return True
```

---

## Java Quick Reference

```java
import java.util.*;

// ── Build Adjacency List ──────────────────────────────────────────────────────
Map<Integer, List<Integer>> buildGraph(int n, int[][] edges, boolean directed) {
    Map<Integer, List<Integer>> graph = new HashMap<>();
    for (int i = 0; i < n; i++) graph.put(i, new ArrayList<>());
    for (int[] e : edges) {
        graph.get(e[0]).add(e[1]);
        if (!directed) graph.get(e[1]).add(e[0]);
    }
    return graph;
}

// ── BFS ───────────────────────────────────────────────────────────────────────
List<Integer> bfs(Map<Integer, List<Integer>> graph, int start) {
    List<Integer> order = new ArrayList<>();
    Set<Integer> visited = new HashSet<>();
    Deque<Integer> queue = new ArrayDeque<>();
    queue.offer(start); visited.add(start);
    while (!queue.isEmpty()) {
        int node = queue.poll();
        order.add(node);
        for (int nb : graph.getOrDefault(node, Collections.emptyList())) {
            if (visited.add(nb)) queue.offer(nb);
        }
    }
    return order;
}

// ── DFS (iterative) ───────────────────────────────────────────────────────────
List<Integer> dfs(Map<Integer, List<Integer>> graph, int start) {
    List<Integer> order = new ArrayList<>();
    Set<Integer> visited = new HashSet<>();
    Deque<Integer> stack = new ArrayDeque<>();
    stack.push(start);
    while (!stack.isEmpty()) {
        int node = stack.pop();
        if (!visited.add(node)) continue;
        order.add(node);
        for (int nb : graph.getOrDefault(node, Collections.emptyList()))
            if (!visited.contains(nb)) stack.push(nb);
    }
    return order;
}

// ── Dijkstra ──────────────────────────────────────────────────────────────────
int[] dijkstra(int n, int[][] edges, int src) {
    // edges: [u, v, weight]
    Map<Integer, List<int[]>> graph = new HashMap<>();
    for (int i = 0; i < n; i++) graph.put(i, new ArrayList<>());
    for (int[] e : edges) {
        graph.get(e[0]).add(new int[]{e[1], e[2]});
        graph.get(e[1]).add(new int[]{e[0], e[2]});
    }
    int[] dist = new int[n];
    Arrays.fill(dist, Integer.MAX_VALUE);
    dist[src] = 0;
    PriorityQueue<int[]> heap = new PriorityQueue<>(Comparator.comparingInt(a -> a[0]));
    heap.offer(new int[]{0, src});
    while (!heap.isEmpty()) {
        int[] curr = heap.poll();
        int d = curr[0], u = curr[1];
        if (d > dist[u]) continue;
        for (int[] nb : graph.get(u)) {
            int v = nb[0], w = nb[1];
            if (dist[u] + w < dist[v]) {
                dist[v] = dist[u] + w;
                heap.offer(new int[]{dist[v], v});
            }
        }
    }
    return dist;
}

// ── Topological Sort (Kahn's) ─────────────────────────────────────────────────
int[] topoSort(int n, int[][] prereqs) {
    List<List<Integer>> graph = new ArrayList<>();
    int[] inDegree = new int[n];
    for (int i = 0; i < n; i++) graph.add(new ArrayList<>());
    for (int[] p : prereqs) { graph.get(p[1]).add(p[0]); inDegree[p[0]]++; }

    Deque<Integer> queue = new ArrayDeque<>();
    for (int i = 0; i < n; i++) if (inDegree[i] == 0) queue.offer(i);

    int[] order = new int[n]; int idx = 0;
    while (!queue.isEmpty()) {
        int node = queue.poll(); order[idx++] = node;
        for (int nb : graph.get(node))
            if (--inDegree[nb] == 0) queue.offer(nb);
    }
    return idx == n ? order : new int[0]; // empty = cycle
}
```
