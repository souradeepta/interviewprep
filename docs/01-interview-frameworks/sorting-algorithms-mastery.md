# Sorting Algorithms Mastery: Time and Space Trade-offs

Master sorting algorithms and when to use each one.

---

## Sorting Algorithm Comparison

| Algorithm | Best | Average | Worst | Space | Stable | Notes |
|-----------|------|---------|-------|-------|--------|-------|
| **Bubble** | O(n) | O(n²) | O(n²) | O(1) | Yes | Simple, terrible |
| **Selection** | O(n²) | O(n²) | O(n²) | O(1) | No | Minimal swaps |
| **Insertion** | O(n) | O(n²) | O(n²) | O(1) | Yes | Best for nearly sorted |
| **Merge** | O(n log n) | O(n log n) | O(n log n) | O(n) | Yes | Stable, predictable |
| **Quick** | O(n log n) | O(n log n) | O(n²) | O(log n) | No | Fast, random |
| **Heap** | O(n log n) | O(n log n) | O(n log n) | O(1) | No | In-place, consistent |
| **Counting** | O(n+k) | O(n+k) | O(n+k) | O(k) | Yes | For integers only |
| **Radix** | O(nk) | O(nk) | O(nk) | O(n+k) | Yes | For integers, large k |

---

## Quick Sort Implementation

```python
def quicksort(arr):
    if len(arr) <= 1:
        return arr
    
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    
    return quicksort(left) + middle + quicksort(right)

# Time: O(n log n) average, O(n²) worst
# Space: O(n) for temp arrays
# Better: In-place quick sort with partition
```

### In-Place Quick Sort

```python
def quicksort_inplace(arr, low, high):
    if low < high:
        pi = partition(arr, low, high)
        quicksort_inplace(arr, low, pi - 1)
        quicksort_inplace(arr, pi + 1, high)

def partition(arr, low, high):
    pivot = arr[high]
    i = low - 1
    
    for j in range(low, high):
        if arr[j] < pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1

# Time: O(n log n) average, Space: O(log n) call stack
```

---

## Merge Sort Implementation

```python
def mergesort(arr):
    if len(arr) <= 1:
        return arr
    
    mid = len(arr) // 2
    left = mergesort(arr[:mid])
    right = mergesort(arr[mid:])
    
    return merge(left, right)

def merge(left, right):
    result = []
    i = j = 0
    
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    
    result.extend(left[i:])
    result.extend(right[j:])
    return result

# Time: O(n log n) guaranteed, Space: O(n)
# Stable, good for linked lists
```

---

## Counting Sort (For Integers)

```python
def counting_sort(arr, max_val):
    count = [0] * (max_val + 1)
    
    # Count occurrences
    for num in arr:
        count[num] += 1
    
    # Cumulative count
    for i in range(1, len(count)):
        count[i] += count[i - 1]
    
    # Place elements
    result = [0] * len(arr)
    for num in reversed(arr):  # Reversed for stability
        result[count[num] - 1] = num
        count[num] -= 1
    
    return result

# Time: O(n + k) where k = range of values
# Space: O(n + k)
# Only for non-negative integers or small range
```

---

## Choosing the Right Algorithm

### Use Quick Sort When:
- Average case matters (O(n log n) good enough)
- Space is limited (O(log n) stack)
- Generic sorting needed (default choice)

### Use Merge Sort When:
- Worst-case guarantee needed (O(n log n) always)
- Stability required (preserve order of equal elements)
- External sorting (data doesn't fit in RAM)

### Use Counting Sort When:
- Sorting integers with bounded range
- k (max value) is small relative to n
- Need O(n + k) linear time

### Use Heap Sort When:
- Need O(n log n) guaranteed
- Space is limited (O(1) extra)
- Don't need stability

### Use Insertion Sort When:
- Data nearly sorted (O(n) best case)
- Small arrays (< 50 elements)
- Online sorting (data arrives as you sort)

---

## 3-Way Quick Sort (For Duplicates)

```python
def quicksort_3way(arr, low, high):
    if low < high:
        lt, gt = partition_3way(arr, low, high)
        quicksort_3way(arr, low, lt - 1)
        quicksort_3way(arr, gt + 1, high)

def partition_3way(arr, low, high):
    pivot = arr[low]
    i = low
    lt = low
    gt = high + 1
    
    while i < gt:
        if arr[i] < pivot:
            arr[lt], arr[i] = arr[i], arr[lt]
            lt += 1
            i += 1
        elif arr[i] > pivot:
            gt -= 1
            arr[i], arr[gt] = arr[gt], arr[i]
        else:
            i += 1
    
    return lt, gt

# Time: O(n log n) average, O(n) if many duplicates
# Handles duplicates efficiently
```

---

## Sorting Checklist

- ✓ Chose right algorithm for problem
- ✓ Consider stability (equal elements order preserved)
- ✓ Consider space constraints
- ✓ Tested on edge cases (empty, one element, all same)
- ✓ Python: Use `sorted()` or `.sort()` (Timsort, O(n log n))
- ✓ Understood time/space complexity
- ✓ Know when each algorithm is optimal

