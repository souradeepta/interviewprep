# Graph Algorithms Mastery: Traversal, Shortest Path, and Advanced Techniques

Master graph algorithms from basic traversal to advanced path-finding and flow algorithms.

---

## Graph Representation & Complexity

```
Adjacency List: O(V+E) space, O(degree) per vertex
Adjacency Matrix: O(V²) space, O(1) edge lookup

For most interviews: Use adjacency list
```

---

## Traversal Algorithms

### BFS (Breadth-First Search)

```python
from collections import deque

def bfs(graph, start):
    visited = set()
    queue = deque([start])
    visited.add(start)
    
    while queue:
        node = queue.popleft()
        print(node)
        
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    
    # Use: Shortest path in unweighted graph, level-order, bipartite check
    # Time: O(V+E), Space: O(V)
```

### DFS (Depth-First Search)

```python
def dfs_recursive(graph, node, visited):
    visited.add(node)
    print(node)
    
    for neighbor in graph[node]:
        if neighbor not in visited:
            dfs_recursive(graph, neighbor, visited)

def dfs_iterative(graph, start):
    visited = set()
    stack = [start]
    
    while stack:
        node = stack.pop()
        if node not in visited:
            visited.add(node)
            print(node)
            stack.extend(reversed(graph[node]))
    
    # Use: Cycle detection, topological sort, connected components
    # Time: O(V+E), Space: O(V)
```

---

## Shortest Path Algorithms

### Dijkstra's (Non-negative weights)

```python
import heapq

def dijkstra(graph, start):
    dist = {node: float('inf') for node in graph}
    dist[start] = 0
    pq = [(0, start)]
    
    while pq:
        d, node = heapq.heappop(pq)
        
        if d > dist[node]:
            continue
        
        for neighbor, weight in graph[node]:
            if dist[node] + weight < dist[neighbor]:
                dist[neighbor] = dist[node] + weight
                heapq.heappush(pq, (dist[neighbor], neighbor))
    
    return dist

# Time: O((V+E) log V), Space: O(V)
# Use: Shortest path with non-negative weights
```

### Bellman-Ford (Handles negatives, detects cycles)

```python
def bellman_ford(edges, start, n):
    dist = [float('inf')] * n
    dist[start] = 0
    
    # Relax edges V-1 times
    for _ in range(n - 1):
        for u, v, w in edges:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
    
    # Check for negative cycle
    for u, v, w in edges:
        if dist[u] + w < dist[v]:
            return None  # Negative cycle detected
    
    return dist

# Time: O(V·E), Space: O(V)
# Use: Handles negative edges, detects negative cycles
```

### Floyd-Warshall (All-pairs shortest path)

```python
def floyd_warshall(graph):
    n = len(graph)
    dist = [row[:] for row in graph]
    
    for k in range(n):
        for i in range(n):
            for j in range(n):
                dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])
    
    return dist

# Time: O(V³), Space: O(V²)
# Use: All pairs shortest path, small graphs only
```

---

## Minimum Spanning Tree

### Kruskal's Algorithm (Edge-based)

```python
def kruskal(edges, n):
    edges.sort(key=lambda x: x[2])  # Sort by weight
    uf = UnionFind(n)
    mst = []
    
    for u, v, w in edges:
        if uf.find(u) != uf.find(v):
            uf.union(u, v)
            mst.append((u, v, w))
    
    return mst

# Time: O(E log E), Space: O(V)
# Use: Sparse graphs
```

### Prim's Algorithm (Vertex-based)

```python
def prim(graph, start):
    visited = {start}
    edges = [(w, start, v) for v, w in graph[start]]
    heapq.heapify(edges)
    mst = []
    
    while edges:
        w, u, v = heapq.heappop(edges)
        if v in visited:
            continue
        
        visited.add(v)
        mst.append((u, v, w))
        
        for next_v, next_w in graph[v]:
            if next_v not in visited:
                heapq.heappush(edges, (next_w, v, next_v))
    
    return mst

# Time: O((V+E) log V), Space: O(V)
# Use: Dense graphs
```

---

## Topological Sort

### DFS-based Topological Sort

```python
def topological_sort(graph, n):
    visited = [False] * n
    stack = []
    
    def dfs(node):
        visited[node] = True
        for neighbor in graph[node]:
            if not visited[neighbor]:
                dfs(neighbor)
        stack.append(node)
    
    for i in range(n):
        if not visited[i]:
            dfs(i)
    
    return stack[::-1]

# Time: O(V+E), Space: O(V)
# Use: Dependency resolution, task scheduling, detecting cycles
```

### Kahn's Algorithm (BFS-based)

```python
def kahn(graph, n):
    in_degree = [0] * n
    for u in range(n):
        for v in graph[u]:
            in_degree[v] += 1
    
    queue = [i for i in range(n) if in_degree[i] == 0]
    result = []
    
    while queue:
        node = queue.pop(0)
        result.append(node)
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    
    return result if len(result) == n else []  # Empty if cycle exists

# Time: O(V+E), Space: O(V)
```

---

## Advanced Topics

### Bipartite Graph Check

```python
def is_bipartite(graph, n):
    color = [-1] * n
    
    for start in range(n):
        if color[start] == -1:
            queue = [start]
            color[start] = 0
            
            while queue:
                node = queue.pop(0)
                for neighbor in graph[node]:
                    if color[neighbor] == -1:
                        color[neighbor] = 1 - color[node]
                        queue.append(neighbor)
                    elif color[neighbor] == color[node]:
                        return False
    
    return True

# Time: O(V+E), Space: O(V)
```

### Strongly Connected Components (Kosaraju)

```python
def kosaraju(graph, n):
    # DFS to get finishing times
    visited = [False] * n
    stack = []
    
    def dfs1(node):
        visited[node] = True
        for neighbor in graph[node]:
            if not visited[neighbor]:
                dfs1(neighbor)
        stack.append(node)
    
    for i in range(n):
        if not visited[i]:
            dfs1(i)
    
    # Create reverse graph
    reverse_graph = [[] for _ in range(n)]
    for u in range(n):
        for v in graph[u]:
            reverse_graph[v].append(u)
    
    # DFS on reverse graph in reverse finish order
    visited = [False] * n
    sccs = []
    
    def dfs2(node, scc):
        visited[node] = True
        scc.append(node)
        for neighbor in reverse_graph[node]:
            if not visited[neighbor]:
                dfs2(neighbor, scc)
    
    while stack:
        node = stack.pop()
        if not visited[node]:
            scc = []
            dfs2(node, scc)
            sccs.append(scc)
    
    return sccs

# Time: O(V+E), Space: O(V)
```

### Union-Find (Disjoint Set Union)

```python
class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n
    
    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])  # Path compression
        return self.parent[x]
    
    def union(self, x, y):
        px, py = self.find(x), self.find(y)
        if px == py:
            return False
        
        # Union by rank
        if self.rank[px] < self.rank[py]:
            px, py = py, px
        self.parent[py] = px
        if self.rank[px] == self.rank[py]:
            self.rank[px] += 1
        return True

# Time: O(α(n)) ≈ O(1) per operation
# Use: Connected components, cycle detection in undirected graphs, MST
```

---

## Graph Problems Decision Tree

| Problem | Algorithm | Time | Space |
|---------|-----------|------|-------|
| Shortest unweighted | BFS | O(V+E) | O(V) |
| Shortest weighted | Dijkstra | O((V+E)logV) | O(V) |
| Shortest with negatives | Bellman-Ford | O(V·E) | O(V) |
| All pairs | Floyd-Warshall | O(V³) | O(V²) |
| MST sparse | Kruskal | O(E log E) | O(V) |
| MST dense | Prim | O((V+E)logV) | O(V) |
| Topological sort | DFS or Kahn | O(V+E) | O(V) |
| Bipartite check | 2-coloring BFS | O(V+E) | O(V) |
| SCC | Kosaraju | O(V+E) | O(V) |
| Connected components | Union-Find | O(α(n)) | O(V) |

---

## Graph Checklist

- ✓ Chose correct algorithm (weighted/unweighted, directed/undirected)
- ✓ Used adjacency list for sparse graphs
- ✓ BFS for shortest unweighted path
- ✓ Dijkstra for shortest weighted path (non-negative)
- ✓ Bellman-Ford for negative weights
- ✓ DFS for cycle detection and topological sort
- ✓ Union-Find for connectivity and cycle detection
- ✓ Handled disconnected components
- ✓ Verified start/end node exists
- ✓ Tested on small examples before submitting

