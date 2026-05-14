"""
B+ Tree (Database Index Structure)

Time Complexity:
- Search: O(log n)
- Insert: O(log n)
- Delete: O(log n)
- Range scan: O(log n + k) where k = results

Space Complexity: O(n)

Use Cases:
- Database indexing (primary index)
- File system indexing
- Multi-level sorted data structure
- Disk-based searching (minimizes I/O)
- Range queries over large datasets

Key Insight:
- All keys in leaves, internal nodes just guide search
- All leaves at same depth (balanced)
- Each node contains 60% to 100% of max capacity (t-1 to 2t-1 keys)
- Facilitates efficient range scans
- Leaf nodes can be linked for sequential access
"""

from typing import List, Optional, Tuple


class BPlusNode:
    """Node in B+ tree."""

    def __init__(self, is_leaf: bool, t: int):
        self.is_leaf = is_leaf
        self.t = t  # Minimum degree
        self.keys = []
        self.children = []
        self.next = None  # For leaf nodes: link to next leaf

    def is_full(self) -> bool:
        """Check if node is full."""
        return len(self.keys) == 2 * self.t - 1

    def has_min_keys(self) -> bool:
        """Check if node has minimum keys."""
        return len(self.keys) >= self.t - 1


class BPlusTree:
    """B+ tree for efficient searching and range queries."""

    def __init__(self, t: int = 3):
        """
        Initialize B+ tree.

        Args:
            t: Minimum degree (internal nodes have t-1 to 2t-1 keys)
        """
        self.root = BPlusNode(is_leaf=True, t=t)
        self.t = t

    def search(self, key: int) -> bool:
        """Search for key in tree."""
        return self._search(self.root, key) is not None

    def _search(self, node: BPlusNode, key: int) -> Optional[BPlusNode]:
        """Search and return leaf node containing key."""
        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i += 1

        if node.is_leaf:
            return node if i < len(node.keys) and node.keys[i] == key else None

        if i < len(node.keys) and key == node.keys[i]:
            return self._search(node.children[i + 1], key)

        return self._search(node.children[i], key)

    def insert(self, key: int) -> None:
        """Insert key into tree."""
        if self.root.is_full():
            new_root = BPlusNode(is_leaf=False, t=self.t)
            new_root.children.append(self.root)
            self._split_child(new_root, 0)
            self.root = new_root

        self._insert_non_full(self.root, key)

    def _insert_non_full(self, node: BPlusNode, key: int) -> None:
        """Insert into non-full node."""
        i = len(node.keys) - 1

        if node.is_leaf:
            # Find position and insert
            node.keys.append(None)
            while i >= 0 and key < node.keys[i]:
                node.keys[i + 1] = node.keys[i]
                i -= 1
            node.keys[i + 1] = key
        else:
            # Find child to recurse
            while i >= 0 and key < node.keys[i]:
                i -= 1
            i += 1

            if node.children[i].is_full():
                self._split_child(node, i)
                if key > node.keys[i]:
                    i += 1

            self._insert_non_full(node.children[i], key)

    def _split_child(self, parent: BPlusNode, idx: int) -> None:
        """Split child at index idx."""
        full_child = parent.children[idx]
        new_child = BPlusNode(is_leaf=full_child.is_leaf, t=self.t)

        mid = self.t - 1

        # Copy keys to new child
        new_child.keys = full_child.keys[mid + 1:]
        full_child.keys = full_child.keys[:mid]

        # If not leaf, copy children
        if not full_child.is_leaf:
            new_child.children = full_child.children[mid + 1:]
            full_child.children = full_child.children[:mid + 1]
        else:
            # Link leaf nodes
            new_child.next = full_child.next
            full_child.next = new_child

        # Move median key to parent
        parent.keys.insert(idx, full_child.keys[mid] if full_child.keys else new_child.keys[0])
        parent.children.insert(idx + 1, new_child)

    def range_search(self, lower: int, upper: int) -> List[int]:
        """Find all keys in range [lower, upper]."""
        result = []
        leaf = self._find_leaf(self.root, lower)

        while leaf:
            for key in leaf.keys:
                if lower <= key <= upper:
                    result.append(key)
                elif key > upper:
                    return result

            leaf = leaf.next

        return result

    def _find_leaf(self, node: BPlusNode, key: int) -> Optional[BPlusNode]:
        """Find leaf that could contain key."""
        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i += 1

        if node.is_leaf:
            return node

        return self._find_leaf(node.children[i], key)

    def delete(self, key: int) -> None:
        """Delete key from tree."""
        self._delete(self.root, key)

        if len(self.root.keys) == 0:
            if not self.root.is_leaf and len(self.root.children) > 0:
                self.root = self.root.children[0]

    def _delete(self, node: BPlusNode, key: int) -> None:
        """Delete key from node (simplified)."""
        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i += 1

        if node.is_leaf:
            if i < len(node.keys) and node.keys[i] == key:
                node.keys.pop(i)
        else:
            if i < len(node.keys) and node.keys[i] == key:
                # Merge children
                if len(node.children[i].keys) >= self.t:
                    node.keys[i] = node.children[i].keys[-1]
                    self._delete(node.children[i], node.keys[i])
                else:
                    self._delete(node.children[i + 1], key)
            else:
                self._delete(node.children[i], key)

    def inorder(self) -> List[int]:
        """Get all keys in order."""
        result = []
        self._inorder(self.root, result)
        return result

    def _inorder(self, node: BPlusNode, result: List[int]) -> None:
        """Inorder traversal."""
        if node.is_leaf:
            result.extend(node.keys)
        else:
            for i in range(len(node.keys)):
                self._inorder(node.children[i], result)
                result.append(node.keys[i])
            self._inorder(node.children[-1], result)


if __name__ == "__main__":
    # Example 1: Basic operations
    print("=== Example 1: Basic B+ Tree Operations ===")
    tree = BPlusTree(t=3)

    keys = [10, 20, 5, 6, 12, 30, 7, 17]
    print(f"Inserting: {keys}")
    for key in keys:
        tree.insert(key)

    print(f"Inorder: {tree.inorder()}")

    for key in keys + [8, 100]:
        print(f"Search {key}: {tree.search(key)}")

    # Example 2: Range search
    print("\n=== Example 2: Range Search ===")
    print(f"Range [5, 20]: {tree.range_search(5, 20)}")
    print(f"Range [7, 15]: {tree.range_search(7, 15)}")

    # Example 3: Larger tree
    print("\n=== Example 3: Larger Tree ===")
    tree2 = BPlusTree(t=3)
    for i in range(1, 21):
        tree2.insert(i)

    print(f"Inorder (1-20): {tree2.inorder()}")
    print(f"Range [5, 15]: {tree2.range_search(5, 15)}")
