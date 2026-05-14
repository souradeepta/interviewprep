"""
LRU Cache — Two Implementations
=================================
An LRU (Least Recently Used) cache evicts the entry that has not been
accessed for the longest time when the cache reaches capacity.

Implementation 1 — OrderedDict:
    Python's collections.OrderedDict maintains insertion order and supports
    O(1) move_to_end.  This makes the LRU cache trivially simple.

Implementation 2 — Doubly-Linked List + HashMap:
    The "canonical" interview implementation.  A doubly-linked list orders
    entries by recency (head = most recent, tail = least recent).
    A hash map provides O(1) node lookup by key.

Complexities (both implementations):
    - get(key):        O(1)
    - put(key, val):   O(1)
    - Space:           O(capacity)
"""

from __future__ import annotations
from collections import OrderedDict
from typing import Any, Dict, Optional


# ======================================================================
# Implementation 1: OrderedDict-based
# ======================================================================

class LRUCacheOD:
    """
    LRU Cache backed by collections.OrderedDict.

    OrderedDict.move_to_end(key) is O(1) and marks the key as most recently
    used.  popitem(last=False) removes the LRU entry in O(1).
    """

    def __init__(self, capacity: int) -> None:
        if capacity <= 0:
            raise ValueError("Capacity must be a positive integer.")
        self._capacity = capacity
        self._cache: OrderedDict = OrderedDict()

    def get(self, key: Any) -> Optional[Any]:
        """
        Return the value for *key*, or None if not present.
        Marks *key* as most recently used.

        Time:  O(1)
        """
        if key not in self._cache:
            return None
        # Move to the end (= most recently used position).
        self._cache.move_to_end(key)
        return self._cache[key]

    def put(self, key: Any, val: Any) -> None:
        """
        Insert or update *key* with *val*.
        Evicts the least recently used entry if at capacity.

        Time:  O(1)
        """
        if key in self._cache:
            self._cache.move_to_end(key)
        self._cache[key] = val
        if len(self._cache) > self._capacity:
            # popitem(last=False) removes the FIRST (oldest) item.
            self._cache.popitem(last=False)

    @property
    def size(self) -> int:
        return len(self._cache)

    def __repr__(self) -> str:
        # Show MRU → LRU order.
        items = list(reversed(self._cache.items()))
        return f"LRUCacheOD(cap={self._capacity}, items={items})"


# ======================================================================
# Implementation 2: Doubly-Linked List + HashMap
# ======================================================================

class _DLLNode:
    """A node in the doubly-linked list."""

    __slots__ = ("key", "val", "prev", "next")

    def __init__(self, key: Any = None, val: Any = None) -> None:
        self.key = key
        self.val = val
        self.prev: Optional[_DLLNode] = None
        self.next: Optional[_DLLNode] = None


class LRUCacheDLL:
    """
    LRU Cache using a Doubly-Linked List + HashMap.

    Layout:
        HEAD (dummy) ↔ [MRU node] ↔ ... ↔ [LRU node] ↔ TAIL (dummy)

    Sentinel HEAD and TAIL nodes eliminate edge-case checks for empty lists.

    Operations:
        get(key):
            1. Look up node in hashmap → O(1).
            2. Move node to just after HEAD → O(1).
        put(key, val):
            1. If key exists, update val and move to front.
            2. Else insert new node after HEAD.
            3. If over capacity, remove node just before TAIL (LRU).
    """

    def __init__(self, capacity: int) -> None:
        if capacity <= 0:
            raise ValueError("Capacity must be a positive integer.")
        self._capacity = capacity
        self._map: Dict[Any, _DLLNode] = {}

        # Sentinels — never removed, never stored in the hashmap.
        self._head = _DLLNode()   # most-recent end
        self._tail = _DLLNode()   # least-recent end
        self._head.next = self._tail
        self._tail.prev = self._head

    # ------------------------------------------------------------------
    # DLL helpers
    # ------------------------------------------------------------------

    def _remove(self, node: _DLLNode) -> None:
        """Unlink *node* from the DLL in O(1)."""
        node.prev.next = node.next
        node.next.prev = node.prev

    def _insert_after_head(self, node: _DLLNode) -> None:
        """Insert *node* right after HEAD (= most recently used) in O(1)."""
        node.prev = self._head
        node.next = self._head.next
        self._head.next.prev = node
        self._head.next = node

    def _move_to_front(self, node: _DLLNode) -> None:
        """Move existing *node* to the MRU position in O(1)."""
        self._remove(node)
        self._insert_after_head(node)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get(self, key: Any) -> Optional[Any]:
        """
        Return value for *key*, or None if absent.

        Time:  O(1)
        """
        if key not in self._map:
            return None
        node = self._map[key]
        self._move_to_front(node)
        return node.val

    def put(self, key: Any, val: Any) -> None:
        """
        Insert or update *key* / *val*.
        Evicts LRU entry if over capacity.

        Time:  O(1)
        """
        if key in self._map:
            node = self._map[key]
            node.val = val
            self._move_to_front(node)
        else:
            node = _DLLNode(key, val)
            self._map[key] = node
            self._insert_after_head(node)
            if len(self._map) > self._capacity:
                # Evict LRU: the node just before TAIL.
                lru = self._tail.prev
                self._remove(lru)
                del self._map[lru.key]

    @property
    def size(self) -> int:
        return len(self._map)

    def _to_list(self):
        """Return items as [(key, val), ...] in MRU → LRU order."""
        result = []
        cur = self._head.next
        while cur is not self._tail:
            result.append((cur.key, cur.val))
            cur = cur.next
        return result

    def __repr__(self) -> str:
        return f"LRUCacheDLL(cap={self._capacity}, items={self._to_list()})"


# ----------------------------------------------------------------------
# Demo
# ----------------------------------------------------------------------

if __name__ == "__main__":
    def run_demo(cache, label: str) -> None:
        print(f"=== {label} (capacity=3) ===")
        cache.put(1, "one")
        cache.put(2, "two")
        cache.put(3, "three")
        print("After put(1), put(2), put(3):", repr(cache))

        print("get(1):", cache.get(1))        # "one"  — 1 becomes MRU
        cache.put(4, "four")                  # evicts 2 (LRU)
        print("After get(1) + put(4):", repr(cache))

        print("get(2):", cache.get(2))        # None   — 2 was evicted
        print("get(3):", cache.get(3))        # "three"
        cache.put(5, "five")                  # evicts 4 (LRU)
        print("After put(5):", repr(cache))
        print()

    run_demo(LRUCacheOD(3), "LRUCache (OrderedDict)")
    run_demo(LRUCacheDLL(3), "LRUCache (DLL + HashMap)")

    # Stress-test equivalence.
    print("=== Equivalence stress test ===")
    od = LRUCacheOD(4)
    dll = LRUCacheDLL(4)
    ops = [
        ("put", "a", 1), ("put", "b", 2), ("put", "c", 3), ("put", "d", 4),
        ("get", "b", None), ("put", "e", 5),
        ("get", "a", None), ("get", "c", None),
        ("put", "f", 6), ("get", "d", None), ("get", "e", None),
    ]
    for op in ops:
        if op[0] == "put":
            od.put(op[1], op[2])
            dll.put(op[1], op[2])
        else:
            r1, r2 = od.get(op[1]), dll.get(op[1])
            assert r1 == r2, f"Mismatch on get({op[1]}): OD={r1}, DLL={r2}"
    print("All operations match between both implementations.")
