# Two-Pointer — Problems

## Easy

---

### Problem 1: Two Sum II — Input Array Is Sorted  [Easy]  [LC #167]

**1. Clarifying questions to ask**
- Is the array guaranteed to be sorted in non-decreasing order? (Yes, per problem name — confirm ascending vs descending)
- Is there exactly one solution? (Yes, per problem statement)
- Is 1-indexed output expected? (Yes, per LC)
- Can I use extra space? (Expect O(1) space solution; hash map is O(n) and would be rejected)
- Can the same element be used twice? (No, the two indices must differ)

**2. Brute force**
Check every pair (i, j) where i < j. Time O(n²), Space O(1).

**3. Optimization**
Since the array is sorted, use opposite-ends two-pointer. If sum < target, move left pointer right (increase sum). If sum > target, move right pointer left (decrease sum). Each step eliminates at least one element, so we terminate in O(n).

```
numbers = [2, 7, 11, 15],  target = 9
           L            R   sum=17 > 9 → move R left
           L        R       sum=13 > 9 → move R left
           L    R           sum=9  = 9 → return [1, 2]
```

**4. Edge cases**
- Array of size 2 (always return [1, 2] since exactly one solution exists)
- Target is sum of first + last element
- Negative numbers (algorithm works identically)
- Duplicate values — harmless since we stop at the first match

**5. Final code**
```python
def two_sum_sorted(numbers: list[int], target: int) -> list[int]:
    left, right = 0, len(numbers) - 1
    while left < right:
        s = numbers[left] + numbers[right]
        if s == target:
            return [left + 1, right + 1]  # 1-indexed
        elif s < target:
            left += 1
        else:
            right -= 1
    return []  # guaranteed to find answer per problem
```

**Complexity:** Time O(n), Space O(1)

**6. Follow-up questions**
- What if the array is not sorted? Use a hash map — Two Sum LC #1 — O(n) time and space.
- What if there can be multiple valid pairs? Collect all; still O(n) with an outer continuation instead of return.
- What if we need triplets? Outer loop + two-pointer inner loop = 3Sum (see Problem 6).
- What if indices are 0-based? Remove the `+ 1` offsets.

---

### Problem 2: Valid Palindrome  [Easy]  [LC #125]

**1. Clarifying questions to ask**
- What counts as alphanumeric? Letters a-z, A-Z, digits 0-9.
- Is the comparison case-sensitive? No — treat uppercase as lowercase.
- Is an empty string a palindrome? Yes (by convention; LC returns True).
- Can the string contain only non-alphanumeric characters like `" "`? Yes — treat as empty → True.

**2. Brute force**
Filter the string to only alphanumeric characters, lowercase everything, then check if it equals its reverse. Time O(n), Space O(n).

**3. Optimization**
Use opposite-ends two-pointer directly on the original string. Skip non-alphanumeric characters by advancing the pointer without consuming it. Saves the O(n) space of building a filtered copy.

```
s = "A man, a plan, a canal: Panama"
     L                             R
     A == A → advance both
        L                       R
        m == a? skip commas/spaces...
→ each alphanumeric pair gets compared in O(1) amortized
```

**4. Edge cases**
- All non-alphanumeric (e.g., `"!!"`) → left and right converge without comparing → return True
- Single character → `left < right` is False immediately → True
- Mixed case: `"Aa"` → lowercased comparison → True

**5. Final code**
```python
def is_palindrome(s: str) -> bool:
    left, right = 0, len(s) - 1
    while left < right:
        # Skip non-alphanumeric from both ends
        while left < right and not s[left].isalnum():
            left += 1
        while left < right and not s[right].isalnum():
            right -= 1
        if s[left].lower() != s[right].lower():
            return False
        left += 1
        right -= 1
    return True
```

**Complexity:** Time O(n), Space O(1)

**6. Follow-up questions**
- What if we need to check if a string can become a palindrome by removing at most one character? (LC #680 Valid Palindrome II — extend with a helper that allows one skip.)
- What about Unicode? `isalnum()` handles Unicode letters and digits correctly in Python.
- Can you do it recursively? Yes, but O(n) call stack depth — not preferred for large inputs.

---

### Problem 3: Move Zeroes  [Easy]  [LC #283]

**1. Clarifying questions to ask**
- Must relative order of non-zero elements be preserved? Yes.
- Is in-place required? Yes.
- Does it matter what fills the end positions? No (but they should be 0).

**2. Brute force**
Create a new array: append all non-zeros, then pad with zeros. Copy back. Time O(n), Space O(n).

**3. Optimization**
Fast/slow two-pointer (read/write). `slow` (write pointer) tracks the next position to place a non-zero value. `fast` (read pointer) scans forward. When `fast` finds a non-zero, swap it to `slow`'s position and advance `slow`. This keeps zeros accumulating at the tail.

```
[0, 1, 0, 3, 12]
 W
 R               fast=0, nums[R]=0 → skip
    W
    R            fast=1, nums[R]=1 → swap(W,R), slow++
       W
       R         fast=2, nums[R]=0 → skip
       W
          R      fast=3, nums[R]=3 → swap(W,R), slow++
          W
             R   fast=4, nums[R]=12 → swap(W,R), slow++

Result: [1, 3, 12, 0, 0]
```

**4. Edge cases**
- All zeros: slow never advances, all remain 0
- No zeros: every swap is a self-swap (fast==slow), no visible change
- Single element: loop doesn't execute

**5. Final code**
```python
def move_zeroes(nums: list[int]) -> None:
    slow = 0
    for fast in range(len(nums)):
        if nums[fast] != 0:
            nums[slow], nums[fast] = nums[fast], nums[slow]
            slow += 1
    # slow now points to first zero position; tail is already 0
```

**Complexity:** Time O(n), Space O(1)

**6. Follow-up questions**
- Minimize the number of writes: if `slow != fast`, only then swap — the above code already does this since when `slow == fast` the swap is a no-op.
- What if we want zeros at the front instead? Reverse the condition or scan from right to left.
- What if we have multiple values to move (e.g., move all 1s to end)? Same pattern — `if nums[fast] != 1`.

---

### Problem 4: Remove Duplicates from Sorted Array  [Easy]  [LC #26]

**1. Clarifying questions to ask**
- Is the array sorted? Yes (critical — algorithm relies on this).
- Should duplicates be removed in-place? Yes.
- Do elements beyond the returned count matter? No.
- Return value: count of unique elements, not the array itself.

**2. Brute force**
Use a set to track seen elements, rebuild the array. Time O(n), Space O(n).

**3. Optimization**
Fast/slow two-pointer with a write pointer. `slow` is the index of the last unique element placed. `fast` scans ahead. Whenever `nums[fast] != nums[slow]`, advance `slow` and overwrite `nums[slow] = nums[fast]`. No swap needed — we only write forward.

```
[1, 1, 2, 3, 3]
 S
    F           nums[F]=1 == nums[S]=1 → skip
       F        nums[F]=2 != nums[S]=1 → slow++, write 2
          F     nums[F]=3 != nums[S]=2 → slow++, write 3
             F  nums[F]=3 == nums[S]=3 → skip

slow=2 → return slow+1 = 3
nums[:3] = [1, 2, 3]
```

**4. Edge cases**
- Empty array: return 0 immediately
- All duplicates (e.g., `[1,1,1]`): slow stays at 0, return 1
- All unique: slow advances with every step, return n

**5. Final code**
```python
def remove_duplicates(nums: list[int]) -> int:
    if not nums:
        return 0
    slow = 0
    for fast in range(1, len(nums)):
        if nums[fast] != nums[slow]:
            slow += 1
            nums[slow] = nums[fast]  # overwrite, no swap needed
    return slow + 1
```

**Complexity:** Time O(n), Space O(1)

**6. Follow-up questions**
- What if duplicates are allowed up to k times? Generalize: `if fast - slow < k or nums[fast] != nums[slow - k + 1]` — LC #80.
- Why overwrite instead of swap? Swap would corrupt the sorted order if elements ahead aren't processed yet. Since we only read `fast` forward, overwrite is safe.
- What if the array is not sorted? Cannot use two-pointer; use a hash map or sort first.

---

### Problem 5: Reverse String  [Easy]  [LC #344]

**1. Clarifying questions to ask**
- In-place reversal required? Yes.
- Input type: list of characters (not a Python string, which is immutable).
- Any constraint on extra space? Must be O(1).

**2. Brute force**
`s[:] = s[::-1]` in Python — reversal via slice creates a copy. Acceptable in practice but uses O(n) space.

**3. Optimization**
Opposite-ends two-pointer. Swap `s[left]` and `s[right]`, move `left` right and `right` left, until they meet. Classic textbook example of opposite-ends variant.

```
s = ['h', 'e', 'l', 'l', 'o']
     L                    R    swap → ['o', 'e', 'l', 'l', 'h']
          L          R         swap → ['o', 'l', 'l', 'e', 'h']
               L,R             left >= right → stop

Result: ['o', 'l', 'l', 'e', 'h']
```

**4. Edge cases**
- Empty array: loop doesn't execute
- Single character: left >= right immediately, no swap
- Even length: pointers cross cleanly (left ends up > right)
- Odd length: pointers meet at the middle character, `left < right` is False, middle stays

**5. Final code**
```python
def reverse_string(s: list[str]) -> None:
    left, right = 0, len(s) - 1
    while left < right:
        s[left], s[right] = s[right], s[left]
        left += 1
        right -= 1
```

**Complexity:** Time O(n), Space O(1)

**6. Follow-up questions**
- Reverse only a portion (indices i to j)? Set `left, right = i, j` and apply the same loop.
- Reverse words in a sentence in-place? Reverse entire string, then reverse each word — O(n) overall.
- What about Unicode surrogate pairs or multi-byte characters? Python handles them as single `chr` objects, so no special handling needed in Python.

---

## Medium

---

### Problem 6: 3Sum  [Medium]  [LC #15]

**1. Clarifying questions to ask**
- Must the output be unique triplets? Yes, no duplicate triplets.
- Can the same element be used multiple times? No — each index used at most once.
- Is the output order required? No (LC accepts any order).
- Can there be duplicate values in the input? Yes.

**2. Brute force**
Triple nested loop checking all (i, j, k) combinations. Time O(n³), Space O(1) ignoring output.

**3. Optimization**
Sort the array. Fix one element with outer loop index `i`. Then run opposite-ends two-pointer on `nums[i+1..n-1]` looking for a pair summing to `-nums[i]`. This converts the inner loop from O(n²) to O(n).

Duplicate handling is the hard part:
- Skip `nums[i]` if it equals `nums[i-1]` (same outer element as last iteration)
- After finding a triplet, skip duplicate `left` and `right` values before advancing

```
nums = [-4, -1, -1, 0, 1, 2]   (sorted)
i=0: nums[i]=-4, target=4 → two-pointer on [-1,-1,0,1,2]
     L=-1, R=2 → sum=1 < 4 → L++
     L=-1, R=2 → sum=1 < 4 → L++
     L=0,  R=2 → sum=2 < 4 → L++
     L=1,  R=2 → sum=3 < 4 → L++
     left >= right → no match at i=0

i=1: nums[i]=-1, target=1 → two-pointer on [-1,0,1,2]
     L=-1, R=2 → sum=1 == 1 → triplet [-1,-1,2], skip dups, L++,R--
     L=0,  R=1 → sum=1 == 1 → triplet [-1,0,1], L++,R--
     left >= right → done

i=2: nums[i]=-1 == nums[i-1]=-1 → skip (duplicate outer)
i=3: nums[i]=0, target=0 → two-pointer on [1,2]
     L=1, R=2 → sum=3 > 0 → no match
```

**4. Edge cases**
- All zeros: `[0,0,0]` → one triplet `[0,0,0]`
- All positive: no valid triplet (sorted → `nums[i] >= 0` early termination possible)
- Two elements: not enough for a triplet → return `[]`
- Duplicates: skip logic is essential to avoid repeats

**5. Final code**
```python
def three_sum(nums: list[int]) -> list[list[int]]:
    nums.sort()
    result = []
    for i in range(len(nums) - 2):
        if i > 0 and nums[i] == nums[i - 1]:
            continue  # skip duplicate outer element
        left, right = i + 1, len(nums) - 1
        while left < right:
            s = nums[i] + nums[left] + nums[right]
            if s == 0:
                result.append([nums[i], nums[left], nums[right]])
                # Skip duplicate left values
                while left < right and nums[left] == nums[left + 1]:
                    left += 1
                # Skip duplicate right values
                while left < right and nums[right] == nums[right - 1]:
                    right -= 1
                left += 1
                right -= 1
            elif s < 0:
                left += 1
            else:
                right -= 1
    return result
```

**Complexity:** Time O(n²), Space O(1) excluding output

**6. Follow-up questions**
- 4Sum (LC #18)? Add one more outer loop — O(n³). The pattern generalizes: k-Sum uses k-2 nested loops + two-pointer.
- Find the triplet closest to a target? Track `min_diff` alongside the current best triplet.
- How does the early termination `nums[i] > 0 → break` help? Since sorted, if the smallest element is positive, no triplet can sum to 0.

---

### Problem 7: Container With Most Water  [Medium]  [LC #11]

**1. Clarifying questions to ask**
- Are the heights all non-negative integers? Yes.
- Can heights be 0? Yes (though that line holds no water).
- Is there exactly one optimal answer? No — may be ties, but return any max area.
- Must I return the area, not the indices? Yes.

**2. Brute force**
Check all pairs (i, j). Area = `min(height[i], height[j]) * (j - i)`. Time O(n²), Space O(1).

**3. Optimization**
Start with the widest possible container (left=0, right=n-1). Compute area. Then move the pointer pointing to the shorter line inward — because keeping the shorter line can only reduce or maintain width, while moving the taller line inward guarantees the shorter line is the limiting factor anyway.

Key insight: the current area is `min(h[L], h[R]) * width`. If we move the taller pointer, width decreases AND the height cannot increase (still capped by the shorter side) → area strictly decreases. So we must move the shorter pointer to have any chance of finding a larger area.

```
height = [1, 8, 6, 2, 5, 4, 8, 3, 7]
indices:   0  1  2  3  4  5  6  7  8

L=0, R=8: area = min(1,7)*8 = 8,  h[L]<h[R] → L++
L=1, R=8: area = min(8,7)*7 = 49, h[L]>h[R] → R--
L=1, R=7: area = min(8,3)*6 = 18, h[L]>h[R] → R--
L=1, R=6: area = min(8,8)*5 = 40, h[L]==h[R] → R-- (move either)
...
max_area = 49
```

**4. Edge cases**
- Two elements: only one possible container, return it
- All equal heights: area decreases monotonically as pointers converge
- Ascending heights: max is always at L=0, R=n-1 (picked first)

**5. Final code**
```python
def container_with_most_water(height: list[int]) -> int:
    left, right = 0, len(height) - 1
    max_area = 0
    while left < right:
        area = min(height[left], height[right]) * (right - left)
        max_area = max(max_area, area)
        if height[left] < height[right]:
            left += 1
        else:
            right -= 1
    return max_area
```

**Complexity:** Time O(n), Space O(1)

**6. Follow-up questions**
- Why is it safe to move the shorter pointer? Moving the taller pointer can only decrease the area — the new height is still capped by the shorter side, and width has decreased. No solution is missed.
- What if we need to track which pair gave the max? Store `(left, right)` alongside `max_area`.
- Trapping Rain Water vs Container: Container picks two walls (no middle bars); Trapping fills water between ALL bars (see Problem 9).

---

### Problem 8: Sort Colors  [Medium]  [LC #75]

**1. Clarifying questions to ask**
- Values are exactly 0, 1, 2? Yes (red=0, white=1, blue=2).
- In-place required? Yes.
- Can I use a counting sort approach? Interviewer may accept it but will ask for a one-pass solution.
- One pass, O(1) space? Yes — that is the target approach.

**2. Brute force**
Count occurrences of 0, 1, 2, then overwrite the array. Two passes, O(1) extra space. Correct but not impressive.

**3. Optimization**
Dutch National Flag algorithm (Dijkstra). Three pointers:
- `low`: boundary between 0-section and 1-section (next slot for 0)
- `mid`: current element being examined
- `high`: boundary between 1-section and 2-section (next slot for 2)

Invariant maintained: `nums[0..low-1]` are all 0, `nums[low..mid-1]` are all 1, `nums[high+1..n-1]` are all 2.

```
[2, 0, 2, 1, 1, 0]
 L  M           H

mid=2: swap(mid,high), high--  → [0, 0, 2, 1, 1, 2], H=4
mid=0: swap(low,mid), low++, mid++ → [0, 0, 2, 1, 1, 2], L=1,M=1
mid=0: swap(low,mid), low++, mid++ → [0, 0, 2, 1, 1, 2], L=2,M=2
mid=2: swap(mid,high), high--  → [0, 0, 1, 1, 2, 2], H=3
mid=1: mid++                   → M=3
mid=1: mid++                   → M=4, mid>high → stop

Result: [0, 0, 1, 1, 2, 2]
```

**4. Edge cases**
- All same color: pointer adjusts without swapping, O(n) passes
- Already sorted: `mid` scans to `high` advancing every step
- Two elements: handled correctly by the invariant

**5. Final code**
```python
def sort_colors(nums: list[int]) -> None:
    low, mid, high = 0, 0, len(nums) - 1
    while mid <= high:
        if nums[mid] == 0:
            nums[low], nums[mid] = nums[mid], nums[low]
            low += 1
            mid += 1          # nums[low..mid-1] were 1s; after swap, mid is 1
        elif nums[mid] == 1:
            mid += 1          # 1 is already in the right section
        else:                 # nums[mid] == 2
            nums[mid], nums[high] = nums[high], nums[mid]
            high -= 1         # don't advance mid — swapped-in value unexamined
```

**Complexity:** Time O(n), Space O(1), exactly one pass

**6. Follow-up questions**
- Why not advance `mid` when swapping with `high`? The element swapped from `high` has not been examined yet; it could be 0, 1, or 2.
- Generalize to k colors? Use a different algorithm (e.g., counting sort or quicksort with k partitions); Dutch National Flag is specific to 3 values.
- What if values are not 0/1/2 but arbitrary? Map them to 0/1/2 first, or use a general sort.

---

## Hard

---

### Problem 9: Trapping Rain Water  [Hard]  [LC #42]

**1. Clarifying questions to ask**
- Heights are non-negative integers? Yes.
- Can the array be empty or have fewer than 3 elements? Yes — return 0.
- Is O(n) time and O(1) space the target? Yes.
- Can I verify with the classic O(n) space approach first? Good practice in an interview — show you know it, then optimize.

**2. Brute force**
For each position `i`, find `max_left = max(heights[0..i])` and `max_right = max(heights[i..n-1])`. Water at `i` = `min(max_left, max_right) - height[i]`. Time O(n²), Space O(1).

**3. O(n) space approach (stepping stone)**
Precompute `left_max[i]` and `right_max[i]` arrays. Water at each position is `min(left_max[i], right_max[i]) - height[i]`. Time O(n), Space O(n).

**4. Optimization: two-pointer O(1) space**
Key insight: if `height[left] < height[right]`, then `right_max >= height[right] > height[left]`, so the water at `left` is determined entirely by `left_max`. We do not need `right_max` for this column. Move `left` inward.

Similarly, if `height[right] <= height[left]`, the water at `right` is determined by `right_max`.

```
height = [0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]
          L                                   R

Trace (left_max, right_max track running maxima):
L=0,R=11: h[L]=0 < h[R]=1 → left_max=0, water+=0-0=0, L++
L=1,R=11: h[L]=1 >= h[R]=1 → right_max=1, water+=1-1=0, R--
L=1,R=10: h[L]=1 >= h[R]=2 → right_max=2, water+=2-2=0, R--
L=1,R=9:  h[L]=1 >= h[R]=1 → right_max=2, water+=2-1=1, R--
L=1,R=8:  h[L]=1 < h[R]=2  → left_max=1, water+=1-1=0, L++
L=2,R=8:  h[L]=0 < h[R]=2  → left_max=1, water+=1-0=1, L++
L=3,R=8:  h[L]=2 >= h[R]=2 → right_max=2, water+=2-2=0, R--
... continues until total = 6
```

**5. Edge cases**
- Empty array: return 0
- Monotonically increasing/decreasing: no water trapped (pointers converge without adding)
- All same height: no water
- Single valley (e.g., `[3, 0, 3]`): 3 units of water

**6. Final code**
```python
def trap_rain_water(height: list[int]) -> int:
    if not height:
        return 0
    left, right = 0, len(height) - 1
    left_max = right_max = 0
    water = 0
    while left < right:
        if height[left] < height[right]:
            if height[left] >= left_max:
                left_max = height[left]       # update running max
            else:
                water += left_max - height[left]  # water fills to left_max
            left += 1
        else:
            if height[right] >= right_max:
                right_max = height[right]
            else:
                water += right_max - height[right]
            right -= 1
    return water
```

**Complexity:** Time O(n), Space O(1)

**7. Follow-up questions**
- Why does knowing `height[left] < height[right]` mean we can compute water at `left` without knowing the actual `right_max`? Because `right_max >= height[right] > height[left]`, so `min(left_max, right_max) = left_max`. The right side is guaranteed to be at least as tall.
- 3D variant (LC #407 Trapping Rain Water II)? Use a min-heap (priority queue) instead of two-pointer — add boundary cells, always process the shortest boundary first.
- How does this relate to Container With Most Water? Both use opposite-ends two-pointer on heights, but Container picks exactly two walls; Trapping Rain Water fills gaps between all walls.

---

## Medium (Linked List)

---

### Problem 10: Linked List Cycle II  [Medium]  [LC #142]

**1. Clarifying questions to ask**
- Should I return the node where the cycle begins, or just detect if there is a cycle? Return the node (LC #142 asks for entry point; LC #141 is just detection).
- Return `None` if no cycle? Yes.
- Can I use O(1) extra space? Yes — that is the target (hash set approach is O(n)).

**2. Brute force**
Use a hash set: traverse the list, add each node to the set. First node seen twice is the cycle entry. Time O(n), Space O(n).

**3. Optimization: Floyd's algorithm (two phases)**

**Phase 1 — Detect cycle:**
Use `slow` (moves 1 step) and `fast` (moves 2 steps). If they ever meet, a cycle exists.

**Phase 2 — Find entry point:**
Mathematical insight: when `slow` and `fast` meet inside the cycle, if we reset one pointer to `head` and move both at speed 1, they will meet exactly at the cycle entry.

Why it works (proof sketch):
- Let `F` = distance from head to cycle entry
- Let `C` = cycle length
- Let `a` = distance from entry to meeting point
- When they meet: slow traveled `F + a`, fast traveled `F + a + k*C` for some integer k
- Since fast travels 2× as far: `2(F + a) = F + a + k*C` → `F = k*C - a`
- Distance from meeting point back to entry = `C - a`
- `F = k*C - a = (k-1)*C + (C - a)` — which means walking `F` steps from head lands at the entry at the same time as walking `C - a` from the meeting point.

```
head → [1 → 2 → 3 → 4 → 5]
                ↑           |
                └───────────┘
                  cycle entry = 3

Phase 1: slow=1,fast=1
  step1: slow=2, fast=3
  step2: slow=3, fast=5
  step3: slow=4, fast=4  ← meet at node 4

Phase 2: reset slow to head=1, fast stays at 4
  step1: slow=2, fast=5
  step2: slow=3, fast=3  ← meet at node 3 = cycle entry ✓
```

**4. Edge cases**
- No cycle: `fast` reaches `None` or `fast.next` is `None` → return `None`
- Cycle at head (entire list is a cycle): `F=0`, pointers meet at head
- Cycle of length 1 (self-loop): detected on first fast step
- List of one node with self-loop

**5. Final code**
```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def detect_cycle(head: ListNode | None) -> ListNode | None:
    # Phase 1: detect if cycle exists
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:
            break
    else:
        return None  # no cycle (loop ended without break)

    # Phase 2: find cycle entry
    slow = head
    while slow is not fast:
        slow = slow.next
        fast = fast.next
    return slow  # cycle entry node
```

**Complexity:** Time O(n), Space O(1)

**6. Follow-up questions**
- How do you find the cycle length? After Phase 1 meeting, keep `fast` still, move `slow` one step at a time counting until they meet again — that count is the cycle length.
- What if you only need to detect a cycle (LC #141)? Phase 1 alone suffices — return `True` if `slow is fast`, `False` if loop exits.
- Can you use this on arrays? Yes — if values are indices (LC #287 Find the Duplicate Number uses the same Floyd's approach treating array values as next pointers).
- Space-time trade-off: hash set is O(n)/O(n) with simpler code; Floyd's is O(n)/O(1) and demonstrates deeper understanding — interviewers prefer Floyd's.
