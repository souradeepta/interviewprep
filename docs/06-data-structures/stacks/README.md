# Stacks — LIFO Order, O(1) Push/Pop/Peek

**Level:** L3-L4
**Time to read:** ~20 min

Last-In, First-Out. The data structure behind function calls, undo/redo, expression evaluation, and iterative DFS.

---

## Quick Summary

A stack stores elements with LIFO (Last-In, First-Out) access. Push adds to the top; pop removes from the top. Use when you need to reverse order, track "the last thing seen," or convert recursion to iteration. Key property: O(1) push/pop with no random access.

---

## Operations & Complexity Table

| Operation | Time (avg) | Time (worst) | Space | Notes                                |
|-----------|-----------|-------------|-------|--------------------------------------|
| Push      | O(1)      | O(n)*       | O(1)  | *O(n) only on dynamic array resize   |
| Pop       | O(1)      | O(1)        | O(1)  | Remove and return top element         |
| Peek/Top  | O(1)      | O(1)        | O(1)  | View top without removing             |
| Search    | O(n)      | O(n)        | O(1)  | No direct access — must pop to search |
| isEmpty   | O(1)      | O(1)        | O(1)  | Check size or top pointer             |
| Size      | O(1)      | O(1)        | O(1)  | Maintain a counter                    |

---

## Memory Layout / Internal Structure

```
Array-Backed Stack (Python list)
─────────────────────────────────────────────────────
top index = 3
         ↓
[ 10 | 20 | 30 | 40 | __ | __ ]
  [0]  [1]  [2]  [3]  [4]  [5]
                  ↑
               logical top (most recently pushed)

Push(50): top=4 → [ 10 | 20 | 30 | 40 | 50 | __ ]
Pop():    top=3 ← [ 10 | 20 | 30 | 40 | __ | __ ]  returns 50

Linked-List-Backed Stack
─────────────────────────────────────────────────────
top
 │
 ▼
┌──────┬──────┐     ┌──────┬──────┐     ┌──────┬──────┐
│  40  │  ──────►   │  30  │  ──────►   │  20  │  ──────►  ...
└──────┴──────┘     └──────┴──────┘     └──────┴──────┘
 (last pushed)

Push: prepend a new node, update top pointer → O(1)
Pop:  remove head node, advance top pointer → O(1)

Call Stack (OS/Language runtime)
─────────────────────────────────────────────────────
┌─────────────────┐  ← Stack grows downward
│  main()         │  frame 0: local vars, return addr
├─────────────────┤
│  foo(a=5)       │  frame 1: pushed on call
├─────────────────┤
│  bar(x=3)       │  frame 2: pushed on call
├─────────────────┤  ← stack pointer (SP)
│   (free space)  │
└─────────────────┘
```

---

## Trade-offs vs Alternatives

| Feature              | Stack         | Queue          | Deque               |
|----------------------|---------------|----------------|---------------------|
| Add/remove order     | LIFO          | FIFO           | Both ends           |
| Push to top/front    | O(1)          | O(1)           | O(1)                |
| Pop from top/front   | O(1)          | O(1)           | O(1)                |
| Random access        | No            | No             | O(n)                |
| Reverse traversal    | Natural       | Not native     | O(n)                |
| Use case             | DFS, undo     | BFS, scheduling| Sliding window      |

```
Array-backed vs Linked-list-backed stack:
┌────────────────────────────────────────────────────────────┐
│ Need bounded size (stack overflow protection)? → Array     │
│ Stack can grow unboundedly?                    → Either    │
│ Minimize allocations?                          → Array     │
│ Avoid resize cost at any push?                 → Linked    │
│ Cache performance matters?                     → Array     │
│ In Python?                                     → list      │
└────────────────────────────────────────────────────────────┘
```

---

## When NOT to Use

- **Need FIFO order** — use a queue; stack reverses order.
- **Need random access** — stacks only expose the top; use an array or deque.
- **Priority-based retrieval** — use a heap; stack doesn't sort on push.
- **Breadth-first search** — BFS requires a queue; using a stack gives DFS.
- **Deep recursion replacement without memory concern** — recursive call stack is simpler; only convert to explicit stack when stack overflow is a real risk (very deep trees).

---

## Core Operations (Code)

```python
# ── Python list as stack (idiomatic, array-backed) ────────────────────────
stack = []
stack.append(10)     # push  → O(1) amortized
stack.append(20)
stack.append(30)
top = stack[-1]      # peek  → O(1)
val = stack.pop()    # pop   → O(1), returns 30
is_empty = not stack # check → O(1)

# ── Explicit Stack class ───────────────────────────────────────────────────
class Stack:
    def __init__(self):
        self._data = []

    def push(self, val) -> None:
        self._data.append(val)

    def pop(self):
        if self.is_empty():
            raise IndexError("pop from empty stack")
        return self._data.pop()

    def peek(self):
        if self.is_empty():
            raise IndexError("peek from empty stack")
        return self._data[-1]

    def is_empty(self) -> bool:
        return len(self._data) == 0

    def size(self) -> int:
        return len(self._data)

# ── Monotonic Stack (pattern for next greater element) ────────────────────
def next_greater_element(nums: list[int]) -> list[int]:
    # For each element, find the next element that is greater.
    # Monotonic stack maintains a decreasing order.
    result = [-1] * len(nums)
    stack = []   # stores indices of elements with no answer yet

    for i, num in enumerate(nums):
        # Pop elements smaller than current: current is their "next greater"
        while stack and nums[stack[-1]] < num:
            idx = stack.pop()
            result[idx] = num
        stack.append(i)
    return result
    # Time: O(n) — each element pushed and popped at most once

# ── Iterative DFS using explicit stack ────────────────────────────────────
def dfs_iterative(graph: dict, start) -> list:
    visited = set()
    stack = [start]
    order = []
    while stack:
        node = stack.pop()
        if node not in visited:
            visited.add(node)
            order.append(node)
            for neighbor in graph[node]:
                if neighbor not in visited:
                    stack.append(neighbor)
    return order
```

---

## 3 Worked Problems

---

### Problem 1 — Valid Parentheses (LeetCode #20)

**Clarifying Questions**
- Which bracket types? `()`, `[]`, `{}`?
- Is an empty string valid? (Yes — vacuously true)
- Are there non-bracket characters? (No — input is brackets only)

**Brute Force**
```python
def is_valid_brute(s: str) -> bool:
    # Repeatedly remove matched pairs until nothing changes
    while "()" in s or "[]" in s or "{}" in s:
        s = s.replace("()", "").replace("[]", "").replace("{}", "")
    return s == ""
    # Time: O(n²) — each pass is O(n), up to n/2 passes
```

**Optimization**

Push open brackets; on close bracket, check that the top matches. If not, or if stack is empty on close, invalid.

```python
def is_valid(s: str) -> bool:
    match = {')': '(', ']': '[', '}': '{'}
    stack = []
    for ch in s:
        if ch in "([{":
            stack.append(ch)
        else:
            if not stack or stack[-1] != match[ch]:
                return False
            stack.pop()
    return not stack   # valid only if all opens were closed

```

**Edge Cases**
- `"]"` — close on empty stack → False.
- `"([)]"` — mismatched nesting → False (stack top is `[` when `)` arrives).
- `"(("` — stack non-empty at end → False.
- `""` — never enters loops, returns `not []` = True.

**Complexity**
- Time: O(n) — single pass
- Space: O(n) — worst case all opens

**Follow-ups**
- "Minimum removals to make valid?" → Count unmatched opens + unmatched closes (LeetCode #1249).
- "Generate all valid combinations?" → Backtracking with open/close counts (LeetCode #22).

---

### Problem 2 — Min Stack (LeetCode #155)

**Clarifying Questions**
- All operations O(1)? (Yes — that's the constraint)
- Can `getMin()` be called on an empty stack? (Guaranteed not per problem)
- What values — integers only? (Yes)

**Brute Force**
```python
class MinStackBrute:
    def __init__(self):
        self.data = []

    def push(self, val):
        self.data.append(val)

    def pop(self):
        self.data.pop()

    def top(self):
        return self.data[-1]

    def getMin(self):
        return min(self.data)   # O(n) — scans entire stack
```

**Optimization (Auxiliary Min Stack)**

Maintain a second stack that tracks the current minimum at each level. When pushing, push to min stack only if val <= current min. When popping, pop min stack if top equals popped value.

```python
class MinStack:
    def __init__(self):
        self.stack = []
        self.min_stack = []   # min_stack[-1] always holds current minimum

    def push(self, val: int) -> None:
        self.stack.append(val)
        # Push to min_stack if it's empty or val is <= current min
        if not self.min_stack or val <= self.min_stack[-1]:
            self.min_stack.append(val)

    def pop(self) -> None:
        val = self.stack.pop()
        if val == self.min_stack[-1]:
            self.min_stack.pop()

    def top(self) -> int:
        return self.stack[-1]

    def getMin(self) -> int:
        return self.min_stack[-1]

# Alternative: store (val, current_min) pairs in one stack
class MinStackPairs:
    def __init__(self):
        self.stack = []   # stores (value, min_so_far)

    def push(self, val: int) -> None:
        curr_min = min(val, self.stack[-1][1]) if self.stack else val
        self.stack.append((val, curr_min))

    def pop(self) -> None:
        self.stack.pop()

    def top(self) -> int:
        return self.stack[-1][0]

    def getMin(self) -> int:
        return self.stack[-1][1]
```

**Edge Cases**
- Duplicate minimums: `[3, 1, 1]` — when first 1 is popped, second 1 must still be in min_stack. Using `<=` instead of `<` handles this.
- Single element: min_stack holds it; pop removes from both.

**Complexity**
- Time: O(1) all operations
- Space: O(n) — min_stack at most same size as main stack

**Follow-ups**
- "Max Stack?" → Same pattern with a max auxiliary stack.
- "Median Stack?" → Need two heaps (much harder, O(log n) operations).

---

### Problem 3 — Evaluate Reverse Polish Notation (LeetCode #150)

**Clarifying Questions**
- What operators? `+`, `-`, `*`, `/` (integer division truncating toward zero)?
- Are operands guaranteed valid (no division by zero)? (Yes per problem)
- What's the result range? (Fits in 32-bit integer)

**Why RPN?**

RPN eliminates parentheses and operator precedence. `3 4 + 5 *` = `(3 + 4) * 5 = 35`. A stack evaluates it naturally: push operands, apply operators to top two elements.

```python
def eval_rpn(tokens: list[str]) -> int:
    stack = []
    ops = {
        '+': lambda a, b: a + b,
        '-': lambda a, b: a - b,
        '*': lambda a, b: a * b,
        '/': lambda a, b: int(a / b),   # truncate toward zero (not //!)
    }
    for token in tokens:
        if token in ops:
            b = stack.pop()   # second operand (top)
            a = stack.pop()   # first operand
            stack.append(ops[token](a, b))
        else:
            stack.append(int(token))
    return stack[0]

# Example trace: ["2","1","+","3","*"]
# token="2" → stack=[2]
# token="1" → stack=[2,1]
# token="+" → pop 1,2; push 3 → stack=[3]
# token="3" → stack=[3,3]
# token="*" → pop 3,3; push 9 → stack=[9]
# return 9
```

**Edge Cases**
- Division truncation: `-7 / 2` should be `-3` (toward zero), not `-4` (floor). Use `int(a/b)` not `a//b` in Python for negatives.
- Order of operands: `a - b` means first popped is `b` (right operand), second popped is `a` (left operand).
- Single number: `["42"]` → return 42.

**Complexity**
- Time: O(n) — process each token once
- Space: O(n) — stack holds at most (n+1)/2 operands

**Follow-ups**
- "Convert infix to RPN?" → Shunting-yard algorithm using operator stack + output queue.
- "Evaluate infix with parentheses?" → Two stacks (operands and operators); process precedence on push.

---

## Interview Q&A

**Q1 (Easy): What does LIFO mean and name two real-world examples?**

LIFO = Last-In, First-Out. The last element pushed is the first one popped.

Examples:
1. **Function call stack** — the most recently called function is the first to return.
2. **Browser back button** — each page visited is pushed; back pops to the previous.
3. **Undo/redo** — each action is pushed onto an undo stack; undo pops the last action.

---

**Q2 (Easy): When is a linked-list implementation of a stack better than array-backed?**

When you need guaranteed O(1) push with no worst-case spikes. Array-backed stacks occasionally trigger O(n) resizes. Linked-list stacks never resize — push always allocates a new node (O(1)). The trade-off: linked-list nodes have allocation overhead and poor cache locality, while array stacks are cache-friendly but have occasional resize latency. For most applications, array-backed wins (amortized O(1) with better constants).

---

**Q3 (Medium): How do you convert a recursive DFS to iterative using a stack?**

Replace the call stack with an explicit stack. Instead of making a recursive call, push the "work to do" onto the stack and loop.

```python
# Recursive DFS
def dfs_recursive(node):
    if not node: return
    process(node)
    dfs_recursive(node.left)
    dfs_recursive(node.right)

# Iterative equivalent
def dfs_iterative(root):
    if not root: return
    stack = [root]
    while stack:
        node = stack.pop()
        process(node)
        if node.right: stack.append(node.right)  # right first (LIFO reversal)
        if node.left:  stack.append(node.left)
```

Key insight: push right before left so left is processed first (LIFO reverses order).

---

**Q4 (Medium): What is a monotonic stack? When do you use it?**

A monotonic stack maintains elements in increasing or decreasing order. When a new element violates the order, pop elements until the property is restored. Use for:
- **Next Greater Element** — pop when current > top; O(n) amortized
- **Largest Rectangle in Histogram** — pop when current < top
- **Daily Temperatures** — pop when today's temp > top's temp
- **Trapping Rain Water** — can use monotonic stack or two-pointer

Each element is pushed and popped at most once, giving O(n) total time despite the nested loop appearance.

---

**Q5 (Medium): Explain stack overflow. How do programming languages guard against it?**

The call stack has a fixed size (typically 1–8 MB). Each function call pushes a frame (local variables, return address). Infinite recursion or very deep call chains exhaust this space — stack overflow.

Guards:
- **Stack size limits** — OS sets a hard limit per thread
- **Recursion depth limits** — Python default is 1000 (`sys.setrecursionlimit`)
- **Tail-call optimization** — some languages (Haskell, Kotlin) reuse the current frame for tail calls, avoiding stack growth
- **Iterative conversion** — manually use an explicit heap-allocated stack instead

---

**Q6 (Hard): Design a browser history system (LeetCode #1472) using stacks.**

```python
class BrowserHistory:
    def __init__(self, homepage: str):
        self.back_stack = [homepage]  # pages visited
        self.forward_stack = []       # pages after current

    def visit(self, url: str) -> None:
        self.back_stack.append(url)
        self.forward_stack.clear()    # visiting clears forward history

    def back(self, steps: int) -> str:
        while steps > 1 and len(self.back_stack) > 1:
            self.forward_stack.append(self.back_stack.pop())
            steps -= 1
        return self.back_stack[-1]

    def forward(self, steps: int) -> str:
        while steps > 0 and self.forward_stack:
            self.back_stack.append(self.forward_stack.pop())
            steps -= 1
        return self.back_stack[-1]

# All operations O(steps), space O(n) pages total
```

---

**Q7 (Hard): Largest Rectangle in Histogram (LeetCode #84) — explain the stack approach.**

```python
def largest_rectangle(heights: list[int]) -> int:
    # Monotonic increasing stack stores bar indices.
    # When a shorter bar is found, pop taller bars and compute their max width.
    stack = []
    max_area = 0
    heights = heights + [0]   # sentinel forces flush at end

    for i, h in enumerate(heights):
        start = i
        while stack and stack[-1][1] > h:
            idx, height = stack.pop()
            max_area = max(max_area, height * (i - idx))
            start = idx    # extend left to where the popped bar started
        stack.append((start, h))

    return max_area

# Intuition: a bar's max rectangle extends left as far as bars are >= its height.
# When we see a shorter bar, we know the taller bars can't extend further right.
# Time: O(n) — each bar pushed and popped once. Space: O(n).
```

---

## Interview Tips

- **Monotonic stack is the highest-value pattern** — it unlocks O(n) solutions to problems that look O(n²). Practice next-greater, histogram, and rain-water.
- **Always name the invariant** — for monotonic stacks, state "I maintain a [increasing/decreasing] stack" to show you understand the pattern, not just the code.
- **Stack vs recursion trade-off** — when asked to avoid recursion, explicit stack + loop is the standard answer; clarify that it trades call-stack space for heap space.
- **Division direction** — in RPN and expression evaluators, second `pop` is the left operand, first `pop` is the right operand. Draw it.
- **Min/Max stack** is a common variant follow-up — always offer it after implementing a plain stack.
- **For parenthesis problems** — the key insight is "push open brackets, match close brackets against top." This generalizes to tag matching, HTML validation, and arithmetic expressions.
