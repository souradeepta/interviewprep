"""
Fibonacci Heap

Time Complexity (Amortized):
- Insert: O(1)
- Find Min: O(1)
- Delete Min: O(log n)
- Decrease Key: O(1)
- Delete: O(log n)
- Merge: O(1)

Space Complexity: O(n)

Use Cases:
- Dijkstra's algorithm (faster for sparse graphs)
- Prim's algorithm
- Dynamic connectivity
- Network algorithms with decrease-key

Key Insight:
- Collection of min-heaps organized as forest of Fibonacci trees
- O(1) decrease-key via cascading cuts
- Lazy consolidation in delete-min
- Better amortized complexity than binary heaps for key operations
- Not practical for small inputs due to high constants
"""

from typing import Optional, List
import math


class FibonacciNode:
    """Node in Fibonacci heap."""

    def __init__(self, key):
        self.key = key
        self.parent = None
        self.child = None
        self.left = self
        self.right = self
        self.degree = 0
        self.marked = False


class FibonacciHeap:
    """Fibonacci heap for efficient merge and decrease-key."""

    def __init__(self):
        self.min = None
        self.num_nodes = 0

    def insert(self, key) -> FibonacciNode:
        """Insert key and return node."""
        new_node = FibonacciNode(key)
        self.num_nodes += 1

        if self.min is None:
            self.min = new_node
        else:
            self._link(self.min, new_node)
            if new_node.key < self.min.key:
                self.min = new_node

        return new_node

    def find_min(self) -> Optional[int]:
        """Find minimum element."""
        return self.min.key if self.min else None

    def merge(self, other: 'FibonacciHeap') -> None:
        """Merge with another Fibonacci heap."""
        if other.min is None:
            return

        if self.min is None:
            self.min = other.min
            self.num_nodes = other.num_nodes
        else:
            self._link(self.min, other.min)
            if other.min.key < self.min.key:
                self.min = other.min
            self.num_nodes += other.num_nodes

    def delete_min(self) -> Optional[int]:
        """Delete and return minimum element."""
        if self.min is None:
            return None

        min_val = self.min.key

        # Remove min from root list
        if self.min.right == self.min:
            self.min = None
        else:
            self._remove_from_list(self.min)
            self.min = self.min.right

        # Add all children to root list
        if self.min is not None:
            node = self.min.child
            if node is not None:
                child_list = []
                current = node
                while True:
                    child_list.append(current)
                    current = current.right
                    if current == node:
                        break

                for child in child_list:
                    child.parent = None
                    self._link(self.min, child)

            # Consolidate
            self._consolidate()

        self.num_nodes -= 1
        return min_val

    def decrease_key(self, node: FibonacciNode, new_key) -> None:
        """Decrease key of node (must be <= current key)."""
        if new_key > node.key:
            raise ValueError("New key is greater than current key")

        node.key = new_key

        if node.parent is None:
            if new_key < self.min.key:
                self.min = node
        else:
            if node.key < node.parent.key:
                self._cut(node, node.parent)
                self._cascading_cut(node.parent)

    def delete(self, node: FibonacciNode) -> None:
        """Delete a node."""
        self.decrease_key(node, float('-inf'))
        self.delete_min()

    def _link(self, a: FibonacciNode, b: FibonacciNode) -> None:
        """Link two nodes in root list."""
        a.right.left = b
        b.right = a.right
        a.right = b
        b.left = a

    def _remove_from_list(self, node: FibonacciNode) -> None:
        """Remove node from circular doubly-linked list."""
        node.left.right = node.right
        node.right.left = node.left

    def _consolidate(self) -> None:
        """Consolidate root list."""
        max_degree = int(math.log2(self.num_nodes)) + 1
        degree_table = [None] * (max_degree + 1)

        # Process each node in root list
        node = self.min
        if node is None:
            return

        root_list = []
        current = node
        while True:
            root_list.append(current)
            current = current.right
            if current == node:
                break

        for root in root_list:
            degree = root.degree
            while degree_table[degree] is not None:
                other = degree_table[degree]
                if root.key > other.key:
                    root, other = other, root

                self._heapify_link(root, other)
                degree_table[degree] = None
                degree += 1

            degree_table[degree] = root

        self.min = None
        for i in range(len(degree_table)):
            if degree_table[i] is not None:
                if self.min is None:
                    self.min = degree_table[i]
                    self.min.left = self.min
                    self.min.right = self.min
                else:
                    self._link(self.min, degree_table[i])
                    if degree_table[i].key < self.min.key:
                        self.min = degree_table[i]

    def _heapify_link(self, parent: FibonacciNode, child: FibonacciNode) -> None:
        """Link child to parent."""
        self._remove_from_list(child)

        if parent.child is None:
            parent.child = child
            child.left = child
            child.right = child
        else:
            self._link(parent.child, child)

        child.parent = parent
        parent.degree += 1
        child.marked = False

    def _cut(self, node: FibonacciNode, parent: FibonacciNode) -> None:
        """Cut node from parent."""
        if parent.child == node:
            if node.right == node:
                parent.child = None
            else:
                parent.child = node.right

        self._remove_from_list(node)
        self._link(self.min, node)
        node.parent = None
        node.marked = False

    def _cascading_cut(self, node: FibonacciNode) -> None:
        """Cascading cut for amortized analysis."""
        while node.parent is not None:
            if not node.marked:
                node.marked = True
                return
            else:
                parent = node.parent
                self._cut(node, parent)
                node = parent


if __name__ == "__main__":
    # Example 1: Basic operations
    print("=== Example 1: Basic Operations ===")
    fib = FibonacciHeap()

    elements = [7, 3, 9, 1, 5, 11, 2]
    print(f"Inserting: {elements}")
    nodes = {}
    for elem in elements:
        nodes[elem] = fib.insert(elem)

    print(f"Min: {fib.find_min()}")

    print("\nExtract min in order:")
    while fib.min is not None:
        print(f"  {fib.delete_min()}")

    # Example 2: Decrease key
    print("\n=== Example 2: Decrease Key ===")
    fib2 = FibonacciHeap()
    nodes2 = {}
    for x in [10, 20, 30, 40, 50]:
        nodes2[x] = fib2.insert(x)

    print(f"Initial min: {fib2.find_min()}")

    print("Decrease 40 to 5")
    fib2.decrease_key(nodes2[40], 5)
    print(f"New min: {fib2.find_min()}")

    print("Decrease 50 to 3")
    fib2.decrease_key(nodes2[50], 3)
    print(f"New min: {fib2.find_min()}")

    # Example 3: Merge
    print("\n=== Example 3: Heap Merge ===")
    fib3a = FibonacciHeap()
    fib3b = FibonacciHeap()

    for x in [1, 5, 9]:
        fib3a.insert(x)
    for x in [2, 3, 7]:
        fib3b.insert(x)

    print(f"Heap A min: {fib3a.find_min()}")
    print(f"Heap B min: {fib3b.find_min()}")

    fib3a.merge(fib3b)
    print(f"After merge min: {fib3a.find_min()}")
