# Greedy Problems

## Activity Selection / Interval Scheduling
**When to use:** Non-overlapping maximum selection, task scheduling

**Best DS:** Array (intervals with start/end), sorted by end time

**Key Algorithms:** Sort by end time, greedily select earliest-ending activity

**Example Problems:**
1. "Max meetings in one room" → Sort by end time, greedily select non-overlapping. Time: O(n log n)

---

## Huffman Coding
**When to use:** Data compression, optimal prefix-free codes

**Best DS:** Min-heap, Binary tree

**Key Algorithms:** Build min-heap of frequencies, pop two min nodes, create parent

**Example Problems:**
1. "Huffman tree construction" → Min-heap, build tree bottom-up. Your repo: `python/advanced/heap.py`. Time: O(n log n)

---

## Interval Merging
**When to use:** Merging overlapping ranges, meeting room scheduling

**Best DS:** Array of intervals, sorted by start time

**Key Algorithms:** Sort intervals, merge if overlapping (current.start <= prev.end)

**Example Problems:**
1. "Merge intervals" → Sort by start, merge overlapping. Time: O(n log n)

---

See [Master Index](problem-to-pattern-matcher.md) for all 50+ patterns.
