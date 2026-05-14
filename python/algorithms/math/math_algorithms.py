"""
Math Algorithms
===============
Essential number-theory and combinatorics algorithms for SDE interview preparation.

Each function includes docstrings with time/space complexity. A concrete
demonstration of every algorithm is in the __main__ block at the bottom.

Complexity Summary
------------------
Algorithm                       Time                Space
----------------------------------------------------------------------
GCD (Euclidean)                 O(log min(a,b))     O(log min(a,b)) *
LCM                             O(log min(a,b))     O(1)
Extended GCD                    O(log min(a,b))     O(log min(a,b)) *
Sieve of Eratosthenes           O(n log log n)      O(n)
Fast Exponentiation             O(log exp)          O(log exp) *
Modular Inverse (Fermat)        O(log p)            O(log p) *
Modular Inverse (Extended GCD)  O(log min(a,m))     O(log min(a,m)) *
Prime Factorization             O(sqrt(n))          O(log n)
Pollard-Rho Factorization       O(n^(1/4)) expected O(log n)
nCr (Pascal's Triangle)         O(n^2)              O(n^2)
nCr (Mod, Lucas-style)          O(n)                O(n)
nPr                             O(r)                O(1)
Catalan Number (DP)             O(n^2)              O(n)
Matrix Exponentiation           O(k^3 log n)        O(k^2)

* recursion stack depth
"""

import math
import random
from typing import Optional


# ---------------------------------------------------------------------------
# 1. GCD / LCM — Euclidean + Extended Euclidean
# ---------------------------------------------------------------------------

def gcd(a: int, b: int) -> int:
    """Greatest Common Divisor via the Euclidean algorithm.

    Repeatedly replaces (a, b) with (b, a % b) until b == 0.

    Parameters
    ----------
    a, b : int
        Non-negative integers.

    Returns
    -------
    int
        GCD(a, b).  gcd(0, x) == x by convention.

    Complexity
    ----------
    Time  : O(log min(a, b))
    Space : O(log min(a, b))  — recursion depth
    """
    if b == 0:
        return a
    return gcd(b, a % b)


def lcm(a: int, b: int) -> int:
    """Least Common Multiple.

    Uses the identity LCM(a, b) = a * b / GCD(a, b).

    Parameters
    ----------
    a, b : int
        Positive integers.

    Returns
    -------
    int
        LCM(a, b).

    Complexity
    ----------
    Time  : O(log min(a, b))
    Space : O(1)
    """
    return a // gcd(a, b) * b  # divide first to avoid overflow


def extended_gcd(a: int, b: int) -> tuple[int, int, int]:
    """Extended Euclidean Algorithm.

    Finds integers x, y such that  a*x + b*y = gcd(a, b).

    Parameters
    ----------
    a, b : int
        Non-negative integers (a >= b recommended).

    Returns
    -------
    (g, x, y) : tuple[int, int, int]
        g = gcd(a, b), and  a*x + b*y == g.

    Complexity
    ----------
    Time  : O(log min(a, b))
    Space : O(log min(a, b))  — recursion depth
    """
    if b == 0:
        return a, 1, 0
    g, x1, y1 = extended_gcd(b, a % b)
    # Back-substitute: a*x + b*y = g
    # gcd(b, a%b): b*x1 + (a%b)*y1 = g
    # a%b = a - (a//b)*b  →  b*x1 + (a - (a//b)*b)*y1 = g
    # a*y1 + b*(x1 - (a//b)*y1) = g
    x = y1
    y = x1 - (a // b) * y1
    return g, x, y


# ---------------------------------------------------------------------------
# 2. Sieve of Eratosthenes
# ---------------------------------------------------------------------------

def sieve(n: int) -> list[int]:
    """Generate all primes up to n using the Sieve of Eratosthenes.

    Marks composites by crossing out multiples of each prime starting
    from p^2 (all smaller multiples have already been crossed out).

    Parameters
    ----------
    n : int
        Upper bound (inclusive).  Must be >= 2.

    Returns
    -------
    list[int]
        Sorted list of all primes p with 2 <= p <= n.

    Complexity
    ----------
    Time  : O(n log log n)
    Space : O(n)
    """
    if n < 2:
        return []
    is_prime = bytearray([1]) * (n + 1)
    is_prime[0] = is_prime[1] = 0
    p = 2
    while p * p <= n:
        if is_prime[p]:
            # Mark all multiples of p starting from p*p
            is_prime[p * p : n + 1 : p] = bytearray(len(is_prime[p * p : n + 1 : p]))
        p += 1
    return [i for i, v in enumerate(is_prime) if v]


# ---------------------------------------------------------------------------
# 3. Fast Exponentiation — binary exponentiation
# ---------------------------------------------------------------------------

def fast_pow(base: int, exp: int, mod: Optional[int] = None) -> int:
    """Binary (fast) exponentiation: base^exp [% mod].

    Squares the base and halves the exponent at each step.
    Equivalent to Python's built-in pow(base, exp, mod) — shown here
    for instructional clarity.

    Parameters
    ----------
    base : int
        The base.
    exp : int
        Non-negative exponent.
    mod : int, optional
        If provided, computes (base^exp) % mod.

    Returns
    -------
    int
        base ** exp, optionally reduced modulo mod.

    Complexity
    ----------
    Time  : O(log exp)
    Space : O(log exp)  — recursion depth; use iterative for O(1)
    """
    if exp == 0:
        return 1 % (mod if mod else 1 + 1)  # handles mod=1 edge case gracefully
    if exp % 2 == 1:
        half = fast_pow(base, exp - 1, mod)
        result = base * half
    else:
        half = fast_pow(base, exp // 2, mod)
        result = half * half
    return result % mod if mod is not None else result


def fast_pow_iterative(base: int, exp: int, mod: Optional[int] = None) -> int:
    """Iterative binary exponentiation — O(log exp) time, O(1) space.

    Parameters
    ----------
    base, exp, mod : same as fast_pow.

    Returns
    -------
    int
    """
    result = 1
    if mod is not None:
        base %= mod
    while exp > 0:
        if exp & 1:
            result = result * base if mod is None else result * base % mod
        base = base * base if mod is None else base * base % mod
        exp >>= 1
    return result


# ---------------------------------------------------------------------------
# 4. Modular Arithmetic — modular inverse
# ---------------------------------------------------------------------------

def mod_inverse_fermat(a: int, p: int) -> int:
    """Modular inverse of a modulo a prime p using Fermat's Little Theorem.

    By Fermat: a^(p-1) ≡ 1 (mod p)  →  a^(-1) ≡ a^(p-2) (mod p).
    Requires p to be prime and gcd(a, p) == 1.

    Parameters
    ----------
    a : int
        Integer whose inverse is sought (1 <= a < p).
    p : int
        A prime modulus.

    Returns
    -------
    int
        a^(-1) mod p.

    Complexity
    ----------
    Time  : O(log p)
    Space : O(log p)
    """
    return fast_pow_iterative(a, p - 2, p)


def mod_inverse_ext_gcd(a: int, m: int) -> int:
    """Modular inverse of a modulo m via the Extended Euclidean Algorithm.

    Works for any m (not just prime) as long as gcd(a, m) == 1.

    Parameters
    ----------
    a : int
        Integer whose inverse is sought.
    m : int
        The modulus.

    Returns
    -------
    int
        x such that (a * x) % m == 1.

    Raises
    ------
    ValueError
        If gcd(a, m) != 1 (inverse does not exist).

    Complexity
    ----------
    Time  : O(log min(a, m))
    Space : O(log min(a, m))
    """
    g, x, _ = extended_gcd(a % m, m)
    if g != 1:
        raise ValueError(f"Modular inverse does not exist: gcd({a}, {m}) = {g}")
    return x % m


# ---------------------------------------------------------------------------
# 5. Prime Factorization — trial division + Pollard-rho
# ---------------------------------------------------------------------------

def prime_factors_trial(n: int) -> list[int]:
    """Prime factorization via trial division.

    Divides out 2, then tries all odd divisors up to sqrt(n).

    Parameters
    ----------
    n : int
        Positive integer >= 2.

    Returns
    -------
    list[int]
        Prime factors in non-decreasing order (with repetition).

    Complexity
    ----------
    Time  : O(sqrt(n))
    Space : O(log n)  — at most log2(n) prime factors
    """
    factors: list[int] = []
    while n % 2 == 0:
        factors.append(2)
        n //= 2
    d = 3
    while d * d <= n:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 2
    if n > 1:
        factors.append(n)
    return factors


def _miller_rabin(n: int, a: int) -> bool:
    """Deterministic Miller-Rabin primality test for witness a."""
    if n % a == 0:
        return n == a
    d, r = n - 1, 0
    while d % 2 == 0:
        d //= 2
        r += 1
    x = pow(a, d, n)
    if x == 1 or x == n - 1:
        return True
    for _ in range(r - 1):
        x = x * x % n
        if x == n - 1:
            return True
    return False


def is_prime_fast(n: int) -> bool:
    """Deterministic primality test for n < 3.3 * 10^24 using Miller-Rabin.

    Parameters
    ----------
    n : int
        Integer to test.

    Returns
    -------
    bool
    """
    if n < 2:
        return False
    for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]:
        if n == p:
            return True
        if not _miller_rabin(n, p):
            return False
    return True


def _pollard_rho(n: int) -> int:
    """Find a non-trivial factor of n using Pollard's rho algorithm.

    Uses Floyd's cycle detection with f(x) = x^2 + c (mod n).

    Parameters
    ----------
    n : int
        Composite integer > 1.

    Returns
    -------
    int
        A factor of n (may equal n if unlucky; caller retries with different c).
    """
    if n % 2 == 0:
        return 2
    while True:
        x = random.randint(2, n - 1)
        y = x
        c = random.randint(1, n - 1)
        d = 1
        while d == 1:
            x = (x * x + c) % n
            y = (y * y + c) % n
            y = (y * y + c) % n
            d = math.gcd(abs(x - y), n)
        if d != n:
            return d


def prime_factors_pollard(n: int) -> list[int]:
    """Prime factorization using Pollard's rho algorithm.

    Recursively factorizes using Miller-Rabin primality testing and
    Pollard's rho for finding factors of composite numbers.

    Parameters
    ----------
    n : int
        Positive integer >= 2.

    Returns
    -------
    list[int]
        Prime factors in non-decreasing order (with repetition).

    Complexity
    ----------
    Time  : O(n^(1/4)) expected per factor
    Space : O(log n)
    """
    if n <= 1:
        return []
    if is_prime_fast(n):
        return [n]
    # Find a factor
    factor = n
    while factor == n:
        factor = _pollard_rho(n)
    return sorted(prime_factors_pollard(factor) + prime_factors_pollard(n // factor))


# ---------------------------------------------------------------------------
# 6. Combination / Permutation
# ---------------------------------------------------------------------------

def build_pascal_triangle(max_n: int) -> list[list[int]]:
    """Build Pascal's triangle up to row max_n.

    C[i][j] = C(i, j) = number of ways to choose j items from i.

    Parameters
    ----------
    max_n : int
        Maximum n for which nCr will be needed.

    Returns
    -------
    list[list[int]]
        2-D table where C[n][r] = nCr.

    Complexity
    ----------
    Time  : O(max_n^2)
    Space : O(max_n^2)
    """
    C: list[list[int]] = [[0] * (max_n + 1) for _ in range(max_n + 1)]
    for i in range(max_n + 1):
        C[i][0] = 1
        for j in range(1, i + 1):
            C[i][j] = C[i - 1][j - 1] + C[i - 1][j]
    return C


def ncr(n: int, r: int, C: Optional[list[list[int]]] = None) -> int:
    """n Choose r — number of r-element subsets of an n-element set.

    Uses a pre-built Pascal's triangle table if provided, otherwise
    builds one on the fly.

    Parameters
    ----------
    n, r : int
        0 <= r <= n.
    C : list[list[int]], optional
        Pre-built Pascal's triangle from build_pascal_triangle(n).

    Returns
    -------
    int
        C(n, r).

    Complexity
    ----------
    Time  : O(1) with pre-built table, O(n^2) otherwise
    Space : O(n^2) for table
    """
    if r < 0 or r > n:
        return 0
    if C is None:
        C = build_pascal_triangle(n)
    return C[n][r]


def ncr_mod(n: int, r: int, mod: int) -> int:
    """nCr modulo a prime, using precomputed factorials and modular inverses.

    Parameters
    ----------
    n, r : int
        0 <= r <= n.
    mod : int
        A prime modulus (e.g. 10**9 + 7).

    Returns
    -------
    int
        C(n, r) % mod.

    Complexity
    ----------
    Time  : O(n) for precomputation, O(1) per query
    Space : O(n)
    """
    if r < 0 or r > n:
        return 0
    fact = [1] * (n + 1)
    for i in range(1, n + 1):
        fact[i] = fact[i - 1] * i % mod
    inv_fact = [1] * (n + 1)
    inv_fact[n] = mod_inverse_fermat(fact[n], mod)
    for i in range(n - 1, -1, -1):
        inv_fact[i] = inv_fact[i + 1] * (i + 1) % mod
    return fact[n] * inv_fact[r] % mod * inv_fact[n - r] % mod


def npr(n: int, r: int) -> int:
    """n Permute r — number of ordered r-arrangements from n elements.

    nPr = n! / (n-r)! = n * (n-1) * ... * (n-r+1).

    Parameters
    ----------
    n, r : int
        0 <= r <= n.

    Returns
    -------
    int
        P(n, r).

    Complexity
    ----------
    Time  : O(r)
    Space : O(1)
    """
    if r < 0 or r > n:
        return 0
    result = 1
    for i in range(n, n - r, -1):
        result *= i
    return result


# ---------------------------------------------------------------------------
# 7. Catalan Numbers
# ---------------------------------------------------------------------------

def catalan(n: int) -> list[int]:
    """Compute the first n+1 Catalan numbers C(0) .. C(n) via DP.

    C(0) = 1,  C(n) = sum_{i=0}^{n-1} C(i) * C(n-1-i).

    Catalan numbers count: valid parenthesizations, BST shapes,
    monotonic lattice paths, triangulations of a polygon, etc.

    Parameters
    ----------
    n : int
        Upper index (inclusive).

    Returns
    -------
    list[int]
        cat[i] = C(i) for i in 0..n.

    Complexity
    ----------
    Time  : O(n^2)
    Space : O(n)
    """
    cat = [0] * (n + 1)
    cat[0] = 1
    for i in range(1, n + 1):
        for j in range(i):
            cat[i] += cat[j] * cat[i - 1 - j]
    return cat


# ---------------------------------------------------------------------------
# 8. Matrix Exponentiation
# ---------------------------------------------------------------------------

Matrix = list[list[int]]


def mat_mul(A: Matrix, B: Matrix, mod: Optional[int] = None) -> Matrix:
    """Multiply two square matrices A and B (both k x k).

    Parameters
    ----------
    A, B : Matrix
        Square matrices of the same dimension k.
    mod : int, optional
        If provided, entries are reduced modulo mod.

    Returns
    -------
    Matrix
        A @ B, optionally reduced modulo mod.

    Complexity
    ----------
    Time  : O(k^3)
    Space : O(k^2)
    """
    k = len(A)
    C: Matrix = [[0] * k for _ in range(k)]
    for i in range(k):
        for l in range(k):            # noqa: E741
            if A[i][l] == 0:
                continue
            for j in range(k):
                C[i][j] += A[i][l] * B[l][j]
        if mod is not None:
            for j in range(k):
                C[i][j] %= mod
    return C


def mat_pow(M: Matrix, exp: int, mod: Optional[int] = None) -> Matrix:
    """Raise a square matrix M to the power exp using binary exponentiation.

    Parameters
    ----------
    M : Matrix
        A square matrix (k x k).
    exp : int
        Non-negative integer exponent.
    mod : int, optional
        If provided, all entries are kept modulo mod.

    Returns
    -------
    Matrix
        M^exp (the identity matrix when exp == 0).

    Complexity
    ----------
    Time  : O(k^3 log exp)
    Space : O(k^2)
    """
    k = len(M)
    # Identity matrix
    result: Matrix = [[1 if i == j else 0 for j in range(k)] for i in range(k)]
    base = [row[:] for row in M]
    while exp > 0:
        if exp & 1:
            result = mat_mul(result, base, mod)
        base = mat_mul(base, base, mod)
        exp >>= 1
    return result


def fib_matrix(n: int, mod: Optional[int] = None) -> int:
    """Compute F(n) using 2x2 matrix exponentiation.

    The recurrence [[F(n+1)], [F(n)]] = [[1,1],[1,0]]^n * [[1],[0]].

    Parameters
    ----------
    n : int
        Non-negative Fibonacci index (F(0)=0, F(1)=1).
    mod : int, optional
        If provided, computes F(n) % mod.

    Returns
    -------
    int
        F(n), optionally modulo mod.

    Complexity
    ----------
    Time  : O(log n)
    Space : O(1)  — matrix is always 2x2
    """
    if n == 0:
        return 0
    M = [[1, 1], [1, 0]]
    result = mat_pow(M, n, mod)
    return result[0][1]  # M^n[0][1] = F(n)


def linear_recurrence_matrix(coeffs: list[int], initial: list[int],
                              n: int, mod: Optional[int] = None) -> int:
    """Solve a linear recurrence of order k via matrix exponentiation.

    Given f(n) = c[0]*f(n-1) + c[1]*f(n-2) + ... + c[k-1]*f(n-k)
    with initial values f(0), f(1), ..., f(k-1).

    Parameters
    ----------
    coeffs : list[int]
        Recurrence coefficients [c0, c1, ..., c_{k-1}].
    initial : list[int]
        Initial values [f(0), f(1), ..., f(k-1)].
    n : int
        The index to compute.
    mod : int, optional
        Modulus for computation.

    Returns
    -------
    int
        f(n).

    Complexity
    ----------
    Time  : O(k^3 log n)
    Space : O(k^2)
    """
    k = len(coeffs)
    if n < k:
        return initial[n] % mod if mod else initial[n]
    # Build companion matrix
    # [[c0, c1, ..., c_{k-1}],
    #  [1,  0,  ..., 0      ],
    #  [0,  1,  ..., 0      ],
    #  ...
    #  [0,  0,  ..., 1, 0   ]]
    M: Matrix = [[0] * k for _ in range(k)]
    M[0] = list(coeffs)
    for i in range(1, k):
        M[i][i - 1] = 1
    Mn = mat_pow(M, n - k + 1, mod)
    # State vector: [f(k-1), f(k-2), ..., f(0)]
    state = list(reversed(initial))
    result = 0
    for j in range(k):
        val = Mn[0][j] * state[j]
        result += val % mod if mod else val
    return result % mod if mod else result


# ---------------------------------------------------------------------------
# __main__ demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    SEP = "=" * 60

    print(SEP)
    print("MATH ALGORITHMS DEMO")
    print(SEP)

    # ---- GCD / LCM ----
    print("\n--- GCD / LCM ---")
    a, b = 48, 18
    print(f"  gcd({a}, {b})           = {gcd(a, b)}")
    print(f"  lcm({a}, {b})           = {lcm(a, b)}")
    g, x, y = extended_gcd(a, b)
    print(f"  extended_gcd({a},{b}) => g={g}, x={x}, y={y}")
    print(f"  verify: {a}*{x} + {b}*{y} = {a*x + b*y}  (should be {g})")

    # ---- Sieve ----
    print("\n--- Sieve of Eratosthenes (primes up to 50) ---")
    primes = sieve(50)
    print(f"  {primes}")

    # ---- Fast Exponentiation ----
    print("\n--- Fast Exponentiation ---")
    MOD = 10**9 + 7
    print(f"  2^10           = {fast_pow(2, 10)}")
    print(f"  2^10 (iter)    = {fast_pow_iterative(2, 10)}")
    print(f"  3^1000000 % MOD= {fast_pow_iterative(3, 1_000_000, MOD)}")

    # ---- Modular Inverse ----
    print("\n--- Modular Inverse ---")
    p = 1_000_000_007
    a_val = 123456789
    inv_f = mod_inverse_fermat(a_val, p)
    inv_e = mod_inverse_ext_gcd(a_val, p)
    print(f"  inv({a_val}) via Fermat      = {inv_f}")
    print(f"  inv({a_val}) via Ext GCD     = {inv_e}")
    print(f"  verify: {a_val} * inv % p   = {a_val * inv_f % p}  (should be 1)")

    # ---- Prime Factorization ----
    print("\n--- Prime Factorization ---")
    for num in [360, 97, 1_000_000_007, 2**32]:
        f_trial = prime_factors_trial(num)
        f_rho   = prime_factors_pollard(num)
        print(f"  {num:15d}: trial={f_trial}  pollard={f_rho}")

    # ---- nCr / nPr ----
    print("\n--- Combinations / Permutations ---")
    C = build_pascal_triangle(10)
    print(f"  C(10,3)        = {ncr(10, 3, C)}")
    print(f"  C(10,3) mod 1e9+7 = {ncr_mod(10, 3, 10**9+7)}")
    print(f"  P(10,3)        = {npr(10, 3)}")
    # Pascal's row 5
    print(f"  Pascal row 5   = {[C[5][j] for j in range(6)]}")

    # ---- Catalan Numbers ----
    print("\n--- Catalan Numbers (C(0)..C(9)) ---")
    cats = catalan(9)
    for i, c in enumerate(cats):
        print(f"  C({i}) = {c}")

    # ---- Matrix Exponentiation ----
    print("\n--- Matrix Exponentiation ---")
    # Fibonacci via matrix
    for idx in [0, 1, 5, 10, 50]:
        print(f"  F({idx:2d}) via matrix = {fib_matrix(idx)}")
    print(f"  F(50) via matrix % 1e9+7 = {fib_matrix(50, 10**9+7)}")

    # Tribonacci: f(n) = f(n-1) + f(n-2) + f(n-3), f(0)=0, f(1)=0, f(2)=1
    print("\n--- Tribonacci via linear_recurrence_matrix ---")
    trib_coeffs  = [1, 1, 1]
    trib_initial = [0, 0, 1]
    for idx in range(10):
        val = linear_recurrence_matrix(trib_coeffs, trib_initial, idx)
        print(f"  T({idx}) = {val}")
