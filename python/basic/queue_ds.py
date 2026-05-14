"""
Queue and Circular Queue
========================
Two queue implementations:

  1. Queue          -- backed by collections.deque for O(1) enqueue/dequeue.
  2. CircularQueue  -- fixed-size ring buffer using a plain list; classic for
                       producer-consumer problems and OS scheduling interviews.

Time Complexities:
  enqueue  -- O(1)
  dequeue  -- O(1)
  peek     -- O(1)
  is_empty -- O(1)
  size     -- O(1)
"""

from collections import deque


# ======================================================================
# Implementation 1 – deque-backed Queue
# ======================================================================


class Queue:
    """
    First-In, First-Out (FIFO) queue backed by collections.deque.

    deque provides O(1) append (right) and popleft (left) operations,
    making it the idiomatic choice for queues in Python.
    """

    def __init__(self):
        """Initialize an empty queue.

        Time: O(1)
        """
        self._data: deque = deque()

    def enqueue(self, val) -> None:
        """Add *val* to the back of the queue.

        Time: O(1)
        """
        self._data.append(val)

    def dequeue(self):
        """Remove and return the front element.

        Raises:
            IndexError: if the queue is empty.

        Time: O(1)
        """
        if self.is_empty():
            raise IndexError("dequeue from empty queue")
        return self._data.popleft()

    def peek(self):
        """Return the front element without removing it.

        Raises:
            IndexError: if the queue is empty.

        Time: O(1)
        """
        if self.is_empty():
            raise IndexError("peek from empty queue")
        return self._data[0]

    def is_empty(self) -> bool:
        """Return True if the queue contains no elements.

        Time: O(1)
        """
        return len(self._data) == 0

    def size(self) -> int:
        """Return the number of elements in the queue.

        Time: O(1)
        """
        return len(self._data)

    def __len__(self) -> int:
        return self.size()

    def __str__(self) -> str:
        """Visualize the queue from front to back.

        Example:
            Queue FRONT -> [1, 2, 3] <- BACK   size=3
        """
        return f"Queue FRONT -> {list(self._data)} <- BACK   size={self.size()}"

    def __repr__(self) -> str:
        return f"Queue({list(self._data)})"


# ======================================================================
# Implementation 2 – Fixed-size Circular Queue (Ring Buffer)
# ======================================================================


class CircularQueue:
    """
    Fixed-size circular queue implemented as a ring buffer over a plain list.

    Two index pointers, *_front* and *_rear*, advance modulo *capacity*,
    avoiding any shifting of elements.  This is the classic implementation
    asked about in OS, embedded, and system-design interviews.

    Attributes:
        _data     : fixed-size backing list
        _capacity : maximum number of elements (user-supplied)
        _front    : index of the front element
        _rear     : index where the next element will be written
        _size     : current number of elements stored
    """

    def __init__(self, capacity: int):
        """Initialize a circular queue that can hold up to *capacity* elements.

        Args:
            capacity: maximum number of elements; must be >= 1.

        Raises:
            ValueError: if *capacity* < 1.

        Time: O(1)
        """
        if capacity < 1:
            raise ValueError("Capacity must be at least 1")
        self._capacity = capacity
        self._data: list = [None] * capacity
        self._front: int = 0   # index of the next element to dequeue
        self._rear: int = 0    # index where the next element will be enqueued
        self._size: int = 0

    def enqueue(self, val) -> None:
        """Add *val* to the back of the queue.

        Raises:
            OverflowError: if the queue is full.

        Time: O(1)
        """
        if self.is_full():
            raise OverflowError("enqueue into full circular queue")
        self._data[self._rear] = val
        self._rear = (self._rear + 1) % self._capacity
        self._size += 1

    def dequeue(self):
        """Remove and return the front element.

        Raises:
            IndexError: if the queue is empty.

        Time: O(1)
        """
        if self.is_empty():
            raise IndexError("dequeue from empty circular queue")
        val = self._data[self._front]
        self._data[self._front] = None  # help GC
        self._front = (self._front + 1) % self._capacity
        self._size -= 1
        return val

    def peek(self):
        """Return the front element without removing it.

        Raises:
            IndexError: if the queue is empty.

        Time: O(1)
        """
        if self.is_empty():
            raise IndexError("peek from empty circular queue")
        return self._data[self._front]

    def is_empty(self) -> bool:
        """Return True if the queue has no elements.

        Time: O(1)
        """
        return self._size == 0

    def is_full(self) -> bool:
        """Return True if the queue has reached maximum capacity.

        Time: O(1)
        """
        return self._size == self._capacity

    def size(self) -> int:
        """Return the current number of elements.

        Time: O(1)
        """
        return self._size

    def capacity(self) -> int:
        """Return the maximum capacity.

        Time: O(1)
        """
        return self._capacity

    def __len__(self) -> int:
        return self.size()

    def __str__(self) -> str:
        """Show the raw backing array and logical order.

        Example (capacity=5, front=2, rear=0, size=3):
            CircularQueue raw=[_, _, 10, 20, 30]  front=2 rear=0 size=3/5
            logical FRONT -> [10, 20, 30] <- BACK
        """
        raw = [str(x) if x is not None else "_" for x in self._data]
        logical = []
        for i in range(self._size):
            logical.append(str(self._data[(self._front + i) % self._capacity]))
        lines = [
            f"CircularQueue raw=[{', '.join(raw)}]  "
            f"front={self._front} rear={self._rear} size={self._size}/{self._capacity}",
            f"  logical FRONT -> [{', '.join(logical)}] <- BACK",
        ]
        return "\n".join(lines)

    def __repr__(self) -> str:
        logical = [
            self._data[(self._front + i) % self._capacity]
            for i in range(self._size)
        ]
        return f"CircularQueue({logical}, capacity={self._capacity})"


# ======================================================================
# Demo
# ======================================================================

if __name__ == "__main__":
    # ------------------------------------------------------------------ #
    # deque-backed Queue
    # ------------------------------------------------------------------ #
    print("=" * 60)
    print("Queue (deque-backed) Demo")
    print("=" * 60)

    q = Queue()
    print(f"Initial        : {q}")
    print(f"is_empty()     : {q.is_empty()}")

    for v in [1, 2, 3, 4, 5]:
        q.enqueue(v)
        print(f"enqueue({v})     : {q}")

    print(f"\npeek()         : {q.peek()}")
    print(f"size()         : {q.size()}")

    while not q.is_empty():
        print(f"dequeue() -> {q.dequeue():<3}  : {q}")

    print("\nError handling:")
    try:
        q.dequeue()
    except IndexError as e:
        print(f"  dequeue() on empty -> IndexError: {e}")

    # ------------------------------------------------------------------ #
    # Circular Queue
    # ------------------------------------------------------------------ #
    print()
    print("=" * 60)
    print("CircularQueue (ring buffer, capacity=5) Demo")
    print("=" * 60)

    cq = CircularQueue(capacity=5)
    print(f"Initial:\n{cq}\n")

    for v in [10, 20, 30]:
        cq.enqueue(v)
        print(f"enqueue({v}):\n{cq}\n")

    print(f"dequeue() -> {cq.dequeue()}")
    print(f"dequeue() -> {cq.dequeue()}")
    print(f"After two dequeues:\n{cq}\n")

    # Wrap-around: enqueue more to demonstrate ring behavior
    for v in [40, 50, 60, 70]:
        cq.enqueue(v)
        print(f"enqueue({v}) (wrap-around):\n{cq}\n")

    print(f"is_full()      : {cq.is_full()}")
    print(f"peek()         : {cq.peek()}")

    print("\nDraining the circular queue:")
    while not cq.is_empty():
        print(f"  dequeue() -> {cq.dequeue()}")

    print("\nError handling:")
    try:
        cq.dequeue()
    except IndexError as e:
        print(f"  dequeue() on empty -> IndexError: {e}")

    cq2 = CircularQueue(capacity=2)
    cq2.enqueue(1)
    cq2.enqueue(2)
    try:
        cq2.enqueue(3)
    except OverflowError as e:
        print(f"  enqueue() when full -> OverflowError: {e}")
