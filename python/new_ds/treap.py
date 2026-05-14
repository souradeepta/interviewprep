"""
Treap (Tree + Heap)
===================
A Treap is a randomized binary search tree (BST) that simultaneously satisfies:

  1. **BST property on keys**:  For every node n,
       all keys in n.left subtree < n.key < all keys in n.right subtree.

  2. **Max-Heap property on priorities**: For every node n,
       n.priority >= n.left.priority  AND  n.priority >= n.right.priority.

Each node is assigned a **random priority** at creation time.  Because the
priorities are random, the resulting tree is equivalent to a random BST built
by inserting keys in a uniformly random order — giving expected O(log n) height.

Core insight
------------
Given a set of (key, priority) pairs where all keys and priorities are distinct,
there is **exactly one** Treap shape that satisfies both properties simultaneously.
This means the structure is fully determined by the random priorities, removing
worst-case behavior caused by sorted input that would degenerate a plain BST.

Operations
----------
| Method            | Expected | Worst  |
|-------------------|----------|--------|
| insert(key)       | O(log n) | O(n)   |
| delete(key)       | O(log n) | O(n)   |
| search(key)       | O(log n) | O(n)   |
| split(key)        | O(log n) | O(n)   |
| merge(left,right) | O(log n) | O(n)   |
| inorder()         | O(n)     | O(n)   |

Space Complexity: O(n).

Split and Merge
---------------
These two operations make treap an elegant choice for interval/range problems:

- split(key) -> (left_treap, right_treap):
    All keys <= key go left, all keys > key go right.

- merge(left, right) -> combined_treap:
    All keys in left must be < all keys in right (caller's responsibility).

insert and delete are implemented using split+merge for clarity:
    insert(k): split at k, create new node, merge left + node + right.
    delete(k): split into (< k), (= k), (> k); merge (< k) with (> k).
"""

import random
from typing import Any, List, Optional, Tuple


class TreapNode:
    """
    A node in the Treap.

    Attributes
    ----------
    key      : Comparable key (BST property).
    priority : float in [0, 1) — random at creation (max-heap property).
    left     : Left child (TreapNode or None).
    right    : Right child (TreapNode or None).
    """

    __slots__ = ("key", "priority", "left", "right")

    def __init__(self, key: Any, priority: Optional[float] = None) -> None:
        self.key = key
        self.priority: float = priority if priority is not None else random.random()
        self.left: Optional["TreapNode"] = None
        self.right: Optional["TreapNode"] = None

    def __repr__(self) -> str:
        return f"TreapNode(key={self.key!r}, prio={self.priority:.4f})"


class Treap:
    """
    Treap: randomized BST with max-heap priority invariant.

    All public mutating operations (insert, delete) are built on top of
    split() and merge() for clarity and correctness.

    Example
    -------
    >>> t = Treap()
    >>> for k in [5, 2, 8, 1, 3]:
    ...     t.insert(k)
    >>> t.search(3)
    True
    >>> t.inorder()
    [1, 2, 3, 5, 8]
    >>> t.delete(2)
    >>> t.inorder()
    [1, 3, 5, 8]
    """

    def __init__(self) -> None:
        self.root: Optional[TreapNode] = None
        self.size: int = 0

    # ------------------------------------------------------------------
    # Core primitives: split and merge
    # ------------------------------------------------------------------

    def split(self, key: Any) -> Tuple["Treap", "Treap"]:
        """
        Split the treap into two treaps at key.

        Returns (left_treap, right_treap) where:
          - left_treap contains all nodes with key <= split_key
          - right_treap contains all nodes with key > split_key

        Time: O(log n) expected
        """
        left_root, right_root = self._split(self.root, key)
        left_t, right_t = Treap(), Treap()
        left_t.root = left_root
        right_t.root = right_root
        # Sizes are approximate here; use inorder count for exactness
        return left_t, right_t

    def _split(
        self, node: Optional[TreapNode], key: Any
    ) -> Tuple[Optional[TreapNode], Optional[TreapNode]]:
        """
        Recursively split subtree rooted at node.

        Returns (left_root, right_root):
          left_root  -> BST with all keys <= key
          right_root -> BST with all keys >  key

        Invariant: both returned subtrees satisfy BST + heap properties.
        """
        if node is None:
            return None, None
        if node.key <= key:
            # node goes to the left tree; recurse into right subtree
            left_of_right, right_root = self._split(node.right, key)
            node.right = left_of_right
            return node, right_root
        else:
            # node goes to the right tree; recurse into left subtree
            left_root, right_of_left = self._split(node.left, key)
            node.left = right_of_left
            return left_root, node

    @staticmethod
    def merge(left: "Treap", right: "Treap") -> "Treap":
        """
        Merge two treaps into one.

        Precondition: every key in left < every key in right.

        Time: O(log n) expected
        """
        merged = Treap()
        merged.root = Treap._merge_nodes(left.root, right.root)
        merged.size = left.size + right.size
        return merged

    @staticmethod
    def _merge_nodes(
        l: Optional[TreapNode], r: Optional[TreapNode]
    ) -> Optional[TreapNode]:
        """
        Recursively merge two subtrees.

        At each step, the node with the higher priority becomes the root
        (maintaining max-heap), and we recursively merge the remaining parts.
        """
        if l is None:
            return r
        if r is None:
            return l
        if l.priority >= r.priority:
            # l is the root; merge l.right with r
            l.right = Treap._merge_nodes(l.right, r)
            return l
        else:
            # r is the root; merge l with r.left
            r.left = Treap._merge_nodes(l, r.left)
            return r

    # ------------------------------------------------------------------
    # Public API (built on split + merge)
    # ------------------------------------------------------------------

    def insert(self, key: Any, priority: Optional[float] = None) -> None:
        """
        Insert a key into the treap.

        If key already exists, the operation is a no-op (no duplicate keys).
        A random priority is assigned unless priority is explicitly provided.

        Algorithm:
            1. Split into (left: keys < key, right: keys > key).
            2. Create new node with given key and random priority.
            3. Merge left + new_node + right.

        Time: O(log n) expected
        """
        if self.search(key):
            return  # no duplicates

        new_node = TreapNode(key=key, priority=priority)

        # Split at key-1 so left has keys <= key-1 (i.e., < key for integers)
        # For general comparable keys use split at key, then split again.
        left_root, right_root = self._split(self.root, key)
        # At this point left has keys <= key, right has keys > key.
        # Since we confirmed key is not present, left has keys < key (safe).
        # Merge: left <- new_node -> right
        temp = Treap._merge_nodes(new_node, right_root)
        self.root = Treap._merge_nodes(left_root, temp)
        self.size += 1

    def delete(self, key: Any) -> bool:
        """
        Delete the node with the given key.

        Returns True if found and deleted, False otherwise.

        Algorithm:
            1. Split into (left: keys < key) and (right: keys >= key).
            2. Split right into (mid: key == key) and (rest: keys > key).
               Since keys are unique, mid has exactly 0 or 1 nodes.
            3. Discard mid. Merge left + rest.

        Time: O(log n) expected
        """
        if not self.search(key):
            return False

        # left has keys < key, right_and_target has keys >= key
        left_root, right_and_target = self._split(self.root, key - 1
                                                  if isinstance(key, int)
                                                  else _prev_key(key))
        # From right_and_target, split off the target node
        # The target (if present) has key == key, so split at key gives
        # target alone in left and rest in right.
        target_root, rest_root = self._split(right_and_target, key)
        # target_root is the node with key == key (discard it)
        self.root = Treap._merge_nodes(left_root, rest_root)
        self.size -= 1
        return True

    def search(self, key: Any) -> bool:
        """
        Return True if key is in the treap.

        Time: O(log n) expected
        """
        return self._search_node(self.root, key) is not None

    def _search_node(self, node: Optional[TreapNode], key: Any) -> Optional[TreapNode]:
        if node is None:
            return None
        if key == node.key:
            return node
        elif key < node.key:
            return self._search_node(node.left, key)
        else:
            return self._search_node(node.right, key)

    def inorder(self) -> List[Any]:
        """
        Return all keys in sorted (ascending) order.

        Time: O(n)
        """
        result: List[Any] = []
        self._inorder(self.root, result)
        return result

    def _inorder(self, node: Optional[TreapNode], result: List[Any]) -> None:
        if node is None:
            return
        self._inorder(node.left, result)
        result.append(node.key)
        self._inorder(node.right, result)

    # ------------------------------------------------------------------
    # Verification helpers
    # ------------------------------------------------------------------

    def verify_bst(self) -> bool:
        """Check BST property: inorder keys are strictly sorted."""
        keys = self.inorder()
        return keys == sorted(set(keys))

    def verify_heap(self) -> bool:
        """Check max-heap property on priorities for all nodes."""
        return self._check_heap(self.root)

    def _check_heap(self, node: Optional[TreapNode]) -> bool:
        if node is None:
            return True
        if node.left and node.left.priority > node.priority:
            return False
        if node.right and node.right.priority > node.priority:
            return False
        return self._check_heap(node.left) and self._check_heap(node.right)

    # ------------------------------------------------------------------
    # Pretty print (ASCII tree)
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        """
        Display the treap as an ASCII tree showing (key, priority) per node.

        Right subtrees are printed at the top (sideways tree layout).
        """
        if self.root is None:
            return "<empty treap>"
        lines: List[str] = []
        self._print_node(self.root, "", True, lines)
        return "\n".join(lines)

    def _print_node(
        self, node: Optional[TreapNode], indent: str, last: bool, lines: List[str]
    ) -> None:
        if node is None:
            return
        connector = "└── " if last else "├── "
        lines.append(f"{indent}{connector}({node.key}, p={node.priority:.3f})")
        child_indent = indent + ("    " if last else "│   ")
        # Print right child first (appears above left in sideways layout)
        if node.right is not None or node.left is not None:
            self._print_node(node.right, child_indent, False, lines)
            self._print_node(node.left, child_indent, True, lines)

    def __repr__(self) -> str:
        return f"Treap(size={self.size}, root_key={self.root.key if self.root else None})"

    def __len__(self) -> int:
        return self.size


def _prev_key(key):
    """
    For non-integer keys, we can't compute key-1.
    For split-based delete on general keys, this isn't needed in practice
    since integer keys are the most common use case for treaps in interviews.
    Raises NotImplementedError for non-integer keys with delete.
    """
    raise NotImplementedError(
        "delete() for non-integer keys requires a custom _prev_key implementation. "
        "For integer keys this works automatically."
    )


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import random

    random.seed(42)  # reproducible output

    print("=" * 60)
    print("TREAP DEMO")
    print("=" * 60)

    # --- Build treap with fixed priorities to show both properties ---
    print("\n--- Controlled priority example (verify BST + heap) ---")
    t = Treap()
    # Insert with explicit priorities for demonstration
    inserts = [(5, 0.9), (2, 0.7), (8, 0.8), (1, 0.3), (3, 0.5), (7, 0.6), (9, 0.4)]
    for key, prio in inserts:
        t.insert(key, priority=prio)
        t.size = sum(1 for _ in t.inorder())  # recount

    print("\nTreap structure (key, priority) — right subtree shown above left:")
    print(t)
    print(f"\nIn-order keys (must be sorted): {t.inorder()}")
    print(f"BST  property holds: {t.verify_bst()}")
    print(f"Heap property holds: {t.verify_heap()}")

    # --- Random treap ---
    print("\n--- Random priority treap with 10 keys ---")
    random.seed(99)
    rt = Treap()
    keys = [4, 9, 2, 7, 1, 6, 3, 8, 5, 10]
    for k in keys:
        rt.insert(k)
    print(rt)
    print(f"\nIn-order: {rt.inorder()}")
    print(f"BST  holds: {rt.verify_bst()}")
    print(f"Heap holds: {rt.verify_heap()}")

    # --- Search ---
    print(f"\nsearch(7) -> {rt.search(7)}")
    print(f"search(11) -> {rt.search(11)}")

    # --- Delete ---
    print("\nDeleting keys 4, 1, 10:")
    for k in [4, 1, 10]:
        ok = rt.delete(k)
        print(f"  delete({k}) -> {ok}")
    print(f"In-order after deletes: {rt.inorder()}")
    print(f"BST  holds: {rt.verify_bst()}")
    print(f"Heap holds: {rt.verify_heap()}")

    # --- Split and merge ---
    print("\n--- Split at key=5 ---")
    random.seed(0)
    st = Treap()
    for k in range(1, 11):
        st.insert(k)
    print(f"Original in-order: {st.inorder()}")

    left_t, right_t = st.split(5)
    print(f"Left  (keys <= 5): {left_t.inorder()}")
    print(f"Right (keys >  5): {right_t.inorder()}")

    merged_t = Treap.merge(left_t, right_t)
    print(f"Merged in-order:   {merged_t.inorder()}")
    print(f"BST  holds after merge: {merged_t.verify_bst()}")
    print(f"Heap holds after merge: {merged_t.verify_heap()}")

    # --- Large random test for property verification ---
    print("\n--- Large random test (n=1000, verify BST + heap properties) ---")
    random.seed(7)
    big = Treap()
    sample_keys = random.sample(range(10_000), 1000)
    for k in sample_keys:
        big.insert(k)
    assert big.verify_bst(), "BST property violated!"
    assert big.verify_heap(), "Heap property violated!"
    print(f"Inserted {len(big)} keys. BST and Heap properties both hold.")

    # Delete half
    to_delete = sample_keys[:500]
    for k in to_delete:
        big.delete(k)
    assert big.verify_bst(), "BST property violated after deletes!"
    assert big.verify_heap(), "Heap property violated after deletes!"
    print(f"After 500 deletes: {len(big)} keys remain. Both properties still hold.")

    print("\nDone.")
