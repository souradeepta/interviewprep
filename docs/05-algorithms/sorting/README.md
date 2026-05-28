# Sorting Algorithms

**Level:** L3-L4
**Time to read:** ~25 min

Master the eight core sorting algorithms — know when each wins and why interviewers keep asking about merge sort and quick sort.

---

## Comparative Trade-off Table

| Algorithm | Best | Average | Worst | Space | Stable? | When to use |
|-----------|------|---------|-------|-------|---------|-------------|
| Bubble | O(n) | O(n²) | O(n²) | O(1) | Yes | Never (educational only) |
| Selection | O(n²) | O(n²) | O(n²) | O(1) | No | Memory writes expensive |
| Insertion | O(n) | O(n²) | O(n²) | O(1) | Yes | Small/nearly-sorted arrays |
| Merge | O(n log n) | O(n log n) | O(n log n) | O(n) | Yes | Linked lists, external sort |
| Quick | O(n log n) | O(n log n) | O(n²) | O(log n) | No | General purpose, cache friendly |
| Heap | O(n log n) | O(n log n) | O(n log n) | O(1) | No | Guaranteed O(n log n), in-place |
| Counting | O(n+k) | O(n+k) | O(n+k) | O(k) | Yes | Small integer range |
| Radix | O(nk) | O(nk) | O(nk) | O(n+k) | Yes | Integers, fixed-length strings |

**k** = range of input values (Counting) or number of digits (Radix).

### Decision Framework

```
Need stable sort?
  YES → Merge Sort (general), Insertion Sort (small/nearly-sorted)
  NO  → Quick Sort (cache-friendly, good avg case), Heap Sort (guaranteed O(n log n))

Know input range is small integers?
  YES → Counting Sort (integers), Radix Sort (multi-digit integers/strings)
  NO  → Comparison-based sorts above

Working with linked lists?
  YES → Merge Sort (no random access needed)
  NO  → Quick Sort or Heap Sort

External sort (data doesn't fit in memory)?
  YES → Merge Sort (sequential access pattern)
  NO  → Any in-memory sort
```

---

## Algorithm Breakdowns

### Bubble Sort
Compare adjacent pairs, swap if out of order, repeat until no swaps occur. Each pass bubbles the largest unsorted element to its correct position. Best case O(n) if already sorted (no swaps in first pass).

**Complexity:** Time O(n²) avg/worst, O(n) best | Space O(1) | Stable: Yes

```python
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        swapped = False
        for j in range(n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:
            break  # Already sorted
    return arr
```

---

### Selection Sort
Find the minimum element in the unsorted portion and swap it to the front. Makes exactly n-1 swaps total — useful when write operations are expensive (e.g., flash memory). Cannot be made stable without extra work.

**Complexity:** Time O(n²) all cases | Space O(1) | Stable: No

```python
def selection_sort(arr):
    n = len(arr)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            if arr[j] < arr[min_idx]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
    return arr
```

---

### Insertion Sort
Build the sorted array one element at a time by inserting each new element into its correct position. Efficient for small or nearly-sorted data; used as the base case in hybrid sorts like Timsort. Online algorithm — can sort as elements arrive.

**Complexity:** Time O(n²) avg/worst, O(n) best | Space O(1) | Stable: Yes

```python
def insertion_sort(arr):
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    return arr
```

---

### Merge Sort
Divide array in half recursively until single elements, then merge sorted halves back together. The merge step combines two sorted arrays in O(n) time, yielding guaranteed O(n log n). Preferred for linked lists and external sorting due to sequential access.

**Complexity:** Time O(n log n) all cases | Space O(n) | Stable: Yes

```python
def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return merge(left, right)

def merge(left, right):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:   # <= preserves stability
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result
```

---

### Quick Sort
Choose a pivot, partition array into elements ≤ pivot and > pivot, recurse on each partition. Average O(n log n) with excellent cache locality; worst case O(n²) on already-sorted input without randomization. Python's built-in sort (Timsort) uses merge sort — quick sort shines in C/C++ systems code.

**Complexity:** Time O(n log n) avg, O(n²) worst | Space O(log n) avg | Stable: No

```python
import random

def quick_sort(arr, lo=0, hi=None):
    if hi is None:
        hi = len(arr) - 1
    if lo < hi:
        pivot_idx = partition(arr, lo, hi)
        quick_sort(arr, lo, pivot_idx - 1)
        quick_sort(arr, pivot_idx + 1, hi)
    return arr

def partition(arr, lo, hi):
    # Random pivot prevents O(n²) on sorted input
    rand_idx = random.randint(lo, hi)
    arr[rand_idx], arr[hi] = arr[hi], arr[rand_idx]
    pivot = arr[hi]
    i = lo - 1
    for j in range(lo, hi):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[hi] = arr[hi], arr[i + 1]
    return i + 1
```

**Quick Select (O(n) average — find kth element):**

```python
def quick_select(arr, lo, hi, k):
    """Find kth smallest element (0-indexed k)."""
    if lo == hi:
        return arr[lo]
    pivot_idx = partition(arr, lo, hi)
    if k == pivot_idx:
        return arr[pivot_idx]
    elif k < pivot_idx:
        return quick_select(arr, lo, pivot_idx - 1, k)
    else:
        return quick_select(arr, pivot_idx + 1, hi, k)
```

---

### Heap Sort
Build a max-heap from the array (O(n)), then repeatedly extract the max and place it at the end. Guaranteed O(n log n) with O(1) extra space — useful when you can't afford merge sort's O(n) memory. Poor cache performance due to non-sequential access patterns.

**Complexity:** Time O(n log n) all cases | Space O(1) | Stable: No

```python
def heap_sort(arr):
    n = len(arr)
    # Build max-heap
    for i in range(n // 2 - 1, -1, -1):
        heapify(arr, n, i)
    # Extract elements one by one
    for i in range(n - 1, 0, -1):
        arr[0], arr[i] = arr[i], arr[0]
        heapify(arr, i, 0)
    return arr

def heapify(arr, n, i):
    largest = i
    left, right = 2 * i + 1, 2 * i + 2
    if left < n and arr[left] > arr[largest]:
        largest = left
    if right < n and arr[right] > arr[largest]:
        largest = right
    if largest != i:
        arr[i], arr[largest] = arr[largest], arr[i]
        heapify(arr, n, largest)
```

---

### Counting Sort
Count occurrences of each value, then reconstruct sorted array from counts. Linear time only when k (value range) is small relative to n. Requires non-negative integer keys or a mapping to integers.

**Complexity:** Time O(n+k) | Space O(k) | Stable: Yes

```python
def counting_sort(arr):
    if not arr:
        return arr
    max_val = max(arr)
    min_val = min(arr)
    offset = min_val
    k = max_val - min_val + 1
    
    count = [0] * k
    for x in arr:
        count[x - offset] += 1
    
    # Prefix sums for stable placement
    for i in range(1, k):
        count[i] += count[i - 1]
    
    output = [0] * len(arr)
    for x in reversed(arr):        # Reversed preserves stability
        count[x - offset] -= 1
        output[count[x - offset]] = x
    return output
```

---

### Radix Sort
Sort by least-significant digit first (LSD), using a stable sort (counting sort) at each digit level. Achieves linear time when the number of digits k is fixed. Works on integers and fixed-length strings.

**Complexity:** Time O(nk) | Space O(n+k) | Stable: Yes

```python
def radix_sort(arr):
    if not arr:
        return arr
    max_val = max(arr)
    exp = 1
    while max_val // exp > 0:
        arr = counting_sort_by_digit(arr, exp)
        exp *= 10
    return arr

def counting_sort_by_digit(arr, exp):
    n = len(arr)
    output = [0] * n
    count = [0] * 10
    
    for x in arr:
        digit = (x // exp) % 10
        count[digit] += 1
    for i in range(1, 10):
        count[i] += count[i - 1]
    for x in reversed(arr):
        digit = (x // exp) % 10
        count[digit] -= 1
        output[count[digit]] = x
    return output
```

---

## Worked Problems

### Problem 1: Sort an Array (LeetCode #912)

**Clarifying Questions:**
- Are there duplicates? → Yes, handle them
- What is the value range? → -5×10⁴ to 5×10⁴
- Do we need to sort in-place or can we return new array? → Either
- Is stability required? → Not specified

**Brute Force:** Use Python's built-in sort — O(n log n), but interviewer wants you to implement.

**Optimization:** Implement merge sort (guaranteed O(n log n), stable) or quick sort with random pivot.

**Edge Cases:**
- Single element → return as-is
- All duplicates → both algorithms handle correctly
- Already sorted → merge sort unaffected, quick sort needs random pivot to avoid O(n²)

**Code (Merge Sort):**
```python
def sortArray(nums):
    if len(nums) <= 1:
        return nums
    mid = len(nums) // 2
    left = sortArray(nums[:mid])
    right = sortArray(nums[mid:])
    
    merged = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i]); i += 1
        else:
            merged.append(right[j]); j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged
```

**Follow-ups:**
- Can you do it in O(n log n) worst case in-place? → Heap sort
- What if the array has many duplicates? → 3-way partition (Dutch National Flag)
- How does Python's Timsort work? → Hybrid merge/insertion, exploits natural runs

---

### Problem 2: Kth Largest Element (LeetCode #215)

**Clarifying Questions:**
- Is k always valid (1 ≤ k ≤ n)? → Yes
- Can we modify the input array? → Yes
- What is n? → Up to 10⁵

**Brute Force:** Sort descending, return index k-1. O(n log n) time.

**Optimization:** Quick Select — average O(n) time, O(1) extra space. The kth largest is the (n-k)th smallest.

**Edge Cases:**
- k=1 → largest element (max)
- k=n → smallest element (min)
- All equal elements → always return that element

**Code (Quick Select):**
```python
import random

def findKthLargest(nums, k):
    k = len(nums) - k  # Convert to kth smallest (0-indexed)
    
    def quick_select(lo, hi):
        pivot = nums[hi]
        # Random pivot to avoid O(n²) worst case
        rand = random.randint(lo, hi)
        nums[rand], nums[hi] = nums[hi], nums[rand]
        pivot = nums[hi]
        
        i = lo
        for j in range(lo, hi):
            if nums[j] <= pivot:
                nums[i], nums[j] = nums[j], nums[i]
                i += 1
        nums[i], nums[hi] = nums[hi], nums[i]
        
        if i == k:
            return nums[i]
        elif i < k:
            return quick_select(i + 1, hi)
        else:
            return quick_select(lo, i - 1)
    
    return quick_select(0, len(nums) - 1)
```

**Follow-ups:**
- What if the stream is online (elements arrive one at a time)? → Min-heap of size k: O(n log k)
- What if n is 10⁹ but k is small? → Use a min-heap of size k
- Worst case for quick select? → O(n²) but random pivot makes it practically O(n)

---

### Problem 3: Merge Intervals (LeetCode #56)

**Clarifying Questions:**
- Are intervals guaranteed non-empty? → Yes
- Can two intervals share an endpoint (e.g., [1,4] and [4,5])? → Yes, merge them
- Is input sorted? → No
- Return any order? → Yes

**Brute Force:** Compare every pair of intervals, merge if overlapping. O(n²).

**Optimization:** Sort by start time, then linear scan — O(n log n) dominated by sort.

**Edge Cases:**
- Single interval → return it unchanged
- No overlaps → return sorted input
- All intervals overlap → return single merged interval
- Interval completely contained in another → [1,10] contains [2,5]

**Code:**
```python
def merge(intervals):
    intervals.sort(key=lambda x: x[0])  # Sort by start
    merged = [intervals[0]]
    
    for start, end in intervals[1:]:
        last_end = merged[-1][1]
        if start <= last_end:           # Overlap: start ≤ previous end
            merged[-1][1] = max(last_end, end)  # Extend if needed
        else:
            merged.append([start, end])
    
    return merged
```

**Follow-ups:**
- Insert a new interval into an already-merged list? → LeetCode #57, binary search for position
- Find total coverage length after merging? → Sum of (end - start) for merged intervals
- What if 3D intervals (time + room)? → Greedy with priority queue (meeting rooms II)

---

## Common Mistakes

**1. QuickSort worst case on sorted input**
```python
# BAD: Always pick last element as pivot
pivot = arr[hi]  # O(n²) if array is sorted/reverse-sorted

# GOOD: Random pivot
rand = random.randint(lo, hi)
arr[rand], arr[hi] = arr[hi], arr[rand]
pivot = arr[hi]
```

**2. Stability confusion**
Quick sort and heap sort are NOT stable. If you need stable sort, use merge sort.
```python
# Example: sorting (name, age) tuples by age
# Quick sort may reorder equal ages — merge sort won't
```

**3. Forgetting Counting Sort requires bounded integers**
```python
# BAD: Using counting sort on floats or large ranges
arr = [0.5, 1.5, 2.5]  # Can't index by float

# GOOD: Verify integer keys with small range (k << n)
```

**4. Off-by-one in merge/quick boundaries**
```python
# Common error in partition:
for j in range(lo, hi):    # hi is EXCLUSIVE (don't include pivot)
    ...
arr[i + 1], arr[hi] = arr[hi], arr[i + 1]  # Place pivot at i+1
```

**5. Not using <= in merge step**
```python
# BAD: < causes right to win ties, breaking stability
if left[i] < right[j]:

# GOOD: <= keeps left (earlier) element first, preserving stability
if left[i] <= right[j]:
```

**6. Heap sort heapify direction**
Build heap bottom-up starting from `n//2 - 1`, not from root — O(n) vs O(n log n).

---

## Interview Q&A

**Q1: Why does Python use Timsort instead of quicksort?**
Timsort is a hybrid (merge + insertion sort) that exploits natural runs in real data. It's stable, guarantees O(n log n) worst case, and performs O(n) on already-sorted data. Python prioritizes predictability and stability; quicksort's O(n²) worst case is unacceptable in a general-purpose language.

**Q2: When would you choose heap sort over merge sort?**
When memory is the constraint. Heap sort runs in O(n log n) time with O(1) extra space, while merge sort needs O(n). For embedded systems or when sorting very large arrays close to memory limits, heap sort wins. Tradeoff: heap sort has poor cache locality, so in practice merge sort is often faster despite the memory cost.

**Q3: What makes quicksort cache-friendly?**
Quicksort accesses elements sequentially within partitions, so data stays in CPU cache. Heap sort jumps between parent/child positions (indices i, 2i+1, 2i+2), causing frequent cache misses on large arrays. On modern hardware, quicksort is typically 2-3x faster than heap sort despite the same asymptotic complexity.

**Q4: Can you make quicksort O(n log n) worst case?**
Yes: use median-of-three or introselect pivot selection, or switch to heapsort when recursion depth exceeds 2 log n (this is "introsort," used by C++ std::sort). Alternatively, randomized pivot gives O(n log n) expected with negligible probability of worst case.

**Q5: How would you sort 1 billion integers that don't fit in memory?**
External merge sort: divide data into chunks that fit in RAM, sort each chunk, write to disk, then k-way merge the sorted chunks. This requires k file handles and a min-heap of size k to merge efficiently. Total I/O: O(n/B) passes where B is block size.

**Q6: Given an array of 0s, 1s, and 2s, sort it in O(n) time and O(1) space.**
Dutch National Flag algorithm (3-way partition). Maintain three pointers: lo (boundary of 0s), mid (current), hi (boundary of 2s). Scan mid left to right, swap 0s to lo and 2s to hi. This is the 3-way partition used to optimize quicksort on arrays with many duplicates.

```python
def sort_colors(nums):
    lo, mid, hi = 0, 0, len(nums) - 1
    while mid <= hi:
        if nums[mid] == 0:
            nums[lo], nums[mid] = nums[mid], nums[lo]
            lo += 1; mid += 1
        elif nums[mid] == 1:
            mid += 1
        else:
            nums[mid], nums[hi] = nums[hi], nums[mid]
            hi -= 1
```

**Q7: Why is merge sort preferred for linked lists?**
Linked lists don't support O(1) random access, so algorithms that index (quicksort, heapsort) require O(n) per access — killing their performance. Merge sort only needs sequential access (find midpoint via slow/fast pointer, then merge). Split and merge on linked lists are O(1) pointer operations, making merge sort truly O(n log n) without extra memory.

**Q8: What's the lower bound for comparison-based sorting?**
Ω(n log n). Any comparison-based sort must distinguish between n! permutations, requiring at least log₂(n!) comparisons. By Stirling's approximation, log₂(n!) ≈ n log₂ n. This is a theoretical lower bound — counting/radix sort bypass it by not using comparisons.
