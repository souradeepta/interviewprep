# Sliding Window — Problems

## Easy

---

### Problem 1: Maximum Sum Subarray of Size K  [Easy]  [Custom]

**1. Clarifying questions to ask**
- Is `k` guaranteed to be ≤ `len(nums)`? Clarify — if not, return 0 or raise.
- Can nums contain negative numbers? Yes — the algorithm handles them correctly since we are looking for the maximum, not assuming positivity.
- Is the array guaranteed non-empty? Assume yes unless told otherwise.
- Return the sum, not the indices? Yes.

**2. Brute force**
For every starting index `i` in `[0, n-k]`, sum `nums[i..i+k-1]`. Time O(n·k), Space O(1).

**3. Optimization**
Fixed-size sliding window. Bootstrap the sum on the first window `nums[0..k-1]`. Then for each new position, add the incoming element and subtract the outgoing element. One pass, O(n).

```
nums = [2, 1, 5, 1, 3, 2],  k = 3

Bootstrap:  window_sum = 2 + 1 + 5 = 8,  max_sum = 8
            [2, 1, 5, 1, 3, 2]
             ^-----^

i=3: add nums[3]=1, remove nums[0]=2 → sum = 8 + 1 - 2 = 7
i=4: add nums[4]=3, remove nums[1]=1 → sum = 7 + 3 - 1 = 9  ← new max
i=5: add nums[5]=2, remove nums[2]=5 → sum = 9 + 2 - 5 = 6

Answer: 9
```

Key: `window_sum += nums[i] - nums[i - k]` — adding right element, dropping left element.

**4. Edge cases**
- `k == len(nums)`: single window, return sum of entire array
- All negative numbers: correctly returns the least-negative k-sum
- `k == 1`: every single element is a window; return max element
- `nums` contains zeros: no special handling needed

**5. Final code**
```python
def max_subarray_sum_k(nums: list[int], k: int) -> int:
    window_sum = sum(nums[:k])
    max_sum = window_sum
    for i in range(k, len(nums)):
        window_sum += nums[i] - nums[i - k]
        max_sum = max(max_sum, window_sum)
    return max_sum
```

**Complexity:** Time O(n), Space O(1)

**6. Follow-up questions**
- What if you need the starting index of the best window? Track `best_start = i - k` when a new max is found.
- What if you want the minimum sum window of size k? Change `max` to `min` and initialize `min_sum`.
- Variable window: what if you want the maximum sum subarray of any length? That is Kadane's algorithm (DP), not sliding window.

---

## Medium

---

### Problem 2: Longest Substring Without Repeating Characters  [Medium]  [LC #3]

**1. Clarifying questions to ask**
- What characters can appear? ASCII? Unicode? Assume all printable ASCII unless told otherwise.
- Return the length, not the substring itself? Yes (though storing the substring is a natural follow-up).
- Is an empty string valid input? Yes — return 0.
- Are spaces and punctuation considered characters? Yes, treat every character equally.

**2. Brute force**
Check every substring `s[i..j]`. For each, verify all characters are unique using a set. Time O(n³) (O(n²) substrings × O(n) uniqueness check), Space O(min(n, alphabet)).

**3. Optimization**
Variable-size sliding window with a dictionary mapping each character to its most recent index.

Key insight: when a duplicate character is found at `right`, `left` must jump past the previous occurrence of that character — we do not need to shrink one step at a time.

```
s = "abcabcbb"
     0123456 7

left=0, right=0: 'a' not seen → char_idx={'a':0}, len=1
left=0, right=1: 'b' not seen → char_idx={'a':0,'b':1}, len=2
left=0, right=2: 'c' not seen → char_idx={..,'c':2}, len=3
left=0, right=3: 'a' seen at 0, 0 >= left → left = 0+1 = 1
                 char_idx['a']=3, len=3
left=1, right=4: 'b' seen at 1, 1 >= left → left = 1+1 = 2
                 char_idx['b']=4, len=3
left=2, right=5: 'c' seen at 2, 2 >= left → left = 2+1 = 3
                 char_idx['c']=5, len=3
left=3, right=6: 'b' seen at 4, 4 >= left → left = 4+1 = 5
                 char_idx['b']=6, len=2
left=5, right=7: 'b' seen at 6, 6 >= left → left = 6+1 = 7
                 char_idx['b']=7, len=1

Answer: 3
```

The guard `char_idx[ch] >= left` is critical: a character may be in the dict from before the current window — only jump left if the previous occurrence is actually inside the window.

**4. Edge cases**
- Empty string `""`: loop doesn't execute, return 0
- All same characters `"bbbbb"`: left jumps to right on every step, max_len stays 1
- All unique `"abcdef"`: left never moves, max_len = n
- Single character: right=0, no duplicate, return 1

**5. Final code**
```python
def length_of_longest_substring(s: str) -> int:
    char_index: dict[str, int] = {}
    max_len = 0
    left = 0
    for right, ch in enumerate(s):
        if ch in char_index and char_index[ch] >= left:
            left = char_index[ch] + 1
        char_index[ch] = right
        max_len = max(max_len, right - left + 1)
    return max_len
```

**Complexity:** Time O(n), Space O(min(n, alphabet)) — at most one entry per unique character

**6. Follow-up questions**
- Return the actual substring, not just the length? Track `best_left` and `best_right` when `max_len` updates; return `s[best_left:best_right+1]`.
- What if at most k repeating characters are allowed? Generalize with a frequency counter and shrink when any character frequency exceeds k — LC #395 and LC #340 variants.
- Why is a dict faster than a set here? The dict stores the last seen index, enabling O(1) jump of `left` to skip past the duplicate. A set requires shrinking one step at a time — O(n) amortized either way, but the dict saves the inner while loop.

---

### Problem 3: Minimum Size Subarray Sum  [Medium]  [LC #209]

**1. Clarifying questions to ask**
- Are all numbers positive? Yes (per LC #209). This is essential — with negatives, the window cannot reliably shrink.
- Is the target always achievable? No — if no valid subarray exists, return 0.
- Do we want the length, not the subarray itself? Yes.
- Is `target` positive? Yes.

**2. Brute force**
Check every subarray `nums[i..j]`. Sum each and track the minimum length where sum ≥ target. Time O(n²), Space O(1).

**3. Optimization**
Variable-size sliding window. Expand right to grow the sum. Once `window_sum >= target`, record the window length and shrink from the left — the current window is a candidate; shrinking may find a shorter one.

```
nums = [2, 3, 1, 2, 4, 3],  target = 7

right=0: sum=2 < 7
right=1: sum=5 < 7
right=2: sum=6 < 7
right=3: sum=8 >= 7 → min_len = min(inf, 3-0+1=4) = 4
         shrink: remove nums[0]=2 → sum=6 < 7, left=1
right=4: sum=10 >= 7 → min_len = min(4, 4-1+1=4) = 4
         shrink: remove nums[1]=3 → sum=7 >= 7, left=2
         min_len = min(4, 4-2+1=3) = 3
         shrink: remove nums[2]=1 → sum=6 < 7, left=3
right=5: sum=9 >= 7 → min_len = min(3, 5-3+1=3) = 3
         shrink: remove nums[3]=2 → sum=7 >= 7, left=4
         min_len = min(3, 5-4+1=2) = 2
         shrink: remove nums[4]=4 → sum=3 < 7, left=5

Answer: 2  (subarray [4,3])
```

**4. Edge cases**
- No valid subarray (e.g., sum of all elements < target): return 0
- Single element equals target: return 1
- All elements equal target: return 1
- Entire array needed: return `len(nums)`

**5. Final code**
```python
def min_subarray_sum(target: int, nums: list[int]) -> int:
    left = 0
    window_sum = 0
    min_len = float("inf")
    for right in range(len(nums)):
        window_sum += nums[right]
        while window_sum >= target:
            min_len = min(min_len, right - left + 1)
            window_sum -= nums[left]
            left += 1
    return 0 if min_len == float("inf") else min_len
```

**Complexity:** Time O(n) — each element enters and exits the window once, Space O(1)

**6. Follow-up questions**
- What if numbers can be negative? Sliding window breaks (shrinking may increase the sum). Use prefix sums + binary search for O(n log n), or a deque-based approach.
- What if you want the maximum length subarray with sum ≤ target? Flip the condition — expand while valid, record length before shrinking.
- O(n log n) alternative? Build prefix sums, then for each `i` binary search for the smallest `j` such that `prefix[j] - prefix[i] >= target`. Valid when numbers are positive (prefix sum is monotone).

---

### Problem 4: Longest Repeating Character Replacement  [Medium]  [LC #424]

**1. Clarifying questions to ask**
- Is the string uppercase only? Yes per LC #424.
- What does "at most k replacements" mean? You can change at most k characters in the window to any letter to make all characters the same.
- Return the length of the longest such window? Yes.
- Can k be 0? Yes — then no replacements allowed; find longest run of a single character.

**2. Brute force**
Check all substrings. For each, count the most frequent character; if `length - max_freq <= k`, it is a valid window. Track max length. Time O(n²) or O(n²·26), Space O(26).

**3. Optimization**
Variable-size sliding window with a frequency map.

Key insight: a window `[left, right]` is valid if `(right - left + 1) - max_freq <= k` — i.e., the characters that are not the most frequent can all be replaced with ≤ k replacements. When the window becomes invalid, shrink by one from the left.

Important subtlety: `max_freq` is never decremented when shrinking — it may be stale (overestimated). This is safe because a stale `max_freq` means we will not accept a window smaller than one we have already seen, so the answer is correct.

```
s = "AABABBA",  k = 1

right=0: freq={A:1}, max_freq=1, size=1, size-max_freq=0<=1  valid
right=1: freq={A:2}, max_freq=2, size=2, 0<=1  valid
right=2: freq={A:2,B:1}, max_freq=2, size=3, 1<=1  valid
right=3: freq={A:3,B:1}, max_freq=3, size=4, 1<=1  valid
right=4: freq={A:3,B:2}, max_freq=3, size=5, 2>1   invalid!
         shrink: remove s[left=0]='A' → freq={A:2,B:2}, left=1
         max_freq stays 3 (stale but safe), size=4, 4-3=1<=1  valid
right=5: freq={A:2,B:3}, max_freq=3, size=5, 2>1   invalid!
         shrink: remove s[left=1]='A' → freq={A:1,B:3}, left=2
         max_freq=3, size=4, 4-3=1<=1  valid
right=6: freq={A:2,B:3}, max_freq=3, size=5, 2>1   invalid!
         shrink: remove s[left=2]='A' → freq={A:1,B:3}, left=3
         max_freq=3, size=4, 4-3=1<=1  valid

max window size seen: 4
Answer: 4
```

**4. Edge cases**
- `k >= len(s)`: entire string is valid, return `len(s)`
- `k == 0`: find longest run of a single repeated character
- All same characters: `max_freq == size` always, window grows to full length
- Single character: return 1

**5. Final code**
```python
from collections import defaultdict

def longest_repeating_char_replacement(s: str, k: int) -> int:
    freq: dict[str, int] = defaultdict(int)
    max_freq = left = max_len = 0
    for right, ch in enumerate(s):
        freq[ch] += 1
        max_freq = max(max_freq, freq[ch])
        window_size = right - left + 1
        if window_size - max_freq > k:
            freq[s[left]] -= 1
            left += 1
        max_len = max(max_len, right - left + 1)
    return max_len
```

**Complexity:** Time O(n), Space O(26) = O(1)

**6. Follow-up questions**
- Why is the stale `max_freq` safe? We only shrink by 1 when the window is invalid. A stale `max_freq` means `window_size - max_freq` appears to violate the constraint even if technically valid — but this only prevents the window from growing, never from shrinking. The maximum window size found is always achievable.
- What if the alphabet is lowercase? Change nothing — the algorithm is alphabet-agnostic.
- What if you want the actual replacement characters? Track which character is most frequent in the final window and identify the positions of all other characters.

---

### Problem 5: Permutation in String  [Medium]  [LC #567]

**1. Clarifying questions to ask**
- What counts as a permutation? Any rearrangement of all characters of `s1`.
- Both strings contain only lowercase English letters? Yes per LC.
- Return boolean — does any window in `s2` match? Yes.
- If `len(s1) > len(s2)`, return False immediately? Yes.

**2. Brute force**
Generate all permutations of `s1`, then search for each in `s2`. Time O(n! · m) — completely impractical.

Or: for every window of size `len(s1)` in `s2`, sort the window and compare to sorted `s1`. Time O(m · k log k), Space O(k).

**3. Optimization**
Fixed-size sliding window of size `k = len(s1)`. Maintain a frequency counter for the current window in `s2`. On each slide, add the incoming character and remove the outgoing character. Compare counters in O(26) = O(1).

```
s1="ab", s2="eidbaooo"
k=2, need={a:1, b:1}

Bootstrap window s2[0:2]="ei": {e:1,i:1}  ≠ need
Slide to i=2: add s2[2]='d', remove s2[0]='e' → {i:1,d:1}  ≠ need
Slide to i=3: add s2[3]='b', remove s2[1]='i' → {d:1,b:1}  ≠ need
Slide to i=4: add s2[4]='a', remove s2[2]='d' → {b:1,a:1}  == need  ← True!
```

When decrementing a character's count to 0, delete the key from the Counter so that equality comparison works correctly (a Counter with a 0-count key is not equal to one without it).

**4. Edge cases**
- `len(s1) > len(s2)`: return False immediately
- `s1` and `s2` are the same string: bootstrap window equals need → True
- All characters the same in `s1`: need a run of that character of length `len(s1)` in `s2`
- `s1` has duplicate characters: frequency comparison handles this correctly (e.g., `s1="aa"` requires two 'a's in the window)

**5. Final code**
```python
from collections import Counter

def permutation_in_string(s1: str, s2: str) -> bool:
    if len(s1) > len(s2):
        return False
    need = Counter(s1)
    window = Counter(s2[:len(s1)])
    if window == need:
        return True
    for i in range(len(s1), len(s2)):
        add_ch = s2[i]
        remove_ch = s2[i - len(s1)]
        window[add_ch] += 1
        window[remove_ch] -= 1
        if window[remove_ch] == 0:
            del window[remove_ch]
        if window == need:
            return True
    return False
```

**Complexity:** Time O(n) — n = len(s2), each step is O(26) = O(1), Space O(26) = O(1)

**6. Follow-up questions**
- What if we need to return the starting index? Add `return i - len(s1) + 1` instead of `return True` — see Problem 6.
- Can we avoid Counter equality comparison (which is O(26))? Yes — maintain a `matches` count tracking how many characters have the correct frequency; increment/decrement on each slide. This gives O(1) per step with the same O(n) overall.
- What if the strings are Unicode? Use a `defaultdict(int)` instead of Counter; the logic is identical.

---

### Problem 6: Find All Anagrams in a String  [Medium]  [LC #438]

**1. Clarifying questions to ask**
- Return a list of all starting indices where `p`'s anagram begins in `s`? Yes.
- Both lowercase English letters only? Yes.
- Can indices overlap? They can in theory if `len(p) == 1`, but anagram windows don't overlap since they are fixed length.
- Return indices in sorted order? Yes (they are naturally sorted since we scan left to right).

**2. Brute force**
Same as Problem 5 brute force but collect all valid starting indices. Time O(n · k log k), Space O(k).

**3. Optimization**
Same fixed-size sliding window approach as Problem 5, but instead of returning True on the first match, append the starting index `i - len(p) + 1` to the result list.

```
s="cbaebabacd", p="abc"
k=3, need={a:1,b:1,c:1}

Bootstrap s[0:3]="cba": {c:1,b:1,a:1} == need → append 0
Slide i=3: add 'e', remove 'c' → {b:1,a:1,e:1} ≠ need
Slide i=4: add 'b', remove 'b' → {b:1,a:1,e:1} ≠ need   (b added, b removed, no change)
Slide i=5: add 'a', remove 'a' → {b:1,a:1,e:1} ≠ need   (a added, a removed)
Slide i=6: add 'b', remove 'e' → {b:2,a:1} ≠ need
Slide i=7: add 'a', remove 'b' → {b:1,a:2} ≠ need
Slide i=8: add 'c', remove 'b' → {a:2,c:1} ≠ need
Slide i=9: add 'd', remove 'a' → {a:1,c:1,d:1} ≠ need

Wait — let me retrace more carefully for "cbaebabacd":
indices:  0 1 2 3 4 5 6 7 8 9
chars:    c b a e b a b a c d

Bootstrap [0:3]="cba": {c:1,b:1,a:1} == need → result=[0]
i=3: add s[3]='e', remove s[0]='c' → {b:1,a:1,e:1}  ≠ need
i=4: add s[4]='b', remove s[1]='b' → {b:1,a:1,e:1}  ≠ need
i=5: add s[5]='a', remove s[2]='a' → {b:1,a:1,e:1}  ≠ need
i=6: add s[6]='b', remove s[3]='e' → {b:2,a:1}       ≠ need
i=7: add s[7]='a', remove s[4]='b' → {b:1,a:2}       ≠ need
i=8: add s[8]='c', remove s[5]='a' → {b:1,a:1,c:1}  == need → result=[0,6]
i=9: add s[9]='d', remove s[6]='b' → {a:1,c:1,d:1}  ≠ need

Answer: [0, 6]
```

**4. Edge cases**
- `len(p) > len(s)`: return `[]`
- `s == p`: return `[0]`
- No anagrams exist: return `[]`
- `p` has all duplicate characters (e.g., `p="aaa"`): window must contain exactly three 'a's

**5. Final code**
```python
from collections import Counter
from typing import List

def find_all_anagrams(s: str, p: str) -> List[int]:
    result = []
    if len(p) > len(s):
        return result
    need = Counter(p)
    window = Counter(s[:len(p)])
    if window == need:
        result.append(0)
    for i in range(len(p), len(s)):
        window[s[i]] += 1
        old_ch = s[i - len(p)]
        window[old_ch] -= 1
        if window[old_ch] == 0:
            del window[old_ch]
        if window == need:
            result.append(i - len(p) + 1)
    return result
```

**Complexity:** Time O(n), Space O(26) = O(1)

**6. Follow-up questions**
- Difference from Problem 5? Problem 5 returns on the first match; this collects all matches. Code difference: one line.
- Optimize using a `matches` counter? Track per-character satisfaction counts; eliminate the O(26) Counter comparison with an O(1) `matches == 26` check.
- What if the pattern is very long (e.g., `len(p) = len(s)`)? One window check — O(len(s)) for bootstrap, then 0 slides. Efficient.

---

## Hard

---

### Problem 7: Minimum Window Substring  [Hard]  [LC #76]

**1. Clarifying questions to ask**
- Must the result contain all characters of `t` including duplicates? Yes — if `t="AA"`, the window must have at least two 'A's.
- If no valid window exists, return `""`? Yes.
- Can `s` and `t` contain characters other than lowercase letters? Yes — both can be any ASCII characters.
- If multiple minimum windows of the same length exist, return any? Yes, return the leftmost.

**2. Brute force**
Generate all substrings of `s`. For each, check if it contains all characters of `t`. Return the shortest valid one. Time O(n² · (n + |t|)), Space O(|t|).

**3. Optimization**
Variable-size sliding window with `need` (required frequencies) and `have` (current window frequencies).

Key: maintain a `formed` counter that tracks how many distinct characters from `t` have been satisfied (i.e., `have[ch] >= need[ch]`). When `formed == required` (all characters satisfied), try to shrink from the left to minimize the window — shrink as long as the window remains valid.

```
s="ADOBECODEBANC", t="ABC"
need={A:1, B:1, C:1}, required=3

right=0 'A': have={A:1}, formed=1 (A satisfied)
right=1 'D': have={A:1,D:1}, formed=1
right=2 'O': formed=1
right=3 'B': have[B]=1, formed=2 (B satisfied)
right=4 'E': formed=2
right=5 'C': have[C]=1, formed=3 ← all satisfied!
  → record window s[0:5]="ADOBEC", len=6
  → shrink: remove s[0]='A', have[A]=0 < need[A]=1 → formed=2
left=1, formed=2
right=6 'O': formed=2
right=7 'D': formed=2
right=8 'E': formed=2
right=9 'B': have[B]=2, formed=2 (B was already satisfied, no change)
right=10 'A': have[A]=1, formed=3 ← all satisfied!
  → record window s[1:10]="DOBECODEBA", len=10  (no improvement)
  → shrink: remove s[1]='D', have[D] drops but D not in need → formed stays 3
  → record window s[2:10]="OBECODEBA", len=9
  → shrink: remove s[2]='O' → formed 3
  → record s[3:10]="BECODEBA", len=8
  → shrink: remove s[3]='B', have[B]=1 still >=1 → formed 3
  → record s[4:10]="ECODEBA", len=7
  → shrink: remove s[4]='E' → formed 3
  → record s[5:10]="CODEBA", len=6
  → shrink: remove s[5]='C', have[C]=0 < 1 → formed=2
left=6
right=11 'N': formed=2
right=12 'C': have[C]=1, formed=3 ← all satisfied!
  → record s[6:12]="ODEBANC", len=7  (no improvement)
  → shrink: remove s[6]='O' → formed 3, record s[7:12]="DEBANC", len=6
  → shrink: remove s[7]='D' → formed 3, record s[8:12]="EBANC", len=5
  → shrink: remove s[8]='E' → formed 3, record s[9:12]="BANC", len=4  ← new min!
  → shrink: remove s[9]='B', have[B]=0 < 1 → formed=2
left=10

No more characters. best = (4, 9, 12) → s[9:13] = "BANC"
Answer: "BANC"
```

**4. Edge cases**
- `t` is empty: return `""` (per LC convention)
- `len(s) < len(t)`: no valid window, return `""`
- `s == t`: return `s`
- `t` has duplicate characters: `need[ch]` is > 1; `formed` increments only when `have[ch]` exactly reaches `need[ch]` for the first time
- No valid window: `best[0] == float("inf")`, return `""`

**5. Final code**
```python
from collections import Counter, defaultdict

def min_window_substring(s: str, t: str) -> str:
    if not t:
        return ""
    need = Counter(t)
    have: dict[str, int] = defaultdict(int)
    formed = 0
    required = len(need)   # number of distinct characters to satisfy
    left = 0
    best = (float("inf"), 0, 0)  # (length, left, right)
    for right, ch in enumerate(s):
        have[ch] += 1
        if ch in need and have[ch] == need[ch]:
            formed += 1           # this character is now fully satisfied
        while formed == required:
            # try to record and shrink
            if right - left + 1 < best[0]:
                best = (right - left + 1, left, right)
            have[s[left]] -= 1
            if s[left] in need and have[s[left]] < need[s[left]]:
                formed -= 1       # losing a required character
            left += 1
    return "" if best[0] == float("inf") else s[best[1]: best[2] + 1]
```

**Complexity:** Time O(|s| + |t|), Space O(|s| + |t|) for the frequency maps

**6. Follow-up questions**
- Why track `formed` instead of checking `have == need` directly? `have == need` is O(|t|) per step. `formed` reduces it to O(1) — increment only when a character transitions from under-satisfied to exactly satisfied.
- What if `t` contains characters not in `s`? `formed` can never reach `required` — return `""`.
- What if you want all minimum-length windows? After finding one of length `best[0]`, continue scanning but only record windows of the same length. Store all of them.
- Time complexity breakdown: each character is added once (`right` scan) and removed at most once (`left` shrink) → O(2n) = O(n).

---

### Problem 8: Sliding Window Maximum  [Hard]  [LC #239]

**1. Clarifying questions to ask**
- Return the max of every window of size `k`? Yes.
- Are there negative numbers? Yes — the algorithm handles them.
- What if `k == 1`? Return a copy of `nums` (every element is its own max).
- What if `k == len(nums)`? Return a single-element list with the global max.

**2. Brute force**
For each window `[i, i+k-1]`, scan all k elements to find the max. Time O(n·k), Space O(1) excluding output.

**3. Optimization**
Monotonic deque (decreasing). The deque stores indices, maintaining the invariant that `nums[deque[0]] >= nums[deque[1]] >= ...`. The front of the deque is always the index of the maximum element in the current window.

On each step:
1. Remove from the front if the front index is outside the current window (`i - k`).
2. Remove from the back while `nums[deque[-1]] <= nums[i]` (smaller elements can never be the max while `i` is in the window).
3. Append `i` to the back.
4. Once `i >= k - 1`, the window is full — append `nums[deque[0]]` to results.

```
nums = [1, 3, -1, -3, 5, 3, 6, 7],  k = 3

i=0 (val=1):  deque=[]  → append 0. deque=[0]
i=1 (val=3):  3>nums[0]=1 → pop 0. deque=[] → append 1. deque=[1]
i=2 (val=-1): -1<3 → append 2. deque=[1,2]. window full → result=[nums[1]]=3
              front 1 >= i-k+1=0 ✓ (still in window)

i=3 (val=-3): -3<-1 → append 3. deque=[1,2,3]. result=[3, nums[1]]=3,3
              front 1 >= i-k+1=1 ✓

i=4 (val=5):  5>nums[3]=-3 → pop 3. 5>nums[2]=-1 → pop 2. 5>nums[1]=3 → pop 1.
              deque=[] → append 4. deque=[4]. result=[3,3, nums[4]]=3,3,5
              front 4 >= i-k+1=2 ✓

i=5 (val=3):  3<5 → append 5. deque=[4,5]. result=[3,3,5, nums[4]]=3,3,5,5
              front 4 >= i-k+1=3 ✓

i=6 (val=6):  6>nums[5]=3 → pop 5. 6>nums[4]=5 → pop 4.
              deque=[] → append 6. deque=[6]. result=[3,3,5,5, nums[6]]=3,3,5,5,6
              front 6 >= i-k+1=4 ✓

i=7 (val=7):  7>nums[6]=6 → pop 6. deque=[] → append 7. deque=[7].
              result=[3,3,5,5,6, nums[7]]=3,3,5,5,6,7
              front 7 >= i-k+1=5 ✓

Answer: [3, 3, 5, 5, 6, 7]
```

**4. Edge cases**
- `k == 1`: deque always has one element, result is just `nums`
- `k == len(nums)`: one window, result is `[max(nums)]`
- All same values: deque keeps only the rightmost index, result is all that value
- Strictly decreasing array: deque retains all k indices for each window; front is always the max

**5. Final code**
```python
from collections import deque
from typing import List

def sliding_window_maximum(nums: List[int], k: int) -> List[int]:
    dq: deque[int] = deque()   # stores indices, decreasing values
    result: List[int] = []
    for i in range(len(nums)):
        # 1. Remove indices that have fallen out of the window
        if dq and dq[0] < i - k + 1:
            dq.popleft()
        # 2. Remove smaller elements from the back — they are useless
        while dq and nums[dq[-1]] <= nums[i]:
            dq.pop()
        dq.append(i)
        # 3. Record max once first full window is formed
        if i >= k - 1:
            result.append(nums[dq[0]])
    return result
```

**Complexity:** Time O(n) — each index is appended and removed at most once, Space O(k) for the deque

**6. Follow-up questions**
- Why store indices instead of values in the deque? We need to check if the front element has exited the window (`dq[0] < i - k + 1`). Values alone cannot tell us this.
- Can you solve this with a max-heap? Yes — O(n log k). Push `(-val, index)` pairs; pop stale maxima (index outside window) when queried. More complex than the deque approach and slower.
- Sliding window minimum? Change `<=` to `>=` in the pop condition — maintain an increasing deque instead.
- What if k is given dynamically (different k per query)? Pre-processing with sparse tables gives O(1) per query after O(n log n) build — a range maximum query (RMQ) structure.

---

## Medium (Variable Window — Running Sum)

---

### Problem 9: Longest Subarray with Sum At Most K  [Medium]  [Custom]

**1. Clarifying questions to ask**
- Can elements be negative? This is the critical question. If yes, the shrinking logic breaks because removing a positive element from the left may not reduce the sum enough; we need a different strategy.
- For this problem: assume all elements are non-negative. (With negatives, use prefix sums + sorted structure for O(n log n).)
- Return the length, not the subarray? Yes.
- What if no element satisfies (e.g., every element > k)? Return 0.
- Is `k` guaranteed positive? Assume yes.

**2. Brute force**
Check all subarrays. Sum each and track the longest where sum ≤ k. Time O(n²), Space O(1).

**3. Optimization**
Variable-size sliding window. Expand right unconditionally. Once `window_sum > k`, shrink from the left until `window_sum <= k` again. Record the window length after each right-expansion.

```
nums = [3, 1, 2, 7, 4, 2, 1, 1, 5],  k = 8

right=0: sum=3 <= 8, len=1
right=1: sum=4 <= 8, len=2
right=2: sum=6 <= 8, len=3
right=3: sum=13 > 8 → shrink:
         remove nums[0]=3 → sum=10 > 8, left=1
         remove nums[1]=1 → sum=9 > 8, left=2
         remove nums[2]=2 → sum=7 <= 8, left=3
         len=1
right=4: sum=11 > 8 → shrink:
         remove nums[3]=7 → sum=4 <= 8, left=4
         len=2
right=5: sum=6 <= 8, len=3
right=6: sum=7 <= 8, len=4
right=7: sum=8 <= 8, len=5
right=8: sum=13 > 8 → shrink:
         remove nums[4]=4 → sum=9 > 8, left=5
         remove nums[5]=2 → sum=7 <= 8, left=6
         len=3

max_len tracked = 5 (window [4,2,1,1] wait — [4,2,1,1] = 8, len=4? Let me recount:
right=7 (val=1): sum = nums[4]+nums[5]+nums[6]+nums[7] = 4+2+1+1 = 8 ≤ 8
left=4, right=7 → len = 7-4+1 = 4
right=8 (val=5): sum=13... shrink to left=6: len = 8-6+1 = 3

max window = 4  (subarray [4, 2, 1, 1])
Answer: 4
```

Pattern: record the window length on every step (after potential shrinking), not just when the window is valid. After shrinking, the window is always valid.

**4. Edge cases**
- All elements > k: every single element exceeds k, so every window is immediately invalid; after shrinking, the window becomes empty — handle with `max_len = max(max_len, right - left + 1)` guard
- Single element ≤ k: window of size 1 is valid, return 1
- `k == 0` and all positive elements: no valid subarray, return 0
- All elements equal to k: every single element is a valid window of length 1; check if two consecutive elements sum ≤ k

**5. Final code**
```python
def longest_subarray_sum_at_most_k(nums: list[int], k: int) -> int:
    left = 0
    window_sum = 0
    max_len = 0
    for right in range(len(nums)):
        window_sum += nums[right]
        while window_sum > k and left <= right:
            window_sum -= nums[left]
            left += 1
        max_len = max(max_len, right - left + 1)
    return max_len
```

**Complexity:** Time O(n), Space O(1)

**6. Follow-up questions**
- What if elements can be negative? The window can no longer reliably shrink from the left (removing a negative element increases the sum). Use prefix sums: for each `right`, find the largest `left` such that `prefix[right] - prefix[left-1] <= k`. With a sorted structure or binary search on monotone prefix sums, this is O(n log n).
- What if you want exactly sum equal to k (not at most)? Use a hash map of prefix sums — `prefix[j] - prefix[i] == k` — LC #560 Subarray Sum Equals K.
- What if you want the maximum subarray with at most k distinct elements? Replace the sum condition with a frequency-map size condition — LC #340.
- Minimum length subarray with sum at least k (all positive)? That is Problem 3. The shrink condition flips: shrink while valid, record minimum, then stop shrinking.
