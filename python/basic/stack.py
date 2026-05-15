"""
Stack (Last-In-First-Out Data Structure)
=========================================

A Stack is a fundamental LIFO (Last-In-First-Out) abstract data structure where elements
are added and removed from the same end called the 'top'. This restriction makes stacks
essential for many real-world problems including:
  - Function call management (call stack in all programming languages)
  - Expression evaluation (infix → postfix conversion, parenthesis matching)
  - Backtracking algorithms (DFS, maze solving, undo/redo functionality)
  - Browser navigation (back button), text editor undo history
  - Parsing nested structures (XML, HTML, JSON validation)

DESIGN PHILOSOPHY:
The stack enforces a strict ordering constraint (LIFO), which:
  • Guarantees O(1) access to only the most recent element
  • Prevents random access (unlike arrays) - this is intentional and valuable
  • Naturally models recursive structures and control flow

IMPLEMENTATIONS PROVIDED:
  1. ListStack
     - Backed by Python's dynamic array/list
     - Uses amortized O(1) push/pop (append/pop at end)
     - Recommended for most cases (cache-friendly, less memory overhead)
     - Potential: O(n) space overhead due to list over-allocation

  2. LinkedListStack
     - Backed by singly linked list nodes
     - Guarantees O(1) worst-case (not amortized) push/pop
     - More flexible for custom memory management
     - Drawback: Higher memory per node due to next pointers + GC overhead

INTERVIEW TIPS:
  - Know when to use stack vs queue vs deque
  - Common pattern: use stack for problems with "undo" or "nested" structure
  - Be ready to discuss ListStack vs LinkedListStack trade-offs
  - Remember: stack doesn't support efficient middle insertion/deletion

TIME/SPACE COMPLEXITIES:
  Operation    | ListStack    | LinkedListStack | Notes
  push(val)    | O(1) amort.  | O(1) worst      | append() has O(n) worst but rare
  pop()        | O(1) amort.  | O(1) worst      | remove from end/head only
  peek()       | O(1)         | O(1)            | access top element
  is_empty()   | O(1)         | O(1)            | check _size or _top
  size()       | O(1)         | O(1)            | maintain counter explicitly
  Space        | O(n) + waste | O(n) + pointers | n = num elements in stack
"""


# ======================================================================
# Implementation 1 – List-backed Stack
# ======================================================================


class ListStack:
    """
    Array-based Stack implementation using Python's dynamic list.

    DESIGN RATIONALE:
    We choose the END of the list as the stack top (not the beginning) because:
      - list.append(val) is O(1) amortized (add to end)
      - list.pop()        is O(1) amortized (remove from end)
      - list.pop(0)       is O(n)           (requires shifting all elements)
    This choice is critical for maintaining O(1) amortized complexity.

    MEMORY CHARACTERISTICS:
    - Python lists use dynamic arrays with exponential growth (capacity ≈ 1.125 * size)
    - This causes amortized O(1) but occasional O(n) reallocation
    - Trade-off: slightly wasted space for guaranteed amortized O(1) operations

    WHEN TO USE:
    - Most general-purpose stack use cases (expression eval, DFS, undo/redo)
    - When cache locality matters (contiguous memory layout)
    - When you want simpler implementation than linked list
    - Applications without strict real-time guarantees

    WHEN NOT TO USE:
    - If you need strict O(1) worst-case behavior → use LinkedListStack
    - If memory is extremely constrained → consider LinkedListStack
    - If your language doesn't have dynamic arrays → use LinkedListStack

    ATTRIBUTES:
        _data (list): Internal list storing stack elements, where _data[-1] is the top
    """

    def __init__(self):
        """Initialize an empty stack.

        Creates an empty list to hold stack elements. No memory is wasted here;
        the list grows dynamically as elements are added.

        Time: O(1)
        Space: O(1) - minimal overhead for empty list object
        """
        self._data: list = []

    def push(self, val) -> None:
        """Push (insert) *val* onto the top of the stack.

        The new element becomes the top and can be accessed via peek() or pop().
        If the internal list is full (capacity exceeded), Python automatically
        reallocates with ~12.5% extra space. This occasional O(n) reallocation
        is amortized O(1) across many operations.

        INTERVIEW NOTE: Understand why we append to END (not beginning):
          - END: append() = O(1)
          - BEGINNING: insert(0, val) = O(n) due to shifting

        Args:
            val: Any value to push onto the stack (can be None, objects, etc.)

        Returns: None (modifies stack in-place)

        Time: O(1) amortized (O(n) occasionally when list resizes)
        Space: O(1) per call (reuses existing list capacity)
        """
        self._data.append(val)

    def pop(self):
        """Remove and return the element at the top of the stack.

        This is the core stack operation: returns the MOST RECENTLY ADDED element.
        After pop(), the next element becomes the new top.

        EDGE CASE: Empty stack
          - This is an error condition in most systems
          - Some implementations return None or a sentinel value
          - This implementation raises IndexError (explicit is better than implicit)
          - Interview discussion: trade-offs between different error handling strategies

        Args: None

        Returns: The element that was at the top of the stack

        Raises:
            IndexError: If the stack is empty (pop from empty stack)
                - This matches Python's built-in list.pop() behavior
                - Prevents silent failure bugs

        Time: O(1) amortized
        Space: O(1) - no extra space needed
        """
        if self.is_empty():
            raise IndexError("pop from empty stack")
        return self._data.pop()

    def peek(self):
        """Return the element at the top WITHOUT removing it.

        Useful when you want to inspect the top before deciding whether to pop.
        Common in parsing and expression evaluation:
          - Parser peeks at next token to decide what to do
          - Expression evaluator checks top for precedence rules

        DIFFERENCE FROM POP:
          pop() → removes and returns (modifies stack)
          peek() → just returns (read-only)

        Args: None

        Returns: The element currently at the top of the stack

        Raises:
            IndexError: If the stack is empty (peek from empty stack)
                - Consistent with pop() behavior
                - Caller must check is_empty() before peek() if unsure

        Time: O(1) - direct array indexing
        Space: O(1) - no extra allocation
        """
        if self.is_empty():
            raise IndexError("peek from empty stack")
        return self._data[-1]

    def is_empty(self) -> bool:
        """Check whether the stack contains any elements.

        COMMON USAGE PATTERN:
          while not stack.is_empty():
              process(stack.pop())

        This is safer than catching exceptions because:
          - Explicit logic is clearer
          - No reliance on exception handling for control flow
          - Better performance (exceptions are expensive)

        Args: None

        Returns: True if stack contains zero elements, False otherwise

        Time: O(1) - simply check list length
        Space: O(1) - constant memory
        """
        return len(self._data) == 0

    def size(self) -> int:
        """Return the current number of elements on the stack.

        Useful for:
          - Determining stack depth in recursive algorithms
          - Allocating space for output
          - Loop bounds checking
          - Debugging and monitoring

        Args: None

        Returns: Integer count of elements (0 if empty)

        Time: O(1) - Python lists maintain size counter
        Space: O(1) - no extra allocation
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
    """Internal singly linked node used by LinkedListStack.

    DESIGN NOTES:
    - Marked private (leading underscore) as it's implementation detail
    - Uses __slots__ to reduce memory overhead of empty node objects
      (prevents automatic __dict__ creation)
    - Each node stores: val (data) + next (pointer)

    MEMORY LAYOUT:
      _StackNode object = overhead + val reference + next pointer
      Typical: ~40 bytes per node (Python 3.x) + object overhead

    LINKED LIST ALTERNATIVE TO ARRAY:
      ListStack:      [1][2][3]  <- contiguous memory, fast access
      LinkedListStack: [1]->[2]->[3]  <- scattered, slower cache, but flexible

    ATTRIBUTES:
        val: The data stored in this node (can be any Python object or None)
        next: Reference to the next _StackNode in the chain (None if end of chain)
    """

    __slots__ = ("val", "next")

    def __init__(self, val, next_node=None):
        """Initialize a node with a value and optional next pointer.

        Args:
            val: Any value to store in this node
            next_node: Reference to the next node (_StackNode or None)

        Time: O(1)
        Space: O(1) per node
        """
        self.val = val
        self.next = next_node


class LinkedListStack:
    """
    Pointer-based Stack implementation using singly linked list nodes.

    DESIGN PHILOSOPHY:
    Instead of storing elements in a dynamic array (ListStack), we chain them
    together using explicit next pointers. The head of the chain is the stack top.

    KEY ADVANTAGE OVER ListStack:
    - Guarantees O(1) WORST-CASE for push/pop (not just amortized)
    - Never requires reallocation or memory reorganization
    - Stack growth is truly incremental (no exponential overhead)

    THE HEAD-AS-TOP PATTERN:
      Push operation:        Pop operation:
        old_head               return self._top.val
           ↓      →  new_head       ↓
        [new val]→[old_head]    [old_head]→[next]
                                    ↓
                               self._top = self._top.next

    MEMORY CHARACTERISTICS:
    - Each node costs: ~40 bytes (Python overhead) + val ref + next pointer
    - Total space: O(n) but with higher per-element overhead than ListStack
    - Garbage collection overhead: Python must track and free each node

    CACHE LOCALITY:
    - LinkedListStack: Poor (nodes scattered in memory, random access pattern)
    - ListStack: Better (elements contiguous in array)
    - Modern CPUs favor contiguous arrays due to cache lines

    WHEN TO USE LinkedListStack:
    1. Real-time systems where O(1) worst-case matters (no GC pauses)
    2. Embedded systems with strict memory budgets (no over-allocation)
    3. Teaching pointer-based data structures
    4. Systems where array resizing would be problematic

    WHEN TO USE ListStack INSTEAD:
    1. Most general-purpose applications (faster in practice)
    2. When cache performance matters
    3. When memory usage matters (less overhead)
    4. Learning modern data structures (arrays dominate)

    INTERVIEW PERSPECTIVE:
    Know the trade-off: amortized O(1) vs. worst-case O(1)
    Most practical systems prefer amortized O(1) (ListStack)
    But some systems (embedded, real-time) need worst-case guarantees

    ATTRIBUTES:
        _top (_StackNode | None): Reference to the head node (top of stack)
        _size (int): Explicit counter of nodes in the stack
    """

    def __init__(self):
        """Initialize an empty linked-list stack.

        Creates a new stack with no nodes. The _top is None and size is 0.
        Ready to accept push() operations.

        INITIALIZATION STATE:
          _top = None     (no nodes in list yet)
          _size = 0       (zero elements)

        Why track _size explicitly?
          - Could traverse list to count: O(n) every call
          - Instead maintain counter: O(1) access
          - Same trade-off as ListStack maintaining len()

        Time: O(1)
        Space: O(1) - constant overhead for object creation
        """
        self._top: _StackNode | None = None
        self._size: int = 0

    def push(self, val) -> None:
        """Push (insert) *val* onto the top of the stack.

        OPERATION SEQUENCE:
        1. Create a new node with val as data
        2. Link the new node to the current top
        3. Update _top to point to the new node
        4. Increment size counter

        BEFORE:        _top                 AFTER:       _top
                       ↓                                  ↓
                    [old_val] → ...                  [new_val] → [old_val] → ...

        This is the fundamental LIFO operation: newest element always at head.

        POINTER MANIPULATION (WHY THIS WORKS):
        - Creating _StackNode(val, self._top) links new node to old top
        - Assignment self._top = new_node makes new node the new top
        - Old top is still reachable via new node's next pointer
        - No element is lost; all remain in the chain

        Args:
            val: Any Python object or value to store in the stack

        Returns: None (modifies stack in-place)

        Time: O(1) - just one node creation and pointer update
        Space: O(1) per call - new node requires constant space
        """
        self._top = _StackNode(val, self._top)
        self._size += 1

    def pop(self):
        """Remove and return the element at the top of the stack.

        OPERATION SEQUENCE:
        1. Check if stack is empty (error condition)
        2. Save the value from the top node
        3. Move _top to point to the next node
        4. Decrement size counter
        5. Return the saved value

        BEFORE:       _top                 AFTER:        _top
                      ↓                                   ↓
                   [top_val] → [next_val] → ...      [next_val] → ...

        The top node is no longer referenced by _top, so Python's garbage
        collector will eventually free it (when no other references exist).

        EDGE CASE: Empty stack
        - Raises IndexError (consistent with ListStack and Python's list.pop())
        - This prevents silent failures and makes bugs explicit
        - Caller should check is_empty() or use peek() first if uncertain

        Args: None

        Returns: The value that was stored at the top of the stack

        Raises:
            IndexError: If the stack is empty
                - Message: "pop from empty stack" (debugging hint)
                - Matches ListStack behavior for consistency

        Time: O(1) - just pointer updates and counter decrement
        Space: O(1) - no extra allocation needed
        """
        if self.is_empty():
            raise IndexError("pop from empty stack")
        val = self._top.val
        self._top = self._top.next
        self._size -= 1
        return val

    def peek(self):
        """Return the element at the top WITHOUT removing it.

        Read-only operation: examines the top without modifying the stack.

        USE CASE:
        - Expression parser peeks at next operator to decide precedence
        - DFS algorithm peeks to see what's on the stack without popping
        - State machine checks top element to validate transition

        COMPARED TO POP:
          peek() → returns self._top.val (read-only)
          pop()  → returns value AND updates _top and _size (modifying)

        SAFE USAGE:
          val = stack.peek()  # OK to examine
          stack.pop()         # Then remove

        DANGEROUS ALTERNATIVE:
          val = stack.pop()   # Did you want to remove it?

        Args: None

        Returns: The value currently at the top of the stack

        Raises:
            IndexError: If the stack is empty
                - Cannot examine top of empty stack
                - Caller should check is_empty() first

        Time: O(1) - direct access to _top node
        Space: O(1) - no extra allocation
        """
        if self.is_empty():
            raise IndexError("peek from empty stack")
        return self._top.val

    def is_empty(self) -> bool:
        """Check whether the stack contains any elements.

        Two equivalent checks (both O(1)):
          1. return self._top is None     (check head pointer)
          2. return self._size == 0       (check counter)

        This implementation uses approach #1 (check head).
        Either is correct; #1 is slightly faster (one pointer compare).

        BEST PRACTICE:
        Always check is_empty() before peek() or pop() to avoid exceptions:
          if not stack.is_empty():
              val = stack.pop()

        Args: None

        Returns: True if no elements in stack, False otherwise

        Time: O(1) - single pointer comparison
        Space: O(1) - no extra allocation
        """
        return self._top is None

    def size(self) -> int:
        """Return the current number of elements on the stack.

        WHY MAINTAIN EXPLICIT _size COUNTER?
        Alternative: traverse list from _top to None and count nodes
          - Simple: just one loop
          - Cost: O(n) time for each call
          - When used: rarely justified

        Actual approach: maintain _size counter
          - Cost: O(1) per operation
          - Overhead: one extra integer field (~8 bytes)
          - Trade-off: highly worthwhile (like Python's len() on lists)

        USAGE:
        - Loop bounds: for i in range(stack.size())
        - Capacity checks: if stack.size() >= max_depth
        - Debugging: print(f"Stack depth: {stack.size()}")

        Args: None

        Returns: Integer count of elements currently in the stack

        Time: O(1) - direct access to _size field
        Space: O(1) - no extra allocation
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
