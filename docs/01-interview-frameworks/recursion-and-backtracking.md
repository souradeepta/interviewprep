# Recursion & Backtracking Mastery: Decision Trees and Exploration

**Level:** L3-L4
**Time to read:** ~20 min

Master recursive problem solving and backtracking patterns for combinatorial problems.

---

## Recursion Fundamentals

**3 Components:**
1. Base case: When to stop recursing
2. Recursive case: How to break problem into smaller subproblems
3. Return value: Combine results from subproblems

```python
def recursion_template(problem):
    # Base case
    if is_base_case(problem):
        return base_solution
    
    # Recursive case
    subproblem = reduce_problem(problem)
    subresult = recursion_template(subproblem)
    
    # Combine results
    return combine(problem, subresult)
```

---

## Backtracking Pattern

**Core Idea:** Explore all possibilities, undo choices if not leading to solution.

```python
def backtrack(candidates, current_path, result):
    # Base case: found complete solution
    if is_solution(current_path):
        result.append(current_path[:])
        return
    
    # Try each candidate
    for candidate in candidates:
        # Prune: skip if candidate can't lead to solution
        if not is_valid(candidate, current_path):
            continue
        
        # Choose: add to path
        current_path.append(candidate)
        
        # Explore: recursively solve
        backtrack(get_next_candidates(candidate), current_path, result)
        
        # Undo: remove from path
        current_path.pop()
    
    return result
```

---

## Classic Backtracking Problems

### Permutations

```python
def permutations(nums):
    result = []
    
    def backtrack(path, remaining):
        if not remaining:
            result.append(path)
            return
        
        for i, num in enumerate(remaining):
            backtrack(path + [num], remaining[:i] + remaining[i+1:])
    
    backtrack([], nums)
    return result

# Time: O(n!), Space: O(n)
```

### Combinations

```python
def combinations(nums, k):
    result = []
    
    def backtrack(start, path):
        if len(path) == k:
            result.append(path)
            return
        
        for i in range(start, len(nums)):
            backtrack(i + 1, path + [nums[i]])
    
    backtrack(0, [])
    return result

# Time: O(C(n,k)), Space: O(k)
```

### Subsets (Power Set)

```python
def subsets(nums):
    result = []
    
    def backtrack(start, path):
        result.append(path[:])  # Record current path as a subset
        
        for i in range(start, len(nums)):
            path.append(nums[i])
            backtrack(i + 1, path)
            path.pop()
    
    backtrack(0, [])
    return result

# Time: O(n·2^n), Space: O(n)
```

### N-Queens

```python
def solve_n_queens(n):
    result = []
    board = ['.' * n for _ in range(n)]
    
    def is_safe(row, col, board):
        # Check column
        for i in range(row):
            if board[i][col] == 'Q':
                return False
        
        # Check diagonals
        for i, j in zip(range(row-1, -1, -1), range(col-1, -1, -1)):
            if board[i][j] == 'Q':
                return False
        for i, j in zip(range(row-1, -1, -1), range(col+1, n)):
            if board[i][j] == 'Q':
                return False
        
        return True
    
    def backtrack(row):
        if row == n:
            result.append(board[:])
            return
        
        for col in range(n):
            if is_safe(row, col, board):
                board[row] = board[row][:col] + 'Q' + board[row][col+1:]
                backtrack(row + 1)
                board[row] = board[row][:col] + '.' + board[row][col+1:]
    
    backtrack(0)
    return result

# Time: O(n!), Space: O(n)
```

---

## Optimization Techniques

### Pruning (Avoid Exploring Dead Ends)

```python
def backtrack_with_pruning(candidates, target):
    result = []
    candidates.sort()
    
    def backtrack(start, path, remaining):
        if remaining == 0:
            result.append(path)
            return
        
        for i in range(start, len(candidates)):
            # Pruning: if candidates[i] > remaining, skip
            if candidates[i] > remaining:
                break
            
            # Continue with this candidate
            backtrack(i, path + [candidates[i]], remaining - candidates[i])
    
    backtrack(0, [], target)
    return result

# Pruning reduces search space significantly
```

### Memoization (Cache Results)

```python
def backtrack_with_memo(n, memo={}):
    if n in memo:
        return memo[n]
    
    if n <= 1:
        return n
    
    result = backtrack_with_memo(n-1, memo) + backtrack_with_memo(n-2, memo)
    memo[n] = result
    return result

# Avoid recomputing same subproblems
```

---

## Recursion vs Iteration

| Aspect | Recursion | Iteration |
|--------|-----------|-----------|
| **Readability** | Often clearer for trees/graphs | Clearer for linear problems |
| **Space** | O(h) call stack | O(1) typically |
| **Speed** | Slower (function calls) | Faster |
| **Safety** | Stack overflow risk | No depth limit |
| **Use** | DFS, backtracking | BFS, DP |

---

## Recursion Checklist

- ✓ Base case defined clearly
- ✓ Recursive case reduces problem size
- ✓ No infinite recursion
- ✓ Verified with small examples (n=1,2)
- ✓ Time complexity acceptable (not exponential unless necessary)
- ✓ Space complexity acceptable (stack depth)
- ✓ Consider converting to iteration if too deep

