# Bit Manipulation Problems

## XOR Tricks
**When to use:** Finding unique elements, parity checks, swapping without temp variable

**Best DS:** Integer

**Key Algorithms:** XOR properties: a ^ a = 0, a ^ 0 = a, XOR is commutative

**Example Problems:**
1. "Single number (all appear twice except one)" → XOR all numbers; pairs cancel, leaving single. Time: O(n)
2. "Find difference" → XOR all nums1 and nums2 elements; difference remains. Time: O(n)

---

## Bitmask DP
**When to use:** State compression, subset enumeration, exponential subproblems

**Best DS:** Integer (bitmask state), DP array

**Key Algorithms:** Each bit represents element inclusion, enumerate all masks 0 to 2^n - 1

**Example Problems:**
1. "Traveling salesman problem" → dp[mask][i] = min distance to visit cities in mask, ending at i. Time: O(2^n × n²)

---

## Subset Generation
**When to use:** All subsets, combinations, iterative power set

**Best DS:** Bit enumeration, Recursion

**Key Algorithms:** Bit iteration: each number represents one subset

**Example Problems:**
1. "Subsets (bit enumeration)" → Iterate i from 0 to 2^n - 1; each bit indicates inclusion. Time: O(2^n)

---

See [Master Index](problem-to-pattern-matcher.md) for all 50+ patterns.
