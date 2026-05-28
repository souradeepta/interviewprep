# Linked Lists — Dynamic Nodes, O(1) Insert at Known Position

**Level:** L3-L4
**Time to read:** ~20 min

Nodes scattered in heap memory, connected by pointers. Trade random access for O(1) insert/delete at any known position.

---

## Quick Summary

A linked list stores elements in nodes, each holding a value and a pointer to the next node. Use when you need frequent insertions/deletions at known positions and don't need random access. Key property: pointer-following gives flexibility, but eliminates the index-based O(1) access that arrays provide.

---

## Operations & Complexity Table

| Operation          | Time (avg) | Time (worst) | Space  | Notes                                      |
|--------------------|-----------|-------------|--------|--------------------------------------------|
| Access by index    | O(n)      | O(n)        | O(1)   | Must traverse from head                    |
| Search             | O(n)      | O(n)        | O(1)   | Linear scan, no binary search possible     |
| Insert at head     | O(1)      | O(1)        | O(1)   | Adjust head pointer                        |
| Insert at tail     | O(1)*     | O(1)*       | O(1)   | *O(1) only if tail pointer maintained      |
| Insert at position | O(1)**    | O(1)**      | O(1)   | **Only if you hold the predecessor node    |
| Delete at head     | O(1)      | O(1)        | O(1)   | Advance head pointer                       |
| Delete at position | O(1)**    | O(1)**      | O(1)   | **Only if you hold the predecessor node    |
| Delete by value    | O(n)      | O(n)        | O(1)   | Must search first                          |

---

## Memory Layout / Internal Structure

```
Singly Linked List
─────────────────────────────────────────────────────────
head
 │
 ▼
┌──────┬──────┐     ┌──────┬──────┐     ┌──────┬──────┐
│  10  │  ──────►   │  20  │  ──────►   │  30  │ None │
└──────┴──────┘     └──────┴──────┘     └──────┴──────┘
[data | next]       [data | next]       [data | next]

Node overhead: 1 extra pointer per node (8 bytes on 64-bit)
Memory: NOT contiguous — nodes allocated anywhere on heap

Doubly Linked List
─────────────────────────────────────────────────────────
head                                                 tail
 │                                                    │
 ▼                                                    ▼
┌──────┬──────┬──────┐     ┌──────┬──────┬──────┐     ┌──────┬──────┬──────┐
│None  │  10  │  ──────►   │ ◄──  │  20  │  ──────►   │ ◄──  │  30  │ None │
└──────┴──────┴──────┘     └──────┴──────┴──────┘     └──────┴──────┴──────┘
[prev | data | next]       [prev | data | next]       [prev | data | next]

Node overhead: 2 pointers per node (16 bytes on 64-bit)
Enables O(1) backward traversal and O(1) delete given the node itself

Circular Linked List
─────────────────────────────────────────────────────────
head ─► [10] ─► [20] ─► [30] ─┐
         ▲                     │
         └─────────────────────┘
Used for: round-robin schedulers, Josephus problem
```

---

## Trade-offs vs Alternatives

| Feature               | Linked List   | Array          | Deque (collections.deque) |
|-----------------------|---------------|----------------|--------------------------|
| Random access         | O(n)          | O(1)           | O(n)                     |
| Insert at head        | O(1)          | O(n)           | O(1)                     |
| Insert at tail        | O(1)*         | O(1) amort.    | O(1)                     |
| Insert at position    | O(1)**        | O(n)           | O(n)                     |
| Delete at head        | O(1)          | O(n)           | O(1)                     |
| Memory per element    | High (pointer)| Low            | Moderate (blocks)        |
| Cache locality        | Poor          | Excellent      | Good (blocked)           |
| Reverse iteration     | O(n) singly   | O(n)           | O(n)                     |

*Only if tail pointer maintained; **Only if predecessor reference held

```
Singly vs Doubly decision:
┌───────────────────────────────────────────────────────┐
│ Only forward traversal needed?    → Singly            │
│ Need backward traversal?          → Doubly            │
│ Delete given node (not prev)?     → Doubly            │
│ Memory-constrained?               → Singly            │
│ Implementing LRU Cache?           → Doubly + HashMap  │
└───────────────────────────────────────────────────────┘
```

---

## When NOT to Use

- **Need random access** — O(n) index lookup is a dealbreaker; use an array.
- **Cache performance is critical** — pointer chasing causes cache misses on every node; arrays are 10-100× faster for sequential scans.
- **Memory-constrained environment** — each node carries 8–16 bytes of pointer overhead; array stores elements with zero overhead.
- **Binary search required** — no index = no binary search; sort + binary search only works on arrays.
- **Small collections (< 100 elements)** — array's constant-factor advantage dominates; the indirection overhead of linked lists hurts.

---

## Core Operations (Code)

```python
# ── Node definition ───────────────────────────────────────────────────────
class ListNode:
    def __init__(self, val=0, nxt=None):
        self.val = val
        self.next = nxt

# ── Build from list (helper) ──────────────────────────────────────────────
def build(values: list) -> ListNode | None:
    dummy = ListNode()
    cur = dummy
    for v in values:
        cur.next = ListNode(v)
        cur = cur.next
    return dummy.next

# ── Traverse / print ──────────────────────────────────────────────────────
def to_list(head: ListNode | None) -> list:
    result = []
    while head:
        result.append(head.val)
        head = head.next
    return result

# ── Insert after a node — O(1) ───────────────────────────────────────────
def insert_after(node: ListNode, val: int) -> None:
    node.next = ListNode(val, node.next)

# ── Delete next node — O(1) ──────────────────────────────────────────────
def delete_after(node: ListNode) -> None:
    if node.next:
        node.next = node.next.next

# ── Dummy-head pattern (simplifies edge cases) ───────────────────────────
def remove_value(head: ListNode | None, val: int) -> ListNode | None:
    dummy = ListNode(0, head)      # dummy before head
    cur = dummy
    while cur.next:
        if cur.next.val == val:
            cur.next = cur.next.next   # skip the node
        else:
            cur = cur.next
    return dummy.next              # new head (may have changed)

# ── Fast/slow pointer (Floyd's cycle detection) ───────────────────────────
def has_cycle(head: ListNode | None) -> bool:
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:
            return True
    return False
```

---

## 3 Worked Problems

---

### Problem 1 — Reverse Linked List (LeetCode #206)

**Clarifying Questions**
- Singly or doubly linked? (Singly per problem definition)
- In-place reversal or can I allocate a new list? (In-place expected)
- What to return for empty list? (Return None)

**Brute Force**
```python
def reverse_list_extra_space(head):
    # Collect values, rebuild — O(n) time, O(n) space
    values = to_list(head)
    return build(values[::-1])
```

**Optimization (Iterative — O(1) space)**

Rewire `next` pointers as you traverse. Keep three pointers: prev, curr, and the saved next.

```python
def reverse_list(head: ListNode | None) -> ListNode | None:
    prev = None
    curr = head
    while curr:
        nxt = curr.next      # save next before overwriting
        curr.next = prev     # reverse the pointer
        prev = curr          # advance prev
        curr = nxt           # advance curr
    return prev              # prev is now the new head

# Recursive version (O(n) call stack space)
def reverse_list_recursive(head: ListNode | None) -> ListNode | None:
    if not head or not head.next:
        return head
    new_head = reverse_list_recursive(head.next)
    head.next.next = head    # node after head points back
    head.next = None         # head is now the tail
    return new_head
```

**Edge Cases**
- Empty list: `while curr` never executes, returns None.
- Single node: loop runs once, `prev = node`, `curr = None`, returns node.
- Two nodes: verify pointer swap visually.

**Complexity**
- Time: O(n) — single pass
- Space: O(1) iterative / O(n) recursive (call stack)

**Follow-ups**
- "Reverse in groups of k?" → LeetCode #25 — reverse k nodes at a time.
- "Reverse between positions l and r?" → LeetCode #92 — partial reversal with dummy node.

---

### Problem 2 — Merge Two Sorted Lists (LeetCode #21)

**Clarifying Questions**
- Are both lists sorted ascending? (Yes)
- Can lists be empty? (Yes — return the other)
- Should I modify the original lists or create a new one? (Reuse nodes — in-place)

**Brute Force**
```python
def merge_brute(l1, l2):
    # Collect all, sort, rebuild — O((m+n) log(m+n)) time, O(m+n) space
    values = to_list(l1) + to_list(l2)
    values.sort()
    return build(values)
```

**Optimization (Dummy-head iterative)**

Compare heads, attach the smaller, advance that pointer. The dummy node eliminates the null-check for the initial head.

```python
def merge_two_lists(l1: ListNode | None, l2: ListNode | None) -> ListNode | None:
    dummy = ListNode(0)     # sentinel avoids special-casing head
    cur = dummy
    while l1 and l2:
        if l1.val <= l2.val:
            cur.next = l1
            l1 = l1.next
        else:
            cur.next = l2
            l2 = l2.next
        cur = cur.next
    cur.next = l1 or l2     # attach remaining list
    return dummy.next

# Recursive version
def merge_two_lists_rec(l1, l2):
    if not l1: return l2
    if not l2: return l1
    if l1.val <= l2.val:
        l1.next = merge_two_lists_rec(l1.next, l2)
        return l1
    else:
        l2.next = merge_two_lists_rec(l1, l2.next)
        return l2
```

**Edge Cases**
- One or both empty: `l1 or l2` handles remaining attachment.
- All elements of one list are smaller: works naturally.
- Duplicate values: `<=` ensures stable merge.

**Complexity**
- Time: O(m + n) — touch each node once
- Space: O(1) iterative / O(m + n) recursive call stack

**Follow-ups**
- "Merge k sorted lists?" → Min-heap of (value, list_index, node), O(n log k) (LeetCode #23).
- "Merge in reverse?" → Reverse both, merge, reverse result.

---

### Problem 3 — Linked List Cycle (LeetCode #141)

**Clarifying Questions**
- Just detect cycle, or also find the start node? (Detect only; LeetCode #142 finds start)
- Can the list be empty? (Yes — no cycle)

**Brute Force**
```python
def has_cycle_set(head):
    # Store visited nodes in a set — O(n) time, O(n) space
    seen = set()
    while head:
        if id(head) in seen:
            return True
        seen.add(id(head))
        head = head.next
    return False
```

**Optimization (Floyd's Tortoise and Hare)**

Slow pointer advances 1 step, fast pointer advances 2 steps. If a cycle exists, they must meet inside it. If no cycle, fast reaches None.

```python
def has_cycle(head: ListNode | None) -> bool:
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:        # identity check, not equality
            return True
    return False

# Bonus: find cycle start (LeetCode #142)
def detect_cycle_start(head: ListNode | None) -> ListNode | None:
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:
            # Reset slow to head; both advance 1 step
            slow = head
            while slow is not fast:
                slow = slow.next
                fast = fast.next
            return slow         # cycle entry point
    return None
```

**Why does resetting slow to head find the cycle start?**
```
Let: distance head→cycle_start = F
     distance cycle_start→meeting_point = a
     cycle length = C

When they meet: slow traveled F+a, fast traveled F+a+n*C (lapped n times)
Fast = 2 * slow:  F + a + n*C = 2(F + a)
                  n*C = F + a
                  F = n*C - a

So from meeting point, F more steps = (n*C - a) = n full cycles - a
Starting from head, F steps = cycle_start.
Both arrive at cycle_start simultaneously.
```

**Complexity**
- Time: O(n) — fast pointer covers at most 2n steps
- Space: O(1)

**Follow-ups**
- "Find cycle length?" → After detecting cycle, keep fast still, advance slow until it returns; count steps.
- "Remove cycle?" → Find start, traverse back to find node whose next = start, set next = None.

---

## Interview Q&A

**Q1 (Easy): What is the difference between a singly and doubly linked list?**

A singly linked list has one pointer per node (`next`), enabling forward traversal only. A doubly linked list has two pointers per node (`prev` + `next`), enabling O(1) delete of a node given only its reference (no predecessor search needed) and O(1) backward traversal. Cost: 8 extra bytes per node. Use doubly for LRU cache, browser history (forward/back), and text editors.

---

**Q2 (Easy): Why is random access O(n) for linked lists?**

There is no index-to-address formula. To reach node i, you must follow `next` pointers from head, traversing i nodes. Memory is non-contiguous, so the CPU cannot compute an address offset — it must dereference each pointer, which is likely a cache miss for each hop.

---

**Q3 (Medium): When would you use a dummy head node?**

A dummy (sentinel) node before the actual head simplifies code that modifies the head: you never need a special case for "node to delete is the head." Pattern:
```python
dummy = ListNode(0, head)
cur = dummy
# ... modify cur.next freely ...
return dummy.next  # actual head (may have changed)
```
Used in: remove nth from end, merge sorted lists, partition list, delete node by value.

---

**Q4 (Medium): What is the memory overhead of a linked list vs array?**

Array: 0 overhead (elements stored directly).
Singly linked list: 8 bytes per node (one 64-bit pointer).
Doubly linked list: 16 bytes per node (two pointers).

For 1M integers (4 bytes each):
- Array: 4 MB
- Singly list: 12 MB (3× overhead)
- Doubly list: 20 MB (5× overhead)

Plus Python object overhead (~28 bytes per `int` object, ~56 bytes per custom node object) makes the real overhead much larger in interpreted languages.

---

**Q5 (Medium): Explain the fast/slow pointer technique and name two applications.**

Two pointers traverse the list at different speeds (usually 1× and 2×). If a cycle exists, the fast pointer "laps" the slow pointer and they meet. If no cycle, fast reaches None.

Applications:
1. **Cycle detection** (LeetCode #141, #142)
2. **Find middle of list** — when fast reaches end, slow is at middle (LeetCode #876)
3. **Find kth from end** — fast advances k steps ahead, then both advance together

---

**Q6 (Hard): How would you implement an LRU cache using a linked list?**

```python
from collections import OrderedDict

class LRUCache:
    # Simple version using OrderedDict (doubly linked list + hash map)
    def __init__(self, capacity: int):
        self.cap = capacity
        self.cache = OrderedDict()   # maintains insertion order

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        self.cache.move_to_end(key)  # mark as recently used
        return self.cache[key]

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.cap:
            self.cache.popitem(last=False)  # evict least recently used
```

For a from-scratch implementation: doubly linked list (O(1) node removal/insertion) + hash map (O(1) lookup). The hash map stores key → node reference; the list maintains recency order. All operations O(1).

---

**Q7 (Hard): Reverse a linked list in groups of k.**

```python
def reverse_k_group(head: ListNode | None, k: int) -> ListNode | None:
    # Check if k nodes remain
    count, node = 0, head
    while node and count < k:
        node = node.next
        count += 1
    if count < k:
        return head    # fewer than k nodes, leave as-is

    # Reverse k nodes
    prev, curr = None, head
    for _ in range(k):
        nxt = curr.next
        curr.next = prev
        prev = curr
        curr = nxt

    # head is now the tail of reversed group
    head.next = reverse_k_group(curr, k)
    return prev   # prev is new head of reversed group

# Time: O(n), Space: O(n/k) recursive call stack
```

---

**Q8 (Hard): Find the intersection point of two linked lists (LeetCode #160).**

```python
def get_intersection(headA, headB):
    # Two pointers: when one reaches end, redirect to other list's head.
    # They meet at intersection after traveling same total distance.
    a, b = headA, headB
    while a is not b:
        a = a.next if a else headB
        b = b.next if b else headA
    return a   # None if no intersection

# Why this works:
# Distance: a travels lenA + lenB, b travels lenB + lenA
# If intersection exists, they meet at it (same total distance).
# If no intersection, both reach None simultaneously.
```

---

## Interview Tips

- **Always use a dummy head** for problems that might modify the head node. It removes a whole class of edge-case bugs.
- **Draw the pointer diagram** before coding any reversal or merge problem. Pointer bugs are invisible without visualization.
- **Fast/slow pointer** is the go-to for cycle, middle, and kth-from-end — know all three derivations.
- **Singly vs doubly** is almost always the first follow-up; know the exact trade-off (delete-given-node is O(1) only with doubly).
- **State the space complexity of your recursive solution** — interviewers expect you to note O(n) call stack and offer the iterative O(1) alternative.
- **LRU cache** is the canonical doubly-linked-list system design question — implement it from scratch at L4+.
