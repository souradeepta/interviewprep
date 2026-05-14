# Data Structures — SDE Interview Prep

A comprehensive reference and practice repository covering all essential data structures for software engineering technical interviews. Every structure includes Python and Java implementations, ASCII-art documentation, and complexity tables.

## Repository Structure

```
datastructures/
├── docs/
│   ├── basic/          # Array, LinkedList, Stack, Queue, Deque, HashMap
│   ├── advanced/       # BST, AVL, Heap, Trie, Graph, B-Tree, Seg Tree, Fenwick, DSU, LRU
│   ├── new_ds/         # Red-Black Tree, Skip List, Bloom Filter, LFU Cache, Sparse Table, Treap
│   └── algorithms/     # Sorting, Searching, DP, Graph Algorithms, String, Math
├── python/
│   ├── basic/          # Python implementations — basic DS
│   ├── advanced/       # Python implementations — advanced DS
│   ├── new_ds/         # Python implementations — new/specialized DS
│   └── algorithms/     # Python implementations — algorithms
├── java/
│   ├── basic/          # Java implementations — basic DS
│   ├── advanced/       # Java implementations — advanced DS
│   ├── new_ds/         # Java implementations — new/specialized DS
│   └── algorithms/     # Java implementations — algorithms
├── .claude/
│   └── agents/
│       ├── sde2-interviewer.md   # Mock interviewer agent
│       └── sde-candidate.md     # Mock candidate agent
├── AGENTS.md           # How to use the interview agents
└── README.md
```

## Data Structures Covered

### Basic

| Data Structure | Python | Java | Docs |
|---|---|---|---|
| Dynamic Array | `python/basic/array.py` | `java/basic/DynamicArray.java` | `docs/basic/array.md` |
| Singly Linked List | `python/basic/linked_list.py` | `java/basic/SinglyLinkedList.java` | `docs/basic/linked_list.md` |
| Doubly Linked List | `python/basic/linked_list.py` | `java/basic/DoublyLinkedList.java` | `docs/basic/linked_list.md` |
| Stack | `python/basic/stack.py` | `java/basic/Stack.java` | `docs/basic/stack.md` |
| Queue | `python/basic/queue_ds.py` | `java/basic/Queue.java` | `docs/basic/queue.md` |
| Deque | `python/basic/deque_ds.py` | `java/basic/Deque.java` | `docs/basic/deque.md` |
| HashMap | `python/basic/hashmap.py` | `java/basic/HashMap.java` | `docs/basic/hashmap.md` |

### Advanced

| Data Structure | Python | Java | Docs |
|---|---|---|---|
| Binary Search Tree | `python/advanced/bst.py` | `java/advanced/BST.java` | `docs/advanced/bst.md` |
| AVL Tree | `python/advanced/avl_tree.py` | `java/advanced/AVLTree.java` | `docs/advanced/avl_tree.md` |
| Min/Max Heap | `python/advanced/heap.py` | `java/advanced/MinHeap.java` | `docs/advanced/heap.md` |
| Trie | `python/advanced/trie.py` | `java/advanced/Trie.java` | `docs/advanced/trie.md` |
| Graph | `python/advanced/graph.py` | `java/advanced/Graph.java` | `docs/advanced/graph.md` |
| B-Tree | `python/advanced/btree.py` | `java/advanced/BTree.java` | `docs/advanced/btree.md` |
| Segment Tree | `python/advanced/segment_tree.py` | `java/advanced/SegmentTree.java` | `docs/advanced/segment_tree.md` |
| Fenwick Tree | `python/advanced/fenwick_tree.py` | `java/advanced/FenwickTree.java` | `docs/advanced/fenwick_tree.md` |
| Union Find | `python/advanced/union_find.py` | `java/advanced/UnionFind.java` | `docs/advanced/union_find.md` |
| LRU Cache | `python/advanced/lru_cache.py` | `java/advanced/LRUCache.java` | `docs/advanced/lru_cache.md` |

### New / Specialized

| Data Structure | Python | Java | Docs |
|---|---|---|---|
| Red-Black Tree | `python/new_ds/red_black_tree.py` | `java/new_ds/RedBlackTree.java` | `docs/new_ds/red_black_tree.md` |
| Skip List | `python/new_ds/skip_list.py` | `java/new_ds/SkipList.java` | `docs/new_ds/skip_list.md` |
| Bloom Filter | `python/new_ds/bloom_filter.py` | `java/new_ds/BloomFilter.java` | `docs/new_ds/bloom_filter.md` |
| LFU Cache | `python/new_ds/lfu_cache.py` | `java/new_ds/LFUCache.java` | `docs/new_ds/lfu_cache.md` |
| Sparse Table | `python/new_ds/sparse_table.py` | `java/new_ds/SparseTable.java` | `docs/new_ds/sparse_table.md` |
| Treap | `python/new_ds/treap.py` | `java/new_ds/Treap.java` | `docs/new_ds/treap.md` |

## Advanced / Specialized Data Structures

| Data Structure | Python | Java | Docs | Use Cases |
|---|---|---|---|---|
| Suffix Tree | `python/new_ds/suffix_tree.py` | `java/new_ds/SuffixTree.java` | `docs/new_ds/suffix_tree.md` | Pattern matching, string compression, DNA sequencing |
| Suffix Array | `python/new_ds/suffix_array.py` | `java/new_ds/SuffixArray.java` | `docs/new_ds/suffix_array.md` | Pattern matching, substring search, longest repeated substring |
| Heavy-Light Decomposition | `python/new_ds/heavy_light_decomposition.py` | `java/new_ds/HeavyLightDecomposition.java` | `docs/new_ds/heavy_light_decomposition.md` | Tree path queries, tree updates, competitive programming |
| Link-Cut Tree | `python/new_ds/link_cut_tree.py` | `java/new_ds/LinkCutTree.java` | `docs/new_ds/link_cut_tree.md` | Dynamic tree queries, connectivity, dynamic MST |
| Persistent Segment Tree | `python/new_ds/persistent_segment_tree.py` | `java/new_ds/PersistentSegmentTree.java` | `docs/new_ds/persistent_segment_tree.md` | Historical queries, version control, path queries |
| Cartesian Tree | `python/new_ds/cartesian_tree.py` | `java/new_ds/CartesianTree.java` | `docs/new_ds/cartesian_tree.md` | Range minimum queries, stack simulation, offline queries |
| Splay Tree | `python/new_ds/splay_tree.py` | `java/new_ds/SplayTree.java` | `docs/new_ds/splay_tree.md` | Amortized O(log n) operations, cache-oblivious |
| AC Automaton | `python/new_ds/ac_automaton.py` | `java/new_ds/ACAutomaton.java` | `docs/new_ds/ac_automaton.md` | Multiple pattern matching, dictionary search |
| KD-Tree | `python/new_ds/kd_tree.py` | `java/new_ds/KDTree.java` | `docs/new_ds/kd_tree.md` | Nearest neighbor search, range queries, spatial data |
| Dancing Links | `python/new_ds/dancing_links.py` | `java/new_ds/DancingLinks.java` | `docs/new_ds/dancing_links.md` | Exact cover problem, Sudoku solving, constraint satisfaction |
| Van Emde Boas Tree | `python/new_ds/van_emde_boas.py` | `java/new_ds/VanEmdeBoas.java` | `docs/new_ds/van_emde_boas.md` | Integer range operations, O(log log U) operations |
| Leftist Heap | `python/new_ds/leftist_heap.py` | `java/new_ds/LeftistHeap.java` | `docs/new_ds/leftist_heap.md` | Efficient merge, priority queue merging |
| Fibonacci Heap | `python/new_ds/fibonacci_heap.py` | `java/new_ds/FibonacciHeap.java` | `docs/new_ds/fibonacci_heap.md` | Amortized optimal decreaseKey, Dijkstra optimization |
| B+ Tree | `python/new_ds/bplus_tree.py` | `java/new_ds/BPlusTree.java` | `docs/new_ds/bplus_tree.md` | Database indices, range queries, sorted access |
| Segment Tree Lazy Propagation | `python/new_ds/segment_tree_lazy.py` | `java/new_ds/SegmentTreeLazy.java` | `docs/new_ds/segment_tree_lazy.md` | Range updates, range queries, lazy evaluation |

## Advanced Algorithms

### Dynamic Programming Advanced

| Algorithm | Python | Java | Docs | Time Complexity |
|---|---|---|---|---|
| Convex Hull Trick (CHT) | `python/algorithms/dp_advanced/dp_advanced.py` | `java/algorithms/dp_advanced/DPAdvanced.java` | `docs/algorithms/dp_advanced/dp_advanced.md` | O(n log n) |
| Digit Dynamic Programming | `python/algorithms/dp_advanced/dp_advanced.py` | `java/algorithms/dp_advanced/DPAdvanced.java` | `docs/algorithms/dp_advanced/dp_advanced.md` | O(d² · 10^d) |
| Tree Dynamic Programming | `python/algorithms/dp_advanced/dp_advanced.py` | `java/algorithms/dp_advanced/DPAdvanced.java` | `docs/algorithms/dp_advanced/dp_advanced.md` | O(n²) |
| Sum Over Subsets (SOS DP) | `python/algorithms/dp_advanced/dp_advanced.py` | `java/algorithms/dp_advanced/DPAdvanced.java` | `docs/algorithms/dp_advanced/dp_advanced.md` | O(n · 2^n) |
| Knuth-Yao Speedup | `python/algorithms/dp_advanced/dp_advanced.py` | `java/algorithms/dp_advanced/DPAdvanced.java` | `docs/algorithms/dp_advanced/dp_advanced.md` | O(n²) |

### Graph Algorithms Advanced

| Algorithm | Python | Java | Docs | Time Complexity |
|---|---|---|---|---|
| Max Flow (Ford-Fulkerson) | `python/algorithms/graph_advanced/graph_advanced.py` | `java/algorithms/graph_advanced/GraphAdvanced.java` | `docs/algorithms/graph_advanced/graph_advanced.md` | O(E · max_flow) |
| Max Flow (Edmonds-Karp) | `python/algorithms/graph_advanced/graph_advanced.py` | `java/algorithms/graph_advanced/GraphAdvanced.java` | `docs/algorithms/graph_advanced/graph_advanced.md` | O(V · E²) |
| Min Cost Max Flow | `python/algorithms/graph_advanced/graph_advanced.py` | `java/algorithms/graph_advanced/GraphAdvanced.java` | `docs/algorithms/graph_advanced/graph_advanced.md` | O(V² · E · log V) |
| Bipartite Matching (Hungarian) | `python/algorithms/graph_advanced/graph_advanced.py` | `java/algorithms/graph_advanced/GraphAdvanced.java` | `docs/algorithms/graph_advanced/graph_advanced.md` | O(V³) |
| 2-SAT Solver | `python/algorithms/graph_advanced/graph_advanced.py` | `java/algorithms/graph_advanced/GraphAdvanced.java` | `docs/algorithms/graph_advanced/graph_advanced.md` | O(V + E) |
| Minimum Vertex Cover | `python/algorithms/graph_advanced/graph_advanced.py` | `java/algorithms/graph_advanced/GraphAdvanced.java` | `docs/algorithms/graph_advanced/graph_advanced.md` | O(2^n) |

### String Algorithms Advanced

| Algorithm | Python | Java | Docs | Time Complexity |
|---|---|---|---|---|
| Boyer-Moore | `python/algorithms/string_advanced/string_advanced.py` | `java/algorithms/string_advanced/StringAdvanced.java` | `docs/algorithms/string_advanced/string_advanced.md` | O(n/m) best |
| Aho-Corasick Automaton | `python/algorithms/string_advanced/string_advanced.py` | `java/algorithms/string_advanced/StringAdvanced.java` | `docs/algorithms/string_advanced/string_advanced.md` | O((n+m) log Σ) |
| Suffix Array Construction | `python/algorithms/string_advanced/string_advanced.py` | `java/algorithms/string_advanced/StringAdvanced.java` | `docs/algorithms/string_advanced/string_advanced.md` | O(n log n) |
| Suffix Tree Construction (Ukkonen) | `python/algorithms/string_advanced/string_advanced.py` | `java/algorithms/string_advanced/StringAdvanced.java` | `docs/algorithms/string_advanced/string_advanced.md` | O(n) |
| Lyndon Factorization | `python/algorithms/string_advanced/string_advanced.py` | `java/algorithms/string_advanced/StringAdvanced.java` | `docs/algorithms/string_advanced/string_advanced.md` | O(n) |

### Geometry Algorithms

| Algorithm | Python | Java | Docs | Time Complexity |
|---|---|---|---|---|
| Convex Hull (Graham Scan) | `python/algorithms/geometry/geometry.py` | `java/algorithms/geometry/Geometry.java` | `docs/algorithms/geometry/geometry.md` | O(n log n) |
| Convex Hull (Andrew's Monotone Chain) | `python/algorithms/geometry/geometry.py` | `java/algorithms/geometry/Geometry.java` | `docs/algorithms/geometry/geometry.md` | O(n log n) |
| Closest Pair of Points | `python/algorithms/geometry/geometry.py` | `java/algorithms/geometry/Geometry.java` | `docs/algorithms/geometry/geometry.md` | O(n log n) |
| Line Intersection | `python/algorithms/geometry/geometry.py` | `java/algorithms/geometry/Geometry.java` | `docs/algorithms/geometry/geometry.md` | O(1) |
| Point in Polygon | `python/algorithms/geometry/geometry.py` | `java/algorithms/geometry/Geometry.java` | `docs/algorithms/geometry/geometry.md` | O(n) |

### Tree Algorithms Advanced

| Algorithm | Python | Java | Docs | Time Complexity |
|---|---|---|---|---|
| Heavy-Light Decomposition | `python/algorithms/tree_advanced/tree_advanced.py` | `java/algorithms/tree_advanced/TreeAdvanced.java` | `docs/algorithms/tree_advanced/tree_advanced.md` | O(log² n) per query |
| Link-Cut Tree Operations | `python/algorithms/tree_advanced/tree_advanced.py` | `java/algorithms/tree_advanced/TreeAdvanced.java` | `docs/algorithms/tree_advanced/tree_advanced.md` | O(log n) amortized |
| Centroid Decomposition | `python/algorithms/tree_advanced/tree_advanced.py` | `java/algorithms/tree_advanced/TreeAdvanced.java` | `docs/algorithms/tree_advanced/tree_advanced.md` | O(n log n) |
| Square Root Decomposition | `python/algorithms/tree_advanced/tree_advanced.py` | `java/algorithms/tree_advanced/TreeAdvanced.java` | `docs/algorithms/tree_advanced/tree_advanced.md` | O(√n) per query |
| Mo's Algorithm | `python/algorithms/tree_advanced/tree_advanced.py` | `java/algorithms/tree_advanced/TreeAdvanced.java` | `docs/algorithms/tree_advanced/tree_advanced.md` | O((n+q)√n) |

## Interview Algorithms (30 New Algorithms)

Added comprehensive interview-focused algorithms with detailed documentation, decision flowcharts, and step-by-step examples.

### Backtracking Algorithms (8)

| Algorithm | Python | Docs | Use Case | Frequency |
|-----------|--------|------|----------|-----------|
| N-Queens | `python/algorithms/dp/dp.py` | `docs/algorithms/dp/backtracking_patterns.md` | Constraint satisfaction | ★★★★★ |
| Sudoku Solver | `python/algorithms/dp/dp.py` | `docs/algorithms/dp/backtracking_patterns.md` | Constraint satisfaction | ★★★★★ |
| Word Search | `python/algorithms/dp/dp.py` | `docs/algorithms/dp/backtracking_patterns.md` | Grid path finding | ★★★★★ |
| Permutations | `python/algorithms/dp/dp.py` | `docs/algorithms/dp/backtracking_patterns.md` | All arrangements | ★★★★★ |
| Combinations | `python/algorithms/dp/dp.py` | `docs/algorithms/dp/backtracking_patterns.md` | All selections | ★★★★★ |
| Letter Combinations | `python/algorithms/dp/dp.py` | `docs/algorithms/dp/backtracking_patterns.md` | Mapping generation | ★★★★☆ |
| Subsets | `python/algorithms/dp/dp.py` | `docs/algorithms/dp/backtracking_patterns.md` | Power set | ★★★★★ |
| Generate Parentheses | `python/algorithms/dp/dp.py` | `docs/algorithms/dp/backtracking_patterns.md` | Balanced strings | ★★★★☆ |

### Grid & 2D DP (7)

| Algorithm | Python | Docs | Use Case | Frequency |
|-----------|--------|------|----------|-----------|
| Unique Paths | `python/algorithms/dp/dp.py` | `docs/algorithms/dp/grid_dp_patterns.md` | Path counting | ★★★★★ |
| Bomb Enemy | `python/algorithms/dp/dp.py` | `docs/algorithms/dp/grid_dp_patterns.md` | Range queries | ★★★☆☆ |
| Max Island Area | `python/algorithms/dp/dp.py` | `docs/algorithms/dp/grid_dp_patterns.md` | Connected components | ★★★★★ |
| Dungeon Game | `python/algorithms/dp/dp.py` | `docs/algorithms/dp/grid_dp_patterns.md` | Reverse DP | ★★★★☆ |
| Trapping Rain Water 2D | `python/algorithms/dp/dp.py` | `docs/algorithms/dp/grid_dp_patterns.md` | Elevation handling | ★★★☆☆ |
| Word Ladder | `python/algorithms/dp/dp.py` | `docs/algorithms/dp/grid_dp_patterns.md` | Graph BFS | ★★★★☆ |
| Word Pattern Matching | `python/algorithms/dp/dp.py` | `docs/algorithms/dp/grid_dp_patterns.md` | Bijective matching | ★★★☆☆ |

### Tree DP & Traversals (14)

| Algorithm | Python | Docs | Use Case | Frequency |
|-----------|--------|------|----------|-----------|
| Lowest Common Ancestor | `python/algorithms/graph/graph_algorithms.py` | `docs/algorithms/graph/tree_dp_guide.md` | Path queries | ★★★★★ |
| Path Sum | `python/algorithms/graph/graph_algorithms.py` | `docs/algorithms/graph/tree_dp_guide.md` | Path validation | ★★★★★ |
| All Root-to-Leaf Paths | `python/algorithms/graph/graph_algorithms.py` | `docs/algorithms/graph/tree_dp_guide.md` | Path collection | ★★★★☆ |
| Tree Diameter | `python/algorithms/graph/graph_algorithms.py` | `docs/algorithms/graph/tree_dp_guide.md` | Longest path | ★★★★☆ |
| House Robber III | `python/algorithms/graph/graph_algorithms.py` | `docs/algorithms/graph/tree_dp_guide.md` | Tree DP state | ★★★★☆ |
| Build Tree (Pre/Inorder) | `python/algorithms/graph/graph_algorithms.py` | `docs/algorithms/graph/tree_dp_guide.md` | Tree reconstruction | ★★★★☆ |
| Serialize/Deserialize Tree | `python/algorithms/graph/graph_algorithms.py` | `docs/algorithms/graph/tree_dp_guide.md` | Tree encoding | ★★★★☆ |
| Count Islands | `python/algorithms/graph/graph_algorithms.py` | `docs/algorithms/graph/traversal_patterns.md` | Connected components | ★★★★★ |
| Bipartite Check | `python/algorithms/graph/graph_algorithms.py` | `docs/algorithms/graph/traversal_patterns.md` | 2-coloring | ★★★★☆ |
| Cycle Detection (Directed) | `python/algorithms/graph/graph_algorithms.py` | `docs/algorithms/graph/traversal_patterns.md` | Dependency cycles | ★★★★★ |
| Cycle Detection (Undirected) | `python/algorithms/graph/graph_algorithms.py` | `docs/algorithms/graph/traversal_patterns.md` | Tree verification | ★★★★☆ |

**Key Resources:**
- **Pattern Guides**: See [`backtracking_patterns.md`](docs/algorithms/dp/backtracking_patterns.md), [`grid_dp_patterns.md`](docs/algorithms/dp/grid_dp_patterns.md), [`tree_dp_guide.md`](docs/algorithms/graph/tree_dp_guide.md), [`traversal_patterns.md`](docs/algorithms/graph/traversal_patterns.md)
- **Test Coverage**: 29 unit tests covering all algorithms
- **Interview Frequency**: Rated ★★★★★ (very common) to ★★☆☆☆ (less common) in technical interviews

## Problem-Solving Guides

This repository includes structured decision guides to help you select the right data structure or algorithm for any problem.

| Guide | Location | Purpose | How to Use |
|---|---|---|---|
| **Data Structure Selection Guide** | `docs/guides/data_structure_selection.md` | Flowchart for choosing the optimal DS based on operation needs | Start here when you need to pick a DS — answer questions about required operations |
| **Algorithm Selection Guide** | `docs/guides/algorithm_selection.md` | Decision tree for algorithm selection across problem categories | Use when you recognize a problem type but aren't sure which algorithm applies |
| **Problem-Solving Flowchart** | `docs/guides/problem_solving_flowchart.md` | Step-by-step approach for analyzing interview problems | Follow when you encounter a new problem in an interview |

## Algorithms Covered

### Sorting

| Algorithm | Python | Java | Docs | Time Complexity |
|---|---|---|---|---|
| Bubble Sort | `python/algorithms/sorting/sorting.py` | `java/algorithms/sorting/Sorting.java` | `docs/algorithms/sorting/sorting.md` | O(n²) |
| Selection Sort | `python/algorithms/sorting/sorting.py` | `java/algorithms/sorting/Sorting.java` | `docs/algorithms/sorting/sorting.md` | O(n²) |
| Insertion Sort | `python/algorithms/sorting/sorting.py` | `java/algorithms/sorting/Sorting.java` | `docs/algorithms/sorting/sorting.md` | O(n²) |
| Merge Sort | `python/algorithms/sorting/sorting.py` | `java/algorithms/sorting/Sorting.java` | `docs/algorithms/sorting/sorting.md` | O(n log n) |
| Quick Sort (3-way) | `python/algorithms/sorting/sorting.py` | `java/algorithms/sorting/Sorting.java` | `docs/algorithms/sorting/sorting.md` | O(n log n) avg |
| Heap Sort | `python/algorithms/sorting/sorting.py` | `java/algorithms/sorting/Sorting.java` | `docs/algorithms/sorting/sorting.md` | O(n log n) |
| Counting Sort | `python/algorithms/sorting/sorting.py` | `java/algorithms/sorting/Sorting.java` | `docs/algorithms/sorting/sorting.md` | O(n + k) |
| Radix Sort | `python/algorithms/sorting/sorting.py` | `java/algorithms/sorting/Sorting.java` | `docs/algorithms/sorting/sorting.md` | O(n·k) |
| Bucket Sort | `python/algorithms/sorting/sorting.py` | `java/algorithms/sorting/Sorting.java` | `docs/algorithms/sorting/sorting.md` | O(n + k) avg |
| Tim Sort | `python/algorithms/sorting/sorting.py` | `java/algorithms/sorting/Sorting.java` | `docs/algorithms/sorting/sorting.md` | O(n log n) |

### Searching

| Algorithm | Python | Java | Docs | Time Complexity |
|---|---|---|---|---|
| Binary Search (iterative) | `python/algorithms/searching/searching.py` | `java/algorithms/searching/Searching.java` | `docs/algorithms/searching/searching.md` | O(log n) |
| Binary Search (recursive) | `python/algorithms/searching/searching.py` | `java/algorithms/searching/Searching.java` | `docs/algorithms/searching/searching.md` | O(log n) |
| Binary Search (first/last occurrence) | `python/algorithms/searching/searching.py` | `java/algorithms/searching/Searching.java` | `docs/algorithms/searching/searching.md` | O(log n) |
| Rotated Array Search | `python/algorithms/searching/searching.py` | `java/algorithms/searching/Searching.java` | `docs/algorithms/searching/searching.md` | O(log n) |
| Peak Finding | `python/algorithms/searching/searching.py` | `java/algorithms/searching/Searching.java` | `docs/algorithms/searching/searching.md` | O(log n) |
| Ternary Search | `python/algorithms/searching/searching.py` | `java/algorithms/searching/Searching.java` | `docs/algorithms/searching/searching.md` | O(log n) |
| Exponential Search | `python/algorithms/searching/searching.py` | `java/algorithms/searching/Searching.java` | `docs/algorithms/searching/searching.md` | O(log n) |
| Interpolation Search | `python/algorithms/searching/searching.py` | `java/algorithms/searching/Searching.java` | `docs/algorithms/searching/searching.md` | O(log log n) avg |

### Dynamic Programming

| Algorithm | Python | Java | Docs | Time Complexity |
|---|---|---|---|---|
| Fibonacci | `python/algorithms/dp/dp.py` | `java/algorithms/dp/DP.java` | `docs/algorithms/dp/dp.md` | O(n) |
| 0/1 Knapsack | `python/algorithms/dp/dp.py` | `java/algorithms/dp/DP.java` | `docs/algorithms/dp/dp.md` | O(n·W) |
| Longest Common Subsequence | `python/algorithms/dp/dp.py` | `java/algorithms/dp/DP.java` | `docs/algorithms/dp/dp.md` | O(m·n) |
| Longest Increasing Subsequence | `python/algorithms/dp/dp.py` | `java/algorithms/dp/DP.java` | `docs/algorithms/dp/dp.md` | O(n log n) |
| Edit Distance | `python/algorithms/dp/dp.py` | `java/algorithms/dp/DP.java` | `docs/algorithms/dp/dp.md` | O(m·n) |
| Coin Change | `python/algorithms/dp/dp.py` | `java/algorithms/dp/DP.java` | `docs/algorithms/dp/dp.md` | O(n·W) |
| Matrix Chain Multiplication | `python/algorithms/dp/dp.py` | `java/algorithms/dp/DP.java` | `docs/algorithms/dp/dp.md` | O(n³) |
| Longest Palindromic Substring | `python/algorithms/dp/dp.py` | `java/algorithms/dp/DP.java` | `docs/algorithms/dp/dp.md` | O(n²) |

### Graph Algorithms

| Algorithm | Python | Java | Docs | Time Complexity |
|---|---|---|---|---|
| Dijkstra's Shortest Path | `python/algorithms/graph/graph_algorithms.py` | `java/algorithms/graph/GraphAlgorithms.java` | `docs/algorithms/graph/graph_algorithms.md` | O((V + E) log V) |
| Bellman-Ford | `python/algorithms/graph/graph_algorithms.py` | `java/algorithms/graph/GraphAlgorithms.java` | `docs/algorithms/graph/graph_algorithms.md` | O(V·E) |
| Floyd-Warshall | `python/algorithms/graph/graph_algorithms.py` | `java/algorithms/graph/GraphAlgorithms.java` | `docs/algorithms/graph/graph_algorithms.md` | O(V³) |
| Kruskal MST | `python/algorithms/graph/graph_algorithms.py` | `java/algorithms/graph/GraphAlgorithms.java` | `docs/algorithms/graph/graph_algorithms.md` | O(E log E) |
| Prim MST | `python/algorithms/graph/graph_algorithms.py` | `java/algorithms/graph/GraphAlgorithms.java` | `docs/algorithms/graph/graph_algorithms.md` | O((V + E) log V) |
| Tarjan SCC | `python/algorithms/graph/graph_algorithms.py` | `java/algorithms/graph/GraphAlgorithms.java` | `docs/algorithms/graph/graph_algorithms.md` | O(V + E) |
| Topological Sort (Kahn) | `python/algorithms/graph/graph_algorithms.py` | `java/algorithms/graph/GraphAlgorithms.java` | `docs/algorithms/graph/graph_algorithms.md` | O(V + E) |
| A* Search | `python/algorithms/graph/graph_algorithms.py` | `java/algorithms/graph/GraphAlgorithms.java` | `docs/algorithms/graph/graph_algorithms.md` | O(E log V) |

### String Algorithms

| Algorithm | Python | Java | Docs | Time Complexity |
|---|---|---|---|---|
| KMP | `python/algorithms/string/string_algorithms.py` | `java/algorithms/string/StringAlgorithms.java` | `docs/algorithms/string/string_algorithms.md` | O(n + m) |
| Rabin-Karp | `python/algorithms/string/string_algorithms.py` | `java/algorithms/string/StringAlgorithms.java` | `docs/algorithms/string/string_algorithms.md` | O(n + m) avg |
| Z-Algorithm | `python/algorithms/string/string_algorithms.py` | `java/algorithms/string/StringAlgorithms.java` | `docs/algorithms/string/string_algorithms.md` | O(n + m) |
| Manacher's | `python/algorithms/string/string_algorithms.py` | `java/algorithms/string/StringAlgorithms.java` | `docs/algorithms/string/string_algorithms.md` | O(n) |
| String Hashing | `python/algorithms/string/string_algorithms.py` | `java/algorithms/string/StringAlgorithms.java` | `docs/algorithms/string/string_algorithms.md` | O(n) |
| Anagram Detection | `python/algorithms/string/string_algorithms.py` | `java/algorithms/string/StringAlgorithms.java` | `docs/algorithms/string/string_algorithms.md` | O(n) |
| Longest Common Substring | `python/algorithms/string/string_algorithms.py` | `java/algorithms/string/StringAlgorithms.java` | `docs/algorithms/string/string_algorithms.md` | O(m·n) |
| Run-Length Encoding | `python/algorithms/string/string_algorithms.py` | `java/algorithms/string/StringAlgorithms.java` | `docs/algorithms/string/string_algorithms.md` | O(n) |

### Math Algorithms

| Algorithm | Python | Java | Docs | Time Complexity |
|---|---|---|---|---|
| GCD / LCM | `python/algorithms/math/math_algorithms.py` | `java/algorithms/math/MathAlgorithms.java` | `docs/algorithms/math/math_algorithms.md` | O(log min(a,b)) |
| Sieve of Eratosthenes | `python/algorithms/math/math_algorithms.py` | `java/algorithms/math/MathAlgorithms.java` | `docs/algorithms/math/math_algorithms.md` | O(n log log n) |
| Fast Exponentiation | `python/algorithms/math/math_algorithms.py` | `java/algorithms/math/MathAlgorithms.java` | `docs/algorithms/math/math_algorithms.md` | O(log n) |
| Modular Arithmetic | `python/algorithms/math/math_algorithms.py` | `java/algorithms/math/MathAlgorithms.java` | `docs/algorithms/math/math_algorithms.md` | O(log n) |
| Prime Factorization | `python/algorithms/math/math_algorithms.py` | `java/algorithms/math/MathAlgorithms.java` | `docs/algorithms/math/math_algorithms.md` | O(√n) |
| Combinations / Permutations | `python/algorithms/math/math_algorithms.py` | `java/algorithms/math/MathAlgorithms.java` | `docs/algorithms/math/math_algorithms.md` | O(n) |
| Catalan Numbers | `python/algorithms/math/math_algorithms.py` | `java/algorithms/math/MathAlgorithms.java` | `docs/algorithms/math/math_algorithms.md` | O(n) |
| Matrix Exponentiation | `python/algorithms/math/math_algorithms.py` | `java/algorithms/math/MathAlgorithms.java` | `docs/algorithms/math/math_algorithms.md` | O(k³ log n) |

## Quick Complexity Reference

| Data Structure | Access | Search | Insert | Delete | Space |
|---|---|---|---|---|---|
| Array | O(1) | O(n) | O(n) | O(n) | O(n) |
| Linked List | O(n) | O(n) | O(1) | O(1)* | O(n) |
| Stack | O(n) | O(n) | O(1) | O(1) | O(n) |
| Queue | O(n) | O(n) | O(1) | O(1) | O(n) |
| HashMap | O(1) avg | O(1) avg | O(1) avg | O(1) avg | O(n) |
| BST | O(log n) avg | O(log n) avg | O(log n) avg | O(log n) avg | O(n) |
| AVL Tree | O(log n) | O(log n) | O(log n) | O(log n) | O(n) |
| Heap | O(1) peek | O(n) | O(log n) | O(log n) | O(n) |
| Trie | — | O(m) | O(m) | O(m) | O(n·m) |
| Segment Tree | — | O(log n) | O(log n) | O(log n) | O(n) |
| Fenwick Tree | — | O(log n) | O(log n) | — | O(n) |
| Union Find | — | O(α(n)) | O(α(n)) | — | O(n) |
| B-Tree | O(log n) | O(log n) | O(log n) | O(log n) | O(n) |
| Red-Black Tree | O(log n) | O(log n) | O(log n) | O(log n) | O(n) |
| Skip List | O(log n) avg | O(log n) avg | O(log n) avg | O(log n) avg | O(n log n) |
| Bloom Filter | — | O(k) | O(k) | — | O(m) |
| Sparse Table | O(1) | O(1) | O(n log n)† | — | O(n log n) |
| LFU Cache | O(1) | O(1) | O(1) | O(1) | O(n) |
| Treap | O(log n) avg | O(log n) avg | O(log n) avg | O(log n) avg | O(n) |

*with reference to node
†build time; queries are O(1)

#### Advanced / Specialized Data Structures Complexity

| Data Structure | Access | Search | Insert | Delete | Space | Notes |
|---|---|---|---|---|---|---|
| Suffix Tree | — | O(m) | O(n) build | — | O(n) | Preprocessing; linear space variant |
| Suffix Array | — | O(m log n) | O(n log n) build | — | O(n) | Memory efficient, often preferred |
| Heavy-Light Decomp. | — | O(log² n) | O(log² n) | O(log² n) | O(n) | Tree path queries |
| Link-Cut Tree | — | O(log n) | O(log n) | O(log n) | O(n) | Dynamic connectivity |
| Persistent Seg. Tree | — | O(log n) | O(log n) | — | O(n log n) | Immutable versions |
| Cartesian Tree | — | O(log n) avg | O(log n) avg | O(log n) avg | O(n) | RMQ, stack simulation |
| Splay Tree | — | O(log n) amort. | O(log n) amort. | O(log n) amort. | O(n) | Cache-oblivious |
| AC Automaton | — | O(n+m) | O(m log Σ) build | — | O(n·m) | Multi-pattern matching |
| KD-Tree | — | O(√n) avg | O(log n) avg | — | O(n) | Spatial data, range queries |
| Dancing Links | — | O(k) | O(k) | O(1) | O(n·m) | Exact cover, constraint satisfaction |
| Van Emde Boas | O(1) | O(log log U) | O(log log U) | O(log log U) | O(U) | Integer universe U |
| Leftist Heap | O(1) peek | O(log n) | O(log n) | O(log n) | O(n) | Mergeable, merge O(log n) |
| Fibonacci Heap | O(1) peek | O(log n) | O(1) amort. | O(log n) amort. | O(n) | Optimal decreaseKey |
| B+ Tree | O(log n) | O(log n) | O(log n) | O(log n) | O(n) | Database indices |
| Seg. Tree Lazy | — | O(log n) | O(log n) | O(log n) | O(n) | Range updates |

## How to Use the Agents

This repo includes two Claude Code agents for mock interview practice.

### sde2-interviewer — Practice being the candidate

```
/agent sde2-interviewer
```

Alex (the interviewer) will conduct a realistic 45-60 minute mock interview. Just respond as you would in a real interview — think out loud, ask clarifying questions, write code.

### sde-candidate — Practice being the interviewer

```
/agent sde-candidate
```

Jordan (the candidate) will respond to any problem you give. Use this to practice formulating good questions, giving hints, and evaluating answers.

See `AGENTS.md` for example conversation flows.

## How to Navigate This Repo

**Recommended study approach:**

1. **Read the doc** (`docs/`) — understand the structure, invariants, and complexity
2. **Study the Python implementation** — easier to read, great for understanding the algorithm
3. **Study the Java implementation** — practice for language-specific interviews
4. **Run the demos** — each implementation has a `main` block you can execute

```bash
# Run a Python demo
python3 python/basic/stack.py
python3 python/advanced/avl_tree.py

# Run a Java demo (compile first)
javac java/basic/Stack.java && java -cp java/basic Stack
```

## Features

This repository provides a comprehensive, interview-ready resource:

- **Dual Language Coverage**: Python for clarity, Java for production readiness — each data structure and algorithm in both languages
- **Visual Documentation**: ASCII art diagrams, tree structures, and state transitions for every concept
- **Complexity Analysis**: Complete time and space complexity for all operations
- **Implementation Demonstrations**: Runnable demos in both languages showing practical usage
- **Mermaid Flowcharts**: Visual decision trees and algorithm flow diagrams
- **Problem-Solving Guides**: Structured decision guides for DS and algorithm selection
- **Mock Interview Agents**: Two Claude agents for realistic practice interviews
- **Progressive Difficulty**: From basic (arrays, linked lists) to advanced (suffix trees, flow algorithms)

## Interview Prep Roadmap

### Week 1 — Basic Data Structures
- Day 1-2: Array, Dynamic Array
- Day 3-4: Linked Lists (singly + doubly)
- Day 5: Stack + Queue
- Day 6: Deque
- Day 7: HashMap (including collision resolution)

### Week 2 — Trees and Heaps
- Day 1-2: BST (insert, delete, traversals)
- Day 3-4: AVL Tree (rotations, balancing)
- Day 5-6: Heap (min/max, heap sort, K-th element problems)
- Day 7: Trie (autocomplete, word search)

### Week 3 — Graphs and Advanced Structures
- Day 1-2: Graph (BFS, DFS, cycle detection, topological sort)
- Day 3: Union Find
- Day 4: Segment Tree + Fenwick Tree
- Day 5: LRU Cache
- Day 6: B-Tree (conceptual for system design)
- Day 7: Mock interviews with the agents

### Week 4 — New / Specialized DS and Algorithms
- Day 1: Red-Black Tree + Treap (self-balancing BST variants)
- Day 2: Skip List + Sparse Table (probabilistic structures + range queries)
- Day 3: Bloom Filter + LFU Cache (probabilistic membership + advanced caching)
- Day 4: Sorting algorithms (Merge, Quick 3-way, Heap, Tim Sort) + Searching (binary search variants, rotated array, peak finding)
- Day 5: Dynamic Programming (Knapsack, LCS, LIS, Edit Distance, Coin Change)
- Day 6: Graph algorithms (Dijkstra, Bellman-Ford, Floyd-Warshall, Kruskal/Prim MST, Tarjan SCC, A*)
- Day 7: String algorithms (KMP, Rabin-Karp, Z-algorithm, Manacher's) + Math algorithms (Sieve, fast exponentiation, matrix exponentiation) + Mock interviews with the agents

### Week 5 — Advanced Data Structures
- Day 1-2: Suffix Tree + Suffix Array (advanced string indexing)
- Day 3-4: Heavy-Light Decomposition + Link-Cut Tree (advanced tree queries)
- Day 5: Persistent Segment Tree + Cartesian Tree
- Day 6: Splay Tree + Dancing Links
- Day 7: Specialized structures (KD-Tree, Van Emde Boas, Fibonacci Heap) + Use cases review

### Week 6 — Advanced Algorithms
- Day 1-2: Advanced DP (CHT, Digit DP, Tree DP, SOS DP, Knuth-Yao)
- Day 3-4: Graph algorithms (Max Flow, Min Cost Max Flow, Bipartite Matching, 2-SAT)
- Day 5: String algorithms (Boyer-Moore, AC Automaton, Lyndon Factorization)
- Day 6: Geometry (Convex Hull, Closest Pair, Point in Polygon, Line Intersection)
- Day 7: Tree algorithms (Centroid Decomposition, Square Root Decomposition, Mo's Algorithm) + Mock interviews

### Week 7 — Integration & Practice
- Day 1-2: Use data structure and algorithm selection guides on mixed problems
- Day 3-4: Solve problems requiring multiple DS/algorithm combinations
- Day 5-6: Practice explaining trade-offs and optimization decisions
- Day 7: Full mock interview with complex, multi-concept problems

### Week 8 — Mock Interviews
- Conduct 3-4 full 45-60 minute mock interviews
- Use `/agent sde2-interviewer` to practice as candidate
- Use `/agent sde-candidate` to practice problem formulation and evaluation
- Focus on communication, problem breakdown, and optimization
