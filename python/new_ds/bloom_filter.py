"""
Bloom Filter
============
A space-efficient probabilistic data structure used to test whether an element
is a member of a set. It can produce **false positives** (reports "maybe in
set" when element was never added) but **never false negatives** (if the filter
says "not in set", the element is definitely absent).

How it works
------------
- Maintains a bit array of m bits, initially all 0.
- Uses k independent hash functions h1 … hk, each mapping an item to [0, m).
- **add(item)**: set bits h1(item), h2(item), …, hk(item) to 1.
- **contains(item)**: return True iff ALL k bits are 1. If any bit is 0 the
  item was definitely not added. If all are 1 it was *probably* added.

False-positive probability
--------------------------
  p ≈ (1 − e^{−kn/m})^k

where n is the number of items inserted.  Given m and n, the optimal k is:
  k_opt = (m/n) * ln 2

For typical deployments (p ≈ 1%):  m ≈ 9.6 * n bits.

Time Complexity
---------------
| Operation         | Time    |
|-------------------|---------|
| add(item)         | O(k)    |
| contains(item)    | O(k)    |
| false_positive_rate| O(1)   |

Space Complexity
----------------
O(m) bits = O(m/8) bytes, independent of item size.

Design: k hash functions are simulated using (hash(item) + i * hash2(item)) % m
(double hashing), which is equivalent to k independent hash functions for most
practical purposes.
"""

import math
from typing import List


class BitArray:
    """
    Compact bit array backed by a Python bytearray.

    Stores m bits using ceil(m/8) bytes.  Each bit is accessed by index.

    Example
    -------
    >>> ba = BitArray(16)
    >>> ba.set(3)
    >>> ba.get(3)
    True
    >>> ba.get(4)
    False
    """

    def __init__(self, size: int) -> None:
        """
        Parameters
        ----------
        size : int  Number of bits to allocate.
        """
        if size <= 0:
            raise ValueError("BitArray size must be positive")
        self.size = size
        self._data = bytearray(math.ceil(size / 8))

    def set(self, index: int) -> None:
        """Set bit at position index to 1."""
        if not 0 <= index < self.size:
            raise IndexError(f"Bit index {index} out of range [0, {self.size})")
        byte_idx, bit_idx = divmod(index, 8)
        self._data[byte_idx] |= (1 << bit_idx)

    def get(self, index: int) -> bool:
        """Return True if bit at position index is 1."""
        if not 0 <= index < self.size:
            raise IndexError(f"Bit index {index} out of range [0, {self.size})")
        byte_idx, bit_idx = divmod(index, 8)
        return bool(self._data[byte_idx] & (1 << bit_idx))

    def count_set(self) -> int:
        """Return the number of bits currently set to 1."""
        return sum(bin(byte).count("1") for byte in self._data)

    def __str__(self) -> str:
        """Return a string of '0'/'1' characters for the first min(size,64) bits."""
        display_len = min(self.size, 64)
        bits = "".join("1" if self.get(i) else "0" for i in range(display_len))
        suffix = "..." if self.size > 64 else ""
        return bits + suffix

    def __repr__(self) -> str:
        return f"BitArray(size={self.size}, set={self.count_set()})"


class BloomFilter:
    """
    Bloom Filter using k simulated independent hash functions over a bit array.

    Double-hashing scheme:
        h_i(x) = (hash1(x) + i * hash2(x)) % m    for i in 0 … k-1

    where:
        hash1(x) = hash(x)
        hash2(x) = hash(x + "_salt")   (a different hash value)

    This avoids storing k separate hash functions while achieving near-optimal
    independence.

    Parameters
    ----------
    capacity    : Expected number of items to insert (n).
    error_rate  : Desired false-positive probability (0 < p < 1).

    Derived parameters (computed automatically):
        m = -n * ln(p) / (ln 2)^2      — optimal bit array size
        k = (m/n) * ln 2               — optimal number of hash functions

    Example
    -------
    >>> bf = BloomFilter(capacity=1000, error_rate=0.01)
    >>> bf.add("apple")
    >>> bf.contains("apple")
    True
    >>> bf.contains("banana")  # likely False (not added)
    False
    """

    def __init__(self, capacity: int = 1000, error_rate: float = 0.01) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be a positive integer")
        if not (0 < error_rate < 1):
            raise ValueError("error_rate must be in (0, 1)")

        self.capacity = capacity
        self.error_rate = error_rate

        # Optimal bit array size
        self.m: int = self._optimal_m(capacity, error_rate)
        # Optimal number of hash functions
        self.k: int = self._optimal_k(self.m, capacity)

        self._bits = BitArray(self.m)
        self._count = 0  # number of items added

    # ------------------------------------------------------------------
    # Optimal parameter formulas
    # ------------------------------------------------------------------

    @staticmethod
    def _optimal_m(n: int, p: float) -> int:
        """m = ceil( -n * ln(p) / (ln 2)^2 )"""
        return max(1, math.ceil(-n * math.log(p) / (math.log(2) ** 2)))

    @staticmethod
    def _optimal_k(m: int, n: int) -> int:
        """k = round( (m/n) * ln 2 ), at least 1"""
        return max(1, round((m / n) * math.log(2)))

    # ------------------------------------------------------------------
    # Hash functions (double hashing)
    # ------------------------------------------------------------------

    def _hash_positions(self, item) -> List[int]:
        """
        Return k bit positions for item using double hashing.

        h_i(item) = (hash1 + i * hash2) % m
        """
        item_str = str(item)
        h1 = hash(item_str) % self.m
        h2 = hash(item_str + "\x00salt") % self.m
        # h2 must be odd (co-prime to m if m is a power of 2) to cover all positions
        if h2 == 0:
            h2 = 1
        return [(h1 + i * h2) % self.m for i in range(self.k)]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def add(self, item) -> None:
        """
        Add item to the Bloom Filter by setting k bit positions.

        Time: O(k)
        """
        for pos in self._hash_positions(item):
            self._bits.set(pos)
        self._count += 1

    def contains(self, item) -> bool:
        """
        Test membership.

        Returns
        -------
        True  — item was *probably* added (may be a false positive).
        False — item was *definitely not* added (no false negatives).

        Time: O(k)
        """
        return all(self._bits.get(pos) for pos in self._hash_positions(item))

    def false_positive_rate(self) -> float:
        """
        Empirical estimate of the current false-positive probability.

        Uses the formula p ≈ (1 − e^{−kn/m})^k where n = items inserted so far.

        Time: O(1)
        """
        if self._count == 0:
            return 0.0
        exponent = -self.k * self._count / self.m
        return (1 - math.exp(exponent)) ** self.k

    def __len__(self) -> int:
        """Return number of items added (approximate — duplicates counted)."""
        return self._count

    def __str__(self) -> str:
        set_bits = self._bits.count_set()
        fill_pct = 100 * set_bits / self.m
        return (
            f"BloomFilter("
            f"m={self.m} bits, k={self.k} hashes, "
            f"items_added={self._count}, "
            f"bits_set={set_bits} ({fill_pct:.1f}%), "
            f"est_fp_rate={self.false_positive_rate():.4%})\n"
            f"Bit array: [{self._bits}]"
        )

    def __repr__(self) -> str:
        return (f"BloomFilter(capacity={self.capacity}, error_rate={self.error_rate}, "
                f"m={self.m}, k={self.k})")


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("BLOOM FILTER DEMO")
    print("=" * 60)

    # --- Basic functionality ---
    print("\n--- Basic add / contains ---")
    bf = BloomFilter(capacity=100, error_rate=0.01)
    print(f"Configured: m={bf.m} bits, k={bf.k} hash functions")

    words = ["apple", "banana", "cherry", "date", "elderberry"]
    for w in words:
        bf.add(w)
    print(f"Added: {words}")

    for w in words:
        print(f"  contains({w!r:12}) -> {bf.contains(w)}")

    not_added = ["fig", "grape", "honeydew", "kiwi", "lemon"]
    print(f"\nChecking items NOT added:")
    for w in not_added:
        print(f"  contains({w!r:12}) -> {bf.contains(w)}")

    print(f"\n{bf}")

    # --- False positive demonstration ---
    print("\n--- False positive rate experiment ---")
    import random, string

    def random_word(length: int = 8) -> str:
        return "".join(random.choices(string.ascii_lowercase, k=length))

    N = 1000
    error_rate = 0.02
    bf2 = BloomFilter(capacity=N, error_rate=error_rate)

    added_set = set()
    for _ in range(N):
        w = random_word()
        added_set.add(w)
        bf2.add(w)

    # Generate items definitely not in the filter
    test_negatives = []
    while len(test_negatives) < 5000:
        w = random_word()
        if w not in added_set:
            test_negatives.append(w)

    false_positives = sum(1 for w in test_negatives if bf2.contains(w))
    measured_fp = false_positives / len(test_negatives)

    print(f"Target error rate:   {error_rate:.2%}")
    print(f"Theoretical fp rate: {bf2.false_positive_rate():.4%}")
    print(f"Measured fp rate:    {measured_fp:.4%}  ({false_positives}/{len(test_negatives)} false positives)")
    print(f"\n{bf2}")

    # --- BitArray demo ---
    print("\n--- BitArray demo ---")
    ba = BitArray(32)
    for i in [0, 5, 15, 31]:
        ba.set(i)
    print(f"BitArray(32) after setting bits 0,5,15,31: [{ba}]")
    print(f"  get(5)={ba.get(5)}, get(6)={ba.get(6)}, count_set={ba.count_set()}")

    print("\nDone.")
