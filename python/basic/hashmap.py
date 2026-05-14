"""
HashMap
=======
Two collision-resolution strategies are provided:

  1. ChainingHashMap  -- separate chaining using a list of (key, value) pairs
                         per bucket.  Simple, cache-unfriendly, unbounded load.
  2. ProbingHashMap   -- open addressing with linear probing.  Cache-friendly,
                         requires a deleted sentinel to handle probe chains.

Both support dynamic resizing:
  - Expand (double) when load factor > 0.75
  - Shrink (halve) when load factor < 0.25 (minimum 8 buckets)

Time Complexities (average case):
  put(key, val)   -- O(1) amortized
  get(key)        -- O(1) average, O(n) worst (all keys collide)
  delete(key)     -- O(1) average
  contains(key)   -- O(1) average

Space: O(n) where n is the number of key-value pairs stored.
"""

from __future__ import annotations

from typing import Any, Iterator


# ======================================================================
# Implementation 1 – Separate Chaining HashMap
# ======================================================================

_CHAIN_INITIAL_CAPACITY = 8
_CHAIN_LOAD_MAX = 0.75
_CHAIN_LOAD_MIN = 0.25


class ChainingHashMap:
    """
    HashMap using separate chaining for collision resolution.

    Each bucket is a Python list of (key, value) pairs.  On collision,
    the new pair is appended to the existing bucket list.

    Attributes:
        _buckets  : list of bucket lists
        _capacity : number of buckets
        _size     : number of key-value pairs stored
    """

    def __init__(self, initial_capacity: int = _CHAIN_INITIAL_CAPACITY):
        """Initialize an empty hash map.

        Args:
            initial_capacity: number of buckets to allocate initially.

        Time: O(capacity)
        """
        self._capacity = max(initial_capacity, 1)
        self._buckets: list[list[tuple]] = [[] for _ in range(self._capacity)]
        self._size = 0

    # ------------------------------------------------------------------
    # Core operations
    # ------------------------------------------------------------------

    def put(self, key, val) -> None:
        """Insert or update the value for *key*.

        If *key* already exists, its value is overwritten.
        Triggers a resize when the load factor exceeds 0.75.

        Time: O(1) amortized
        """
        self._maybe_resize_up()
        bucket = self._get_bucket(key)
        for i, (k, _) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, val)  # update existing key
                return
        bucket.append((key, val))
        self._size += 1

    def get(self, key) -> Any:
        """Return the value associated with *key*.

        Raises:
            KeyError: if *key* is not in the map.

        Time: O(1) average
        """
        bucket = self._get_bucket(key)
        for k, v in bucket:
            if k == key:
                return v
        raise KeyError(key)

    def delete(self, key) -> Any:
        """Remove *key* and return its value.

        Raises:
            KeyError: if *key* is not in the map.

        Time: O(1) average
        """
        bucket = self._get_bucket(key)
        for i, (k, v) in enumerate(bucket):
            if k == key:
                del bucket[i]
                self._size -= 1
                self._maybe_resize_down()
                return v
        raise KeyError(key)

    def contains(self, key) -> bool:
        """Return True if *key* exists in the map.

        Time: O(1) average
        """
        bucket = self._get_bucket(key)
        return any(k == key for k, _ in bucket)

    # ------------------------------------------------------------------
    # Resize
    # ------------------------------------------------------------------

    def resize(self, new_capacity: int) -> None:
        """Rehash all entries into a new backing array of *new_capacity* buckets.

        Time: O(n)
        """
        old_buckets = self._buckets
        self._capacity = max(new_capacity, 1)
        self._buckets = [[] for _ in range(self._capacity)]
        self._size = 0
        for bucket in old_buckets:
            for k, v in bucket:
                self.put(k, v)

    # ------------------------------------------------------------------
    # Utility / Dunder
    # ------------------------------------------------------------------

    def load_factor(self) -> float:
        """Return current load factor (size / capacity).

        Time: O(1)
        """
        return self._size / self._capacity

    def size(self) -> int:
        """Return the number of key-value pairs.

        Time: O(1)
        """
        return self._size

    def __len__(self) -> int:
        return self._size

    def __contains__(self, key) -> bool:
        return self.contains(key)

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, val) -> None:
        self.put(key, val)

    def __delitem__(self, key) -> None:
        self.delete(key)

    def items(self) -> Iterator[tuple]:
        """Yield all (key, value) pairs.

        Time: O(n)
        """
        for bucket in self._buckets:
            yield from bucket

    def keys(self) -> list:
        return [k for k, _ in self.items()]

    def values(self) -> list:
        return [v for _, v in self.items()]

    def __str__(self) -> str:
        """Show bucket structure for debugging.

        Example:
            ChainingHashMap  size=3  capacity=8  load=0.38
              [0]:
              [1]: ('b', 2)
              [2]: ('a', 1)
              ...
        """
        lines = [
            f"ChainingHashMap  size={self._size}  capacity={self._capacity}"
            f"  load={self.load_factor():.2f}"
        ]
        for i, bucket in enumerate(self._buckets):
            if bucket:
                pairs = ", ".join(f"({k!r}: {v!r})" for k, v in bucket)
                lines.append(f"  [{i:>3}]: {pairs}")
            else:
                lines.append(f"  [{i:>3}]: (empty)")
        return "\n".join(lines)

    def __repr__(self) -> str:
        return f"ChainingHashMap({dict(self.items())})"

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _bucket_index(self, key) -> int:
        return hash(key) % self._capacity

    def _get_bucket(self, key) -> list:
        return self._buckets[self._bucket_index(key)]

    def _maybe_resize_up(self) -> None:
        if self._size >= self._capacity * _CHAIN_LOAD_MAX:
            self.resize(self._capacity * 2)

    def _maybe_resize_down(self) -> None:
        min_cap = _CHAIN_INITIAL_CAPACITY
        if (
            self._size <= self._capacity * _CHAIN_LOAD_MIN
            and self._capacity // 2 >= min_cap
        ):
            self.resize(self._capacity // 2)


# ======================================================================
# Implementation 2 – Open Addressing (Linear Probing) HashMap
# ======================================================================

_PROBE_INITIAL_CAPACITY = 8
_PROBE_LOAD_MAX = 0.65   # lower threshold than chaining to keep probes short
_PROBE_LOAD_MIN = 0.15

_DELETED = object()   # sentinel for tombstone slots


class ProbingHashMap:
    """
    HashMap using open addressing with linear probing.

    On collision, we probe index (h + i) % capacity for i = 1, 2, ...
    until an empty slot is found.  Deleted slots are marked with a
    tombstone sentinel so that existing probe chains remain intact.

    Attributes:
        _keys     : backing array for keys   (None = empty, _DELETED = tombstone)
        _values   : backing array for values
        _capacity : number of slots
        _size     : number of live key-value pairs
        _deleted  : number of tombstone slots
    """

    def __init__(self, initial_capacity: int = _PROBE_INITIAL_CAPACITY):
        """Initialize an empty hash map.

        Args:
            initial_capacity: number of slots to allocate initially.

        Time: O(capacity)
        """
        self._capacity = max(initial_capacity, 1)
        self._keys:   list = [None] * self._capacity
        self._values: list = [None] * self._capacity
        self._size:    int = 0
        self._deleted: int = 0

    # ------------------------------------------------------------------
    # Core operations
    # ------------------------------------------------------------------

    def put(self, key, val) -> None:
        """Insert or update the value for *key*.

        Time: O(1) amortized average
        """
        self._maybe_resize_up()
        idx = self._find_slot_for_put(key)
        if self._keys[idx] is None or self._keys[idx] is _DELETED:
            if self._keys[idx] is _DELETED:
                self._deleted -= 1
            self._size += 1
        self._keys[idx] = key
        self._values[idx] = val

    def get(self, key) -> Any:
        """Return the value for *key*.

        Raises:
            KeyError: if *key* is not present.

        Time: O(1) average
        """
        idx = self._find_slot_for_get(key)
        if idx is None:
            raise KeyError(key)
        return self._values[idx]

    def delete(self, key) -> Any:
        """Remove *key* and return its value, leaving a tombstone.

        Raises:
            KeyError: if *key* is not present.

        Time: O(1) average
        """
        idx = self._find_slot_for_get(key)
        if idx is None:
            raise KeyError(key)
        val = self._values[idx]
        self._keys[idx] = _DELETED
        self._values[idx] = None
        self._size -= 1
        self._deleted += 1
        self._maybe_resize_down()
        return val

    def contains(self, key) -> bool:
        """Return True if *key* exists in the map.

        Time: O(1) average
        """
        return self._find_slot_for_get(key) is not None

    # ------------------------------------------------------------------
    # Resize
    # ------------------------------------------------------------------

    def resize(self, new_capacity: int) -> None:
        """Rehash all live entries into a new backing array.

        Time: O(n)
        """
        old_keys = self._keys
        old_vals = self._values
        old_cap  = self._capacity
        self._capacity = max(new_capacity, 1)
        self._keys   = [None] * self._capacity
        self._values = [None] * self._capacity
        self._size   = 0
        self._deleted = 0
        for i in range(old_cap):
            k = old_keys[i]
            if k is not None and k is not _DELETED:
                self.put(k, old_vals[i])

    # ------------------------------------------------------------------
    # Utility / Dunder
    # ------------------------------------------------------------------

    def load_factor(self) -> float:
        """Return (live + deleted) / capacity.  Used internally for resize.

        Time: O(1)
        """
        return (self._size + self._deleted) / self._capacity

    def size(self) -> int:
        """Return the number of live key-value pairs.

        Time: O(1)
        """
        return self._size

    def __len__(self) -> int:
        return self._size

    def __contains__(self, key) -> bool:
        return self.contains(key)

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, val) -> None:
        self.put(key, val)

    def __delitem__(self, key) -> None:
        self.delete(key)

    def items(self) -> Iterator[tuple]:
        """Yield all live (key, value) pairs.

        Time: O(capacity)
        """
        for i in range(self._capacity):
            k = self._keys[i]
            if k is not None and k is not _DELETED:
                yield k, self._values[i]

    def keys(self) -> list:
        return [k for k, _ in self.items()]

    def values(self) -> list:
        return [v for _, v in self.items()]

    def __str__(self) -> str:
        """Show slot-level view of the backing arrays.

        Example:
            ProbingHashMap  size=3  capacity=8  load=0.38
              [ 0]: EMPTY
              [ 1]: 'b' -> 2
              [ 2]: DELETED
              ...
        """
        lines = [
            f"ProbingHashMap  size={self._size}  capacity={self._capacity}"
            f"  load={self.load_factor():.2f}"
        ]
        for i in range(self._capacity):
            k = self._keys[i]
            if k is None:
                lines.append(f"  [{i:>3}]: EMPTY")
            elif k is _DELETED:
                lines.append(f"  [{i:>3}]: DELETED (tombstone)")
            else:
                lines.append(f"  [{i:>3}]: {k!r} -> {self._values[i]!r}")
        return "\n".join(lines)

    def __repr__(self) -> str:
        return f"ProbingHashMap({dict(self.items())})"

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _home_index(self, key) -> int:
        return hash(key) % self._capacity

    def _find_slot_for_put(self, key) -> int:
        """Return the index where *key* should be written.

        Scans past tombstones, but records the first tombstone as a
        candidate slot (reuse tombstone rather than extending the chain).
        """
        start = self._home_index(key)
        first_tombstone: int | None = None
        for i in range(self._capacity):
            idx = (start + i) % self._capacity
            k = self._keys[idx]
            if k is None:
                return first_tombstone if first_tombstone is not None else idx
            if k is _DELETED:
                if first_tombstone is None:
                    first_tombstone = idx
            elif k == key:
                return idx
        # All slots occupied (should not happen if resize works correctly)
        return first_tombstone if first_tombstone is not None else start

    def _find_slot_for_get(self, key) -> int | None:
        """Return the index of *key*, or None if absent."""
        start = self._home_index(key)
        for i in range(self._capacity):
            idx = (start + i) % self._capacity
            k = self._keys[idx]
            if k is None:
                return None          # end of probe chain
            if k is not _DELETED and k == key:
                return idx
        return None

    def _maybe_resize_up(self) -> None:
        if (self._size + self._deleted) >= self._capacity * _PROBE_LOAD_MAX:
            self.resize(self._capacity * 2)

    def _maybe_resize_down(self) -> None:
        min_cap = _PROBE_INITIAL_CAPACITY
        if (
            self._size <= self._capacity * _PROBE_LOAD_MIN
            and self._capacity // 2 >= min_cap
        ):
            self.resize(self._capacity // 2)


# ======================================================================
# Demo
# ======================================================================

if __name__ == "__main__":
    # ------------------------------------------------------------------ #
    # Chaining HashMap
    # ------------------------------------------------------------------ #
    print("=" * 60)
    print("ChainingHashMap Demo")
    print("=" * 60)

    cm = ChainingHashMap()

    entries = [("apple", 1), ("banana", 2), ("cherry", 3),
               ("date", 4), ("elderberry", 5)]
    for k, v in entries:
        cm.put(k, v)
        print(f"put({k!r}, {v})  -> size={cm.size()}  load={cm.load_factor():.2f}")

    print()
    print(cm)

    print(f"\nget('banana')       : {cm.get('banana')}")
    print(f"contains('cherry')  : {cm.contains('cherry')}")
    print(f"contains('fig')     : {cm.contains('fig')}")

    # Update existing key
    cm.put("banana", 99)
    print(f"\nAfter put('banana', 99), get('banana') = {cm.get('banana')}")

    # Delete
    val = cm.delete("date")
    print(f"delete('date') -> {val}  size={cm.size()}")

    print(f"\nkeys()   : {sorted(cm.keys())}")
    print(f"values() : {sorted(cm.values())}")

    # Trigger resize manually for demonstration
    print("\nAdding more entries to trigger resize...")
    for i in range(10):
        cm.put(f"key{i}", i * 10)
    print(f"size={cm.size()}  capacity={cm._capacity}  load={cm.load_factor():.2f}")

    print("\nError handling:")
    try:
        cm.get("nonexistent")
    except KeyError as e:
        print(f"  get('nonexistent') -> KeyError: {e}")
    try:
        cm.delete("ghost")
    except KeyError as e:
        print(f"  delete('ghost')    -> KeyError: {e}")

    # ------------------------------------------------------------------ #
    # Probing HashMap
    # ------------------------------------------------------------------ #
    print()
    print("=" * 60)
    print("ProbingHashMap (Linear Probing) Demo")
    print("=" * 60)

    pm = ProbingHashMap()

    for k, v in [("x", 10), ("y", 20), ("z", 30), ("w", 40)]:
        pm.put(k, v)
        print(f"put({k!r}, {v})  -> size={pm.size()}  load={pm.load_factor():.2f}")

    print()
    print(pm)

    print(f"\nget('y')            : {pm.get('y')}")
    print(f"contains('z')       : {pm.contains('z')}")
    print(f"contains('q')       : {pm.contains('q')}")

    pm.put("y", 200)
    print(f"\nAfter update put('y', 200), get('y') = {pm.get('y')}")

    val = pm.delete("x")
    print(f"delete('x') -> {val}   (tombstone left in slot)")
    print()
    print(pm)

    print(f"\nkeys()   : {sorted(pm.keys())}")
    print(f"values() : {sorted(pm.values())}")

    print("\nError handling:")
    try:
        pm.get("missing")
    except KeyError as e:
        print(f"  get('missing')  -> KeyError: {e}")
    try:
        pm.delete("missing")
    except KeyError as e:
        print(f"  delete('missing') -> KeyError: {e}")
