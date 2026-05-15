# Dynamic Programming Problems

## 0/1 Knapsack
**When to use:** Each item usable 0 or 1 time, capacity constraint, subset selection

**Best DS:** 2D DP table, 1D DP array (space-optimized)

**Key Algorithms:** DP state: dp[i][w] = max value using first i items with capacity w

**Example Problems:**
1. "Partition equal subset sum" → Reduce to knapsack where target = sum / 2. Time: O(n × sum)
2. "Target sum" → Partition into two subsets with difference = target. Time: O(n × sum)

---

## Unbounded Knapsack
**When to use:** Items can be used multiple times, coin change, unlimited supply

**Best DS:** 1D DP array

**Key Algorithms:** dp[w] = max value with capacity w, items usable multiple times

**Example Problems:**
1. "Coin change (minimum coins)" → Unbounded knapsack; each coin usable unlimited times. Time: O(amount × coin_types)
2. "Coin change II (combinations)" → Count ways instead of minimum. Time: O(amount × coin_types)

---

## LIS (Longest Increasing Subsequence)
**When to use:** Finding longest ordered sequence, not necessarily contiguous

**Best DS:** DP array, Binary search + DP

**Key Algorithms:** O(n²): dp[i] = max(dp[j] + 1) for j < i where arr[j] < arr[i]. O(n log n): binary search

**Example Problems:**
1. "Longest increasing subsequence" → DP or binary search method. Time: O(n²) or O(n log n)

---

## LCS & Edit Distance
**When to use:** String similarity, minimum edits, sequence alignment

**Best DS:** 2D DP table

**Key Algorithms:** LCS: dp[i][j] = longest common subseq. Edit distance: add operations

**Example Problems:**
1. "Edit distance (Levenshtein)" → DP with insert/delete/replace operations. Time: O(m × n)

---

## Matrix Chain Multiplication
**When to use:** Optimal parenthesization, expression evaluation, cost minimization

**Best DS:** 2D DP table

**Key Algorithms:** dp[i][j] = min cost to multiply matrices from i to j

**Example Problems:**
1. "Burst balloons" → Interval DP similar to matrix chain. Time: O(n³)

---

## Palindrome DP
**When to use:** Palindrome partitioning, longest palindrome, palindrome checking

**Best DS:** 2D DP table, HashMap

**Key Algorithms:** Check: dp[i][j] = is s[i:j+1] palindrome. Count: min cuts

**Example Problems:**
1. "Palindrome partitioning (minimum cuts)" → DP with palindrome checking. Time: O(n²)

---

See [Master Index](problem-to-pattern-matcher.md) for all 50+ patterns.
