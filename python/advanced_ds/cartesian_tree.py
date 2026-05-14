"""
Cartesian Tree (Min/Max + RMQ)

Time Complexity:
- Construction: O(n) using stack-based algorithm
- RMQ Query: O(log n) or O(1) with preprocessing (LCA)
- Space Complexity: O(n)

Use Cases:
- Range Minimum Query (RMQ)
- Range Maximum Query
- Finding nearest smaller/larger element
- Lowest Common Ancestor queries
- Split representation for persistent structures

Key Insight:
- BST on values with heap property on array indices
- Subtree root is minimum element in range
- Linear construction with stack
- Can be converted to RMQ via LCA reduction
- Each element has unique position: left subtree = elements to left, smaller than root
"""

from typing import List, Optional, Tuple


class CartesianNode:
    """Node in Cartesian tree."""

    def __init__(self, val: int, idx: int):
        self.val = val
        self.idx = idx
        self.left = None
        self.right = None
        self.parent = None


class CartesianTree:
    """Cartesian tree for efficient RMQ."""

    def __init__(self, arr: List[int]):
        """
        Build Cartesian tree from array.

        Args:
            arr: Input array
        """
        self.arr = arr
        self.n = len(arr)
        self.root = self._build_tree(arr) if arr else None

    def _build_tree(self, arr: List[int]) -> Optional[CartesianNode]:
        """Build tree using stack in O(n) time."""
        if not arr:
            return None

        stack = []
        root = None

        for i, val in enumerate(arr):
            node = CartesianNode(val, i)
            last_popped = None

            # Pop elements greater than current
            while stack and stack[-1].val > val:
                last_popped = stack.pop()

            # If we popped something, it becomes left child
            if last_popped:
                node.left = last_popped
                last_popped.parent = node

            # Current node becomes right child of stack top
            if stack:
                stack[-1].right = node
                node.parent = stack[-1]
            else:
                root = node

            stack.append(node)

        return root

    def query_min(self, l: int, r: int) -> int:
        """Find minimum value in range [l, r]."""
        if l > r or l < 0 or r >= self.n:
            return float('inf')

        return self._query_min(self.root, l, r)

    def _query_min(self, node: Optional[CartesianNode], l: int, r: int) -> int:
        """Recursive RMQ query."""
        if node is None:
            return float('inf')

        # If node is outside range, skip it
        if node.idx < l or node.idx > r:
            if node.idx < l:
                return self._query_min(node.right, l, r)
            else:
                return self._query_min(node.left, l, r)

        # Node is in range - check both subtrees
        left_min = self._query_min(node.left, l, r)
        right_min = self._query_min(node.right, l, r)

        return min(node.val, left_min, right_min)

    def query_max(self, l: int, r: int) -> int:
        """Find maximum value in range [l, r]."""
        if l > r or l < 0 or r >= self.n:
            return float('-inf')

        return self._query_max(self.root, l, r)

    def _query_max(self, node: Optional[CartesianNode], l: int, r: int) -> int:
        """Recursive max query."""
        if node is None:
            return float('-inf')

        if node.idx < l or node.idx > r:
            if node.idx < l:
                return self._query_max(node.right, l, r)
            else:
                return self._query_max(node.left, l, r)

        left_max = self._query_max(node.left, l, r)
        right_max = self._query_max(node.right, l, r)

        return max(node.val, left_max, right_max)

    def nearest_smaller_left(self, idx: int) -> int:
        """Find nearest smaller element to the left."""
        if idx <= 0:
            return -1

        # In Cartesian tree, parent is always smaller than children in range
        # This is more complex - simplified version: linear search
        for i in range(idx - 1, -1, -1):
            if self.arr[i] < self.arr[idx]:
                return i

        return -1

    def nearest_larger_left(self, idx: int) -> int:
        """Find nearest larger element to the left."""
        if idx <= 0:
            return -1

        for i in range(idx - 1, -1, -1):
            if self.arr[i] > self.arr[idx]:
                return i

        return -1

    def inorder(self) -> List[int]:
        """Get inorder traversal."""
        result = []
        self._inorder(self.root, result)
        return result

    def _inorder(self, node: Optional[CartesianNode], result: List[int]) -> None:
        """Inorder traversal."""
        if node:
            self._inorder(node.left, result)
            result.append(node.val)
            self._inorder(node.right, result)

    def preorder(self) -> List[Tuple[int, int]]:
        """Get preorder traversal (val, idx)."""
        result = []
        self._preorder(self.root, result)
        return result

    def _preorder(self, node: Optional[CartesianNode], result: List) -> None:
        """Preorder traversal showing structure."""
        if node:
            result.append((node.val, node.idx))
            self._preorder(node.left, result)
            self._preorder(node.right, result)


if __name__ == "__main__":
    # Example 1: RMQ on simple array
    print("=== Example 1: Range Minimum Query ===")
    arr = [7, 3, 9, 2, 5, 1, 8]
    tree = CartesianTree(arr)

    print(f"Array: {arr}")
    print(f"Preorder (structure): {tree.preorder()}")

    queries = [(0, 4), (1, 5), (2, 6), (0, 6)]
    for l, r in queries:
        min_val = tree.query_min(l, r)
        print(f"Min in [{l}, {r}]: {min_val}")

    # Example 2: Range maximum query
    print("\n=== Example 2: Range Maximum Query ===")
    for l, r in queries:
        max_val = tree.query_max(l, r)
        print(f"Max in [{l}, {r}]: {max_val}")

    # Example 3: Nearest smaller
    print("\n=== Example 3: Nearest Smaller Left ===")
    arr2 = [1, 5, 0, 3, 4, 5]
    tree2 = CartesianTree(arr2)

    print(f"Array: {arr2}")
    for i in range(len(arr2)):
        idx = tree2.nearest_smaller_left(i)
        print(f"Element {arr2[i]} at index {i}: nearest smaller left = {idx}")

    # Example 4: Larger array
    print("\n=== Example 4: Larger Array ===")
    arr3 = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]
    tree3 = CartesianTree(arr3)

    print(f"Array: {arr3}")
    print(f"Min in [2, 8]: {tree3.query_min(2, 8)}")
    print(f"Max in [2, 8]: {tree3.query_max(2, 8)}")
    print(f"Min in [0, 4]: {tree3.query_min(0, 4)}")
