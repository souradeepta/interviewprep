"""
Splay Tree - Self-Adjusting Binary Search Tree

Time Complexity (Amortized):
- Insert: O(log n)
- Delete: O(log n)
- Search: O(log n)
- Access: O(log n)

Space Complexity: O(n)

Use Cases:
- Recently accessed elements are faster to retrieve
- Cache-like behavior
- Adaptive performance for skewed access patterns
- Competitive with other balanced BSTs asymptotically

Key Insight:
- After each operation, splay the accessed node to root
- Splaying uses zig, zig-zig, and zig-zag rotations
- Self-balancing without explicit balance factors
- Amortized analysis gives O(log n) per operation
"""

from typing import Optional, List, Tuple


class SplayNode:
    """Node in splay tree."""

    def __init__(self, key):
        self.key = key
        self.left = None
        self.right = None
        self.parent = None


class SplayTree:
    """Self-adjusting binary search tree."""

    def __init__(self):
        self.root = None

    def _rotate_right(self, x: SplayNode) -> SplayNode:
        """Right rotation around x."""
        y = x.left
        x.left = y.right
        if y.right:
            y.right.parent = x
        y.parent = x.parent
        if not x.parent:
            self.root = y
        elif x == x.parent.right:
            x.parent.right = y
        else:
            x.parent.left = y
        y.right = x
        x.parent = y
        return y

    def _rotate_left(self, x: SplayNode) -> SplayNode:
        """Left rotation around x."""
        y = x.right
        x.right = y.left
        if y.left:
            y.left.parent = x
        y.parent = x.parent
        if not x.parent:
            self.root = y
        elif x == x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y
        y.left = x
        x.parent = y
        return y

    def _splay(self, x: SplayNode) -> None:
        """Splay node x to root."""
        while x.parent:
            parent = x.parent
            grandparent = parent.parent

            if not grandparent:
                # Zig: node is child of root
                if x == parent.left:
                    self._rotate_right(parent)
                else:
                    self._rotate_left(parent)
            elif parent == grandparent.left:
                if x == parent.left:
                    # Zig-zig (left-left)
                    self._rotate_right(grandparent)
                    self._rotate_right(parent)
                else:
                    # Zig-zag (left-right)
                    self._rotate_left(parent)
                    self._rotate_right(grandparent)
            else:
                if x == parent.right:
                    # Zig-zig (right-right)
                    self._rotate_left(grandparent)
                    self._rotate_left(parent)
                else:
                    # Zig-zag (right-left)
                    self._rotate_right(parent)
                    self._rotate_left(grandparent)

    def insert(self, key) -> bool:
        """Insert key into splay tree."""
        if not self.root:
            self.root = SplayNode(key)
            return True

        # Find insertion point
        curr = self.root
        while True:
            if key == curr.key:
                self._splay(curr)
                return False  # Duplicate

            if key < curr.key:
                if curr.left:
                    curr = curr.left
                else:
                    curr.left = SplayNode(key)
                    curr.left.parent = curr
                    self._splay(curr.left)
                    return True
            else:
                if curr.right:
                    curr = curr.right
                else:
                    curr.right = SplayNode(key)
                    curr.right.parent = curr
                    self._splay(curr.right)
                    return True

    def search(self, key) -> bool:
        """Search for key in splay tree."""
        curr = self.root
        while curr:
            if key == curr.key:
                self._splay(curr)
                return True
            elif key < curr.key:
                curr = curr.left
            else:
                curr = curr.right

        return False

    def delete(self, key) -> bool:
        """Delete key from splay tree."""
        if not self.search(key):
            return False

        # key is now at root
        left_subtree = self.root.left
        right_subtree = self.root.right

        if not left_subtree:
            self.root = right_subtree
            if self.root:
                self.root.parent = None
            return True

        # Find max in left subtree, splay it to root of left subtree
        max_node = left_subtree
        while max_node.right:
            max_node = max_node.right

        self.root = left_subtree
        self.root.parent = None
        self._splay(max_node)

        # Attach right subtree
        self.root.right = right_subtree
        if right_subtree:
            right_subtree.parent = self.root

        return True

    def inorder(self) -> List:
        """Return inorder traversal."""
        result = []

        def traverse(node):
            if node:
                traverse(node.left)
                result.append(node.key)
                traverse(node.right)

        traverse(self.root)
        return result

    def __contains__(self, key) -> bool:
        """Support 'in' operator."""
        return self.search(key)


if __name__ == "__main__":
    tree = SplayTree()

    # Test insertions
    keys = [50, 30, 70, 20, 40, 60, 80, 10, 25, 35, 65]
    print("Inserting keys:", keys)
    for key in keys:
        tree.insert(key)

    print("Inorder traversal:", tree.inorder())

    # Test search
    print("\nSearching for 35:", tree.search(35))
    print("Inorder after search(35):", tree.inorder())

    # Test search not found
    print("\nSearching for 100:", tree.search(100))

    # Test deletion
    print("\nDeleting 30...")
    tree.delete(30)
    print("Inorder after delete(30):", tree.inorder())

    print("\nDeleting 50 (root)...")
    tree.delete(50)
    print("Inorder after delete(50):", tree.inorder())

    # Test containment
    print("\n35 in tree:", 35 in tree)
    print("30 in tree:", 30 in tree)
