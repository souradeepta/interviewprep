# Cartesian Tree

## Overview

A **Cartesian Tree** is a binary search tree with an additional min-heap property: for each node, the value is smaller than all values in its subtree. Given an array, a Cartesian tree can be built in O(n) time and enables solving range minimum query (RMQ) problems in O(1) query time after O(n) preprocessing.

Invented by Vuillemin (1980) and used extensively in competitive programming, Cartesian trees are fundamental to many advanced algorithms. They appear in suffix arrays (with LCP arrays), sparse tables, and dynamic programming optimizations.

A Cartesian tree is uniquely defined by any permutation: the array structure determines the tree structure. This one-to-one correspondence enables using Cartesian trees to solve problems that seem unrelated at first.

## When to Use

- **Range minimum queries (RMQ)**: O(1) query after O(n) preprocessing
- **Building LCP (Longest Common Prefix) data structures**: From suffix arrays to fast LCS queries
- **Eliminating nesting in parenthesis matching**: Cartesian tree structure encodes nesting naturally
- **Finding lowest common ancestor (LCA)**: Cartesian tree encodes LCA as the minimum in range
- **Problem transformation**: Convert array problems to tree structure problems

## ASCII Visualization

```
Array: [3, 2, 5, 1, 4, 6]

Cartesian Tree (min-heap property on tree structure):

           1 (min value in entire array)
          / \
        2     4
       /     / \
      3    6   6

Wait, let me redo this correctly with values:

Array: [3, 2, 5, 1, 4, 6]
Index: [0, 1, 2, 3, 4, 5]

Cartesian Tree structure:
                1 (smallest value, at index 3)
              /   \
            2       4
           /       / \
          3       5   6

Node value = array value
Subtree of node covers consecutive indices in the original array
- Root (value 1) covers entire array [0,5]
- Left child (value 2) covers [0,2]
- Left-left (value 3) covers [0,0]
- Right child (value 4) covers [4,5]
- Right-left (value 5) covers [2,2]
- Right-right (value 6) covers [5,5]

Property: Every node's value is the minimum in its subtree's index range.
         The minimum of any subarray [l, r] is the value at the LCA of indices l and r.
```

### RMQ via Cartesian Tree

```
Query RMQ(2, 4) on array [3, 2, 5, 1, 4, 6]:

Cartesian tree encodes: minimum in range [2,4] is at node covering [2,4]
Traverse from node at index 2 to node at index 4 via their LCA
LCA of indices 2,4 is the node covering [2,4], which is the node with value 4
Answer: min(5, 1, 4) = 1
```

## Operations & Complexity

| Operation          | Time Complexity | Space Complexity | Notes |
|-------------------|:---------------:|:----------------:|-------|
| Build Cartesian Tree | O(n)          | O(n)             | Single-pass stack-based |
| RMQ query          | O(1)            | O(1)             | After O(n) preprocessing with LCA |
| LCA (with preprocessing) | O(1)      | O(1)             | Binary lifting or sparse table |
| RMQ (no preprocessing) | O(log n)  | O(1)             | Query by tree traversal |
| Space             | —               | O(n)             | Tree with n nodes |

> O(n) build + O(n) LCA preprocessing = O(n) total for O(1) RMQ queries. Simpler than segment trees for RMQ when memory is available for preprocessing.

## Key Invariants

1. **Min-heap property**: Every node's value is ≤ all values in its subtree.
2. **BST on indices**: If we label each node by its original array index, the in-order traversal gives the original array order.
3. **Subtree index ranges**: The subtree rooted at a node covers a contiguous range of indices [l, r].
4. **Unique structure**: For any permutation of values, there is exactly one Cartesian tree.
5. **Depth bound**: The tree can be as deep as O(n) in the worst case (e.g., sorted array), but average case is O(log n).

## Solution Approach Flowchart

```mermaid
flowchart TD
    A["Problem: Range queries or structure"] -->|Query type?| B{RMQ or LCA?}
    B -->|RMQ (range minimum)| C["Build Cartesian Tree<br/>O(n) stack-based"]
    B -->|Tree structure analysis| D["Cartesian tree encodes<br/>nesting/ordering"]
    C --> E["Preprocess LCA<br/>Binary lifting or sparse table<br/>O(n log n) or O(n)"]
    E --> F["Answer O(1) RMQ queries<br/>LCA on tree"]
    D --> G["Identify tree relationships<br/>in original array"]
    G --> H["Parent-child = nesting<br/>Ancestor = range property"]
    H --> I["Solve using tree DP"]
    F --> J["Time: O(n + q)<br/>for n queries"]
    I --> J
```

## Common Patterns

1. **RMQ with O(1) Query**: Build Cartesian tree from array in O(n). Preprocess LCA with binary lifting in O(n log n). For each RMQ(l, r): find LCA of nodes at indices l and r; their LCA is the minimum. Time: O(n log n) prep, O(1) per query.

2. **Nesting Structure Recognition**: Use Cartesian tree to identify nested structures in an array. The tree structure naturally encodes hierarchy: parent-child relationships are containment relationships in the original array.

3. **Dynamic Programming with Cartesian Tree**: For problems involving subarrays and minimum/maximum values, use Cartesian tree to decompose into subproblems. Process the tree bottom-up, combining results from subtrees.

4. **Parenthesis Matching**: Map parenthesis matching problems to Cartesian tree depth. Match closing parenthesis with opening: find the "minimum cost" path on the tree.

## Interview Questions

1. **Why is a Cartesian tree's structure unique for a given array?** The root must be the minimum element (min-heap property). Removing the root partitions the array into left and right subarrays. Recursively, the structure of each subarray's Cartesian tree is unique. Hence the overall tree is unique.

2. **How do you build a Cartesian tree in O(n) time?** Use a stack. Process elements left to right. For each new element: pop all elements larger than it (they become its left subtree). The popped element becomes the parent, and the new element becomes the right child of the last popped. This ensures in-order = original order.

3. **Can you use Cartesian tree for range maximum queries (RMQ)?** Yes, modify the min-heap property to max-heap. The tree structure changes, but the LCA approach for RMQ remains the same.

4. **What's the difference between Cartesian tree and segment tree for RMQ?** Cartesian tree: O(n) build + O(n log n) LCA preprocessing = O(n log n) total, O(1) per query. Segment tree: O(n) build, O(log n) per query, no preprocessing beyond build. Cartesian tree is better for many queries; segment tree is better if updates are frequent.

5. **How is a Cartesian tree related to suffix arrays and LCP arrays?** The Cartesian tree on an LCP array encodes the structure of LCP values. The tree's structure reveals which suffixes share long common prefixes, useful for advanced string algorithms.

6. **Can the depth of a Cartesian tree be O(n)?** Yes. For a sorted array [1, 2, 3, ..., n], the Cartesian tree is a right-skewed line (or left-skewed, depending on tie-breaking). Each element is either the min (root) or greater than its parent, forcing depth O(n).

7. **How would you parallelize Cartesian tree construction?** Difficult; O(n) stack-based construction is inherently sequential. However, you can use deterministic skip lists or other techniques for parallel tree building, though they have higher constants.

## Implementation Notes

- **Stack-Based Construction**: Use a stack to process elements. Key insight: when popping, the popped element becomes the left child of the current element. The new top of stack becomes the parent. Order matters!
- **Handling Ties**: If there are duplicate values, the Cartesian tree structure can vary. Decide: do duplicates go left or right? Be consistent. Use indices as tie-breakers.
- **LCA Preprocessing**: Once you have the tree, use binary lifting (with parent and ancestor arrays) for O(1) LCA after O(n log n) preprocessing. Alternative: sparse table on the DFS Euler tour.
- **Tree Traversal**: Ensure in-order traversal matches the original array indices. If not, reconstruction is wrong.
- **Edge Cases**: Empty array, single element, all identical values, sorted arrays (worst case depth).

## References

1. Vuillemin, J. (1980). "A unifying look at data structures." *Communications of the ACM*, 23(4), 229-239.
2. Gusfield, D. (1997). *Algorithms on Strings, Trees, and Sequences*. Cambridge University Press.
3. Competitive Programming community (Codeforces blogs, TopCoder editorials).
