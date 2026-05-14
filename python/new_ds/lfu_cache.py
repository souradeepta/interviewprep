"""
LFU (Least Frequently Used) Cache
===================================
Evicts the item that has been accessed the **fewest** number of times.
When multiple items have the same minimum frequency, the **least recently
used** (LRU) among them is evicted (LFU with LRU tiebreaking).

Two implementations are provided:
----------------------------------
1. LFUCacheSimple  — uses Counter + OrderedDict; clear and easy to read;
                     O(log n) amortized due to sorting/Counter updates.

2. LFUCacheOptimal — O(1) worst-case get and put using:
   - A hashmap: key -> (value, frequency)
   - A hashmap: frequency -> OrderedDict of keys (doubly-linked insertion order)
   - A min_freq tracker updated in O(1)

Time Complexity
---------------
                | get   | put
LFUCacheSimple  | O(1)  | O(n)  (finding min-freq victim)
LFUCacheOptimal | O(1)  | O(1)

Space Complexity: O(capacity) for both.

When to use LFU vs LRU
-----------------------
- LRU: Good for temporal locality (recently accessed items likely accessed again).
- LFU: Good for frequency locality (popular items should stay longer).
- LFU can be slow to "forget" old popular items — an item accessed 1000 times
  long ago won't be evicted until many new items accumulate higher counts.
"""

from collections import OrderedDict, defaultdict
from typing import Any, Dict, Optional


# ===========================================================================
# Implementation 1: Simple LFU (easier to understand)
# ===========================================================================

class LFUCacheSimple:
    """
    Simple LFU Cache using a frequency counter and ordered-dict per frequency.

    Uses Counter to track access counts and an OrderedDict to maintain
    insertion/access order within the same frequency bucket (for LRU tiebreaking).

    Parameters
    ----------
    capacity : int  Maximum number of items to hold before evicting.

    Example
    -------
    >>> c = LFUCacheSimple(2)
    >>> c.put(1, 10)
    >>> c.put(2, 20)
    >>> c.get(1)         # freq[1]=2, freq[2]=1
    10
    >>> c.put(3, 30)     # evicts key 2 (lowest freq)
    >>> c.get(2)
    -1
    """

    def __init__(self, capacity: int) -> None:
        if capacity <= 0:
            raise ValueError("Capacity must be a positive integer")
        self.capacity = capacity
        self._vals: Dict[Any, Any] = {}                    # key -> value
        self._freq: Dict[Any, int] = {}                    # key -> frequency count
        # freq_map[f] = OrderedDict of keys with frequency f (LRU order)
        self._freq_map: Dict[int, OrderedDict] = defaultdict(OrderedDict)
        self._min_freq: int = 0

    def _bump_freq(self, key: Any) -> None:
        """Increment frequency of an existing key."""
        f = self._freq[key]
        del self._freq_map[f][key]
        if not self._freq_map[f]:
            del self._freq_map[f]
            if self._min_freq == f:
                self._min_freq = f + 1
        self._freq[key] = f + 1
        self._freq_map[f + 1][key] = None  # OrderedDict used as ordered set

    def get(self, key: Any) -> Any:
        """
        Return the value of key, or -1 if not present.

        Also increments the access frequency of key.

        Time: O(1)
        """
        if key not in self._vals:
            return -1
        self._bump_freq(key)
        return self._vals[key]

    def put(self, key: Any, value: Any) -> None:
        """
        Insert or update key with value.

        If cache is at capacity, evict the LFU item (LRU tiebreaking).

        Time: O(1)
        """
        if key in self._vals:
            self._vals[key] = value
            self._bump_freq(key)
            return

        if len(self._vals) >= self.capacity:
            # Evict: remove the LRU item from the min-frequency bucket
            evict_key, _ = self._freq_map[self._min_freq].popitem(last=False)
            if not self._freq_map[self._min_freq]:
                del self._freq_map[self._min_freq]
            del self._vals[evict_key]
            del self._freq[evict_key]

        self._vals[key] = value
        self._freq[key] = 1
        self._freq_map[1][key] = None
        self._min_freq = 1  # new item always has frequency 1

    def __repr__(self) -> str:
        items = {k: (v, self._freq[k]) for k, v in self._vals.items()}
        return f"LFUCacheSimple(capacity={self.capacity}, items={items})"


# ===========================================================================
# Implementation 2: Optimal O(1) LFU
# ===========================================================================

class _DLinkedNode:
    """Doubly linked list node for O(1) insert/remove within frequency buckets."""
    __slots__ = ("key", "val", "freq", "prev", "next")

    def __init__(self, key=None, val=None, freq=0):
        self.key = key
        self.val = val
        self.freq = freq
        self.prev: Optional["_DLinkedNode"] = None
        self.next: Optional["_DLinkedNode"] = None


class _FreqBucket:
    """
    A doubly linked list used as an ordered set of cache entries with the
    same frequency.

    head.next ... tail.prev  = items in order from LRU (oldest) to MRU (newest).

    Insertion adds to the tail (MRU end); eviction removes from the head.next (LRU end).
    """

    def __init__(self):
        self.head = _DLinkedNode()  # sentinel head
        self.tail = _DLinkedNode()  # sentinel tail
        self.head.next = self.tail
        self.tail.prev = self.head
        self.size = 0

    def append(self, node: _DLinkedNode) -> None:
        """Add node to the MRU (tail) end."""
        node.prev = self.tail.prev
        node.next = self.tail
        self.tail.prev.next = node
        self.tail.prev = node
        self.size += 1

    def remove(self, node: _DLinkedNode) -> None:
        """Remove node from anywhere in the list in O(1)."""
        node.prev.next = node.next
        node.next.prev = node.prev
        node.prev = None
        node.next = None
        self.size -= 1

    def pop_lru(self) -> Optional[_DLinkedNode]:
        """Remove and return the LRU (head.next) node, or None if empty."""
        if self.size == 0:
            return None
        lru = self.head.next
        self.remove(lru)
        return lru

    def is_empty(self) -> bool:
        return self.size == 0


class LFUCacheOptimal:
    """
    O(1) get and put LFU Cache.

    Data structures
    ---------------
    key_map   : key -> _DLinkedNode  (fast O(1) node lookup)
    freq_map  : freq -> _FreqBucket  (doubly linked list per frequency)
    min_freq  : int  (the current minimum frequency in the cache)

    Invariants
    ----------
    - Every node in key_map is also in exactly one freq_map[node.freq] bucket.
    - min_freq always points to the frequency of the LFU item(s).
    - When a frequency bucket becomes empty and its freq == min_freq,
      min_freq is incremented (new inserts always start at freq=1, so
      after eviction min_freq is reset to 1 on the next put).

    Example
    -------
    >>> c = LFUCacheOptimal(3)
    >>> c.put(1, 10); c.put(2, 20); c.put(3, 30)
    >>> c.get(1); c.get(1); c.get(2)   # freqs: 1->3, 2->2, 3->1
    >>> c.put(4, 40)                    # evicts key 3 (freq=1, LRU)
    >>> c.get(3)
    -1
    """

    def __init__(self, capacity: int) -> None:
        if capacity <= 0:
            raise ValueError("Capacity must be a positive integer")
        self.capacity = capacity
        self.size = 0
        self.min_freq = 0
        self.key_map: Dict[Any, _DLinkedNode] = {}
        self.freq_map: Dict[int, _FreqBucket] = defaultdict(_FreqBucket)

    def _increment_freq(self, node: _DLinkedNode) -> None:
        """
        Move node from freq bucket f to bucket f+1.

        Update min_freq if the old bucket is now empty and it was the minimum.

        Time: O(1)
        """
        f = node.freq
        self.freq_map[f].remove(node)
        if self.freq_map[f].is_empty() and f == self.min_freq:
            self.min_freq += 1
        node.freq += 1
        self.freq_map[node.freq].append(node)

    def get(self, key: Any) -> Any:
        """
        Return the value for key, or -1 if absent.

        Increments key's frequency and updates min_freq accordingly.

        Time: O(1)
        """
        if key not in self.key_map:
            return -1
        node = self.key_map[key]
        self._increment_freq(node)
        return node.val

    def put(self, key: Any, value: Any) -> None:
        """
        Insert or update key with value.

        On capacity overflow, evict the least-frequently-used item,
        with LRU order as the tiebreaker.

        Time: O(1)
        """
        if key in self.key_map:
            node = self.key_map[key]
            node.val = value
            self._increment_freq(node)
            return

        if self.size >= self.capacity:
            # Evict LRU item from the min-frequency bucket
            evicted = self.freq_map[self.min_freq].pop_lru()
            if evicted is not None:
                del self.key_map[evicted.key]
                self.size -= 1

        # Insert new node with frequency 1
        new_node = _DLinkedNode(key=key, val=value, freq=1)
        self.key_map[key] = new_node
        self.freq_map[1].append(new_node)
        self.min_freq = 1  # new item has the lowest possible frequency
        self.size += 1

    def __repr__(self) -> str:
        items = {k: (n.val, n.freq) for k, n in self.key_map.items()}
        return f"LFUCacheOptimal(capacity={self.capacity}, min_freq={self.min_freq}, items={items})"


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("LFU CACHE DEMO")
    print("=" * 60)

    def run_scenario(CacheClass, label: str) -> None:
        print(f"\n{'=' * 40}")
        print(f"{label}")
        print(f"{'=' * 40}")

        cache = CacheClass(capacity=3)
        print(f"\nCapacity = 3. Put keys 1, 2, 3.")
        cache.put(1, "one")
        cache.put(2, "two")
        cache.put(3, "three")
        print(cache)

        print("\nAccess key 1 twice, key 2 once:")
        print(f"  get(1) -> {cache.get(1)}")
        print(f"  get(1) -> {cache.get(1)}")
        print(f"  get(2) -> {cache.get(2)}")
        print(f"  Frequencies now: 1->3, 2->2, 3->1")
        print(cache)

        print("\nPut key 4 (should evict key 3, the LFU with freq=1):")
        cache.put(4, "four")
        print(f"  get(3) -> {cache.get(3)}  (expected -1, evicted)")
        print(f"  get(4) -> {cache.get(4)}  (expected 'four')")
        print(cache)

        print("\nPut key 5 (ties: keys 2 and 4 both have freq=1; evict LRU among them = key 4):")
        # After above: freq[1]=3, freq[2]=2, freq[4]=1. So 4 is LFU.
        cache.put(5, "five")
        print(f"  get(4) -> {cache.get(4)}  (expected -1, evicted)")
        print(f"  get(5) -> {cache.get(5)}  (expected 'five')")
        print(cache)

    run_scenario(LFUCacheSimple, "LFUCacheSimple (Counter + OrderedDict)")
    run_scenario(LFUCacheOptimal, "LFUCacheOptimal (O(1) doubly linked list)")

    # --- Frequency-based eviction showcase ---
    print("\n" + "=" * 60)
    print("FREQUENCY EVICTION SHOWCASE")
    print("=" * 60)
    c = LFUCacheOptimal(capacity=4)
    ops = [
        ("put", "a", "alpha"), ("put", "b", "beta"), ("put", "c", "gamma"), ("put", "d", "delta"),
        ("get", "a", None), ("get", "a", None), ("get", "a", None),  # a -> freq=4
        ("get", "b", None), ("get", "b", None),                       # b -> freq=3
        ("get", "c", None),                                            # c -> freq=2
        # d stays at freq=1 — will be evicted first
        ("put", "e", "epsilon"),  # should evict d
    ]
    print(f"\n{'Op':10} {'Key':5} {'Result':10} State")
    print("-" * 60)
    for op in ops:
        if op[0] == "put":
            _, k, v = op
            c.put(k, v)
            freqs = {key: node.freq for key, node in c.key_map.items()}
            print(f"put        {k!r:5} {'':10} freqs={freqs}")
        else:
            _, k, _ = op
            result = c.get(k)
            freqs = {key: node.freq for key, node in c.key_map.items()}
            print(f"get        {k!r:5} {str(result):10} freqs={freqs}")

    print(f"\nget('d') -> {c.get('d')}  (evicted as LFU with freq=1)")
    print(f"get('e') -> {c.get('e')}  (still present)")

    # --- Performance comparison ---
    import time, random
    print("\n--- Performance: Simple vs Optimal (10,000 random get/put) ---")
    ITERS = 10_000
    CAP = 512

    for CacheClass, label in [(LFUCacheSimple, "Simple "), (LFUCacheOptimal, "Optimal")]:
        cache = CacheClass(CAP)
        t0 = time.perf_counter()
        for _ in range(ITERS):
            k = random.randint(0, CAP * 2)
            if random.random() < 0.5:
                cache.put(k, k)
            else:
                cache.get(k)
        elapsed = time.perf_counter() - t0
        print(f"  {label}: {elapsed*1000:.2f} ms for {ITERS:,} ops")

    print("\nDone.")
