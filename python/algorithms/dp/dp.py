"""
Dynamic Programming Algorithms
===============================
Classic DP patterns for SDE interview preparation.

Each function includes docstrings with time/space complexity and a
concrete demonstration in the __main__ block at the bottom.
"""

import bisect
from functools import lru_cache


# ---------------------------------------------------------------------------
# 1. Fibonacci — memoization / tabulation / space-optimized
# ---------------------------------------------------------------------------

def fibonacci(n: int) -> dict:
    """Compute the n-th Fibonacci number using three DP strategies.

    Compares memoization (top-down), tabulation (bottom-up), and
    the space-optimized two-variable approach.

    Parameters
    ----------
    n : int
        Non-negative integer index (F(0)=0, F(1)=1).

    Returns
    -------
    dict with keys:
        'memoization'    : int  — result via top-down memoization
        'tabulation'     : int  — result via bottom-up table
        'space_optimized': int  — result via O(1) space iteration

    Complexity
    ----------
    All three variants:
        Time  : O(n)
        Space : O(n) for memoization and tabulation, O(1) for optimized
    """

    # --- top-down with memoization ---
    memo: dict[int, int] = {}

    def _memo(k: int) -> int:
        if k <= 1:
            return k
        if k not in memo:
            memo[k] = _memo(k - 1) + _memo(k - 2)
        return memo[k]

    result_memo = _memo(n)

    # --- bottom-up tabulation ---
    if n == 0:
        result_tab = 0
    elif n == 1:
        result_tab = 1
    else:
        table = [0] * (n + 1)
        table[1] = 1
        for i in range(2, n + 1):
            table[i] = table[i - 1] + table[i - 2]
        result_tab = table[n]

    # --- space-optimized ---
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    result_space = a

    return {
        "memoization": result_memo,
        "tabulation": result_tab,
        "space_optimized": result_space,
    }


# ---------------------------------------------------------------------------
# 2. 0/1 Knapsack
# ---------------------------------------------------------------------------

def knapsack_01(
    weights: list[int],
    values: list[int],
    capacity: int,
) -> tuple[int, list[int]]:
    """0/1 Knapsack — maximize total value without exceeding capacity.

    Each item can be taken at most once (0/1 choice).

    Parameters
    ----------
    weights : list[int]
        Weight of each item.
    values : list[int]
        Value of each item.
    capacity : int
        Maximum weight the knapsack can hold.

    Returns
    -------
    max_value : int
        Maximum achievable value.
    chosen_items : list[int]
        Indices (0-based) of items included in the optimal solution.

    Complexity
    ----------
    Time  : O(n * capacity)
    Space : O(n * capacity)  — full table kept for backtracking
    """
    n = len(weights)
    # dp[i][w] = max value using items 0..i-1 with capacity w
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        wi, vi = weights[i - 1], values[i - 1]
        for w in range(capacity + 1):
            dp[i][w] = dp[i - 1][w]
            if wi <= w:
                dp[i][w] = max(dp[i][w], dp[i - 1][w - wi] + vi)

    # Backtrack to find chosen items
    chosen = []
    w = capacity
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i - 1][w]:
            chosen.append(i - 1)
            w -= weights[i - 1]
    chosen.reverse()

    return dp[n][capacity], chosen


# ---------------------------------------------------------------------------
# 3. Longest Common Subsequence
# ---------------------------------------------------------------------------

def lcs(s1: str, s2: str) -> tuple[int, str]:
    """Longest Common Subsequence of two strings.

    Parameters
    ----------
    s1, s2 : str
        Input strings.

    Returns
    -------
    length : int
        Length of the LCS.
    subsequence : str
        One LCS (there may be multiple of equal length).

    Complexity
    ----------
    Time  : O(m * n)   where m = len(s1), n = len(s2)
    Space : O(m * n)
    """
    m, n = len(s1), len(s2)
    # dp[i][j] = LCS length of s1[:i] and s2[:j]
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    # Backtrack
    seq = []
    i, j = m, n
    while i > 0 and j > 0:
        if s1[i - 1] == s2[j - 1]:
            seq.append(s1[i - 1])
            i -= 1
            j -= 1
        elif dp[i - 1][j] >= dp[i][j - 1]:
            i -= 1
        else:
            j -= 1
    seq.reverse()

    return dp[m][n], "".join(seq)


# ---------------------------------------------------------------------------
# 4. Longest Increasing Subsequence — O(n log n) patience sorting
# ---------------------------------------------------------------------------

def lis(arr: list[int]) -> tuple[int, list[int]]:
    """Longest Increasing Subsequence via patience sorting.

    Uses binary search (bisect_left) to maintain a *tails* array where
    tails[i] is the smallest tail element of all increasing subsequences
    of length i+1 found so far.

    Parameters
    ----------
    arr : list[int]
        Input sequence.

    Returns
    -------
    length : int
        Length of the LIS.
    subsequence : list[int]
        One actual LIS (reconstructed via predecessor links).

    Complexity
    ----------
    Time  : O(n log n)
    Space : O(n)
    """
    if not arr:
        return 0, []

    n = len(arr)
    tails: list[int] = []   # tails[i] = smallest tail for LIS of length i+1
    tail_idx: list[int] = []  # index in arr of each tail
    pred = [-1] * n          # predecessor array for reconstruction
    pos = [-1] * n           # position in tails array for each element

    for i, x in enumerate(arr):
        lo = bisect.bisect_left(tails, x)
        if lo == len(tails):
            tails.append(x)
            tail_idx.append(i)
        else:
            tails[lo] = x
            tail_idx[lo] = i
        pos[i] = lo
        pred[i] = tail_idx[lo - 1] if lo > 0 else -1

    # Reconstruct
    length = len(tails)
    idx = tail_idx[length - 1]
    subseq = []
    while idx != -1:
        subseq.append(arr[idx])
        idx = pred[idx]
    subseq.reverse()

    return length, subseq


# ---------------------------------------------------------------------------
# 5. Edit Distance (Levenshtein)
# ---------------------------------------------------------------------------

def edit_distance(s1: str, s2: str) -> tuple[int, list[str]]:
    """Levenshtein edit distance between two strings.

    Operations: insert, delete, substitute (each costs 1).

    Parameters
    ----------
    s1, s2 : str
        Source and target strings.

    Returns
    -------
    distance : int
        Minimum number of single-character edits.
    operations : list[str]
        Human-readable sequence of edit operations to transform s1 -> s2.

    Complexity
    ----------
    Time  : O(m * n)
    Space : O(m * n)
    """
    m, n = len(s1), len(s2)
    # dp[i][j] = edit distance between s1[:i] and s2[:j]
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(
                    dp[i - 1][j],      # delete from s1
                    dp[i][j - 1],      # insert into s1
                    dp[i - 1][j - 1],  # substitute
                )

    # Backtrack to recover operations
    ops = []
    i, j = m, n
    while i > 0 or j > 0:
        if i > 0 and j > 0 and s1[i - 1] == s2[j - 1]:
            ops.append(f"keep '{s1[i-1]}'")
            i -= 1
            j -= 1
        elif j > 0 and (i == 0 or dp[i][j - 1] <= dp[i - 1][j] and dp[i][j - 1] <= dp[i - 1][j - 1]):
            ops.append(f"insert '{s2[j-1]}'")
            j -= 1
        elif i > 0 and (j == 0 or dp[i - 1][j] <= dp[i][j - 1] and dp[i - 1][j] <= dp[i - 1][j - 1]):
            ops.append(f"delete '{s1[i-1]}'")
            i -= 1
        else:
            ops.append(f"substitute '{s1[i-1]}' -> '{s2[j-1]}'")
            i -= 1
            j -= 1
    ops.reverse()

    return dp[m][n], ops


# ---------------------------------------------------------------------------
# 6. Coin Change — minimum coins
# ---------------------------------------------------------------------------

def coin_change(coins: list[int], amount: int) -> tuple[int, list[int]]:
    """Minimum number of coins to make up *amount*.

    Parameters
    ----------
    coins : list[int]
        Available coin denominations (positive integers).
    amount : int
        Target amount (>= 0).

    Returns
    -------
    count : int
        Minimum number of coins, or -1 if the amount cannot be made.
    combination : list[int]
        Coins used in the optimal solution (multiset as sorted list).

    Complexity
    ----------
    Time  : O(amount * len(coins))
    Space : O(amount)
    """
    INF = float("inf")
    dp = [INF] * (amount + 1)
    dp[0] = 0
    last_coin = [-1] * (amount + 1)  # for reconstruction

    for a in range(1, amount + 1):
        for c in coins:
            if c <= a and dp[a - c] + 1 < dp[a]:
                dp[a] = dp[a - c] + 1
                last_coin[a] = c

    if dp[amount] == INF:
        return -1, []

    # Reconstruct
    combination = []
    cur = amount
    while cur > 0:
        combination.append(last_coin[cur])
        cur -= last_coin[cur]

    return dp[amount], sorted(combination)


# ---------------------------------------------------------------------------
# 7. Matrix Chain Multiplication
# ---------------------------------------------------------------------------

def matrix_chain_mult(dims: list[int]) -> tuple[int, str]:
    """Optimal parenthesization for matrix chain multiplication.

    Parameters
    ----------
    dims : list[int]
        Sequence of n+1 dimensions: matrix i has size dims[i] x dims[i+1].
        Must have at least 2 elements (1 matrix).

    Returns
    -------
    min_ops : int
        Minimum number of scalar multiplications.
    parenthesization : str
        Optimal parenthesization as a string, e.g. '((A0 x A1) x A2)'.

    Complexity
    ----------
    Time  : O(n^3)
    Space : O(n^2)
    """
    n = len(dims) - 1  # number of matrices
    # dp[i][j] = min cost to multiply matrices i..j (0-indexed)
    dp = [[0] * n for _ in range(n)]
    split = [[0] * n for _ in range(n)]

    for length in range(2, n + 1):         # chain length
        for i in range(n - length + 1):
            j = i + length - 1
            dp[i][j] = float("inf")
            for k in range(i, j):
                cost = dp[i][k] + dp[k + 1][j] + dims[i] * dims[k + 1] * dims[j + 1]
                if cost < dp[i][j]:
                    dp[i][j] = cost
                    split[i][j] = k

    def _build(i, j) -> str:
        if i == j:
            return f"A{i}"
        k = split[i][j]
        return f"({_build(i, k)} x {_build(k + 1, j)})"

    return dp[0][n - 1], _build(0, n - 1)


# ---------------------------------------------------------------------------
# 8. Longest Palindromic Substring — DP O(n²) + Manacher O(n)
# ---------------------------------------------------------------------------

def longest_palindromic_substr(s: str) -> dict:
    """Longest palindromic substring via two approaches.

    Parameters
    ----------
    s : str
        Input string.

    Returns
    -------
    dict with keys:
        'dp_result'      : str  — result via O(n²) DP
        'dp_length'      : int
        'manacher_result': str  — result via O(n) Manacher's algorithm
        'manacher_length': int

    Complexity
    ----------
    DP approach:
        Time  : O(n^2)
        Space : O(n^2)
    Manacher's algorithm:
        Time  : O(n)
        Space : O(n)
    """
    n = len(s)
    if n == 0:
        return {"dp_result": "", "dp_length": 0,
                "manacher_result": "", "manacher_length": 0}

    # --- DP approach ---
    # dp[i][j] = True if s[i..j] is a palindrome
    dp = [[False] * n for _ in range(n)]
    dp_start, dp_max = 0, 1
    for i in range(n):
        dp[i][i] = True

    for i in range(n - 1):
        if s[i] == s[i + 1]:
            dp[i][i + 1] = True
            dp_start, dp_max = i, 2

    for length in range(3, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            if s[i] == s[j] and dp[i + 1][j - 1]:
                dp[i][j] = True
                if length > dp_max:
                    dp_start, dp_max = i, length

    dp_result = s[dp_start: dp_start + dp_max]

    # --- Manacher's algorithm ---
    # Transform: "abc" -> "#a#b#c#"
    t = "#" + "#".join(s) + "#"
    tn = len(t)
    p = [0] * tn  # p[i] = radius of palindrome centred at i in t
    centre = right = 0

    for i in range(tn):
        if i < right:
            mirror = 2 * centre - i
            p[i] = min(right - i, p[mirror])
        while i + p[i] + 1 < tn and i - p[i] - 1 >= 0 and t[i + p[i] + 1] == t[i - p[i] - 1]:
            p[i] += 1
        if i + p[i] > right:
            centre, right = i, i + p[i]

    max_len_t = max(p)
    centre_t = p.index(max_len_t)
    # Map back to original string
    man_start = (centre_t - max_len_t) // 2
    man_result = s[man_start: man_start + max_len_t]

    return {
        "dp_result": dp_result,
        "dp_length": dp_max,
        "manacher_result": man_result,
        "manacher_length": max_len_t,
    }


# ---------------------------------------------------------------------------
# __main__ demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("DYNAMIC PROGRAMMING ALGORITHMS DEMO")
    print("=" * 60)

    # ---- Fibonacci ----
    print("\n--- Fibonacci (n=10) ---")
    fib = fibonacci(10)
    for method, val in fib.items():
        print(f"  {method:20s}: {val}")

    # ---- 0/1 Knapsack ----
    print("\n--- 0/1 Knapsack ---")
    weights = [2, 3, 4, 5]
    values  = [3, 4, 5, 6]
    cap = 8
    max_val, items = knapsack_01(weights, values, cap)
    print(f"  Max value: {max_val}  Items (0-indexed): {items}")

    # ---- LCS ----
    print("\n--- Longest Common Subsequence ---")
    length, subseq = lcs("ABCBDAB", "BDCABA")
    print(f"  LCS length: {length}  Subsequence: '{subseq}'")

    # ---- LIS ----
    print("\n--- Longest Increasing Subsequence ---")
    arr = [10, 9, 2, 5, 3, 7, 101, 18]
    l, seq = lis(arr)
    print(f"  LIS length: {l}  Subsequence: {seq}")

    # ---- Edit Distance ----
    print("\n--- Edit Distance ---")
    dist, ops = edit_distance("kitten", "sitting")
    print(f"  Distance: {dist}")
    for op in ops:
        print(f"    {op}")

    # ---- Coin Change ----
    print("\n--- Coin Change ---")
    count, combo = coin_change([1, 5, 6, 9], 11)
    print(f"  Min coins: {count}  Combination: {combo}")

    # No solution
    count2, _ = coin_change([3, 5], 7)
    print(f"  Coins [3,5] for 7: {count2}  (should be -1)")

    # ---- Matrix Chain ----
    print("\n--- Matrix Chain Multiplication ---")
    dims = [40, 20, 30, 10, 30]
    ops_count, parens = matrix_chain_mult(dims)
    print(f"  Min multiplications: {ops_count}")
    print(f"  Parenthesization: {parens}")

    # ---- Longest Palindromic Substring ----
    print("\n--- Longest Palindromic Substring ---")
    result = longest_palindromic_substr("babad")
    print(f"  Input: 'babad'")
    print(f"  DP result:      '{result['dp_result']}' (len {result['dp_length']})")
    print(f"  Manacher result: '{result['manacher_result']}' (len {result['manacher_length']})")

    result2 = longest_palindromic_substr("cbbd")
    print(f"  Input: 'cbbd'  -> '{result2['manacher_result']}'")
