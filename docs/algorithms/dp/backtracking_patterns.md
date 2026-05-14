# Backtracking Algorithms: Decision Flowchart & Patterns

A comprehensive guide to backtracking algorithms for SDE interview preparation. Backtracking is a systematic exploration technique that explores all possible solutions through trial-and-error, abandoning (backtracking) when constraints are violated. This guide covers when to use backtracking, how to structure the algorithm, common patterns, and interview tips.

---

## When to Use Backtracking

Backtracking is the right approach when:

1. **You need ALL solutions** (not just one) — Backtracking exhaustively explores the solution space
2. **Solutions can be built incrementally** — You can construct partial solutions and extend them
3. **You can prune branches early** — Invalid branches can be identified and skipped without exploring them fully
4. **The problem has constraints** — Valid solutions must satisfy multiple constraints (no conflicts, balance, bijection, etc.)

**Key insight:** Backtracking = DFS on solution tree with early pruning.

### Backtracking Process

The algorithm follows this sequence:
1. **Build**: Add a choice to the current partial solution
2. **Check**: Verify that constraints are still satisfied
3. **Recurse**: Recursively solve the remaining subproblem
4. **Backtrack**: Undo the choice and try the next alternative

```
Backtracking on N-Queens (n=4):

Place queens row by row, checking for conflicts

  [0] Queen at (0,0)
    [1] Queen at (1,2) - check: no column/diagonal conflicts
      [2] Queen at (2,0) - fails: column conflict with (0,0) - BACKTRACK
      [2] Queen at (2,1) - fails: diagonal conflict with (1,2) - BACKTRACK
      [2] Queen at (2,3) - check: valid
        [3] Queen at (3,1) - check: valid → SOLUTION [0,2,1,3]... BACKTRACK
        [3] Try next... all fail → BACKTRACK
    [1] Try (1,3) → ... → SOLUTION [0,3,1,0]... found or exhausted → BACKTRACK
  [0] Try (0,1) → ... continue exhaustively
```

## Decision Flowchart

```mermaid
graph TD
    A["Does the problem require<br/>FINDING ALL solutions?"] -->|No| B["Not backtracking<br/>Try greedy, DP, or other"]
    A -->|Yes| C["Can you build<br/>incrementally?"]
    
    C -->|No| B
    C -->|Yes| D["What are you building?"]
    
    D -->|Permutations<br/>all orderings| E["permute()"]
    D -->|Combinations<br/>all selections| F["combine()"]
    D -->|Subsets<br/>power set| G["subsets()"]
    D -->|Constrained placement<br/>no conflicts| H["solve_nqueens(),<br/>solve_sudoku()"]
    D -->|Path in grid| I["word_search()"]
    D -->|Balanced strings| J["generate_parentheses()"]
    D -->|Mapping to strings| K["letter_combinations(),<br/>word_pattern_match()"]
```

## Algorithm Summary Table

| Algorithm | Problem | Time | Space | Key Insight |
|-----------|---------|------|-------|-------------|
| N-Queens | Place n queens, no conflicts | O(N!) | O(N²) | Prune early if position invalid |
| Sudoku | Fill 9x9 grid, row/col/box unique | O(9^(n²)) | O(1) | Constraint checking is key |
| Word Search | Find path in grid for word | O(N·M·4^L) | O(L) | Track visited cells per path |
| Permutations | All orderings of list | O(N! · N) | O(N!) | Use indices or marked set |
| Combinations | All k-selections from n | O(C(n,k)·k) | O(k) | Use start index to avoid duplicates |
| Subsets | Power set | O(N · 2^N) | O(2^N) | Include all decisions |
| Letter Combos | Keypad combinations | O(4^N · N) | O(4^N) | Multiply possible outputs |
| Parentheses | Valid n-pair brackets | O(Cat_N) | O(N) | Track open vs closed count |

## Template Pattern

```python
def backtrack_problem(input_data):
    result = []
    
    def is_valid(path, candidate):
        # Check constraints for current decision
        return True/False
    
    def backtrack(path, remaining_choices):
        # Base case: solution complete
        if is_complete(path):
            result.append(path[:])  # Copy to result
            return
        
        # Pruning: skip invalid branches early
        if not is_promising(path):
            return
        
        # Explore all choices
        for choice in get_next_choices(remaining_choices):
            # Build
            path.append(choice)
            
            # Recurse
            backtrack(path, remaining_choices - {choice})
            
            # Backtrack (undo)
            path.pop()
    
    backtrack([], input_data)
    return result
```

## Common Mistakes

1. **Forgetting to copy** when adding to result - use `path[:]` not `path`
2. **Not backtracking** after recursion - must undo changes
3. **No pruning** - check constraints early to reduce search space
4. **Using indices wrong** - start index vs element indices matter

## When NOT to Backtrack

- ✗ Only need one solution → use greedy or DP
- ✗ Only need count → use combinatorics (math formula)
- ✗ All solutions fit pattern → use iteration (letters)

## Interview Tips

**Permutations vs Combinations:**
- Permutations: Use index tracking or "seen" set, remove each element
- Combinations: Use start index to avoid duplicates automatically

**Grid Problems:**
- Mark visited BEFORE recursing
- Unmark visited AFTER recursing (to explore other branches)
- Use visited set per path, not global

**Constraint Satisfaction:**
- Check constraints as early as possible
- Return false immediately when constraint violated
- Prune branches before exploring

**Complexity Analysis:**
- Time is often O(k^n) where k=choices per level, n=depth
- Space is recursion depth + output size
- Focus on pruning effectiveness, not absolute numbers
