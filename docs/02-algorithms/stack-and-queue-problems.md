# Stack & Queue Problems

## Monotonic Stack
**When to use:** Finding next/previous greater/smaller element, largest rectangle, trapping rain water

**Best DS:** Stack, Deque

**Key Algorithms:** Maintain decreasing stack, pop and compute when monotonicity breaks

**Example Problems:**
1. "Next greater element" → Stack stores indices; pop while top < current. Your repo: `python/basic/stack.py`. Time: O(n)
2. "Largest rectangle in histogram" → Monotonic stack of heights; compute area with popped bar. Time: O(n)

---

## Parentheses Matching
**When to use:** Expression validation, nested structure checking, code parsing

**Best DS:** Stack

**Key Algorithms:** Stack-based validation, counter-based validation

**Example Problems:**
1. "Valid parentheses" → Push open, pop and match on closing. Your repo: `python/basic/stack.py`. Time: O(n)
2. "Longest valid parentheses" → Stack stores indices; compute lengths on match. Time: O(n)

---

## BFS via Queue
**When to use:** Level-order traversal, shortest path in unweighted graph, word ladder problems

**Best DS:** Queue, Deque

**Key Algorithms:** Standard BFS, level-order with level tracking, shortest path discovery

**Example Problems:**
1. "Binary tree level order traversal" → Queue stores nodes; process level by level. Your repo: `python/advanced/bst.py`. Time: O(n)
2. "Word ladder" → BFS from start word; generate neighbors by changing one letter. Your repo: `python/basic/queue_ds.py`. Time: O(n × word_length)

---

## DFS via Stack
**When to use:** Post-order computations, expression evaluation, topological sort setup

**Best DS:** Stack, Recursion

**Key Algorithms:** Explicit stack simulation, post-order evaluation

**Example Problems:**
1. "Evaluate reverse Polish notation" → Stack stores numbers; on operator, pop two, compute, push result. Your repo: `python/basic/stack.py`. Time: O(n)

---

## Sliding Window Max / Deque
**When to use:** Maximum/minimum in sliding window, concurrent element tracking

**Best DS:** Deque, PriorityQueue

**Key Algorithms:** Deque maintains decreasing order, remove front when outside window

**Example Problems:**
1. "Sliding window maximum" → Deque stores indices in decreasing order. Your repo: `python/basic/deque_ds.py`. Time: O(n)

---

See [Master Index](problem-to-pattern-matcher.md) for all 50+ patterns.
