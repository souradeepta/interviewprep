# Grid & 2D DP: Pattern Recognition & Decision Flowchart

A comprehensive guide to solving problems on 2D grids using dynamic programming. Grid DP problems involve filling or analyzing a 2D array with specific patterns and constraints. This guide covers pattern recognition, solution templates, and detailed examples for each category.

---

## Understanding Grid DP

Grid DP involves solving problems on m×n 2D arrays where:
- **State**: `dp[i][j]` represents the optimal solution for the subgrid from `(0,0)` to `(i,j)` or a specific property at position `(i,j)`
- **Transition**: Each cell's value depends on neighbors (typically top and left for forward DP, or bottom and right for reverse)
- **Key constraint**: Grid dimensions and movement rules (4-directional, only right/down, etc.)

### Example: Unique Paths

```
Problem: Count paths in m×n grid moving only right or down

Grid (3×3):
  [1] [2] [3]
  [4] [5] [6]
  [7] [8] [9]

Movement: → or ↓ only

DP approach:
  dp[i][j] = number of ways to reach (i,j) from (0,0)
  dp[i][j] = dp[i-1][j] + dp[i][j-1]  (from top or left)

Example: 3×3 grid
  dp[0][0]=1    (start)
  dp[0][1]=1    (only right)
  dp[0][2]=1    (only right)
  dp[1][0]=1    (only down)
  dp[1][1]=2    (top=1 + left=1)
  dp[1][2]=3    (top=1 + left=2)
  dp[2][0]=1    (only down)
  dp[2][1]=3    (top=2 + left=1)
  dp[2][2]=6    (top=3 + left=3)  ← Answer

Paths: 6 unique paths from (0,0) to (2,2)
```

---

## Grid Problem Patterns

```mermaid
graph TD
    A["Is it a grid problem?"] -->|No| B["Use other DP patterns"]
    A -->|Yes| C["What's the goal?"]
    
    C -->|Count paths/ways| D["Unique Paths<br/>Combinations"]
    C -->|Find max/min| E["What's changing?"]
    C -->|Hit all targets| F["State compression<br/>BFS"]
    C -->|Transform | G["Word Ladder<br/>BFS"]
    
    E -->|Direction| H["Dungeon Game<br/>Reverse DP"]
    E -->|Obstacles| I["Max Island<br/>Connected components"]
    E -->|Height/elevation| J["Trapping Rain<br/>Priority Queue"]
    E -->|Direction constraints| K["Bomb Enemy<br/>Preprocessing"]
```

## Grid DP Template

```python
def grid_dp(grid):
    m, n = len(grid), len(grid[0])
    dp = [[0] * n for _ in range(m)]
    
    # Initialize first cell
    dp[0][0] = initial_value(grid[0][0])
    
    # Fill first row (if applicable)
    for j in range(1, n):
        dp[0][j] = compute_from_left(dp[0][j-1], grid[0][j])
    
    # Fill first column (if applicable)
    for i in range(1, m):
        dp[i][0] = compute_from_top(dp[i-1][0], grid[i][0])
    
    # Fill rest of table
    for i in range(1, m):
        for j in range(1, n):
            dp[i][j] = combine(
                dp[i-1][j],      # from top
                dp[i][j-1],      # from left
                grid[i][j]       # current cell
            )
    
    return dp[m-1][n-1]
```

## Direction Handling Variations

**Down/Right only**: Simple left/top dependencies
**All 4 directions**: Need BFS or special handling
**Reverse (min health)**: Process bottom-right to top-left
**2D ranges (water)**: Use priority queue

## Problem Categories

| Category | Algorithm | Pattern | Example |
|----------|-----------|---------|---------|
| Path Counting | unique_paths | DP[i][j] = DP[i-1][j] + DP[i][j-1] | m×n grid, right/down only |
| Constraint Optimization | bomb_enemy | Precompute per direction | Range queries per row/col |
| Connected Components | max_island_area | DFS/BFS all connected cells | Island maximum area |
| Reverse Constraint | dungeon_game | Process bottom-right to top-left | Minimum health requirement |
| Elevation/Boundaries | trapping_rain_water_2d | Priority queue + visited | Water level between boundaries |
| Path Finding | word_ladder | BFS on implicit graph | Shortest transformation path |
| Pattern Matching | word_pattern_match | Bijective backtracking | String-to-pattern assignment |

## Complexity Summary

| Algorithm | Time | Space | Type |
|-----------|------|-------|------|
| Unique Paths | O(m·n) | O(m·n) | Path counting |
| Bomb Enemy | O(m·n·(m+n)) | O(m·n) | Preprocessing |
| Max Island | O(m·n) | O(m·n) | Connected components |
| Dungeon Game | O(m·n) | O(m·n) | Reverse DP |
| Trapping Rain 2D | O(m·n·log(m·n)) | O(m·n) | Priority queue |
| Word Ladder | O(n·L²) | O(n·L) | Implicit graph BFS |
| Word Pattern | O(n·2^m) | O(m+n) | Bijective backtrack |

## Interview Tips

**Initialization:**
- First cell depends on problem (usually base case)
- First row and column often have special rules
- Consider boundary conditions

**Direction Handling:**
- Forward direction: process top-left to bottom-right
- Reverse direction: process bottom-right to top-left
- All directions: often requires BFS with explicit queue

**Space Optimization:**
- Simple 2D DP: keep full table
- Space-optimized: keep only previous row or two rows
- Challenge: Can you do it in O(1) space?

**Connected Components:**
- Use DFS/BFS for each unvisited cell
- Mark visited to avoid revisits
- Count increments per component found

**Constraint Propagation:**
- Multiple constraints (row, col, box): check all
- Early termination: return false immediately on failure
- Precomputation: compute auxiliary tables once
