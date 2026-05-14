"""
Binary Search Tree (BST)
========================
A node-based binary tree where each node's left subtree contains only nodes
with keys less than the node's key, and the right subtree contains only nodes
with keys greater than the node's key.

Complexities (balanced tree):
    - Insert:   O(log n) average, O(n) worst
    - Delete:   O(log n) average, O(n) worst
    - Search:   O(log n) average, O(n) worst
    - Traversal: O(n)
    - Space:    O(n)
"""

from __future__ import annotations
from typing import Optional, List, Any


class Node:
    """A single node in a Binary Search Tree."""

    def __init__(self, key: Any) -> None:
        self.key: Any = key
        self.left: Optional[Node] = None
        self.right: Optional[Node] = None

    def __repr__(self) -> str:
        return f"Node({self.key})"


class BST:
    """
    Binary Search Tree.

    Supports generic comparable keys. All public methods are thin wrappers
    around private recursive helpers so callers never need to pass the root.
    """

    def __init__(self) -> None:
        self._root: Optional[Node] = None

    # ------------------------------------------------------------------
    # Insert
    # ------------------------------------------------------------------

    def insert(self, key: Any) -> None:
        """
        Insert *key* into the BST.

        Time:  O(log n) average, O(n) worst (degenerate tree)
        Space: O(log n) call stack average
        """
        self._root = self._insert(self._root, key)

    def _insert(self, node: Optional[Node], key: Any) -> Node:
        if node is None:
            return Node(key)
        if key < node.key:
            node.left = self._insert(node.left, key)
        elif key > node.key:
            node.right = self._insert(node.right, key)
        # Duplicate keys are silently ignored.
        return node

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def search(self, key: Any) -> bool:
        """
        Return True if *key* exists in the BST, else False.

        Time:  O(log n) average, O(n) worst
        Space: O(log n) call stack average
        """
        return self._search(self._root, key)

    def _search(self, node: Optional[Node], key: Any) -> bool:
        if node is None:
            return False
        if key == node.key:
            return True
        if key < node.key:
            return self._search(node.left, key)
        return self._search(node.right, key)

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------

    def delete(self, key: Any) -> None:
        """
        Remove *key* from the BST (no-op if absent).

        Strategy:
          - Leaf node      → simply remove.
          - One child      → replace node with that child.
          - Two children   → replace with in-order successor (min of right
                             subtree), then delete the successor.

        Time:  O(log n) average, O(n) worst
        Space: O(log n) call stack average
        """
        self._root = self._delete(self._root, key)

    def _delete(self, node: Optional[Node], key: Any) -> Optional[Node]:
        if node is None:
            return None
        if key < node.key:
            node.left = self._delete(node.left, key)
        elif key > node.key:
            node.right = self._delete(node.right, key)
        else:
            # Node to delete found.
            if node.left is None:
                return node.right
            if node.right is None:
                return node.left
            # Two children: find in-order successor.
            successor = self._min_node(node.right)
            node.key = successor.key
            node.right = self._delete(node.right, successor.key)
        return node

    # ------------------------------------------------------------------
    # Min / Max
    # ------------------------------------------------------------------

    def find_min(self) -> Any:
        """
        Return the minimum key in the BST.

        Time:  O(log n) average, O(n) worst
        Space: O(1)
        Raises ValueError if the tree is empty.
        """
        if self._root is None:
            raise ValueError("BST is empty")
        return self._min_node(self._root).key

    def find_max(self) -> Any:
        """
        Return the maximum key in the BST.

        Time:  O(log n) average, O(n) worst
        Space: O(1)
        Raises ValueError if the tree is empty.
        """
        if self._root is None:
            raise ValueError("BST is empty")
        node = self._root
        while node.right:
            node = node.right
        return node.key

    def _min_node(self, node: Node) -> Node:
        while node.left:
            node = node.left
        return node

    # ------------------------------------------------------------------
    # Height
    # ------------------------------------------------------------------

    def height(self) -> int:
        """
        Return the height of the tree (number of edges on the longest
        root-to-leaf path). An empty tree has height -1.

        Time:  O(n)
        Space: O(n) call stack
        """
        return self._height(self._root)

    def _height(self, node: Optional[Node]) -> int:
        if node is None:
            return -1
        return 1 + max(self._height(node.left), self._height(node.right))

    # ------------------------------------------------------------------
    # Balance check
    # ------------------------------------------------------------------

    def is_balanced(self) -> bool:
        """
        Return True if the BST is height-balanced (no subtree differs in
        height by more than 1 at any node).

        Time:  O(n)
        Space: O(n) call stack
        """
        return self._check_balanced(self._root) != -2

    def _check_balanced(self, node: Optional[Node]) -> int:
        """Return height if balanced, -2 as sentinel for 'unbalanced'."""
        if node is None:
            return -1
        left_h = self._check_balanced(node.left)
        if left_h == -2:
            return -2
        right_h = self._check_balanced(node.right)
        if right_h == -2:
            return -2
        if abs(left_h - right_h) > 1:
            return -2
        return 1 + max(left_h, right_h)

    # ------------------------------------------------------------------
    # Traversals
    # ------------------------------------------------------------------

    def inorder(self) -> List[Any]:
        """
        Return keys in sorted (ascending) order.

        Time:  O(n)
        Space: O(n)
        """
        result: List[Any] = []
        self._inorder(self._root, result)
        return result

    def _inorder(self, node: Optional[Node], result: List[Any]) -> None:
        if node:
            self._inorder(node.left, result)
            result.append(node.key)
            self._inorder(node.right, result)

    def preorder(self) -> List[Any]:
        """
        Return keys in root → left → right order.

        Time:  O(n)
        Space: O(n)
        """
        result: List[Any] = []
        self._preorder(self._root, result)
        return result

    def _preorder(self, node: Optional[Node], result: List[Any]) -> None:
        if node:
            result.append(node.key)
            self._preorder(node.left, result)
            self._preorder(node.right, result)

    def postorder(self) -> List[Any]:
        """
        Return keys in left → right → root order.

        Time:  O(n)
        Space: O(n)
        """
        result: List[Any] = []
        self._postorder(self._root, result)
        return result

    def _postorder(self, node: Optional[Node], result: List[Any]) -> None:
        if node:
            self._postorder(node.left, result)
            self._postorder(node.right, result)
            result.append(node.key)

    # ------------------------------------------------------------------
    # ASCII visualization
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        """
        Return a sideways ASCII representation of the tree.
        The root is on the left; right subtrees are on top.

        Example for keys [4, 2, 6, 1, 3, 5, 7]:
            7
          6
            5
        4
            3
          2
            1
        """
        lines: List[str] = []
        self._build_str(self._root, 0, lines)
        return "\n".join(lines)

    def _build_str(
        self, node: Optional[Node], level: int, lines: List[str]
    ) -> None:
        if node is None:
            return
        self._build_str(node.right, level + 1, lines)
        lines.append("  " * level + str(node.key))
        self._build_str(node.left, level + 1, lines)


# ----------------------------------------------------------------------
# Demo
# ----------------------------------------------------------------------

if __name__ == "__main__":
    bst = BST()
    for val in [5, 3, 7, 1, 4, 6, 8, 2]:
        bst.insert(val)

    print("=== Binary Search Tree ===")
    print(bst)
    print()
    print("Inorder   :", bst.inorder())
    print("Preorder  :", bst.preorder())
    print("Postorder :", bst.postorder())
    print()
    print("Min       :", bst.find_min())
    print("Max       :", bst.find_max())
    print("Height    :", bst.height())
    print("Balanced? :", bst.is_balanced())
    print()
    print("Search 4  :", bst.search(4))
    print("Search 9  :", bst.search(9))
    print()
    bst.delete(3)
    print("After deleting 3:")
    print("Inorder   :", bst.inorder())
    print(bst)
