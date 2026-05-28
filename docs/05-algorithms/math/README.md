---
Level: L4-L5
Time: ~20 min
---

# Math Algorithms

## Quick Summary

Number theory primitives — GCD, primes, modular arithmetic, and combinatorics — appear in 10-15% of coding interviews, usually embedded in larger problems. Knowing O(log n) GCD, O(n log log n) sieve, and O(log b) modular exponentiation is sufficient for FAANG-level interviews.

---

## Quick Reference

| Operation | Algorithm | Time | Notes |
|-----------|-----------|------|-------|
| GCD(a, b) | Euclidean | O(log min(a,b)) | `math.gcd` in Python |
| LCM(a, b) | Via GCD | O(log min(a,b)) | `a*b // gcd(a,b)` — overflow risk in C++/Java |
| All primes ≤ n | Sieve of Eratosthenes | O(n log log n) | Space O(n) |
| Is n prime? | Trial division | O(√n) | Check up to √n |
| Prime factorization | Trial division | O(√n) | Divide out each factor |
| a^b mod m | Fast exponentiation | O(log b) | `pow(a, b, m)` in Python |
| C(n, k) mod m | DP table | O(nk) | Pascal's triangle, avoids overflow |
| C(n, k) exact | `math.comb` | O(k) | Python 3.8+ |

---

## Algorithms

### 1. GCD and LCM

**Euclidean algorithm:** `gcd(a, b) = gcd(b, a % b)`, base case `gcd(a, 0) = a`.

**Why it works:** `gcd(a, b)` divides any linear combination of `a` and `b`, including `a - qb = a % b`. So `gcd(a, b) = gcd(b, a % b)`.

```python
import math

# Python built-in (use this in interviews)
print(math.gcd(48, 18))   # 6
print(math.lcm(4, 6))     # 12  (Python 3.9+)

# Manual implementation (for explanation)
def gcd(a: int, b: int) -> int:
    while b:
        a, b = b, a % b
    return a

def lcm(a: int, b: int) -> int:
    return a * b // gcd(a, b)

# Edge cases
print(gcd(0, 5))    # 5  — gcd(0, n) = n by convention
print(gcd(7, 7))    # 7
print(lcm(0, 5))    # 0  — lcm(0, n) = 0
```

---

### 2. Sieve of Eratosthenes

**Approach:** Mark all multiples of each prime starting from 2. Remaining unmarked numbers are prime.

**Time:** O(n log log n) | **Space:** O(n)

```python
def sieve(n: int) -> list[int]:
    """Returns sorted list of all primes <= n."""
    if n < 2:
        return []
    is_prime = [True] * (n + 1)
    is_prime[0] = is_prime[1] = False

    # Only need to sieve up to sqrt(n)
    p = 2
    while p * p <= n:
        if is_prime[p]:
            # Mark multiples starting from p^2 (smaller ones already marked)
            for multiple in range(p * p, n + 1, p):
                is_prime[multiple] = False
        p += 1

    return [i for i in range(2, n + 1) if is_prime[i]]


# Example
primes = sieve(50)
print(primes)
# [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
print(len(sieve(1000000)))  # 78498 primes below 1 million
```

**Variant — segmented sieve** for very large `n` (> 10^7): generate primes up to √n, then sieve segments of size √n. Memory usage drops from O(n) to O(√n).

---

### 3. Modular Arithmetic

**Key rules:**
```
(a + b) % m == ((a % m) + (b % m)) % m
(a * b) % m == ((a % m) * (b % m)) % m
(a - b) % m == ((a % m) - (b % m) + m) % m   # +m to stay positive
```

**Fast modular exponentiation:** Compute `a^b mod m` in O(log b) using repeated squaring.

```python
# Python built-in (ALWAYS use this — it handles large numbers efficiently)
print(pow(2, 10, 1000))    # 24  (2^10 = 1024, 1024 % 1000 = 24)
print(pow(2, 100, 10**9))  # fast even for huge exponents

# Manual implementation (for explanation)
def mod_pow(base: int, exp: int, mod: int) -> int:
    result = 1
    base %= mod
    while exp > 0:
        if exp & 1:               # if current bit is set
            result = result * base % mod
        base = base * base % mod  # square the base
        exp >>= 1                 # move to next bit
    return result


# Modular inverse (when mod is prime): Fermat's little theorem
# a^(m-1) ≡ 1 (mod m)  →  a^(-1) ≡ a^(m-2) (mod m)
def mod_inverse(a: int, mod: int) -> int:
    """mod must be prime."""
    return pow(a, mod - 2, mod)


# Combinations mod p (for large n, k)
MOD = 10**9 + 7

def precompute_factorials(n: int, mod: int) -> tuple[list[int], list[int]]:
    fact = [1] * (n + 1)
    for i in range(1, n + 1):
        fact[i] = fact[i-1] * i % mod
    inv_fact = [1] * (n + 1)
    inv_fact[n] = pow(fact[n], mod - 2, mod)
    for i in range(n - 1, -1, -1):
        inv_fact[i] = inv_fact[i + 1] * (i + 1) % mod
    return fact, inv_fact

def comb_mod(n: int, k: int, fact: list[int], inv_fact: list[int], mod: int) -> int:
    if k < 0 or k > n:
        return 0
    return fact[n] * inv_fact[k] % mod * inv_fact[n - k] % mod
```

---

## Worked Problems

### Problem 1: Count Primes — LC #204

**Section 1 — Understand the problem.**
Return the count of prime numbers strictly less than `n`.

**Section 2 — Examples.**
```
n = 10 → 4  (2, 3, 5, 7)
n = 0  → 0
n = 1  → 0
```

**Section 3 — Constraints & edge cases.**
- 0 ≤ n ≤ 5 * 10^6
- n = 0 or n = 1 → 0

**Section 4 — Approach.**
Sieve of Eratosthenes on range `[0, n-1]`.

**Section 5 — Code.**
```python
def countPrimes(n: int) -> int:
    if n < 2:
        return 0
    is_prime = [True] * n
    is_prime[0] = is_prime[1] = False
    p = 2
    while p * p < n:
        if is_prime[p]:
            for multiple in range(p * p, n, p):
                is_prime[multiple] = False
        p += 1
    return sum(is_prime)
```

**Section 6 — Complexity.**
Time O(n log log n), Space O(n).

---

### Problem 2: Pow(x, n) — LC #50

**Section 1 — Understand the problem.**
Implement `pow(x, n)` without using the built-in. `n` can be negative.

**Section 2 — Examples.**
```
x=2.0, n=10  → 1024.0
x=2.1, n=3   → 9.261000...
x=2.0, n=-2  → 0.25
```

**Section 3 — Constraints & edge cases.**
- -100.0 ≤ x ≤ 100.0
- -2^31 ≤ n ≤ 2^31 - 1
- Negative n → compute `1 / pow(x, -n)`
- n = 0 → return 1.0

**Section 4 — Approach.**
Fast exponentiation by repeated squaring. Handle negative exponent by inverting x.

**Section 5 — Code.**
```python
def myPow(x: float, n: int) -> float:
    if n < 0:
        x = 1 / x
        n = -n

    result = 1.0
    while n:
        if n & 1:
            result *= x
        x *= x
        n >>= 1
    return result
```

**Section 6 — Complexity.**
Time O(log n), Space O(1).

---

### Problem 3: Ugly Number II — LC #264

**Section 1 — Understand the problem.**
An ugly number has only 2, 3, 5 as prime factors. Return the n-th ugly number (1-indexed, 1 is considered ugly).

**Section 2 — Examples.**
```
n=1 → 1
n=10 → 12   (sequence: 1,2,3,4,5,6,8,9,10,12)
```

**Section 3 — Constraints & edge cases.**
- 1 ≤ n ≤ 1690
- Sequence starts at 1

**Section 4 — Approach.**
Three-pointer DP. Maintain pointers `i2, i3, i5` into the ugly list for the next multiple of 2, 3, 5 respectively. At each step, take the minimum, advance the relevant pointer(s).

**Section 5 — Code.**
```python
def nthUglyNumber(n: int) -> int:
    ugly = [1] * n
    i2 = i3 = i5 = 0

    for i in range(1, n):
        next2 = ugly[i2] * 2
        next3 = ugly[i3] * 3
        next5 = ugly[i5] * 5
        ugly[i] = min(next2, next3, next5)
        if ugly[i] == next2: i2 += 1
        if ugly[i] == next3: i3 += 1
        if ugly[i] == next5: i5 += 1

    return ugly[n - 1]
```

Note: all three pointers advance when there's a tie (e.g., `6 = 2*3 = 3*2` — avoid duplicates).

**Section 6 — Complexity.**
Time O(n), Space O(n).

---

## Common Mistakes

1. **Integer overflow in C++/Java:** `a * b // gcd(a, b)` can overflow if `a` and `b` are both `int`. In Python this is never an issue (arbitrary precision). In C++, cast to `long long` before multiplying.

2. **Modular exponentiation vs. regular:** `2 ** 100_000_000` in Python is extremely slow (large integer). `pow(2, 100_000_000, MOD)` is O(log n). Always use `pow(a, b, m)` when the modulus is given.

3. **gcd(0, n):** By convention, `gcd(0, n) = n`. Python's `math.gcd` handles this. Manual implementations sometimes fail on this edge case.

4. **Starting the sieve from p^2:** The inner loop starts at `p*p`, not `2*p`. All multiples `k*p` for `k < p` have a prime factor smaller than `p` and were already marked. Starting from `2*p` is correct but wastes time.

5. **Modular inverse requires prime modulus (Fermat):** `pow(a, mod-2, mod)` only gives the correct modular inverse when `mod` is prime. For composite moduli, use the extended Euclidean algorithm.

6. **Not handling n=0 in pow:** `x^0 = 1` for any x. Ensure your loop exits correctly (the bit-shift loop handles this naturally since `n=0` never enters the loop).

---

## Interview Q&A

**Q1: What is the time complexity of the Euclidean algorithm and why?**
O(log min(a, b)). Each step reduces the larger number by at least half (provable by examining two consecutive steps: if `b ≤ a/2`, it's halved directly; if `b > a/2`, then `a % b < a/2`). So after at most `2 log₂(min(a,b))` steps, we reach 0.

**Q2: Why is the Sieve of Eratosthenes O(n log log n) and not O(n log n)?**
The inner loop runs `n/p` times for each prime `p`. Total work = `n * Σ(1/p for primes p ≤ n)`. By Mertens' theorem, this sum converges to `log log n`, not `log n` (which would be the harmonic series over all integers).

**Q3: How would you compute C(n, k) mod p for large n and k without overflow?**
Precompute factorials and their modular inverses up to n using `fact[i] = fact[i-1]*i % p` and `inv_fact[i] = pow(fact[n], p-2, p)` (when p is prime). Then `C(n,k) = fact[n] * inv_fact[k] * inv_fact[n-k] % p`. This runs in O(n) preprocessing and O(1) per query.

**Q4: What is Fermat's little theorem and when do you use it in competitive programming?**
If p is prime and gcd(a, p) = 1, then `a^(p-1) ≡ 1 (mod p)`, so `a^(-1) ≡ a^(p-2) (mod p)`. Use it to compute modular inverses when you need division in modular arithmetic (e.g., `C(n,k) mod p`, probability problems mod 10^9+7).

**Q5: How do you find all prime factors of n efficiently?**
Trial division up to √n: for each `p` from 2 to √n, divide out all occurrences. If anything remains after the loop, it's a prime factor > √n. Time O(√n).

```python
def prime_factors(n):
    factors = []
    p = 2
    while p * p <= n:
        while n % p == 0:
            factors.append(p)
            n //= p
        p += 1
    if n > 1:
        factors.append(n)  # remaining prime factor > sqrt(original n)
    return factors
```

**Q6: When would you use Lucas' theorem over precomputed factorials?**
Lucas' theorem computes `C(n, k) mod p` when `n` is very large (> 10^7) and `p` is a small prime. It breaks the problem into base-p digits and multiplies smaller binomials. Precomputed factorials are better when `n` is bounded and `p` is a large prime (10^9+7).
