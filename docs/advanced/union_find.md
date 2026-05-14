# Union-Find / Disjoint Set Union (DSU)

## Overview

**Union-Find** (also called Disjoint Set Union or DSU) is a data structure that tracks a collection of elements partitioned into disjoint (non-overlapping) sets. It supports two primary operations: **union** (merge two sets) and **find** (determine which set an element belongs to). With path compression and union by rank/size, both operations run in nearly O(1) amortized time.

**When to use:**
- Detect cycles in undirected graphs
- Connected components (dynamic connectivity)
- Kruskal's Minimum Spanning Tree algorithm
- Network connectivity: "Are A and B in the same network?"
- Percolation problems
- Image processing (labeling connected regions)

---

## Visualization

### Initial State (6 elements, each in its own set)

```
Elements: {0, 1, 2, 3, 4, 5}

parent: [0, 1, 2, 3, 4, 5]
rank:   [0, 0, 0, 0, 0, 0]

Each element is its own root (parent[i] = i):
  ○  ○  ○  ○  ○  ○
  0  1  2  3  4  5
```

### After union(0,1), union(2,3), union(4,5)

```
parent: [0, 0, 2, 2, 4, 4]
rank:   [1, 0, 1, 0, 1, 0]

   0    2    4
  / \  / \  / \
 (0) 1 (2) 3 (4) 5

Sets:  {0,1}   {2,3}   {4,5}
Roots:   0        2       4
```

### After union(0,2) — merge sets {0,1} and {2,3}

```
Union by rank: rank[0] = 1, rank[2] = 1 → equal ranks
  → attach 2 under 0, increment rank[0]

parent: [0, 0, 0, 2, 4, 4]
rank:   [2, 0, 1, 0, 1, 0]

       0
     / | \
   (0) 1   2
          / \
        (2)  3

Sets: {0,1,2,3}   {4,5}
Root:     0          4
```

### Path Compression: find(3) before and after

```
Before compression:          After find(3) with path compression:
       0                              0
     / | \                          / | \  \
   (0) 1   2           →         (0) 1  2   3
          / \                           |
        (2)  3                         (2)

find(3):
  3 → parent[3]=2 → parent[2]=0 → root!
  Path compression: set parent[3] = 0 directly
  Now: parent = [0, 0, 0, 0, 4, 4]

Every node on the find path points directly to root after compression.
Next find(3): 3 → 0 in ONE step. ✓
```

### Union by Size (alternative to rank)

```
size[i] = number of elements in the set rooted at i

union(A, B):
  rootA = find(A), rootB = find(B)
  if rootA == rootB: return  (already same set)
  if size[rootA] < size[rootB]:
      parent[rootA] = rootB
      size[rootB] += size[rootA]
  else:
      parent[rootB] = rootA
      size[rootA] += size[rootB]

Ensures smaller tree attaches to larger → keeps height O(log n)
```

---

## Operations & Complexity

| Operation       | Time (naive)     | Time (with path compression + union by rank) | Space  |
|-----------------|:----------------:|:--------------------------------------------:|:------:|
| Make Set (init) | O(1)             | O(1)                                         | O(n)   |
| Find            | O(n) worst       | O(α(n)) amortized ≈ O(1)                     | O(1)   |
| Union           | O(n) worst       | O(α(n)) amortized ≈ O(1)                     | O(1)   |
| Connected?      | O(n) worst       | O(α(n)) amortized ≈ O(1)                     | O(1)   |
| Space           | —                | —                                             | O(n)   |

> α(n) is the inverse Ackermann function — grows so slowly it's effectively constant (≤ 4 for any practical n).

---

## Key Properties / Invariants

1. **Disjoint sets**: Every element belongs to exactly one set.
2. **Representative (root)**: Each set has a unique representative — the root of its tree.
3. **find(x) == find(y) ↔ same set**: The canonical way to check membership.
4. **Path compression**: After find(x), every node on the path to root points directly to root.
5. **Union by rank/size**: Always attach the smaller/shorter tree under the taller/larger one.
6. **Both optimizations together** give the nearly-O(1) amortized guarantee.

---

## Common Interview Patterns

### Pattern 1: Detect Cycle in Undirected Graph

```
For each edge (u, v):
  if find(u) == find(v): CYCLE DETECTED (u and v already connected)
  else: union(u, v)
```

### Pattern 2: Number of Connected Components

```
Initialize DSU for all n nodes.
For each edge: union(u, v)
Count distinct roots: len({find(i) for i in range(n)})
```

### Pattern 3: Kruskal's Minimum Spanning Tree

```
Sort edges by weight (ascending).
For each edge (u, v, w):
  if find(u) != find(v):
      union(u, v)
      mst_cost += w
      mst_edges.append((u, v, w))
  Stop when MST has n-1 edges.
```

### Pattern 4: Dynamic Connectivity / Online Queries

```
"Are cities A and B connected at query time t?"
Process union operations (add roads) and find queries (connectivity checks) online.
Union-Find handles both in O(α(n)) per operation.
```

### Pattern 5: Accounts Merge / Group Similar Elements

```
Assign each element an initial DSU ID.
For each group: union all elements with the first element.
After processing all groups, elements with the same root belong to the same merged group.
```

---

## Interview Tips

- **Always implement both optimizations**: Path compression + union by rank/size. Alone, each only gives O(log n); together they give O(α(n)).
- **find() is recursive OR iterative**: Recursive is cleaner but may stack overflow on very deep trees (before compression). Iterative find with path compression is safer.
- **Union by rank vs size**: Both are correct. Union by size is slightly easier to reason about.
- **Weighted Union-Find**: Can store edge weights or other information on the path (e.g., for parity/distance problems).
- **Connected components count**: Maintain a `count` variable, decrement on each successful union.
- **Off-by-one with 1-indexed graphs**: If nodes are labeled 1..n, initialize DSU of size n+1.

---

## Example Problems

| Problem                                       | Pattern                             |
|-----------------------------------------------|-------------------------------------|
| Number of Connected Components (LC 323)       | Count distinct roots after unions   |
| Graph Valid Tree (LC 261)                     | Cycle detection + connectivity      |
| Redundant Connection (LC 684)                 | Find edge that creates cycle        |
| Accounts Merge (LC 721)                       | Group similar elements              |
| Number of Operations to Make Network Connected (LC 1319) | Count cables needed      |

---

## Python Quick Reference

```python
# ── Union-Find with Path Compression + Union by Size ──────────────────────────
class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))  # parent[i] = i (each is its own root)
        self.size   = [1] * n         # size of each component
        self.count  = n               # number of distinct components

    # ── Find with path compression (iterative) ────────────────────────────────
    def find(self, x):
        root = x
        while self.parent[root] != root:
            root = self.parent[root]
        # Path compression: make all nodes point directly to root
        while self.parent[x] != root:
            self.parent[x], x = root, self.parent[x]
        return root

    # ── Union by size ─────────────────────────────────────────────────────────
    def union(self, x, y):
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False  # already in same set
        # Attach smaller to larger
        if self.size[rx] < self.size[ry]:
            rx, ry = ry, rx
        self.parent[ry] = rx
        self.size[rx] += self.size[ry]
        self.count -= 1
        return True

    # ── Connected check ───────────────────────────────────────────────────────
    def connected(self, x, y):
        return self.find(x) == self.find(y)

    # ── Get number of components ──────────────────────────────────────────────
    def num_components(self):
        return self.count

# ── Usage ─────────────────────────────────────────────────────────────────────
uf = UnionFind(6)
uf.union(0, 1)
uf.union(2, 3)
uf.union(4, 5)
print(uf.num_components())   # 3
uf.union(0, 2)
print(uf.num_components())   # 2
print(uf.connected(1, 3))    # True  (1→0→root, 3→2→0→root)
print(uf.connected(1, 4))    # False

# ── Cycle Detection ───────────────────────────────────────────────────────────
def has_cycle(n, edges):
    uf = UnionFind(n)
    for u, v in edges:
        if not uf.union(u, v):  # u and v already connected → cycle
            return True
    return False

# ── Kruskal's MST ──────────────────────────────────────────────────────────────
def kruskal(n, edges):
    edges.sort(key=lambda e: e[2])  # sort by weight
    uf = UnionFind(n)
    mst_cost, mst_edges = 0, []
    for u, v, w in edges:
        if uf.union(u, v):
            mst_cost += w
            mst_edges.append((u, v, w))
            if len(mst_edges) == n - 1:
                break
    return mst_cost, mst_edges

# ── Accounts Merge (LC 721 style) ─────────────────────────────────────────────
def accounts_merge(accounts):
    email_to_id = {}
    uf = UnionFind(len(accounts) * 10)  # rough upper bound

    for i, account in enumerate(accounts):
        for email in account[1:]:
            if email not in email_to_id:
                email_to_id[email] = len(email_to_id)
            uf.union(email_to_id[account[1]], email_to_id[email])

    # Group emails by root
    from collections import defaultdict
    groups = defaultdict(set)
    for email, eid in email_to_id.items():
        groups[uf.find(eid)].add(email)

    # Map back to account names
    id_to_name = {}
    for i, account in enumerate(accounts):
        for email in account[1:]:
            id_to_name[uf.find(email_to_id[email])] = account[0]

    return [[id_to_name[root]] + sorted(emails)
            for root, emails in groups.items()]

# ── Union-Find with rank (alternative to size) ────────────────────────────────
class UnionFindRank:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank   = [0] * n

    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])  # recursive + compression
        return self.parent[x]

    def union(self, x, y):
        rx, ry = self.find(x), self.find(y)
        if rx == ry: return False
        if self.rank[rx] < self.rank[ry]:
            rx, ry = ry, rx
        self.parent[ry] = rx
        if self.rank[rx] == self.rank[ry]:
            self.rank[rx] += 1
        return True
```

---

## Java Quick Reference

```java
class UnionFind {
    private int[] parent, size;
    private int count;

    UnionFind(int n) {
        parent = new int[n];
        size   = new int[n];
        count  = n;
        for (int i = 0; i < n; i++) {
            parent[i] = i;
            size[i]   = 1;
        }
    }

    // Find with path compression (iterative)
    public int find(int x) {
        int root = x;
        while (parent[root] != root) root = parent[root];
        // Path compression
        while (parent[x] != root) {
            int next = parent[x];
            parent[x] = root;
            x = next;
        }
        return root;
    }

    // Union by size
    public boolean union(int x, int y) {
        int rx = find(x), ry = find(y);
        if (rx == ry) return false;
        if (size[rx] < size[ry]) { int tmp = rx; rx = ry; ry = tmp; }
        parent[ry] = rx;
        size[rx] += size[ry];
        count--;
        return true;
    }

    public boolean connected(int x, int y) { return find(x) == find(y); }
    public int numComponents()             { return count; }
}

// Kruskal's MST
int kruskal(int n, int[][] edges) {
    // edges: [u, v, weight]
    Arrays.sort(edges, (a, b) -> a[2] - b[2]);
    UnionFind uf = new UnionFind(n);
    int cost = 0, edgesUsed = 0;
    for (int[] e : edges) {
        if (uf.union(e[0], e[1])) {
            cost += e[2];
            if (++edgesUsed == n - 1) break;
        }
    }
    return edgesUsed == n - 1 ? cost : -1;  // -1 if no MST (disconnected)
}
```
