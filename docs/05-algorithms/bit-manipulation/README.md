---
Level: L4-L5
Time: ~20 min
---

# Bit Manipulation

## Quick Summary

Bit manipulation uses bitwise operators (AND, OR, XOR, shifts) to solve problems in O(1) space with minimal branching. Core uses: checking/setting/clearing bits, counting set bits, generating subsets, and the XOR identity `a ^ a = 0` for finding unique elements.

---

## Bit Manipulation Cheat Sheet

| Operation | Code | Use case |
|-----------|------|---------|
| Check bit i | `n & (1 << i)` | Is bit i set? Returns non-zero if yes |
| Set bit i | `n \| (1 << i)` | Turn on bit i |
| Clear bit i | `n & ~(1 << i)` | Turn off bit i |
| Toggle bit i | `n ^ (1 << i)` | Flip bit i |
| Lowest set bit | `n & (-n)` | Isolate rightmost 1; used in Fenwick trees |
| Clear lowest set bit | `n & (n - 1)` | Removes rightmost 1; used to count set bits |
| Is power of 2? | `n > 0 and n & (n-1) == 0` | Powers of 2 have exactly one bit set |
| XOR to find unique | `a ^ a == 0`, `a ^ 0 == a` | Cancel duplicates, find singleton |
| Count set bits (Python) | `bin(n).count('1')` | Direct; also `int.bit_count()` in Python 3.10+ |
| Count set bits (fast) | Brian Kernighan algorithm | Loops only once per set bit |
| All subsets of n bits | `for mask in range(1 << n)` | Enumerate 2^n subsets |
| Bit length | `n.bit_length()` | Equivalent to `floor(log2(n)) + 1` |

---

## Core Operations Explained

### XOR Properties
```
a ^ 0   = a          (identity)
a ^ a   = 0          (self-inverse)
a ^ b ^ a = b        (commutativity + self-inverse)
XOR is commutative and associative
```

**Application:** XOR all elements in an array — duplicates cancel, leaving the unique element.

### Two's Complement and Negative Numbers
In Python, integers have arbitrary precision and `-n` is always `~n + 1`. The trick `n & (-n)` isolates the lowest set bit because `-n` flips all bits and adds 1, which means everything below the lowest set bit gets zeroed.

```
n    =  ...1 0 1 1 0 0  (some bits)
-n   =  ...0 1 0 1 0 0  (flip all bits, add 1)
n&-n =  ...0 0 0 1 0 0  (only lowest set bit remains)
```

---

## Algorithms

### 1. Brian Kernighan Bit Count

**Approach:** Repeatedly clear the lowest set bit with `n = n & (n-1)` and count iterations.

**Time:** O(k) where k = number of set bits | **Space:** O(1)

```python
def count_bits_kernighan(n: int) -> int:
    count = 0
    while n:
        n &= n - 1    # clear lowest set bit
        count += 1
    return count


# Verify
print(count_bits_kernighan(13))  # 13 = 1101 → 3 set bits
print(count_bits_kernighan(0))   # 0
print(bin(13).count('1'))        # 3 — same result, simpler in Python
```

---

### 2. Subset Generation via Bitmask

**Approach:** Every integer from `0` to `2^n - 1` represents a subset. Bit `i` being set means element `i` is included.

**Time:** O(2^n * n) to enumerate and process all subsets | **Space:** O(n) for each subset

```python
def generate_subsets(nums: list) -> list[list]:
    n = len(nums)
    result = []
    for mask in range(1 << n):          # 0 to 2^n - 1
        subset = []
        for i in range(n):
            if mask & (1 << i):         # bit i is set
                subset.append(nums[i])
        result.append(subset)
    return result


# Example
print(generate_subsets([1, 2, 3]))
# [[], [1], [2], [1,2], [3], [1,3], [2,3], [1,2,3]]
```

---

### 3. XOR Tricks

```python
# Find the single number in an array where all others appear twice
def single_number(nums: list[int]) -> int:
    result = 0
    for n in nums:
        result ^= n     # duplicates cancel: a ^ a = 0
    return result

print(single_number([4, 1, 2, 1, 2]))  # 4

# Swap two variables without temp
def swap_xor(a: int, b: int) -> tuple[int, int]:
    a ^= b
    b ^= a    # b = b ^ (a ^ b) = a
    a ^= b    # a = (a ^ b) ^ a = b
    return a, b

# Check if two integers have opposite signs
def opposite_signs(a: int, b: int) -> bool:
    return (a ^ b) < 0    # different sign bits → XOR of sign bits = 1
```

---

## Worked Problems

### Problem 1: Single Number — LC #136

**Section 1 — Understand the problem.**
Every element in `nums` appears twice except one. Find the element that appears only once. Must run in O(n) time and O(1) space.

**Section 2 — Examples.**
```
[2, 2, 1]         → 1
[4, 1, 2, 1, 2]   → 4
[1]               → 1
```

**Section 3 — Constraints & edge cases.**
- 1 ≤ len(nums) ≤ 3 * 10^4
- Guaranteed exactly one element appears once
- Cannot use a hash map (O(n) space would be too easy)

**Section 4 — Approach.**
XOR all elements. Pairs cancel (`a ^ a = 0`). The remaining value is the unique element.

**Section 5 — Code.**
```python
def singleNumber(nums: list[int]) -> int:
    result = 0
    for n in nums:
        result ^= n
    return result

# One-liner
from functools import reduce
import operator
def singleNumber_v2(nums: list[int]) -> int:
    return reduce(operator.xor, nums)
```

**Section 6 — Complexity.**
Time O(n), Space O(1).

---

### Problem 2: Number of 1 Bits — LC #191

**Section 1 — Understand the problem.**
Return the number of set bits (Hamming weight) in the binary representation of `n`.

**Section 2 — Examples.**
```
n = 11  (binary: 1011) → 3
n = 128 (binary: 10000000) → 1
n = 2147483645 (binary: 1111111111111111111111111111101) → 30
```

**Section 3 — Constraints & edge cases.**
- 0 ≤ n ≤ 2^31 - 1
- n = 0 → 0

**Section 4 — Approach.**
Brian Kernighan: `n & (n-1)` clears the lowest set bit. Count how many times until `n` becomes 0.

**Section 5 — Code.**
```python
def hammingWeight(n: int) -> int:
    count = 0
    while n:
        n &= n - 1
        count += 1
    return count

# Python 3.10+ built-in
def hammingWeight_builtin(n: int) -> int:
    return n.bit_count()
```

**Section 6 — Complexity.**
Time O(k) where k = number of set bits (at most 32 for 32-bit input), Space O(1).

---

### Problem 3: Subsets — LC #78

**Section 1 — Understand the problem.**
Return all possible subsets (the power set) of `nums`. The solution set must not contain duplicate subsets. Return in any order.

**Section 2 — Examples.**
```
[1,2,3] → [[],[1],[2],[1,2],[3],[1,3],[2,3],[1,2,3]]
[0]     → [[],[0]]
```

**Section 3 — Constraints & edge cases.**
- 1 ≤ len(nums) ≤ 10
- All elements unique
- `2^10 = 1024` subsets max

**Section 4 — Approach.**
Bitmask enumeration: for each integer `mask` from `0` to `2^n - 1`, include `nums[i]` when bit `i` is set in `mask`.

**Section 5 — Code.**
```python
def subsets(nums: list[int]) -> list[list[int]]:
    n = len(nums)
    result = []
    for mask in range(1 << n):
        subset = [nums[i] for i in range(n) if mask & (1 << i)]
        result.append(subset)
    return result
```

**Section 6 — Complexity.**
Time O(n * 2^n) — `n` bits checked per mask, `2^n` masks. Space O(n * 2^n) for the output.

---

## Common Mistakes

1. **Operator precedence:** `n & 1 == 0` is parsed as `n & (1 == 0)` which is `n & False` = `n & 0` = `0` — always zero. Always wrap bitwise operations in parentheses: `(n & 1) == 0`.

2. **Negative numbers in C++:** Right-shifting a negative signed integer is implementation-defined in C++ (arithmetic vs. logical shift). In Python, right shift is always arithmetic (preserves sign bit), and integers are arbitrary precision — but bit tricks like `n & (-n)` work correctly.

3. **Forgetting XOR is its own inverse:** `a ^ b ^ a == b`. This catches people off-guard in multi-step problems. If you XOR the same value twice anywhere in a sequence, it cancels.

4. **Using `n & (n-1)` to check bit 0:** `n & (n-1)` clears the *lowest* set bit, which is not necessarily bit 0. To check if bit 0 is set, use `n & 1`.

5. **Subset enumeration off-by-one:** Masks range from `0` to `(1 << n) - 1` inclusive. `range(1 << n)` is correct. A common bug is `range(1 << n - 1)` which is `range(1 << (n-1))` due to precedence, giving only half the subsets.

6. **Assuming `~n == -n`:** In Python (and two's complement systems), `~n == -(n+1)`, not `-n`. The bit complement of 5 (`101`) is `-(5+1) = -6`. Use `-n` for negation, `~n` only when you want bit flipping.

---

## Interview Q&A

**Q1: What does `n & (n-1)` do and why?**
It clears the lowest set bit of `n`. Subtracting 1 from `n` flips the lowest set bit to 0 and sets all lower bits to 1. ANDing with the original `n` preserves higher bits and zeroes out the lowest set bit and everything below it. Application: count set bits in O(k) iterations, check if `n` is a power of 2 (`n > 0 and n & (n-1) == 0`).

**Q2: How do you generate all subsets of a set using bitmasks?**
For a set of `n` elements, iterate `mask` from `0` to `2^n - 1`. Each mask represents a subset: element `i` is included when bit `i` of `mask` is set. This gives all `2^n` subsets in O(n * 2^n) time.

**Q3: Why does XOR find the single number in an array of pairs?**
XOR is commutative, associative, and self-inverse (`a ^ a = 0`, `a ^ 0 = a`). XORing all elements, duplicate pairs cancel to 0, leaving only the unique element.

**Q4: What is `n & (-n)` used for?**
It isolates the lowest set bit of `n`. In two's complement, `-n = ~n + 1`. The bit flip inverts all bits, and adding 1 restores bits above the lowest set bit while leaving exactly the lowest set bit set. Critical operation in Fenwick (Binary Indexed) trees for advancing/retreating indices.

**Q5: How do you check if exactly one bit is set (n is a power of 2)?**
`n > 0 and (n & (n-1)) == 0`. The `n > 0` guard handles the case `n = 0` (zero is not a power of 2 but `0 & (-1) = 0` would incorrectly pass otherwise).

**Q6: Can bit manipulation be used for set intersection and union?**
Yes, when elements are integers in a small range `[0, W)`. Represent the set as a bitmask of width W. Union = `A | B`, intersection = `A & B`, difference = `A & ~B`, complement = `~A & ((1<<W)-1)`. This is why bitsets are used for graph problems with small vertex counts and for DP over subsets (`n ≤ 20`).

**Q7: What is the Hamming distance between two numbers?**
The number of bit positions where they differ. Compute `xor = a ^ b`, then count set bits in `xor`. `bin(a ^ b).count('1')` in Python.
