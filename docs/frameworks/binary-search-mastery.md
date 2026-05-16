# Binary Search Mastery: Searching, Boundaries, and Variants

Master binary search patterns for efficient searching and finding boundaries.

---

## Standard Binary Search

```python
def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return -1  # Not found

# Time: O(log n), Space: O(1)
```

**Key Points:**
- `left <= right` (inclusive)
- `mid = (left + right) // 2` (avoid overflow in other languages)
- Three cases: found, go right, go left

---

## Finding Boundaries

### Find First Position (Lower Bound)

```python
def find_first(arr, target):
    left, right = 0, len(arr)
    
    while left < right:
        mid = (left + right) // 2
        if arr[mid] < target:
            left = mid + 1
        else:
            right = mid
    
    return left if left < len(arr) and arr[left] == target else -1

# Returns index of first occurrence or -1
# [1, 1, 1, 2, 2, 3] → find_first(2) = 3
```

### Find Last Position (Upper Bound)

```python
def find_last(arr, target):
    left, right = 0, len(arr)
    
    while left < right:
        mid = (left + right) // 2
        if arr[mid] <= target:
            left = mid + 1
        else:
            right = mid
    
    return left - 1 if left > 0 and arr[left - 1] == target else -1

# Returns index of last occurrence or -1
# [1, 1, 1, 2, 2, 3] → find_last(2) = 4
```

---

## Binary Search Variants

### Search in Rotated Sorted Array

```python
def search_rotated(arr, target):
    left, right = 0, len(arr) - 1
    
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        
        # Left half is sorted
        if arr[left] <= arr[mid]:
            if arr[left] <= target < arr[mid]:
                right = mid - 1
            else:
                left = mid + 1
        # Right half is sorted
        else:
            if arr[mid] < target <= arr[right]:
                left = mid + 1
            else:
                right = mid - 1
    
    return -1

# [4,5,6,7,0,1,2] → find 0: check which half is sorted, then recurse
```

### Search in Unknown Size Array

```python
def search_unknown_size(reader, target):
    # First, find the right boundary (exponential search)
    left, right = 0, 1
    while reader.get(right) < target:
        left = right
        right *= 2
    
    # Now do binary search in [left, right]
    while left <= right:
        mid = (left + right) // 2
        if reader.get(mid) == target:
            return mid
        elif reader.get(mid) < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return -1

# Time: O(log n), Space: O(1)
```

### Find Peak Element

```python
def find_peak(arr):
    left, right = 0, len(arr) - 1
    
    while left < right:
        mid = (left + right) // 2
        if arr[mid] > arr[mid + 1]:
            right = mid  # Peak is in left half (including mid)
        else:
            left = mid + 1  # Peak is in right half
    
    return left

# [1,2,3,1] → 3 is peak (index 2)
# [1,2,1,2,1] → could be 2 (index 1 or 3)
```

### Sqrt Using Binary Search

```python
def my_sqrt(x):
    if x == 0:
        return 0
    
    left, right = 1, x
    
    while left <= right:
        mid = (left + right) // 2
        if mid * mid == x:
            return mid
        elif mid * mid < x:
            left = mid + 1
        else:
            right = mid - 1
    
    return right  # Return floor of sqrt

# my_sqrt(8) = 2 (since 2² < 8 < 3²)
```

---

## Binary Search Patterns

| Problem | Pattern | Key Insight |
|---------|---------|-----------|
| Find exact value | Standard | Three cases: ==, <, > |
| Find first position | Left boundary | `arr[mid] < target` → `left = mid + 1` |
| Find last position | Right boundary | `arr[mid] <= target` → `left = mid + 1` |
| Find in rotated | Check sorted half | One half always sorted |
| Find peak | Compare with neighbor | Peak has arr[i] > arr[i+1] |
| Find in unknown size | Exponential then binary | Find boundary, then search |

---

## Edge Cases

```python
def test_binary_search():
    # Empty array
    assert binary_search([], 5) == -1
    
    # Single element
    assert binary_search([5], 5) == 0
    assert binary_search([5], 1) == -1
    
    # Target not in array
    assert binary_search([1,3,5], 4) == -1
    
    # Target at boundaries
    assert binary_search([1,3,5], 1) == 0
    assert binary_search([1,3,5], 5) == 2
    
    # Duplicates (find first vs last)
    assert find_first([1,1,1,2,2,3], 1) == 0
    assert find_last([1,1,1,2,2,3], 1) == 2
```

---

## Binary Search Checklist

- ✓ Verified array is sorted (or has sortable property)
- ✓ Chose correct variant (standard, boundary, rotation, etc.)
- ✓ Loop condition: `<=` or `<` ?
- ✓ Mid calculation: `(left + right) // 2`
- ✓ Handled edge cases (empty, one element, target not found)
- ✓ Time complexity O(log n)
- ✓ Tested on small examples

