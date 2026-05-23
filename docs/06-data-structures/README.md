# Data Structures — Complete Implementation Reference

Fundamental and advanced data structures with Python and Java implementations.

---

## 📚 Data Structure Categories

### 🔤 Linear Structures
- **[Arrays & Strings](arrays/)** — Static arrays, dynamic arrays, string operations
- **[Linked Lists](linked-lists/)** — Singly, doubly, circular linked lists
- **[Stacks](stacks/)** — LIFO data structure, applications
- **[Queues](queues/)** — FIFO data structure, variants (deque, priority queue)

### 🌳 Tree Structures
- **[Trees Basics](trees/)** — Binary trees, tree traversals, properties
- **[Binary Search Trees](trees/bst/)** — BST operations, self-balancing trees
- **[Advanced Trees](trees/advanced/)** — AVL, Red-Black, B-trees, segment trees

### 📊 Hash-Based Structures
- **[Hash Tables](hash-tables/)** — Hash functions, collision resolution, implementation
- **[Hash Maps/Sets](hash-tables/)** — Practical usage, complexity analysis

### 🎯 Priority & Heap Structures
- **[Heaps](heaps/)** — Min/max heaps, heap operations, applications

### 🔗 Advanced Structures
- **[Tries](tries/)** — Prefix trees, auto-complete, IP routing
- **[Graphs](graphs/)** — Adjacency list, adjacency matrix, graph representations
- **[Disjoint Set Union](dsu/)** — Union-Find, path compression, union by rank

---

## 🎯 Quick Access

| Data Structure | Pros | Cons | Use Case | Time Complexity |
|---|---|---|---|---|
| Array | O(1) access | Fixed size | Sequences | O(1) access, O(n) insert |
| Linked List | Dynamic, O(1) insert | O(n) access | Queues, stacks | O(n) access, O(1) insert |
| Hash Table | O(1) avg | O(n) worst case | Fast lookup | O(1) average |
| Binary Tree | O(log n) search | Unbalanced | Sorted data | O(log n) balanced |
| Heap | O(1) min, O(log n) extract | Not searchable | Priority queues | O(log n) operations |
| Trie | O(m) per key | Memory intensive | Prefix search | O(m) where m = length |
| Graph | Flexible | Complex | Networks | Variable |

---

## 📁 Repository Structure

```
docs/06-data-structures/
├── README.md (this file)
├── arrays/
│   ├── README.md (arrays guide)
│   ├── code/
│   │   ├── python/
│   │   │   └── arrays.py
│   │   └── java/
│   │       └── Arrays.java
│   └── problems.md
├── linked-lists/
│   ├── README.md
│   ├── code/
│   │   ├── python/
│   │   └── java/
│   └── problems.md
├── stacks/
├── queues/
├── trees/
│   ├── README.md
│   ├── code/
│   ├── bst/
│   │   ├── README.md
│   │   └── code/
│   └── advanced/
├── heaps/
├── hash-tables/
├── tries/
├── graphs/
└── dsu/
```

---

## 🚀 Learning Path

### Week 1: Fundamentals
- Arrays/Strings
- Linked Lists
- Stacks & Queues

### Week 2: Trees
- Basic trees & traversals
- Binary Search Trees
- Heaps

### Week 3: Advanced
- Hash Tables (advanced)
- Tries
- Graphs

### Week 4+: Specialized
- Self-balancing trees (AVL, RB)
- Advanced graphs
- Disjoint Set Union

---

## ✅ All Data Structures

### Linear (4)
- Arrays, Linked Lists, Stacks, Queues

### Trees (3 + advanced)
- Binary Trees, BST, Heaps

### Hash-Based (2)
- Hash Tables, Hash Maps

### String (1)
- Tries

### Graph (2)
- Graphs, Disjoint Set Union

**Total:** 17 core data structures with variants

---

## 💡 Interview Tips

- **Array problems:** Think 2-pointer, sliding window
- **Linked list:** Think fast/slow pointers, reversal
- **Trees:** Think recursion, traversals, DFS/BFS
- **Graphs:** Think DFS/BFS, shortest path
- **Hash tables:** Think frequency counting, grouping

---

**Last updated:** 2026-05-22
