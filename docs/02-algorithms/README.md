# New Curated Problems for Learning Paths

This directory contains the infrastructure for **58 new curated problems** designed to fill gaps in the learning path domains.

---

## Status

- ✅ **Definitions:** All 58 problems documented with descriptions, patterns, and requirements
- ✅ **Templates:** Code structure templates for Python and Java
- ✅ **Examples:** 2 sample problems fully implemented (reverse linked list, coin change)
- ⏳ **Implementation:** 56 remaining problems need solutions

---

## Files

- **PROBLEM_DEFINITIONS.md** — Complete list of all 58 problems, organized by domain
- **TEMPLATE.md** — Code structure and style guidelines
- **python/new_problems/** — Python solution files
- **java/new_problems/** — Java solution files

---

## Quick Start: Implement a Problem

### 1. Choose a Problem
Start with problems in priority order:
1. Linked Lists (9 needed)
2. Bit Manipulation (7 needed)
3. Dynamic Programming (7 needed)
4. Strings (7 needed)

See `PROBLEM_DEFINITIONS.md` for the full list.

### 2. Create Solution Files

Create two files following the template in `TEMPLATE.md`:

```bash
python/new_problems/{problem_name}.py
java/new_problems/{ProblemName}.java
```

### 3. Use Examples as Reference

See completed implementations:
- `python/new_problems/reverse_linked_list.py` (Linked List - Easy)
- `java/new_problems/ReverseLinkedList.java` (Linked List - Easy)
- `python/new_problems/coin_change.py` (Dynamic Programming - Medium)
- `java/new_problems/CoinChange.java` (Dynamic Programming - Medium)

### 4. Test Locally

Run your Python file:
```bash
python3 python/new_problems/my_problem.py
```

Compile and run Java:
```bash
cd java/new_problems
javac MyProblem.java
java MyProblem
```

### 5. Link to Learning Path

Add the problem to the appropriate domain file in `learning-paths/domains/`:

```markdown
N. **Problem Name** (Time) ⭐⭐
   - **Problem:** Description
   - **Pattern:** Pattern name
   - **Solutions:** 
     - [Python](../../python/new_problems/problem_name.py)
     - [Java](../../java/new_problems/ProblemName.java)
```

---

## Implementation Checklist

For each problem:

- [ ] Python file created with docstring
- [ ] Java file created with JavaDoc comments
- [ ] Both have test cases
- [ ] Both pass test cases
- [ ] Time/space complexity documented
- [ ] Code follows template style
- [ ] Problem added to domain file
- [ ] Problem linked from playbook (if applicable)

---

## Current Progress

### Implemented (2 problems)
1. ✅ **Reverse Linked List** (Linked Lists, Easy)
   - Python: `reverse_linked_list.py`
   - Java: `ReverseLinkedList.java`

2. ✅ **Coin Change** (Dynamic Programming, Medium)
   - Python: `coin_change.py`
   - Java: `CoinChange.java`

### Not Yet Implemented (56 problems)

By domain:
- Linked Lists: 8 remaining
- Bit Manipulation: 7
- Dynamic Programming: 6
- Strings: 7
- Arrays: 6
- Graphs: 6
- Sorting & Searching: 6
- Heaps: 4
- Hash Tables: 3
- Stacks/Queues: 3
- System Design Fundamentals: 3

---

## Tips for Efficient Implementation

1. **Batch by pattern:** Implement similar problems together (e.g., all hash map problems)
2. **Use existing code:** Copy utility functions (ListNode, TreeNode, etc.) from existing implementations
3. **Test as you go:** Don't implement all 56 without testing
4. **Start with easy:** Easier problems build momentum
5. **Focus on coverage:** Prioritize filling gaps (linked lists first)

---

## Example Workflow

### Week 1: Linked Lists (9 problems)
```
Day 1: Reverse Linked List (done)
Day 2: Detect Cycle
Day 3: Remove Nth Node
...
```

### Week 2: DP (7 problems)
```
Day 1: Coin Change (done)
Day 2: Climbing Stairs
Day 3: House Robber
...
```

---

## After Implementation

Once all 58 problems are implemented:

1. **Update domain files** with links to new problems
2. **Update sequential tracks** to include new problems
3. **Run validation** to check all links
4. **Test learning paths** end-to-end
5. **Commit to main** branch

---

## Resources

- **PROBLEM_DEFINITIONS.md** — Problem statements and patterns
- **TEMPLATE.md** — Code structure examples
- **Learning Paths** — Where these problems will be linked
- **Existing Code** — Reference implementations in `python/` and `java/`

---

## Questions?

Each problem in `PROBLEM_DEFINITIONS.md` includes:
- Clear problem statement
- Example input/output
- Key pattern(s) to use
- Expected time complexity
- File paths where solutions go

Start with any problem and use the templates as a guide!
