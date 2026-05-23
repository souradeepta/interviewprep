# Algorithms — Complete Implementation Reference

Algorithms organized by category with Python and Java implementations.

---

## 📚 Algorithm Categories

### 🔤 Sorting & Searching
- **[Sorting Algorithms](sorting/)** — Bubble, selection, insertion, merge, quick, heap, counting, radix
- **[Searching Algorithms](searching/)** — Linear search, binary search, variations

### 🧮 Dynamic Programming
- **[DP Patterns](dp/)** — Fibonacci, coin change, knapsack, LCS, LIS, edit distance, matrix chain

### 📊 Graph Algorithms
- **[Graph Fundamentals](graphs/)** — BFS, DFS, topological sort, cycle detection
- **[Advanced Graph](graphs/advanced/)** — Dijkstra, Bellman-Ford, MST (Kruskal, Prim), Floyd-Warshall

### 🔤 String Algorithms
- **[String Matching](string-algorithms/)** — KMP, Z-algorithm, Rabin-Karp, suffix arrays

### 🎯 Greedy Algorithms
- **[Greedy Patterns](greedy/)** — Activity selection, fractional knapsack, Huffman coding

### 🔢 Math & Number Theory
- **[Math Fundamentals](math/)** — GCD, LCM, prime checking, modular arithmetic, combinatorics

### 🎨 Bit Manipulation
- **[Bit Techniques](bit-manipulation/)** — AND, OR, XOR tricks, bit counting, subset generation

### 📐 Geometry
- **[Geometry Basics](geometry/)** — Coordinate geometry, distance, area, line intersection

---

## 🎯 Quick Access

| Algorithm | Difficulty | Time | Space | Guide | Python | Java |
|-----------|-----------|------|-------|-------|--------|------|
| Bubble Sort | Easy | O(n²) | O(1) | [Link](sorting/) | [Py](sorting/code/python/) | [Jv](sorting/code/java/) |
| Merge Sort | Medium | O(n log n) | O(n) | [Link](sorting/) | [Py](sorting/code/python/) | [Jv](sorting/code/java/) |
| Binary Search | Medium | O(log n) | O(1) | [Link](searching/) | [Py](searching/code/python/) | [Jv](searching/code/java/) |
| Dynamic Programming | Hard | Varies | Varies | [Link](dp/) | [Py](dp/code/python/) | [Jv](dp/code/java/) |
| Graph BFS/DFS | Medium | O(V+E) | O(V) | [Link](graphs/) | [Py](graphs/code/python/) | [Jv](graphs/code/java/) |
| Dijkstra | Hard | O((V+E)logV) | O(V) | [Link](graphs/advanced/) | [Py](graphs/code/python/) | [Jv](graphs/code/java/) |
| KMP String Match | Hard | O(n+m) | O(m) | [Link](string-algorithms/) | [Py](string-algorithms/code/python/) | [Jv](string-algorithms/code/java/) |

---

## 🚀 Learning Path

### Beginner Week
1. Sorting (bubble, selection, insertion)
2. Searching (linear, binary)
3. Basic DP (Fibonacci, coin change)

### Intermediate Week
4. Graph basics (BFS, DFS)
5. More DP (knapsack, LCS)
6. String algorithms

### Advanced Week
7. Advanced graph (Dijkstra, MST)
8. Bit manipulation tricks
9. Complex DP (matrix chain)

---

## 📁 Repository Structure

```
docs/05-algorithms/
├── README.md (this file)
├── sorting/
│   ├── README.md (sorting guide)
│   ├── code/
│   │   ├── python/
│   │   │   ├── sorting.py
│   │   │   └── test_sorting.py
│   │   └── java/
│   │       ├── Sorting.java
│   │       └── SortingTest.java
│   └── problems.md (LeetCode problems)
├── searching/
├── dp/
├── graphs/
├── string-algorithms/
├── greedy/
├── math/
├── bit-manipulation/
└── geometry/
```

---

## ✅ How to Use

1. **Learn concept:** Read category README (e.g., `sorting/README.md`)
2. **See implementations:** Check `code/python/` or `code/java/`
3. **Practice problems:** Solve problems in `problems.md`
4. **Run tests:** `pytest docs/05-algorithms/sorting/code/python/test_sorting.py`

---

## 🎯 All Algorithms At a Glance

### Sorting (8 algorithms)
- Bubble, Selection, Insertion, Merge, Quick, Heap, Counting, Radix

### Searching (3 algorithms)
- Linear, Binary, Binary (recursive)

### Dynamic Programming (10+ patterns)
- Fibonacci, Knapsack, LCS, LIS, Edit Distance, Coin Change, Matrix Chain, etc.

### Graph (8+ algorithms)
- BFS, DFS, Topological Sort, Dijkstra, Bellman-Ford, Kruskal, Prim, Floyd-Warshall

### String Matching (4 algorithms)
- KMP, Z-Algorithm, Rabin-Karp, Suffix Arrays

### Other (15+ techniques)
- Greedy, Math, Bit Manipulation, Geometry

**Total:** 50+ algorithms with complete implementations

---

**Last updated:** 2026-05-22
