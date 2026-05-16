# Math & Number Theory: Essential Interview Techniques

Master mathematical concepts for algorithm and system design problems.

---

## GCD and LCM

### Euclidean Algorithm (GCD)

```python
def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

# gcd(48, 18) = gcd(18, 12) = gcd(12, 6) = gcd(6, 0) = 6
# Time: O(log min(a, b))
```

### Extended Euclidean Algorithm

```python
def extended_gcd(a, b):
    if b == 0:
        return a, 1, 0
    gcd_val, x1, y1 = extended_gcd(b, a % b)
    x = y1
    y = x1 - (a // b) * y1
    return gcd_val, x, y

# Returns: gcd, x, y such that a*x + b*y = gcd
# Used for: Modular inverse, Chinese Remainder Theorem
```

### LCM

```python
def lcm(a, b):
    return (a * b) // gcd(a, b)
```

---

## Prime Numbers

### Sieve of Eratosthenes

```python
def sieve(n):
    is_prime = [True] * (n + 1)
    is_prime[0] = is_prime[1] = False
    
    for i in range(2, int(n**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, n + 1, i):
                is_prime[j] = False
    
    return [i for i in range(n + 1) if is_prime[i]]

# Find all primes up to n in O(n log log n)
```

### Prime Factorization

```python
def prime_factorize(n):
    factors = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors[d] = factors.get(d, 0) + 1
            n //= d
        d += 1
    if n > 1:
        factors[n] = factors.get(n, 0) + 1
    return factors

# 12 = 2^2 * 3 → {2: 2, 3: 1}
```

---

## Modular Arithmetic

### Modular Exponentiation

```python
def pow_mod(base, exp, mod):
    result = 1
    base = base % mod
    while exp > 0:
        if exp % 2 == 1:
            result = (result * base) % mod
        exp = exp >> 1
        base = (base * base) % mod
    return result

# Compute base^exp % mod efficiently
# 2^100 % 1000 in O(log 100)
```

### Modular Inverse

```python
def mod_inverse(a, m):
    # Using extended GCD
    gcd_val, x, _ = extended_gcd(a, m)
    if gcd_val != 1:
        return None  # No inverse exists
    return (x % m + m) % m

# a^-1 (mod m) such that a * a^-1 ≡ 1 (mod m)
```

---

## Combinatorics

### Permutations & Combinations

```python
from math import factorial

def nPr(n, r):
    return factorial(n) // factorial(n - r)

def nCr(n, r):
    return factorial(n) // (factorial(r) * factorial(n - r))

# P(5, 3) = 60 (arrange 3 of 5 items)
# C(5, 3) = 10 (choose 3 of 5 items)
```

### Pascal's Triangle (Binomial Coefficients)

```python
def binomial(n):
    row = [1]
    for k in range(1, n + 1):
        row.append(row[-1] * (n - k + 1) // k)
    return row

# Row n: coefficients of (a+b)^n
# C(5, 0) = 1, C(5, 1) = 5, C(5, 2) = 10, ...
```

---

## Catalan Numbers

```python
def catalan(n):
    if n <= 1:
        return 1
    
    dp = [0] * (n + 1)
    dp[0] = dp[1] = 1
    
    for i in range(2, n + 1):
        for j in range(i):
            dp[i] += dp[j] * dp[i - 1 - j]
    
    return dp[n]

# Catalan(n) = C(2n, n) / (n+1)
# Uses: Binary trees, parenthesis matching, polygon triangulation
# Catalan(0..5) = 1, 1, 2, 5, 14, 42
```

---

## Number Theory Problems

| Problem | Technique | Example |
|---------|-----------|---------|
| **GCD/LCM** | Euclidean | gcd(48, 18) = 6 |
| **Prime check** | Trial division or Miller-Rabin | Is 97 prime? |
| **Factorization** | Trial or Pollard's rho | 12 = 2^2 * 3 |
| **Modular inverse** | Extended GCD | 3^-1 (mod 7) = 5 |
| **Power mod** | Fast exponentiation | 2^100 (mod 1000) |
| **Combinatorics** | DP or formulas | C(5, 3) = 10 |
| **Catalan** | DP | Catalan(5) = 42 |

---

## Math & Number Theory Checklist

- ✓ GCD using Euclidean algorithm
- ✓ Prime checking (trial division or Miller-Rabin)
- ✓ Sieve of Eratosthenes for range of primes
- ✓ Prime factorization
- ✓ Modular exponentiation for large powers
- ✓ Modular inverse for equations
- ✓ Combinatorics (P, C, factorial)
- ✓ Catalan numbers for structure counting
- ✓ Overflow handling (use modulo, long long)
- ✓ Tested on small examples

