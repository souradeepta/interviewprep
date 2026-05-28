# Graph Algorithms Mastery: Traversal, Shortest Path, and Advanced Techniques

**Level:** L3-L5
**Time to read:** ~30 min

Master graph algorithms from basic traversal to advanced path-finding and flow algorithms.

---

## Graph Representation & Complexity

```
Adjacency List: O(V+E) space, O(degree) per vertex
Adjacency Matrix: O(V²) space, O(1) edge lookup

For most interviews: Use adjacency list (sparse graphs, easier to iterate)
```

### Graph Building Example

```python
# Build adjacency list for undirected graph
graph = {
    'A': ['B', 'C'],
    'B': ['A', 'D'],
    'C': ['A', 'D'],
    'D': ['B', 'C']
}

# Or from edge list
edges = [('A','B'), ('A','C'), ('B','D'), ('C','D')]
graph = {}
for u, v in edges:
    if u not in graph: graph[u] = []
    if v not in graph: graph[v] = []
    graph[u].append(v)
    graph[v].append(u)  # Add reverse for undirected
```

---

## Traversal Algorithms

### BFS (Breadth-First Search)

**Real Example: Find Shortest Path**

```python
from collections import deque

def bfs_shortest_path(graph, start, end):
    visited = {start}
    queue = deque([(start, [start])])  # (node, path)
    
    while queue:
        node, path = queue.popleft()
        
        if node == end:
            return path
        
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    
    return None  # No path found

# Example: graph = {'A': ['B', 'C'], 'B': ['D'], 'C': ['D'], 'D': []}
# bfs_shortest_path(graph, 'A', 'D') → ['A', 'B', 'D']
# Time: O(V+E), Space: O(V)
```

**Common Mistakes:**
- ❌ Forgetting to mark visited BEFORE enqueueing (leads to duplicates)
- ❌ Forgetting to handle disconnected graphs
- ❌ Using regular list instead of deque (deque.popleft is O(1), list.pop(0) is O(n))

### DFS (Depth-First Search)

**Real Example: Detect Cycle in Undirected Graph**

```python
def has_cycle_undirected(graph, n):
    visited = [False] * n
    
    def dfs(node, parent):
        visited[node] = True
        for neighbor in graph[node]:
            if not visited[neighbor]:
                if dfs(neighbor, node):
                    return True
            elif neighbor != parent:  # Not the edge we came from
                return True  # Found a back edge = cycle
        return False
    
    for i in range(n):
        if not visited[i]:
            if dfs(i, -1):
                return True
    return False

# Example: graph = [[1,2], [0,2], [0,1]]
# Nodes 0-1-2 form a cycle
# Time: O(V+E), Space: O(V) for recursion stack
```

**Common Mistakes:**
- ❌ Forgetting parent check in undirected (sees same edge twice)
- ❌ Not handling disconnected components (multiple DFS calls needed)
- ❌ Using recursive when stack depth is deep (use iterative)

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

## Interview Tips for Graph Problems

### Clarifying Questions (Phase 1)

When you get a graph problem, ask:
- "Is the graph directed or undirected?"
- "Can there be cycles or is it acyclic?"
- "Are there negative edge weights?"
- "Is the graph guaranteed to be connected?"
- "What should I return if no path exists?"
- "Should I optimize for time or space?"

### Common Interview Questions

**Q: Find shortest path between two nodes**
- Unweighted: BFS (simpler, O(V+E))
- Weighted: Dijkstra (single source) or Floyd-Warshall (all pairs, if small)

**Q: Detect cycle in graph**
- Undirected: DFS with parent check OR Union-Find
- Directed: DFS with recursion stack (visiting state), OR Kahn's algorithm

**Q: Find connected components**
- Union-Find (elegant, O(α(n)))
- DFS/BFS with visited set

**Q: Topological sort**
- DFS (naturally produces reverse finish order)
- Kahn's algorithm (simultaneously checks for cycles)

### Edge Cases to Mention

```python
# Case 1: Empty graph
graph = {}
# Solution: handle gracefully, return empty result

# Case 2: Single node (no edges)
graph = {'A': []}
# Solution: return [A] for paths/components

# Case 3: Disconnected graph
graph = {'A': ['B'], 'B': ['A'], 'C': []}
# Solution: loop through all unvisited nodes

# Case 4: Self-loop
graph = {'A': ['A', 'B'], 'B': ['A']}
# Solution: mark visited before exploring to avoid infinite loop

# Case 5: Bidirectional vs unidirectional
# Clarify: A->B, is B->A also an edge?
```

---

## Real Interview Examples

### Example 1: Course Schedule (Detect Cycle via Topological Sort)

**Problem:** Given n courses and prerequisites like [1,0] (course 1 requires 0), determine if all courses can be finished.

**Solution:** If topological sort can order all n courses, answer is yes. Otherwise, cycle exists.

```python
def canFinish(numCourses, prerequisites):
    graph = [[] for _ in range(numCourses)]
    in_degree = [0] * numCourses
    
    for course, prereq in prerequisites:
        graph[prereq].append(course)
        in_degree[course] += 1
    
    queue = [i for i in range(numCourses) if in_degree[i] == 0]
    count = 0
    
    while queue:
        node = queue.pop(0)
        count += 1
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    
    return count == numCourses
```

### Example 2: Number of Islands (Connected Components)

**Problem:** Count distinct islands in a grid (1 = land, 0 = water).

**Solution:** DFS/BFS from each unvisited land cell, mark entire island as visited.

```python
def numIslands(grid):
    if not grid:
        return 0
    
    count = 0
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            if grid[i][j] == '1':
                dfs(grid, i, j)
                count += 1
    return count

def dfs(grid, i, j):
    if i < 0 or i >= len(grid) or j < 0 or j >= len(grid[0]) or grid[i][j] == '0':
        return
    grid[i][j] = '0'
    dfs(grid, i+1, j)
    dfs(grid, i-1, j)
    dfs(grid, i, j+1)
    dfs(grid, i, j-1)
```

### Example 3: Lowest Common Ancestor (Graph Traversal)

**Problem:** Find LCA of two nodes in a DAG.

**Solution:** Traverse from both nodes upward, mark visited ancestors, return first common.

```python
def lowestCommonAncestor(root, p, q):
    ancestors = set()
    
    def traverse(node):
        if not node:
            return
        ancestors.add(node)
        traverse(node.parent)
    
    traverse(p)
    
    while q:
        if q in ancestors:
            return q
        q = q.parent
    
    return None
```

## Graph Checklist

- ✓ Clarified: directed/undirected, weighted/unweighted, connected/disconnected
- ✓ Chose correct algorithm per decision tree
- ✓ Used adjacency list (not matrix)
- ✓ Handled disconnected components (loop over all nodes)
- ✓ Handled edge cases: empty graph, single node, self-loops
- ✓ Marked visited BEFORE enqueuing in BFS (avoid duplicates)
- ✓ Handled parent check in undirected DFS (avoid revisiting edge source)
- ✓ Tested on small hand-traced example
- ✓ Discussed time/space complexity
- ✓ Mentioned optimizations if time allows

