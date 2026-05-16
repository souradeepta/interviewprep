# Coding Interview Framework: 45-Minute Problem Solving

A proven 5-step framework for solving algorithmic problems in 45-minute technical interviews.

---

## Phase 1: Clarify & Verify (5 minutes)

**Goal:** Understand the problem completely before coding.

### Questions to Ask

**Input/Output:**
- "What's the input format? (array, string, tree, graph)"
- "What are the constraints on input size?"
- "What should I return?"

**Edge Cases:**
- "Should I handle empty input?"
- "Are there negative numbers / duplicates?"
- "What's the maximum value of n?"

**Optimization Hints:**
- "Is there a specific time or space target?"
- "Would O(n log n) be acceptable?"

### Template to Fill Out

```
Problem: [Name]

Input: [Format and constraints]
Output: [What to return]

Constraints:
- n: _____
- Values: _____
- Time: O(?)
- Space: O(?)

Examples:
Input: _____
Output: _____
```

---

## Phase 2: Think Aloud (2-3 minutes)

**Goal:** Show your thinking process. Avoid silent coding.

### Approach to Discuss

**Brute Force First:**
- "Naive approach: [O(n²) solution]"
- Explain the idea, even if it's not optimal

**Identify Pattern:**
- "I notice this looks like a [DP/BFS/greedy] problem"
- "This is similar to [known pattern] because..."

**Optimize:**
- "Can I use [data structure] to improve to O(n log n)?"
- "What trade-off am I making (time vs. space)?"

### Red Flags to Avoid

- ❌ Silent coding with no explanation
- ❌ Jumping to code without discussing approach
- ❌ Implementing complex solution without verifying idea first
- ❌ Over-optimizing prematurely

**Green Flags to Show**

- ✅ "Let me verify my understanding first"
- ✅ "My brute force is O(n²), let me optimize to..."
- ✅ "I'll use [structure] because it gives me O(?) complexity"
- ✅ "Let me trace through an example to verify"

---

## Phase 3: Code Cleanly (25-30 minutes)

**Goal:** Write readable, bug-free code.

### Structure to Follow

```
1. Function signature with clear parameter names
2. Input validation (if time permits)
3. Initialize data structures
4. Main logic (clearly structured)
5. Return result
```

### Best Practices

**Naming:**
- Use descriptive variable names (not `i`, `x`, `temp`)
- Avoid single-letter vars except loop counters

**Structure:**
- Break into helper functions if >20 lines
- Use comments for non-obvious steps only
- Keep indentation consistent

**Avoid Common Mistakes:**
- Off-by-one errors: use `i < n` not `i <= n` (verify bounds)
- Null pointer checks: handle `None` / `null` cases
- Integer overflow: use `//` for integer division, watch modulo
- Mutable default arguments: `def func(arr=[])` is bad

### Python Template

```python
def solve(arr, target):
    # Validate input
    if not arr:
        return []
    
    # Initialize
    result = []
    seen = set()
    
    # Main logic
    for num in arr:
        if num not in seen:
            # Process
            result.append(num)
            seen.add(num)
    
    return result
```

### Java Template

```java
public class Solution {
    public int[] solve(int[] arr, int target) {
        // Validate
        if (arr == null || arr.length == 0) {
            return new int[]{};
        }
        
        // Initialize
        List<Integer> result = new ArrayList<>();
        Set<Integer> seen = new HashSet<>();
        
        // Main logic
        for (int num : arr) {
            if (!seen.contains(num)) {
                result.add(num);
                seen.add(num);
            }
        }
        
        // Convert and return
        return result.stream().mapToInt(i -> i).toArray();
    }
}
```

---

## Phase 4: Test & Verify (5-8 minutes)

**Goal:** Ensure correctness before submitting.

### Test Cases to Run

**Happy Path:**
- Example given in problem statement
- Trace through your code step-by-step

**Edge Cases:**
- Empty input: `[]`, `""`, `None`
- Single element: `[5]`
- Duplicates: `[1, 1, 1]`
- Negatives: `[-5, 0, 5]`
- Boundary values: `[0, MAX_INT, MIN_INT]`

### How to Trace

```
Input: [3, 1, 4, 1, 5]
Target: 1

Step 1: num=3, seen={}, add 3 → result=[3], seen={3}
Step 2: num=1, seen={3}, add 1 → result=[3,1], seen={3,1}
Step 3: num=4, seen={3,1}, add 4 → result=[3,1,4], seen={3,1,4}
Step 4: num=1, seen={3,1,4}, skip (duplicate)
Step 5: num=5, seen={3,1,4}, add 5 → result=[3,1,4,5], seen={3,1,4,5}

Output: [3,1,4,5] ✓
```

### Verification Checklist

- ✓ Code compiles/runs without syntax errors
- ✓ Happy path example produces correct output
- ✓ Edge cases handled (empty, single, negatives, max)
- ✓ No off-by-one errors in loops
- ✓ Variable initializations are correct
- ✓ Return statement is correct

---

## Phase 5: Complexity & Discussion (5-10 minutes)

**Goal:** Articulate time/space complexity and discuss improvements.

### Complexity Calculation

**Time Complexity:**
- Identify the dominant loop/operation
- Count iterations: "I loop through n elements once: O(n)"
- Count nested loops: "For each of n, I do log n binary search: O(n log n)"
- Add asymptotics: "O(n) iteration + O(1) per element = O(n)"

**Space Complexity:**
- Hash set storing n elements: O(n)
- Recursion depth d on call stack: O(d)
- Output array of size m: O(m)

**Example:**

```
Problem: Remove duplicates from array

Time: O(n) - single pass through array
Space: O(n) - hash set stores up to n elements in worst case (all unique)

Can we do better?
- Time: Already optimal (need to look at each element once)
- Space: Could sort in-place O(1) but that modifies input
- Trade-off: O(n) space for O(n) time is good here
```

### Follow-up Optimization

**If you finished with time left:**
- "Can I optimize space from O(n) to O(1)?"
- "Can I solve this in O(n) instead of O(n²)?"
- "What if the array was sorted? Could I use two pointers?"

**If you struggled with bugs:**
- "Let me refactor this section to be clearer"
- "Can I break this into helper functions?"

---

## Communication During Interview

### What to Say

| Situation | What to Say |
|-----------|-----------|
| **Stuck on approach** | "Let me think about this... [pause] The brute force would be... [explain]. Can I optimize?" |
| **Found a pattern** | "I notice this is similar to [problem pattern]." |
| **Trade-off decision** | "I'm choosing O(n) time and O(n) space because the time constraint is more important here." |
| **Found a bug** | "Wait, let me trace through this again... I see the issue is [explain]." |
| **Don't know solution** | "I'm not sure of the optimal approach. Let me code the brute force first: [explain]." |
| **Time running out** | "I see we're running short. Let me [finish core logic / explain remaining approach]." |

### Red Flags to Avoid

| Mistake | Why It Hurts |
|---------|-------------|
| Silent for 10+ minutes | Interviewer can't follow your thinking |
| Coding without planning | Leads to bugs, wastes time rewriting |
| Not asking clarifying questions | Miss constraints, solve wrong problem |
| Ignoring edge cases | Solution fails on simple inputs |
| Off-by-one errors | Code doesn't compile or fails test |
| Blaming the problem | "This problem is ambiguous" (even if true) |

---

## Problem Categories & Patterns

### Arrays & Strings

| Pattern | Time | Approach |
|---------|------|----------|
| Two pointers | O(n) | Converge from ends |
| Sliding window | O(n) | Fixed/dynamic window |
| Prefix sum | O(n) | Precompute cumulative |
| Hashing | O(n) | Store in set/dict |
| Sorting | O(n log n) | Sort then solve |

### Trees & Graphs

| Pattern | Time | Approach |
|---------|------|----------|
| BFS | O(n+e) | Level-order queue |
| DFS | O(n+e) | Recursive traversal |
| Binary search tree | O(log n) avg | Leverage BST property |
| Union-Find | O(α(n)) | Track components |
| Topological sort | O(n+e) | DFS/Kahn's |

### Dynamic Programming

| Pattern | Time | Approach |
|---------|------|----------|
| 1D DP | O(n) | Recurrence on prev state |
| 2D DP | O(n²) | Table filling |
| Backtracking | O(k^n) | Explore all choices |
| Memoization | O(states) | Cache results |

---

## Coding Interview Checklist

- ✓ Ask clarifying questions (constraints, edge cases)
- ✓ Think aloud about approach before coding
- ✓ Start with brute force, then optimize
- ✓ Use clear variable names and structure
- ✓ Trace through example while coding
- ✓ Handle edge cases (empty, single, negatives, max)
- ✓ Test code on provided examples
- ✓ Discuss time and space complexity
- ✓ Explain trade-offs in your solution
- ✓ Ask if interviewer wants further optimization

---

## Interview Checklist by Time

| Time | Action |
|------|--------|
| 0-5 min | Clarify problem, ask questions, verify understanding |
| 5-10 min | Discuss approach, draw examples, get agreement |
| 10-35 min | Code cleanly, trace through examples, fix bugs |
| 35-40 min | Test on edge cases, verify correctness |
| 40-45 min | Discuss complexity, mention optimizations, wrap up |

