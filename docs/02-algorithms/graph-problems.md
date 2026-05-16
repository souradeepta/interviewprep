# Graph Problems

## DFS/BFS Traversal
**When to use:** Connected components, reachability, all-paths enumeration

**Best DS:** Adjacency list, Adjacency matrix, Stack/Queue

**Key Algorithms:** DFS (recurse to unvisited neighbors), BFS (queue-based level exploration)

**Example Problems:**
1. "Number of islands" → DFS/BFS to mark all land cells of one island. Your repo: `python/advanced/graph.py`. Time: O(m × n)
2. "Clone graph" → BFS or DFS with node mapping. Time: O(V + E)

---

## Shortest Path (Unweighted)
**When to use:** Fewest hops, level-based distance, BFS applications

**Best DS:** Queue, Adjacency list

**Key Algorithms:** Standard BFS (distance = level), distance array tracking

**Example Problems:**
1. "Shortest path in grid" → BFS from start, distance = number of steps. Your repo: `python/advanced/graph.py`. Time: O(m × n)

---

## Shortest Path (Weighted)
**When to use:** Weighted edges, optimal cost path, network routing

**Best DS:** Priority Queue, Distance array

**Key Algorithms:** Dijkstra's algorithm (non-negative weights), Bellman-Ford (negative weights)

**Example Problems:**
1. "Network delay time (Dijkstra)" → Dijkstra from node, return max distance. Your repo: `python/advanced/graph.py`. Time: O((V + E) log V)

---

## Minimum Spanning Tree (MST)
**When to use:** Connect all nodes with minimum cost, infrastructure planning

**Best DS:** Union-Find, Priority Queue

**Key Algorithms:** Kruskal (sort edges, use Union-Find), Prim (start from node, add cheapest outgoing)

**Example Problems:**
1. "Min cost to connect cities (Kruskal)" → Sort edges by weight, use Union-Find to avoid cycles. Your repo: `python/advanced/union_find.py`. Time: O(E log E)

---

## Topological Sort
**When to use:** Dependency resolution, task scheduling, DAG processing

**Best DS:** Adjacency list, Queue

**Key Algorithms:** Kahn's algorithm (BFS-based, in-degree tracking), DFS-based

**Example Problems:**
1. "Course schedule (cycle detection)" → Kahn's algorithm; if all courses processed, no cycle. Your repo: `python/advanced/graph.py`. Time: O(V + E)

---

## Union-Find / Disjoint Set Union
**When to use:** Connected components, cycle detection, dynamic connectivity

**Best DS:** Union-Find with path compression and union by rank

**Key Algorithms:** Path compression, union by rank

**Example Problems:**
1. "Connected components count" → Union-Find; number of components = count of roots. Your repo: `python/advanced/union_find.py`. Time: O(n α(n))
2. "Detect cycle in undirected graph" → If edge connects two nodes already in same component, cycle. Time: O(E α(E))

---

See [Master Index](problem-to-pattern-matcher.md) for all 50+ patterns.
