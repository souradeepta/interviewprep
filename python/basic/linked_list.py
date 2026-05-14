"""
Linked Lists
============
Provides both SinglyLinkedList and DoublyLinkedList in a single module.

SinglyLinkedList -- each node holds a value and a pointer to the next node.
DoublyLinkedList -- each node holds a value plus pointers to both next and prev.

Common Time Complexities:
  append / prepend   -- O(1)  (tail pointer maintained)
  insert_after(node) -- O(1)  (given the node; O(n) to find it first)
  delete(val)        -- O(n)
  search(val)        -- O(n)
  reverse            -- O(n)
  to_list            -- O(n)
"""


# ======================================================================
# Singly Linked List
# ======================================================================


class _SNode:
    """Internal node for SinglyLinkedList."""

    __slots__ = ("val", "next")

    def __init__(self, val, next_node=None):
        self.val = val
        self.next = next_node

    def __repr__(self):
        return f"SNode({self.val})"


class SinglyLinkedList:
    """
    A singly linked list with a tail pointer for O(1) appends.

    Attributes:
        head  : first node (None if empty)
        tail  : last node  (None if empty)
        _size : number of elements
    """

    def __init__(self):
        """Initialize an empty singly linked list.

        Time: O(1)
        """
        self.head: _SNode | None = None
        self.tail: _SNode | None = None
        self._size: int = 0

    # ------------------------------------------------------------------
    # Insertion
    # ------------------------------------------------------------------

    def append(self, val) -> None:
        """Add *val* at the end of the list.

        Time: O(1)
        """
        node = _SNode(val)
        if self.tail is None:
            self.head = self.tail = node
        else:
            self.tail.next = node
            self.tail = node
        self._size += 1

    def prepend(self, val) -> None:
        """Add *val* at the beginning of the list.

        Time: O(1)
        """
        node = _SNode(val, self.head)
        self.head = node
        if self.tail is None:
            self.tail = node
        self._size += 1

    def insert_after(self, target_val, new_val) -> bool:
        """Insert *new_val* immediately after the first node with value *target_val*.

        Args:
            target_val: value of the node after which to insert.
            new_val:    value to insert.

        Returns:
            True if insertion succeeded, False if *target_val* was not found.

        Time: O(n)
        """
        current = self.head
        while current:
            if current.val == target_val:
                new_node = _SNode(new_val, current.next)
                current.next = new_node
                if current is self.tail:
                    self.tail = new_node
                self._size += 1
                return True
            current = current.next
        return False

    # ------------------------------------------------------------------
    # Deletion
    # ------------------------------------------------------------------

    def delete(self, val) -> bool:
        """Remove the first node whose value equals *val*.

        Returns:
            True if a node was removed, False if *val* was not found.

        Time: O(n)
        """
        if self.head is None:
            return False

        # Special case: deleting the head
        if self.head.val == val:
            self.head = self.head.next
            if self.head is None:
                self.tail = None
            self._size -= 1
            return True

        prev, current = self.head, self.head.next
        while current:
            if current.val == val:
                prev.next = current.next
                if current is self.tail:
                    self.tail = prev
                self._size -= 1
                return True
            prev, current = current, current.next
        return False

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def search(self, val) -> _SNode | None:
        """Return the first node with value *val*, or None if not found.

        Time: O(n)
        """
        current = self.head
        while current:
            if current.val == val:
                return current
            current = current.next
        return None

    # ------------------------------------------------------------------
    # Transformation
    # ------------------------------------------------------------------

    def reverse(self) -> None:
        """Reverse the list in place.

        Time: O(n)
        Space: O(1)
        """
        self.tail = self.head
        prev = None
        current = self.head
        while current:
            nxt = current.next
            current.next = prev
            prev = current
            current = nxt
        self.head = prev

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    def to_list(self) -> list:
        """Return all values as a Python list (head to tail).

        Time: O(n)
        """
        result = []
        current = self.head
        while current:
            result.append(current.val)
            current = current.next
        return result

    def size(self) -> int:
        """Return the number of elements.

        Time: O(1)
        """
        return self._size

    def __len__(self) -> int:
        return self._size

    def __str__(self) -> str:
        """ASCII arrow visualization: HEAD -> 1 -> 2 -> 3 -> None"""
        if self.head is None:
            return "HEAD -> None"
        nodes = []
        current = self.head
        while current:
            nodes.append(str(current.val))
            current = current.next
        return "HEAD -> " + " -> ".join(nodes) + " -> None"

    def __repr__(self) -> str:
        return f"SinglyLinkedList({self.to_list()})"


# ======================================================================
# Doubly Linked List
# ======================================================================


class _DNode:
    """Internal node for DoublyLinkedList."""

    __slots__ = ("val", "next", "prev")

    def __init__(self, val, prev_node=None, next_node=None):
        self.val = val
        self.prev = prev_node
        self.next = next_node

    def __repr__(self):
        return f"DNode({self.val})"


class DoublyLinkedList:
    """
    A doubly linked list with sentinel head/tail nodes to simplify
    edge-case handling.

    Internal layout:
        sentinel_head <-> node1 <-> node2 <-> ... <-> sentinel_tail

    Attributes:
        _head  : sentinel head node
        _tail  : sentinel tail node
        _size  : number of real (non-sentinel) elements
    """

    def __init__(self):
        """Initialize an empty doubly linked list with sentinel nodes.

        Time: O(1)
        """
        self._head = _DNode("HEAD_SENTINEL")
        self._tail = _DNode("TAIL_SENTINEL")
        self._head.next = self._tail
        self._tail.prev = self._head
        self._size = 0

    # ------------------------------------------------------------------
    # Insertion
    # ------------------------------------------------------------------

    def append(self, val) -> None:
        """Add *val* at the end of the list (before the tail sentinel).

        Time: O(1)
        """
        self._insert_before(self._tail, val)

    def prepend(self, val) -> None:
        """Add *val* at the beginning of the list (after the head sentinel).

        Time: O(1)
        """
        self._insert_after(self._head, val)

    def insert_after(self, target_val, new_val) -> bool:
        """Insert *new_val* immediately after the first node with *target_val*.

        Returns:
            True on success, False if *target_val* was not found.

        Time: O(n)
        """
        node = self._find(target_val)
        if node is None:
            return False
        self._insert_after(node, new_val)
        return True

    # ------------------------------------------------------------------
    # Deletion
    # ------------------------------------------------------------------

    def delete(self, val) -> bool:
        """Remove the first node whose value equals *val*.

        Returns:
            True if removed, False if not found.

        Time: O(n)
        """
        node = self._find(val)
        if node is None:
            return False
        self._unlink(node)
        return True

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def search(self, val) -> _DNode | None:
        """Return the first real node with value *val*, or None.

        Time: O(n)
        """
        return self._find(val)

    # ------------------------------------------------------------------
    # Transformation
    # ------------------------------------------------------------------

    def reverse(self) -> None:
        """Reverse the list in place by swapping next/prev pointers.

        Time: O(n)
        """
        current = self._head
        while current:
            # Swap next and prev for every node including sentinels
            current.next, current.prev = current.prev, current.next
            current = current.prev  # move forward (was 'next' before swap)
        # Swap sentinel roles
        self._head, self._tail = self._tail, self._head

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    def to_list(self) -> list:
        """Return all values as a Python list (head to tail).

        Time: O(n)
        """
        result = []
        current = self._head.next
        while current is not self._tail:
            result.append(current.val)
            current = current.next
        return result

    def size(self) -> int:
        """Return the number of elements.

        Time: O(1)
        """
        return self._size

    def __len__(self) -> int:
        return self._size

    def __str__(self) -> str:
        """ASCII bidirectional arrow visualization:
        None <-> 1 <-> 2 <-> 3 <-> None
        """
        current = self._head.next
        if current is self._tail:
            return "None"
        parts = []
        while current is not self._tail:
            parts.append(str(current.val))
            current = current.next
        return "None <-> " + " <-> ".join(parts) + " <-> None"

    def __repr__(self) -> str:
        return f"DoublyLinkedList({self.to_list()})"

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _insert_after(self, node: _DNode, val) -> _DNode:
        """Insert a new node with *val* directly after *node*."""
        new_node = _DNode(val, prev_node=node, next_node=node.next)
        node.next.prev = new_node
        node.next = new_node
        self._size += 1
        return new_node

    def _insert_before(self, node: _DNode, val) -> _DNode:
        """Insert a new node with *val* directly before *node*."""
        return self._insert_after(node.prev, val)

    def _unlink(self, node: _DNode) -> None:
        """Remove *node* from the list (does not check sentinel boundaries)."""
        node.prev.next = node.next
        node.next.prev = node.prev
        node.next = node.prev = None
        self._size -= 1

    def _find(self, val) -> _DNode | None:
        """Return the first real node with *val*, or None."""
        current = self._head.next
        while current is not self._tail:
            if current.val == val:
                return current
            current = current.next
        return None


# ======================================================================
# Demo
# ======================================================================

if __name__ == "__main__":
    # ------------------------------------------------------------------ #
    # Singly Linked List
    # ------------------------------------------------------------------ #
    print("=" * 60)
    print("Singly Linked List Demo")
    print("=" * 60)

    sll = SinglyLinkedList()
    print(f"Empty list     : {sll}")

    for v in [10, 20, 30, 40]:
        sll.append(v)
    print(f"After appends  : {sll}")

    sll.prepend(5)
    print(f"prepend(5)     : {sll}")

    sll.insert_after(20, 25)
    print(f"insert_after(20, 25): {sll}")

    sll.insert_after(40, 45)
    print(f"insert_after(40, 45): {sll}")

    node = sll.search(25)
    print(f"search(25)     : {node}")
    print(f"search(99)     : {sll.search(99)}")

    sll.delete(5)
    print(f"delete(5)      : {sll}")
    sll.delete(25)
    print(f"delete(25)     : {sll}")
    sll.delete(45)
    print(f"delete(45)     : {sll}")

    print(f"to_list()      : {sll.to_list()}")
    print(f"size()         : {sll.size()}")

    sll.reverse()
    print(f"reverse()      : {sll}")

    # ------------------------------------------------------------------ #
    # Doubly Linked List
    # ------------------------------------------------------------------ #
    print()
    print("=" * 60)
    print("Doubly Linked List Demo")
    print("=" * 60)

    dll = DoublyLinkedList()
    print(f"Empty list     : {dll}")

    for v in [10, 20, 30, 40]:
        dll.append(v)
    print(f"After appends  : {dll}")

    dll.prepend(5)
    print(f"prepend(5)     : {dll}")

    dll.insert_after(20, 25)
    print(f"insert_after(20, 25): {dll}")

    node = dll.search(25)
    print(f"search(25)     : {node}")
    print(f"search(99)     : {dll.search(99)}")

    dll.delete(5)
    print(f"delete(5)      : {dll}")
    dll.delete(25)
    print(f"delete(25)     : {dll}")
    dll.delete(40)
    print(f"delete(40)     : {dll}")

    print(f"to_list()      : {dll.to_list()}")
    print(f"size()         : {dll.size()}")

    dll.reverse()
    print(f"reverse()      : {dll}")
