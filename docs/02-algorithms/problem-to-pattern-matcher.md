# Problem-to-Pattern Matcher: Master Index

Quick reference table mapping 50+ problem types to data structures, algorithms, and examples.

| Problem Type | Best-Fit DS | Key Algorithms | Example | Category Link |
|---|---|---|---|---|
| **Sliding Window** | Deque, HashMap | Two-pointer window | Longest substring without repeating chars | [Array & String](array-and-string-problems.md) |
| **Prefix Sum** | Array | Cumulative sum, prefix table | Range sum query, subarray sum equals k | [Array & String](array-and-string-problems.md) |
| **Two Pointers** | Array | Pointer convergence | Two sum sorted, container with most water | [Array & String](array-and-string-problems.md) |
| **Binary Search** | Array | Divide and conquer | Search in rotated array, find first/last | [Array & String](array-and-string-problems.md) |
| **Array Rotation** | Array | Index manipulation | Rotate array by k, find min in rotated | [Array & String](array-and-string-problems.md) |
| **String Matching** | Trie, HashMap | KMP, rolling hash | Longest prefix suffix, pattern matching | [Array & String](array-and-string-problems.md) |
| **Fast/Slow Pointers** | Linked List | Tortoise & hare | Cycle detection, find middle, find kth | [Linked List](linked-list-problems.md) |
| **Cycle Detection** | Linked List, Set | Floyd's algorithm | Linked list cycle, starting node of cycle | [Linked List](linked-list-problems.md) |
| **List Merging** | Linked List | Merge sort, merge pointers | Merge k lists, merge sorted lists | [Linked List](linked-list-problems.md) |
| **List Reversal** | Linked List | Iterative/recursive | Reverse list, reverse k-group | [Linked List](linked-list-problems.md) |
| **Reordering** | Linked List | Slow pointer, recursion | Reorder list, palindrome list | [Linked List](linked-list-problems.md) |
| **Monotonic Stack** | Stack | Stack with comparison | Next greater element, largest rectangle | [Stack & Queue](stack-and-queue-problems.md) |
| **Parentheses Matching** | Stack | Bracket matching | Valid parentheses, longest valid substring | [Stack & Queue](stack-and-queue-problems.md) |
| **BFS via Queue** | Queue | Level order, shortest path | Binary tree level order, word ladder | [Stack & Queue](stack-and-queue-problems.md) |
| **DFS via Stack** | Stack | Post-order traversal | Evaluate expression, largest rectangle | [Stack & Queue](stack-and-queue-problems.md) |
| **Calcs/Updates** | Stack, Deque | Monotonic deque | Sliding window max, max in subarray | [Stack & Queue](stack-and-queue-problems.md) |
| **BST Search/Insert** | BST | In-order traversal | Kth smallest, validate BST | [Tree](tree-problems.md) |
| **Tree Traversal** | Tree | DFS/BFS, all orders | Inorder, preorder, postorder, level-order | [Tree](tree-problems.md) |
| **LCA (Lowest Common Ancestor)** | BST/Tree | Recursive LCA, path tracking | LCA in BST, LCA in binary tree | [Tree](tree-problems.md) |
| **Subtree Problems** | Tree | DFS recursion | Subtree of another tree, max path sum | [Tree](tree-problems.md) |
| **Tree Serialization** | Tree | Pre-order encoding | Serialize/deserialize binary tree | [Tree](tree-problems.md) |
| **Tree Diameter** | Tree | DFS, track depth | Tree diameter, longest path | [Tree](tree-problems.md) |
| **DFS/BFS** | Graph, Queue/Stack | Traversal | Clone graph, number of islands | [Graph](graph-problems.md) |
| **Shortest Path (Unweighted)** | Graph, Queue | BFS | Shortest path in grid, word ladder | [Graph](graph-problems.md) |
| **Shortest Path (Weighted)** | Graph, PriorityQueue | Dijkstra | Shortest path, network delay time | [Graph](graph-problems.md) |
| **MST (Minimum Spanning Tree)** | Graph, Union-Find | Kruskal/Prim | Connect cities, min cost to connect | [Graph](graph-problems.md) |
| **Topological Sort** | Graph, Queue | Kahn's algorithm, DFS | Course schedule, task ordering | [Graph](graph-problems.md) |
| **Union-Find** | DSU | Path compression, union by rank | Connected components, parent finding | [Graph](graph-problems.md) |
| **0/1 Knapsack** | DP | Bottom-up table | Partition equal subset, target sum | [Dynamic Programming](dynamic-programming-problems.md) |
| **Unbounded Knapsack** | DP | Coin change variant | Coin combinations, change making | [Dynamic Programming](dynamic-programming-problems.md) |
| **LIS (Longest Increasing Subsequence)** | DP, BIT | DP + binary search | LIS, LDS, maximum subarray | [Dynamic Programming](dynamic-programming-problems.md) |
| **LCS (Longest Common Subsequence)** | DP | 2D table | Edit distance, longest common subseq | [Dynamic Programming](dynamic-programming-problems.md) |
| **Matrix Chain Multiplication** | DP | Bottom-up table | Burst balloons, palindrome partitioning | [Dynamic Programming](dynamic-programming-problems.md) |
| **Palindrome DP** | DP | 2D expand-around | Palindrome partitioning, longest palindrome | [Dynamic Programming](dynamic-programming-problems.md) |
| **Activity Selection** | Greedy | Sort by end time | Max non-overlapping intervals | [Greedy](greedy-problems.md) |
| **Huffman Coding** | Greedy, Heap | Frequency-based | Data compression, optimal prefix codes | [Greedy](greedy-problems.md) |
| **Interval Scheduling** | Greedy | Sort and merge | Merge intervals, max meetings | [Greedy](greedy-problems.md) |
| **XOR Tricks** | Bit | XOR properties | Single number, find difference | [Bit Manipulation](bit-manipulation-problems.md) |
| **Bitmask DP** | Bit, DP | State compression | Traveling salesman, assignment problem | [Bit Manipulation](bit-manipulation-problems.md) |
| **Subset Generation** | Bit | Bit enumeration | All subsets, power set | [Bit Manipulation](bit-manipulation-problems.md) |
| **LRU Cache** | HashMap, LinkedList | Eviction policy | LRU design, frequency-based cache | [Design](design-problems.md) |
| **LFU Cache** | HashMap, Heap | Frequency tracking | LFU design, access frequency | [Design](design-problems.md) |
| **Trie-Based** | Trie | Prefix tree | Autocomplete, word search, spell check | [Design](design-problems.md) |
| **Custom Data Structure** | Multiple | Composition | Time-based key-value, random pick | [Design](design-problems.md) |
| **GCD/LCM** | Math | Euclidean algorithm | Greatest common divisor, least common multiple | [Math & Geometry](math-and-geometry-problems.md) |
| **Prime Numbers** | Math | Sieve of Eratosthenes | Prime checking, count primes | [Math & Geometry](math-and-geometry-problems.md) |
| **Modular Arithmetic** | Math | Modulo operations | Modular exponentiation, fermat's little theorem | [Math & Geometry](math-and-geometry-problems.md) |
| **Coordinate Geometry** | Math | Distance, area formulas | Point in polygon, line intersection | [Math & Geometry](math-and-geometry-problems.md) |
| **Segment Tree** | SegmentTree | Range query/update | Range sum/min, lazy propagation | [Advanced Patterns](advanced-patterns.md) |
| **Fenwick Tree (BIT)** | BIT | Prefix sum optimization | 2D range sum, inversion count | [Advanced Patterns](advanced-patterns.md) |
| **Heavy-Light Decomposition** | Tree | Path decomposition | Tree path queries and updates | [Advanced Patterns](advanced-patterns.md) |
| **AC Automaton** | Trie | Multiple pattern matching | Dictionary search, multi-pattern match | [Advanced Patterns](advanced-patterns.md) |

See category pages for detailed explanations, time complexities, and code references.
