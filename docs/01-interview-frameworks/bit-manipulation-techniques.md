# Bit Manipulation Techniques: Working with Binary Representations

Master bit operations for efficient algorithms and clever solutions.

---

## Fundamental Bit Operations

### Basic Operations

```
AND (&): Both bits must be 1
  1010 & 1100 = 1000

OR (|): At least one bit is 1
  1010 | 1100 = 1110

XOR (^): Bits must be different
  1010 ^ 1100 = 0110

NOT (~): Flip all bits
  ~1010 = 0101 (in 4-bit)

Left Shift (<<): Multiply by 2^k
  1010 << 2 = 101000 (10 * 4 = 40)

Right Shift (>>): Divide by 2^k
  1010 >> 2 = 0010 (10 / 4 = 2)
```

---

## Bit Manipulation Tricks

### Check if Bit at Position i is Set

```python
def is_bit_set(num, i):
    return (num >> i) & 1 == 1
    # Or: (num & (1 << i)) != 0
```

### Set Bit at Position i

```python
def set_bit(num, i):
    return num | (1 << i)
```

### Clear Bit at Position i

```python
def clear_bit(num, i):
    return num & ~(1 << i)
```

### Toggle Bit at Position i

```python
def toggle_bit(num, i):
    return num ^ (1 << i)
```

### Check if Power of 2

```python
def is_power_of_2(n):
    return n > 0 and (n & (n - 1)) == 0
    # Trick: n & (n-1) removes the rightmost set bit
    # If n is power of 2, it has only 1 set bit, so n & (n-1) == 0
```

### Count Set Bits (Hamming Weight)

```python
def count_set_bits(n):
    count = 0
    while n:
        count += n & 1
        n >>= 1
    return count

# Or: Brian Kernighan's algorithm (only iterates over set bits)
def count_set_bits_fast(n):
    count = 0
    while n:
        n &= n - 1  # Remove rightmost set bit
        count += 1
    return count

# Or: Python built-in
count = bin(n).count('1')
```

### Get Position of Rightmost Set Bit

```python
def rightmost_set_bit(n):
    return n & -n
    # Trick: -n in two's complement flips all bits and adds 1
    # n & -n isolates the rightmost set bit
```

### Check if Bits i and j are Different

```python
def bits_different(num, i, j):
    return ((num >> i) & 1) != ((num >> j) & 1)
    # Or: ((num ^ (1 << i)) & (num ^ (1 << j))) != 0
```

---

## XOR Properties (Most Useful)

```
a ^ a = 0  (Any number XOR with itself = 0)
a ^ 0 = a  (Any number XOR 0 = itself)
a ^ b = b ^ a  (Commutative)
(a ^ b) ^ c = a ^ (b ^ c)  (Associative)

Key insight: a ^ a ^ b = b (cancels out duplicates)
```

### Find Single Number (all others appear twice)

```python
def single_number(nums):
    result = 0
    for num in nums:
        result ^= num
    return result

# [4, 1, 2, 1, 2] → 4 ^ 1 ^ 2 ^ 1 ^ 2 = 4 ^ (1^1) ^ (2^2) = 4 ^ 0 ^ 0 = 4
```

### Find Two Unique Numbers (all others appear twice)

```python
def find_two_unique(nums):
    xor_all = 0
    for num in nums:
        xor_all ^= num
    
    # xor_all = num1 ^ num2 (since all others cancel)
    # Find a set bit in xor_all (this bit differs between num1 and num2)
    rightmost_set = xor_all & -xor_all
    
    # Partition numbers by this bit and XOR separately
    num1, num2 = 0, 0
    for num in nums:
        if num & rightmost_set:
            num1 ^= num
        else:
            num2 ^= num
    
    return [num1, num2]
```

---

## Common Bit Manipulation Problems

| Problem | Technique | Trick |
|---------|-----------|-------|
| Power of 2 check | n & (n-1) == 0 | Removes rightmost set bit |
| Hamming weight | Count '1' bits | Brian Kernighan or built-in |
| Single number (duplicates) | XOR all | Duplicates cancel out |
| Two unique (duplicates) | XOR + partition | Find differing bit |
| Reverse bits | Shift and build | For each bit position |
| Missing number | XOR 0..n | All numbers 1..n except one |
| Gray code | i ^ (i >> 1) | Gray code = binary XOR right shift |
| Swap without temp | a ^= b; b ^= a; a ^= b | Uses XOR property |

---

## Integer Representation

### Two's Complement (Negative Numbers)

```
Positive: 5 = 0101
Negative: -5 = 1011 (flip bits + add 1)
           = NOT(0101) + 1
           = 1010 + 1
           = 1011
```

### Sign Extension

```python
# When converting short to int, preserve sign
# Arithmetic right shift (>>) preserves sign bit
# Logical right shift (>>>) zeros out high bits
```

---

## Bit Manipulation Checklist

- ✓ Know bit operations (AND, OR, XOR, NOT, shifts)
- ✓ Check/set/clear/toggle bits confidently
- ✓ Recognize power of 2 pattern
- ✓ Use XOR for finding unique elements
- ✓ Understand two's complement for negatives
- ✓ Brian Kernighan for counting bits
- ✓ Test on small examples (0, 1, -1)

