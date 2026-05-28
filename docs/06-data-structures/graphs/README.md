# Graphs — Adjacency Lists, BFS/DFS, Topological Sort

**Level:** L4-L5
**Time to read:** ~25 min

The most general data structure. Trees are graphs. Grids are graphs. Dependency chains are graphs. Master graph traversal and a huge class of problems becomes approachable.

---

## Quick Summary

A graph is a set of vertices (nodes) connected by edges. Unlike trees, graphs can have cycles, multiple paths between nodes, and disconnected components. Represent with adjacency list (sparse graphs) or adjacency matrix (dense graphs). BFS finds shortest path in unweighted graphs; DFS finds connected components, cycles, and topological order. Time: O(V+E) for traversal.

---

## Operations & Complexity Table

| Operation              | Adjacency List | Adjacency Matrix | Notes                           |
|------------------------|---------------|-----------------|----------------------------------|
| Add vertex             | O(1)          | O(V²) rebuild   | Matrix requires fixed V           |
| Add edge               | O(1)          | O(1)            | List: append; matrix: set bit    |
| Check edge(u, v)       | O(degree(u))  | O(1)            | Matrix wins for dense graphs     |
| Neighbors of u         | O(degree(u))  | O(V)            | List wins for sparse graphs      |
| BFS / DFS              | O(V + E)      | O(V²)           | Matrix must scan all V neighbors |
| Space                  | O(V + E)      | O(V²)           | List wins unless graph is dense  |
| Topological sort       | O(V + E)      | O(V²)           | Kahn's or DFS-based              |

---

## Memory Layout / Internal Structure

```
Graph: 5 nodes (0-4), edges: 0→1, 0→2, 1→3, 2→3, 3→4

Adjacency List (sparse — standard choice):
  0: [1, 2]
  1: [3]
  2: [3]
  3: [4]
  4: []

  Space: O(V + E) = O(5 + 5) = O(10)
  List[u] gives neighbors in O(degree(u))

Adjacency Matrix (dense):
       0  1  2  3  4
  0  [ 0  1  1  0  0 ]
  1  [ 0  0  0  1  0 ]
  2  [ 0  0  0  1  0 ]
  3  [ 0  0  0  0  1 ]
  4  [ 0  0  0  0  0 ]

  Space: O(V²) = O(25)
  matrix[u][v] = 1 means edge exists — O(1) lookup

Graph Taxonomy:
  Undirected: edge(u,v) = edge(v,u)
  Directed:   edge(u,v) ≠ edge(v,u) (one-way)
  Weighted:   edges have costs/distances
  Unweighted: all edges equal
  Cyclic:     contains at least one cycle
  Acyclic:    no cycles (DAG = Directed Acyclic Graph)

BFS Queue State (on graph above, start=0):
  Init:   queue=[0],     visited={0}
  Pop 0:  queue=[1,2],   visited={0,1,2}
  Pop 1:  queue=[2,3],   visited={0,1,2,3}
  Pop 2:  queue=[3],     (3 already visited)
  Pop 3:  queue=[4],     visited={0,1,2,3,4}
  Pop 4:  queue=[], done
```

---

## Trade-offs vs Alternatives

| Representation      | Adjacency List   | Adjacency Matrix  | Edge List           |
|---------------------|------------------|-------------------|---------------------|
| Space               | O(V + E)         | O(V²)             | O(E)                |
| Check edge u→v      | O(degree)        | O(1)              | O(E)                |
| All neighbors of u  | O(degree)        | O(V)              | O(E)                |
| Add edge            | O(1)             | O(1)              | O(1)                |
| Dense graph (E≈V²)  | Wastes nothing   | Good fit          | Impractical         |
| Sparse graph (E≈V)  | Best             | 99% wasted        | Simple for offline  |
| BFS/DFS             | O(V+E)           | O(V²)             | O(V×E) naive        |

```
When to choose representation:
┌─────────────────────────────────────────────────────────────────────┐
│ Sparse graph (social network, city map)?  → Adjacency List         │
│ Dense graph (V nodes, ~V² edges)?         → Adjacency Matrix       │
│ Just need "does edge exist?", many checks → Adjacency Matrix       │
│ One-time offline algorithm (Kruskal)?     → Edge List              │
│ Grid / 2D matrix problems?                → Implicit adjacency     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## When NOT to Use

- **Strict hierarchy without cycles** — a tree is simpler and more efficient.
- **When all edges go in one direction with no back edges** — this is a DAG; use topological sort.
- **Adjacency matrix for sparse graphs** — 99% of matrix would be zeros; wastes O(V²) space.
- **DFS for shortest path in unweighted graph** — BFS guarantees shortest path; DFS does not.
- **BFS for topological sort** — Kahn's algorithm (BFS-based) works, but DFS-based is more intuitive; both O(V+E).

---

## Core Operations (Code)

```python
from collections import deque, defaultdict
from typing import Optional

# ── Graph Representations ─────────────────────────────────────────────────────

# Adjacency List (most common for interviews)
graph = defaultdict(list)
graph[0].extend([1, 2])
graph[1].append(3)
graph[2].append(3)
graph[3].append(4)

# From edge list
def build_graph(n: int, edges: list[list[int]]) -> dict:
    adj = defaultdict(list)
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)   # omit for directed graph
    return adj

# ── BFS — Shortest Path (unweighted) ─────────────────────────────────────────

def bfs(graph: dict, start: int) -> dict[int, int]:
    # Returns shortest distance from start to each reachable node
    dist    = {start: 0}
    queue   = deque([start])
    while queue:
        node = queue.popleft()
        for neighbor in graph[node]:
            if neighbor not in dist:
                dist[neighbor] = dist[node] + 1
                queue.append(neighbor)
    return dist

# ── DFS — Connected Components ────────────────────────────────────────────────

def dfs(graph: dict, node: int, visited: set) -> None:
    visited.add(node)
    for neighbor in graph[node]:
        if neighbor not in visited:
            dfs(graph, neighbor, visited)

def count_components(n: int, edges: list[list[int]]) -> int:
    graph = build_graph(n, edges)
    visited = set()
    count = 0
    for node in range(n):
        if node not in visited:
            dfs(graph, node, visited)
            count += 1
    return count

# ── Cycle Detection (Directed Graph) ─────────────────────────────────────────

def has_cycle_directed(graph: dict, n: int) -> bool:
    # DFS with 3-color: WHITE=0, GRAY=1 (in stack), BLACK=2 (done)
    color = [0] * n

    def dfs_cycle(node: int) -> bool:
        color[node] = 1        # GRAY: currently being explored
        for neighbor in graph[node]:
            if color[neighbor] == 1:   # back edge → cycle
                return True
            if color[neighbor] == 0 and dfs_cycle(neighbor):
                return True
        color[node] = 2        # BLACK: fully explored
        return False

    return any(color[i] == 0 and dfs_cycle(i) for i in range(n))

# ── Topological Sort — Kahn's Algorithm (BFS) ────────────────────────────────

def topological_sort_kahn(n: int, edges: list[list[int]]) -> list[int]:
    in_degree = [0] * n
    graph     = defaultdict(list)
    for u, v in edges:
        graph[u].append(v)
        in_degree[v] += 1

    queue = deque(i for i in range(n) if in_degree[i] == 0)
    order = []
    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    return order if len(order) == n else []   # empty = cycle detected

# ── Topological Sort — DFS-based ─────────────────────────────────────────────

def topological_sort_dfs(n: int, edges: list[list[int]]) -> list[int]:
    graph   = defaultdict(list)
    for u, v in edges:
        graph[u].append(v)
    visited = set()
    stack   = []

    def dfs_topo(node: int) -> None:
        visited.add(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                dfs_topo(neighbor)
        stack.append(node)    # add AFTER all descendants processed

    for i in range(n):
        if i not in visited:
            dfs_topo(i)

    return stack[::-1]        # reverse: first in stack = processed last = has no dependencies
```

---

## 3 Worked Problems

---

### Problem 1 — Number of Islands (LeetCode #200)

**Clarifying Questions**
- Grid contains only '1' (land) and '0' (water)? (Yes)
- Can an island be a single cell? (Yes)
- Connected means 4-directional (up/down/left/right)? (Yes — not diagonal)
- Can I modify the grid in place? (Yes — mark visited)

**Brute Force**

Track visited array; DFS from each unvisited land cell.

**Optimal**

Same approach but mark visited by mutating the grid (avoids extra O(m×n) space).

```python
def num_islands(grid: list[list[str]]) -> int:
    if not grid:
        return 0
    rows, cols = len(grid), len(grid[0])
    count = 0

    def dfs(r: int, c: int) -> None:
        if r < 0 or r >= rows or c < 0 or c >= cols or grid[r][c] != '1':
            return
        grid[r][c] = '#'     # mark visited (avoid revisit)
        dfs(r+1, c); dfs(r-1, c); dfs(r, c+1); dfs(r, c-1)

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == '1':
                dfs(r, c)
                count += 1

    return count
```

**Edge Cases**
- All water → 0
- All land → 1 (one giant island)
- Single cell grid → 0 or 1

**Complexity**
- Time: O(m × n) — each cell visited at most once
- Space: O(m × n) recursion stack in worst case (all land)

**Follow-ups**
- "Max area of island?" → LeetCode #695; return size from DFS instead of count.
- "Number of distinct islands?" → LeetCode #694; encode island shape as string.
- "Count islands with BFS?" → Replace DFS with BFS queue; same complexity.

---

### Problem 2 — Course Schedule (LeetCode #207)

**Clarifying Questions**
- `prerequisites[i] = [a, b]` means "to take a, must finish b first"? (Yes, b→a)
- Can there be duplicate prerequisites? (Problem says no, but handle safely)
- Can numCourses be 0? (Yes — return True)
- Return: can you finish all courses? (Yes/No — detect if DAG)

**Brute Force**

Try all topological orderings — exponential, impractical.

**Optimal — Kahn's Algorithm (BFS, detect cycle)**

```python
from collections import deque

def can_finish(numCourses: int, prerequisites: list[list[int]]) -> bool:
    in_degree = [0] * numCourses
    graph     = defaultdict(list)

    for course, prereq in prerequisites:
        graph[prereq].append(course)
        in_degree[course] += 1

    # Start with all courses that have no prerequisites
    queue = deque(i for i in range(numCourses) if in_degree[i] == 0)
    completed = 0

    while queue:
        course = queue.popleft()
        completed += 1
        for next_course in graph[course]:
            in_degree[next_course] -= 1
            if in_degree[next_course] == 0:
                queue.append(next_course)

    return completed == numCourses   # True if all courses completed (no cycle)
```

Alternative — DFS cycle detection:

```python
def can_finish_dfs(numCourses: int, prerequisites: list[list[int]]) -> bool:
    graph = defaultdict(list)
    for course, prereq in prerequisites:
        graph[prereq].append(course)

    # 0=unvisited, 1=in-progress (gray), 2=done (black)
    state = [0] * numCourses

    def has_cycle(node: int) -> bool:
        if state[node] == 1: return True    # back edge → cycle
        if state[node] == 2: return False   # already verified safe
        state[node] = 1
        for neighbor in graph[node]:
            if has_cycle(neighbor):
                return True
        state[node] = 2
        return False

    return not any(has_cycle(i) for i in range(numCourses) if state[i] == 0)
```

**Edge Cases**
- No prerequisites → always True
- Self-loop `[0, 0]` → cycle detected immediately
- Disconnected components → Kahn's handles (processes each component)

**Complexity**
- Time: O(V + E) — V=numCourses, E=prerequisites
- Space: O(V + E) — graph + in_degree

**Follow-ups**
- "Return actual order?" → LeetCode #210; collect `order` list in Kahn's.
- "Multiple valid orderings?" → All topological sorts of the DAG.

---

### Problem 3 — Clone Graph (LeetCode #133)

**Clarifying Questions**
- What is the node structure? (`val` + `neighbors` list)
- Is the graph connected? (Yes — only one connected component)
- Can there be self-loops? (No per problem constraints)
- Return: deep copy of entire graph? (Yes)

**Brute Force**

Two passes: first create all cloned nodes, then wire up neighbors.

**Optimal**

BFS/DFS with hash map (original node → clone node) to handle cycles and revisits.

```python
from typing import Optional

class Node:
    def __init__(self, val=0, neighbors=None):
        self.val       = val
        self.neighbors = neighbors or []

def clone_graph(node: Optional['Node']) -> Optional['Node']:
    if not node:
        return None

    cloned = {}                         # original → clone

    def dfs(n: Node) -> Node:
        if n in cloned:
            return cloned[n]            # already cloned → return existing clone
        copy = Node(n.val)
        cloned[n] = copy                # register BEFORE recursing (handles cycles)
        for neighbor in n.neighbors:
            copy.neighbors.append(dfs(neighbor))
        return copy

    return dfs(node)

# BFS version:
def clone_graph_bfs(node: Optional['Node']) -> Optional['Node']:
    if not node:
        return None
    cloned = {node: Node(node.val)}
    queue  = deque([node])
    while queue:
        curr = queue.popleft()
        for neighbor in curr.neighbors:
            if neighbor not in cloned:
                cloned[neighbor] = Node(neighbor.val)
                queue.append(neighbor)
            cloned[curr].neighbors.append(cloned[neighbor])
    return cloned[node]
```

**Edge Cases**
- Single node, no neighbors → return a new node with same val
- Graph with cycle (A→B→A) → hash map prevents infinite recursion
- Disconnected? → Problem guarantees connected; if not, BFS from all nodes

**Complexity**
- Time: O(V + E) — each node and edge visited once
- Space: O(V) hash map + O(V) recursion/queue

**Follow-ups**
- "Clone directed graph?" → Same approach; don't add reverse edges.
- "Serialize/deserialize graph?" → BFS with adjacency list format.

---

## Interview Q&A

**Q1: Adjacency list vs adjacency matrix — how do you choose?**

A:
```
Adjacency List (default choice):
  - Space: O(V + E) — great for sparse graphs (E << V²)
  - Enumerate neighbors: O(degree(u)) — only real neighbors
  - Check edge u→v: O(degree(u)) — scan neighbor list
  - When: social networks, city maps, dependency graphs

Adjacency Matrix:
  - Space: O(V²) — only practical for dense graphs (E ≈ V²)
  - Enumerate neighbors: O(V) — must scan all V columns
  - Check edge u→v: O(1) — direct array lookup
  - When: small V (< ~1000), frequent edge existence checks, Floyd-Warshall

Rule: default to adjacency list. Switch to matrix only if V is small
AND you need O(1) edge queries.
```

---

**Q2: BFS vs DFS — when does each give the right answer?**

A:
```
BFS (Level-order):
  ✓ Shortest path in unweighted graph (by edge count)
  ✓ All nodes at distance k from source
  ✓ Connected components (same as DFS)
  ✓ Topological sort (Kahn's algorithm)
  ✗ Doesn't find topological order naturally
  Space: O(V) queue

DFS:
  ✓ Topological sort (natural via finish times)
  ✓ Cycle detection (back edge = cycle)
  ✓ Strongly connected components (Tarjan/Kosaraju)
  ✓ Path problems (all paths, maze traversal)
  ✗ NOT shortest path (may find longer path first)
  Space: O(V) stack

Shortest path weighted: Dijkstra (non-negative) or Bellman-Ford (negative edges)
```

---

**Q3: How do you detect a cycle in a directed vs undirected graph?**

A:
```
Directed graph (DFS, 3-color):
  - WHITE (0): not visited
  - GRAY (1):  currently in DFS stack (being explored)
  - BLACK (2): fully explored
  - Cycle detected when you visit a GRAY node (back edge)
  - O(V + E)

Undirected graph (DFS, parent tracking):
  - Track parent to avoid false "cycle" from bidirectional edge
  - Cycle if you visit a visited node that isn't your parent
  def has_cycle(node, parent, visited):
      visited.add(node)
      for neighbor in graph[node]:
          if neighbor not in visited:
              if has_cycle(neighbor, node, visited): return True
          elif neighbor != parent:
              return True     # real back edge
      return False

Alternative for both: Union-Find (elegant for undirected)
  - Union each edge; if find(u) == find(v) before union → cycle
```

---

**Q4: What is topological sort and when is it used?**

A: Topological sort is a linear ordering of vertices in a DAG such that for every directed edge u→v, u comes before v. It only exists for DAGs (cycles make it impossible). Real-world uses: course prerequisites (take prereq before course), build systems (compile dependency before dependent), task scheduling (task A before task B).

Two approaches: (1) Kahn's BFS — process nodes with in-degree 0; if all nodes processed → valid toposort, else cycle. (2) DFS — recursively process all dependencies first, push node to stack after; reverse stack is toposort.

---

**Q5: What is the time complexity of BFS/DFS and why?**

A: O(V + E) for both with adjacency list. Each vertex is added to the queue/stack exactly once (O(V)). Each edge is traversed exactly once when processing its source vertex's neighbor list (O(E)). With adjacency matrix, neighbor enumeration costs O(V) per vertex, giving O(V²) total. This is why adjacency list is preferred for sparse graphs.

---

**Q6: How do you handle disconnected graphs in BFS/DFS?**

A: Run BFS/DFS from every unvisited vertex. The outer loop ensures all components are covered:

```python
visited = set()
for node in range(n):
    if node not in visited:
        bfs(graph, node, visited)    # or dfs()
```

This is the pattern for "number of connected components": count how many times you start a new traversal.

---

**Q7: How does Dijkstra's algorithm differ from BFS?**

A:
```
BFS:
  - All edges have equal weight (weight = 1)
  - Queue: FIFO deque
  - Gives shortest path by edge count
  - O(V + E)

Dijkstra:
  - Weighted edges (must be non-negative)
  - Queue: min-heap (priority queue keyed by distance)
  - Gives shortest path by total weight
  - O((V + E) log V) with binary heap

The key difference: BFS explores nodes in order of hop count;
Dijkstra explores in order of accumulated weight.

If weights are negative: Bellman-Ford O(V×E)
If graph is a DAG: relax edges in topological order O(V+E)
```

---

**Q8: What is a strongly connected component (SCC)?**

A: In a directed graph, an SCC is a maximal set of vertices where every vertex is reachable from every other vertex. Example: if A→B→C→A, all three form one SCC. Finding SCCs is done by Kosaraju's algorithm (two DFS passes, O(V+E)) or Tarjan's algorithm (one DFS with low-link values, O(V+E)). Used in: compiler optimization, web crawling (identify clusters of mutually-linking pages), deadlock detection.

---

**Q9: When would you use BFS on a grid vs DFS?**

A:
```
Grid problems where BFS wins:
  - Minimum steps to reach target (shortest path)
  - "Spread" problems: rot oranges (#994), walls and gates (#286)
  - Level-by-level expansion

Grid problems where DFS wins:
  - Connected components (number of islands #200)
  - Flood fill (#733)
  - Marking entire connected regions
  - "Reachability" without caring about distance

Both work for connectivity; BFS is mandatory for minimum distance.
Rule: "minimum steps" → BFS. "Does path exist?" → either.
```

---

## Interview Tips

- **Draw the graph.** Even for small examples (4 nodes, 3 edges), sketch it. Errors in graph problems usually come from mental model mistakes.
- **Visited set is mandatory.** Every BFS/DFS must track visited nodes or you'll loop forever on cycles. Forget this and you'll get infinite loops.
- **Topological sort = Kahn's for interviews.** It's the cleaner code and naturally detects cycles (if `completed != numCourses`, there's a cycle). DFS version is trickier to get right.
- **Grid = implicit graph.** When you see a 2D grid with connectivity questions, it's a graph problem. BFS/DFS from each cell; neighbors are up/down/left/right.
- **State the complexity in V+E terms.** "This runs in O(V+E) time and O(V) space for the visited set" immediately signals you understand graph analysis.
- **Cycle detection pattern.** For directed graphs: 3-color DFS (white/gray/black). For undirected: track parent. For either: Union-Find is elegant.
