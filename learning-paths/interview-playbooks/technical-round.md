---
title: "Technical Interview Playbook"
interview_type: "Technical Coding Round"
duration: "45-60 minutes"
difficulty: "Medium to Hard"
focus: "All Data Structures, Algorithms, Problem-Solving"
---

# Technical Interview Playbook

**Duration:** 45-60 minutes  
**Expected Problems:** 1-2 problems (1 medium + 1 hard, OR 2 medium)  
**Goal:** Solve correctly, optimize, handle edge cases

---

## Interview Format

### Time Breakdown (60 min total)
- **0-2 min:** Greeting & setup
- **2-5 min:** Problem statement
- **5-10 min:** Clarify requirements & examples
- **10-35 min:** Whiteboard/code solution (20-25 min coding)
- **35-45 min:** Test with examples & edge cases
- **45-55 min:** Optimize or second problem
- **55-60 min:** Final questions

---

## What to Expect

**Problem Type:** Usually 1 MEDIUM problem, or 1 MEDIUM + 1 EASY follow-up.

**Topics:** Any domain — arrays, trees, graphs, DP, etc.

**Difficulty:** Problem that takes 20-25 minutes to solve correctly.

**Evaluation:**
- Understand problem and edge cases
- Propose reasonable solution
- Code it correctly (no bugs)
- Test with examples and edge cases
- Optimize time/space if asked
- Communicate throughout

---

## Domain Focus

Prepare MEDIUM-tier problems from these domains:

| Domain | Solve Count | Time Each |
|--------|------------|-----------|
| Arrays | 2 | 20 min |
| Strings | 1 | 20 min |
| Trees | 2 | 20 min |
| Graphs | 2 | 20 min |
| Dynamic Programming | 2 | 20 min |
| Linked Lists | 1 | 20 min |
| Hash Tables | 1 | 15 min |

See [4-Week Focused Track](../sequential-tracks/4-week-focused.md) for curated problems.

---

## Sample Problem Strategies

### High-Probability Problem 1: Tree Traversal (Medium)
- **Common variants:** Path sum, level order, lowest common ancestor
- **Key insight:** DFS vs BFS trade-off
- **Approach:** Recursion vs iterative with stack/queue
- See: [Trees Domain](../domains/trees.md)

### High-Probability Problem 2: Graph BFS/DFS (Medium)
- **Common variants:** Number of islands, connected components
- **Key insight:** Mark visited to avoid cycles
- **Approach:** Use queue for BFS or stack for DFS
- See: [Graphs Domain](../domains/graphs.md)

### High-Probability Problem 3: DP (Medium)
- **Common variants:** Coin change, house robber, LCS
- **Key insight:** Identify state and transitions
- **Approach:** Memoization or tabulation
- See: [Dynamic Programming Domain](../domains/dynamic-programming.md)

---

## Interview Strategy

### Phase 1: Clarify (5 min)
✅ Repeat problem back  
✅ Ask about edge cases  
✅ Confirm input constraints  
✅ "Should I modify input?" "Any memory constraints?"

### Phase 2: Approach (5 min)
✅ Explain approach before coding  
✅ Propose time/space complexity  
✅ Ask "Does this sound right?"  
❌ Don't jump to coding

### Phase 3: Code (20-25 min)
✅ Pseudocode first (2 min)  
✅ Then write actual code (15-20 min)  
✅ Write clean code — interviewer reads it  
✅ Use helper functions for clarity

### Phase 4: Test (10 min)
✅ Test with provided example  
✅ Test with YOUR example  
✅ Test edge cases:
  - Empty input
  - Single element
  - Large input
  - All same elements
  - Negative numbers

### Phase 5: Optimize (5-10 min, if time)
✅ Can we do better time-wise?  
✅ Can we use less space?  
✅ Any bugs in current solution?

---

## Common Pitfalls

### ❌ Mistakes to Avoid
- Coding before explaining approach
- Only testing happy path
- Off-by-one errors (index boundaries)
- Forgetting edge cases
- Not testing before declaring done
- Using unexplained variable names

### ✅ How to Avoid
- Always explain first, then code
- Always test with edge cases BEFORE declaring done
- Use meaningful variable names
- Run code mentally before coding
- Ask "Did I handle empty input?"

---

## Debugging Under Pressure

If you get stuck or find a bug:

1. **Stay calm** — Bugs are normal, interviewers expect it
2. **Explain the bug** — "I think the issue is here..."
3. **Walk through logic** — Trace through an example
4. **Ask for hint** — "Should I be thinking about this differently?"
5. **Fix it** — Make the fix, test again

Interviewers LIKE seeing you debug. It shows problem-solving.

---

## What Interviewers Care About

1. **Can you understand problems?** — You get requirements, ask smart questions
2. **Can you code?** — Clean, readable, working code
3. **Do you test?** — You check edge cases
4. **Can you communicate?** — You explain your thinking
5. **Can you optimize?** — You think about time/space trade-offs

---

## 🔗 Resources

- [All Domains](../domains/) — Pick weakest and drill
- [4-Week Focused Track](../sequential-tracks/4-week-focused.md) — Curated problems
- [Mock Interviewer](../../AGENTS.md) — Practice sessions
