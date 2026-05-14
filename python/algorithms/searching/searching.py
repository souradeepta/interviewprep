"""
searching.py — Complete searching algorithm implementations for SDE interview prep.

Algorithms included:
    1. binary_search           — O(log n), iterative
    2. binary_search_recursive — O(log n), recursive
    3. binary_search_first     — O(log n), find first occurrence
    4. binary_search_last      — O(log n), find last occurrence
    5. search_rotated_array    — O(log n), search in rotated sorted array
    6. find_peak               — O(log n), find any peak element
    7. ternary_search          — O(log₃ n), divide search space into thirds
    8. exponential_search      — O(log n), for unknown-size or large arrays
    9. interpolation_search    — O(log log n) avg for uniform data

All functions assume 0-indexed lists. Functions that require sorted input
document this requirement in their docstring.

Usage:
    python searching.py    # runs the full demo block
"""

from typing import List, Optional


# ---------------------------------------------------------------------------
# 1. Binary Search — Iterative
# ---------------------------------------------------------------------------

def binary_search(arr: List[int], target: int) -> int:
    """
    Binary Search (iterative) — repeatedly halve the search space by comparing
    the target with the middle element.

    Precondition: `arr` must be sorted in ascending order.

    Time Complexity:
        Best    : O(1)      — target is at the midpoint
        Average : O(log n)
        Worst   : O(log n)

    Space Complexity: O(1) — no extra space (iterative)

    Args:
        arr   : Sorted list of comparable elements.
        target: The value to search for.

    Returns:
        Index of `target` in `arr`, or -1 if not found.
        If duplicates exist, returns an arbitrary matching index (use
        binary_search_first / binary_search_last for deterministic results).

    Interview Notes:
        - Classic divide-and-conquer reduction; each step cuts the remaining
          search space in half → log₂(n) steps.
        - Off-by-one errors are the most common mistake. The invariant:
              arr[lo] <= target <= arr[hi]
          must hold throughout. Use lo <= hi (not lo < hi) so a single-element
          array is still checked.
        - Overflow-safe midpoint: mid = lo + (hi - lo) // 2
          (avoids integer overflow in languages like Java/C++ with fixed-width int).
    """
    lo, hi = 0, len(arr) - 1

    while lo <= hi:
        mid = lo + (hi - lo) // 2   # overflow-safe

        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            lo = mid + 1             # target must be in right half
        else:
            hi = mid - 1             # target must be in left half

    return -1   # not found


# ---------------------------------------------------------------------------
# 2. Binary Search — Recursive
# ---------------------------------------------------------------------------

def binary_search_recursive(arr: List[int], target: int,
                             lo: int = 0, hi: int = -1) -> int:
    """
    Binary Search (recursive) — same logic as the iterative version but
    expressed through recursive calls.

    Precondition: `arr` must be sorted in ascending order.

    Time Complexity:
        Best    : O(1)      — target found at first midpoint
        Average : O(log n)
        Worst   : O(log n)
        Recurrence: T(n) = T(n/2) + O(1) → O(log n) by Master Theorem

    Space Complexity: O(log n) — recursive call stack depth

    Args:
        arr   : Sorted list of comparable elements.
        target: The value to search for.
        lo    : Lower bound of current search range (default 0).
        hi    : Upper bound of current search range (default len(arr)-1).

    Returns:
        Index of `target` in `arr`, or -1 if not found.

    Interview Notes:
        - Functionally identical to iterative but uses O(log n) stack space.
        - Python has a default recursion limit of 1000; for very large arrays
          use the iterative version.
        - The default hi=-1 sentinel lets callers omit the argument while
          still supporting sub-range searches.
    """
    if hi == -1:                 # handle default argument (can't use len(arr)-1 directly)
        hi = len(arr) - 1

    if lo > hi:
        return -1                # base case: search space exhausted

    mid = lo + (hi - lo) // 2

    if arr[mid] == target:
        return mid
    elif arr[mid] < target:
        return binary_search_recursive(arr, target, mid + 1, hi)
    else:
        return binary_search_recursive(arr, target, lo, mid - 1)


# ---------------------------------------------------------------------------
# 3. Binary Search — First Occurrence
# ---------------------------------------------------------------------------

def binary_search_first(arr: List[int], target: int) -> int:
    """
    Binary Search — First Occurrence.

    Finds the leftmost (first) index where `target` appears in a sorted array.
    Handles duplicates correctly by continuing to search left even after a match.

    Precondition: `arr` must be sorted in ascending order.

    Time Complexity : O(log n)
    Space Complexity: O(1)

    Args:
        arr   : Sorted list (may contain duplicates).
        target: The value to search for.

    Returns:
        The smallest index i such that arr[i] == target, or -1 if not found.

    Example:
        arr = [1, 2, 2, 2, 3, 4]
        binary_search_first(arr, 2) → 1   (not 2 or 3)

    Interview Notes:
        - Key insight: when arr[mid] == target, don't return immediately.
          Record the candidate position and continue searching LEFT (hi = mid - 1)
          to see if there is an earlier occurrence.
        - This pattern extends to "find first element >= target" (lower_bound
          in C++) by changing the equality condition.
        - Lower bound variant: replace `arr[mid] == target` with `arr[mid] >= target`
          and always continue left — gives the insertion point.
    """
    lo, hi = 0, len(arr) - 1
    result = -1

    while lo <= hi:
        mid = lo + (hi - lo) // 2

        if arr[mid] == target:
            result = mid         # record match; continue searching left
            hi = mid - 1
        elif arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1

    return result


# ---------------------------------------------------------------------------
# 4. Binary Search — Last Occurrence
# ---------------------------------------------------------------------------

def binary_search_last(arr: List[int], target: int) -> int:
    """
    Binary Search — Last Occurrence.

    Finds the rightmost (last) index where `target` appears in a sorted array.

    Precondition: `arr` must be sorted in ascending order.

    Time Complexity : O(log n)
    Space Complexity: O(1)

    Args:
        arr   : Sorted list (may contain duplicates).
        target: The value to search for.

    Returns:
        The largest index i such that arr[i] == target, or -1 if not found.

    Example:
        arr = [1, 2, 2, 2, 3, 4]
        binary_search_last(arr, 2) → 3   (not 1 or 2)

    Interview Notes:
        - Mirror of binary_search_first: when arr[mid] == target, record the
          candidate and search RIGHT (lo = mid + 1).
        - Together, first and last occurrence give you the count of a value:
              count = last - first + 1   (when first != -1)
        - Upper bound variant: find first element > target by replacing
          `arr[mid] == target` with `arr[mid] > target`.
    """
    lo, hi = 0, len(arr) - 1
    result = -1

    while lo <= hi:
        mid = lo + (hi - lo) // 2

        if arr[mid] == target:
            result = mid         # record match; continue searching right
            lo = mid + 1
        elif arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1

    return result


# ---------------------------------------------------------------------------
# 5. Search in Rotated Sorted Array
# ---------------------------------------------------------------------------

def search_rotated_array(arr: List[int], target: int) -> int:
    """
    Search in Rotated Sorted Array — O(log n).

    A sorted array has been rotated at some unknown pivot point.
    For example: [4, 5, 6, 7, 0, 1, 2] is [0,1,2,4,5,6,7] rotated at index 4.

    Key insight: at every midpoint, at least one half of the array is
    guaranteed to be sorted. Use this to determine which half to search.

    Precondition: Array was originally sorted ascending and rotated once.
                  All elements are distinct.

    Time Complexity : O(log n)
    Space Complexity: O(1)

    Args:
        arr   : Rotated sorted array with distinct elements.
        target: The value to search for.

    Returns:
        Index of `target`, or -1 if not found.

    Example:
        arr = [4, 5, 6, 7, 0, 1, 2], target = 0 → 4
        arr = [4, 5, 6, 7, 0, 1, 2], target = 3 → -1

    Algorithm:
        if arr[lo] <= arr[mid]:    # left half is sorted
            if arr[lo] <= target < arr[mid]:
                search left half
            else:
                search right half
        else:                      # right half is sorted
            if arr[mid] < target <= arr[hi]:
                search right half
            else:
                search left half

    Interview Notes:
        - LeetCode 33. Commonly asked at FAANG.
        - The key insight is checking which half is sorted (not which has target).
        - With duplicates (LeetCode 81): add a case for arr[lo] == arr[mid] == arr[hi]
          → shrink both ends: lo++, hi-- → degrades to O(n) worst case.
    """
    lo, hi = 0, len(arr) - 1

    while lo <= hi:
        mid = lo + (hi - lo) // 2

        if arr[mid] == target:
            return mid

        if arr[lo] <= arr[mid]:          # left half [lo..mid] is sorted
            if arr[lo] <= target < arr[mid]:
                hi = mid - 1             # target in sorted left half
            else:
                lo = mid + 1             # target in right half
        else:                            # right half [mid..hi] is sorted
            if arr[mid] < target <= arr[hi]:
                lo = mid + 1             # target in sorted right half
            else:
                hi = mid - 1             # target in left half

    return -1


# ---------------------------------------------------------------------------
# 6. Find Peak Element
# ---------------------------------------------------------------------------

def find_peak(arr: List[int]) -> int:
    """
    Find Peak Element — O(log n).

    A peak element is one that is strictly greater than its neighbours.
    arr[-1] and arr[n] are treated as -infinity (boundaries are never peaks
    unless the neighbour condition is met with the real elements).

    Observation: if arr[mid] < arr[mid+1], there must be a peak to the RIGHT
    of mid (the values are increasing; either arr[mid+1] is a peak or there's
    a higher peak further right). Similarly if arr[mid] < arr[mid-1], a peak
    exists to the LEFT.

    This lets us binary-search for a peak without knowing the full structure.

    Time Complexity : O(log n)
    Space Complexity: O(1)

    Args:
        arr: List of integers (adjacent elements are distinct).

    Returns:
        Index of any peak element.
        If multiple peaks exist, returns the index of one of them.

    Example:
        arr = [1, 2, 3, 1]    → 2  (arr[2]=3 is a peak)
        arr = [1, 2, 1, 3, 5] → 1 or 4  (multiple peaks; either valid)

    Interview Notes:
        - LeetCode 162. Classic O(log n) on unsorted array.
        - The trick: we don't need the global maximum; any local maximum qualifies.
        - Proof of correctness: the "climb toward increasing side" invariant
          guarantees we never rule out all peaks from the search space.
        - Can be extended to 2D matrices (LeetCode 1901).
    """
    lo, hi = 0, len(arr) - 1

    while lo < hi:
        mid = lo + (hi - lo) // 2

        if arr[mid] < arr[mid + 1]:
            lo = mid + 1       # ascending slope → peak is to the right
        else:
            hi = mid           # descending slope → peak is at mid or to the left

    # lo == hi; this element is a peak
    return lo


# ---------------------------------------------------------------------------
# 7. Ternary Search
# ---------------------------------------------------------------------------

def ternary_search(arr: List[int], target: int) -> int:
    """
    Ternary Search — divide the search space into THREE equal parts instead
    of two, ruling out one-third at each step.

    Precondition: `arr` must be sorted in ascending order.

    Time Complexity:
        Best    : O(1)
        Average : O(log₃ n) = O(log n / log 3)
        Worst   : O(log₃ n)

    Note: Despite dividing into thirds, ternary search is NOT faster than
    binary search in practice:
        Binary search: each step requires 1 comparison, eliminates n/2.
        Ternary search: each step requires 2 comparisons, eliminates 2n/3.
        Binary after k steps: n/2^k comparisons needed → k = log₂(n) steps
        Ternary after k steps: n/(3/2)^k → k = log_{3/2}(n) ≈ 1.71 log₂(n) steps
        Total comparisons: binary: log₂(n), ternary: 2 * 1.71 log₂(n)/log₂(3) ≈ 2.16 log₂(n)
        Binary wins by ~2x in comparisons!

    Space Complexity: O(1)

    Args:
        arr   : Sorted list of comparable elements.
        target: The value to search for.

    Returns:
        Index of `target`, or -1 if not found.

    Interview Notes:
        - Ternary search IS useful for finding the maximum of a unimodal
          (single-peaked) function, where binary search doesn't directly apply.
        - Not preferred over binary search for sorted-array lookup.
        - The analysis above is a common interview follow-up question.
    """
    lo, hi = 0, len(arr) - 1

    while lo <= hi:
        third = (hi - lo) // 3
        mid1 = lo + third
        mid2 = hi - third

        if arr[mid1] == target:
            return mid1
        if arr[mid2] == target:
            return mid2

        if target < arr[mid1]:
            hi = mid1 - 1           # target in left third
        elif target > arr[mid2]:
            lo = mid2 + 1           # target in right third
        else:
            lo = mid1 + 1           # target in middle third
            hi = mid2 - 1

    return -1


# ---------------------------------------------------------------------------
# 8. Exponential Search
# ---------------------------------------------------------------------------

def exponential_search(arr: List[int], target: int) -> int:
    """
    Exponential Search (also called doubling search or Struzik search) —
    find a range [2^(k-1), 2^k) that contains the target using exponential
    jumps, then apply binary search within that range.

    Precondition: `arr` must be sorted in ascending order.

    Time Complexity:
        Best    : O(1)      — target is at index 0
        Average : O(log n)
        Worst   : O(log n)
        — finding the range: O(log i) where i is the target's index
        — binary search within range: O(log i)
        — total: O(log i) ≤ O(log n)

    Space Complexity: O(1)

    Args:
        arr   : Sorted list of comparable elements.
        target: The value to search for.

    Returns:
        Index of `target`, or -1 if not found.

    Interview Notes:
        - Advantages over plain binary search:
            1. Works when array size is unknown (e.g., sorted stream or file).
            2. Faster than binary search when the element is near the beginning
               (O(log i) instead of O(log n)).
        - Useful for unbounded / infinite sorted arrays.
        - The range-finding phase doubles the index each step, so it reaches
          position i in ⌈log₂(i)⌉ steps.
    """
    n = len(arr)
    if n == 0:
        return -1
    if arr[0] == target:
        return 0

    # Find range for binary search by repeated doubling
    bound = 1
    while bound < n and arr[bound] <= target:
        bound *= 2

    # Binary search in arr[bound//2 .. min(bound, n-1)]
    lo = bound // 2
    hi = min(bound, n - 1)
    return _binary_search_range(arr, target, lo, hi)


def _binary_search_range(arr: List[int], target: int,
                          lo: int, hi: int) -> int:
    """Standard binary search restricted to arr[lo..hi]."""
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1


# ---------------------------------------------------------------------------
# 9. Interpolation Search
# ---------------------------------------------------------------------------

def interpolation_search(arr: List[int], target: int) -> int:
    """
    Interpolation Search — improvement over binary search for uniformly
    distributed sorted data. Instead of always probing the midpoint, estimate
    the probable position of the target using linear interpolation (like how
    humans search a phone book — if looking for "Smith," you open near the end).

    Probe formula:
        pos = lo + (target - arr[lo]) * (hi - lo) // (arr[hi] - arr[lo])

    This estimates where the target would fall if values were uniformly spread
    between arr[lo] and arr[hi].

    Precondition: `arr` must be sorted in ascending order.

    Time Complexity:
        Best    : O(1)
        Average : O(log log n)  — for uniformly distributed data
        Worst   : O(n)          — for exponentially distributed data
                                  (each probe eliminates only 1 element)

    Space Complexity: O(1)

    Args:
        arr   : Sorted list of integers (works best with uniform distribution).
        target: The value to search for.

    Returns:
        Index of `target`, or -1 if not found.

    Example:
        arr = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        target = 70
        pos = 0 + (70 - 10) * (9 - 0) // (100 - 10) = 0 + 60*9//90 = 6
        arr[6] = 70 → found in ONE step instead of several.

    Interview Notes:
        - O(log log n) is theoretically faster than O(log n) but requires
          uniform distribution — a strong assumption rarely guaranteed.
        - Worst case O(n) makes it unsuitable when data distribution is unknown.
        - Guard against division by zero: arr[lo] == arr[hi] (all remaining
          elements equal).
        - Practical use: searching very large sorted tables of uniform numeric
          keys (e.g., timestamps at regular intervals).
    """
    lo, hi = 0, len(arr) - 1

    while lo <= hi and arr[lo] <= target <= arr[hi]:
        if arr[lo] == arr[hi]:
            # All remaining elements are equal; check directly
            if arr[lo] == target:
                return lo
            return -1

        # Interpolation probe
        pos = lo + (target - arr[lo]) * (hi - lo) // (arr[hi] - arr[lo])

        # Clamp to valid range (in case of non-uniform distribution)
        pos = max(lo, min(hi, pos))

        if arr[pos] == target:
            return pos
        elif arr[pos] < target:
            lo = pos + 1
        else:
            hi = pos - 1

    return -1


# ---------------------------------------------------------------------------
# Demo / __main__
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 65)
    print("  Searching Algorithms — SDE Interview Prep Demo")
    print("=" * 65)

    # ---- Basic binary search ------------------------------------------------
    sorted_arr = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19]
    print(f"\nSorted array: {sorted_arr}")

    for target, expected_idx in [(7, 3), (1, 0), (19, 9), (4, -1), (20, -1)]:
        idx_iter = binary_search(sorted_arr, target)
        idx_rec  = binary_search_recursive(sorted_arr, target)
        ok = "[PASS]" if idx_iter == expected_idx and idx_rec == expected_idx else "[FAIL]"
        print(f"  binary_search({target:>2}) → iterative={idx_iter:>2}, "
              f"recursive={idx_rec:>2}  (expected {expected_idx:>2})  {ok}")

    # ---- First and last occurrence ------------------------------------------
    dup_arr = [1, 2, 2, 2, 3, 3, 4, 5]
    print(f"\nArray with duplicates: {dup_arr}")

    cases = [
        (2, 1, 3),
        (3, 4, 5),
        (1, 0, 0),
        (5, 7, 7),
        (6, -1, -1),
    ]
    for target, exp_first, exp_last in cases:
        first = binary_search_first(dup_arr, target)
        last  = binary_search_last(dup_arr, target)
        ok_f = "[PASS]" if first == exp_first else "[FAIL]"
        ok_l = "[PASS]" if last  == exp_last  else "[FAIL]"
        print(f"  target={target}: first={first} {ok_f}  last={last} {ok_l}")

    # ---- Rotated sorted array -----------------------------------------------
    rotated = [4, 5, 6, 7, 0, 1, 2]
    print(f"\nRotated sorted array: {rotated}")

    for target, expected in [(0, 4), (3, -1), (7, 3), (4, 0), (2, 6)]:
        idx = search_rotated_array(rotated, target)
        ok = "[PASS]" if idx == expected else "[FAIL]"
        print(f"  search_rotated_array({target}) → {idx}  (expected {expected})  {ok}")

    # ---- Find peak ----------------------------------------------------------
    peak_cases = [
        ([1, 2, 3, 1],    2),
        ([1, 2, 1, 3, 5], None),   # 1 or 4 both valid
        ([5, 4, 3, 2, 1], 0),
        ([1],             0),
    ]
    print(f"\nFind Peak Element:")
    for arr, expected in peak_cases:
        idx = find_peak(arr)
        if expected is None:
            # Any peak is valid; verify it satisfies the peak condition
            n = len(arr)
            is_peak = (
                (idx == 0 or arr[idx - 1] < arr[idx]) and
                (idx == n - 1 or arr[idx + 1] < arr[idx])
            )
            ok = "[PASS]" if is_peak else "[FAIL]"
            print(f"  find_peak({arr}) → idx={idx}  val={arr[idx]}  {ok} (any peak valid)")
        else:
            ok = "[PASS]" if idx == expected else "[FAIL]"
            print(f"  find_peak({arr}) → idx={idx}  (expected {expected})  {ok}")

    # ---- Ternary search -----------------------------------------------------
    sorted_arr2 = list(range(0, 40, 2))   # [0, 2, 4, ..., 38]
    print(f"\nTernary Search on {sorted_arr2}:")
    for target, expected in [(10, 5), (0, 0), (38, 19), (7, -1)]:
        idx = ternary_search(sorted_arr2, target)
        ok = "[PASS]" if idx == expected else "[FAIL]"
        print(f"  ternary_search({target:>2}) → {idx:>2}  (expected {expected:>2})  {ok}")

    # ---- Exponential search -------------------------------------------------
    large_sorted = list(range(1, 1001))   # 1..1000
    print(f"\nExponential Search on [1..1000]:")
    for target, expected in [(1, 0), (500, 499), (1000, 999), (0, -1), (1001, -1)]:
        idx = exponential_search(large_sorted, target)
        ok = "[PASS]" if idx == expected else "[FAIL]"
        print(f"  exponential_search({target:>4}) → {idx:>4}  (expected {expected:>4})  {ok}")

    # ---- Interpolation search -----------------------------------------------
    uniform = list(range(10, 110, 10))   # [10, 20, 30, ..., 100]
    print(f"\nInterpolation Search on {uniform}:")
    for target, expected in [(10, 0), (70, 6), (100, 9), (55, -1)]:
        idx = interpolation_search(uniform, target)
        ok = "[PASS]" if idx == expected else "[FAIL]"
        print(f"  interpolation_search({target:>3}) → {idx:>2}  (expected {expected:>2})  {ok}")

    # ---- Complexity Summary -------------------------------------------------
    print("\n" + "=" * 65)
    print("  Complexity Summary")
    print("=" * 65)
    rows = [
        ("Algorithm",               "Best",       "Avg",          "Worst",    "Space"),
        ("-" * 22,                  "-" * 10,     "-" * 14,       "-" * 8,    "-" * 8),
        ("binary_search (iter)",    "O(1)",       "O(log n)",     "O(log n)", "O(1)"),
        ("binary_search (recur)",   "O(1)",       "O(log n)",     "O(log n)", "O(log n)"),
        ("binary_search_first",     "O(1)",       "O(log n)",     "O(log n)", "O(1)"),
        ("binary_search_last",      "O(1)",       "O(log n)",     "O(log n)", "O(1)"),
        ("search_rotated_array",    "O(1)",       "O(log n)",     "O(log n)", "O(1)"),
        ("find_peak",               "O(1)",       "O(log n)",     "O(log n)", "O(1)"),
        ("ternary_search",          "O(1)",       "O(log₃ n)",    "O(log n)", "O(1)"),
        ("exponential_search",      "O(1)",       "O(log n)",     "O(log n)", "O(1)"),
        ("interpolation_search",    "O(1)",       "O(log log n)", "O(n)",     "O(1)"),
    ]
    for name, best, avg, worst, space in rows:
        print(f"  {name:<26} {best:<12} {avg:<16} {worst:<10} {space}")
