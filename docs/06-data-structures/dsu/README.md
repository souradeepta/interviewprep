# Disjoint Set Union (Union-Find) — Near-O(1) Connected Components

**Level:** L4-L5
**Time to read:** ~20 min

Elegant solution for "are these two nodes in the same group?" when groups merge but never split.

---

## Quick Summary

DSU (Union-Find) maintains a collection of disjoint sets with two operations: `find` (which component does x belong to?) and `union` (merge the components of x and y). With path compression and union by rank, both operations run in near-O(1) amortized time — technically O(α(n)) where α is the inverse Ackermann function, effectively constant for all practical inputs. Use for: connected components, cycle detection in undirected graphs, and any problem where groups merge but never split.

---

## Operations & Complexity Table

| Operation           | Naive (no opt.) | Path Compression | Path Comp + Union by Rank |
|---------------------|----------------|-----------------|--------------------------|
| find(x)             | O(n) worst      | O(log n) amort. | O(α(n)) ≈ O(1) amort.   |
| union(x, y)         | O(n) worst      | O(log n) amort. | O(α(n)) ≈ O(1) amort.   |
| connected(x, y)     | O(n)            | O(log n)        | O(α(n))                  |
| Build n unions      | O(n²) worst     | O(n log n)      | O(n × α(n)) ≈ O(n)      |
| Space               | O(n)            | O(n)            | O(n)                     |

α(n) = inverse Ackermann function; α(10^80) = 4. Practically constant.

---

## Memory Layout / Internal Structure

```
DSU for nodes {0,1,2,3,4} — initial state (each is its own component):

parent: [0, 1, 2, 3, 4]   (parent[i] = i means i is a root)
rank:   [0, 0, 0, 0, 0]

After union(0,1), union(1,2):
parent: [0, 0, 0, 3, 4]   (1→0, 2→0; rank[0] becomes 1)
rank:   [1, 0, 0, 0, 0]

Tree view:
    0
   / \
  1   2   3   4
  (3 components: {0,1,2}, {3}, {4})

After union(3,4):
parent: [0, 0, 0, 3, 3]
rank:   [1, 0, 0, 1, 0]

Tree view:
    0       3
   / \     / 
  1   2   4  
  (2 components)

Path Compression: find(2) before compression:
  2 → parent[2]=0 → root is 0

find(2) WITH compression:
  Traverse: 2→0 (already root)
  (no change needed since 2's parent is already root)

find(2) on deeper tree: 2→1→0
  After: parent[2] = 0 directly (path compressed)
  Future find(2) = O(1) direct lookup

Union by Rank: always attach smaller tree under root of larger tree.
  rank[0] > rank[3] → parent[3] = 0  (not parent[0] = 3)
  Keeps tree height minimal → log n worst case without path compression
```

---

## Trade-offs vs Alternatives

| Operation                       | DSU              | BFS/DFS          | Notes                               |
|---------------------------------|------------------|------------------|-------------------------------------|
| Connected(x, y) query           | O(α(n))          | O(V+E) per query | DSU amortizes across many queries   |
| All connected components        | O(n×α(n))        | O(V+E)           | Both linear; DSU simpler for merges |
| Dynamic edge additions          | O(α(n)) per edge | Rebuild: O(V+E)  | DSU handles online updates          |
| Cycle detection (undirected)    | O(E×α(V))        | O(V+E)           | DSU elegant; BFS/DFS equivalent     |
| Directed graph components       | Not applicable   | O(V+E) DFS       | DSU only for undirected             |
| Edge deletion                   | Not supported    | O(V+E) rebuild   | DSU is union-only (no split)        |
| Minimum spanning tree (Kruskal) | O(E log E + E×α(V)) | N/A           | DSU cycle check is the bottleneck   |

```
When to choose DSU:
┌─────────────────────────────────────────────────────────────────────┐
│ Repeated "are x and y connected?" queries?     → DSU               │
│ Edges added online, components merge over time?→ DSU               │
│ Cycle detection in undirected graph?           → DSU (elegant)     │
│ Kruskal's MST?                                 → DSU required      │
│ Need to handle directed graphs?                → BFS/DFS           │
│ Need to detect connected components once?      → BFS/DFS simpler   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## When NOT to Use

- **Directed graphs** — DSU is fundamentally undirected. Edge direction is ignored in union; use BFS/DFS for directed component detection.
- **When components split** — DSU is union-only. Once merged, sets can't be separated. Use link-cut trees for fully dynamic connectivity.
- **Single query on sparse graph** — if you only need connectivity once, BFS/DFS from the source is simpler.
- **When you need the actual path** — DSU only answers "same component?"; it doesn't store or return paths. Use BFS for path reconstruction.
- **When you need all edges in a component** — DSU tracks which nodes belong together but not which edges connect them.

---

## Core Operations (Code)

```python
# ── DSU with Path Compression + Union by Rank ────────────────────────────────

class DSU:
    def __init__(self, n: int):
        self.parent = list(range(n))   # parent[i] = i: i is its own root
        self.rank   = [0] * n          # rank[i]: approximate height of tree rooted at i
        self.components = n            # number of distinct components

    def find(self, x: int) -> int:
        # Path compression: make all nodes on path point directly to root
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])   # recursive compression
        return self.parent[x]

    def union(self, x: int, y: int) -> bool:
        # Returns True if x and y were in different components (merge happened)
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False               # already connected
        # Union by rank: attach smaller tree under larger tree
        if self.rank[rx] < self.rank[ry]:
            rx, ry = ry, rx            # ensure rx has higher (or equal) rank
        self.parent[ry] = rx           # attach ry's tree under rx
        if self.rank[rx] == self.rank[ry]:
            self.rank[rx] += 1         # same rank → result is one taller
        self.components -= 1
        return True

    def connected(self, x: int, y: int) -> bool:
        return self.find(x) == self.find(y)


# ── Iterative find (avoids recursion limit for large n) ──────────────────────

def find_iterative(parent: list[int], x: int) -> int:
    root = x
    while parent[root] != root:
        root = parent[root]            # find root
    while parent[x] != root:          # path compression
        parent[x], x = root, parent[x]
    return root


# ── Path compression variants ─────────────────────────────────────────────────
# Full compression (recursive): parent[x] = root  → best amortized
# Path halving: parent[x] = parent[parent[x]]  → same amortized, iterative
# Path splitting: every node on path points to grandparent → similar

def find_path_halving(parent: list[int], x: int) -> int:
    while parent[x] != x:
        parent[x] = parent[parent[x]]   # skip one level
        x = parent[x]
    return x


# ── Quick DSU template (interview-ready, 10 lines) ────────────────────────────

def make_dsu(n):
    parent = list(range(n))
    rank   = [0] * n

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]   # path halving
            x = parent[x]
        return x

    def union(x, y):
        rx, ry = find(x), find(y)
        if rx == ry: return False
        if rank[rx] < rank[ry]: rx, ry = ry, rx
        parent[ry] = rx
        if rank[rx] == rank[ry]: rank[rx] += 1
        return True

    return find, union
```

---

## 3 Worked Problems

---

### Problem 1 — Number of Connected Components (LeetCode #323)

**Clarifying Questions**
- Undirected graph? (Yes)
- n nodes (0 to n-1), list of undirected edges? (Yes)
- No self-loops? (Assume not, but DSU handles them)

**Brute Force**

BFS/DFS counting separate traversals.

```python
from collections import defaultdict

def count_components_bfs(n: int, edges: list[list[int]]) -> int:
    graph = defaultdict(list)
    for u, v in edges:
        graph[u].append(v)
        graph[v].append(u)
    visited = set()
    count = 0
    for node in range(n):
        if node not in visited:
            # BFS
            queue = [node]
            visited.add(node)
            while queue:
                curr = queue.pop()
                for nb in graph[curr]:
                    if nb not in visited:
                        visited.add(nb)
                        queue.append(nb)
            count += 1
    return count
```

**Optimization**

DSU: start with n components, decrement on each successful union.

```python
def count_components(n: int, edges: list[list[int]]) -> int:
    parent = list(range(n))
    rank   = [0] * n

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        rx, ry = find(x), find(y)
        if rx == ry: return False
        if rank[rx] < rank[ry]: rx, ry = ry, rx
        parent[ry] = rx
        if rank[rx] == rank[ry]: rank[rx] += 1
        return True

    components = n
    for u, v in edges:
        if union(u, v):
            components -= 1
    return components
```

**Edge Cases**
- No edges → n components (each node isolated)
- All nodes connected → 1 component
- n=1 → 1 component

**Complexity**
- Time: O(n + E × α(n)) ≈ O(n + E)
- Space: O(n)

**Follow-ups**
- "Add edges dynamically and query components after each?" → DSU handles online.
- "Largest component size?" → Track component sizes in a separate `size` array.

---

### Problem 2 — Redundant Connection (LeetCode #684)

**Clarifying Questions**
- Undirected graph that started as a tree + one extra edge? (Yes)
- Return the edge that creates the cycle? (Yes — the last edge in input that makes it cyclic)
- If multiple valid answers, return the one last in input? (Yes)

**Brute Force**

For each edge, check if removing it leaves the graph as a tree (connected + n-1 edges). O(E × (V+E)).

**Optimal**

Process edges one by one. The first edge where both endpoints are already connected (same DSU component) is the redundant connection.

```python
def find_redundant_connection(edges: list[list[int]]) -> list[int]:
    n = len(edges)
    parent = list(range(n + 1))   # 1-indexed nodes
    rank   = [0] * (n + 1)

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        rx, ry = find(x), find(y)
        if rx == ry:
            return False              # already connected → this edge is redundant
        if rank[rx] < rank[ry]: rx, ry = ry, rx
        parent[ry] = rx
        if rank[rx] == rank[ry]: rank[rx] += 1
        return True

    for u, v in edges:
        if not union(u, v):
            return [u, v]

    return []   # guaranteed to find one per problem
```

**Edge Cases**
- Self-loop `[1, 1]` → find(1) == find(1) immediately returns it
- Tree path: 1-2-3-4-5 with edge 5→1 → found at that edge

**Complexity**
- Time: O(E × α(V)) ≈ O(E)
- Space: O(V)

**Follow-ups**
- "Directed graph redundant connection?" → LeetCode #685; harder, requires DFS.
- "Find the cycle itself, not just the edge?" → Reconstruct the cycle from parent array.

---

### Problem 3 — Accounts Merge (LeetCode #721)

**Clarifying Questions**
- Accounts: first element is name, rest are emails? (Yes)
- Two accounts are same person if they share at least one email? (Yes)
- Return merged accounts, emails sorted? (Yes)
- Same name but different emails = different people unless linked? (Yes)

**Brute Force**

For each pair of accounts, check if they share any email — O(A² × E²) — too slow.

**Optimal**

Map each email to an index; union emails that appear in the same account; group by DSU root.

```python
from collections import defaultdict

def accounts_merge(accounts: list[list[str]]) -> list[list[str]]:
    parent = {}

    def find(x):
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]

    def union(x, y):
        parent[find(x)] = find(y)

    email_to_name = {}

    # Initialize DSU with all emails as their own roots
    for account in accounts:
        name = account[0]
        for email in account[1:]:
            if email not in parent:
                parent[email] = email
            email_to_name[email] = name
            # Union all emails in this account together
            union(account[1], email)    # first email as "canonical" for this account

    # Group emails by their root
    groups = defaultdict(list)
    for email in parent:
        groups[find(email)].append(email)

    return [
        [email_to_name[root]] + sorted(emails)
        for root, emails in groups.items()
    ]
```

**Edge Cases**
- Single-email account → forms its own component
- All accounts same person (all share one email) → one merged account
- Two accounts with same name but no shared email → separate

**Complexity**
- Time: O(N × E × α(N×E)) ≈ O(N×E × log(N×E)) where N=accounts, E=avg emails
- Space: O(N×E) for email map

**Follow-ups**
- "How many unique users?" → count distinct DSU roots
- "Add new account dynamically?" → DSU handles online unions

---

## Interview Q&A

**Q1: Why is DSU near-O(1) amortized? Explain path compression.**

A: Path compression makes every node on the find path point directly to the root. The first `find(x)` in a deep chain costs O(chain length), but all subsequent calls to any node on that path are O(1). Over n operations, the total work amortizes to near-O(1) per operation. Combined with union by rank (which keeps tree height at O(log n)), the amortized complexity is O(α(n)) — the inverse Ackermann function, which is ≤ 4 for any input size encountered in practice (including 10^80 nodes).

---

**Q2: What is union by rank and why does it matter?**

A: Without union by rank, always making one root the child of another could create chains of height O(n). Union by rank always attaches the shorter tree under the taller one, keeping tree height at O(log n) in the worst case (before path compression). The "rank" is an upper bound on height — it only increments when two trees of equal rank merge. With both path compression and union by rank together, operations achieve the near-O(1) amortized bound.

---

**Q3: When should you use DSU vs BFS/DFS for connected components?**

A:
```
Use DSU when:
  - Edges are added dynamically (online algorithm)
  - You need repeated "are x and y connected?" queries
  - Building MST with Kruskal's algorithm
  - Simple cycle detection in undirected graphs
  - Code clarity: DSU is often 15 lines vs 30 for BFS

Use BFS/DFS when:
  - Single-pass component detection (no dynamic updates)
  - Directed graph components
  - Need to find the actual path between nodes
  - Need all edges in a component

Both are O(V+E) for a static graph; DSU wins for dynamic graphs.
```

---

**Q4: Can DSU detect cycles? How?**

A: Yes, for undirected graphs. Before unioning an edge (u, v), call `find(u)` and `find(v)`. If they return the same root, u and v are already in the same component — adding edge (u, v) would create a cycle. This is the basis of LeetCode #684 (Redundant Connection) and the cycle-detection step in Kruskal's MST algorithm.

Note: DSU cannot detect cycles in directed graphs — it treats all edges as undirected.

---

**Q5: What is the inverse Ackermann function α(n)?**

A: α(n) is the functional inverse of the Ackermann function — an extremely fast-growing function. Since the Ackermann function grows faster than any primitive recursive function, its inverse α(n) grows extremely slowly: α(1) = 1, α(4) = 2, α(65536) = 3, α(2^65536) = 4. For all practical purposes, α(n) ≤ 4. So saying DSU is O(α(n)) is as close to O(1) as any non-constant function can be. In interviews, "amortized O(1)" or "near-O(1)" is fine.

---

**Q6: How does DSU enable Kruskal's MST algorithm?**

A:
```
Kruskal's algorithm:
1. Sort all edges by weight: O(E log E)
2. For each edge (u, v) in sorted order:
   - If find(u) != find(v): add edge to MST, union(u, v)
   - If find(u) == find(v): skip (would create cycle)
3. Stop when MST has V-1 edges

DSU role: O(α(V)) cycle check per edge
Total: O(E log E + E × α(V)) ≈ O(E log E)

Why not Prim's? Kruskal's is better for sparse graphs;
Prim's (with heap) is better for dense graphs O(E log V).
```

---

**Q7: What are the limitations of DSU?**

A:
```
1. Undirected only — doesn't respect edge direction
2. Union only — once merged, sets cannot split (no "undo")
   (Link-cut trees support splits in O(log n))
3. No path information — answers "connected?" but not "what path?"
4. No edge information — tracks nodes, not which edges connect them
5. Not thread-safe by default — concurrent union/find needs synchronization

For dynamic connectivity with both insertions AND deletions:
use offline algorithm (rollback DSU) or link-cut trees.
```

---

## Interview Tips

- **Know both path compression variants.** Recursive (`parent[x] = find(parent[x])`) is cleaner; iterative path halving (`parent[x] = parent[parent[x]]`) avoids stack overflow. Both work in interviews.
- **The 15-line template.** Memorize the compact DSU template: `parent = list(range(n))`, `rank = [0]*n`, `find` with halving, `union` with rank. You can write it in under 2 minutes.
- **Cycle detection = union returns False.** The moment `find(u) == find(v)` before you union, you have a cycle. This is the core insight for redundant connection problems.
- **Component count shortcut.** Start with `components = n`, decrement by 1 on each successful union. At the end, `components` is the answer.
- **String keys work too.** DSU works with any hashable keys (strings, tuples), not just integers. For Accounts Merge, email strings are the keys directly.
- **Mention α(n) but explain it.** Say "DSU with path compression and union by rank runs in O(α(n)) per operation — effectively O(1) for all practical purposes since α(n) ≤ 4 for any realistic input size."
