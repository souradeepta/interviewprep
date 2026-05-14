# Data Structure Selection Guide

## How to Use This Guide

When solving an interview problem, use this guide to quickly identify the best data structure for your use case:

1. **Start with the Main Decision Flowchart** below to navigate through your problem characteristics
2. **Check the Quick Decision Table** for common patterns and their recommended DS
3. **Review the Common Interview Scenarios** to see real-world examples similar to your problem
4. **Use complexity analysis** to verify your choice meets time/space constraints

This guide covers fundamental, intermediate, and advanced data structures to help you make optimal choices during interviews.

---

## Main Decision Flowchart

```mermaid
graph TD
    A["🎯 START: Data Structure Selection"] --> B["What are you storing?"]
    
    B -->|Key-Value pairs| C["What operations matter most?"]
    B -->|Sorted items| D["Do you need fast insertion/deletion?"]
    B -->|Items with priority| E["Min or Max priority?"]
    B -->|Hierarchical data| F["Need parent/child relationships?"]
    B -->|Network/Graph data| G["What graph operations?"]
    B -->|String data| H["Pattern matching needed?"]
    B -->|Range queries| I["Static or dynamic data?"]
    B -->|Exact duplicates OK| J["Do you need probability?"]
    
    C -->|Fast lookup| K{"Insertion/deletion needed?"}
    C -->|Insertion/Deletion critical| L["Do you need sorted order?"]
    
    K -->|Minimal updates| M["Use HashMap"]
    K -->|Frequent updates| L
    
    L -->|Yes, sorted| N["Use TreeMap<br/>or BST"]
    L -->|No, fast ops| M
    
    D -->|Yes, balanced| O["Insertion freq?"]
    D -->|No, array OK| P["Use Sorted Array"]
    
    O -->|Very frequent| Q["Use AVL Tree<br/>or Red-Black Tree"]
    O -->|Moderate| R["Use BST<br/>or Skip List"]
    
    E -->|Min priority| S["Use Min Heap"]
    E -->|Max priority| T["Use Max Heap"]
    
    F -->|Search in tree| U["Need all traversals?"]
    F -->|Special structure| V["Use appropriate<br/>Tree variant"]
    
    U -->|Yes| W["Use BST or AVL"]
    U -->|Only sorted| X["Use Trie for<br/>autocomplete"]
    
    G -->|Shortest path| Y["Weighted edges?"]
    G -->|Connected components| Z["Use Union Find"]
    G -->|Cycle detection| AA["Use Graph +<br/>DFS/BFS"]
    G -->|DAG traversal| AB["Use Topological<br/>Sort + DP"]
    
    Y -->|Yes| AC["Use Dijkstra's<br/>or Bellman-Ford"]
    Y -->|No| AD["Use BFS"]
    
    H -->|Prefix matching| AE["Use Trie"]
    H -->|Full text search| AF["Use Trie or<br/>KMP/Rabin-Karp"]
    H -->|Substring matching| AG["Use KMP or<br/>Rabin-Karp or<br/>Suffix Tree"]
    
    I -->|Static| AH["Use Sparse Table<br/>or Precompute"]
    I -->|Dynamic| AI["Point updates?"]
    
    AI -->|Yes| AJ["Use Segment Tree<br/>or Fenwick Tree"]
    AI -->|Range updates| AK["Use Lazy Segment Tree"]
    
    J -->|Set membership| AL["Use Bloom Filter"]
    J -->|Frequency counts| AM["Use HashMap"]
    
    M --> BA["✓ HashMap<br/>O(1) avg lookup<br/>O(n) worst case"]
    N --> BA
    P --> BB["✓ Sorted Array<br/>O(n log n) sort<br/>O(log n) search<br/>O(n) insert/delete"]
    Q --> BC["✓ AVL/RB Tree<br/>O(log n) all ops<br/>Self-balancing"]
    R --> BD["✓ BST/Skip List<br/>O(log n) expected<br/>Easier to implement"]
    S --> BE["✓ Min Heap<br/>O(1) peek min<br/>O(log n) insert/remove"]
    T --> BF["✓ Max Heap<br/>O(1) peek max<br/>O(log n) insert/remove"]
    W --> BG["✓ BST/AVL Tree<br/>All tree ops<br/>In-order traversal"]
    X --> BH["✓ Trie<br/>O(m) per operation<br/>m = string length"]
    Z --> BI["✓ Union Find<br/>Nearly O(1) per op<br/>With path compression"]
    AA --> BJ["✓ KMP/Rabin-Karp<br/>O(n+m) or O(n)<br/>No preprocessing"]
    AC --> BK["✓ Dijkstra's<br/>O((V+E)logV)<br/>Non-negative weights"]
    AD --> BL["✓ BFS<br/>O(V+E)<br/>Unweighted graphs"]
    AE --> BM["✓ Trie<br/>O(m) insert/search<br/>Memory intensive"]
    AH --> BN["✓ Sparse Table<br/>O(1) query<br/>No updates"]
    AJ --> BO["✓ Segment Tree<br/>O(log n) per op<br/>Complex code"]
    AK --> BP["✓ Lazy Segment Tree<br/>O(log n) per op<br/>Handles range updates"]
    AL --> BQ["✓ Bloom Filter<br/>O(k) operations<br/>No false negatives"]
```

---

## Quick Decision Table

| Problem Characteristic | Recommended DS | Why | Complexity | Space |
|---|---|---|---|---|
| Fast key-value lookup | HashMap | O(1) average case, simple to implement | O(1) lookup | O(n) |
| Sorted key-value pairs | TreeMap / BST | Maintains order, O(log n) operations | O(log n) all ops | O(n) |
| Top K elements | Min Heap (max-k heap) | Efficient extraction of k largest | O(log k) per insert | O(k) |
| LRU Cache | HashMap + Doubly Linked List | O(1) access, maintains LRU order | O(1) all ops | O(capacity) |
| Autocomplete | Trie | Fast prefix matching, lexicographic order | O(m) per operation | O(alphabet × depth) |
| Range minimum query (static) | Sparse Table | O(1) query after preprocessing | O(1) query | O(n log n) |
| Range min/sum (dynamic) | Segment Tree | Handles point updates + range queries | O(log n) per op | O(n) |
| Range updates + queries | Lazy Segment Tree | Efficiently handles range modifications | O(log n) per op | O(n) |
| Frequency table | HashMap | Count occurrences, O(1) access | O(1) avg | O(n) |
| Sorted stream + find median | Two Heaps | Balanced min/max heaps track median | O(log n) insert | O(n) |
| Connected components | Union Find | Nearly O(1) with path compression | O(α(n)) per op | O(n) |
| Cycle detection | Graph + DFS/Union Find | Detects cycles in directed/undirected | O(V+E) | O(V) |
| Shortest path (unweighted) | BFS | Simple, optimal for unweighted graphs | O(V+E) | O(V) |
| Shortest path (weighted) | Dijkstra's Algorithm | Works with non-negative weights | O((V+E)logV) | O(V) |
| All-pairs shortest path | Floyd-Warshall | Works with negative weights (no cycles) | O(V^3) | O(V^2) |
| Substring matching | KMP / Rabin-Karp | Linear time pattern matching | O(n+m) KMP | O(m) |
| Autocorrect / Spell check | Trie | Fast prefix-based suggestions | O(m) | O(alphabet × depth) |
| Membership testing (prob ok) | Bloom Filter | O(k) constant time, space-efficient | O(k) hash | O(m bits) |
| Self-balancing sorted | AVL Tree | Strictly balanced, better search | O(log n) all ops | O(n) |
| Self-balancing flexible | Red-Black Tree | Fewer rotations, more flexible | O(log n) all ops | O(n) |
| Randomized balanced | Skip List | Simpler than tree balancing, O(log n) | O(log n) expected | O(n) |
| Randomized BST | Treap | Combines BST + heap properties | O(log n) expected | O(n) |
| String indexing | Suffix Tree | Preprocess string for fast queries | O(n) build, O(m+k) query | O(n) |
| Multiple pattern search | Aho-Corasick | Find all patterns in text simultaneously | O(n+m+z) | O(m) |
| Range queries (count/sum) | Fenwick Tree / BIT | Simpler than segment tree | O(log n) per op | O(n) |
| Heavy-light decomposition | Graph Trees | LCA, tree path queries | O(log^2 n) query | O(n log n) |
| Set membership, static | Sorted Array + Binary Search | Efficient if not updating | O(log n) search | O(n) |

---

## Common Interview Scenarios

### Scenario 1: "I need fast lookup and insertion"
**Example:** Design a cache with O(1) access and insertion.

**Decision Tree:**
- Need sorted order? No → Use **HashMap**
  - Time: O(1) average case
  - Space: O(n)
  - Catch: No ordering, worst case O(n)
- Need sorted order? Yes → Use **TreeMap / BST**
  - Time: O(log n) per operation
  - Space: O(n)
  - Better: RedBlack Tree (fewer rotations)

**Real Interview:** "Design an LRU Cache" → HashMap + Doubly Linked List

---

### Scenario 2: "I need to find the k-th largest element in a stream"
**Example:** Real-time analytics receiving continuous data.

**Decision Tree:**
- Storing all elements? Too much memory. Use **Min Heap of size k**
  - Maintain min-heap with k largest elements
  - Insert: O(log k)
  - Space: O(k) instead of O(n)
  - Answer at heap top: O(1)

**Real Interview:** "Kth Largest Element in Stream" (LeetCode 703)

---

### Scenario 3: "I need autocomplete functionality"
**Example:** Search engine suggestions as user types.

**Decision Tree:**
- Fast prefix matching → **Trie**
  - Insert word: O(m) where m = word length
  - Search all words with prefix: O(p + n) where p = prefix length, n = results
  - Memory: O(alphabet size × total characters)
  - Order: Lexicographic by default

**Real Interview:** "Implement Autocomplete System" (LeetCode 642)

---

### Scenario 4: "I need range minimum query on a static array"
**Example:** Precomputed queries on immutable data.

**Decision Tree:**
- One-time preprocessing OK? Yes → **Sparse Table**
  - Preprocess: O(n log n)
  - Query: O(1)
  - Space: O(n log n)
  - Best when queries >> updates

**Real Interview:** "Range Sum Query - Immutable" or "Sparse Matrix"

---

### Scenario 5: "I need range queries with point updates"
**Example:** Interval sum queries where values change.

**Decision Tree:**
- Many queries + many updates → **Segment Tree**
  - Insert: O(log n)
  - Range query: O(log n)
  - Space: O(n)
  - Or use **Fenwick Tree** (simpler, better cache)

**Real Interview:** "Range Sum Query - Mutable" (LeetCode 307)

---

### Scenario 6: "I need to check if element exists very quickly (probably)"
**Example:** Web crawler checking millions of seen URLs.

**Decision Tree:**
- False positives acceptable? Yes → **Bloom Filter**
  - Insert: O(k) where k = number of hash functions
  - Lookup: O(k), constant time
  - Space: O(m bits) << O(n) for storing elements
  - No deletions possible

**Real Interview:** "Design a System - URL Deduplication"

---

### Scenario 7: "I need sorted order with frequent updates"
**Example:** Leaderboard with players joining/leaving.

**Decision Tree:**
- Need self-balancing? Yes → **AVL Tree or Red-Black Tree**
  - Insert/Delete/Search: O(log n)
  - Maintains balance → guaranteed O(log n)
  - AVL: stricter balance, more rotations
  - RB-Tree: flexible balance, fewer rotations
  - Alternative: **Skip List** (simpler, probabilistic)

**Real Interview:** "Design a Leaderboard" or "Frequency Tracker"

---

### Scenario 8: "I need to track connected components"
**Example:** Social network - count friend groups.

**Decision Tree:**
- Queries about component membership? → **Union Find**
  - Union: O(α(n)) amortized (nearly O(1))
  - Find: O(α(n)) amortized
  - Path compression + union by rank
  - No easy "which component" traversal

**Real Interview:** "Number of Connected Components in Undirected Graph" (LeetCode 323)

---

### Scenario 9: "I need to find the shortest path in a graph"
**Example:** GPS navigation, network routing.

**Decision Tree:**
- Unweighted edges? → **BFS**
  - Time: O(V + E)
  - Space: O(V)
  - Finds shortest path in unweighted graph
- Weighted edges, no negatives? → **Dijkstra's Algorithm**
  - Time: O((V + E) log V) with min-heap
  - Space: O(V)
  - Greedy approach with priority queue
- Negative weights? → **Bellman-Ford**
  - Time: O(V × E)
  - Space: O(V)
  - Detects negative cycles

**Real Interview:** "Network Delay Time" (LeetCode 743)

---

### Scenario 10: "I need to find all occurrences of a pattern in text"
**Example:** Text editor find-all feature.

**Decision Tree:**
- Single pattern? → **KMP Algorithm**
  - Time: O(n + m) where n = text length, m = pattern length
  - Space: O(m) for failure function
  - No preprocessing needed
- Multiple patterns? → **Aho-Corasick**
  - Build trie of patterns, run automaton on text
  - Time: O(n + m + z) where z = number of matches
  - Space: O(m × alphabet)
  - Alternative: Rabin-Karp for multiple patterns

**Real Interview:** "Implement strStr()" (LeetCode 28)

---

### Scenario 11: "I need to detect a cycle in a graph"
**Example:** Deadlock detection, circular dependency checker.

**Decision Tree:**
- Directed graph? → **DFS + recursion stack**
  - Time: O(V + E)
  - Space: O(V) recursion
  - Or use **Union Find** for undirected
- Undirected graph? → **DFS or Union Find**
  - DFS: Track parent, if revisit non-parent = cycle
  - Union Find: If both vertices in same set = cycle
  - Time: O(V + E)

**Real Interview:** "Course Schedule" (LeetCode 207)

---

### Scenario 12: "I need to maintain sorted order with median access"
**Example:** Real-time statistics, stock price analysis.

**Decision Tree:**
- Need fast median? → **Two Heaps (Min + Max)**
  - Min heap for larger half, max heap for smaller half
  - Insert: O(log n)
  - Find median: O(1)
  - Space: O(n)

**Real Interview:** "Find Median from Data Stream" (LeetCode 295)

---

### Scenario 13: "I need fast membership checking for many items"
**Example:** Database index, duplicate detection.

**Decision Tree:**
- False positives OK? → **Bloom Filter**
  - O(k) operations, very space-efficient
- Exact matching required? → **HashMap or Hash Set**
  - O(1) average case lookup
  - O(n) space
- Need sorted iteration? → **TreeSet / TreeMap**
  - O(log n) insert/lookup
  - O(n) space

**Real Interview:** "Two Sum", "Duplicate Detection"

---

### Scenario 14: "I need to find LCA (Lowest Common Ancestor) in a tree"
**Example:** File system hierarchy, organizational charts.

**Decision Tree:**
- Single queries on static tree? → **LCA with DFS**
  - Preprocess: O(n log n) with binary lifting
  - Query: O(log n)
- Many queries? → **Binary Lifting or Heavy-Light Decomposition**
  - Preprocess: O(n log n)
  - Query: O(log n) or O(log^2 n)

**Real Interview:** "Lowest Common Ancestor of a Binary Search Tree" (LeetCode 235)

---

### Scenario 15: "I need to solve a range update + range query problem"
**Example:** Classroom scheduling, interval merging.

**Decision Tree:**
- Only point updates? → **Segment Tree**
  - Insert: O(log n)
  - Range query: O(log n)
- Range updates needed? → **Lazy Segment Tree**
  - Range update: O(log n)
  - Range query: O(log n)
  - Defers updates for efficiency
  - Code complexity: High

**Real Interview:** "Range Addition" (LeetCode 370)

---

## Decision Quick Reference by Use Case

### Priority-Based Access
- **Min/Max Element**: Heap
- **K-Largest**: Min Heap with size k
- **K-Smallest**: Max Heap with size k

### Ordered Access
- **Sorted Insertion/Deletion**: AVL/RB Tree, Skip List
- **Sorted Static Data**: Sorted Array + Binary Search
- **Lexicographic Order**: Trie

### Search Optimization
- **Prefix Search**: Trie
- **Pattern Matching**: KMP, Rabin-Karp
- **Substring**: Suffix Tree, KMP

### Space-Time Tradeoff
- **Speed Critical**: Bloom Filter (space efficient)
- **Memory Critical**: Sparse Table (query efficient)
- **Balanced**: Segment Tree, HashMap

### Graph Operations
- **Connectivity**: Union Find, BFS/DFS
- **Shortest Path**: Dijkstra (weighted), BFS (unweighted)
- **Cycle Detection**: DFS, Union Find
- **Topological Sort**: DFS, Kahn's algorithm

### Caching
- **LRU**: HashMap + Doubly Linked List
- **LFU**: HashMap + Frequency List
- **TTL Cache**: HashMap + Min Heap

---

## Tips for Interview Success

1. **Name the structure first**: "I'll use a HashMap here" sounds more professional than "I'll use a fast lookup structure"

2. **Justify your choice**: Always explain the time/space tradeoff

3. **Consider alternatives**: Mention why you chose X over Y

4. **Handle edge cases**: Empty input, single element, duplicates

5. **Optimize iteratively**: Start simple, then optimize if time permits

6. **Code template**: Have quick implementations ready for:
   - HashMap operations
   - Heap operations (min/max)
   - BST traversals
   - Graph BFS/DFS
   - Trie insert/search

7. **Precomputed Tables**: Many problems benefit from preprocessing (Sparse Table, Trie)

