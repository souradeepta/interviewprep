# Advanced Algorithms - Quick Reference Guide

## 30 Algorithms at a Glance

### How to Use This Guide
- **Read the algorithm name** to identify what you need
- **Check the Time/Space complexity** for performance requirements
- **Use the file location** to find the implementation
- **Run the demo** to see working examples

---

## 1. DYNAMIC PROGRAMMING - ADVANCED

### ConvexHullTrick
- **Problem**: Optimize DP transitions where `dp[i] = min(dp[j] + cost(j,i))`
- **Time**: O(n log n) | **Space**: O(n)
- **Files**: Python `advanced_algorithms.py:L127`, Java `AdvancedAlgorithms.java:L24`
- **When to use**: When DP recurrence involves linear functions forming convex hull

### DigitDP
- **Problem**: Count numbers in [0,N] with digit properties
- **Time**: O(log N × state_space) | **Space**: O(state_space)
- **Example**: Count numbers with no consecutive 1s in binary
- **Files**: Python `L179`, Java `L106`

### TreeDP
- **Problem**: DP on tree structures (maximum independent set, coloring)
- **Time**: O(n) | **Space**: O(n)
- **Example**: Maximum nodes selected with no adjacency
- **Files**: Python `L235`, Java `L137`

### KnuthYaoOptimization
- **Problem**: Reduce O(n³) DP to O(n²) when costs satisfy quadrangle inequality
- **Time**: O(n²) | **Space**: O(n)
- **Example**: Optimal BST cost computation
- **Files**: Python `L291`, Java `N/A`

### SOS_DP
- **Problem**: Process all subsets in O(n × 2^n) instead of O(3^n)
- **Time**: O(n × 2^n) | **Space**: O(2^n)
- **Example**: Subset sum convolution
- **Files**: Python `L327`, Java `L160`

---

## 2. GRAPH ALGORITHMS - ADVANCED

### MaxFlowFordFulkerson
- **Problem**: Find maximum flow from source to sink (simple version)
- **Time**: O(E × max_flow) | **Space**: O(V + E)
- **Limitation**: Can be slow with bad edge orderings
- **Files**: Python `L375`, Java `N/A`

### MaxFlowDinic ⭐ **MUST KNOW**
- **Problem**: Find maximum flow efficiently
- **Time**: O(V² × E) | **Space**: O(V + E)
- **When to use**: Better than Ford-Fulkerson for most cases
- **Files**: Python `L423`, Java `L186`
- **Demo**: 6-node graph → max flow 23

### MinCostMaxFlow
- **Problem**: Find max flow with minimum total cost
- **Time**: O(V × E × log V) | **Space**: O(V + E)
- **When to use**: Need both maximum flow AND minimum cost
- **Files**: Python `L486`, Java `N/A`

### BipartiteMatchingAugmenting ⭐ **MUST KNOW**
- **Problem**: Find maximum matching in bipartite graph
- **Time**: O(V × E) | **Space**: O(V)
- **When to use**: Assignment problems, Hall's theorem applications
- **Files**: Python `L564`, Java `L237`
- **Demo**: 3×3 bipartite → matching 3

### BipartiteMatchingHopcroftKarp
- **Problem**: Maximum bipartite matching (faster version)
- **Time**: O(E × √V) | **Space**: O(V)
- **When to use**: Large bipartite graphs
- **Files**: Python `L614`, Java `N/A`

### TwoSAT ⭐ **MUST KNOW**
- **Problem**: Determine if 2-CNF formula is satisfiable
- **Time**: O(V + E) | **Space**: O(V + E)
- **When to use**: Boolean satisfiability with 2-literal clauses
- **Files**: Python `L679`, Java `L275`
- **Demo**: 3 variables → satisfiable [F,F,T]

### ArticulationPointsBridges
- **Problem**: Find cut vertices and bridges (critical edges)
- **Time**: O(V + E) | **Space**: O(V + E)
- **When to use**: Find critical vertices/edges in network
- **Files**: Python `L745`, Java `L313`

### VertexConnectivity
- **Problem**: Find minimum vertex cut
- **Time**: O(V² × flow) | **Space**: O(V + E)
- **When to use**: Minimum nodes to disconnect graph
- **Files**: Python `L812`, Java `N/A`

### TransitiveClosure
- **Problem**: Floyd-Warshall for reachability matrix
- **Time**: O(V³) | **Space**: O(V²)
- **When to use**: All-pairs reachability in DAG
- **Files**: Python `L841`, Java `L358`

---

## 3. STRING ALGORITHMS - ADVANCED

### BoyerMoore ⭐
- **Problem**: Efficient pattern matching
- **Time**: O(n/m) best, O(nm) worst | **Space**: O(σ)
- **When to use**: Single pattern search in long text
- **Files**: Python `L882`, Java `L374`
- **Demo**: "PATTERN" in text → positions [10, 27]

### AhoCorasick ⭐
- **Problem**: Find multiple patterns in text efficiently
- **Time**: O(n + z) where z=matches | **Space**: O(m × σ)
- **When to use**: Need to match many patterns simultaneously
- **Files**: Python `L938`, Java `L414`
- **Demo**: Find "he", "she", "his", "hers" → 3 matches

### SuffixArray
- **Problem**: String indexing with LCP for pattern search
- **Time**: O(n log² n) simple | **Space**: O(n)
- **When to use**: Frequent pattern searches on same text
- **Files**: Python `L1003`, Java `N/A`

### Manacher
- **Problem**: Find longest palindromic substring in O(n)
- **Time**: O(n) | **Space**: O(n)
- **When to use**: Palindrome problems
- **Files**: Python `L1050`, Java `N/A`

### ZAlgorithm ⭐
- **Problem**: Pattern matching with Z-array computation
- **Time**: O(n + m) | **Space**: O(n + m)
- **When to use**: Linear-time pattern matching
- **Files**: Python `L1093`, Java `L451`
- **Demo**: "aab" in "aabaaab" → [0, 4]

---

## 4. COMPUTATIONAL GEOMETRY

### ConvexHullGrahamScan
- **Problem**: Find convex hull of points
- **Time**: O(n log n) | **Space**: O(n)
- **Files**: Python `L1149`, Java `N/A`

### ConvexHullAndrewChain ⭐
- **Problem**: Find convex hull (simpler implementation)
- **Time**: O(n log n) | **Space**: O(n)
- **When to use**: Most interviews prefer this approach
- **Files**: Python `L1198`, Java `L495`
- **Demo**: 6 points → hull with 4 vertices

### ClosestPair ⭐
- **Problem**: Find two points with minimum distance
- **Time**: O(n log n) | **Space**: O(n)
- **When to use**: Divide & conquer geometry problems
- **Files**: Python `L1243`, Java `L524`
- **Demo**: 5 points → min distance 3.6056

### LineIntersection
- **Problem**: Check if two line segments intersect
- **Time**: O(1) | **Space**: O(1)
- **When to use**: Segment intersection detection
- **Files**: Python `L1311`, Java `L567`

### PointInPolygon
- **Problem**: Check if point is inside polygon
- **Time**: O(n) | **Space**: O(1)
- **When to use**: Polygon containment queries
- **Files**: Python `L1354`, Java `N/A`

---

## 5. TREE ALGORITHMS

### HeavyLightDecomposition ⭐ **MUST KNOW**
- **Problem**: Path queries on trees
- **Time**: O(n log n) preprocessing, O(log² n) per query | **Space**: O(n)
- **When to use**: Path sum/max queries on trees
- **Files**: Python `L1395`, Java `L595`
- **Demo**: 5-node tree, path 3→4 = [4,3,1,0]

### SquareRootDecomposition ⭐
- **Problem**: Range queries and point updates
- **Time**: O(√n) per operation | **Space**: O(n)
- **When to use**: Array range queries/updates without segment tree
- **Files**: Python `L1492`, Java `L671`
- **Demo**: Array [1,3,5,7,9,11], range sum [1,4] = 24

### MosAlgorithm
- **Problem**: Optimize offline range queries
- **Time**: O((n + q) × √n) | **Space**: O(n + q)
- **When to use**: Many range queries available offline
- **Files**: Python `L1549`, Java `N/A`

---

## 6. MISCELLANEOUS ADVANCED

### QuickSelect
- **Problem**: Find k-th smallest element
- **Time**: O(n) average, O(n²) worst | **Space**: O(log n)
- **When to use**: Finding percentiles, medians
- **Files**: Python `L1600`, Java `L703`
- **Demo**: [3,2,1,5,4], k=2 → 3

### HuffmanCoding
- **Problem**: Generate optimal prefix-free codes
- **Time**: O(n log n) | **Space**: O(n)
- **When to use**: Data compression, encoding
- **Files**: Python `L1653`, Java `L735`
- **Demo**: Frequencies → variable-length codes

### ActivitySelection ⭐
- **Problem**: Select maximum non-overlapping activities
- **Time**: O(n log n) | **Space**: O(n)
- **When to use**: Greedy interval scheduling
- **Files**: Python `L1734`, Java `L768`
- **Demo**: 6 activities → 3 non-overlapping selected

---

## Quick Lookup Table

| Problem | Algorithm | Time | File |
|---------|-----------|------|------|
| Max flow | Dinic | O(V²E) | Python:L423, Java:L186 |
| Bipartite match | Augmenting | O(VE) | Python:L564, Java:L237 |
| 2-SAT | TwoSAT | O(V+E) | Python:L679, Java:L275 |
| Convex hull | Andrew | O(n log n) | Python:L1198, Java:L495 |
| Closest pair | D&C | O(n log n) | Python:L1243, Java:L524 |
| Pattern search | Boyer-Moore | O(n/m) | Python:L882, Java:L374 |
| Multi-pattern | Aho-Corasick | O(n+z) | Python:L938, Java:L414 |
| Pattern match | Z-Algorithm | O(n+m) | Python:L1093, Java:L451 |
| Tree paths | HLD | O(log² n) | Python:L1395, Java:L595 |
| Range query | Sqrt | O(√n) | Python:L1492, Java:L671 |
| k-th smallest | QuickSelect | O(n) avg | Python:L1600, Java:L703 |
| Intervals | Activity Select | O(n log n) | Python:L1734, Java:L768 |

---

## How to Run Demos

### Python
```bash
cd /home/sbisw/github/interviewprep
python3 python/algorithms/advanced/advanced_algorithms.py
```

### Java
```bash
cd /home/sbisw/github/interviewprep/java/algorithms/advanced
javac AdvancedAlgorithms.java
java AdvancedAlgorithms
```

---

## Interview Preparation Priority

### Must Know (Week 1)
1. MaxFlowDinic
2. BipartiteMatching
3. ConvexHullAndrew
4. HeavyLightDecomposition
5. TwoSAT

### Should Know (Week 2)
6. SquareRootDecomposition
7. BoyerMoore
8. AhoCorasick
9. ClosestPair
10. ActivitySelection

### Good to Know (Week 3+)
- Rest of algorithms

---

## Tips for Using This Reference

1. **Before coding**: Check time/space complexity
2. **While coding**: Copy-paste from implementations
3. **During interview**: Explain the algorithm choice
4. **After interview**: Review if you got wrong time complexity

---

## File Structure

```
/home/sbisw/github/interviewprep/
├── python/algorithms/advanced/
│   ├── __init__.py              (30 imports)
│   └── advanced_algorithms.py   (1,868 lines)
├── java/algorithms/advanced/
│   └── AdvancedAlgorithms.java  (1,237 lines)
├── ADVANCED_ALGORITHMS.md       (full guide)
├── IMPLEMENTATION_SUMMARY.md    (completion report)
└── QUICK_REFERENCE.md           (this file)
```

---

**Last Updated**: 2026-05-14
**Total Algorithms**: 30
**Languages**: Python + Java
**Status**: Complete & Tested
