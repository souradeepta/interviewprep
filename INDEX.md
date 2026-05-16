# Datastructures Repository Index

A comprehensive resource for learning and practicing data structures and algorithms with implementations in Python and Java.

---

## Table of Contents
1. [Data Structures](#data-structures)
2. [Algorithms](#algorithms)
3. [Problem-Solving Guides](#problem-solving-guides)
4. [Agent Practice Tools](#agent-practice-tools)

---

## Data Structures

### Basic Data Structures (7)
Foundational data structures that form the building blocks for more complex structures.

**Python** (`python/basic/`):
- [Array/Dynamic Array](python/basic/array.py) - Resizable array implementation
- [Stack](python/basic/stack.py) - LIFO data structure
- [Queue](python/basic/queue_ds.py) - FIFO data structure
- [Deque](python/basic/deque_ds.py) - Double-ended queue
- [Singly Linked List](python/basic/linked_list.py) - Single pointer chain
- [Hash Map](python/basic/hashmap.py) - Key-value storage

**Java** (`java/basic/`):
- DynamicArray.java - Resizable array implementation
- Stack.java - LIFO data structure
- Queue.java - FIFO data structure
- Deque.java - Double-ended queue
- SinglyLinkedList.java - Single pointer chain
- DoublyLinkedList.java - Bidirectional linked list
- HashMap.java - Key-value storage

---

### Advanced Data Structures (11)
Tree and forest-based structures with advanced search and ordering capabilities.

**Python** (`python/advanced/`):
- [Binary Search Tree (BST)](python/advanced/bst.py) - Ordered tree structure
- [AVL Tree](python/advanced/avl_tree.py) - Self-balancing binary search tree
- [B-Tree](python/advanced/btree.py) - Multi-way balanced search tree
- [Heap/Min Heap](python/advanced/heap.py) - Complete binary tree with heap property
- [Trie](python/advanced/trie.py) - Prefix tree for string storage
- [Graph](python/advanced/graph.py) - General graph with vertices and edges
- [Union-Find](python/advanced/union_find.py) - Disjoint set union structure
- [Fenwick Tree (BIT)](python/advanced/fenwick_tree.py) - Binary indexed tree
- [Segment Tree](python/advanced/segment_tree.py) - Range query tree
- [LRU Cache](python/advanced/lru_cache.py) - Least recently used cache

**Java** (`java/advanced/`):
- BST.java - Ordered tree structure
- AVLTree.java - Self-balancing binary search tree
- BTree.java - Multi-way balanced search tree
- MinHeap.java - Complete binary tree with heap property
- Trie.java - Prefix tree for string storage
- Graph.java - General graph with vertices and edges
- UnionFind.java - Disjoint set union structure
- FenwickTree.java - Binary indexed tree
- SegmentTree.java - Range query tree
- LRUCache.java - Least recently used cache

---

### Specialized/Hybrid Data Structures (7)
Modern data structures combining multiple concepts for specific use cases.

**Python** (`python/new_ds/`):
- [Skip List](python/new_ds/skip_list.py) - Probabilistic balanced list
- [Red-Black Tree](python/new_ds/red_black_tree.py) - Self-balancing BST variant
- [Treap](python/new_ds/treap.py) - Randomized search tree
- [Bloom Filter](python/new_ds/bloom_filter.py) - Probabilistic membership test
- [Sparse Table](python/new_ds/sparse_table.py) - Preprocessed RMQ structure
- [LFU Cache](python/new_ds/lfu_cache.py) - Least frequently used cache

**Java** (`java/new_ds/`):
- SkipList.java - Probabilistic balanced list
- RedBlackTree.java - Self-balancing BST variant
- Treap.java - Randomized search tree
- BloomFilter.java - Probabilistic membership test
- SparseTable.java - Preprocessed RMQ structure
- LFUCache.java - Least frequently used cache

---

### Advanced/Specialized Data Structures (2)
Highly specialized structures for complex problems and optimizations.

**Python** (`python/advanced_ds/`):
- [Heavy-Light Decomposition](python/advanced_ds/heavy_light_decomposition.py) - Tree decomposition technique
- [Segment Tree with Lazy Propagation](python/advanced_ds/segment_tree_lazy.py) - Optimized range update/query

**Java** (`java/advanced_ds/`):
- HeavyLightDecomposition.java - Tree decomposition technique

---

## Algorithms

### Sorting Algorithms (10)
Algorithms for arranging elements in order.

**Python** (`python/algorithms/sorting/`):
- sorting.py - Includes multiple sorting algorithms

**Java** (`java/algorithms/sorting/`):
- Sorting.java - Comprehensive sorting implementations

Covered algorithms typically include:
- Bubble Sort, Selection Sort, Insertion Sort
- Merge Sort, Quick Sort, Heap Sort
- Counting Sort, Radix Sort, Bucket Sort
- Shell Sort

---

### Searching Algorithms (9)
Algorithms for finding elements in data structures.

**Python** (`python/algorithms/searching/`):
- searching.py - Linear and binary search implementations

**Java** (`java/algorithms/searching/`):
- Searching.java - Comprehensive searching implementations

Covered algorithms typically include:
- Linear Search, Binary Search
- Interpolation Search, Exponential Search
- Jump Search, Ternary Search
- Fibonacci Search

---

### Dynamic Programming (8)
Techniques for solving optimization problems with overlapping subproblems.

**Python** (`python/algorithms/dp/`):
- [dp.py](python/algorithms/dp/dp.py) - DP algorithms and techniques

**Java** (`java/algorithms/dp/`):
- DP.java - DP algorithms and techniques

Covered problems typically include:
- Fibonacci, Coin Change
- Longest Common Subsequence (LCS)
- Longest Increasing Subsequence (LIS)
- Knapsack Problems
- Matrix Chain Multiplication

---

### Graph Algorithms (8)
Algorithms for processing and analyzing graphs.

**Python** (`python/algorithms/graph/`):
- [graph_algorithms.py](python/algorithms/graph/graph_algorithms.py) - Graph traversal and algorithms

**Java** (`java/algorithms/graph/`):
- GraphAlgorithms.java - Graph traversal and algorithms

Covered algorithms typically include:
- BFS, DFS, Topological Sort
- Dijkstra's Algorithm, Bellman-Ford
- Floyd-Warshall, Minimum Spanning Tree (Kruskal/Prim)
- Strongly Connected Components

---

### String Algorithms (10)
Algorithms for string processing and pattern matching.

**Python** (`python/algorithms/string/`):
- [string_algorithms.py](python/algorithms/string/string_algorithms.py) - String manipulation and matching

**Java** (`java/algorithms/string/`):
- StringAlgorithms.java - String manipulation and matching

Covered algorithms typically include:
- Pattern Matching (KMP, Rabin-Karp)
- Palindrome Detection, Anagram Checking
- Longest Palindromic Subsequence
- Edit Distance, LCS
- Trie-based operations

---

### Math Algorithms (8)
Algorithms for mathematical computations and number theory.

**Python** (`python/algorithms/math/`):
- [math_algorithms.py](python/algorithms/math/math_algorithms.py) - Mathematical algorithms

**Java** (`java/algorithms/math/`):
- MathAlgorithms.java - Mathematical algorithms

Covered algorithms typically include:
- Prime Checking, Sieve of Eratosthenes
- GCD, LCM, Modular Arithmetic
- Fast Exponentiation
- Combinatorics, Permutations
- Number Theory problems

---

### Advanced Algorithms (~1+)
Complex algorithms combining multiple techniques.

**Python** (`python/algorithms/advanced/`):
- Space for advanced algorithm combinations

**Java** (`java/algorithms/advanced/`):
- Space for advanced algorithm combinations

---

## Problem-Solving Guides

### Quick Reference
- **[DS Selection Guide](docs/guides/)** - Choose the right data structure for your problem
- **[Algorithm Selection Guide](docs/guides/)** - Choose the right algorithm for your use case
- **[Problem-Solving Flowchart](docs/guides/)** - Step-by-step approach to tackling problems

### Documentation by Category

**Data Structure Docs** (`docs/`):
- `basic/` - Explanations of basic data structures
- `advanced/` - Explanations of advanced data structures
- `new_ds/` - Explanations of specialized data structures
- `advanced_ds/` - Explanations of highly specialized structures

**Algorithm Docs** (`docs/algorithms/`):
- `sorting/` - Sorting algorithm explanations
- `searching/` - Searching algorithm explanations
- `dp/` - Dynamic programming explanations
- `graph/` - Graph algorithm explanations
- `string/` - String algorithm explanations
- `math/` - Mathematical algorithm explanations
- `advanced/` - Advanced algorithm combinations

---

## Agent Practice Tools

### Interview Practice Agents

1. **[SDE2 Interviewer](agents/sde2-interviewer/)** 
   - Advanced system design and problem-solving practice
   - Interview simulation with real-world scenarios
   - Uses data structures and algorithms in practical contexts

2. **[SDE Candidate](agents/sde-candidate/)**
   - General SDE interview preparation
   - Covers data structures, algorithms, and coding problems
   - Interactive practice mode

---

## Quick Start Guide

### For Learning a Specific Data Structure
1. Navigate to the appropriate folder (basic, advanced, new_ds, or advanced_ds)
2. Read the implementation in Python or Java
3. Check the corresponding docs folder for explanation and complexity analysis
4. Try implementing modifications or solving related problems

### For Learning a Specific Algorithm
1. Navigate to the appropriate algorithm category folder
2. Study the implementation
3. Review the docs for algorithm explanation and complexity
4. Practice with related problems

### For Interview Preparation
1. Start with basic data structures and algorithms
2. Move to advanced data structures
3. Practice with the agent tools (sde2-interviewer, sde-candidate)
4. Solve real problem-solving challenges using the guides

### For Quick Lookups
- Use this INDEX as your navigation hub
- Refer to docs/guides for decision-making
- Check Python implementations first (usually more readable), then Java for production code

---

## Repository Statistics

**Data Structures:** 38 total implementations
- Basic: 7
- Advanced: 11
- Specialized: 7
- Advanced/Specialized: 2
- Other: 11 (new_ds folder split)

**Algorithms:** 83+ implementations across categories
- Sorting: 10
- Searching: 9
- Dynamic Programming: 8
- Graph: 8
- String: 10
- Math: 8
- Advanced: 1+

**Languages:** Python and Java implementations for most structures

**Documentation:** Comprehensive guides and problem-solving resources

---

## File Organization

```
interviewprep/
├── python/
│   ├── basic/              (7 implementations)
│   ├── advanced/           (11 implementations)
│   ├── new_ds/             (7 implementations)
│   ├── advanced_ds/        (2 implementations)
│   └── algorithms/
│       ├── sorting/        (10 algorithms)
│       ├── searching/      (9 algorithms)
│       ├── dp/             (8 algorithms)
│       ├── graph/          (8 algorithms)
│       ├── string/         (10 algorithms)
│       ├── math/           (8 algorithms)
│       └── advanced/       (1+ algorithms)
├── java/
│   ├── basic/              (7 implementations)
│   ├── advanced/           (10 implementations)
│   ├── new_ds/             (6 implementations)
│   ├── advanced_ds/        (1 implementation)
│   └── algorithms/
│       ├── sorting/
│       ├── searching/
│       ├── dp/
│       ├── graph/
│       ├── string/
│       ├── math/
│       └── advanced/
├── docs/                   (Comprehensive documentation)
├── agents/                 (Interview practice tools)
└── INDEX.md               (This file - your navigation hub)
```

---

## Usage Tips

1. **For Beginners:** Start with basic data structures, understand each thoroughly, then move to advanced
2. **For Interview Prep:** Use the agent tools after mastering individual components
3. **For Reference:** This INDEX serves as your quick lookup table for finding implementations
4. **For Implementation:** Check both Python (for clarity) and Java (for production) versions

---

Last updated: 2026-05-14
