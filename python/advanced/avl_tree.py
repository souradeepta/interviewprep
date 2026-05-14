"""
AVL Tree (Adelson-Velsky and Landis)
=====================================
A self-balancing Binary Search Tree where the heights of the two child
subtrees of any node differ by at most one. Rebalancing is done via single
and double rotations after every insert/delete.

Complexities:
    - Insert:  O(log n)   — guaranteed, not amortized
    - Delete:  O(log n)
    - Search:  O(log n)
    - Space:   O(n)
"""

from __future__ import annotations
from typing import Optional, Any, List


class AVLNode:
    """A node that also stores its subtree height for O(1) balance queries."""

    def __init__(self, key: Any) -> None:
        self.key: Any = key
        self.left: Optional[AVLNode] = None
        self.right: Optional[AVLNode] = None
        self.height: int = 1  # new node is a leaf

    def __repr__(self) -> str:
        return f"AVLNode({self.key}, h={self.height})"


class AVLTree:
    """
    AVL Tree with insert, delete, search, and ASCII visualization.

    All mutation methods return (or internally re-assign) the subtree root so
    the tree re-links itself after rotations without a parent pointer.
    """

    def __init__(self) -> None:
        self._root: Optional[AVLNode] = None

    # ------------------------------------------------------------------
    # Height helper
    # ------------------------------------------------------------------

    @staticmethod
    def _h(node: Optional[AVLNode]) -> int:
        """Return stored height, or 0 for None."""
        return node.height if node else 0

    def _update_height(self, node: AVLNode) -> None:
        node.height = 1 + max(self._h(node.left), self._h(node.right))

    # ------------------------------------------------------------------
    # Balance factor
    # ------------------------------------------------------------------

    def get_balance(self, node: Optional[AVLNode]) -> int:
        """
        Balance factor = height(left) - height(right).
        A value outside [-1, 1] means the node is unbalanced.

        Time:  O(1)
        """
        if node is None:
            return 0
        return self._h(node.left) - self._h(node.right)

    # ------------------------------------------------------------------
    # Rotations
    # ------------------------------------------------------------------

    def rotate_right(self, z: AVLNode) -> AVLNode:
        """
        Right rotation around *z*.

              z                y
             / \\             / \\
            y   T4    →    x    z
           / \\                 / \\
          x   T3              T3  T4

        Time:  O(1)
        """
        y = z.left
        T3 = y.right

        y.right = z
        z.left = T3

        self._update_height(z)
        self._update_height(y)
        return y  # new subtree root

    def rotate_left(self, z: AVLNode) -> AVLNode:
        """
        Left rotation around *z*.

          z                   y
         / \\                 / \\
        T1   y      →      z    x
            / \\           / \\
           T2   x         T1  T2

        Time:  O(1)
        """
        y = z.right
        T2 = y.left

        y.left = z
        z.right = T2

        self._update_height(z)
        self._update_height(y)
        return y  # new subtree root

    # ------------------------------------------------------------------
    # Rebalance
    # ------------------------------------------------------------------

    def _rebalance(self, node: AVLNode) -> AVLNode:
        """Apply the appropriate rotation(s) if *node* is unbalanced."""
        self._update_height(node)
        balance = self.get_balance(node)

        # Left-Left case
        if balance > 1 and self.get_balance(node.left) >= 0:
            return self.rotate_right(node)

        # Left-Right case
        if balance > 1 and self.get_balance(node.left) < 0:
            node.left = self.rotate_left(node.left)
            return self.rotate_right(node)

        # Right-Right case
        if balance < -1 and self.get_balance(node.right) <= 0:
            return self.rotate_left(node)

        # Right-Left case
        if balance < -1 and self.get_balance(node.right) > 0:
            node.right = self.rotate_right(node.right)
            return self.rotate_left(node)

        return node  # already balanced

    # ------------------------------------------------------------------
    # Insert
    # ------------------------------------------------------------------

    def insert(self, key: Any) -> None:
        """
        Insert *key* and rebalance along the path back to the root.

        Time:  O(log n)
        Space: O(log n) call stack
        """
        self._root = self._insert(self._root, key)

    def _insert(self, node: Optional[AVLNode], key: Any) -> AVLNode:
        if node is None:
            return AVLNode(key)
        if key < node.key:
            node.left = self._insert(node.left, key)
        elif key > node.key:
            node.right = self._insert(node.right, key)
        else:
            return node  # duplicate — no change
        return self._rebalance(node)

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------

    def delete(self, key: Any) -> None:
        """
        Delete *key* and rebalance.

        Time:  O(log n)
        Space: O(log n) call stack
        """
        self._root = self._delete(self._root, key)

    def _delete(self, node: Optional[AVLNode], key: Any) -> Optional[AVLNode]:
        if node is None:
            return None
        if key < node.key:
            node.left = self._delete(node.left, key)
        elif key > node.key:
            node.right = self._delete(node.right, key)
        else:
            if node.left is None:
                return node.right
            if node.right is None:
                return node.left
            # Two children: replace with in-order successor.
            successor = self._min_node(node.right)
            node.key = successor.key
            node.right = self._delete(node.right, successor.key)
        return self._rebalance(node)

    def _min_node(self, node: AVLNode) -> AVLNode:
        while node.left:
            node = node.left
        return node

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def search(self, key: Any) -> bool:
        """
        Return True if *key* is in the tree.

        Time:  O(log n)
        Space: O(1) iterative
        """
        node = self._root
        while node:
            if key == node.key:
                return True
            node = node.left if key < node.key else node.right
        return False

    # ------------------------------------------------------------------
    # Height (public)
    # ------------------------------------------------------------------

    def height(self) -> int:
        """Return the height of the tree. Empty tree → 0."""
        return self._h(self._root)

    # ------------------------------------------------------------------
    # ASCII visualization
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        """Sideways ASCII print, right subtree on top."""
        lines: List[str] = []
        self._build_str(self._root, 0, lines)
        return "\n".join(lines) if lines else "<empty>"

    def _build_str(
        self, node: Optional[AVLNode], level: int, lines: List[str]
    ) -> None:
        if node is None:
            return
        self._build_str(node.right, level + 1, lines)
        lines.append("  " * level + f"{node.key}(h={node.height})")
        self._build_str(node.left, level + 1, lines)


# ----------------------------------------------------------------------
# Demo
# ----------------------------------------------------------------------

if __name__ == "__main__":
    avl = AVLTree()
    keys = [10, 20, 30, 40, 50, 25]
    print("=== AVL Tree ===")
    print(f"Inserting: {keys}")
    for k in keys:
        avl.insert(k)

    print(avl)
    print()
    print("Height    :", avl.height())
    print("Balance(root):", avl.get_balance(avl._root))
    print()
    print("Search 25 :", avl.search(25))
    print("Search 99 :", avl.search(99))
    print()
    avl.delete(40)
    print("After deleting 40:")
    print(avl)

    # Demonstrate LL, LR, RL, RR cases by sequential inserts.
    print("\n--- Inserting 1..7 (forces all rotation types) ---")
    avl2 = AVLTree()
    for k in range(1, 8):
        avl2.insert(k)
    print(avl2)
    print("Height:", avl2.height(), "(should be 3 for 7 nodes)")
