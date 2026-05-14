"""
B-Tree (Order t)
=================
A self-balancing search tree generalizing BST to nodes with many children.
Every node has between t-1 and 2t-1 keys (except root which can have as few
as 1). All leaves are at the same depth, making disk-read operations uniform.

Parameter *t* is the **minimum degree** (Cormen et al.):
    - Every non-root node has >= t-1 keys and <= 2t-1 keys.
    - Every non-root non-leaf has >= t children and <= 2t children.
    - Root has >= 1 key (if tree non-empty).

Complexities  (n = number of keys, t = minimum degree):
    - Search:  O(log_t n)  i.e. O(log n)
    - Insert:  O(log_t n)
    - Delete:  O(log_t n)
    - Space:   O(n)

Use cases: database indexing, file systems (ext4, NTFS, HFS+).
"""

from __future__ import annotations
from typing import Any, List, Optional, Tuple


class BTreeNode:
    """
    A node in the B-Tree.

    Attributes:
        keys:     sorted list of keys stored in this node.
        children: list of child BTreeNode pointers (empty for leaves).
        leaf:     True if this node has no children.
    """

    def __init__(self, leaf: bool = True) -> None:
        self.keys: List[Any] = []
        self.children: List[BTreeNode] = []
        self.leaf: bool = leaf

    def __repr__(self) -> str:
        return f"BTreeNode(keys={self.keys}, leaf={self.leaf})"


class BTree:
    """
    B-Tree of minimum degree *t*.

    - Minimum keys per non-root node: t - 1
    - Maximum keys per node:          2t - 1
    """

    def __init__(self, t: int = 2) -> None:
        if t < 2:
            raise ValueError("Minimum degree t must be >= 2")
        self._t = t
        self._root: BTreeNode = BTreeNode(leaf=True)

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def search(self, key: Any) -> bool:
        """
        Return True if *key* exists in the B-Tree.

        Time:  O(log n)
        Space: O(log n) call stack
        """
        return self._search(self._root, key)

    def _search(self, node: BTreeNode, key: Any) -> bool:
        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i += 1
        if i < len(node.keys) and key == node.keys[i]:
            return True
        if node.leaf:
            return False
        return self._search(node.children[i], key)

    # ------------------------------------------------------------------
    # Insert
    # ------------------------------------------------------------------

    def insert(self, key: Any) -> None:
        """
        Insert *key* into the B-Tree.

        If root is full, splits it first (only time tree grows in height).

        Time:  O(log n)
        Space: O(t) per level during split propagation
        """
        root = self._root
        if len(root.keys) == 2 * self._t - 1:
            # Root is full — create a new root and split the old one.
            new_root = BTreeNode(leaf=False)
            new_root.children.append(self._root)
            self._split_child(new_root, 0)
            self._root = new_root
        self._insert_non_full(self._root, key)

    def _insert_non_full(self, node: BTreeNode, key: Any) -> None:
        """Insert *key* into a node guaranteed to be non-full."""
        i = len(node.keys) - 1
        if node.leaf:
            node.keys.append(None)  # placeholder
            while i >= 0 and key < node.keys[i]:
                node.keys[i + 1] = node.keys[i]
                i -= 1
            node.keys[i + 1] = key
        else:
            while i >= 0 and key < node.keys[i]:
                i -= 1
            i += 1
            if len(node.children[i].keys) == 2 * self._t - 1:
                self._split_child(node, i)
                if key > node.keys[i]:
                    i += 1
            self._insert_non_full(node.children[i], key)

    def split_child(self, parent: BTreeNode, i: int) -> None:
        """Public wrapper around _split_child (for testing)."""
        self._split_child(parent, i)

    def _split_child(self, parent: BTreeNode, i: int) -> None:
        """
        Split the full child parent.children[i] into two nodes and
        promote its median key up into *parent*.

        Time:  O(t)
        """
        t = self._t
        full_child = parent.children[i]
        new_child = BTreeNode(leaf=full_child.leaf)

        # Median key index in full_child.
        median_idx = t - 1
        median_key = full_child.keys[median_idx]

        # Right half keys go into new_child.
        new_child.keys = full_child.keys[median_idx + 1:]
        full_child.keys = full_child.keys[:median_idx]

        # Right half children go into new_child (if not leaf).
        if not full_child.leaf:
            new_child.children = full_child.children[t:]
            full_child.children = full_child.children[:t]

        # Insert median key and new child pointer into parent.
        parent.keys.insert(i, median_key)
        parent.children.insert(i + 1, new_child)

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------

    def delete(self, key: Any) -> None:
        """
        Delete *key* from the B-Tree (no-op if absent).

        Handles all cases:
          Case 1: key in leaf node.
          Case 2: key in internal node.
            2a: left child has >= t keys → replace with predecessor.
            2b: right child has >= t keys → replace with successor.
            2c: both children have t-1 keys → merge them.
          Case 3: key not in current node — ensure the child we descend
                  into has >= t keys (borrow from sibling or merge).

        Time:  O(log n)
        """
        self._delete(self._root, key)
        # If root is now empty and has a child, shrink the tree height.
        if len(self._root.keys) == 0 and not self._root.leaf:
            self._root = self._root.children[0]

    def _delete(self, node: BTreeNode, key: Any) -> None:
        t = self._t
        i = self._find_key_index(node, key)

        if i < len(node.keys) and node.keys[i] == key:
            # Key is in this node.
            if node.leaf:
                # Case 1: simply remove.
                node.keys.pop(i)
            else:
                self._delete_from_internal(node, i)
        else:
            # Key is NOT in this node.
            if node.leaf:
                return  # key not in tree
            # Ensure child[i] has at least t keys before descending.
            if len(node.children[i].keys) < t:
                self._fill_child(node, i)
                # After fill, the structure may have shifted.
                i = self._find_key_index(node, key)
                if i < len(node.keys) and node.keys[i] == key:
                    self._delete_from_internal(node, i)
                    return
                # Recalculate child index after potential merge/borrow.
                i = min(i, len(node.children) - 1)
            self._delete(node.children[i], key)

    def _find_key_index(self, node: BTreeNode, key: Any) -> int:
        """Return the index of the first key >= *key* in node.keys."""
        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i += 1
        return i

    def _delete_from_internal(self, node: BTreeNode, i: int) -> None:
        """Delete node.keys[i] from internal node *node*."""
        t = self._t
        key = node.keys[i]
        left_child = node.children[i]
        right_child = node.children[i + 1]

        if len(left_child.keys) >= t:
            # Case 2a: replace with predecessor (max key in left subtree).
            pred = self._get_max(left_child)
            node.keys[i] = pred
            self._delete(left_child, pred)
        elif len(right_child.keys) >= t:
            # Case 2b: replace with successor (min key in right subtree).
            succ = self._get_min(right_child)
            node.keys[i] = succ
            self._delete(right_child, succ)
        else:
            # Case 2c: merge left and right children.
            self._merge_children(node, i)
            self._delete(left_child, key)

    def _get_max(self, node: BTreeNode) -> Any:
        while not node.leaf:
            node = node.children[-1]
        return node.keys[-1]

    def _get_min(self, node: BTreeNode) -> Any:
        while not node.leaf:
            node = node.children[0]
        return node.keys[0]

    def _fill_child(self, parent: BTreeNode, i: int) -> None:
        """
        Ensure parent.children[i] has at least t keys by borrowing from a
        sibling or merging with one.
        """
        t = self._t
        has_left_sibling = i > 0
        has_right_sibling = i < len(parent.children) - 1
        left_rich = has_left_sibling and len(parent.children[i - 1].keys) >= t
        right_rich = has_right_sibling and len(parent.children[i + 1].keys) >= t

        if left_rich:
            self._borrow_from_prev(parent, i)
        elif right_rich:
            self._borrow_from_next(parent, i)
        elif has_left_sibling:
            self._merge_children(parent, i - 1)
        else:
            self._merge_children(parent, i)

    def _borrow_from_prev(self, parent: BTreeNode, i: int) -> None:
        """Borrow a key from parent.children[i-1] (left sibling)."""
        child = parent.children[i]
        left_sib = parent.children[i - 1]
        # Push parent key down to front of child.
        child.keys.insert(0, parent.keys[i - 1])
        # If not leaf, move last child of left_sib to child.
        if not child.leaf:
            child.children.insert(0, left_sib.children.pop())
        # Promote last key of left_sib to parent.
        parent.keys[i - 1] = left_sib.keys.pop()

    def _borrow_from_next(self, parent: BTreeNode, i: int) -> None:
        """Borrow a key from parent.children[i+1] (right sibling)."""
        child = parent.children[i]
        right_sib = parent.children[i + 1]
        # Push parent key down to end of child.
        child.keys.append(parent.keys[i])
        # If not leaf, move first child of right_sib to child.
        if not child.leaf:
            child.children.append(right_sib.children.pop(0))
        # Promote first key of right_sib to parent.
        parent.keys[i] = right_sib.keys.pop(0)

    def _merge_children(self, parent: BTreeNode, i: int) -> None:
        """
        Merge parent.children[i] and parent.children[i+1] together,
        pulling the separator key parent.keys[i] down into the merged node.
        """
        left = parent.children[i]
        right = parent.children[i + 1]
        sep = parent.keys.pop(i)
        parent.children.pop(i + 1)

        left.keys.append(sep)
        left.keys.extend(right.keys)
        if not left.leaf:
            left.children.extend(right.children)

    # ------------------------------------------------------------------
    # ASCII visualization
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        """Print the B-Tree level by level."""
        if not self._root.keys:
            return "<empty B-Tree>"
        lines = []
        level_nodes = [self._root]
        level = 0
        while level_nodes:
            level_keys = [str(n.keys) for n in level_nodes]
            lines.append(f"Level {level}: " + "  |  ".join(level_keys))
            next_level = []
            for node in level_nodes:
                next_level.extend(node.children)
            level_nodes = next_level
            level += 1
        return "\n".join(lines)


# ----------------------------------------------------------------------
# Demo
# ----------------------------------------------------------------------

if __name__ == "__main__":
    print("=== B-Tree (t=3) ===")
    bt = BTree(t=3)
    keys = [10, 20, 5, 6, 12, 30, 7, 17, 3, 1, 15, 25]
    print("Inserting:", keys)
    for k in keys:
        bt.insert(k)
    print()
    print(bt)
    print()
    print("Search 15:", bt.search(15))
    print("Search 99:", bt.search(99))
    print()
    for k in [6, 20, 10]:
        bt.delete(k)
        print(f"After deleting {k}:")
        print(bt)
        print()
