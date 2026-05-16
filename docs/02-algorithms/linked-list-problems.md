# Linked List Problems

## Fast/Slow Pointers (Floyd's Algorithm)
**When to use:** Finding middle, detecting cycles, finding kth element

**Best DS:** Singly Linked List, Doubly Linked List

**Key Algorithms:** Tortoise and hare, finding middle, kth node from end

**Example Problems:**
1. "Find middle of linked list" → Slow moves 1 step, fast moves 2. Your repo: `python/basic/linked_list.py`. Time: O(n)
2. "Linked list cycle" → If they meet, cycle exists. Time: O(n)

---

## Cycle Detection & Starting Node
**When to use:** Finding cycle in linked list, identifying corruption

**Best DS:** Singly Linked List, Hash set

**Key Algorithms:** Floyd's algorithm, reset one pointer to find start

**Example Problems:**
1. "Linked list cycle II (find start)" → Detect cycle, reset one pointer to head, move both 1 step. Your repo: `python/basic/linked_list.py`. Time: O(n)

---

## List Merging
**When to use:** Combining sorted lists, merge sort, multi-way merge

**Best DS:** Singly Linked List, Priority Queue

**Key Algorithms:** Two-pointer merge, heap-based merge for k lists

**Example Problems:**
1. "Merge two sorted lists" → Compare heads, append smaller, advance pointer. Time: O(n + m)
2. "Merge k sorted lists" → Min-heap of list heads. Your repo: `python/advanced/heap.py`. Time: O(n log k)

---

## List Reversal
**When to use:** Reversing directions, palindrome checking, reverse operations

**Best DS:** Singly Linked List

**Key Algorithms:** Iterative reversal with three pointers, recursive reversal

**Example Problems:**
1. "Reverse linked list" → Three pointers (prev, curr, next). Your repo: `python/basic/linked_list.py`. Time: O(n)
2. "Reverse nodes in k-group" → Reverse groups of k. Time: O(n)

---

## Reordering
**When to use:** Rearranging elements, interleaving, palindrome construction

**Best DS:** Singly Linked List, Stack

**Key Algorithms:** Find middle, reverse second half, merge halves

**Example Problems:**
1. "Reorder list (L0 → Ln → L1 → Ln-1 → ...)" → Find middle, reverse second half, merge. Time: O(n)
2. "Palindrome linked list" → Find middle, reverse second half, check equality. Time: O(n)

---

See [Master Index](problem-to-pattern-matcher.md) for all 50+ patterns.
