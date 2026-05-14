# Treap

A randomized binary search tree that simultaneously satisfies the BST property on keys and a max-heap property on randomly assigned priorities, guaranteeing O(log n) expected height without deterministic rebalancing.

---

## Overview

A Treap combines a Binary Search Tree with a heap by assigning each node a random priority at insertion time. The BST invariant orders nodes by key; the max-heap invariant requires every node's priority to be greater than or equal to its children's priorities. Because priorities are random, the resulting tree structure is equivalent to a random BST built by inserting keys in uniformly random order — giving expected height O(log n) regardless of insertion sequence.

The critical insight is uniqueness: given any set of (key, priority) pairs with distinct keys and distinct priorities, there is exactly one tree shape satisfying both invariants simultaneously. This means the tree shape is entirely determined by the random priorities, eliminating the worst-case O(n) behavior caused by sorted insertion that degrades plain BSTs. Unlike AVL or Red-Black trees, no rotations or rebalancing bookkeeping are needed — the random priorities maintain balance probabilistically.

The `split` and `merge` primitives make Treap particularly elegant: insert is implemented as split + create + merge, and delete as two splits + discard target + merge. These same primitives support interval and range operations efficiently. Treaps are used in competitive programming for implicit treaps (array-as-BST), in functional languages for persistent sets, and anywhere a balanced BST is needed with simpler implementation than Red-Black or AVL.

---

## ASCII Visualization

```
Treap with keys {1,2,3,5,7,8,9} and fixed priorities (for illustration):

Inserted: (5,p=0.9), (2,p=0.7), (8,p=0.8), (1,p=0.3), (3,p=0.5), (7,p=0.6), (9,p=0.4)

Resulting tree (key, priority):
               (5, 0.9)              <- highest priority = root
              /          \
        (2, 0.7)        (8, 0.8)
        /      \        /      \
   (1, 0.3) (3, 0.5) (7, 0.6) (9, 0.4)

BST  check (inorder): 1 < 2 < 3 < 5 < 7 < 8 < 9  ✓
Heap check (every node's priority >= children's):
  0.9 >= 0.7, 0.8   ✓
  0.7 >= 0.3, 0.5   ✓
  0.8 >= 0.6, 0.4   ✓

--- split(root, key=5) ---
All keys <= 5 go LEFT, keys > 5 go RIGHT:

    LEFT treap            RIGHT treap
       (5, 0.9)              (8, 0.8)
       /                     /      \
  (2, 0.7)              (7, 0.6)  (9, 0.4)
  /      \
(1,0.3) (3,0.5)

--- merge(LEFT, RIGHT) ---
Compare roots: LEFT.root.prio=0.9 > RIGHT.root.prio=0.8
  -> 5 is new root; recursively merge LEFT.root.right with RIGHT.root
  Result: original tree restored.

--- insert(key=4, prio=0.85) ---
1. split at 4: left={1,2,3}, right={5,7,8,9}
2. create node (4, 0.85)
3. merge left + new_node + right:
   new tree root becomes (5,0.9); (4,0.85) lands between (3,0.5) and (5,0.9)
```

---

## Operations & Complexity

| Operation       | Expected | Worst | Notes                                          |
|-----------------|----------|-------|------------------------------------------------|
| `insert(key)`   | O(log n) | O(n)  | One split + two merges                         |
| `delete(key)`   | O(log n) | O(n)  | Two splits + one merge + discard               |
| `search(key)`   | O(log n) | O(n)  | Standard BST traversal                         |
| `split(key)`    | O(log n) | O(n)  | Traces one root-to-leaf path                   |
| `merge(L, R)`   | O(log n) | O(n)  | Traces one combined root-to-leaf path          |
| `inorder()`     | O(n)     | O(n)  | Full DFS traversal                             |
| Space           | O(n)     | O(n)  | One node per key                               |

- Expected bounds hold with high probability over the random priority choices.
- Worst case O(n) is theoretically possible but astronomically unlikely with independent uniform random priorities.

---

## Key Invariants

- **BST property**: for every node `n`, all keys in `n.left` subtree are strictly less than `n.key`, and all keys in `n.right` subtree are strictly greater than `n.key`.
- **Max-heap property on priorities**: `n.priority >= n.left.priority` and `n.priority >= n.right.priority` for every node `n`.
- **Uniqueness**: given distinct keys and distinct priorities, the Treap shape is uniquely determined — there is exactly one valid tree satisfying both invariants.
- **Random priorities**: priorities are assigned independently and uniformly at random at node creation; they must never be changed after assignment.
- **No duplicate keys**: the structure assumes unique keys; inserting a duplicate is a no-op in this implementation.
- **Merge precondition**: `merge(L, R)` requires that every key in `L` is strictly less than every key in `R`; violating this breaks the BST property.

---

## Common Interview Questions

- **How does a Treap maintain balance without explicit rotations?** Random priorities make the expected tree shape identical to a random BST. The merge/split operations implicitly enforce both BST and heap properties without tracking balance factors or colors.
- **What is the relationship between a Treap and a random BST?** Inserting n keys into a Treap with random priorities gives the same distribution over tree shapes as inserting those same keys into a plain BST in a uniformly random order — expected height O(log n).
- **Explain split and merge and how they implement insert/delete.** `split(key)` traces a root-to-leaf path and partitions the tree into keys ≤ key and keys > key in O(log n). `merge(L, R)` reconstructs one tree from two by always choosing the higher-priority root. Insert = split + create node + two merges; delete = two splits + one merge.
- **Compare Treap vs Red-Black Tree vs AVL Tree.** All give O(log n) expected/worst operations. Treap has simpler implementation (no rotation cases, no color bookkeeping) but only probabilistic height guarantees. Red-Black and AVL give deterministic worst-case O(log n). Treap is preferred in competitive programming; Red-Black/AVL in production systems requiring deterministic guarantees.
- **What is an implicit Treap and what is it used for?** An implicit (or indexed) Treap uses the subtree size as the implicit key, allowing O(log n) array splicing, reversal of subarrays, and range operations — it acts as an order-statistics tree that supports split/merge.
- **What is the worst-case input for a Treap?** There is no deterministic worst-case input because the tree shape depends only on the random priorities, not the insertion order. An adversary cannot craft an input that causes O(n) behavior without knowing the random priorities in advance.

---

## Implementation Notes

- **Split via recursion**: `_split(node, key)` returns `(left_root, right_root)`; if `node.key <= key`, node goes left and we recurse into `node.right`; otherwise node goes right and we recurse into `node.left`. This traces exactly one path, giving O(depth) = O(log n) expected time.
- **Merge via priority comparison**: `_merge_nodes(l, r)` picks the higher-priority root, then recursively merges the remaining part of that root's subtree with the other tree — always traversing downward, never upward.
- **Delete for integer keys uses `split(key-1)` trick**: split at `key-1` to get all keys < key, then split the remainder at `key` to isolate and discard the target node. This avoids the need to search for the node before deleting it, but requires `key-1` to be computable (works cleanly for integers; requires a custom `_prev_key` for general types).
- **`random.random()` for priorities**: Python's `random.random()` returns floats in `[0.0, 1.0)`. The probability that two nodes receive identical priorities is negligible for practical n, but production code should handle ties (e.g., secondary sort by key) to guarantee the uniqueness invariant.
- **`__slots__` on TreapNode**: using `__slots__ = ("key", "priority", "left", "right")` reduces per-node memory overhead significantly for large n by bypassing the instance `__dict__`.
- **Size tracking**: the `Treap.size` field becomes inaccurate after `split()` because sizes are not redistributed. The implementation notes this limitation; for accurate sizes augment each node with a subtree size field (implicit treap pattern).

---

## References

- [Seidel, R. & Aragon, C. R. (1996). Randomized Search Trees. Algorithmica 16(4/5).](https://link.springer.com/article/10.1007/BF01940876)
- [Wikipedia — Treap](https://en.wikipedia.org/wiki/Treap)
- [CP-Algorithms — Treap](https://cp-algorithms.com/data_structures/treap.html)
