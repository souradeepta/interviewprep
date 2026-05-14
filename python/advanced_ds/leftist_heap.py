"""
Leftist Heap (Leftist Tree)

Time Complexity:
- Insert: O(log n)
- Delete Min: O(log n)
- Merge: O(log n) amortized
- Find Min: O(1)

Space Complexity: O(n)

Use Cases:
- Mergeable priority queue
- Heap merge operations
- Dijkstra's algorithm with merge operation
- Scheduling problems

Key Insight:
- Merge-based heap (vs. array-based binary heap)
- Left path always >= right path (guarantees log n height)
- Efficiently merge two heaps
- Can implement in-place without array reallocation
- Null path length: min dist from node to None node in right-heavy subtree
"""

from typing import Optional, Tuple
from dataclasses import dataclass


@dataclass
class LeftistNode:
    """Node in leftist heap."""
    key: int
    left: Optional['LeftistNode'] = None
    right: Optional['LeftistNode'] = None
    npl: int = 0  # Null path length

    def update_npl(self):
        """Update null path length."""
        right_npl = self.right.npl if self.right else -1
        self.npl = right_npl + 1


class LeftistHeap:
    """Min-heap with efficient merge operation."""

    def __init__(self):
        self.root = None

    def insert(self, key: int) -> None:
        """Insert key into heap."""
        new_node = LeftistNode(key)
        self.root = self._merge(self.root, new_node)

    def merge(self, other: 'LeftistHeap') -> None:
        """Merge with another leftist heap."""
        self.root = self._merge(self.root, other.root)

    def _merge(self, h1: Optional[LeftistNode], h2: Optional[LeftistNode]) -> Optional[LeftistNode]:
        """Merge two heaps."""
        if h1 is None:
            return h2
        if h2 is None:
            return h1

        # Ensure h1.key <= h2.key
        if h1.key > h2.key:
            h1, h2 = h2, h1

        # Recursively merge h2 with h1's right subtree
        h1.right = self._merge(h1.right, h2)

        # Swap left and right to maintain leftist property
        if h1.left is None:
            h1.left, h1.right = h1.right, h1.left
        elif h1.right and h1.left.npl < h1.right.npl:
            h1.left, h1.right = h1.right, h1.left

        # Update null path length
        h1.update_npl()

        return h1

    def delete_min(self) -> Optional[int]:
        """Delete and return minimum element."""
        if self.root is None:
            return None

        min_val = self.root.key
        self.root = self._merge(self.root.left, self.root.right)
        return min_val

    def find_min(self) -> Optional[int]:
        """Find minimum element without deleting."""
        return self.root.key if self.root else None

    def is_empty(self) -> bool:
        """Check if heap is empty."""
        return self.root is None

    def size(self) -> int:
        """Get size of heap."""
        return self._size(self.root)

    def _size(self, node: Optional[LeftistNode]) -> int:
        """Recursively count nodes."""
        if node is None:
            return 0
        return 1 + self._size(node.left) + self._size(node.right)

    def inorder(self) -> list:
        """Get elements in inorder (not necessarily sorted)."""
        result = []
        self._inorder(self.root, result)
        return result

    def _inorder(self, node: Optional[LeftistNode], result: list) -> None:
        """Inorder traversal."""
        if node:
            self._inorder(node.left, result)
            result.append(node.key)
            self._inorder(node.right, result)


if __name__ == "__main__":
    # Example 1: Basic operations
    print("=== Example 1: Basic Operations ===")
    heap = LeftistHeap()

    elements = [7, 3, 9, 1, 5, 11, 2]
    print(f"Inserting: {elements}")
    for elem in elements:
        heap.insert(elem)

    print(f"Min: {heap.find_min()}")
    print(f"Size: {heap.size()}")

    print("\nExtract min in order:")
    while not heap.is_empty():
        print(f"  {heap.delete_min()}")

    # Example 2: Heap merge
    print("\n=== Example 2: Heap Merge ===")
    heap1 = LeftistHeap()
    heap2 = LeftistHeap()

    for x in [1, 5, 9]:
        heap1.insert(x)

    for x in [2, 3, 7]:
        heap2.insert(x)

    print(f"Heap 1: {sorted(heap1.inorder())}")
    print(f"Heap 2: {sorted(heap2.inorder())}")

    heap1.merge(heap2)
    print(f"After merge: {sorted(heap1.inorder())}")
    print(f"Min: {heap1.find_min()}")

    # Example 3: Large scale operations
    print("\n=== Example 3: Delete Min Operations ===")
    heap3 = LeftistHeap()
    elements3 = [15, 10, 20, 8, 2, 16]
    for elem in elements3:
        heap3.insert(elem)

    print(f"Initial size: {heap3.size()}")
    while not heap3.is_empty():
        print(f"Delete min: {heap3.delete_min()}, Size: {heap3.size()}")
