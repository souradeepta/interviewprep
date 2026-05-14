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
