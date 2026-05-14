"""
Stack
=====
A Last-In, First-Out (LIFO) data structure.

Two implementations are provided:
  1. ListStack        -- backed by a Python list (recommended for most uses)
  2. LinkedListStack  -- backed by a singly linked list (illustrates pointer-
                         based implementation; avoids list reallocation)

Time Complexities (both implementations):
  push    -- O(1)
  pop     -- O(1)
  peek    -- O(1)
  is_empty-- O(1)
  size    -- O(1)
"""


# ======================================================================
# Implementation 1 – List-backed Stack
# ======================================================================


class ListStack:
    """
    Stack backed by a Python list.
    The top of the stack is the last element of the list.

    Using the *end* of the list as the top avoids O(n) shifts;
    list.append() and list.pop() are both O(1) amortized.
    """

    def __init__(self):
        """Initialize an empty stack.

        Time: O(1)
        """
        self._data: list = []

    def push(self, val) -> None:
        """Push *val* onto the top of the stack.

        Time: O(1) amortized
        """
        self._data.append(val)

    def pop(self):
        """Remove and return the top element.

        Raises:
            IndexError: if the stack is empty.

        Time: O(1) amortized
        """
        if self.is_empty():
            raise IndexError("pop from empty stack")
        return self._data.pop()

    def peek(self):
        """Return the top element without removing it.

        Raises:
            IndexError: if the stack is empty.

        Time: O(1)
        """
        if self.is_empty():
            raise IndexError("peek from empty stack")
        return self._data[-1]

    def is_empty(self) -> bool:
        """Return True if the stack has no elements.

        Time: O(1)
        """
        return len(self._data) == 0

    def size(self) -> int:
        """Return the number of elements on the stack.

        Time: O(1)
        """
        return len(self._data)

    def __len__(self) -> int:
        return self.size()

    def __str__(self) -> str:
        """Visualize the stack with the top on the right.

        Example:
            Stack (top ->): [1, 2, 3]  size=3
        """
        return f"Stack (top ->): {self._data}  size={self.size()}"

    def __repr__(self) -> str:
        return f"ListStack({self._data})"


# ======================================================================
# Implementation 2 – Linked-list-backed Stack
# ======================================================================


class _StackNode:
    """Internal singly linked node used by LinkedListStack."""

    __slots__ = ("val", "next")

    def __init__(self, val, next_node=None):
        self.val = val
        self.next = next_node


class LinkedListStack:
    """
    Stack backed by a singly linked list.
    The head of the list serves as the top of the stack, so both
    push and pop are O(1) without any shifting or reallocation.

    This is useful when you need guaranteed O(1) worst-case (not just
    amortized) behavior, or when building a stack from scratch without
    using Python's built-in list.
    """

    def __init__(self):
        """Initialize an empty linked-list stack.

        Time: O(1)
        """
        self._top: _StackNode | None = None
        self._size: int = 0

    def push(self, val) -> None:
        """Push *val* onto the top of the stack.

        Time: O(1)
        """
        self._top = _StackNode(val, self._top)
        self._size += 1

    def pop(self):
        """Remove and return the top element.

        Raises:
            IndexError: if the stack is empty.

        Time: O(1)
        """
        if self.is_empty():
            raise IndexError("pop from empty stack")
        val = self._top.val
        self._top = self._top.next
        self._size -= 1
        return val

    def peek(self):
        """Return the top element without removing it.

        Raises:
            IndexError: if the stack is empty.

        Time: O(1)
        """
        if self.is_empty():
            raise IndexError("peek from empty stack")
        return self._top.val

    def is_empty(self) -> bool:
        """Return True if the stack has no elements.

        Time: O(1)
        """
        return self._top is None

    def size(self) -> int:
        """Return the number of elements on the stack.

        Time: O(1)
        """
        return self._size

    def __len__(self) -> int:
        return self.size()

    def __str__(self) -> str:
        """Visualize the stack from top to bottom.

        Example:
            LinkedListStack top -> 3 -> 2 -> 1 -> None   size=3
        """
        parts = []
        current = self._top
        while current:
            parts.append(str(current.val))
            current = current.next
        chain = " -> ".join(parts) + " -> None" if parts else "None"
        return f"LinkedListStack top -> {chain}   size={self._size}"

    def __repr__(self) -> str:
        parts = []
        current = self._top
        while current:
            parts.append(current.val)
            current = current.next
        return f"LinkedListStack({parts})"


# ======================================================================
# Demo
# ======================================================================

if __name__ == "__main__":
    # ------------------------------------------------------------------ #
    # List-backed Stack
    # ------------------------------------------------------------------ #
    print("=" * 60)
    print("ListStack Demo")
    print("=" * 60)

    s = ListStack()
    print(f"Initial        : {s}")
    print(f"is_empty()     : {s.is_empty()}")

    for v in [1, 2, 3, 4, 5]:
        s.push(v)
        print(f"push({v})        : {s}")

    print(f"\npeek()         : {s.peek()}")
    print(f"size()         : {s.size()}")

    while not s.is_empty():
        print(f"pop()  -> {s.pop():<3}  : {s}")

    print(f"\nis_empty()     : {s.is_empty()}")

    print("\nError handling:")
    try:
        s.pop()
    except IndexError as e:
        print(f"  pop() on empty -> IndexError: {e}")
    try:
        s.peek()
    except IndexError as e:
        print(f"  peek() on empty -> IndexError: {e}")

    # ------------------------------------------------------------------ #
    # Linked-list-backed Stack
    # ------------------------------------------------------------------ #
    print()
    print("=" * 60)
    print("LinkedListStack Demo")
    print("=" * 60)

    ls = LinkedListStack()
    print(f"Initial        : {ls}")
    print(f"is_empty()     : {ls.is_empty()}")

    for v in [10, 20, 30]:
        ls.push(v)
        print(f"push({v})       : {ls}")

    print(f"\npeek()         : {ls.peek()}")
    print(f"size()         : {ls.size()}")

    while not ls.is_empty():
        print(f"pop()  -> {ls.pop():<4}  : {ls}")

    # ------------------------------------------------------------------ #
    # Classic interview use-case: balanced parentheses checker
    # ------------------------------------------------------------------ #
    print()
    print("=" * 60)
    print("Bonus: Balanced Parentheses Checker (uses ListStack)")
    print("=" * 60)

    def is_balanced(s: str) -> bool:
        """Return True if all brackets in *s* are balanced."""
        stack = ListStack()
        matching = {")": "(", "]": "[", "}": "{"}
        for ch in s:
            if ch in "([{":
                stack.push(ch)
            elif ch in ")]}":
                if stack.is_empty() or stack.pop() != matching[ch]:
                    return False
        return stack.is_empty()

    tests = ["(())", "()[]{}", "(]", "([)]", "{[]}"]
    for expr in tests:
        print(f"  {expr!r:<10} -> {'balanced' if is_balanced(expr) else 'NOT balanced'}")
