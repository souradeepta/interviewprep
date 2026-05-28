# Trees — Hierarchical Structure, DFS/BFS Traversals

**Level:** L3-L4
**Time to read:** ~25 min

The backbone of recursive thinking. Master traversals here and the rest of tree problems follow naturally.

---

## Quick Summary

A tree is a connected acyclic graph with one root node. Every node has exactly one parent (except root) and zero or more children. Use when data has hierarchical relationships or when you need efficient divide-and-conquer (each subtree is independent). Key property: n nodes → n-1 edges, depth determines recursion depth.

---

## Operations & Complexity Table

| Operation            | Binary Tree  | Notes                                        |
|----------------------|-------------|----------------------------------------------|
| Access (by value)    | O(n)        | Must traverse; no ordering guarantee         |
| DFS traversal        | O(n)        | Visit every node once                        |
| BFS traversal        | O(n)        | Level-by-level; needs O(w) queue (w=width)   |
| Insert (general)     | O(n)        | Find position first; no ordering rule        |
| Height               | O(n)        | Recursively max(left, right) + 1             |
| Diameter             | O(n)        | Max path through any node                   |
| Space (recursion)    | O(h)        | h = height; O(log n) balanced, O(n) skewed  |

---

## Memory Layout / Internal Structure

```
Tree Node (Python)
─────────────────────────────────────
class TreeNode:
    val:   int          # payload (4 bytes)
    left:  TreeNode     # pointer to left child (8 bytes)
    right: TreeNode     # pointer to right child (8 bytes)

Binary Tree Shape (balanced vs skewed):

Balanced (height = log n):          Skewed (height = n, worst case):
         1                                  1
        / \                                  \
       2   3                                  2
      / \ / \                                  \
     4  5 6  7                                  3
                                                 \
     Height = 2 (~log₂ 7)                         4

DFS Stack behavior on balanced tree:
                     1
                    / \
Call stack          2   3
at deepest         / \
node 4:           4   5

Frame stack (top→bottom): visit(4), visit(2), visit(1)
Max stack depth = height h
```

---

## Trade-offs vs Alternatives

| Feature               | Binary Tree   | Array (sorted) | Linked List   | BST            |
|-----------------------|---------------|----------------|---------------|----------------|
| Hierarchical data     | Natural fit   | Forced flat    | Forced flat   | Natural fit    |
| Random access         | O(n)          | O(1)           | O(n)          | O(log n) avg   |
| Insert (ordered)      | O(n)          | O(n) shift     | O(1) w/ ptr   | O(log n) avg   |
| Ordered traversal     | O(n) in-order | O(n) scan      | O(n) scan     | O(n) in-order  |
| Memory                | High (ptrs)   | Low            | Medium        | High (ptrs)    |
| Level-order access    | O(n) BFS      | Direct         | O(n)          | O(n) BFS       |

```
When to choose tree:
┌──────────────────────────────────────────────────────────────────┐
│ Hierarchical data (org chart, file system)?  → Tree              │
│ Need ordered operations + dynamic inserts?   → BST              │
│ Range queries, prefix sums?                  → Segment/Fenwick  │
│ Prefix/autocomplete?                         → Trie             │
│ Simple ordered array, no inserts?            → Sorted Array     │
└──────────────────────────────────────────────────────────────────┘
```

---

## When NOT to Use

- **Flat, non-hierarchical data** — arrays or hash maps are simpler and faster.
- **Frequent random access by index** — trees require traversal; use arrays.
- **Highly skewed input without balancing** — degenerates to O(n) linked list; use self-balancing BST.
- **Cache-sensitive tight loops** — pointer-chasing in trees destroys cache locality; arrays win.
- **Simple key-value lookups** — hash map gives O(1) with less code.

---

## Core Operations (Code)

```python
from collections import deque
from typing import Optional

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

# ── DFS Traversals ────────────────────────────────────────────────────────────

def inorder(root: Optional[TreeNode]) -> list[int]:
    # Left → Root → Right  (gives sorted output for BST)
    if not root:
        return []
    return inorder(root.left) + [root.val] + inorder(root.right)

def preorder(root: Optional[TreeNode]) -> list[int]:
    # Root → Left → Right  (good for serialization/copying)
    if not root:
        return []
    return [root.val] + preorder(root.left) + preorder(root.right)

def postorder(root: Optional[TreeNode]) -> list[int]:
    # Left → Right → Root  (good for deletion, evaluating expressions)
    if not root:
        return []
    return postorder(root.left) + postorder(root.right) + [root.val]

# Iterative inorder (avoids recursion stack overflow on deep trees)
def inorder_iterative(root: Optional[TreeNode]) -> list[int]:
    result, stack = [], []
    curr = root
    while curr or stack:
        while curr:          # go as far left as possible
            stack.append(curr)
            curr = curr.left
        curr = stack.pop()   # process node
        result.append(curr.val)
        curr = curr.right    # move to right subtree
    return result

# ── BFS (Level-Order) ────────────────────────────────────────────────────────

def level_order(root: Optional[TreeNode]) -> list[list[int]]:
    if not root:
        return []
    result, queue = [], deque([root])
    while queue:
        level = []
        for _ in range(len(queue)):      # drain exactly one level
            node = queue.popleft()
            level.append(node.val)
            if node.left:  queue.append(node.left)
            if node.right: queue.append(node.right)
        result.append(level)
    return result

# ── Height & Diameter ────────────────────────────────────────────────────────

def height(root: Optional[TreeNode]) -> int:
    if not root:
        return 0
    return 1 + max(height(root.left), height(root.right))

def diameter_of_binary_tree(root: Optional[TreeNode]) -> int:
    # Diameter = longest path between any two nodes (may not pass through root)
    best = [0]

    def depth(node):
        if not node:
            return 0
        left  = depth(node.left)
        right = depth(node.right)
        best[0] = max(best[0], left + right)   # update global max at each node
        return 1 + max(left, right)

    depth(root)
    return best[0]
```

---

## 3 Worked Problems

---

### Problem 1 — Maximum Depth of Binary Tree (LeetCode #104)

**Clarifying Questions**
- Is an empty tree depth 0 or undefined? (Return 0 for null root)
- Is depth the number of nodes or edges? (Nodes — LeetCode convention)
- Any constraint on tree shape (balanced, complete)? (No — general binary tree)

**Brute Force**

Recursively compute depth: depth(node) = 1 + max(depth(left), depth(right)).

```python
def max_depth_recursive(root: Optional[TreeNode]) -> int:
    if not root:
        return 0
    return 1 + max(max_depth_recursive(root.left),
                   max_depth_recursive(root.right))
```

**Optimization**

The recursive solution is already optimal (O(n) time, O(h) space). Iterative BFS uses O(w) space where w is max width — often worse for balanced trees. Iterative DFS uses a stack and avoids Python's recursion limit.

```python
def max_depth(root: Optional[TreeNode]) -> int:
    # Iterative DFS with explicit stack — avoids recursion limit
    if not root:
        return 0
    stack = [(root, 1)]
    max_d = 0
    while stack:
        node, depth = stack.pop()
        max_d = max(max_d, depth)
        if node.left:  stack.append((node.left,  depth + 1))
        if node.right: stack.append((node.right, depth + 1))
    return max_d
```

**Edge Cases**
- `root = None` → return 0
- Single node → return 1
- Completely skewed tree (linked list shape) → O(n) recursion depth; iterative preferred

**Complexity**
- Time: O(n) — visit every node once
- Space: O(h) recursive (O(log n) balanced, O(n) skewed); O(w) BFS

**Follow-ups**
- "Minimum depth?" → BFS stops at first leaf; recursion needs both children check.
- "Balanced tree check?" → Compare left and right heights; if diff > 1, unbalanced.
- "Path with max sum?" → LeetCode #124, similar DFS pattern with global max.

---

### Problem 2 — Invert Binary Tree (LeetCode #226)

**Clarifying Questions**
- In-place or return new tree? (Return root of modified tree)
- Does inverting mean mirror image? (Yes — swap left/right at every node)
- Should I handle null? (Return null if root is null)

**Brute Force**

Post-order: invert children first, then swap.

```python
def invert_tree_brute(root: Optional[TreeNode]) -> Optional[TreeNode]:
    if not root:
        return None
    # First invert subtrees
    left  = invert_tree_brute(root.left)
    right = invert_tree_brute(root.right)
    # Then swap
    root.left  = right
    root.right = left
    return root
```

**Optimization**

Pre-order is equally valid and slightly more intuitive: swap first, recurse after. Both are O(n).

```python
def invert_tree(root: Optional[TreeNode]) -> Optional[TreeNode]:
    if not root:
        return None
    root.left, root.right = root.right, root.left   # swap
    invert_tree(root.left)
    invert_tree(root.right)
    return root

# Iterative BFS version (useful for very deep trees)
def invert_tree_bfs(root: Optional[TreeNode]) -> Optional[TreeNode]:
    if not root:
        return root
    queue = deque([root])
    while queue:
        node = queue.popleft()
        node.left, node.right = node.right, node.left
        if node.left:  queue.append(node.left)
        if node.right: queue.append(node.right)
    return root
```

**Edge Cases**
- Null root → return None
- Single node → return as-is (no children to swap)
- Only left children → after invert, only right children

**Complexity**
- Time: O(n) — every node visited once
- Space: O(h) recursion; O(w) BFS

**Follow-ups**
- "Symmetric tree check?" → LeetCode #101; compare mirrored subtrees instead of swapping.
- "Same tree check?" → LeetCode #100; recursive comparison.

---

### Problem 3 — Binary Tree Level Order Traversal (LeetCode #102)

**Clarifying Questions**
- Return list of lists or flat list? (List of lists — one per level)
- Left to right within each level? (Yes)
- Empty tree returns `[]`? (Yes)

**Brute Force**

DFS with depth tracking: pass depth as parameter, append to `result[depth]`.

```python
def level_order_dfs(root: Optional[TreeNode]) -> list[list[int]]:
    result = []

    def dfs(node, depth):
        if not node:
            return
        if depth == len(result):
            result.append([])
        result[depth].append(node.val)
        dfs(node.left,  depth + 1)
        dfs(node.right, depth + 1)

    dfs(root, 0)
    return result
```

**Optimization**

BFS with level-size snapshot: record `len(queue)` before processing a level to know when one level ends and next begins.

```python
def level_order(root: Optional[TreeNode]) -> list[list[int]]:
    if not root:
        return []
    result = []
    queue  = deque([root])
    while queue:
        level_size = len(queue)          # snapshot: all nodes at current level
        level = []
        for _ in range(level_size):
            node = queue.popleft()
            level.append(node.val)
            if node.left:  queue.append(node.left)
            if node.right: queue.append(node.right)
        result.append(level)
    return result
```

**Edge Cases**
- Empty tree → `[]`
- Single node → `[[val]]`
- Complete binary tree → last level has n/2 nodes; queue max size = n/2

**Complexity**
- Time: O(n)
- Space: O(w) where w = max width (at most n/2 nodes in queue for complete tree)

**Follow-ups**
- "Zigzag level order?" → LeetCode #103; alternate append direction per level.
- "Right side view?" → LeetCode #199; take last element of each level.
- "Average of levels?" → Sum each level / level_size.

---

## Interview Q&A

**Q1: What are the three DFS traversal orders and when do you use each?**

A: Inorder (Left→Root→Right) gives sorted output for BSTs — use for sorted iteration. Preorder (Root→Left→Right) processes root before children — use for tree serialization or copying. Postorder (Left→Right→Root) processes children before root — use for deletion or evaluating expression trees where you need child results before parent.

---

**Q2: When do you use BFS vs DFS on a tree?**

A:
```
BFS: Use when answer lives near the root / in the shallowest level.
     - Shortest path (unweighted)
     - Level-order output
     - Minimum depth
     - "Find closest X"
     Space: O(w) — width can be n/2 for complete tree

DFS: Use when you must explore full paths or depth matters.
     - Path sum problems
     - Tree height/diameter
     - Serialize/deserialize
     - Any problem with "root-to-leaf path"
     Space: O(h) — height, O(log n) balanced, O(n) skewed

Rule of thumb: BFS for "nearest", DFS for "deepest/all-paths"
```

---

**Q3: How do you implement iterative inorder traversal?**

A: Use an explicit stack. Push left children until null, pop and process, then move to right child. The invariant is: stack holds the "path" of nodes we've visited but not yet processed.

```python
def inorder_iterative(root):
    stack, result, curr = [], [], root
    while curr or stack:
        while curr:
            stack.append(curr)
            curr = curr.left
        curr = stack.pop()
        result.append(curr.val)
        curr = curr.right
    return result
```

---

**Q4: What is the difference between a binary tree and a binary search tree?**

A: A binary tree has at most two children per node with no ordering constraint. A BST adds the invariant: all values in the left subtree < node.val < all values in right subtree. This ordering enables O(log n) search on balanced trees. A valid BST remains valid after in-order traversal produces a sorted sequence.

---

**Q5: How do you find the diameter of a binary tree?**

A: Diameter is the longest path between any two nodes. It does not have to pass through the root. At each node, the longest path through that node = left_depth + right_depth. Run DFS, compute depths bottom-up, update a global maximum at each node.

```
Key insight: max diameter through node N = depth(N.left) + depth(N.right)
Track global max across all nodes.
```

---

**Q6: What is the time and space complexity of recursive tree traversal?**

A: Time is always O(n) — every node is visited exactly once regardless of traversal order. Space is O(h) for the call stack where h is height. For a balanced tree h = O(log n). For a skewed tree (like a sorted-insert BST) h = O(n), which can cause stack overflow in Python (default recursion limit ~1000). Iterative traversal uses an explicit stack with the same O(h) space but no overflow risk.

---

**Q7: How does in-order traversal relate to BST validation?**

A: Inorder traversal of a valid BST always produces a strictly increasing sequence. One validation strategy: collect inorder values and check if sorted. More efficient: track the previous value during traversal and check current > previous, stopping early on violation. O(n) time, O(h) space.

---

**Q8: Why might BFS use more space than DFS on a wide tree?**

A: BFS queue holds all nodes at the current level simultaneously. For a complete binary tree, the last level has n/2 nodes, so BFS queue can hold O(n) nodes. DFS stack holds at most O(h) = O(log n) nodes for a balanced tree. For very wide, shallow trees, DFS is significantly more memory efficient.

---

## Interview Tips

- **Draw the tree first.** Before coding, sketch the example on paper. It takes 30 seconds and eliminates most mistakes.
- **State your traversal choice and why.** "I'll use BFS because we want the shortest path" signals pattern recognition.
- **Handle null at the top.** Every recursive tree function should start with `if not root: return <base_case>`.
- **The "post-order trick."** Many hard tree problems need values computed bottom-up. Recognize this pattern: compute left, compute right, combine, return up.
- **Diameter/path sum pattern.** Problems where the answer might not pass through root require a global variable updated at each node while the function returns something different (e.g., height).
- **Iterative vs recursive.** Default to recursive for clarity. Switch to iterative if asked about very deep trees or stack overflow concerns.
