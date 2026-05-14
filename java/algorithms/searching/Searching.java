package algorithms.searching;

import java.util.Arrays;

/**
 * Comprehensive collection of searching algorithm implementations for SDE interview preparation.
 *
 * <p>All methods that operate on sorted arrays require the input to be sorted in ascending order.
 * Return value conventions follow Java's {@link java.util.Arrays#binarySearch}: a non-negative
 * index on success, or {@code -1} (or another sentinel) when the target is not found.
 *
 * <p>Summary of complexities (n = array length):
 * <pre>
 * Algorithm             | Time              | Space    | Requires Sorted
 * ----------------------+-------------------+----------+----------------
 * Binary Search (iter)  | O(log n)          | O(1)     | Yes
 * Binary Search (recur) | O(log n)          | O(log n) | Yes
 * Binary Search First   | O(log n)          | O(1)     | Yes
 * Binary Search Last    | O(log n)          | O(1)     | Yes
 * Search Rotated Array  | O(log n)          | O(1)     | Yes (rotated)
 * Find Peak Element     | O(log n)          | O(1)     | No
 * Ternary Search        | O(log₃ n)         | O(1)     | Yes
 * Exponential Search    | O(log n)          | O(log n) | Yes
 * Interpolation Search  | O(log log n) avg  | O(1)     | Yes (uniform)
 * </pre>
 */
public class Searching {

    // -----------------------------------------------------------------------
    // 1. Binary Search — iterative
    // -----------------------------------------------------------------------

    /**
     * Searches {@code arr} for {@code target} using iterative binary search.
     *
     * <p>Requires {@code arr} to be sorted in ascending order.
     *
     * <ul>
     *   <li>Time:  O(log n)
     *   <li>Space: O(1)
     * </ul>
     *
     * @param arr    sorted array
     * @param target value to find
     * @return index of {@code target} in {@code arr}, or {@code -1} if not present
     */
    public static int binarySearch(int[] arr, int target) {
        if (arr == null) return -1;
        int lo = 0, hi = arr.length - 1;
        while (lo <= hi) {
            int mid = lo + (hi - lo) / 2; // avoids (lo+hi) overflow
            if (arr[mid] == target) return mid;
            else if (arr[mid] < target) lo = mid + 1;
            else hi = mid - 1;
        }
        return -1;
    }

    // -----------------------------------------------------------------------
    // 2. Binary Search — recursive
    // -----------------------------------------------------------------------

    /**
     * Searches {@code arr} for {@code target} using recursive binary search.
     *
     * <p>Requires {@code arr} to be sorted in ascending order.
     *
     * <ul>
     *   <li>Time:  O(log n)
     *   <li>Space: O(log n) — call stack
     * </ul>
     *
     * @param arr    sorted array
     * @param target value to find
     * @return index of {@code target} in {@code arr}, or {@code -1} if not present
     */
    public static int binarySearchRecursive(int[] arr, int target) {
        if (arr == null) return -1;
        return bsRecHelper(arr, target, 0, arr.length - 1);
    }

    private static int bsRecHelper(int[] arr, int target, int lo, int hi) {
        if (lo > hi) return -1;
        int mid = lo + (hi - lo) / 2;
        if (arr[mid] == target) return mid;
        else if (arr[mid] < target) return bsRecHelper(arr, target, mid + 1, hi);
        else return bsRecHelper(arr, target, lo, mid - 1);
    }

    // -----------------------------------------------------------------------
    // 3. Binary Search — first occurrence
    // -----------------------------------------------------------------------

    /**
     * Finds the index of the <em>first</em> occurrence of {@code target} in a sorted array that
     * may contain duplicates.
     *
     * <ul>
     *   <li>Time:  O(log n)
     *   <li>Space: O(1)
     * </ul>
     *
     * @param arr    sorted array (may have duplicates)
     * @param target value to find
     * @return index of first occurrence, or {@code -1} if not present
     */
    public static int binarySearchFirst(int[] arr, int target) {
        if (arr == null) return -1;
        int lo = 0, hi = arr.length - 1, result = -1;
        while (lo <= hi) {
            int mid = lo + (hi - lo) / 2;
            if (arr[mid] == target) {
                result = mid;   // record and keep searching left
                hi = mid - 1;
            } else if (arr[mid] < target) {
                lo = mid + 1;
            } else {
                hi = mid - 1;
            }
        }
        return result;
    }

    // -----------------------------------------------------------------------
    // 4. Binary Search — last occurrence
    // -----------------------------------------------------------------------

    /**
     * Finds the index of the <em>last</em> occurrence of {@code target} in a sorted array that
     * may contain duplicates.
     *
     * <ul>
     *   <li>Time:  O(log n)
     *   <li>Space: O(1)
     * </ul>
     *
     * @param arr    sorted array (may have duplicates)
     * @param target value to find
     * @return index of last occurrence, or {@code -1} if not present
     */
    public static int binarySearchLast(int[] arr, int target) {
        if (arr == null) return -1;
        int lo = 0, hi = arr.length - 1, result = -1;
        while (lo <= hi) {
            int mid = lo + (hi - lo) / 2;
            if (arr[mid] == target) {
                result = mid;   // record and keep searching right
                lo = mid + 1;
            } else if (arr[mid] < target) {
                lo = mid + 1;
            } else {
                hi = mid - 1;
            }
        }
        return result;
    }

    // -----------------------------------------------------------------------
    // 5. Search in Rotated Sorted Array
    // -----------------------------------------------------------------------

    /**
     * Searches for {@code target} in a sorted array that has been rotated at an unknown pivot.
     *
     * <p>Example: {@code [4, 5, 6, 7, 0, 1, 2]} is a rotation of {@code [0, 1, 2, 4, 5, 6, 7]}.
     * The algorithm exploits the fact that at least one half of the current window is always
     * sorted, enabling binary-search-like elimination.
     *
     * <p>Assumes all elements are distinct.
     *
     * <ul>
     *   <li>Time:  O(log n)
     *   <li>Space: O(1)
     * </ul>
     *
     * @param arr    rotated sorted array with distinct elements
     * @param target value to find
     * @return index of {@code target}, or {@code -1} if not present
     */
    public static int searchRotatedArray(int[] arr, int target) {
        if (arr == null) return -1;
        int lo = 0, hi = arr.length - 1;
        while (lo <= hi) {
            int mid = lo + (hi - lo) / 2;
            if (arr[mid] == target) return mid;

            // Determine which half is sorted
            if (arr[lo] <= arr[mid]) {
                // Left half is sorted
                if (target >= arr[lo] && target < arr[mid]) hi = mid - 1;
                else lo = mid + 1;
            } else {
                // Right half is sorted
                if (target > arr[mid] && target <= arr[hi]) lo = mid + 1;
                else hi = mid - 1;
            }
        }
        return -1;
    }

    // -----------------------------------------------------------------------
    // 6. Find Peak Element
    // -----------------------------------------------------------------------

    /**
     * Finds any peak element in {@code arr} using binary search.
     *
     * <p>A peak element is one that is strictly greater than its neighbours.
     * The boundary elements ({@code arr[0]}, {@code arr[n-1]}) are compared only with their
     * single neighbour. If multiple peaks exist, returns the index of any one of them.
     *
     * <p>Assumes no two adjacent elements are equal.
     *
     * <ul>
     *   <li>Time:  O(log n)
     *   <li>Space: O(1)
     * </ul>
     *
     * @param arr input array (need not be sorted)
     * @return index of a peak element, or {@code -1} for null/empty input
     */
    public static int findPeak(int[] arr) {
        if (arr == null || arr.length == 0) return -1;
        int n = arr.length;
        if (n == 1) return 0;
        if (arr[0] > arr[1]) return 0;
        if (arr[n - 1] > arr[n - 2]) return n - 1;

        int lo = 1, hi = n - 2;
        while (lo <= hi) {
            int mid = lo + (hi - lo) / 2;
            if (arr[mid] > arr[mid - 1] && arr[mid] > arr[mid + 1]) return mid;
            else if (arr[mid] < arr[mid + 1]) lo = mid + 1; // ascending → peak is to the right
            else hi = mid - 1;                              // descending → peak is to the left
        }
        return -1; // should not reach here for valid input
    }

    // -----------------------------------------------------------------------
    // 7. Ternary Search
    // -----------------------------------------------------------------------

    /**
     * Searches {@code arr} for {@code target} using ternary search.
     *
     * <p>Divides the search space into three parts at each step. Despite O(log₃ n) iterations,
     * each iteration performs two comparisons so the total comparison count is higher than binary
     * search. Included here for completeness and interview familiarity.
     *
     * <ul>
     *   <li>Time:  O(log₃ n) iterations = O(log n)
     *   <li>Space: O(1)
     * </ul>
     *
     * @param arr    sorted array
     * @param target value to find
     * @return index of {@code target}, or {@code -1} if not present
     */
    public static int ternarySearch(int[] arr, int target) {
        if (arr == null) return -1;
        int lo = 0, hi = arr.length - 1;
        while (lo <= hi) {
            int third = (hi - lo) / 3;
            int mid1 = lo + third;
            int mid2 = hi - third;

            if (arr[mid1] == target) return mid1;
            if (arr[mid2] == target) return mid2;

            if (target < arr[mid1]) hi = mid1 - 1;
            else if (target > arr[mid2]) lo = mid2 + 1;
            else { lo = mid1 + 1; hi = mid2 - 1; }
        }
        return -1;
    }

    // -----------------------------------------------------------------------
    // 8. Exponential Search
    // -----------------------------------------------------------------------

    /**
     * Searches {@code arr} for {@code target} using exponential search.
     *
     * <p>Useful for unbounded or very large sorted arrays. Doubles the search boundary
     * exponentially until the target's range is found, then falls back to binary search within
     * that range.
     *
     * <ul>
     *   <li>Time:  O(log n) — O(log i) where i is the target's index
     *   <li>Space: O(log n) — recursive binary search stack
     * </ul>
     *
     * @param arr    sorted array
     * @param target value to find
     * @return index of {@code target}, or {@code -1} if not present
     */
    public static int exponentialSearch(int[] arr, int target) {
        if (arr == null || arr.length == 0) return -1;
        if (arr[0] == target) return 0;

        int n = arr.length;
        int bound = 1;
        // Double bound until arr[bound] >= target or we exceed array length
        while (bound < n && arr[bound] < target) bound *= 2;

        // Binary search in [bound/2, min(bound, n-1)]
        return bsRecHelper(arr, target, bound / 2, Math.min(bound, n - 1));
    }

    // -----------------------------------------------------------------------
    // 9. Interpolation Search
    // -----------------------------------------------------------------------

    /**
     * Searches {@code arr} for {@code target} using interpolation search.
     *
     * <p>Probes the array at a position interpolated from the target's expected location,
     * similar to how one would look up a word in a dictionary. Achieves O(log log n) average
     * comparisons when values are uniformly distributed.
     *
     * <ul>
     *   <li>Time:  O(log log n) average (uniform distribution), O(n) worst case
     *   <li>Space: O(1)
     * </ul>
     *
     * @param arr    sorted array with uniformly distributed values
     * @param target value to find
     * @return index of {@code target}, or {@code -1} if not present
     */
    public static int interpolationSearch(int[] arr, int target) {
        if (arr == null) return -1;
        int lo = 0, hi = arr.length - 1;
        while (lo <= hi && target >= arr[lo] && target <= arr[hi]) {
            if (lo == hi) {
                return arr[lo] == target ? lo : -1;
            }
            // Interpolation formula
            int range = arr[hi] - arr[lo];
            int pos = lo + (int) (((long) (target - arr[lo]) * (hi - lo)) / range);

            if (arr[pos] == target) return pos;
            else if (arr[pos] < target) lo = pos + 1;
            else hi = pos - 1;
        }
        return -1;
    }

    // -----------------------------------------------------------------------
    // main — demos for all methods
    // -----------------------------------------------------------------------

    /**
     * Demonstrates every search algorithm with representative test cases.
     *
     * @param args unused
     */
    public static void main(String[] args) {
        System.out.println("=== Searching Algorithm Demos ===\n");

        // Sorted array used by most methods
        int[] sorted = {1, 3, 5, 7, 9, 11, 13, 15, 17, 19};
        // Sorted array with duplicates
        int[] dups = {1, 2, 2, 2, 3, 4, 4, 5, 6, 6, 6, 7};

        System.out.println("Array: " + Arrays.toString(sorted));
        System.out.println();

        // 1. Binary Search — iterative
        System.out.println("1. binarySearch (iterative)");
        System.out.printf("   search(7)  -> index %d%n",  binarySearch(sorted, 7));
        System.out.printf("   search(6)  -> index %d%n",  binarySearch(sorted, 6));
        System.out.printf("   search(1)  -> index %d%n",  binarySearch(sorted, 1));
        System.out.printf("   search(19) -> index %d%n",  binarySearch(sorted, 19));
        System.out.println();

        // 2. Binary Search — recursive
        System.out.println("2. binarySearchRecursive");
        System.out.printf("   search(11) -> index %d%n",  binarySearchRecursive(sorted, 11));
        System.out.printf("   search(4)  -> index %d%n",  binarySearchRecursive(sorted, 4));
        System.out.println();

        // 3. Binary Search — first occurrence
        System.out.println("3. binarySearchFirst (duplicates array: " + Arrays.toString(dups) + ")");
        System.out.printf("   first(2)  -> index %d  (expected 1)%n",  binarySearchFirst(dups, 2));
        System.out.printf("   first(6)  -> index %d  (expected 8)%n",  binarySearchFirst(dups, 6));
        System.out.printf("   first(10) -> index %d  (expected -1)%n", binarySearchFirst(dups, 10));
        System.out.println();

        // 4. Binary Search — last occurrence
        System.out.println("4. binarySearchLast (duplicates array)");
        System.out.printf("   last(2)  -> index %d  (expected 3)%n",  binarySearchLast(dups, 2));
        System.out.printf("   last(6)  -> index %d  (expected 10)%n", binarySearchLast(dups, 6));
        System.out.printf("   last(10) -> index %d  (expected -1)%n", binarySearchLast(dups, 10));
        System.out.println();

        // 5. Search in Rotated Array
        int[] rotated = {6, 7, 8, 9, 10, 1, 2, 3, 4, 5};
        System.out.println("5. searchRotatedArray: " + Arrays.toString(rotated));
        System.out.printf("   search(1)  -> index %d  (expected 5)%n",  searchRotatedArray(rotated, 1));
        System.out.printf("   search(8)  -> index %d  (expected 2)%n",  searchRotatedArray(rotated, 8));
        System.out.printf("   search(5)  -> index %d  (expected 9)%n",  searchRotatedArray(rotated, 5));
        System.out.printf("   search(11) -> index %d  (expected -1)%n", searchRotatedArray(rotated, 11));
        System.out.println();

        // 6. Find Peak
        int[] peakArr = {1, 3, 20, 4, 1, 0};
        System.out.println("6. findPeak: " + Arrays.toString(peakArr));
        int peak = findPeak(peakArr);
        System.out.printf("   peak at index %d, value %d  (expected index 2, value 20)%n", peak, peakArr[peak]);

        int[] peakArr2 = {10, 20, 15, 2, 23, 90, 67};
        System.out.println("   Array: " + Arrays.toString(peakArr2));
        int peak2 = findPeak(peakArr2);
        System.out.printf("   peak at index %d, value %d%n", peak2, peakArr2[peak2]);
        System.out.println();

        // 7. Ternary Search
        System.out.println("7. ternarySearch");
        System.out.printf("   search(15) -> index %d  (expected 7)%n",  ternarySearch(sorted, 15));
        System.out.printf("   search(2)  -> index %d  (expected -1)%n", ternarySearch(sorted, 2));
        System.out.println();

        // 8. Exponential Search
        System.out.println("8. exponentialSearch");
        System.out.printf("   search(19) -> index %d  (expected 9)%n",  exponentialSearch(sorted, 19));
        System.out.printf("   search(1)  -> index %d  (expected 0)%n",  exponentialSearch(sorted, 1));
        System.out.printf("   search(100)-> index %d  (expected -1)%n", exponentialSearch(sorted, 100));
        System.out.println();

        // 9. Interpolation Search
        int[] uniform = {10, 20, 30, 40, 50, 60, 70, 80, 90, 100};
        System.out.println("9. interpolationSearch: " + Arrays.toString(uniform));
        System.out.printf("   search(70)  -> index %d  (expected 6)%n",  interpolationSearch(uniform, 70));
        System.out.printf("   search(10)  -> index %d  (expected 0)%n",  interpolationSearch(uniform, 10));
        System.out.printf("   search(100) -> index %d  (expected 9)%n",  interpolationSearch(uniform, 100));
        System.out.printf("   search(35)  -> index %d  (expected -1)%n", interpolationSearch(uniform, 35));
        System.out.println();

        System.out.println("=== All demos complete ===");
    }
}
