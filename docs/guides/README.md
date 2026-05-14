# Interview Decision Guides

Welcome to the comprehensive interview prep guides. These three documents form a complete system for solving technical interview problems efficiently and correctly.

## Quick Navigation

Use these guides in the following order for maximum effectiveness:

### 1. **Problem-Solving Flowchart** (`problem_solving_flowchart.md`)
**Start here for every interview problem you encounter.**

The complete step-by-step framework for approaching interview problems:
- Clarify & understand the problem
- Identify constraints
- Plan your approach
- Code the solution
- Test thoroughly
- Analyze complexity

Also includes:
- Complexity analysis decision tree
- Common pitfalls and how to avoid them
- Step-by-step walkthrough example
- Interview day tips
- Complete problem-solving checklist

**Read this once to understand the framework, then use as reference checklist during interviews.**

---

### 2. **Data Structure Selection Guide** (`ds_selection_guide.md`)
**Use when deciding what data structure to employ.**

Comprehensive guide to choosing the right data structure:
- Interactive decision flowchart (START → What are you storing? → Recommended DS)
- Quick reference table of 25+ data structures and their use cases
- 15+ common interview scenarios with decision trees:
  - "I need fast lookup and insertion"
  - "I need to find the k-th largest element in a stream"
  - "I need autocomplete functionality"
  - "I need range minimum query on a static array"
  - And 11 more real interview scenarios

- Complexity analysis for each structure
- Quick reference by use case (Priority-based, Ordered, Search, etc.)
- Tips for interview success

**Use during Step 3 (Plan Approach) of problem-solving framework.**

---

### 3. **Algorithm Selection Guide** (`algorithm_selection_guide.md`)
**Use when deciding which algorithm to implement.**

Master guide to choosing the right algorithm:
- Master algorithm decision flowchart (~60+ algorithms)
- Algorithm categories quick reference:
  - Sorting (11 algorithms)
  - Searching (9 algorithms)
  - Dynamic Programming (15 algorithms)
  - Graph (14 algorithms)
  - String (14 algorithms)
  - Mathematical (12 algorithms)
  - Geometry (7 algorithms)
  - Advanced (10 algorithms)

- Problem-to-algorithm mapping with 30+ real interview problems
- Algorithm selection by constraint (time/space limits)
- Tips for algorithm selection in interviews

**Use during Step 3 (Plan Approach) of problem-solving framework.**

---

## How to Use These Guides Effectively

### During Interview Preparation
1. Read **Problem-Solving Flowchart** completely to understand the framework
2. Study **Data Structure Selection Guide** to memorize common patterns
3. Study **Algorithm Selection Guide** to familiarize yourself with algorithm categories
4. Practice 50+ problems using these guides as reference
5. After solving each problem, review relevant sections to reinforce learning

### During Mock Interviews
1. When you receive a problem, use **Problem-Solving Flowchart** as your reference checklist
2. Use **Data Structure Selection Guide** during planning phase
3. Use **Algorithm Selection Guide** to verify algorithm choice
4. Time yourself: 5-7 min understanding, 15-20 min coding, 5-8 min testing, 2-3 min analysis

### During Real Interviews
1. Don't consult guides (obviously!), but internalize the framework
2. Apply the **Problem-Solving Flowchart** mentally:
   - Clarify the problem (ask questions)
   - Identify constraints
   - Plan approach using DS and algorithm knowledge
   - Code step-by-step
   - Test edge cases
   - Analyze complexity
   - Discuss alternatives

3. Remember key patterns from **Data Structure Selection Guide** and **Algorithm Selection Guide**

---

## File Organization

```
/home/sbisw/github/datastructures/docs/guides/
├── README.md                              (this file)
├── problem_solving_flowchart.md          (general framework)
├── ds_selection_guide.md                 (data structure decisions)
└── algorithm_selection_guide.md          (algorithm decisions)
```

---

## Key Concepts Covered

### Data Structures (25+)
Array, Linked List, Stack, Queue, Deque, Hash Map, Hash Set, Binary Search Tree, AVL Tree, Red-Black Tree, Heap (Min/Max), Trie, Graph, Segment Tree, Fenwick Tree, Union Find, LRU Cache, LFU Cache, Bloom Filter, Skip List, Sparse Table, B-Tree, KD-Tree, Suffix Tree, Suffix Array

### Algorithms (~60+)

**Sorting:** Bubble, Insertion, Selection, Merge, Quick, Heap, Counting, Radix, Bucket, Tim Sort, Shell Sort

**Searching:** Linear, Binary, Binary Search variants, Interpolation, Jump, Exponential, Ternary, Hash Table, BST

**Dynamic Programming:** Fibonacci, 0/1 Knapsack, Unbounded Knapsack, Coin Change, LIS, LCS, Edit Distance, Matrix Chain, Subset Sum, Rod Cutting, Climbing Stairs, House Robber, Paint House, Word Break, Distinct Subsequences

**Graph:** BFS, DFS, Dijkstra, Bellman-Ford, Floyd-Warshall, Kruskal, Prim, Topological Sort, SCC, Articulation Points, Bridges, Bipartite Check, Cycle Detection

**String:** Naive Matching, KMP, Boyer-Moore, Rabin-Karp, Aho-Corasick, Suffix Array, Suffix Tree, Trie, LCP, Manacher, Levenshtein, String Hashing, Z-Algorithm

**Math:** Sieve of Eratosthenes, Miller-Rabin, Euclidean, Extended Euclidean, Binary Exponentiation, Factorial, Combinatorics, Fibonacci (matrix), Catalan, Pollard's Rho, CRT, Permutations

**Geometry:** Graham Scan, Andrew's Chain, Jarvis March, Point in Polygon, Line Intersection, Closest Pair, Polygon Area

**Advanced:** Quickselect, Reservoir Sampling, Fisher-Yates, LZ77/LZ78, Huffman, BIT, Segment Tree, HLD, Link-Cut Trees, Ternary Search

---

## Interview Problem Categories

### Data Structure Problems
- LRU/LFU Cache Design
- Two Sum / Hash-based lookups
- Median of Data Stream
- Kth Largest Element
- Top K Elements
- Interval Merging

### Sorting & Searching Problems
- Sort by Property
- Search Variations (rotated, mountain array, etc.)
- Binary Search Optimization
- Multi-key Sorting

### Dynamic Programming Problems
- Knapsack variants
- Longest/Shortest Sequence
- Partition Problems
- Counting Problems
- Path Problems (matrix, tree)
- String/Substring Problems

### Graph Problems
- Shortest Path (BFS, Dijkstra, Bellman-Ford)
- Connected Components (Union Find, DFS)
- Cycle Detection
- Topological Sort
- Spanning Trees
- Strongly Connected Components
- Bipartite Check

### String Problems
- Pattern Matching (KMP, Rabin-Karp)
- Palindrome Problems
- Substring/Subsequence Problems
- Edit Distance
- Word Ladder
- Autocomplete / Trie

### Math Problems
- Prime Testing/Generation
- GCD/LCM
- Modular Arithmetic
- Combinatorics
- Counting/Permutations

---

## Tips for Maximum Benefit

1. **Memorize key patterns**: After each guide, write down top 10 patterns you learned

2. **Create flashcards**: Problem type → DS/Algorithm choice

3. **Practice with guides as reference**: Do 5-10 problems with guides open

4. **Practice without guides**: Do 10-15 problems from memory

5. **Timed practice**: Do 5 problems under time pressure (match interview duration)

6. **Teach others**: Explain a problem and solution to someone else (or rubber duck)

7. **Review mistakes**: After each practice problem, identify what went wrong

8. **Refine your mental framework**: Update your approach based on problems you struggled with

---

## Common Interview Problem Patterns

### Pattern 1: "Fast Access + Order"
- **Data Structure**: TreeMap / BST
- **Example**: "Design a system tracking k largest elements"

### Pattern 2: "Fast Access + Priority"
- **Data Structure**: Heap
- **Example**: "Find median from data stream", "k-th largest"

### Pattern 3: "Prefix Matching"
- **Data Structure**: Trie
- **Example**: "Autocomplete system", "Phone directory"

### Pattern 4: "Range Queries"
- **Data Structure**: Segment Tree / Fenwick Tree
- **Example**: "Range sum query", "Range minimum query"

### Pattern 5: "Membership Testing"
- **Data Structure**: Hash Set / Bloom Filter
- **Example**: "Duplicate detection", "Cache validation"

### Pattern 6: "Shortest Path"
- **Algorithm**: BFS (unweighted) / Dijkstra (weighted)
- **Example**: "Network delay", "Path with minimum cost"

### Pattern 7: "Optimization with Constraints"
- **Algorithm**: Dynamic Programming
- **Example**: "Knapsack", "Coin change", "House robber"

### Pattern 8: "Multiple Patterns in Text"
- **Algorithm**: Aho-Corasick or KMP variants
- **Example**: "Find all occurrences", "Multiple pattern search"

---

## Quick Reference: When to Use What

| When You See | Think | Use |
|---|---|---|
| "Fast lookup" | O(1) access | HashMap |
| "Sorted + updates" | O(log n) access | TreeMap / BST |
| "k-largest" | Heap property | Min Heap |
| "Prefix matching" | Trie property | Trie |
| "Range operations" | Segment decomposition | Segment Tree |
| "Connected components" | Union Find property | Union Find |
| "Shortest path" | Greedy / BFS | Dijkstra / BFS |
| "String matching" | Linear scanning | KMP / Rabin-Karp |
| "Optimal solution" | Overlapping subproblems | Dynamic Programming |
| "All paths" | Graph exploration | DFS / BFS |

---

## Success Checklist

Before submitting your solution in an interview:

- [ ] Problem understood and clarified
- [ ] Input/output formats confirmed
- [ ] Edge cases identified
- [ ] DS choice justified
- [ ] Algorithm choice justified
- [ ] Code is clean and readable
- [ ] All test cases pass
- [ ] Time complexity verified
- [ ] Space complexity verified
- [ ] Alternatives discussed
- [ ] Follow-up questions answered

---

## Additional Resources

All data structures and algorithms mentioned in these guides are implemented in the repository:

- **Python implementations**: `/home/sbisw/github/datastructures/python/`
- **Java implementations**: `/home/sbisw/github/datastructures/java/`
- **Documentation**: Various MD files in each category folder

Use the implementations as reference for:
- Exact code patterns
- Edge case handling
- Performance optimization
- Testing approaches

---

## Final Tips

1. **Master the fundamentals first**: Understand HashMap, Array, Linked List, Tree, Graph, and simple sorting before advanced structures

2. **Know your language**: Practice implementing these structures in your target language (Python, Java, C++, etc.)

3. **Practice consistently**: 2-3 problems per day for 3 months builds strong interview skills

4. **Learn from mistakes**: After each problem, review what went wrong and why

5. **Optimize gradually**: Start with working solution, then optimize if time permits

6. **Communicate clearly**: Explain your approach, justify choices, discuss trade-offs

7. **Stay calm**: Use the framework to stay organized during interviews

---

Good luck with your interview preparation!
