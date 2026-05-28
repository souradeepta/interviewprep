# Binary Search Tree — Ordered Dynamic Data

**Level:** L4
**Time to read:** ~20 min

Sorted array meets dynamic insert/delete. The BST invariant (left < root < right) enables O(log n) search when the tree stays balanced.

---

## Quick Summary

A BST is a binary tree where every node satisfies: all values in the left subtree are less than the node's value, and all values in the right subtree are greater. This invariant enables binary search on a dynamic dataset. Key trade-off: O(log n) average, O(n) worst case when unbalanced. In-order traversal always yields sorted output.

---

## Operations & Complexity Table

| Operation    | Time (avg)  | Time (worst) | Notes                                        |
|--------------|-------------|-------------|----------------------------------------------|
| Search       | O(log n)    | O(n)        | Worst: degenerate (sorted input) → O(n) chain|
| Insert       | O(log n)    | O(n)        | Find correct leaf position                   |
| Delete       | O(log n)    | O(n)        | 3 cases: leaf, one child, two children       |
| Min / Max    | O(log n)    | O(n)        | Leftmost / rightmost node                   |
| In-order     | O(n)        | O(n)        | Always sorted output                         |
| Successor    | O(log n)    | O(n)        | Smallest node greater than k                |
| Space        | O(n)        | O(n)        | One node per element                         |

---

## Memory Layout / Internal Structure

```
BST Node:
┌──────────────────────────────────────────────────────┐
│  val:   int          (4 bytes)                       │
│  left:  *TreeNode    (8 bytes pointer)               │
│  right: *TreeNode    (8 bytes pointer)               │
└──────────────────────────────────────────────────────┘

Valid BST (every left < root < every right):
              8
            /   \
           3     10
          / \      \
         1   6      14
            / \    /
           4   7  13

In-order output: 1, 3, 4, 6, 7, 8, 10, 13, 14  ← always sorted

Degenerate BST (inserting sorted values 1,2,3,4,5):
1
 \
  2
   \
    3
     \
      4
       \
        5
Search for 5 = O(n) — as bad as linked list
```

---

## Trade-offs vs Alternatives

| Feature               | BST (balanced) | Hash Map     | Sorted Array   | Heap           |
|-----------------------|----------------|--------------|----------------|----------------|
| Search                | O(log n)       | O(1) avg     | O(log n)       | O(n)           |
| Insert                | O(log n)       | O(1) avg     | O(n) shift     | O(log n)       |
| Delete                | O(log n)       | O(1) avg     | O(n) shift     | O(log n)       |
| Ordered iteration     | O(n) in-order  | No ordering  | O(n) scan      | No ordering    |
| Range query           | O(log n + k)   | O(n)         | O(log n + k)   | O(n)           |
| Min / Max             | O(log n)       | O(n)         | O(1)           | O(1)           |
| Predecessor/Successor | O(log n)       | O(n)         | O(1) w/ index  | N/A            |
| Memory overhead       | High (ptrs)    | High (hash)  | Low            | Low (array)    |

```
When to choose BST (specifically):
┌─────────────────────────────────────────────────────────────┐
│ Need sorted iteration + insert/delete?   → BST (TreeMap)   │
│ Need range queries (lo..hi)?             → BST              │
│ Need floor/ceiling operations?           → BST              │
│ Just key-value lookup, no ordering?      → Hash Map         │
│ Static sorted data, no inserts?          → Sorted Array     │
│ Just min/max repeatedly?                 → Heap             │
└─────────────────────────────────────────────────────────────┘
```

---

## When NOT to Use

- **Pure lookup with no ordering needs** — hash map gives O(1) vs O(log n) and is simpler.
- **Sorted input without self-balancing** — degenerates to O(n) linked list; use AVL/Red-Black.
- **Memory-constrained systems** — each node has two pointers; sorted array is 3-5x more compact.
- **Top-k or priority-queue operations** — heap has O(1) min/max peek; BST needs O(log n).
- **Concurrent access** — BSTs are hard to make thread-safe; use skip lists or concurrent hash maps.

---

## Core Operations (Code)

```python
from typing import Optional

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

# ── Search ────────────────────────────────────────────────────────────────────

def search_bst(root: Optional[TreeNode], val: int) -> Optional[TreeNode]:
    if not root or root.val == val:
        return root
    if val < root.val:
        return search_bst(root.left, val)
    return search_bst(root.right, val)

# Iterative version (preferred for deep trees)
def search_bst_iter(root: Optional[TreeNode], val: int) -> Optional[TreeNode]:
    while root:
        if val == root.val:   return root
        if val < root.val:    root = root.left
        else:                 root = root.right
    return None

# ── Insert ────────────────────────────────────────────────────────────────────

def insert_bst(root: Optional[TreeNode], val: int) -> TreeNode:
    if not root:
        return TreeNode(val)
    if val < root.val:
        root.left  = insert_bst(root.left, val)
    elif val > root.val:
        root.right = insert_bst(root.right, val)
    # If val == root.val: BST typically ignores duplicates (or handle per spec)
    return root

# ── Delete ────────────────────────────────────────────────────────────────────

def delete_bst(root: Optional[TreeNode], key: int) -> Optional[TreeNode]:
    if not root:
        return None
    if key < root.val:
        root.left  = delete_bst(root.left, key)
    elif key > root.val:
        root.right = delete_bst(root.right, key)
    else:
        # Case 1: leaf node
        if not root.left and not root.right:
            return None
        # Case 2: one child
        if not root.left:  return root.right
        if not root.right: return root.left
        # Case 3: two children — replace with in-order successor (min of right subtree)
        successor = root.right
        while successor.left:
            successor = successor.left
        root.val   = successor.val                        # copy successor value
        root.right = delete_bst(root.right, successor.val)  # delete successor
    return root

# ── Min / Max ─────────────────────────────────────────────────────────────────

def find_min(root: TreeNode) -> int:
    while root.left:
        root = root.left
    return root.val

def find_max(root: TreeNode) -> int:
    while root.right:
        root = root.right
    return root.val

# ── In-order (gives sorted output) ───────────────────────────────────────────

def inorder_sorted(root: Optional[TreeNode]) -> list[int]:
    result = []
    def inorder(node):
        if not node: return
        inorder(node.left)
        result.append(node.val)
        inorder(node.right)
    inorder(root)
    return result
```

---

## 3 Worked Problems

---

### Problem 1 — Validate Binary Search Tree (LeetCode #98)

**Clarifying Questions**
- Can the tree contain duplicate values? (No — strict BST: left < root < right)
- Are node values bounded (INT_MIN, INT_MAX)? (Values fit in 32-bit signed int)
- What does "valid" mean exactly? (Every node satisfies left < node < right including all ancestors)

**Brute Force**

In-order traversal produces sorted output for valid BST. Collect values, check strictly increasing.

```python
def is_valid_bst_brute(root: Optional[TreeNode]) -> bool:
    values = []
    def inorder(node):
        if not node: return
        inorder(node.left)
        values.append(node.val)
        inorder(node.right)
    inorder(root)
    return all(values[i] < values[i+1] for i in range(len(values) - 1))
    # O(n) time, O(n) space — stores all values
```

**Optimization**

Pass valid range [min_val, max_val] down the recursion. Each node must satisfy min_val < node.val < max_val.

```python
def is_valid_bst(root: Optional[TreeNode]) -> bool:
    def validate(node, lo: float, hi: float) -> bool:
        if not node:
            return True
        if not (lo < node.val < hi):
            return False
        return (validate(node.left,  lo,        node.val) and
                validate(node.right, node.val,  hi))

    return validate(root, float('-inf'), float('inf'))
```

**Edge Cases**
- Single node → always valid
- `[5, 4, 6, None, None, 3, 7]` — node 3 is in right subtree of 5 but < 5, invalid; range check catches this
- Duplicate values → `[1,1]` fails strict inequality
- Values at INT boundaries → use float('-inf') / float('inf')

**Complexity**
- Time: O(n) — visit every node
- Space: O(h) — recursion stack

**Follow-ups**
- "Recover BST where two nodes are swapped?" → LeetCode #99; find inversion in inorder.
- "Count nodes in range [lo, hi]?" → Traverse only relevant subtrees.

---

### Problem 2 — Kth Smallest Element in BST (LeetCode #230)

**Clarifying Questions**
- k is 1-indexed? (Yes, k=1 means smallest)
- Is k guaranteed valid (1 ≤ k ≤ n)? (Yes, per problem constraints)
- Can I modify the tree? (Prefer not to)
- Follow-up: BST is frequently modified, how to optimize? (Augment with subtree sizes)

**Brute Force**

In-order gives sorted output; return index k-1.

```python
def kth_smallest_brute(root: Optional[TreeNode], k: int) -> int:
    values = []
    def inorder(node):
        if not node: return
        inorder(node.left)
        values.append(node.val)
        inorder(node.right)
    inorder(root)
    return values[k - 1]
    # O(n) time, O(n) space
```

**Optimization**

In-order traversal with early termination: decrement k at each visit, stop when k reaches 0.

```python
def kth_smallest(root: Optional[TreeNode], k: int) -> int:
    # Iterative in-order with early exit — O(h + k) time, O(h) space
    stack, curr = [], root
    while stack or curr:
        while curr:
            stack.append(curr)
            curr = curr.left
        curr = stack.pop()
        k -= 1
        if k == 0:
            return curr.val
        curr = curr.right
    return -1  # unreachable if k is valid
```

**Edge Cases**
- k = 1 → leftmost node (minimum)
- k = n → rightmost node (maximum)
- Skewed tree → iterative avoids deep recursion

**Complexity**
- Time: O(h + k) — h to reach leftmost, k steps in-order
- Space: O(h) stack

**Follow-ups**
- "If BST is frequently modified and kth-smallest queried often?" → Augment each node with `left_count`; find in O(log n).
- "Kth largest?" → Reverse inorder (Right→Root→Left).

---

### Problem 3 — Insert into BST (LeetCode #701)

**Clarifying Questions**
- Will val already exist in the tree? (Problem guarantees it does not)
- Should I return the root? (Yes)
- In-place or new node? (New node at the correct leaf position)

**Brute Force / Optimal (same here)**

BST insert is naturally optimal: follow BST property to find the leaf position.

```python
def insert_into_bst(root: Optional[TreeNode], val: int) -> TreeNode:
    # Recursive — O(h) time, O(h) space
    if not root:
        return TreeNode(val)
    if val < root.val:
        root.left  = insert_into_bst(root.left, val)
    else:
        root.right = insert_into_bst(root.right, val)
    return root

# Iterative — avoids recursion stack, O(h) time, O(1) space
def insert_into_bst_iter(root: Optional[TreeNode], val: int) -> TreeNode:
    new_node = TreeNode(val)
    if not root:
        return new_node
    curr = root
    while True:
        if val < curr.val:
            if not curr.left:
                curr.left = new_node
                break
            curr = curr.left
        else:
            if not curr.right:
                curr.right = new_node
                break
            curr = curr.right
    return root
```

**Edge Cases**
- Empty tree → new node becomes root
- All values smaller than new val → insert at rightmost leaf
- All values larger → insert at leftmost leaf

**Complexity**
- Time: O(h) — follow path to insertion point
- Space: O(h) recursive; O(1) iterative

**Follow-ups**
- "After many inserts with sorted data, tree degenerates — how to fix?" → Self-balancing BST (AVL or Red-Black).
- "Insert and keep tree balanced?" → Use `sortedcontainers.SortedList` in Python for interview shortcut.

---

## Interview Q&A

**Q1: Why is the worst-case BST O(n) if it's supposed to be O(log n)?**

A: BST gives O(log n) only when balanced (height ≈ log n). Insert elements in sorted order (1, 2, 3, 4...) and you get a right-skewed chain — height = n, making search O(n). Self-balancing BSTs (AVL, Red-Black) prevent this by maintaining height invariants through rotations after every insert/delete.

---

**Q2: How does in-order traversal produce sorted output?**

A: BST invariant guarantees left subtree values < root < right subtree values at every node. In-order visits left subtree first (all smaller), then root, then right subtree (all larger). Applied recursively at every level, this means nodes are visited in strictly increasing order — a proof by structural induction on the BST property.

---

**Q3: When would you use a BST over a hash map?**

A:
```
Use BST when you need:
├─ Ordered iteration (in-order gives sorted sequence)
├─ Range queries: "all keys between 10 and 50"
├─ Floor/Ceiling: "largest key ≤ k" or "smallest key ≥ k"
├─ Predecessor/Successor: "next key after k"
└─ Rank/Select: "kth smallest key"

Use hash map when you need:
├─ Pure O(1) key lookup with no ordering requirements
├─ Simpler implementation
└─ Maximum throughput for get/put operations
```

In Java: `TreeMap` (Red-Black BST) vs `HashMap`. Use `TreeMap` when ordering matters.

---

**Q4: Describe the three cases for BST deletion.**

A:
```
Case 1 — Node is a leaf (no children):
  Simply remove it. Parent's pointer becomes null.

Case 2 — Node has one child:
  Replace node with its child. Parent adopts the grandchild.

Case 3 — Node has two children (hardest):
  Find in-order successor (leftmost node in right subtree).
  Copy successor's value into current node.
  Delete the successor (it has at most one right child → Case 1 or 2).

Why in-order successor? It's the smallest value > current node,
preserving the BST property after replacement.
```

---

**Q5: What is a self-balancing BST and why does it matter in practice?**

A: A self-balancing BST automatically maintains height ≈ O(log n) after every insert/delete using rotations (AVL) or color-flipping (Red-Black). This guarantees worst-case O(log n) for all operations, eliminating the degenerate O(n) case. Java's `TreeMap`/`TreeSet` uses Red-Black trees. Python's `sortedcontainers.SortedList` uses a different structure (sorted blocks). AVL trees are height-balanced (stricter), Red-Black trees have faster inserts (fewer rotations).

---

**Q6: How do you find the in-order successor of a node in a BST?**

A:
```
Case 1: Node has a right subtree
  Successor = leftmost node of right subtree (minimum of right)

Case 2: Node has no right subtree
  Successor = lowest ancestor for which this node is in left subtree
  Travel up via parent pointers until you take a left turn.

Code (with parent pointer):
def successor(node):
    if node.right:
        curr = node.right
        while curr.left:
            curr = curr.left
        return curr
    parent = node.parent
    while parent and node == parent.right:
        node, parent = parent, parent.parent
    return parent
```

---

**Q7: BST vs. Heap — which to use for "find kth largest"?**

A: Both work, but heap is better for streaming/online scenarios.

```
BST (balanced):
  - Insert k elements, then extract max iteratively
  - O(n log n) build + O(k log n) extract
  - Supports arbitrary inserts/deletes

Min-heap of size k:
  - Maintain heap of k largest seen so far
  - When new element > heap min: pop min, push new element
  - O(n log k) total
  - kth largest = heap[0]
  - Better when k << n

Verdict: heap for "kth largest in stream"; BST if also need range queries
```

---

**Q8: What does "augmenting" a BST mean? Give an example.**

A: Augmenting means storing extra information in each node to support additional operations efficiently. Example: store `size` (number of nodes in subtree) at each node. Maintain it on insert/delete with O(1) extra work per rotation. This enables O(log n) rank (how many nodes < k) and select (kth smallest) operations, rather than O(n) traversal. Red-Black trees in Java's TreeMap can be augmented this way for order statistics.

---

## Interview Tips

- **Always mention degenerate case.** When asked "what's the complexity of BST?", say "O(log n) average, O(n) worst case for skewed tree, O(log n) guaranteed with self-balancing BST."
- **In-order = sorted.** Any problem asking for kth smallest or sorted output from a BST is an in-order traversal with early exit.
- **Deletion Case 3 is the trap.** Most candidates forget to handle two-children deletion. Practice it: find in-order successor, copy value, delete successor.
- **Range + ordering = BST over HashMap.** If the interviewer mentions range queries, floor/ceiling, or sorted iteration, BST (e.g., Python `SortedList`, Java `TreeMap`) beats hash map.
- **Validate BST pattern.** Pass `(lo, hi)` bounds down — do not just compare to parent, because a node deep in the right subtree must still be > the root.
