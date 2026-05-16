# Dynamic Programming Mastery: From Theory to Optimization

Master dynamic programming patterns, state representation, and optimization techniques.

---

## DP Decision Tree

```
Problem has optimal substructure?
├─ No → Not DP problem
└─ Yes → Can break into subproblems?
    ├─ No → Greedy/math solution
    └─ Yes → Overlapping subproblems?
        ├─ No → Divide & conquer (no DP benefit)
        └─ Yes → DP applicable
            ├─ 1D state → 1D DP
            ├─ 2D state → 2D DP
            ├─ Multiple intervals → Interval DP
            └─ Tree structure → Tree DP
```

---

## DP State Representation

**Key Insight:** Correctly defining state is 90% of DP problem solving.

### 1D DP: Single Dimension

```python
# dp[i] = answer for subproblem involving first i elements

# Fibonacci: dp[i] = F(i)
dp[i] = dp[i-1] + dp[i-2]

# Coin change: dp[i] = min coins to make amount i
dp[i] = min(dp[i - coin] + 1) for each coin

# LIS: dp[i] = length of longest increasing subsequence ending at i
dp[i] = max(dp[j] + 1) for all j < i where arr[j] < arr[i]
```

### 2D DP: Two Dimensions

```python
# dp[i][j] = answer involving first i of first array, first j of second

# Edit distance: dp[i][j] = min edits to transform s1[0..i] to s2[0..j]
if s1[i] == s2[j]:
    dp[i][j] = dp[i-1][j-1]
else:
    dp[i][j] = 1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])

# Knapsack: dp[i][w] = max value with first i items and weight limit w
dp[i][w] = max(dp[i-1][w], dp[i-1][w-weight[i]] + value[i])

# LCS: dp[i][j] = longest common subsequence of s1[0..i] and s2[0..j]
if s1[i] == s2[j]:
    dp[i][j] = dp[i-1][j-1] + 1
else:
    dp[i][j] = max(dp[i-1][j], dp[i][j-1])
```

### Interval DP: Range Problems

```python
# dp[i][j] = answer for subarray/substring arr[i..j]

# Matrix chain multiplication: min multiplications for arr[i..j]
dp[i][j] = min(dp[i][k] + dp[k+1][j] + cost) for i <= k < j

# Palindrome partitions: min cuts to make arr[i..j] all palindromes
dp[i][j] = min(dp[i][k] + dp[k+1][j] + 1) for i <= k < j
```

### Tree DP: Tree Structure

```python
# dp[node] = answer for subtree rooted at node

# Max path sum in tree
dp[node] = max(
    node.val + dp[left] + dp[right],  # Include both children
    node.val + dp[left],              # Include left only
    node.val + dp[right],             # Include right only
    node.val                          # Just this node
)

# Tree coloring: dp[node][color] = max score coloring subtree
dp[node][c] = node.val[c] + sum(max(dp[child][c2]) for c2 != c)
```

---

## State Transition Patterns

### Pattern 1: Position-Based (Take/Skip)

```python
# dp[i] = best answer considering arr[0..i]
# Recurrence: dp[i] = max(take arr[i], skip arr[i])

def house_robber(arr):
    n = len(arr)
    dp = [0] * n
    dp[0] = arr[0]
    dp[1] = max(arr[0], arr[1])
    
    for i in range(2, n):
        dp[i] = max(dp[i-1], dp[i-2] + arr[i])  # Skip or take
    
    return dp[n-1]
```

### Pattern 2: Bounded Knapsack

```python
# dp[i][w] = max value with first i items and weight ≤ w
# Recurrence: include item i or don't

def knapsack_01(weights, values, capacity):
    n = len(weights)
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]
    
    for i in range(1, n + 1):
        for w in range(capacity + 1):
            # Don't take item i-1
            dp[i][w] = dp[i-1][w]
            # Take item i-1 if it fits
            if weights[i-1] <= w:
                dp[i][w] = max(dp[i][w], dp[i-1][w - weights[i-1]] + values[i-1])
    
    return dp[n][capacity]
```

### Pattern 3: Unbounded (Unlimited Supply)

```python
# dp[i] = answer for amount i (items can be reused)

def coin_change(coins, amount):
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0
    
    for i in range(1, amount + 1):
        for coin in coins:
            if coin <= i:
                dp[i] = min(dp[i], dp[i - coin] + 1)
    
    return dp[amount] if dp[amount] != float('inf') else -1
```

### Pattern 4: Sequence Matching

```python
# dp[i][j] = match score for s1[0..i] and s2[0..j]

def edit_distance(s1, s2):
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i-1] == s2[j-1]:
                dp[i][j] = dp[i-1][j-1]
            else:
                dp[i][j] = 1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])
    
    return dp[m][n]
```

### Pattern 5: Counting/Combinations

```python
# dp[i] = number of ways to reach state i

def climb_stairs(n):
    # Ways to climb n stairs (1 or 2 steps at a time)
    dp = [0] * (n + 1)
    dp[0] = 1  # 1 way to stay at ground
    dp[1] = 1  # 1 way to reach step 1
    
    for i in range(2, n + 1):
        dp[i] = dp[i-1] + dp[i-2]  # From previous 2 states
    
    return dp[n]
```

---

## Optimization Techniques

### 1. Space Optimization (Rolling Array)

```python
# ❌ O(n) space
def fib_space_n(n):
    dp = [0] * (n + 1)
    dp[0], dp[1] = 0, 1
    for i in range(2, n + 1):
        dp[i] = dp[i-1] + dp[i-2]
    return dp[n]

# ✓ O(1) space (only need last 2 values)
def fib_space_1(n):
    prev, curr = 0, 1
    for _ in range(n):
        prev, curr = curr, prev + curr
    return prev
```

### 2. Monotonic Optimization (Convex Hull Trick)

```python
# For recurrences: dp[i] = min(dp[j] + cost(j, i))
# If cost has specific properties, reduce O(n²) to O(n) or O(n log n)

# Requires: slopes monotonic or queries in specific order
```

### 3. Memoization (Top-Down)

```python
# Alternative to tabulation: compute on-demand

def fib_memo(n, memo={}):
    if n in memo:
        return memo[n]
    if n <= 1:
        return n
    
    memo[n] = fib_memo(n-1, memo) + fib_memo(n-2, memo)
    return memo[n]
```

### 4. Prefix Sums (Speed Up Transitions)

```python
# If transition is: dp[i] = min(dp[j]) for j in range
# Precompute prefix min for O(1) lookup

prefix_min = [0] * (n + 1)
for i in range(n):
    prefix_min[i+1] = min(prefix_min[i], dp[i])

# Now dp[i] = prefix_min[i] + cost[i]  # O(1) instead of O(n)
```

---

## Common DP Problems & Patterns

| Problem | State | Transition | Space | Time |
|---------|-------|-----------|-------|------|
| Fibonacci | dp[i] | dp[i] = dp[i-1] + dp[i-2] | O(1) | O(n) |
| Climbing stairs | dp[i] | dp[i] = dp[i-1] + dp[i-2] | O(1) | O(n) |
| House robber | dp[i] | dp[i] = max(dp[i-1], dp[i-2] + arr[i]) | O(1) | O(n) |
| LIS O(n²) | dp[i] = LIS length at i | dp[i] = max(dp[j] + 1) | O(n) | O(n²) |
| LIS O(n log n) | Binary search optimized | Use bisect + auxiliary array | O(n) | O(n log n) |
| Coin change | dp[i] = min coins for i | dp[i] = min(dp[i-coin] + 1) | O(n) | O(n·k) |
| 0/1 Knapsack | dp[w] = max value ≤ w | Iterate items, update backwards | O(w) | O(n·w) |
| Edit distance | dp[i][j] | Match/insert/delete/replace | O(m·n) | O(m·n) |
| LCS | dp[i][j] = LCS(s1[0..i], s2[0..j]) | Match or skip | O(m·n) | O(m·n) |

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| **Wrong base case** | Trace first 2-3 values by hand |
| **Forgetting to initialize** | Set dp[0] (or dp[0][0]) correctly |
| **Order of iteration** | Top-down (memoization) or bottom-up (tabulation) with correct order |
| **Off-by-one in indexing** | Use 1-indexed dp to match problem naturally |
| **Not identifying state** | Draw state diagram first: what does dp[i] represent? |
| **Confusing recurrence** | Write 2-3 examples to verify transition formula |

---

## DP Checklist

- ✓ Identified optimal substructure
- ✓ Defined state clearly (what does dp[i] represent?)
- ✓ Found recurrence relation
- ✓ Identified base case(s)
- ✓ Verified with small examples (n=1,2,3)
- ✓ Analyzed time complexity
- ✓ Optimized space if needed
- ✓ Implemented iteratively (easier) or recursively with memo
- ✓ Tested on edge cases (n=0, n=1, negative)

