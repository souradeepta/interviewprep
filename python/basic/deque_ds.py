"""
Double-Ended Queue (Deque)
==========================
Supports efficient insertion and removal at **both** ends.

Two implementations are provided:

  1. ArrayDeque      -- backed by a resizable circular buffer (plain list).
                        All four push/pop operations are O(1) amortized.
  2. LinkedDeque     -- backed by a doubly linked list.
                        All four push/pop operations are O(1) worst-case.

Time Complexities (both implementations):
  push_front  -- O(1)  amortized (ArrayDeque) / O(1) (LinkedDeque)
  push_back   -- O(1)  amortized / O(1)
  pop_front   -- O(1)  amortized / O(1)
  pop_back    -- O(1)  amortized / O(1)
  peek_front  -- O(1)
  peek_back   -- O(1)
  is_empty    -- O(1)
  size        -- O(1)
"""


# ======================================================================
# Implementation 1 – Circular-buffer Deque
# ======================================================================


class ArrayDeque:
    """
    Double-ended queue backed by a circular buffer (ring array).

    The backing list is allocated at DEFAULT_CAPACITY and doubles when full.
    *_front* always points to the slot that would receive the NEXT push_front,
    ensuring that push_front is O(1) amortized without shifting.

    Internal layout (capacity=8, size=3, front_ptr=5, rear_ptr=0):
        index : 0    1    2    3    4    5    6    7
        data  : C    _    _    _    _    A    B    _
                ^rear                   ^front (logical start)
        logical order: A, B, C
    """

    DEFAULT_CAPACITY = 8

    def __init__(self):
        """Initialize an empty deque.

        Time: O(1)
        """
        self._capacity = self.DEFAULT_CAPACITY
        self._data: list = [None] * self._capacity
        # _front is the index of the FIRST element
        # _rear  is the index one PAST the LAST element
        self._front: int = 0
        self._rear: int = 0
        self._size: int = 0

    # ------------------------------------------------------------------
    # Push
    # ------------------------------------------------------------------

    def push_front(self, val) -> None:
        """Insert *val* at the front of the deque.

        Time: O(1) amortized
        """
        if self._size == self._capacity:
            self._resize(self._capacity * 2)
        self._front = (self._front - 1) % self._capacity
        self._data[self._front] = val
        self._size += 1

    def push_back(self, val) -> None:
        """Insert *val* at the back of the deque.

        Time: O(1) amortized
        """
        if self._size == self._capacity:
            self._resize(self._capacity * 2)
        self._data[self._rear] = val
        self._rear = (self._rear + 1) % self._capacity
        self._size += 1

    # ------------------------------------------------------------------
    # Pop
    # ------------------------------------------------------------------

    def pop_front(self):
        """Remove and return the front element.

        Raises:
            IndexError: if the deque is empty.

        Time: O(1) amortized
        """
        if self.is_empty():
            raise IndexError("pop_front from empty deque")
        val = self._data[self._front]
        self._data[self._front] = None  # help GC
        self._front = (self._front + 1) % self._capacity
        self._size -= 1
        self._shrink_if_needed()
        return val

    def pop_back(self):
        """Remove and return the back element.

        Raises:
            IndexError: if the deque is empty.

        Time: O(1) amortized
        """
        if self.is_empty():
            raise IndexError("pop_back from empty deque")
        self._rear = (self._rear - 1) % self._capacity
        val = self._data[self._rear]
        self._data[self._rear] = None  # help GC
        self._size -= 1
        self._shrink_if_needed()
        return val

    # ------------------------------------------------------------------
    # Peek
    # ------------------------------------------------------------------

    def peek_front(self):
        """Return the front element without removing it.

        Raises:
            IndexError: if the deque is empty.

        Time: O(1)
        """
        if self.is_empty():
            raise IndexError("peek_front from empty deque")
        return self._data[self._front]

    def peek_back(self):
        """Return the back element without removing it.

        Raises:
            IndexError: if the deque is empty.

        Time: O(1)
        """
        if self.is_empty():
            raise IndexError("peek_back from empty deque")
        return self._data[(self._rear - 1) % self._capacity]

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    def is_empty(self) -> bool:
        """Return True if the deque has no elements.

        Time: O(1)
        """
        return self._size == 0

    def size(self) -> int:
        """Return the number of elements.

        Time: O(1)
        """
        return self._size

    def __len__(self) -> int:
        return self._size

    def __str__(self) -> str:
        """Show logical order from front to back.

        Example:
            ArrayDeque FRONT -> [1, 2, 3] <- BACK   size=3  capacity=8
        """
        logical = [
            str(self._data[(self._front + i) % self._capacity])
            for i in range(self._size)
        ]
        return (
            f"ArrayDeque FRONT -> [{', '.join(logical)}] <- BACK   "
            f"size={self._size}  capacity={self._capacity}"
        )

    def __repr__(self) -> str:
        logical = [
            self._data[(self._front + i) % self._capacity]
            for i in range(self._size)
        ]
        return f"ArrayDeque({logical})"

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _resize(self, new_capacity: int) -> None:
        """Re-linearize the circular buffer into a new list of *new_capacity*.

        Time: O(n)
        """
        new_data = [None] * new_capacity
        for i in range(self._size):
            new_data[i] = self._data[(self._front + i) % self._capacity]
        self._data = new_data
        self._front = 0
        self._rear = self._size
        self._capacity = new_capacity

    def _shrink_if_needed(self) -> None:
        """Halve capacity when the array is less than 25% full."""
        min_cap = self.DEFAULT_CAPACITY
        if (
            self._size > 0
            and self._size <= self._capacity // 4
            and self._capacity // 2 >= min_cap
        ):
            self._resize(self._capacity // 2)


# ======================================================================
# Implementation 2 – Doubly-linked-list Deque
# ======================================================================


class _DNode:
    """Internal doubly linked node for LinkedDeque."""

    __slots__ = ("val", "prev", "next")

    def __init__(self, val, prev_node=None, next_node=None):
        self.val = val
        self.prev = prev_node
        self.next = next_node


class LinkedDeque:
    """
    Double-ended queue backed by a doubly linked list with sentinel nodes.

    All four push/pop operations are O(1) worst-case (no amortization needed).
    Preferred when you need strict O(1) guarantees or when memory re-use
    patterns make reallocation costly.
    """

    def __init__(self):
        """Initialize an empty deque.

        Time: O(1)
        """
        self._head = _DNode("SENTINEL_HEAD")
        self._tail = _DNode("SENTINEL_TAIL")
        self._head.next = self._tail
        self._tail.prev = self._head
        self._size = 0

    # ------------------------------------------------------------------
    # Push
    # ------------------------------------------------------------------

    def push_front(self, val) -> None:
        """Insert *val* at the front of the deque.

        Time: O(1)
        """
        self._insert_after(self._head, val)

    def push_back(self, val) -> None:
        """Insert *val* at the back of the deque.

        Time: O(1)
        """
        self._insert_before(self._tail, val)

    # ------------------------------------------------------------------
    # Pop
    # ------------------------------------------------------------------

    def pop_front(self):
        """Remove and return the front element.

        Raises:
            IndexError: if the deque is empty.

        Time: O(1)
        """
        if self.is_empty():
            raise IndexError("pop_front from empty deque")
        node = self._head.next
        self._unlink(node)
        return node.val

    def pop_back(self):
        """Remove and return the back element.

        Raises:
            IndexError: if the deque is empty.

        Time: O(1)
        """
        if self.is_empty():
            raise IndexError("pop_back from empty deque")
        node = self._tail.prev
        self._unlink(node)
        return node.val

    # ------------------------------------------------------------------
    # Peek
    # ------------------------------------------------------------------

    def peek_front(self):
        """Return the front element without removing it.

        Raises:
            IndexError: if the deque is empty.

        Time: O(1)
        """
        if self.is_empty():
            raise IndexError("peek_front from empty deque")
        return self._head.next.val

    def peek_back(self):
        """Return the back element without removing it.

        Raises:
            IndexError: if the deque is empty.

        Time: O(1)
        """
        if self.is_empty():
            raise IndexError("peek_back from empty deque")
        return self._tail.prev.val

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    def is_empty(self) -> bool:
        """Return True if the deque has no elements.

        Time: O(1)
        """
        return self._size == 0

    def size(self) -> int:
        """Return the number of elements.

        Time: O(1)
        """
        return self._size

    def __len__(self) -> int:
        return self._size

    def __str__(self) -> str:
        """Show logical order from front to back."""
        parts = []
        current = self._head.next
        while current is not self._tail:
            parts.append(str(current.val))
            current = current.next
        content = ", ".join(parts) if parts else ""
        return (
            f"LinkedDeque FRONT -> [{content}] <- BACK   size={self._size}"
        )

    def __repr__(self) -> str:
        parts = []
        current = self._head.next
        while current is not self._tail:
            parts.append(current.val)
            current = current.next
        return f"LinkedDeque({parts})"

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _insert_after(self, node: _DNode, val) -> _DNode:
        new_node = _DNode(val, prev_node=node, next_node=node.next)
        node.next.prev = new_node
        node.next = new_node
        self._size += 1
        return new_node

    def _insert_before(self, node: _DNode, val) -> _DNode:
        return self._insert_after(node.prev, val)

    def _unlink(self, node: _DNode) -> None:
        node.prev.next = node.next
        node.next.prev = node.prev
        node.prev = node.next = None
        self._size -= 1


# ======================================================================
# Demo
# ======================================================================

if __name__ == "__main__":
    def demo(cls_name: str, dq) -> None:
        print("=" * 60)
        print(f"{cls_name} Demo")
        print("=" * 60)

        print(f"Initial        : {dq}")
        print(f"is_empty()     : {dq.is_empty()}")

        for v in [10, 20, 30]:
            dq.push_back(v)
            print(f"push_back({v})  : {dq}")

        for v in [5, 1]:
            dq.push_front(v)
            print(f"push_front({v})  : {dq}")

        print(f"\npeek_front()   : {dq.peek_front()}")
        print(f"peek_back()    : {dq.peek_back()}")
        print(f"size()         : {dq.size()}")

        print(f"\npop_front() -> {dq.pop_front():<4}  : {dq}")
        print(f"pop_back()  -> {dq.pop_back():<4}  : {dq}")
        print(f"pop_front() -> {dq.pop_front():<4}  : {dq}")
        print(f"pop_back()  -> {dq.pop_back():<4}  : {dq}")

        print(f"\nRemaining      : {dq}")

        print("\nError handling:")
        while not dq.is_empty():
            dq.pop_front()
        try:
            dq.pop_front()
        except IndexError as e:
            print(f"  pop_front() on empty -> IndexError: {e}")
        try:
            dq.peek_back()
        except IndexError as e:
            print(f"  peek_back() on empty -> IndexError: {e}")
        print()

    demo("ArrayDeque", ArrayDeque())
    demo("LinkedDeque", LinkedDeque())
