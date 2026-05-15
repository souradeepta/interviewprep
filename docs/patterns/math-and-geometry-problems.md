# Math & Geometry Problems

## GCD / LCM
**When to use:** Divisibility, fraction simplification, common factors

**Best DS:** Integer

**Key Algorithms:** Euclidean algorithm: gcd(a, b) = gcd(b, a mod b). LCM: a × b / gcd(a, b)

**Example Problems:**
1. "GCD of array elements" → Iteratively apply gcd to all elements. Time: O(n log(min(a, b)))

---

## Prime Numbers
**When to use:** Prime checking, prime factorization, number theory

**Best DS:** Array (Sieve), Integer

**Key Algorithms:** Sieve of Eratosthenes, trial division up to sqrt(n)

**Example Problems:**
1. "Count primes up to n" → Sieve of Eratosthenes. Time: O(n log log n)

---

## Modular Arithmetic
**When to use:** Overflow prevention, cryptography, number theory

**Best DS:** Integer

**Key Algorithms:** Modular exponentiation, Fermat's little theorem, modular inverse

**Example Problems:**
1. "Pow(x, n) mod 1e9+7" → Binary exponentiation with modulo. Time: O(log n)

---

## Coordinate Geometry
**When to use:** Spatial problems, line/circle intersection, convex hull

**Best DS:** Tuple (x, y), Array (list of points)

**Key Algorithms:** Distance formula, point in polygon, line intersection

**Example Problems:**
1. "Point in polygon" → Ray casting from point to infinity, count boundary crossings. Time: O(n)

---

See [Master Index](problem-to-pattern-matcher.md) for all 50+ patterns.
