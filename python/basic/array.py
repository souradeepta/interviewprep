"""
Dynamic Array (Resizable Array)
================================
Mimics the behavior of Java's ArrayList or C++'s std::vector.
Backed by a fixed-size Python list; doubles capacity when full.

Time Complexities:
  append         -- O(1) amortized
  insert(i, v)   -- O(n)
  delete(i)      -- O(n)
  get(i)         -- O(1)
  set(i, v)      -- O(1)
  size           -- O(1)
  resize         -- O(n)
"""


class DynamicArray:
    """
    A resizable array that doubles its capacity when the backing store is full
    and halves it when the array is less than 25% full.

    Attributes:
        _data     : backing list of fixed logical size
        _size     : number of elements currently stored
        _capacity : current allocated capacity
    """

    DEFAULT_CAPACITY = 4

    def __init__(self):
        """Initialize an empty dynamic array with default capacity.

        Time: O(1)
        """
        self._capacity = self.DEFAULT_CAPACITY
        self._data = [None] * self._capacity
        self._size = 0

    # ------------------------------------------------------------------
    # Core API
    # ------------------------------------------------------------------

    def append(self, value) -> None:
        """Append *value* to the end of the array.

        Triggers a resize (doubling) when the backing store is full.

        Time: O(1) amortized
        """
        if self._size == self._capacity:
            self._resize(self._capacity * 2)
        self._data[self._size] = value
        self._size += 1

    def insert(self, index: int, value) -> None:
        """Insert *value* at position *index*, shifting elements right.

        Args:
            index: 0-based insertion position; must satisfy 0 <= index <= size.
            value: the value to insert.

        Raises:
            IndexError: if *index* is out of range.

        Time: O(n)
        """
        self._check_index_for_insert(index)
        if self._size == self._capacity:
            self._resize(self._capacity * 2)
        # Shift elements right to make room
        for i in range(self._size, index, -1):
            self._data[i] = self._data[i - 1]
        self._data[index] = value
        self._size += 1

    def delete(self, index: int):
        """Remove and return the element at *index*, shifting elements left.

        Args:
            index: 0-based position; must satisfy 0 <= index < size.

        Returns:
            The removed element.

        Raises:
            IndexError: if *index* is out of range.

        Time: O(n)
        """
        self._check_index(index)
        removed = self._data[index]
        # Shift elements left
        for i in range(index, self._size - 1):
            self._data[i] = self._data[i + 1]
        self._data[self._size - 1] = None  # help GC
        self._size -= 1
        # Shrink when less than 25% full (but keep at least DEFAULT_CAPACITY)
        if (
            self._size > 0
            and self._size <= self._capacity // 4
            and self._capacity // 2 >= self.DEFAULT_CAPACITY
        ):
            self._resize(self._capacity // 2)
        return removed

    def get(self, index: int):
        """Return the element at *index*.

        Time: O(1)
        """
        self._check_index(index)
        return self._data[index]

    def set(self, index: int, value) -> None:
        """Overwrite the element at *index* with *value*.

        Time: O(1)
        """
        self._check_index(index)
        self._data[index] = value

    def size(self) -> int:
        """Return the number of elements stored.

        Time: O(1)
        """
        return self._size

    def capacity(self) -> int:
        """Return the current allocated capacity.

        Time: O(1)
        """
        return self._capacity

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _resize(self, new_capacity: int) -> None:
        """Copy existing elements into a new backing list of *new_capacity*.

        Time: O(n)
        """
        new_data = [None] * new_capacity
        for i in range(self._size):
            new_data[i] = self._data[i]
        self._data = new_data
        self._capacity = new_capacity

    def _check_index(self, index: int) -> None:
        if not (0 <= index < self._size):
            raise IndexError(
                f"Index {index} out of range for array of size {self._size}"
            )

    def _check_index_for_insert(self, index: int) -> None:
        if not (0 <= index <= self._size):
            raise IndexError(
                f"Insert index {index} out of range for array of size {self._size}"
            )

    # ------------------------------------------------------------------
    # Dunder helpers
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        return self._size

    def __getitem__(self, index: int):
        return self.get(index)

    def __setitem__(self, index: int, value) -> None:
        self.set(index, value)

    def __iter__(self):
        for i in range(self._size):
            yield self._data[i]

    def __str__(self) -> str:
        """Visualize the array contents and capacity.

        Example output:
            [10, 20, 30, _, _]   size=3  capacity=5
        """
        elements = [str(self._data[i]) for i in range(self._size)]
        empty_slots = ["_"] * (self._capacity - self._size)
        all_slots = elements + empty_slots
        return f"[{', '.join(all_slots)}]   size={self._size}  capacity={self._capacity}"

    def __repr__(self) -> str:
        return f"DynamicArray({list(self)})"


# ======================================================================
# Demo
# ======================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Dynamic Array Demo")
    print("=" * 60)

    arr = DynamicArray()
    print(f"Initial state  : {arr}")

    # append
    for val in [10, 20, 30, 40]:
        arr.append(val)
        print(f"append({val:>2})     : {arr}")

    # trigger first resize (capacity doubles from 4 to 8)
    arr.append(50)
    print(f"append(50)     : {arr}  <-- resize triggered")

    # get / set
    print(f"\nget(2)         : {arr.get(2)}")
    arr.set(2, 99)
    print(f"set(2, 99)     : {arr}")

    # insert
    arr.insert(1, 15)
    print(f"insert(1, 15)  : {arr}")

    arr.insert(0, 5)
    print(f"insert(0,  5)  : {arr}")

    arr.insert(arr.size(), 100)
    print(f"insert(end,100): {arr}")

    # delete
    removed = arr.delete(0)
    print(f"\ndelete(0) -> {removed}  : {arr}")

    removed = arr.delete(arr.size() - 1)
    print(f"delete(end)-> {removed}: {arr}")

    removed = arr.delete(2)
    print(f"delete(2) -> {removed}  : {arr}")

    # shrink on many deletes
    print("\nDeleting elements to trigger shrink:")
    while arr.size() > 1:
        removed = arr.delete(0)
        print(f"  delete(0) -> {removed:<3}  : {arr}")

    # iteration
    arr2 = DynamicArray()
    for v in [7, 14, 21, 28]:
        arr2.append(v)
    print(f"\nIteration over {arr2!r}:")
    print(" ", list(arr2))

    # error handling
    print("\nError handling:")
    try:
        arr2.get(100)
    except IndexError as e:
        print(f"  get(100)  -> IndexError: {e}")
    try:
        arr2.insert(-1, 0)
    except IndexError as e:
        print(f"  insert(-1)-> IndexError: {e}")
