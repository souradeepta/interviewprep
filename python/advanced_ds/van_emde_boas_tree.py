"""
Van Emde Boas Tree (VEB Tree)

Time Complexity:
- Insert: O(log log U) where U = universe size
- Delete: O(log log U)
- Search: O(log log U)
- Min/Max: O(1)
- Successor/Predecessor: O(log log U)

Space Complexity: O(U)

Use Cases:
- Dictionary operations on finite universe of integers [0, U)
- When keys are small integers (better than general BSTs)
- Finding next/previous element
- Bit-manipulation heavy algorithms

Key Insight:
- Recursively partition universe into sqrt(U) blocks
- Each block is itself a VEB tree on universe of size sqrt(U)
- Track min/max globally for O(1) access
- Successor search only needs to check one block + recursive call
"""

from typing import Optional, Tuple


class VanEmdoBoasTree:
    """Van Emde Boas Tree for efficient integer operations."""

    def __init__(self, universe_size: int):
        """
        Initialize VEB tree.

        Args:
            universe_size: Size of universe [0, universe_size)
        """
        self.u = universe_size
        self.min = None
        self.max = None

        if universe_size <= 1:
            return

        # Base case: use array for small universes
        if universe_size == 2:
            self.bits = [False] * 2
            return

        self.sqrt_u = int(universe_size ** 0.5) + 1

        # Recursively create structures
        self.summary = VanEmdoBoasTree(self.sqrt_u)
        self.clusters = [VanEmdoBoasTree(self.sqrt_u) for _ in range(self.sqrt_u)]

    def _high(self, x: int) -> int:
        """Get high bits."""
        return x // self.sqrt_u

    def _low(self, x: int) -> int:
        """Get low bits."""
        return x % self.sqrt_u

    def _index(self, high: int, low: int) -> int:
        """Combine high and low bits."""
        return high * self.sqrt_u + low

    def insert(self, x: int) -> None:
        """Insert element x."""
        if x < 0 or x >= self.u:
            return

        if self.u == 1:
            return

        if self.u == 2:
            self.bits[x] = True
            if self.min is None:
                self.min = x
            self.max = x
            return

        # Handle min/max
        if self.min is None:
            self.min = x
            self.max = x
            return

        if x == self.min or x == self.max:
            return  # Already present

        if x < self.min:
            x, self.min = self.min, x

        if x > self.max:
            self.max = x

        high = self._high(x)
        low = self._low(x)

        # Insert into cluster
        if self.clusters[high].min is None:
            self.summary.insert(high)

        self.clusters[high].insert(low)

    def delete(self, x: int) -> None:
        """Delete element x."""
        if x < 0 or x >= self.u:
            return

        if self.u == 1:
            return

        if self.u == 2:
            self.bits[x] = False
            if not self.bits[0] and not self.bits[1]:
                self.min = None
                self.max = None
            elif self.bits[0]:
                self.min = self.max = 0
            else:
                self.min = self.max = 1
            return

        if self.min == self.max == x:
            self.min = None
            self.max = None
            return

        if x == self.min:
            # Find next element
            first_cluster = self.summary.min
            if first_cluster is not None:
                x = self._index(first_cluster, self.clusters[first_cluster].min)
            self.min = x
            self.max = x if self.min == self.max else self.max
            return

        high = self._high(x)
        low = self._low(x)

        self.clusters[high].delete(low)

        if self.clusters[high].min is None:
            self.summary.delete(high)

    def member(self, x: int) -> bool:
        """Check if x is in tree."""
        if x < 0 or x >= self.u:
            return False

        if x == self.min or x == self.max:
            return True

        if self.u == 1:
            return False

        if self.u == 2:
            return self.bits[x]

        high = self._high(x)
        low = self._low(x)

        return self.clusters[high].member(low)

    def successor(self, x: int) -> Optional[int]:
        """Find successor of x."""
        if self.u == 1:
            return None

        if self.u == 2:
            if x < 1 and self.bits[1]:
                return 1
            return None

        if x < self.min:
            return self.min

        if x >= self.max:
            return None

        high = self._high(x)
        low = self._low(x)

        # Check if successor is in same cluster
        if low < self.clusters[high].max:
            return self._index(high, self.clusters[high].successor(low))

        # Find next non-empty cluster
        next_cluster = self.summary.successor(high)
        if next_cluster is None:
            return None

        return self._index(next_cluster, self.clusters[next_cluster].min)

    def predecessor(self, x: int) -> Optional[int]:
        """Find predecessor of x."""
        if self.u == 1:
            return None

        if self.u == 2:
            if x > 0 and self.bits[0]:
                return 0
            return None

        if x > self.max:
            return self.max

        if x <= self.min:
            return None

        high = self._high(x)
        low = self._low(x)

        # Check if predecessor is in same cluster
        if low > self.clusters[high].min:
            return self._index(high, self.clusters[high].predecessor(low))

        # Find previous non-empty cluster
        prev_cluster = self.summary.predecessor(high)
        if prev_cluster is None:
            return self.min if self.min < x else None

        return self._index(prev_cluster, self.clusters[prev_cluster].max)


if __name__ == "__main__":
    # Example 1: Basic operations
    print("=== Example 1: Basic Operations ===")
    veb = VanEmdoBoasTree(16)

    elements = [1, 3, 5, 7, 9, 12, 14]
    print(f"Inserting: {elements}")
    for elem in elements:
        veb.insert(elem)

    print(f"Min: {veb.min}, Max: {veb.max}")

    for x in [0, 3, 5, 8, 14]:
        print(f"{x} in tree: {veb.member(x)}")

    # Example 2: Successor/Predecessor
    print("\n=== Example 2: Successor/Predecessor ===")
    for x in [3, 5, 7, 12, 15]:
        succ = veb.successor(x)
        pred = veb.predecessor(x)
        print(f"x={x}: successor={succ}, predecessor={pred}")

    # Example 3: Deletion
    print("\n=== Example 3: Deletion ===")
    print(f"Deleting 5...")
    veb.delete(5)
    print(f"5 in tree: {veb.member(5)}")
    print(f"Successor of 3: {veb.successor(3)}")

    # Example 4: Larger universe
    print("\n=== Example 4: Larger Universe (U=256) ===")
    veb2 = VanEmdoBoasTree(256)
    elements2 = [10, 50, 100, 150, 200, 250]
    for elem in elements2:
        veb2.insert(elem)

    print(f"Elements: {elements2}")
    print(f"Min: {veb2.min}, Max: {veb2.max}")
    print(f"Successor of 100: {veb2.successor(100)}")
    print(f"Predecessor of 150: {veb2.predecessor(150)}")
