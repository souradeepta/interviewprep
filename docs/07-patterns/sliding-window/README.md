# Sliding Window Pattern

**Level:** L3-L5
**Time to read:** ~25 min
**Prerequisites:** [Arrays](../../06-data-structures/arrays/README.md)
**Related:** [Two-Pointer](../two-pointer/README.md)

## Quick Summary

Maintain a contiguous subarray or substring that slides across the input, adding one element at the right and optionally removing one at the left. Converts O(n²) brute-force scans into a single O(n) pass. Key signal: "subarray", "substring", "window of size k", "max/min in window", "at most/at least k distinct".

## When to Use It

Signal phrases that strongly indicate sliding window:

- "Maximum/minimum sum subarray of size k"
- "Longest substring without repeating characters"
- "Subarray / substring containing at most k distinct elements"
- "Find all anagrams / permutations of a pattern in a string"
- "Minimum window containing all characters of t"
- "Longest subarray with sum at most / at least k"
- "Window of size k — maximum element"

**Not a fit when:** you need non-contiguous subsequences (use DP), all pairs/combinations (use backtracking), or the condition cannot be expressed as an invariant on a contiguous range.

## How It Works

### Variant 1: Fixed-Size Window

Window size is fixed at `k`. Advance both ends together: add `nums[right]`, remove `nums[right - k]`.

```
nums = [2, 1, 5, 1, 3, 2],  k = 3

Step 0  (bootstrap): window = [2, 1, 5],  sum = 8
                               L     R

Step 1: add nums[3]=1, remove nums[0]=2  → window = [1, 5, 1],  sum = 7
                                  L     R

Step 2: add nums[4]=3, remove nums[1]=1  → window = [5, 1, 3],  sum = 9  ← max
                                     L     R

Step 3: add nums[5]=2, remove nums[2]=5  → window = [1, 3, 2],  sum = 6
                                          L     R

Answer: 9
```

Pattern:
```
1. sum first k elements (bootstrap)
2. for i in range(k, n):
       sum += nums[i] - nums[i - k]
       max_sum = max(max_sum, sum)
```

### Variant 2: Variable-Size Window

Window grows by advancing `right`. When a constraint is violated, shrink from `left` until the constraint holds again. The window always contains a valid configuration.

```
s = "abcabcbb"   (longest substring without repeating characters)

right=0: window="a",    set={a}        valid
right=1: window="ab",   set={a,b}      valid
right=2: window="abc",  set={a,b,c}    valid   ← len=3
right=3: add 'a' → duplicate!
         shrink: remove s[left]='a', left=1
         window="bca",  set={b,c,a}    valid   ← len=3
right=4: add 'b' → duplicate!
         shrink: remove s[left]='b', left=2
         window="cab",  set={c,a,b}    valid   ← len=3
right=5: add 'c' → duplicate!
         shrink: remove s[left]='c', left=3
         window="abc",  set={a,b,c}    valid   ← len=3
right=6: add 'b' → duplicate!
         shrink: remove 'a','b' → left=5
         window="cb",   set={c,b}      valid
right=7: add 'b' → duplicate!
         shrink: remove 'c','b' → left=7
         window="b",    set={b}        valid

Answer: 3
```

Pattern:
```
left = 0
for right in range(n):
    # 1. expand: add s[right] to window state
    # 2. shrink: while constraint violated:
    #        remove s[left] from window state
    #        left += 1
    # 3. update answer with current window
```

### Variant 3: Fixed-Size Window with Frequency Comparison

Used for anagram / permutation problems. Maintain two frequency counters and compare them.

```
s1="ab", s2="eidbaooo"   (check if s1 permutation exists in s2)

need  = {a:1, b:1}   (target frequencies)
window of size 2, slide across s2:

i=0: window=s2[0:2]="ei" → {e:1,i:1}  ≠ need
i=1: window=s2[1:3]="id" → {i:1,d:1}  ≠ need
i=2: window=s2[2:4]="db" → {d:1,b:1}  ≠ need
i=3: window=s2[3:5]="ba" → {b:1,a:1}  == need  ← found!

Answer: True
```

## Decision Tree

```
Does the problem involve a contiguous subarray or substring?
├── YES → Is the window size fixed (given k)?
│         ├── YES → Fixed-size window
│         │         ├── Track sum/product: add new, subtract dropped
│         │         └── Track frequencies: compare two Counters
│         └── NO  → Variable-size window
│                   ├── Maximize length: shrink when constraint violated
│                   └── Minimize length: shrink while constraint satisfied
└── NO  → Not a sliding window problem
          ├── Non-contiguous subsequence → Dynamic programming
          └── All pairs/combinations    → Backtracking or hash map
```

## Complexity

| Variant | Time | Space | Notes |
|---------|------|-------|-------|
| Fixed-size window | O(n) | O(1) or O(k) | O(1) for sum; O(k) if tracking frequencies |
| Variable-size window | O(n) | O(k) | Each element enters and exits the window at most once |
| Monotonic deque (window max) | O(n) | O(k) | Deque holds at most k indices |
| Frequency-compare (anagrams) | O(n) | O(1) | Alphabet size is constant (26 chars) |

Both left and right pointers move only forward — each element is processed at most twice (once added, once removed), giving O(n) regardless of shrink loops.

## Common Mistakes

- **Not shrinking correctly:** using `if` instead of `while` when shrinking — a single removal may not restore the invariant; keep shrinking until the window is valid again
- **Off-by-one on window size:** after the loop, the window is `right - left + 1`, not `right - left`
- **Using O(n) space when O(1) is possible:** tracking character counts with a Counter is O(alphabet), not O(n) — acceptable; but copying the full window into a list is wasteful
- **Forgetting to reset / update window state when shrinking:** decrement the character count, delete the key if count reaches 0, or update the `max_freq` variable
- **Fixed-window bootstrap mistake:** initializing the window sum/counter on the first `k` elements, then starting the loop at index `k` — a common off-by-one if the loop starts at 0 instead
- **Comparing Counter objects on every step:** O(26) = O(1) per step is fine; but recomputing `Counter(window_string)` from scratch each step is O(k) per step → O(nk) total

## Run the Code

```bash
# From repo root
pytest tests/patterns/test_sliding_window.py -v
```

**Implementation:** [`python/patterns/sliding_window.py`](../../../python/patterns/sliding_window.py)
**Tests:** [`tests/patterns/test_sliding_window.py`](../../../tests/patterns/test_sliding_window.py)

## Problems

9 problems with full think-process walk-throughs: [problems.md](problems.md)

| # | Problem | Difficulty | LeetCode | Variant |
|---|---------|-----------|---------|---------|
| 1 | Maximum Sum Subarray of Size K | Easy | custom | Fixed window — sum |
| 2 | Longest Substring Without Repeating Characters | Medium | #3 | Variable window — set/dict |
| 3 | Minimum Size Subarray Sum | Medium | #209 | Variable window — shrink when valid |
| 4 | Longest Repeating Character Replacement | Medium | #424 | Variable window — max freq char |
| 5 | Permutation in String | Medium | #567 | Fixed window — frequency compare |
| 6 | Find All Anagrams in a String | Medium | #438 | Fixed window — collect positions |
| 7 | Minimum Window Substring | Hard | #76 | Variable window — need/have counters |
| 8 | Sliding Window Maximum | Hard | #239 | Fixed window — monotonic deque |
| 9 | Longest Subarray with Sum At Most K | Medium | custom | Variable window — running sum |
