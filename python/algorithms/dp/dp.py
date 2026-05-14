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


# ============================================================================
# SECTION 2: BACKTRACKING ALGORITHMS
# ============================================================================
# Systematic exploration of decision space with constraint-based pruning.
# Each algorithm generates all valid solutions by building incrementally
# and backtracking when constraints are violated.

def solve_nqueens(n: int) -> list[list[int]]:
    """
    Solve N-Queens problem: place n queens on an n×n board with no conflicts.

    Each solution is represented as a list where index = row, value = column.
    Example: [1, 3, 0, 2] means Queen at (0,1), (1,3), (2,0), (3,2).

    Time: O(N!) - exploring N! permutations with pruning
    Space: O(N) - recursion depth + result storage

    Use when: Constraint satisfaction, board/placement problems, need all solutions
    Interview tip: Explain pruning - why we reject invalid placements early
    """
    def is_safe(col_placement, row, col):
        """Check if placing queen at (row, col) is safe."""
        for prev_row in range(row):
            prev_col = col_placement[prev_row]
            # Check same column or diagonal
            if prev_col == col or abs(prev_row - row) == abs(prev_col - col):
                return False
        return True

    def backtrack(col_placement, row):
        """Recursively place queens row by row."""
        if row == n:
            result.append(col_placement[:])
            return

        for col in range(n):
            if is_safe(col_placement, row, col):
                col_placement[row] = col
                backtrack(col_placement, row + 1)
                col_placement[row] = -1  # Reset for backtracking

    result = []
    backtrack([-1] * n, 0)
    return result


def solve_sudoku(board: list[list[int]]) -> None:
    """
    Solve Sudoku puzzle in-place using backtracking.

    0 represents empty cells. Modifies board in-place.
    Time: O(9^(n²)) worst-case, but typically much faster with constraint propagation
    Space: O(1) excluding recursion stack (modifies board in-place)

    Use when: Constraint satisfaction with multiple constraints, exact cover problems
    Interview tip: Discuss how constraint propagation (tracking possibilities) speeds up naive backtracking
    """
    def is_valid(board, row, col, num):
        """Check if placing num at (row, col) is valid."""
        # Check row
        if num in board[row]:
            return False

        # Check column
        if num in [board[i][col] for i in range(9)]:
            return False

        # Check 3x3 box
        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(box_row, box_row + 3):
            for j in range(box_col, box_col + 3):
                if board[i][j] == num:
                    return False

        return True

    def backtrack():
        """Find next empty cell and try numbers 1-9."""
        for row in range(9):
            for col in range(9):
                if board[row][col] == 0:
                    for num in range(1, 10):
                        if is_valid(board, row, col, num):
                            board[row][col] = num
                            if backtrack():
                                return True
                            board[row][col] = 0  # Backtrack
                    return False
        return True  # All cells filled

    backtrack()


def word_search(board: list[list[str]], word: str) -> bool:
    """
    Search for word in 2D grid (word must be contiguous, no cell reuse).

    Time: O(N·M·4^L) where N,M are grid dims, L is word length, 4 neighbors per cell
    Space: O(L) for recursion depth

    Use when: Grid traversal with constraints, avoiding revisits, path finding
    Interview tip: Explain visited set strategy and why we unmark during backtrack
    """
    if not board or not word:
        return False

    rows, cols = len(board), len(board[0])

    def dfs(row, col, index, visited):
        if index == len(word):
            return True

        if row < 0 or row >= rows or col < 0 or col >= cols:
            return False
        if (row, col) in visited or board[row][col] != word[index]:
            return False

        visited.add((row, col))
        found = (dfs(row+1, col, index+1, visited) or
                 dfs(row-1, col, index+1, visited) or
                 dfs(row, col+1, index+1, visited) or
                 dfs(row, col-1, index+1, visited))
        visited.remove((row, col))

        return found

    for i in range(rows):
        for j in range(cols):
            if dfs(i, j, 0, set()):
                return True
    return False


def permute(nums: list[int]) -> list[list[int]]:
    """
    Generate all permutations (arrangements) of a list.

    Time: O(N! · N) - N! permutations, each takes O(N) to copy
    Space: O(N!) for storing all permutations

    Use when: All arrangements needed, order matters, each element used once
    Interview tip: Show both swap-based and removed-element approaches
    """
    result = []

    def backtrack(path):
        if len(path) == len(nums):
            result.append(path[:])
            return

        for i in range(len(nums)):
            if nums[i] not in path:
                path.append(nums[i])
                backtrack(path)
                path.pop()

    backtrack([])
    return result


def combine(n: int, k: int) -> list[list[int]]:
    """
    Generate all combinations C(n, k) from [1, n].

    Time: O(C(n,k) · k) - C(n,k) combinations, each takes O(k) to copy
    Space: O(C(n,k)) for storing results

    Use when: All selections needed, order doesn't matter, each element used once
    Interview tip: Explain why we use start index to avoid duplicates
    """
    result = []

    def backtrack(start, path):
        if len(path) == k:
            result.append(path[:])
            return

        for i in range(start, n + 1):
            path.append(i)
            backtrack(i + 1, path)
            path.pop()

    backtrack(1, [])
    return result


def letter_combinations(digits: str) -> list[str]:
    """
    Generate all letter combinations for phone keypad input.

    Mapping: 2=abc, 3=def, 4=ghi, 5=jkl, 6=mno, 7=pqrs, 8=tuv, 9=wxyz

    Time: O(4^N · N) where N is digit count, 4 is max letters per digit
    Space: O(4^N) for results

    Use when: Combinations from multiple choices with variable counts
    Interview tip: Compare with backtracking - this is simpler iteration pattern
    """
    if not digits:
        return []

    mapping = {
        '2': 'abc', '3': 'def', '4': 'ghi', '5': 'jkl',
        '6': 'mno', '7': 'pqrs', '8': 'tuv', '9': 'wxyz'
    }
    result = []

    def backtrack(index, path):
        if index == len(digits):
            result.append(''.join(path))
            return

        letters = mapping[digits[index]]
        for letter in letters:
            path.append(letter)
            backtrack(index + 1, path)
            path.pop()

    backtrack(0, [])
    return result


def subsets(nums: list[int]) -> list[list[int]]:
    """
    Generate all subsets (power set) of a list.

    Time: O(N · 2^N) - 2^N subsets, each takes O(N) to copy worst-case
    Space: O(2^N) for results

    Use when: All subsequences needed, subset sums, inclusion-exclusion
    Interview tip: Show backtracking approach (easy to understand) vs bit-shift approach (efficient)
    """
    result = []

    def backtrack(index, path):
        result.append(path[:])

        for i in range(index, len(nums)):
            path.append(nums[i])
            backtrack(i + 1, path)
            path.pop()

    backtrack(0, [])
    return result


def generate_parentheses(n: int) -> list[str]:
    """
    Generate all valid n-pair parentheses combinations.

    Valid means: every '(' has matching ')', properly nested.

    Time: O(4^N / √N) - Catalan number C_N ≈ 4^N / (N^1.5 · √π)
    Space: O(4^N / √N) for results

    Use when: Balanced bracket generation, valid sequences, constraint satisfaction
    Interview tip: Show how tracking open count prunes invalid branches early
    """
    result = []

    def backtrack(open_count, close_count, path):
        if open_count == n and close_count == n:
            result.append(''.join(path))
            return

        if open_count < n:
            path.append('(')
            backtrack(open_count + 1, close_count, path)
            path.pop()

        if close_count < open_count:
            path.append(')')
            backtrack(open_count, close_count + 1, path)
            path.pop()

    backtrack(0, 0, [])
    return result


# ============================================================================
# SECTION 3: GRID & 2D DP ALGORITHMS
# ============================================================================
# Dynamic programming on 2D grids with multiple constraints and movements.
# Key patterns: direction-aware DP, min/max path problems, obstacle handling.

def unique_paths(m: int, n: int) -> int:
    """
    Count unique paths in m×n grid moving only right or down.

    Time: O(m·n)
    Space: O(m·n) or O(min(m,n)) with space optimization

    Use when: Path counting, monotonic movement, small state space
    Interview tip: Show both 2D DP and space-optimized 1D approach
    """
    dp = [[1] * n for _ in range(m)]

    for i in range(1, m):
        for j in range(1, n):
            dp[i][j] = dp[i-1][j] + dp[i][j-1]

    return dp[m-1][n-1]


def bomb_enemy(grid: list[list[str]]) -> int:
    """
    Maximum enemies that can be killed by placing one bomb.

    Bomb kills all enemies in same row/column until hitting wall 'W'.
    '0'=empty, 'E'=enemy, 'W'=wall

    Time: O(m·n) with preprocessing
    Space: O(m·n) for DP tables

    Use when: 2D range queries, directional constraints
    Interview tip: Explain preprocessing matrices for each direction
    """
    if not grid:
        return 0
    m, n = len(grid), len(grid[0])

    # Count enemies in rows (counting reset by walls)
    rows = [[0]*n for _ in range(m)]
    for i in range(m):
        count = 0
        for j in range(n):
            if grid[i][j] == 'W':
                count = 0
            else:
                if grid[i][j] == 'E':
                    count += 1
                rows[i][j] = count

    # Count enemies in columns (counting reset by walls)
    cols = [[0]*n for _ in range(m)]
    for j in range(n):
        count = 0
        for i in range(m):
            if grid[i][j] == 'W':
                count = 0
            else:
                if grid[i][j] == 'E':
                    count += 1
                cols[i][j] = count

    max_kill = 0
    for i in range(m):
        for j in range(n):
            if grid[i][j] == '0':
                max_kill = max(max_kill, rows[i][j] + cols[i][j])

    return max_kill


def max_island_area(grid: list[list[int]]) -> int:
    """
    Maximum area of island (connected 1s) in binary grid.

    Time: O(m·n) - visit each cell once
    Space: O(m·n) for visited set or recursion

    Use when: Connected components, area/perimeter calculation
    Interview tip: Compare DFS (clean code) vs BFS (less stack risk) vs Union-Find
    """
    if not grid:
        return 0

    visited = set()

    def dfs(i, j):
        if i < 0 or i >= len(grid) or j < 0 or j >= len(grid[0]):
            return 0
        if (i, j) in visited or grid[i][j] == 0:
            return 0

        visited.add((i, j))
        area = 1
        area += dfs(i+1, j) + dfs(i-1, j) + dfs(i, j+1) + dfs(i, j-1)
        return area

    max_area = 0
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            if grid[i][j] == 1 and (i, j) not in visited:
                max_area = max(max_area, dfs(i, j))

    return max_area


def dungeon_game(dungeon: list[list[int]]) -> int:
    """
    Minimum health required to traverse dungeon and reach exit.

    Health must always be ≥ 1. Each cell changes health by its value.

    Time: O(m·n)
    Space: O(m·n) or O(n) with space optimization

    Use when: Reverse DP, min constraint propagation, path requirements
    Interview tip: Explain why reverse (bottom-right to top-left) is necessary
    """
    if not dungeon:
        return 0

    m, n = len(dungeon), len(dungeon[0])
    dp = [[0] * n for _ in range(m)]

    # Minimum health needed at exit is 1
    dp[m-1][n-1] = max(1, 1 - dungeon[m-1][n-1])

    # Fill last row (can only move right)
    for j in range(n-2, -1, -1):
        dp[m-1][j] = max(1, dp[m-1][j+1] - dungeon[m-1][j])

    # Fill last column (can only move down)
    for i in range(m-2, -1, -1):
        dp[i][n-1] = max(1, dp[i+1][n-1] - dungeon[i][n-1])

    # Fill rest of table
    for i in range(m-2, -1, -1):
        for j in range(n-2, -1, -1):
            min_health_needed = min(dp[i+1][j], dp[i][j+1]) - dungeon[i][j]
            dp[i][j] = max(1, min_health_needed)

    return dp[0][0]


def trapping_rain_water_2d(elevation_map: list[list[int]]) -> int:
    """
    Trap rainwater in 2D elevation map.

    Water fills to minimum boundary height.

    Time: O(m·n·log(m·n)) with priority queue
    Space: O(m·n)

    Use when: 2D range min queries, priority queue-based search
    Interview tip: Explain why boundary cells are processed first (water flows out)
    """
    import heapq

    if not elevation_map or not elevation_map[0]:
        return 0

    m, n = len(elevation_map), len(elevation_map[0])
    visited = [[False] * n for _ in range(m)]
    water = 0

    # Start from boundary (water flows out at edges)
    pq = []
    for i in range(m):
        for j in range(n):
            if i == 0 or i == m-1 or j == 0 or j == n-1:
                heapq.heappush(pq, (elevation_map[i][j], i, j))
                visited[i][j] = True

    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    while pq:
        height, i, j = heapq.heappop(pq)

        for di, dj in directions:
            ni, nj = i + di, j + dj
            if 0 <= ni < m and 0 <= nj < n and not visited[ni][nj]:
                visited[ni][nj] = True
                water += max(0, height - elevation_map[ni][nj])
                heapq.heappush(pq, (max(height, elevation_map[ni][nj]), ni, nj))

    return water


def word_ladder(begin_word: str, end_word: str, word_list: list[str]) -> int:
    """
    Shortest word ladder transformation (BFS on implicit graph).

    Each step changes one letter. All intermediate words in word_list.

    Time: O(n·L²) where n=list size, L=word length
    Space: O(n·L)

    Use when: Shortest path on implicit graph, pattern-based edges
    Interview tip: Discuss word pattern generation (wildcard matching)
    """
    from collections import deque

    if end_word not in word_list:
        return 0

    word_set = set(word_list)
    queue = deque([(begin_word, 1)])
    visited = {begin_word}

    while queue:
        word, level = queue.popleft()

        if word == end_word:
            return level

        for i in range(len(word)):
            for c in 'abcdefghijklmnopqrstuvwxyz':
                new_word = word[:i] + c + word[i+1:]
                if new_word in word_set and new_word not in visited:
                    visited.add(new_word)
                    queue.append((new_word, level + 1))

    return 0


def word_pattern_match(pattern: str, str_: str) -> bool:
    """
    Match pattern to string with bijective mapping.

    Each char in pattern maps to unique substring in str_.

    Time: O(n · 2^m) where n=str length, m=pattern length (exponential in pattern)
    Space: O(m + n) for mapping and recursion

    Use when: Pattern matching, bijective constraints, backtracking with state
    Interview tip: Show memo optimization to avoid recomputation
    """
    memo = {}

    def helper(pi, si, mapping, reverse_mapping):
        if pi == len(pattern) and si == len(str_):
            return True
        if pi == len(pattern) or si == len(str_):
            return False

        key = (pi, si, tuple(sorted(mapping.items())))
        if key in memo:
            return memo[key]

        p_char = pattern[pi]

        for end in range(si + 1, len(str_) + 1):
            sub_str = str_[si:end]

            if p_char in mapping:
                if mapping[p_char] != sub_str:
                    continue
                if helper(pi + 1, end, mapping, reverse_mapping):
                    memo[key] = True
                    return True
            elif sub_str in reverse_mapping:
                continue
            else:
                mapping[p_char] = sub_str
                reverse_mapping[sub_str] = p_char

                if helper(pi + 1, end, mapping, reverse_mapping):
                    memo[key] = True
                    return True

                del mapping[p_char]
                del reverse_mapping[sub_str]

        memo[key] = False
        return False

    return helper(0, 0, {}, {})


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
