# Dynamic Programming

**Level:** L4-L5
**Time to read:** ~35 min

The most important algorithm family for senior SDE interviews. Master the 7 DP categories and you can solve 80% of DP problems by pattern recognition.

---

## What Is Dynamic Programming?

DP = **recursion + memoization** (top-down) or **table filling** (bottom-up).
Apply DP when a problem has:
1. **Optimal substructure** — optimal solution contains optimal solutions to subproblems
2. **Overlapping subproblems** — same subproblems solved multiple times

```
Greedy vs DP:
  Greedy: local optimal choices always lead to global optimum (proof required)
  DP:     try all possibilities, cache results to avoid recomputation

Divide & Conquer vs DP:
  D&C: subproblems are independent (merge sort)
  DP:  subproblems overlap (fibonacci)
```

---

## Comparative Table — DP Problem Categories

| Category | Example Problems | Key Insight | State Definition |
|----------|-----------------|-------------|-----------------|
| 1D linear | Fibonacci, Climbing Stairs, House Robber | Current state depends on k previous | `dp[i] = f(dp[i-k]...dp[i-1])` |
| Knapsack 0/1 | Subset Sum, Partition Equal Subset | Include or exclude each item | `dp[i][w] = take or leave item i` |
| Unbounded knapsack | Coin Change, Combination Sum IV | Can use each item multiple times | `dp[w] = min over all items` |
| LCS/LIS | Longest Common Subsequence, LIS | 2D state for two sequences | `dp[i][j] = LCS of s1[:i], s2[:j]` |
| Edit distance | Edit Distance, One Edit Away | Insert/delete/replace transitions | `dp[i][j] = min edits s1[:i]→s2[:j]` |
| Interval DP | Matrix Chain, Burst Balloons | Split range at every point k | `dp[i][j] = cost of solving i..j` |
| Tree DP | House Robber III, Diameter | Post-order, choose at each node | `(take, skip)` state at each node |

### Approach Selection

```
Single array, each element contributes once?
  → 1D linear DP (Climbing Stairs, House Robber)

Items with weights/values, capacity constraint?
  → Knapsack: 0/1 (each item once) or Unbounded (reuse allowed)

Two sequences to compare/align?
  → LCS/Edit Distance 2D DP

Contiguous subarray optimization?
  → Kadane's algorithm variant

Optimal way to split a range?
  → Interval DP (think: what's the last split point?)

Tree structure, choices at each node?
  → Tree DP with DFS, return tuple of states

Counting arrangements or paths?
  → Usually 1D or 2D DP with addition transitions
```

---

## Core Patterns with Code

### Pattern 1: 1D Linear DP

**Template:**
```python
dp = [base_case] * (n + 1)
dp[0] = ...   # Base case(s)
dp[1] = ...
for i in range(2, n + 1):
    dp[i] = f(dp[i-1], dp[i-2], ...)  # Recurrence
return dp[n]
```

**Fibonacci (Space-Optimized):**
```python
def fib(n):
    if n <= 1:
        return n
    prev2, prev1 = 0, 1
    for _ in range(2, n + 1):
        prev2, prev1 = prev1, prev1 + prev2
    return prev1
```

---

### Pattern 2: 0/1 Knapsack

Each item used at most once. Iterate items in outer loop, weights in inner loop (backward to prevent reuse).

```python
def knapsack_01(weights, values, capacity):
    n = len(weights)
    dp = [0] * (capacity + 1)
    for i in range(n):
        for w in range(capacity, weights[i] - 1, -1):  # Backward!
            dp[w] = max(dp[w], dp[w - weights[i]] + values[i])
    return dp[capacity]
```

---

### Pattern 3: Unbounded Knapsack

Each item can be used unlimited times. Inner loop goes forward (allows reuse).

```python
def unbounded_knapsack(weights, values, capacity):
    dp = [0] * (capacity + 1)
    for w in range(1, capacity + 1):
        for i in range(len(weights)):
            if weights[i] <= w:
                dp[w] = max(dp[w], dp[w - weights[i]] + values[i])
    return dp[capacity]
```

---

### Pattern 4: 2D DP (LCS)

```python
def lcs(s1, s2):
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i-1] == s2[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    return dp[m][n]
```

---

### Pattern 5: Interval DP

```python
def interval_dp(arr):
    n = len(arr)
    dp = [[0] * n for _ in range(n)]
    for length in range(2, n + 1):          # Increasing interval length
        for i in range(n - length + 1):
            j = i + length - 1
            dp[i][j] = float('inf')
            for k in range(i, j):           # Try all split points
                dp[i][j] = min(dp[i][j], dp[i][k] + dp[k+1][j] + cost(i, k, j))
    return dp[0][n-1]
```

---

### Pattern 6: Tree DP

```python
def tree_dp(root):
    def dfs(node):
        if not node:
            return 0, 0          # (take, skip)
        left_take, left_skip = dfs(node.left)
        right_take, right_skip = dfs(node.right)
        take = node.val + left_skip + right_skip
        skip = max(left_take, left_skip) + max(right_take, right_skip)
        return take, skip
    take, skip = dfs(root)
    return max(take, skip)
```

---

## Top-Down vs Bottom-Up

| Aspect | Top-Down (Memoization) | Bottom-Up (Tabulation) |
|--------|----------------------|----------------------|
| Direction | Start from goal, recurse | Start from base cases, build up |
| Code style | Recursive + cache | Iterative + table |
| Space | O(n) + call stack | O(n) (no stack) |
| Computed states | Only needed states | All states |
| Easier when | State is hard to order | Order is clear |

```python
# Top-down: natural recursion + cache
from functools import lru_cache

def climb_stairs_memo(n):
    @lru_cache(maxsize=None)
    def dp(i):
        if i <= 1:
            return 1
        return dp(i - 1) + dp(i - 2)
    return dp(n)

# Bottom-up: explicit table
def climb_stairs_tab(n):
    if n <= 1:
        return 1
    dp = [0] * (n + 1)
    dp[0] = dp[1] = 1
    for i in range(2, n + 1):
        dp[i] = dp[i-1] + dp[i-2]
    return dp[n]

# Space-optimized bottom-up
def climb_stairs_opt(n):
    if n <= 1:
        return 1
    prev2, prev1 = 1, 1
    for _ in range(2, n + 1):
        prev2, prev1 = prev1, prev1 + prev2
    return prev1
```

---

## Worked Problems

### Problem 1: Climbing Stairs (LeetCode #70) — Easy

**Clarifying Questions:**
- Can we take 0 steps? → No (we must reach step n)
- What's the minimum n? → n = 1
- Integer result fits in int? → Yes (n ≤ 45)

**Brute Force:** Recursive — exponential time O(2^n), too slow.

**Optimization:** Each step i can be reached from i-1 or i-2 — this is exactly Fibonacci. dp[i] = dp[i-1] + dp[i-2]. Space optimization: only need two previous values.

**Edge Cases:**
- n=1 → 1 way (single step of 1)
- n=2 → 2 ways (1+1 or 2)

**Code:**
```python
def climbStairs(n):
    if n <= 2:
        return n
    prev2, prev1 = 1, 2
    for i in range(3, n + 1):
        prev2, prev1 = prev1, prev1 + prev2
    return prev1
```

**Time:** O(n) | **Space:** O(1)

**Follow-ups:**
- What if you can take 1, 2, or 3 steps? → dp[i] = dp[i-1] + dp[i-2] + dp[i-3]
- What if each step has a cost (LeetCode #746)? → dp[i] = cost[i] + min(dp[i-1], dp[i-2])
- How many ways with exactly k steps? → Combinatorics, not DP

---

### Problem 2: Coin Change (LeetCode #322) — Medium

**Clarifying Questions:**
- Can we use each coin multiple times? → Yes (unbounded knapsack)
- What if amount is 0? → Return 0
- What if it's impossible to make amount? → Return -1
- Coin denominations distinct? → Yes

**Brute Force:** Try all combinations recursively — exponential.

**Optimization:** Unbounded knapsack DP. `dp[i]` = minimum coins to make amount i. Transition: `dp[i] = min(dp[i - coin] + 1)` for each coin ≤ i.

**Edge Cases:**
- Amount = 0 → 0 coins
- No coin can divide amount → remain infinity → return -1
- Coins larger than amount → dp[amount] stays infinity

**Code:**
```python
def coinChange(coins, amount):
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0               # Base case: 0 coins to make amount 0
    
    for i in range(1, amount + 1):
        for coin in coins:
            if coin <= i and dp[i - coin] != float('inf'):
                dp[i] = min(dp[i], dp[i - coin] + 1)
    
    return dp[amount] if dp[amount] != float('inf') else -1
```

**Time:** O(amount × len(coins)) | **Space:** O(amount)

**State transition diagram:**
```
coins = [1, 2, 5], amount = 6

dp: [0, 1, 1, 2, 2, 1, 2]
     0  1  2  3  4  5  6

dp[5] = 1  (one coin of 5)
dp[6] = dp[1] + 1 = 2  (coin 5 → then coin 1)
```

**Follow-ups:**
- Count number of ways to make amount (Coin Change 2, #518)? → Addition instead of min, order of loops matters
- If coins have denominations up to 10⁶? → dp array too large; use BFS instead
- Minimum coins with bounded supply? → 0/1 knapsack variant

---

### Problem 3: Longest Common Subsequence (LeetCode #1143) — Medium

**Clarifying Questions:**
- Subsequence vs substring? → Subsequence (non-contiguous; characters don't need to be adjacent)
- Case sensitive? → Yes
- Return length or the actual subsequence? → Length (return string is a follow-up)

**Brute Force:** Generate all subsequences of s1, check if each exists in s2 — O(2^m × n).

**Optimization:** 2D DP where `dp[i][j]` = LCS length of s1[:i] and s2[:j].
- If s1[i-1] == s2[j-1]: `dp[i][j] = dp[i-1][j-1] + 1`
- Else: `dp[i][j] = max(dp[i-1][j], dp[i][j-1])`

**Edge Cases:**
- One string empty → LCS = 0
- Identical strings → LCS = len(s1)
- No common characters → LCS = 0

**Code:**
```python
def longestCommonSubsequence(text1, text2):
    m, n = len(text1), len(text2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if text1[i-1] == text2[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1      # Characters match
            else:
                dp[i][j] = max(dp[i-1][j],        # Skip char from text1
                               dp[i][j-1])        # Skip char from text2
    
    return dp[m][n]
```

**State table visualization for "abcde" and "ace":**
```
    ""  a   c   e
""   0   0   0   0
a    0   1   1   1
b    0   1   1   1
c    0   1   2   2
d    0   1   2   2
e    0   1   2   3   ← answer = 3
```

**Time:** O(m × n) | **Space:** O(m × n), reducible to O(min(m,n)) with rolling array

**Space-optimized version:**
```python
def longestCommonSubsequence_opt(text1, text2):
    if len(text1) < len(text2):
        text1, text2 = text2, text1   # Shorter string as columns
    m, n = len(text1), len(text2)
    dp = [0] * (n + 1)
    
    for i in range(1, m + 1):
        prev = 0
        for j in range(1, n + 1):
            temp = dp[j]
            if text1[i-1] == text2[j-1]:
                dp[j] = prev + 1
            else:
                dp[j] = max(dp[j], dp[j-1])
            prev = temp
    return dp[n]
```

**Follow-ups:**
- Reconstruct the actual LCS? → Backtrack through dp table following the choices
- Longest common substring (contiguous)? → Reset to 0 on mismatch; track global max
- Edit distance (LeetCode #72)? → dp[i][j] = 0 (match) or 1 + min(insert, delete, replace)

---

## Common Mistakes

**1. Wrong initialization of dp array**
```python
# BAD: Initializing to 0 when looking for minimum (never updated)
dp = [0] * (amount + 1)   # dp[amount] might stay 0 falsely

# GOOD: Initialize to infinity for minimization problems
dp = [float('inf')] * (amount + 1)
dp[0] = 0
```

**2. Top-down vs bottom-up loop direction confusion**
```python
# 0/1 Knapsack: iterate weights BACKWARD in bottom-up
# (forward would reuse same item multiple times)
for w in range(capacity, weight - 1, -1):   # BACKWARD for 0/1
    dp[w] = max(dp[w], dp[w - weight] + value)

# Unbounded Knapsack: iterate weights FORWARD
for w in range(weight, capacity + 1):       # FORWARD for unbounded
    dp[w] = max(dp[w], dp[w - weight] + value)
```

**3. Off-by-one in 2D DP table indexing**
```python
# dp[i][j] represents s1[:i] and s2[:j] (lengths, not indices)
# Character access is s1[i-1] and s2[j-1]
if text1[i-1] == text2[j-1]:   # NOT text1[i]
    dp[i][j] = dp[i-1][j-1] + 1
```

**4. Not recognizing DP applicability — thinking greedy instead**
Greedy fails for Coin Change with arbitrary denominations:
```
coins = [1, 3, 4], amount = 6
Greedy: 4 + 1 + 1 = 3 coins
DP:     3 + 3 = 2 coins  ← optimal
```
Always verify greedy correctness with a proof or counterexample.

**5. Missing base cases**
```python
# LCS: dp[0][j] = 0 and dp[i][0] = 0 for all i, j
# These are set automatically when initializing to 0, but be explicit:
for i in range(m + 1):
    dp[i][0] = 0
for j in range(n + 1):
    dp[0][j] = 0
```

**6. Forgetting that dp size is (n+1), not n**
```python
# For LCS with strings of length m and n:
dp = [[0] * (n + 1) for _ in range(m + 1)]  # NOT n rows, n cols
```

---

## Interview Q&A

**Q1: How do you recognize a DP problem?**
Look for three signals: (1) optimization ("minimum", "maximum", "fewest", "longest"), (2) counting arrangements or paths, (3) feasibility check across choices. Then verify: can a problem be broken into subproblems? Do subproblems repeat? If yes to all, DP applies. If greedy seems obvious, prove it or test with a counterexample.

**Q2: When is top-down better than bottom-up?**
Top-down (memoization) is better when: the state space is sparse (many states never computed), the recurrence order is non-obvious, or the state involves complex indexing. Bottom-up is better when: all states are needed, you want to optimize space with rolling arrays, or you want to avoid recursion overhead and stack limits.

**Q3: How do you optimize DP space from O(m×n) to O(n)?**
Use a rolling array: observe that dp[i][j] only depends on row i-1. Keep only two rows (current and previous), or one row by iterating carefully. For LCS, maintain `prev` variable to track the diagonal value before overwriting.

**Q4: What's the difference between Coin Change (322) and Coin Change 2 (518)?**
#322 minimizes coin count (min transitions — use min). #518 counts number of ways (sum transitions — use addition). For #518, order of loops matters: outer loop on coins, inner on amounts — this counts combinations. Reversing loops would count permutations (each ordering as distinct).

**Q5: Explain the Bellman equation in DP.**
`V(state) = max over actions: reward(state, action) + γ × V(next_state)`. DP problems are essentially solving Bellman equations. The optimal substructure property means the value of a state can be computed from the values of reachable states — exactly what DP tables compute.

**Q6: How would you handle DP with floating point states (e.g., probability)?**
Use Python's float or Fraction. For probability DP: `dp[i] = sum(dp[j] × transition_probability(j → i))`. Be careful with floating point precision — consider using logarithms for very small probabilities to avoid underflow.

**Q7: What is memoization's time and space complexity?**
Time = number of unique states × cost per state transition. Space = number of unique states (for the cache) + recursion depth (call stack). For most 1D problems: O(n) time, O(n) space. For 2D: O(m×n) time and space. The call stack adds O(n) or O(m×n) on top of cache space.

**Q8: How do you debug a DP solution that gives wrong answers?**
Print the dp table for a small test case. Verify base cases manually. Trace through the recurrence for one cell. Check boundary conditions (empty string, zero capacity). Compare with brute force on small inputs. The most common bugs are: wrong initialization, wrong recurrence direction, and off-by-one in indexing.
