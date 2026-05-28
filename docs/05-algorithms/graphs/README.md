# Graph Algorithms — Fundamentals

**Level:** L4
**Time to read:** ~25 min

BFS, DFS, topological sort, and cycle detection — the four building blocks of graph problem solving.

> For advanced graph algorithms (Dijkstra, Bellman-Ford, MST, Floyd-Warshall), see `docs/05-algorithms/graphs/advanced/`.

---

## Graph Representations

```
Adjacency List (default choice):        Adjacency Matrix:
graph = {                               matrix[i][j] = 1 if edge i→j
    0: [1, 2],
    1: [2, 3],                          Use when: dense graph (E ≈ V²)
    2: [3],                             Space: O(V²)
    3: []
}
Use when: sparse graph (E << V²)
Space: O(V + E)
```

**Graph types:**

```
Undirected:   A — B — C          Directed (digraph):  A → B → C
              |       |                                ↑       ↓
              D ————— E                                D ←———— E

Weighted: edges carry numeric values (distances, costs)
DAG (Directed Acyclic Graph): directed + no cycles → enables topological sort
```

---

## Comparative Trade-off Table

| Algorithm | Best for | Time | Space | Handles disconnected? | Direction |
|-----------|---------|------|-------|----------------------|-----------|
| BFS | Shortest path (unweighted) | O(V+E) | O(V) | Yes (outer loop) | Both |
| DFS | Topological sort, cycle detection, connected components | O(V+E) | O(V) | Yes (outer loop) | Both |
| Iterative DFS | Same as DFS, avoids stack overflow | O(V+E) | O(V) | Yes | Both |
| Kahn's (BFS topo) | Topological sort + cycle detection | O(V+E) | O(V) | DAG only | Directed |

### Decision Framework

```
Shortest path (unweighted or uniform weights)?
  → BFS (guarantees minimum edge hops)

Explore all paths / detect cycle / connected components?
  → DFS (simpler recursion, less memory overhead for sparse graphs)

Large graph with risk of recursion depth limit?
  → Iterative DFS (explicit stack, no Python recursion limit)

Need ordering of tasks with dependencies?
  → Topological sort (Kahn's for cycle detection, DFS for simple ordering)

Check if directed graph has a cycle?
  → DFS with 3-color marking (white/gray/black) OR Kahn's (cycle ↔ leftover nodes)

Find shortest path in weighted graph?
  → Dijkstra (non-negative weights) → see advanced/
```

---

## Algorithm Implementations

### BFS (Breadth-First Search)

Explore level by level using a queue. Guarantees shortest path in unweighted graphs because it visits nodes in increasing order of distance from source.

**Complexity:** Time O(V+E) | Space O(V) for queue and visited set

```python
from collections import deque

def bfs(graph, start):
    visited = {start}
    queue = deque([start])
    order = []
    
    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)     # Mark BEFORE enqueue (critical!)
                queue.append(neighbor)
    
    return order

def bfs_shortest_path(graph, start, end):
    """Returns minimum number of edges from start to end, or -1."""
    if start == end:
        return 0
    visited = {start}
    queue = deque([(start, 0)])           # (node, distance)
    
    while queue:
        node, dist = queue.popleft()
        for neighbor in graph[node]:
            if neighbor == end:
                return dist + 1
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, dist + 1))
    return -1
```

**BFS for disconnected graphs:**
```python
def bfs_all_components(graph):
    visited = set()
    components = []
    for node in graph:
        if node not in visited:
            component = []
            queue = deque([node])
            visited.add(node)
            while queue:
                curr = queue.popleft()
                component.append(curr)
                for nb in graph[curr]:
                    if nb not in visited:
                        visited.add(nb)
                        queue.append(nb)
            components.append(component)
    return components
```

---

### DFS (Recursive)

Explore as deep as possible before backtracking. Natural for tree-like traversal, topological ordering, and cycle detection.

**Complexity:** Time O(V+E) | Space O(V) recursion stack

```python
def dfs(graph, start, visited=None):
    if visited is None:
        visited = set()
    visited.add(start)
    result = [start]
    for neighbor in graph[start]:
        if neighbor not in visited:
            result.extend(dfs(graph, neighbor, visited))
    return result

def dfs_all_components(graph):
    visited = set()
    components = []
    for node in graph:
        if node not in visited:
            component = []
            def explore(v):
                visited.add(v)
                component.append(v)
                for nb in graph[v]:
                    if nb not in visited:
                        explore(nb)
            explore(node)
            components.append(component)
    return components
```

---

### DFS (Iterative)

Same traversal order as recursive DFS using an explicit stack. Avoids Python's default 1000-frame recursion limit — use this for graphs with V > 10³.

**Complexity:** Time O(V+E) | Space O(V) explicit stack

```python
def dfs_iterative(graph, start):
    visited = set()
    stack = [start]
    result = []
    
    while stack:
        node = stack.pop()
        if node in visited:
            continue
        visited.add(node)
        result.append(node)
        for neighbor in graph[node]:       # Reversed for same order as recursive
            if neighbor not in visited:
                stack.append(neighbor)
    
    return result
```

Note: Iterative DFS with a stack produces a different ordering than recursive DFS because the stack reverses children order. For topological sort, use the recursive version with post-order tracking or Kahn's algorithm.

---

### Cycle Detection (Directed Graph)

Use 3-color DFS: white (unvisited) = 0, gray (in current path) = 1, black (fully processed) = 2. A back edge to a gray node indicates a cycle.

```python
def has_cycle_directed(graph):
    """Returns True if directed graph has a cycle."""
    color = {}   # 0=white, 1=gray, 2=black
    
    def dfs(node):
        color[node] = 1          # Mark gray (in current path)
        for neighbor in graph.get(node, []):
            if color.get(neighbor) == 1:
                return True      # Back edge → cycle
            if color.get(neighbor, 0) == 0:
                if dfs(neighbor):
                    return True
        color[node] = 2          # Mark black (fully processed)
        return False
    
    for node in graph:
        if color.get(node, 0) == 0:
            if dfs(node):
                return True
    return False

def has_cycle_undirected(graph):
    """Returns True if undirected graph has a cycle (using parent tracking)."""
    visited = set()
    
    def dfs(node, parent):
        visited.add(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                if dfs(neighbor, node):
                    return True
            elif neighbor != parent:     # Back edge (not to parent)
                return True
        return False
    
    for node in graph:
        if node not in visited:
            if dfs(node, -1):
                return True
    return False
```

---

### Topological Sort

**DFS-based:** Post-order DFS, push to stack when all descendants processed. Reverse stack = topological order.

```python
def topological_sort_dfs(graph):
    visited = set()
    stack = []
    
    def dfs(node):
        visited.add(node)
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                dfs(neighbor)
        stack.append(node)        # Post-order: add AFTER visiting all children
    
    for node in graph:
        if node not in visited:
            dfs(node)
    
    return stack[::-1]            # Reverse post-order = topological order
```

**Kahn's Algorithm (BFS-based):** Track in-degrees. Nodes with in-degree 0 are ready to process. Simultaneously detects cycles (if remaining nodes after processing = cycle).

```python
from collections import deque

def topological_sort_kahns(graph, num_nodes=None):
    """
    graph: dict of node → list of neighbors (directed)
    Returns: topological order list, or [] if cycle detected
    """
    in_degree = {}
    for node in graph:
        in_degree.setdefault(node, 0)
        for neighbor in graph[node]:
            in_degree[neighbor] = in_degree.get(neighbor, 0) + 1
    
    queue = deque([n for n in in_degree if in_degree[n] == 0])
    order = []
    
    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor in graph.get(node, []):
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    
    # Cycle detected if we couldn't process all nodes
    if len(order) < len(in_degree):
        return []   # Cycle exists
    return order
```

---

## Worked Problems

### Problem 1: Number of Islands (LeetCode #200)

**Clarifying Questions:**
- Grid contains only '1' (land) and '0' (water)? → Yes
- Is the grid rectangular? → Yes
- Do we count diagonally connected land? → No, only 4-directional

**Brute Force:** Scan every cell, BFS/DFS each unvisited land cell.

**Optimization:** This IS the optimal approach — O(m×n) time where m, n are grid dimensions. Mark visited by changing '1' to '0' (or use a separate visited set).

**Edge Cases:**
- All water → return 0
- All land → return 1 (one large island)
- Single cell grid → depends on cell value

**Code (BFS):**
```python
from collections import deque

def numIslands(grid):
    if not grid:
        return 0
    
    rows, cols = len(grid), len(grid[0])
    count = 0
    
    def bfs(r, c):
        queue = deque([(r, c)])
        grid[r][c] = '0'              # Mark visited immediately
        while queue:
            row, col = queue.popleft()
            for dr, dc in [(0,1),(0,-1),(1,0),(-1,0)]:
                nr, nc = row + dr, col + dc
                if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == '1':
                    grid[nr][nc] = '0'
                    queue.append((nr, nc))
    
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == '1':
                bfs(r, c)
                count += 1
    
    return count
```

**Time:** O(m×n) | **Space:** O(min(m,n)) for BFS queue (worst case diagonal wave)

**Follow-ups:**
- What if the grid is too large to hold in memory? → Streaming approach with Union-Find
- Count islands where diagonals count? → Add 4 diagonal directions
- Max island size? → Track size during BFS, return global max (LeetCode #695)

---

### Problem 2: Course Schedule (LeetCode #207)

**Clarifying Questions:**
- Can there be duplicate prerequisites? → Yes (handle gracefully)
- Are course numbers 0-indexed? → Yes, 0 to numCourses-1
- Return true if possible to complete all courses? → Yes

**Brute Force:** Try all orderings, check if any is valid — factorial time.

**Optimization:** Cycle detection in directed graph. If prerequisites form a cycle, courses are impossible.

**Edge Cases:**
- No prerequisites → always possible (return True)
- Self-dependency [[0, 0]] → cycle, return False
- Disconnected graph → handle with outer loop over all nodes

**Code (Kahn's — cycle detection via topological sort):**
```python
from collections import deque

def canFinish(numCourses, prerequisites):
    graph = [[] for _ in range(numCourses)]
    in_degree = [0] * numCourses
    
    for course, prereq in prerequisites:
        graph[prereq].append(course)
        in_degree[course] += 1
    
    queue = deque([i for i in range(numCourses) if in_degree[i] == 0])
    completed = 0
    
    while queue:
        course = queue.popleft()
        completed += 1
        for next_course in graph[course]:
            in_degree[next_course] -= 1
            if in_degree[next_course] == 0:
                queue.append(next_course)
    
    return completed == numCourses  # All courses processed = no cycle
```

**Time:** O(V+E) where V=numCourses, E=len(prerequisites) | **Space:** O(V+E)

**Follow-ups:**
- Return the actual course order (LeetCode #210)? → Store order in topological sort result
- What if some prerequisites are optional? → Model as separate graph, different traversal
- What if the same prerequisite appears multiple times? → Deduplicate edges or handle duplicates in in_degree

---

### Problem 3: Word Ladder (LeetCode #127)

**Clarifying Questions:**
- Can we reuse words? → No (each word used at most once)
- Is the transformation case-sensitive? → Yes
- Return 0 if no transformation sequence? → Yes
- Begin word might not be in wordList? → Correct; end word must be in wordList

**Brute Force:** DFS through all paths — exponential.

**Optimization:** BFS from beginWord — guarantees shortest transformation sequence. Key insight: treat each word as a node, words differing by one letter as edges.

**Building the graph efficiently:** For each word, replace each character with a-z wildcards and group by pattern. This avoids O(n²) edge building.

**Edge Cases:**
- endWord not in wordList → return 0 immediately
- beginWord == endWord → return 1 (or handle per constraints)
- No word in list differs by one character from beginWord → return 0

**Code:**
```python
from collections import deque, defaultdict

def ladderLength(beginWord, endWord, wordList):
    wordSet = set(wordList)
    if endWord not in wordSet:
        return 0
    
    # Build adjacency: pattern → list of matching words
    # e.g., "h*t" → ["hot", "hat", "hit"]
    L = len(beginWord)
    pattern_map = defaultdict(list)
    for word in wordList:
        for i in range(L):
            pattern = word[:i] + '*' + word[i+1:]
            pattern_map[pattern].append(word)
    
    queue = deque([(beginWord, 1)])   # (word, level)
    visited = {beginWord}
    
    while queue:
        word, level = queue.popleft()
        for i in range(L):
            pattern = word[:i] + '*' + word[i+1:]
            for neighbor in pattern_map[pattern]:
                if neighbor == endWord:
                    return level + 1
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, level + 1))
    
    return 0
```

**Time:** O(M²×N) where M=word length, N=wordList size | **Space:** O(M²×N)

**Follow-ups:**
- Return all shortest transformation sequences (#126)? → BFS layer by layer, backtrack paths
- What if words can differ by 2 characters? → Build graph differently, BFS still works
- Bidirectional BFS for speedup? → Start BFS from both ends, stop when frontiers meet

---

## Common Mistakes

**1. Not marking visited BEFORE enqueue in BFS**
```python
# BAD: Mark when dequeued — same node added to queue multiple times
if neighbor not in visited:
    queue.append(neighbor)
    # visited.add(neighbor)  ← happens later when dequeued

# GOOD: Mark when enqueued — prevents duplicates in queue
if neighbor not in visited:
    visited.add(neighbor)    # Mark immediately
    queue.append(neighbor)
```

**2. Forgetting to handle disconnected graphs**
```python
# BAD: Only starts BFS/DFS from node 0
dfs(graph, 0)

# GOOD: Loop over all nodes to catch disconnected components
for node in graph:
    if node not in visited:
        dfs(graph, node, visited)
```

**3. Using DFS for shortest path**
DFS does NOT guarantee shortest path — it finds A path, not the shortest. Always use BFS for shortest path in unweighted graphs.

**4. Cycle detection: confusing undirected and directed**
```python
# Undirected: a back edge to parent is NOT a cycle
# You must track parent and ignore the edge back to parent
def dfs(node, parent):
    for nb in graph[node]:
        if nb != parent and nb in visited:  # Back edge (not parent) = cycle

# Directed: back edge to any gray (in-stack) node = cycle
# No parent concept; use 3-color marking
```

**5. Building graph with wrong direction**
```python
# Course Schedule: edge goes from prereq TO course (not course TO prereq)
# If A is prerequisite for B: graph[A].append(B), in_degree[B] += 1
for course, prereq in prerequisites:
    graph[prereq].append(course)   # Direction: prereq → course
    in_degree[course] += 1
```

**6. Not handling nodes with no outgoing edges in adjacency dict**
```python
# If building graph with dict, nodes with no edges may not appear as keys
graph.get(node, [])   # Safe default to empty list
# Or use defaultdict(list)
```

---

## Interview Q&A

**Q1: When would you use BFS over DFS?**
Use BFS when you need shortest path in an unweighted graph (BFS guarantees minimum hops). Use DFS when exploring all paths, doing topological sort, detecting cycles, or when the graph is a tree (DFS maps naturally to recursion). BFS uses more memory (entire frontier level) while DFS uses stack depth.

**Q2: What is the time complexity of BFS and DFS? Why?**
Both are O(V+E). Each vertex is visited once (O(V)), and each edge is examined once from each endpoint (O(E) total). The visited set ensures no vertex is processed twice.

**Q3: Why does Kahn's algorithm detect cycles?**
Kahn's starts with all nodes of in-degree 0. Each processed node reduces its neighbors' in-degrees. A cycle means every node in the cycle has in-degree ≥ 1 permanently (they depend on each other), so they never enter the queue. If processed count < V at the end, the remaining nodes form cycles.

**Q4: What is topological sort and when can you use it?**
Topological sort produces a linear ordering of vertices in a DAG such that for every directed edge u→v, u comes before v. It only works on DAGs (directed acyclic graphs). Used for: build systems (compile order), course scheduling, task dependency resolution, spreadsheet cell evaluation.

**Q5: How do you handle a graph where nodes are strings (like Word Ladder)?**
Use a dictionary or set as the visited structure instead of a boolean array. Build the adjacency list using the string nodes as keys. The algorithm is identical — just replace integer node IDs with string node IDs. For efficient neighbor finding, use wildcard patterns rather than O(n²) pairwise comparison.

**Q6: BFS on a grid vs on an explicit graph — any differences?**
The logic is identical, but grids use directional offsets instead of an adjacency list. Instead of `for nb in graph[node]`, you write `for dr, dc in directions: nr, nc = r+dr, c+dc`. Always check bounds and whether the cell is valid/unvisited before enqueueing.
