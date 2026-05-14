# Math Algorithms

## Overview

This module covers the core number-theory and combinatorics algorithms that appear repeatedly in SDE interviews and competitive programming. These algorithms underpin solutions to problems involving divisibility, prime numbers, modular arithmetic, counting, and matrix-based recurrences.

**When to use:**
- Prime-related checks (sieve, factorization, primality)
- Modular inverse in combinatorics under a prime modulus
- Raising large numbers or matrices to a power efficiently
- Counting problems: subsets, arrangements, valid parenthesizations
- Fast computation of recurrences (Fibonacci, Tribonacci, linear recurrences)

---

## 1. GCD and LCM (Euclidean Algorithm)

### Description

The **Euclidean algorithm** computes gcd(a, b) by repeatedly replacing (a, b) with (b, a % b) until b == 0. The **Extended Euclidean algorithm** additionally finds integers x, y such that `a*x + b*y = gcd(a, b)`, which is the foundation for modular inverse computation. LCM is derived as `a / gcd(a,b) * b`.

### Step-by-step visualization: gcd(48, 18)

```
gcd(48, 18)
  → gcd(18, 48 % 18) = gcd(18, 12)
  → gcd(12, 18 % 12) = gcd(12,  6)
  → gcd( 6, 12 %  6) = gcd( 6,  0)
  → return 6

lcm(48, 18) = 48 / 6 * 18 = 144

Extended GCD: find x, y s.t. 48x + 18y = 6
  extgcd(48, 18):  calls extgcd(18, 12)
    extgcd(18, 12): calls extgcd(12, 6)
      extgcd(12, 6):  calls extgcd(6, 0)
        returns (6, 1, 0)               ← base: 6*1 + 0*0 = 6
      x = 0, y = 1 - (12//6)*0 = 1     ← 12*0 + 6*1 = 6   ✓
      returns (6, 0, 1)
    x = 1, y = 0 - (18//12)*1 = -1     ← 18*1 + 12*(-1) = 6  ✓
    returns (6, 1, -1)
  x = -1, y = 1 - (48//18)*(-1) = 3    ← 48*(-1) + 18*3 = 6  ✓
  returns (6, -1, 3)

Verify: 48 * (-1) + 18 * 3 = -48 + 54 = 6  ✓
```

### Complexity

| Variant          | Time                  | Space                 |
|------------------|-----------------------|-----------------------|
| gcd(a, b)        | O(log min(a, b))      | O(log min(a, b))      |
| lcm(a, b)        | O(log min(a, b))      | O(1)                  |
| extended_gcd     | O(log min(a, b))      | O(log min(a, b))      |

---

## 2. Sieve of Eratosthenes

### Description

The sieve generates all primes up to n by iteratively marking composites. For each prime p, all multiples starting at p^2 are marked (smaller multiples were already handled by earlier primes). The inner loop runs in O(n/p) per prime, and the total work sums to O(n log log n).

### Step-by-step visualization: sieve(30)

```
Initial: mark all as prime
  [- - 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30]

p=2: mark multiples of 2 starting from 4
  cross out: 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30

p=3: mark multiples of 3 starting from 9
  cross out: 9, 15, 21, 27

p=5: mark multiples of 5 starting from 25
  cross out: 25

p=6: 6 > sqrt(30) ≈ 5.47 → stop

Remaining primes: [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
```

### Complexity

| Operation | Time           | Space |
|-----------|----------------|-------|
| Sieve(n)  | O(n log log n) | O(n)  |

---

## 3. Fast (Binary) Exponentiation

### Description

Binary exponentiation computes `base^exp` in O(log exp) multiplications by squaring the base and halving the exponent at each step. The key insight: if exp is even, `base^exp = (base^(exp/2))^2`; if odd, `base^exp = base * base^(exp-1)`. Always use the iterative form for production (O(1) space).

### Step-by-step visualization: 3^13

```
exp = 13 = 1101 in binary  →  3^8 * 3^4 * 3^1

Iterative:
  result=1, base=3, exp=13

  exp=13 (odd):   result = 1*3  = 3;   base = 3*3  =  9;  exp=6
  exp= 6 (even):  result = 3;          base = 9*9  = 81;  exp=3
  exp= 3 (odd):   result = 3*81= 243;  base = 81*81=6561; exp=1
  exp= 1 (odd):   result = 243*6561 = 1594323;            exp=0
  exp= 0: stop

  Result: 3^13 = 1594323  ✓  (verify: 3^13 = 1594323)
```

### Complexity

| Operation              | Time       | Space          |
|------------------------|------------|----------------|
| fast_pow (recursive)   | O(log exp) | O(log exp)     |
| fast_pow (iterative)   | O(log exp) | O(1)           |

---

## 4. Modular Arithmetic — Modular Inverse

### Description

The modular inverse of a (mod m) is x such that `a*x ≡ 1 (mod m)`. Two methods:

1. **Fermat's Little Theorem**: when m is prime, `a^(-1) ≡ a^(m-2) (mod m)`. Uses fast exponentiation.
2. **Extended GCD**: works for any m; find x, y with `a*x + m*y = gcd(a,m) = 1`, then x is the inverse.

### Step-by-step visualization: inverse of 3 (mod 7)

```
Method 1 — Fermat (m=7 is prime):
  a^(-1) = 3^(7-2) mod 7 = 3^5 mod 7
  3^1 = 3
  3^2 = 9 mod 7 = 2
  3^4 = 2^2 mod 7 = 4
  3^5 = 3^4 * 3^1 = 4*3 = 12 mod 7 = 5
  inverse = 5  →  verify: 3*5 = 15 ≡ 1 (mod 7)  ✓

Method 2 — Extended GCD:
  extgcd(3, 7): 3*x + 7*y = 1
    extgcd(7, 3): 7*x + 3*y = 1
      extgcd(3, 1): 3*x + 1*y = 1
        extgcd(1, 0) → (1, 1, 0)
        x = 0, y = 1 - 3*0 = 1  → (1, 0, 1)
      x = 1, y = 0 - 2*1 = -2   → (1, 1, -2)  → 7*1 + 3*(-2) = 1  ✓
    x = -2, y = 1 - 0*(-2) = 1  → (1, -2, 1)  → 3*(-2) + 7*1 = 1 ✓
  inverse = -2 mod 7 = 5  ✓
```

### Complexity

| Method              | Time            | Space           |
|---------------------|-----------------|-----------------|
| Fermat (mod prime)  | O(log p)        | O(1) iterative  |
| Extended GCD        | O(log min(a,m)) | O(log min(a,m)) |

---

## 5. Prime Factorization

### Description

**Trial division**: divide by 2, then try all odd divisors up to sqrt(n). O(sqrt(n)).

**Pollard's rho**: a probabilistic algorithm that finds a non-trivial factor in O(n^(1/4)) expected time using Floyd's cycle detection on the sequence `f(x) = x^2 + c (mod n)`. Combined with **Miller-Rabin** primality testing, this gives an efficient recursive factorization for large numbers.

### Step-by-step visualization: trial division of 360

```
n = 360
  n % 2 == 0 → factor 2, n = 180
  n % 2 == 0 → factor 2, n = 90
  n % 2 == 0 → factor 2, n = 45
  n % 3 == 0 → factor 3, n = 15
  n % 3 == 0 → factor 3, n = 5
  d = 5: 5*5 = 25 > 5 → stop
  n = 5 > 1 → factor 5

Result: 360 = 2^3 * 3^2 * 5  →  [2, 2, 2, 3, 3, 5]
```

### Pollard-rho step (n=1189, c=3)

```
x=2, y=2
  x = (4+3) % 1189 = 7
  y = ((4+3)^2+3) % 1189 = (52+3) % 1189 = 55 ...
  (cycle detection continues until gcd(|x-y|, n) != 1)
  ...eventually finds factor 29 or 41
  1189 = 29 * 41  ✓
```

### Complexity

| Method             | Time            | Space    |
|--------------------|-----------------|----------|
| Trial division     | O(sqrt(n))      | O(log n) |
| Pollard's rho      | O(n^(1/4)) exp. | O(log n) |
| Miller-Rabin test  | O(log^2 n)      | O(1)     |

---

## 6. Combinations and Permutations

### Description

**nCr (Pascal's triangle)**: build a 2-D DP table where `C[i][j] = C[i-1][j-1] + C[i-1][j]` (recurrence from the identity: "either include or exclude the i-th element"). Provides O(1) query after O(n^2) precomputation.

**nCr mod prime**: precompute factorials and their modular inverses using `inv[i] = inv[i+1] * (i+1) % mod`. Then `C(n,r) = fact[n] * inv_fact[r] * inv_fact[n-r] % mod`.

**nPr**: `P(n,r) = n * (n-1) * ... * (n-r+1)`.

### Step-by-step visualization: Pascal's triangle rows 0–5

```
Row 0:  1
Row 1:  1  1
Row 2:  1  2  1
Row 3:  1  3  3  1
Row 4:  1  4  6  4  1
Row 5:  1  5 10 10  5  1

Each entry = sum of the two entries above it:
  C[3][1] = C[2][0] + C[2][1] = 1 + 2 = 3
  C[4][2] = C[3][1] + C[3][2] = 3 + 3 = 6
  C[5][2] = C[4][1] + C[4][2] = 4 + 6 = 10

C(10,3)   = 120       P(10,3)   = 720
C(10,3) mod (10^9+7) = 120
```

### Complexity

| Operation                  | Time          | Space   |
|----------------------------|---------------|---------|
| build_pascal(n)            | O(n^2)        | O(n^2)  |
| nCr with table             | O(1)          | —       |
| nCr mod prime (precompute) | O(n)          | O(n)    |
| nCr mod prime (query)      | O(1)          | —       |
| nPr                        | O(r)          | O(1)    |

---

## 7. Catalan Numbers

### Description

Catalan numbers count a remarkable variety of combinatorial structures. The n-th Catalan number satisfies `C(0)=1` and `C(n) = sum_{i=0}^{n-1} C(i)*C(n-1-i)` — a convolution DP. Equivalently, `C(n) = C(2n, n) / (n+1)`.

Common interpretations:
- Number of valid sequences of n pairs of parentheses
- Number of structurally distinct BSTs with n nodes
- Number of triangulations of a convex (n+2)-gon

### Step-by-step visualization: C(4)

```
C(0) = 1
C(1) = C(0)*C(0) = 1
C(2) = C(0)*C(1) + C(1)*C(0) = 1 + 1 = 2
C(3) = C(0)*C(2) + C(1)*C(1) + C(2)*C(0) = 2 + 1 + 2 = 5
C(4) = C(0)*C(3) + C(1)*C(2) + C(2)*C(1) + C(3)*C(0)
     =    5    +    2    +    2    +    5   = 14

Verification with () notation (C(3) = 5 valid parenthesizations of 3 pairs):
  ((()))   (()())   (())()   ()(())   ()()()   ← 5 ✓

Values: C(0)=1, C(1)=1, C(2)=2, C(3)=5, C(4)=14, C(5)=42, ...
```

### Complexity

| Operation  | Time   | Space |
|------------|--------|-------|
| catalan(n) | O(n^2) | O(n)  |

---

## 8. Matrix Exponentiation

### Description

Matrix exponentiation lifts binary exponentiation to matrices, computing `M^n` in O(k^3 log n) for a k×k matrix. It is the standard technique for computing the n-th term of any linear recurrence in O(log n) time.

**Fibonacci via 2×2 matrix:**
```
[[F(n+1)], [F(n)]] = [[1,1],[1,0]]^n * [[1],[0]]
```
So `M^n[0][1] = F(n)`.

**General linear recurrence** of order k:
```
f(n) = c_0*f(n-1) + c_1*f(n-2) + ... + c_{k-1}*f(n-k)
```
is captured by the companion matrix:
```
M = [[c_0, c_1, ..., c_{k-1}],
     [  1,   0, ...,       0],
     [  0,   1, ...,       0],
     ...
     [  0,   0, ...,   1,  0]]
```

### Step-by-step visualization: F(6) via matrix

```
M = [[1,1],[1,0]]

M^1 = [[1,1],[1,0]]
M^2 = [[2,1],[1,1]]    ← M^1 * M^1
M^4 = [[5,3],[3,2]]    ← M^2 * M^2
M^6 = M^4 * M^2
    = [[5,3],[3,2]] * [[2,1],[1,1]]
    = [[5*2+3*1, 5*1+3*1],[3*2+2*1, 3*1+2*1]]
    = [[13,8],[8,5]]

F(6) = M^6[0][1] = 8  ✓  (Fibonacci: 0,1,1,2,3,5,8,...)
```

### Complexity

| Operation              | Time           | Space   |
|------------------------|----------------|---------|
| mat_mul(k×k)           | O(k^3)         | O(k^2)  |
| mat_pow(M, n)          | O(k^3 log n)   | O(k^2)  |
| fib_matrix(n)          | O(log n)       | O(1)    |
| linear_recurrence(k,n) | O(k^3 log n)   | O(k^2)  |

---

## Operations & Complexity Summary

| Algorithm                         | Time                  | Space        |
|-----------------------------------|-----------------------|--------------|
| GCD (Euclidean)                   | O(log min(a,b))       | O(log min)   |
| LCM                               | O(log min(a,b))       | O(1)         |
| Extended GCD                      | O(log min(a,b))       | O(log min)   |
| Sieve of Eratosthenes             | O(n log log n)        | O(n)         |
| Fast Exponentiation               | O(log exp)            | O(1) iter    |
| Mod Inverse (Fermat, prime mod)   | O(log p)              | O(1)         |
| Mod Inverse (Extended GCD)        | O(log min(a,m))       | O(log min)   |
| Prime Factorization (trial)       | O(sqrt(n))            | O(log n)     |
| Prime Factorization (Pollard rho) | O(n^(1/4)) expected   | O(log n)     |
| Miller-Rabin primality            | O(log^2 n)            | O(1)         |
| Pascal's Triangle build           | O(n^2)                | O(n^2)       |
| nCr (table query)                 | O(1)                  | —            |
| nCr mod prime                     | O(n) pre + O(1) query | O(n)         |
| nPr                               | O(r)                  | O(1)         |
| Catalan DP                        | O(n^2)                | O(n)         |
| Matrix Multiply (k×k)             | O(k^3)                | O(k^2)       |
| Matrix Power (k×k, exp n)         | O(k^3 log n)          | O(k^2)       |
| Fibonacci (matrix exp)            | O(log n)              | O(1)         |

---

## Common Interview Questions

- **"Find all primes up to N efficiently."** — Sieve of Eratosthenes; state the O(n log log n) complexity and why marking starts at p^2.

- **"Compute nCr for large n, result modulo 10^9+7."** — Precompute factorials and their modular inverses using Fermat's theorem; O(n) precompute, O(1) per query. Fermat only applies when the modulus is prime.

- **"Compute the n-th Fibonacci number for very large n (e.g. n = 10^18)."** — Matrix exponentiation on the 2×2 transition matrix; O(log n). Mention that naive DP is O(n) and fails for n = 10^18.

- **"Compute a^b mod m efficiently."** — Binary exponentiation; O(log b). Critical to reduce base by mod at each step to prevent overflow.

- **"How do you find modular inverse when the modulus is NOT prime?"** — Extended Euclidean algorithm; inverse exists iff gcd(a, m) = 1. Fermat's theorem requires a prime modulus.

- **"What are Catalan numbers and when do they appear?"** — C(n) counts: balanced parenthesizations, distinct BST shapes with n nodes, mountain ranges, triangulations of (n+2)-gon. Give the DP recurrence C(n) = sum C(i)*C(n-1-i) and the closed form C(2n,n)/(n+1).

- **"Factorize very large numbers (say n up to 10^18) quickly."** — Pollard's rho algorithm (O(n^(1/4)) expected) combined with Miller-Rabin primality testing; trial division alone is O(sqrt(n)) which is too slow for n = 10^18.

- **"Solve the recurrence f(n) = 3f(n-1) - f(n-2), f(0)=2, f(1)=3, for n up to 10^9."** — Build the 2×2 companion matrix and raise it to the (n-1)-th power via matrix exponentiation; O(log n).
