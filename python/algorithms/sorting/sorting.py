"""
sorting.py — Complete sorting algorithm implementations for SDE interview prep.

Algorithms included:
    1.  bubble_sort         — O(n²) time, O(1) space, stable, in-place
    2.  selection_sort      — O(n²) time, O(1) space, NOT stable, in-place
    3.  insertion_sort      — O(n²) worst / O(n) best, O(1) space, stable, in-place
    4.  merge_sort          — O(n log n) time, O(n) space, stable
    5.  quick_sort          — O(n log n) avg / O(n²) worst, O(log n) stack, NOT stable, in-place
    6.  heap_sort           — O(n log n) time, O(1) space, NOT stable, in-place
    7.  counting_sort       — O(n + k) time, O(k) space, stable, non-negative integers only
    8.  radix_sort          — O(d*(n+k)) time, O(n+k) space, stable, non-negative integers
    9.  bucket_sort         — O(n + k) avg time, O(n) space, stable, floats in [0, 1)
    10. tim_sort_demo       — O(n log n) time, O(n) space, stable (Python's built-in sort)

Usage:
    python sorting.py          # runs demo block
    python sorting.py compare  # runs timing comparison
"""

import random
import time
from typing import List


# ---------------------------------------------------------------------------
# 1. Bubble Sort
# ---------------------------------------------------------------------------

def bubble_sort(arr: List[int]) -> List[int]:
    """
    Bubble Sort — repeatedly swap adjacent elements that are out of order.

    Optimisation: early exit if no swaps occurred in a full pass (already sorted).

    Time Complexity:
        Best    : O(n)   — array already sorted, exits after first pass
        Average : O(n²)
        Worst   : O(n²)  — array reverse sorted

    Space Complexity: O(1) — in-place

    Stable: Yes

    Args:
        arr: List of comparable elements. Modified in-place.

    Returns:
        The same list, sorted in ascending order.

    Interview Notes:
        - Rarely used in production due to O(n²) average case.
        - The early-exit optimisation makes it O(n) on already-sorted input.
        - Good introductory algorithm to explain the concept of stability.
    """
    arr = arr[:]          # work on a copy to avoid mutating caller's list
    n = len(arr)
    for i in range(n - 1):
        swapped = False
        # After each pass the largest unsorted element bubbles to position n-1-i
        for j in range(n - 1 - i):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:          # early exit optimisation
            break
    return arr


# ---------------------------------------------------------------------------
# 2. Selection Sort
# ---------------------------------------------------------------------------

def selection_sort(arr: List[int]) -> List[int]:
    """
    Selection Sort — find the minimum element and place it at the front,
    then repeat for the remaining unsorted portion.

    Time Complexity:
        Best    : O(n²)
        Average : O(n²)
        Worst   : O(n²)
        — always performs exactly n*(n-1)/2 comparisons regardless of input order

    Space Complexity: O(1) — in-place

    Stable: No
        Example of instability: [3a, 3b, 1] → selects 1, swaps with 3a → [1, 3b, 3a]
        Relative order of equal elements (3a, 3b) is disturbed.

    Args:
        arr: List of comparable elements. Not modified in-place (copy returned).

    Returns:
        A new sorted list.

    Interview Notes:
        - Makes at most O(n) swaps, which is useful when write cost is high.
        - Not adaptive — same work regardless of how sorted the input is.
    """
    arr = arr[:]
    n = len(arr)
    for i in range(n - 1):
        min_idx = i
        for j in range(i + 1, n):
            if arr[j] < arr[min_idx]:
                min_idx = j
        if min_idx != i:
            arr[i], arr[min_idx] = arr[min_idx], arr[i]
    return arr


# ---------------------------------------------------------------------------
# 3. Insertion Sort
# ---------------------------------------------------------------------------

def insertion_sort(arr: List[int]) -> List[int]:
    """
    Insertion Sort — build the sorted portion one element at a time by
    inserting each new element into its correct position via backward shifting.

    Time Complexity:
        Best    : O(n)   — already sorted; inner loop never executes
        Average : O(n²)
        Worst   : O(n²)  — reverse sorted

    Space Complexity: O(1) — in-place

    Stable: Yes

    Args:
        arr: List of comparable elements.

    Returns:
        A new sorted list.

    Interview Notes:
        - Excellent for small arrays (n <= ~16) and nearly-sorted data.
        - Used as the base case in Tim Sort (Python's built-in) and intro sort.
        - Adaptive: O(n + k) where k = number of inversions.
        - Online algorithm: can sort a stream as elements arrive.
    """
    arr = arr[:]
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        # Shift elements that are greater than key one position to the right
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    return arr


# ---------------------------------------------------------------------------
# 4. Merge Sort
# ---------------------------------------------------------------------------

def merge_sort(arr: List[int]) -> List[int]:
    """
    Merge Sort — classic divide-and-conquer. Recursively split the array in
    half, sort each half, then merge the two sorted halves.

    Time Complexity:
        Best    : O(n log n)
        Average : O(n log n)
        Worst   : O(n log n)
        — Recurrence: T(n) = 2T(n/2) + O(n) → O(n log n) by Master Theorem

    Space Complexity: O(n) — auxiliary arrays used during merge step
                      O(log n) additional call stack space

    Stable: Yes — merge step preserves relative order of equal elements

    Args:
        arr: List of comparable elements.

    Returns:
        A new sorted list (does not mutate the input).

    Interview Notes:
        - Preferred when stability matters and extra memory is acceptable.
        - Efficient for linked lists (no random access required).
        - Basis of external sort algorithms (sorting data larger than RAM).
        - Python's built-in sort (Tim Sort) is a hybrid of merge sort and
          insertion sort.
    """
    if len(arr) <= 1:
        return arr[:]

    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return _merge(left, right)


def _merge(left: List[int], right: List[int]) -> List[int]:
    """Merge two sorted lists into one sorted list. O(n) time and space."""
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        # '<=' preserves stability (left element wins ties)
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result


# ---------------------------------------------------------------------------
# 5. Quick Sort (median-of-three pivot + 3-way partition variant)
# ---------------------------------------------------------------------------

def quick_sort(arr: List[int]) -> List[int]:
    """
    Quick Sort — partition the array around a pivot so elements smaller than
    the pivot come before it and larger elements come after, then recursively
    sort each partition.

    Pivot selection: Median-of-three (first, middle, last) to avoid worst-case
    O(n²) on sorted/reverse-sorted inputs.

    3-way partition variant (Dutch National Flag) handles arrays with many
    duplicates in O(n) for all-equal inputs instead of O(n²).

    Time Complexity:
        Best    : O(n log n)
        Average : O(n log n)
        Worst   : O(n²) — highly unlikely with median-of-three pivot
        — Recurrence (average): T(n) = 2T(n/2) + O(n)

    Space Complexity: O(log n) — call stack depth (average); O(n) worst case

    Stable: No

    Args:
        arr: List of comparable elements.

    Returns:
        A new sorted list.

    Interview Notes:
        - Typically 2-3x faster than merge sort in practice due to cache
          locality (in-place) and smaller constant factors.
        - Worst case avoided in practice via randomised or median-of-three pivot.
        - 3-way partition is essential when duplicates are common (e.g.,
          sorting by category with few unique values).
    """
    arr = arr[:]
    _quick_sort_3way(arr, 0, len(arr) - 1)
    return arr


def _median_of_three(arr: List[int], lo: int, hi: int) -> int:
    """Return the index of the median of arr[lo], arr[mid], arr[hi]."""
    mid = (lo + hi) // 2
    # Sort lo, mid, hi in-place so arr[mid] is the median
    if arr[lo] > arr[mid]:
        arr[lo], arr[mid] = arr[mid], arr[lo]
    if arr[lo] > arr[hi]:
        arr[lo], arr[hi] = arr[hi], arr[lo]
    if arr[mid] > arr[hi]:
        arr[mid], arr[hi] = arr[hi], arr[mid]
    # arr[lo] <= arr[mid] <= arr[hi]; median is at mid
    return mid


def _quick_sort_3way(arr: List[int], lo: int, hi: int) -> None:
    """
    3-way partition quick sort (Dutch National Flag partitioning).

    After partitioning:
        arr[lo..lt-1]  < pivot
        arr[lt..gt]   == pivot
        arr[gt+1..hi]  > pivot

    This makes the algorithm O(n) when all elements are equal and efficient
    for inputs with many repeated keys.
    """
    if lo >= hi:
        return

    # Median-of-three pivot selection
    pivot_idx = _median_of_three(arr, lo, hi)
    pivot = arr[pivot_idx]

    # 3-way partition
    lt = lo          # arr[lo..lt-1] < pivot
    gt = hi          # arr[gt+1..hi] > pivot
    i = lo           # current element

    while i <= gt:
        if arr[i] < pivot:
            arr[lt], arr[i] = arr[i], arr[lt]
            lt += 1
            i += 1
        elif arr[i] > pivot:
            arr[gt], arr[i] = arr[i], arr[gt]
            gt -= 1
            # Do NOT increment i: newly swapped element needs examination
        else:
            i += 1

    _quick_sort_3way(arr, lo, lt - 1)
    _quick_sort_3way(arr, gt + 1, hi)


# ---------------------------------------------------------------------------
# 6. Heap Sort
# ---------------------------------------------------------------------------

def heap_sort(arr: List[int]) -> List[int]:
    """
    Heap Sort — build a max-heap from the array, then repeatedly extract
    the maximum element to produce a sorted array.

    Phase 1 — Heapify: O(n) to build max-heap (not O(n log n); each sift-down
              is proportional to the subtree height, and summing over all nodes
              gives O(n)).
    Phase 2 — Extraction: O(n log n) — n extractions each costing O(log n).

    Time Complexity:
        Best    : O(n log n)
        Average : O(n log n)
        Worst   : O(n log n)

    Space Complexity: O(1) — in-place (heap is built within the input array)

    Stable: No — the heap extraction step can change relative order of equals

    Args:
        arr: List of comparable elements.

    Returns:
        A new sorted list.

    Interview Notes:
        - Combines guaranteed O(n log n) worst case with O(1) extra space.
        - Poor cache performance compared to quick sort (heap accesses are
          not sequential).
        - Used in intro sort (C++ std::sort) as the fallback when quick sort
          degrades.
    """
    arr = arr[:]
    n = len(arr)

    # Build max-heap: start from last non-leaf node and sift down
    for i in range(n // 2 - 1, -1, -1):
        _sift_down(arr, n, i)

    # Extract elements from heap one by one
    for end in range(n - 1, 0, -1):
        arr[0], arr[end] = arr[end], arr[0]   # move current max to end
        _sift_down(arr, end, 0)                # restore heap property

    return arr


def _sift_down(arr: List[int], heap_size: int, root: int) -> None:
    """
    Sift down the element at `root` to restore max-heap property.
    Only considers elements in arr[0..heap_size-1].
    """
    largest = root
    left = 2 * root + 1
    right = 2 * root + 2

    if left < heap_size and arr[left] > arr[largest]:
        largest = left
    if right < heap_size and arr[right] > arr[largest]:
        largest = right

    if largest != root:
        arr[root], arr[largest] = arr[largest], arr[root]
        _sift_down(arr, heap_size, largest)


# ---------------------------------------------------------------------------
# 7. Counting Sort
# ---------------------------------------------------------------------------

def counting_sort(arr: List[int]) -> List[int]:
    """
    Counting Sort — count occurrences of each value, compute prefix sums to
    determine positions, then place elements into output array.

    Constraints: elements must be non-negative integers.

    Time Complexity:
        Best/Avg/Worst : O(n + k)
        where n = number of elements, k = max value in the array.

    Space Complexity: O(n + k) — count array of size k+1, output array of size n

    Stable: Yes — iterating the input array in reverse during placement
                  preserves relative order of equal elements.

    Args:
        arr: List of non-negative integers.

    Returns:
        A new sorted list.

    Raises:
        ValueError: If any element is negative.

    Interview Notes:
        - O(n + k) makes it faster than comparison-based O(n log n) when k = O(n).
        - Impractical when k >> n (e.g., sorting 10 elements with max value 10^9
          would require a 10^9-element count array).
        - Used as the subroutine in radix sort.
    """
    if not arr:
        return []
    if min(arr) < 0:
        raise ValueError("counting_sort requires non-negative integers")

    k = max(arr)
    count = [0] * (k + 1)

    # Count occurrences
    for val in arr:
        count[val] += 1

    # Prefix sums: count[i] now holds the number of elements <= i
    for i in range(1, k + 1):
        count[i] += count[i - 1]

    # Build output in reverse to preserve stability
    output = [0] * len(arr)
    for val in reversed(arr):
        count[val] -= 1
        output[count[val]] = val

    return output


# ---------------------------------------------------------------------------
# 8. Radix Sort (LSD — Least Significant Digit first)
# ---------------------------------------------------------------------------

def radix_sort(arr: List[int]) -> List[int]:
    """
    Radix Sort (LSD) — sort by each digit from least significant to most
    significant, using counting sort as the stable subroutine at each digit.

    Time Complexity:
        O(d * (n + k))
        where d = number of digits in the maximum element,
              n = number of elements,
              k = base (10 for decimal).
        For 32-bit integers: d <= 10, k = 10 → effectively O(n).

    Space Complexity: O(n + k) per digit pass

    Stable: Yes (because counting sort is stable)

    Args:
        arr: List of non-negative integers.

    Returns:
        A new sorted list.

    Raises:
        ValueError: If any element is negative.

    Interview Notes:
        - Best when d is small relative to log(n), e.g., sorting phone numbers,
          IP addresses, or fixed-length strings.
        - LSD (right-to-left) is more common and simpler to implement stably
          than MSD (left-to-right).
        - Radix sort is NOT comparison-based so the Ω(n log n) lower bound does
          not apply.
    """
    if not arr:
        return []
    if min(arr) < 0:
        raise ValueError("radix_sort requires non-negative integers")

    arr = arr[:]
    max_val = max(arr)
    exp = 1   # current digit position: 1, 10, 100, ...

    while max_val // exp > 0:
        arr = _counting_sort_by_digit(arr, exp)
        exp *= 10

    return arr


def _counting_sort_by_digit(arr: List[int], exp: int) -> List[int]:
    """Stable counting sort on the digit at position exp (1, 10, 100, ...)."""
    n = len(arr)
    output = [0] * n
    count = [0] * 10   # digits 0-9

    for val in arr:
        digit = (val // exp) % 10
        count[digit] += 1

    for i in range(1, 10):
        count[i] += count[i - 1]

    for val in reversed(arr):
        digit = (val // exp) % 10
        count[digit] -= 1
        output[count[digit]] = val

    return output


# ---------------------------------------------------------------------------
# 9. Bucket Sort
# ---------------------------------------------------------------------------

def bucket_sort(arr: List[float]) -> List[float]:
    """
    Bucket Sort — distribute elements into a fixed number of equally-spaced
    buckets, sort each bucket (using insertion sort), then concatenate.

    Designed for uniformly distributed floats in [0, 1).

    Time Complexity:
        Best/Average : O(n + k) ≈ O(n) when distribution is uniform
                       (each bucket has ~n/k elements; insertion sort on k
                       buckets of size n/k is k * O((n/k)²) = O(n²/k);
                       with k = n this is O(n))
        Worst        : O(n²) — all elements fall into the same bucket

    Space Complexity: O(n + k) — k buckets containing n elements total

    Stable: Yes (insertion sort is stable)

    Args:
        arr: List of floats in the range [0, 1).

    Returns:
        A new sorted list.

    Raises:
        ValueError: If any element is outside [0, 1).

    Interview Notes:
        - O(n) average case depends on uniform distribution — degrades to O(n²)
          for skewed distributions.
        - Can be generalised to other ranges by normalisation.
        - Rarely used in practice but important for theoretical understanding.
    """
    if not arr:
        return []
    if not all(0.0 <= x < 1.0 for x in arr):
        raise ValueError("bucket_sort requires all elements in [0, 1)")

    n = len(arr)
    buckets: List[List[float]] = [[] for _ in range(n)]

    for val in arr:
        idx = int(val * n)
        idx = min(idx, n - 1)   # guard for val exactly == 1.0 (won't occur)
        buckets[idx].append(val)

    # Sort each bucket using insertion sort (efficient for small lists)
    result: List[float] = []
    for bucket in buckets:
        result.extend(_insertion_sort_generic(bucket))

    return result


def _insertion_sort_generic(arr):
    """In-place insertion sort that works on any comparable list."""
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    return arr


# ---------------------------------------------------------------------------
# 10. Tim Sort Demo
# ---------------------------------------------------------------------------

def tim_sort_demo(arr: List[int]) -> List[int]:
    """
    Tim Sort — Python's built-in sorting algorithm (used by list.sort() and
    sorted()). This function demonstrates the core idea conceptually and
    delegates to the real implementation.

    Algorithm Overview:
        Tim Sort is a hybrid of Insertion Sort and Merge Sort, designed for
        real-world data that often contains natural "runs" (already sorted
        sequences).

        1. Run Detection:
           Scan the input for natural runs (ascending or descending sequences).
           Descending runs are reversed in-place. Minimum run length (minrun)
           is between 32 and 64 chosen so that n/minrun is a power of 2.

        2. Run Extension (Insertion Sort):
           If a natural run is shorter than minrun, extend it using insertion
           sort until it reaches minrun length.

        3. Stack-based Merge:
           Push run boundaries onto a stack. After each push, maintain the
           invariant:
               |run[i-2]| > |run[i-1]| + |run[i]|   (Fibonacci-like)
               |run[i-1]| > |run[i]|
           Merge runs that violate the invariant. This produces a merge pattern
           that is balanced, ensuring O(n log n) total comparisons.

        4. Galloping Mode:
           During merge, if one side wins many comparisons in a row, switch to
           exponential search to skip large sections — excellent for partially
           sorted data.

    Time Complexity:
        Best    : O(n)        — already sorted (one run, no merges)
        Average : O(n log n)
        Worst   : O(n log n)

    Space Complexity: O(n) — temporary merge buffer

    Stable: Yes

    Args:
        arr: List of comparable elements.

    Returns:
        A new sorted list using Python's built-in Tim Sort.

    Interview Notes:
        - Tim Sort was invented by Tim Peters in 2002 for CPython.
        - It was later adopted by Java (for object arrays), Android, and V8.
        - The key insight: real-world data contains ordered sub-sequences;
          exploiting them gives near-linear performance on partially sorted data.
        - minrun ∈ [32, 64]: chosen so n/minrun ≤ next power of 2, making
          merge passes balanced.
    """
    # Conceptual demo: show insertion sort of a small run, then merge
    MIN_RUN = 32
    result = arr[:]

    def _demo_insertion_sort(a, lo, hi):
        """Sort a[lo:hi+1] in-place using insertion sort."""
        for i in range(lo + 1, hi + 1):
            key = a[i]
            j = i - 1
            while j >= lo and a[j] > key:
                a[j + 1] = a[j]
                j -= 1
            a[j + 1] = key

    def _demo_merge(a, lo, mid, hi):
        """Merge a[lo:mid+1] and a[mid+1:hi+1] in-place."""
        left = a[lo:mid + 1]
        right = a[mid + 1:hi + 1]
        i = j = 0
        k = lo
        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                a[k] = left[i]; i += 1
            else:
                a[k] = right[j]; j += 1
            k += 1
        while i < len(left):
            a[k] = left[i]; i += 1; k += 1
        while j < len(right):
            a[k] = right[j]; j += 1; k += 1

    n = len(result)

    # Step 1: Sort individual runs of size MIN_RUN using insertion sort
    for start in range(0, n, MIN_RUN):
        end = min(start + MIN_RUN - 1, n - 1)
        _demo_insertion_sort(result, start, end)

    # Step 2: Merge runs bottom-up
    size = MIN_RUN
    while size < n:
        for lo in range(0, n, size * 2):
            mid = min(lo + size - 1, n - 1)
            hi = min(lo + size * 2 - 1, n - 1)
            if mid < hi:
                _demo_merge(result, lo, mid, hi)
        size *= 2

    return result


# ---------------------------------------------------------------------------
# Comparison Runner
# ---------------------------------------------------------------------------

def sort_comparison(n: int = 5000) -> None:
    """
    Run all sorting algorithms on the same random integer array and print
    their wall-clock runtimes.

    Args:
        n: Size of the random array (default 5000).

    Note:
        bucket_sort operates on floats ∈ [0, 1) so it receives a separate
        float array of the same size.
    """
    int_arr = [random.randint(0, 10_000) for _ in range(n)]
    float_arr = [random.random() for _ in range(n)]

    algorithms = [
        ("bubble_sort",      lambda a: bubble_sort(a),     int_arr),
        ("selection_sort",   lambda a: selection_sort(a),  int_arr),
        ("insertion_sort",   lambda a: insertion_sort(a),  int_arr),
        ("merge_sort",       lambda a: merge_sort(a),      int_arr),
        ("quick_sort",       lambda a: quick_sort(a),      int_arr),
        ("heap_sort",        lambda a: heap_sort(a),       int_arr),
        ("counting_sort",    lambda a: counting_sort(a),   int_arr),
        ("radix_sort",       lambda a: radix_sort(a),      int_arr),
        ("bucket_sort",      lambda a: bucket_sort(a),     float_arr),
        ("tim_sort_demo",    lambda a: tim_sort_demo(a),   int_arr),
        ("sorted() builtin", lambda a: sorted(a),          int_arr),
    ]

    header = f"{'Algorithm':<20} {'Time (ms)':>12}  {'Array Size':>10}"
    print(header)
    print("-" * len(header))

    for name, fn, data in algorithms:
        start = time.perf_counter()
        result = fn(data)
        elapsed = (time.perf_counter() - start) * 1000
        # Correctness check
        expected = sorted(data)
        ok = "OK" if result == expected else "FAIL"
        print(f"{name:<20} {elapsed:>11.2f}ms  {n:>10}  [{ok}]")


# ---------------------------------------------------------------------------
# Demo / __main__
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "compare":
        print("\n=== Sorting Algorithm Comparison (n=5000) ===\n")
        sort_comparison(5000)
        sys.exit(0)

    print("=" * 60)
    print("  Sorting Algorithms — SDE Interview Prep Demo")
    print("=" * 60)

    sample = [64, 25, 12, 22, 11, 90, 3, 7, 55, 40]
    float_sample = [0.78, 0.17, 0.39, 0.26, 0.72, 0.94, 0.21, 0.12, 0.58, 0.65]

    print(f"\nInput (int):   {sample}")
    print(f"Input (float): {float_sample}")
    print()

    demos = [
        ("1. Bubble Sort",       bubble_sort(sample)),
        ("2. Selection Sort",    selection_sort(sample)),
        ("3. Insertion Sort",    insertion_sort(sample)),
        ("4. Merge Sort",        merge_sort(sample)),
        ("5. Quick Sort",        quick_sort(sample)),
        ("6. Heap Sort",         heap_sort(sample)),
        ("7. Counting Sort",     counting_sort(sample)),
        ("8. Radix Sort",        radix_sort(sample)),
        ("9. Bucket Sort",       bucket_sort(float_sample)),
        ("10. Tim Sort Demo",    tim_sort_demo(sample)),
    ]

    expected = sorted(sample)
    expected_f = sorted(float_sample)

    for label, result in demos:
        if "Bucket" in label:
            ok = "[PASS]" if result == expected_f else "[FAIL]"
            print(f"  {label:<22}: {result}  {ok}")
        else:
            ok = "[PASS]" if result == expected else "[FAIL]"
            print(f"  {label:<22}: {result}  {ok}")

    print()
    print("--- Stability Demonstration ---")
    # Show that bubble/insertion/merge sort preserve relative order of equals
    data = [(1, 'a'), (3, 'b'), (1, 'c'), (2, 'd'), (3, 'e')]
    keyed = [x[0] for x in data]
    print(f"Input:          {data}")
    # Manually stable sort by key
    stable_result = sorted(data, key=lambda x: x[0])
    print(f"Stable sorted:  {stable_result}")
    print("  (stable: equal keys maintain original left-to-right order)")

    print()
    print("--- Performance on Nearly-Sorted Array ---")
    nearly_sorted = list(range(100))
    nearly_sorted[50], nearly_sorted[51] = nearly_sorted[51], nearly_sorted[50]

    t0 = time.perf_counter()
    insertion_sort(nearly_sorted)
    t1 = time.perf_counter()
    print(f"  Insertion sort on 100-element nearly-sorted array: "
          f"{(t1-t0)*1e6:.1f} µs  (O(n) best case)")

    print()
    print("Run `python sorting.py compare` for a full timing comparison.")
