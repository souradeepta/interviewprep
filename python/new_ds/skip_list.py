"""
Skip List
=========
A probabilistic data structure that allows O(log n) average-case search,
insertion, and deletion by maintaining multiple layers of linked lists.

Structure
---------
- Level 0 is the base linked list containing all elements in sorted order.
- Each higher level is a "fast lane" that skips over increasingly many elements.
- A new node is promoted to level k with probability p^k (geometric distribution).

Time Complexity (average case, with p=0.5)
-------------------------------------------
| Operation | Average   | Worst    |
|-----------|-----------|----------|
| search    | O(log n)  | O(n)     |
| insert    | O(log n)  | O(n)     |
| delete    | O(log n)  | O(n)     |

Space Complexity
----------------
- O(n) average (each node appears in ~1/(1-p) levels on average)
- O(n log n) worst case

Why O(log n) average?
---------------------
With p=0.5, the expected number of nodes examined at each level is 2,
and there are O(log n) levels, giving O(log n) total comparisons.
"""

import random
from typing import Any, List, Optional

MAX_LEVEL = 16  # maximum number of levels in the skip list
P = 0.5         # probability of promoting a node to the next level


class SkipListNode:
    """
    A node in the Skip List.

    Attributes
    ----------
    key   : Comparable key used for ordering.
    val   : Associated value stored at this node.
    forward : List of forward pointers, one per level this node occupies.
              forward[0] is the next node at level 0 (base list).
    """

    def __init__(self, key: Any, val: Any, level: int) -> None:
        self.key = key
        self.val = val
        # forward[i] points to the next node at level i; None means end of level
        self.forward: List[Optional["SkipListNode"]] = [None] * (level + 1)

    def __repr__(self) -> str:
        return f"SkipListNode(key={self.key!r}, val={self.val!r}, levels={len(self.forward)})"


class SkipList:
    """
    Skip List with randomized level assignment.

    Maintains keys in sorted order across multiple levels of linked lists.
    The head sentinel node spans all MAX_LEVEL levels.

    Parameters
    ----------
    max_level : int  Maximum number of levels (default MAX_LEVEL=16).
    p         : float  Probability of level promotion (default P=0.5).

    Example
    -------
    >>> sl = SkipList()
    >>> sl.insert(3, "three")
    >>> sl.insert(1, "one")
    >>> sl.search(3)
    'three'
    >>> sl.delete(1)
    >>> sl.search(1) is None
    True
    """

    def __init__(self, max_level: int = MAX_LEVEL, p: float = P) -> None:
        self.max_level = max_level
        self.p = p
        self.current_level = 0  # highest level currently in use (0-indexed)
        self.size = 0
        # Sentinel head node with -inf key; never holds real data
        self._head = SkipListNode(key=float("-inf"), val=None, level=max_level)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _random_level(self) -> int:
        """
        Generate a random level for a new node.

        Flips a coin (probability p) repeatedly; the number of heads
        before the first tail determines the level (capped at max_level).

        Time: O(log n) expected
        """
        level = 0
        while random.random() < self.p and level < self.max_level:
            level += 1
        return level

    def _find_update_positions(self, key: Any) -> List[Optional[SkipListNode]]:
        """
        Walk down from the highest level, collecting the last node at each
        level whose key is strictly less than `key`.

        These are the nodes whose forward pointers must be updated during
        insert or delete.

        Returns
        -------
        update : list of length (max_level + 1) where update[i] is the
                 rightmost node at level i with node.key < key.
        """
        update: List[Optional[SkipListNode]] = [None] * (self.max_level + 1)
        current = self._head
        for i in range(self.current_level, -1, -1):
            while current.forward[i] is not None and current.forward[i].key < key:
                current = current.forward[i]
            update[i] = current
        return update

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def insert(self, key: Any, val: Any) -> None:
        """
        Insert or update a key-value pair.

        If `key` already exists its value is overwritten; otherwise a new
        node is created with a randomly assigned level.

        Time:  O(log n) average
        Space: O(log n) for the new node's forward array
        """
        update = self._find_update_positions(key)
        # Check if key already exists at level 0
        candidate = update[0].forward[0] if update[0] is not None else None
        if candidate is not None and candidate.key == key:
            candidate.val = val  # update existing
            return

        new_level = self._random_level()
        # If new node exceeds current height, extend update for new levels
        if new_level > self.current_level:
            for i in range(self.current_level + 1, new_level + 1):
                update[i] = self._head
            self.current_level = new_level

        new_node = SkipListNode(key=key, val=val, level=new_level)
        for i in range(new_level + 1):
            new_node.forward[i] = update[i].forward[i]
            update[i].forward[i] = new_node

        self.size += 1

    def search(self, key: Any) -> Optional[Any]:
        """
        Search for a key and return its associated value, or None if absent.

        Time: O(log n) average
        """
        current = self._head
        for i in range(self.current_level, -1, -1):
            while current.forward[i] is not None and current.forward[i].key < key:
                current = current.forward[i]
        # One step forward at level 0 lands on the candidate
        current = current.forward[0]
        if current is not None and current.key == key:
            return current.val
        return None

    def delete(self, key: Any) -> bool:
        """
        Delete the node with the given key.

        Returns True if the node was found and deleted, False otherwise.

        Time: O(log n) average
        """
        update = self._find_update_positions(key)
        target = update[0].forward[0] if update[0] is not None else None
        if target is None or target.key != key:
            return False  # key not present

        # Splice out the target node at every level it appears
        for i in range(self.current_level + 1):
            if update[i].forward[i] is not target:
                break
            update[i].forward[i] = target.forward[i]

        # Shrink current_level if the top levels are now empty
        while self.current_level > 0 and self._head.forward[self.current_level] is None:
            self.current_level -= 1

        self.size -= 1
        return True

    def __len__(self) -> int:
        return self.size

    def __contains__(self, key: Any) -> bool:
        return self.search(key) is not None

    def __str__(self) -> str:
        """
        Display all levels of the Skip List from top to bottom.

        Example output:
            Level 3: -inf --> 3 --> 7
            Level 2: -inf --> 1 --> 3 --> 7
            Level 1: -inf --> 1 --> 2 --> 3 --> 5 --> 7
            Level 0: -inf --> 1 --> 2 --> 3 --> 5 --> 7
        """
        lines = []
        for level in range(self.current_level, -1, -1):
            nodes = []
            current = self._head
            while current is not None:
                label = "-inf" if current is self._head else str(current.key)
                nodes.append(label)
                current = current.forward[level]
            lines.append(f"Level {level}: " + " --> ".join(nodes))
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import time

    print("=" * 60)
    print("SKIP LIST DEMO")
    print("=" * 60)

    sl = SkipList()

    # --- Basic insert and search ---
    data = [(5, "five"), (1, "one"), (9, "nine"), (3, "three"),
            (7, "seven"), (2, "two"), (8, "eight"), (4, "four"), (6, "six")]
    for k, v in data:
        sl.insert(k, v)

    print("\nAll levels after inserting 1..9:")
    print(sl)

    print(f"\nsearch(5)  -> {sl.search(5)!r}")
    print(f"search(10) -> {sl.search(10)!r}  (not present)")

    # --- Update existing key ---
    sl.insert(5, "FIVE_UPDATED")
    print(f"After update: search(5) -> {sl.search(5)!r}")

    # --- Delete ---
    sl.delete(3)
    sl.delete(7)
    print(f"\nAfter deleting 3 and 7:")
    print(sl)
    print(f"search(3) -> {sl.search(3)!r}  (deleted)")

    # --- O(log n) average search demonstration ---
    print("\n--- O(log n) average search benchmark ---")
    big_sl = SkipList()
    N = 100_000
    keys = list(range(N))
    random.shuffle(keys)
    for k in keys:
        big_sl.insert(k, k * 2)

    # Time a batch of searches
    search_keys = random.sample(range(N), 1000)
    start = time.perf_counter()
    for k in search_keys:
        big_sl.search(k)
    elapsed = time.perf_counter() - start
    print(f"1 000 searches in a Skip List of {N:,} elements: {elapsed*1000:.2f} ms")
    print(f"Average per search: {elapsed/1000*1e6:.2f} µs  (expected O(log {N}) ≈ {N.bit_length()} comparisons)")

    print("\nDone.")
