---
Level: L4-L5
Time: ~20 min
---

# Greedy Algorithms

## Quick Summary

A greedy algorithm makes the locally optimal choice at each step hoping to reach a global optimum. It works when the **greedy choice property** holds — a local best never needs to be reversed. When subproblems overlap or an early choice blocks a better combo later, use DP instead.

---

## When Greedy Works vs. When DP Is Needed

**The core question:** "Does a locally optimal choice always lead to a globally optimal solution?"

If yes → greedy. If no → DP or backtracking.

**Proving greedy is correct:** Use the **exchange argument** — assume an optimal solution differs from the greedy one, then show you can swap one choice without making it worse, contradicting the assumption.

---

## Comparative Table

| Problem type | Greedy? | Why |
|-------------|---------|-----|
| Activity selection | Yes | Earliest finish maximizes remaining time for more activities |
| Fractional knapsack | Yes | Take highest value/weight ratio first |
| 0/1 Knapsack | No | Taking best item now may block a better combination |
| Coin change (canonical denominations) | No | US coins work, but arbitrary denominations don't |
| Huffman coding | Yes | Greedy tree-building gives optimal prefix codes |
| Interval scheduling / removal | Yes | Sort by end time, take earliest non-overlapping |
| Shortest path (non-negative weights) | Yes (Dijkstra) | Greedy relaxation with priority queue |
| Minimum spanning tree | Yes (Kruskal/Prim) | Safe edge choice never needs reversal |
| Sequence alignment / edit distance | No | DP required — overlapping subproblems |

---

## Algorithms

### 1. Activity Selection (Interval Scheduling)

**Approach:** Sort activities by finish time. Always pick the activity that ends earliest among those compatible with the last selected.

**Why it works:** Choosing the earliest-finishing compatible activity leaves maximum remaining time for future activities. Any other choice produces a solution no better.

**Time:** O(n log n) | **Space:** O(n)

```python
def activity_selection(activities: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """
    activities: list of (start, finish) tuples
    Returns maximum non-overlapping subset.
    """
    # Sort by finish time
    sorted_acts = sorted(activities, key=lambda x: x[1])
    selected = [sorted_acts[0]]
    last_finish = sorted_acts[0][1]

    for start, finish in sorted_acts[1:]:
        if start >= last_finish:      # compatible with last selected
            selected.append((start, finish))
            last_finish = finish

    return selected


# Example
activities = [(1,4), (3,5), (0,6), (5,7), (3,9), (5,9), (6,10), (8,11), (8,12), (2,14), (12,16)]
result = activity_selection(activities)
print(result)  # [(1,4), (5,7), (8,11), (12,16)] — 4 activities
```

---

### 2. Huffman Encoding (Greedy Tree Building)

**Approach:** Use a min-heap. Always merge the two nodes with the lowest frequency. Assign 0/1 to left/right branches.

**Why it works:** Least frequent symbols get the longest codes. The greedy merge of two smallest frequencies minimizes total weighted path length — provable by exchange argument.

**Time:** O(n log n) | **Space:** O(n)

```python
import heapq
from collections import Counter

def huffman_codes(text: str) -> dict[str, str]:
    freq = Counter(text)
    # heap entries: (frequency, unique_id, char_or_node)
    heap = [[f, i, ch] for i, (ch, f) in enumerate(freq.items())]
    heapq.heapify(heap)
    counter = len(heap)

    while len(heap) > 1:
        lo = heapq.heappop(heap)
        hi = heapq.heappop(heap)
        # Merge: internal node with combined frequency
        merged = [lo[0] + hi[0], counter, [lo, hi]]
        counter += 1
        heapq.heappush(heap, merged)

    # Walk the tree to assign codes
    codes: dict[str, str] = {}

    def walk(node, prefix=""):
        if isinstance(node[2], str):     # leaf
            codes[node[2]] = prefix or "0"
        else:
            walk(node[2][0], prefix + "0")
            walk(node[2][1], prefix + "1")

    if heap:
        walk(heap[0])
    return codes


# Example
text = "aabbcccdddd"
codes = huffman_codes(text)
print(codes)
# e.g. {'d': '0', 'c': '10', 'a': '110', 'b': '111'}
```

---

## Worked Problems

### Problem 1: Jump Game — LC #55

**Section 1 — Understand the problem.**
Given array `nums` where `nums[i]` is the maximum jump length from index `i`, return `True` if you can reach the last index starting from index 0.

**Section 2 — Examples.**
```
[2,3,1,1,4] → True
[3,2,1,0,4] → False  (always land on index 3 which has jump 0)
```

**Section 3 — Constraints & edge cases.**
- 1 ≤ len(nums) ≤ 10^4
- 0 ≤ nums[i] ≤ 10^5
- Single element → True

**Section 4 — Approach.**
Track `max_reach` — the furthest index reachable so far. At each index `i`, if `i > max_reach`, you're stuck. Otherwise, update `max_reach = max(max_reach, i + nums[i])`.

**Section 5 — Code.**
```python
def canJump(nums: list[int]) -> bool:
    max_reach = 0
    for i, jump in enumerate(nums):
        if i > max_reach:
            return False          # can't reach this index
        max_reach = max(max_reach, i + jump)
    return True
```

**Section 6 — Complexity.**
Time O(n), Space O(1).

---

### Problem 2: Non-overlapping Intervals — LC #435

**Section 1 — Understand the problem.**
Given a list of intervals, return the minimum number of intervals to remove so the rest are non-overlapping.

**Section 2 — Examples.**
```
[[1,2],[2,3],[3,4],[1,3]] → 1  (remove [1,3])
[[1,2],[1,2],[1,2]]       → 2  (keep one)
[[1,2],[2,3]]             → 0  (already non-overlapping)
```

**Section 3 — Constraints & edge cases.**
- 1 ≤ n ≤ 10^5
- Touching intervals (end == start) are not overlapping

**Section 4 — Approach.**
Sort by end time. Greedily keep intervals with the earliest finish. When an overlap is found, remove the one with the later finish (i.e., the current one — the kept one is already optimal by the greedy argument). Count removals.

**Section 5 — Code.**
```python
def eraseOverlapIntervals(intervals: list[list[int]]) -> int:
    if not intervals:
        return 0
    intervals.sort(key=lambda x: x[1])   # sort by end time
    removals = 0
    last_end = intervals[0][1]

    for start, end in intervals[1:]:
        if start < last_end:              # overlap detected
            removals += 1
            # keep the one with smaller end (already `last_end`), discard current
        else:
            last_end = end                # no overlap; advance

    return removals
```

**Section 6 — Complexity.**
Time O(n log n), Space O(1) (ignoring sort).

---

### Problem 3: Gas Station — LC #134

**Section 1 — Understand the problem.**
`n` gas stations in a circle. `gas[i]` is fuel available, `cost[i]` is fuel to travel to station `i+1`. Return the starting index if you can complete the circuit, else -1. Guaranteed unique answer if solution exists.

**Section 2 — Examples.**
```
gas  = [1,2,3,4,5], cost = [3,4,5,1,2] → 3
gas  = [2,3,4],     cost = [3,4,3]      → -1
```

**Section 3 — Constraints & edge cases.**
- 1 ≤ n ≤ 10^5
- If total gas < total cost → -1

**Section 4 — Approach.**
Two key greedy observations:
1. If total gas < total cost, no solution exists.
2. If starting at `start` causes the tank to go negative at index `i`, then no station between `start` and `i` can be the answer (they'd face the same or worse deficit). Reset `start = i + 1`.

**Section 5 — Code.**
```python
def canCompleteCircuit(gas: list[int], cost: list[int]) -> int:
    total_surplus = 0
    current_surplus = 0
    start = 0

    for i in range(len(gas)):
        diff = gas[i] - cost[i]
        total_surplus += diff
        current_surplus += diff
        if current_surplus < 0:    # can't reach i+1 from `start`
            start = i + 1          # greedy: skip all stations up to i
            current_surplus = 0

    return start if total_surplus >= 0 else -1
```

**Section 6 — Complexity.**
Time O(n), Space O(1).

---

## Common Mistakes

1. **Trusting intuition over proof:** "This feels greedy" is not enough. The coin change problem feels greedy but fails for denominations like `[1, 3, 4]` with target `6` (greedy gives `4+1+1=3 coins`, DP gives `3+3=2 coins`). Always verify with a counter-example or exchange argument.

2. **Wrong sort key for intervals:** Sort by *end* time, not start time, for scheduling and removal problems. Sorting by start produces the wrong greedy order.

3. **Confusing "minimum removals" with "maximum kept":** `min_removals = n - max_non_overlapping`. Both formulations are equivalent; just make sure you're minimizing the right thing.

4. **Not checking global feasibility first:** In Gas Station, always check `sum(gas) >= sum(cost)` equivalently via `total_surplus >= 0`. The greedy reset only finds the best candidate — the total check confirms a solution exists.

5. **Using greedy when subproblem structure matters:** The 0/1 knapsack has overlapping subproblems (taking item i affects what's optimal for the remaining capacity). Greedy ignores this dependency. When items are indivisible, always reach for DP.
