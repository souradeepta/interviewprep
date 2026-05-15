package algorithms.sorting;

import java.util.Arrays;
import java.util.ArrayList;
import java.util.List;

/**
 * Comprehensive collection of sorting algorithm implementations for SDE interview preparation.
 *
 * <p>All sort methods operate in-place (except {@link #bucketSort(double[])} which returns a new
 * array) and sort in ascending order unless otherwise noted.
 *
 * <p>Summary of complexities:
 * <pre>
 * Algorithm        | Time (best/avg/worst) | Space     | Stable
 * -----------------+-----------------------+-----------+-------
 * Bubble Sort      | O(n) / O(n²) / O(n²) | O(1)      | Yes
 * Selection Sort   | O(n²) / O(n²) / O(n²)| O(1)      | No
 * Insertion Sort   | O(n) / O(n²) / O(n²) | O(1)      | Yes
 * Merge Sort       | O(n log n) all        | O(n)      | Yes
 * Quick Sort       | O(n log n) / O(n log n) / O(n²)| O(log n)| No
 * Heap Sort        | O(n log n) all        | O(1)      | No
 * Counting Sort    | O(n+k) all            | O(k)      | Yes
 * Radix Sort       | O(d*(n+k)) all        | O(n+k)    | Yes
 * Bucket Sort      | O(n) avg / O(n²) worst| O(n)      | Yes
 * </pre>
 */
public class Sorting {

    // -----------------------------------------------------------------------
    // 1. Bubble Sort
    // -----------------------------------------------------------------------

    /**
     * Sorts {@code arr} using the Bubble Sort algorithm with an early-exit optimisation.
     *
     * <p>If no swaps are performed during a full pass the array is already sorted and the
     * algorithm exits early, giving O(n) best-case performance on nearly-sorted input.
     *
     * <ul>
     *   <li>Time:  O(n) best, O(n²) average/worst
     *   <li>Space: O(1) — in-place
     *   <li>Stable: yes
     * </ul>
     *
     * @param arr the array to sort (modified in-place)
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public static void bubbleSort(int[] arr) {
        if (arr == null || arr.length < 2) return;
        int n = arr.length;
        for (int i = 0; i < n - 1; i++) {
            boolean swapped = false;
            for (int j = 0; j < n - 1 - i; j++) {
                if (arr[j] > arr[j + 1]) {
                    swap(arr, j, j + 1);
                    swapped = true;
                }
            }
            if (!swapped) break; // early exit — already sorted
        }
    }

    // -----------------------------------------------------------------------
    // 2. Selection Sort
    // -----------------------------------------------------------------------

    /**
     * Sorts {@code arr} using the Selection Sort algorithm.
     *
     * <p>Each pass finds the minimum element in the unsorted portion and moves it to the front.
     * The number of swaps is O(n), making it useful when write cost is high.
     *
     * <ul>
     *   <li>Time:  O(n²) best/average/worst
     *   <li>Space: O(1) — in-place
     *   <li>Stable: no (equal elements may be reordered)
     * </ul>
     *
     * @param arr the array to sort (modified in-place)
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public static void selectionSort(int[] arr) {
        if (arr == null || arr.length < 2) return;
        int n = arr.length;
        for (int i = 0; i < n - 1; i++) {
            int minIdx = i;
            for (int j = i + 1; j < n; j++) {
                if (arr[j] < arr[minIdx]) minIdx = j;
            }
            if (minIdx != i) swap(arr, i, minIdx);
        }
    }

    // -----------------------------------------------------------------------
    // 3a. Insertion Sort
    // -----------------------------------------------------------------------

    /**
     * Sorts {@code arr} using the Insertion Sort algorithm (linear-search variant).
     *
     * <p>Excellent for small or nearly-sorted arrays. Online algorithm — can sort while
     * receiving elements.
     *
     * <ul>
     *   <li>Time:  O(n) best, O(n²) average/worst
     *   <li>Space: O(1) — in-place
     *   <li>Stable: yes
     * </ul>
     *
     * @param arr the array to sort (modified in-place)
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public static void insertionSort(int[] arr) {
        if (arr == null || arr.length < 2) return;
        for (int i = 1; i < arr.length; i++) {
            int key = arr[i];
            int j = i - 1;
            while (j >= 0 && arr[j] > key) {
                arr[j + 1] = arr[j];
                j--;
            }
            arr[j + 1] = key;
        }
    }

    // -----------------------------------------------------------------------
    // 3b. Binary Insertion Sort
    // -----------------------------------------------------------------------

    /**
     * Sorts {@code arr} using the Binary Insertion Sort algorithm.
     *
     * <p>Uses binary search to locate the insertion position, reducing the number of comparisons
     * to O(n log n) total. The number of element moves is still O(n²) in the worst case, so
     * overall time complexity is unchanged, but comparison count is improved.
     *
     * <ul>
     *   <li>Time:  O(n log n) comparisons, O(n²) moves — O(n²) overall
     *   <li>Space: O(1) — in-place
     *   <li>Stable: yes
     * </ul>
     *
     * @param arr the array to sort (modified in-place)
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public static void binaryInsertionSort(int[] arr) {
        if (arr == null || arr.length < 2) return;
        for (int i = 1; i < arr.length; i++) {
            int key = arr[i];
            // Binary search for insertion position in arr[0..i-1]
            int lo = 0, hi = i;
            while (lo < hi) {
                int mid = lo + (hi - lo) / 2;
                if (arr[mid] <= key) lo = mid + 1;
                else hi = mid;
            }
            // Shift elements right to make room
            System.arraycopy(arr, lo, arr, lo + 1, i - lo);
            arr[lo] = key;
        }
    }

    // -----------------------------------------------------------------------
    // 4. Merge Sort (recursive top-down + iterative bottom-up)
    // -----------------------------------------------------------------------

    /**
     * Sorts {@code arr} using top-down recursive Merge Sort.
     *
     * <p>Stable, divide-and-conquer sort. Preferred for linked lists and when stability is
     * required. Uses a temporary buffer to avoid repeated allocation inside the recursion.
     *
     * <ul>
     *   <li>Time:  O(n log n) best/average/worst
     *   <li>Space: O(n) auxiliary
     *   <li>Stable: yes
     * </ul>
     *
     * @param arr the array to sort (modified in-place)
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public static void mergeSort(int[] arr) {
        if (arr == null || arr.length < 2) return;
        int[] temp = new int[arr.length];
        mergeSortHelper(arr, temp, 0, arr.length - 1);
    }

    private static void mergeSortHelper(int[] arr, int[] temp, int lo, int hi) {
        if (lo >= hi) return;
        int mid = lo + (hi - lo) / 2;
        mergeSortHelper(arr, temp, lo, mid);
        mergeSortHelper(arr, temp, mid + 1, hi);
        merge(arr, temp, lo, mid, hi);
    }

    private static void merge(int[] arr, int[] temp, int lo, int mid, int hi) {
        // Copy to temp
        System.arraycopy(arr, lo, temp, lo, hi - lo + 1);
        int i = lo, j = mid + 1, k = lo;
        while (i <= mid && j <= hi) {
            if (temp[i] <= temp[j]) arr[k++] = temp[i++];
            else arr[k++] = temp[j++];
        }
        while (i <= mid) arr[k++] = temp[i++];
        while (j <= hi) arr[k++] = temp[j++];
    }

    /**
     * Sorts {@code arr} using iterative bottom-up Merge Sort.
     *
     * <p>Avoids recursion stack overhead. Merges runs of size 1, then 2, 4, 8, … until the
     * whole array is sorted.
     *
     * <ul>
     *   <li>Time:  O(n log n) best/average/worst
     *   <li>Space: O(n) auxiliary
     *   <li>Stable: yes
     * </ul>
     *
     * @param arr the array to sort (modified in-place)
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public static void mergeSortBottomUp(int[] arr) {
        if (arr == null || arr.length < 2) return;
        int n = arr.length;
        int[] temp = new int[n];
        for (int width = 1; width < n; width *= 2) {
            for (int lo = 0; lo < n; lo += 2 * width) {
                int mid = Math.min(lo + width - 1, n - 1);
                int hi = Math.min(lo + 2 * width - 1, n - 1);
                if (mid < hi) merge(arr, temp, lo, mid, hi);
            }
        }
    }

    // -----------------------------------------------------------------------
    // 5. Quick Sort (median-of-three + 3-way partition)
    // -----------------------------------------------------------------------

    /**
     * Sorts {@code arr} using Quick Sort with median-of-three pivot selection and
     * Dijkstra's 3-way partitioning (Dutch National Flag).
     *
     * <p>Median-of-three reduces the probability of O(n²) worst-case. 3-way partitioning
     * achieves O(n log n) on arrays with many duplicate keys (linear when all equal).
     *
     * <ul>
     *   <li>Time:  O(n log n) average, O(n²) worst (rare with median-of-three)
     *   <li>Space: O(log n) stack
     *   <li>Stable: no
     * </ul>
     *
     * @param arr the array to sort (modified in-place)
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public static void quickSort(int[] arr) {
        if (arr == null || arr.length < 2) return;
        quickSort3Way(arr, 0, arr.length - 1);
    }

    private static void quickSort3Way(int[] arr, int lo, int hi) {
        if (lo >= hi) return;

        // Median-of-three pivot: move median to arr[lo]
        int mid = lo + (hi - lo) / 2;
        if (arr[lo] > arr[mid]) swap(arr, lo, mid);
        if (arr[lo] > arr[hi]) swap(arr, lo, hi);
        if (arr[mid] > arr[hi]) swap(arr, mid, hi);
        // Now arr[lo] <= arr[mid] <= arr[hi]; place pivot at lo
        swap(arr, lo, mid);
        int pivot = arr[lo];

        // 3-way partition: lt..gt contains pivot, left < pivot, right > pivot
        int lt = lo, gt = hi, i = lo + 1;
        while (i <= gt) {
            if (arr[i] < pivot) swap(arr, lt++, i++);
            else if (arr[i] > pivot) swap(arr, i, gt--);
            else i++;
        }

        quickSort3Way(arr, lo, lt - 1);
        quickSort3Way(arr, gt + 1, hi);
    }

    // -----------------------------------------------------------------------
    // 6. Heap Sort
    // -----------------------------------------------------------------------

    /**
     * Sorts {@code arr} using Heap Sort.
     *
     * <p>Builds a max-heap in O(n) then extracts the maximum n times. Consistently O(n log n)
     * with no extra memory required.
     *
     * <ul>
     *   <li>Time:  O(n log n) best/average/worst
     *   <li>Space: O(1) — in-place
     *   <li>Stable: no
     * </ul>
     *
     * @param arr the array to sort (modified in-place)
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public static void heapSort(int[] arr) {
        if (arr == null || arr.length < 2) return;
        int n = arr.length;

        // Build max-heap (heapify from last non-leaf downward)
        for (int i = n / 2 - 1; i >= 0; i--) {
            heapify(arr, n, i);
        }

        // Extract elements from heap one by one
        for (int i = n - 1; i > 0; i--) {
            swap(arr, 0, i);
            heapify(arr, i, 0);
        }
    }

    /** Sifts down element at index {@code i} within a heap of size {@code heapSize}. */
    private static void heapify(int[] arr, int heapSize, int i) {
        int largest = i;
        int left = 2 * i + 1;
        int right = 2 * i + 2;

        if (left < heapSize && arr[left] > arr[largest]) largest = left;
        if (right < heapSize && arr[right] > arr[largest]) largest = right;

        if (largest != i) {
            swap(arr, i, largest);
            heapify(arr, heapSize, largest);
        }
    }

    // -----------------------------------------------------------------------
    // 7. Counting Sort
    // -----------------------------------------------------------------------

    /**
     * Sorts {@code arr} using Counting Sort.
     *
     * <p>Requires all values to be non-negative integers. The range k = max(arr) + 1.
     * Very fast when k is small relative to n.
     *
     * <ul>
     *   <li>Time:  O(n + k) best/average/worst
     *   <li>Space: O(k) auxiliary
     *   <li>Stable: yes (with the prefix-sum accumulation step)
     * </ul>
     *
     * @param arr the array to sort (modified in-place); all values must be &gt;= 0
     * @throws IllegalArgumentException if any element is negative
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public static void countingSort(int[] arr) {
        if (arr == null || arr.length < 2) return;

        int max = 0;
        for (int v : arr) {
            if (v < 0) throw new IllegalArgumentException("countingSort requires non-negative integers");
            if (v > max) max = v;
        }

        int[] count = new int[max + 1];
        for (int v : arr) count[v]++;

        // Prefix sum — count[i] now holds position after last i
        for (int i = 1; i <= max; i++) count[i] += count[i - 1];

        int[] output = new int[arr.length];
        // Traverse in reverse for stability
        for (int i = arr.length - 1; i >= 0; i--) {
            output[--count[arr[i]]] = arr[i];
        }
        System.arraycopy(output, 0, arr, 0, arr.length);
    }

    // -----------------------------------------------------------------------
    // 8. Radix Sort (LSD)
    // -----------------------------------------------------------------------

    /**
     * Sorts {@code arr} using LSD (Least Significant Digit) Radix Sort with base-10 digits.
     *
     * <p>Processes digits from least significant to most significant using a stable counting sort
     * at each digit position. Handles non-negative integers.
     *
     * <ul>
     *   <li>Time:  O(d * (n + k)) where d = number of digits, k = 10 (decimal base)
     *   <li>Space: O(n + k)
     *   <li>Stable: yes
     * </ul>
     *
     * @param arr the array to sort (modified in-place); all values must be &gt;= 0
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public static void radixSort(int[] arr) {
        if (arr == null || arr.length < 2) return;

        int max = 0;
        for (int v : arr) {
            if (v < 0) throw new IllegalArgumentException("radixSort requires non-negative integers");
            if (v > max) max = v;
        }

        // Do counting sort for every digit position
        for (int exp = 1; max / exp > 0; exp *= 10) {
            countingSortByDigit(arr, exp);
        }
    }

    private static void countingSortByDigit(int[] arr, int exp) {
        final int BASE = 10;
        int n = arr.length;
        int[] output = new int[n];
        int[] count = new int[BASE];

        for (int v : arr) count[(v / exp) % BASE]++;
        for (int i = 1; i < BASE; i++) count[i] += count[i - 1];
        // Traverse in reverse for stability
        for (int i = n - 1; i >= 0; i--) {
            int digit = (arr[i] / exp) % BASE;
            output[--count[digit]] = arr[i];
        }
        System.arraycopy(output, 0, arr, 0, n);
    }

    // -----------------------------------------------------------------------
    // 9. Bucket Sort
    // -----------------------------------------------------------------------

    /**
     * Sorts {@code arr} using Bucket Sort, assuming values are uniformly distributed in [0, 1).
     *
     * <p>Distributes elements into n equally-sized buckets, sorts each bucket with insertion
     * sort, then concatenates. Achieves O(n) average-case with uniform input.
     *
     * <ul>
     *   <li>Time:  O(n) average (uniform input), O(n²) worst (all in one bucket)
     *   <li>Space: O(n)
     *   <li>Stable: yes
     * </ul>
     *
     * @param arr the array to sort; all values must satisfy 0 &lt;= v &lt; 1
     * @return a new sorted double array
     * @throws IllegalArgumentException if any value is outside [0, 1)
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public static double[] bucketSort(double[] arr) {
        if (arr == null || arr.length < 2) return arr == null ? new double[0] : arr.clone();

        int n = arr.length;

        @SuppressWarnings("unchecked")
        List<Double>[] buckets = new List[n];
        for (int i = 0; i < n; i++) buckets[i] = new ArrayList<>();

        for (double v : arr) {
            if (v < 0 || v >= 1)
                throw new IllegalArgumentException("bucketSort expects values in [0, 1), got: " + v);
            int idx = (int) (v * n);
            if (idx == n) idx = n - 1; // safety guard for v very close to 1
            buckets[idx].add(v);
        }

        // Sort each bucket (insertion sort is efficient for small lists)
        double[] result = new double[n];
        int pos = 0;
        for (List<Double> bucket : buckets) {
            bucket.sort(null);
            for (double v : bucket) result[pos++] = v;
        }
        return result;
    }

    // -----------------------------------------------------------------------
    // Helper
    // -----------------------------------------------------------------------

    private static void swap(int[] arr, int i, int j) {
        int tmp = arr[i];
        arr[i] = arr[j];
        arr[j] = tmp;
    }

    // -----------------------------------------------------------------------
    // Benchmark
    // -----------------------------------------------------------------------

    /**
     * Runs a benchmark comparing all sorting algorithms on the same random-ish data set.
     *
     * <p>Each algorithm sorts an independent copy of the array and prints elapsed nanoseconds.
     */
    public static void benchmark() {
        // Build a moderately sized test array
        int size = 50_000;
        int[] original = new int[size];
        java.util.Random rng = new java.util.Random(42);
        for (int i = 0; i < size; i++) original[i] = rng.nextInt(100_000);

        System.out.println("=== Sorting Benchmark (n=" + size + ") ===");

        time("bubbleSort",          () -> bubbleSort(original.clone()));
        time("selectionSort",       () -> selectionSort(original.clone()));
        time("insertionSort",       () -> insertionSort(original.clone()));
        time("binaryInsertionSort", () -> binaryInsertionSort(original.clone()));
        time("mergeSort",           () -> mergeSort(original.clone()));
        time("mergeSortBottomUp",   () -> mergeSortBottomUp(original.clone()));
        time("quickSort",           () -> quickSort(original.clone()));
        time("heapSort",            () -> heapSort(original.clone()));
        time("countingSort",        () -> countingSort(original.clone()));
        time("radixSort",           () -> radixSort(original.clone()));

        // Bucket sort operates on doubles [0,1)
        double[] doubles = new double[size];
        for (int i = 0; i < size; i++) doubles[i] = rng.nextDouble();
        time("bucketSort", () -> bucketSort(doubles));
    }

    private static void time(String name, Runnable task) {
        long start = System.nanoTime();
        task.run();
        long elapsed = System.nanoTime() - start;
        System.out.printf("  %-22s %,10d ns%n", name, elapsed);
    }

    // -----------------------------------------------------------------------
    // main — demo + benchmark
    // -----------------------------------------------------------------------

    /**
     * Demonstrates each sorting algorithm and runs the comparison benchmark.
     *
     * @param args unused
     */
    public static void main(String[] args) {
        System.out.println("=== Sorting Algorithm Demos ===\n");

        int[] sample = {64, 25, 12, 22, 11, 90, 3, 50, 7};

        demo("bubbleSort",          sample, arr -> bubbleSort(arr));
        demo("selectionSort",       sample, arr -> selectionSort(arr));
        demo("insertionSort",       sample, arr -> insertionSort(arr));
        demo("binaryInsertionSort", sample, arr -> binaryInsertionSort(arr));
        demo("mergeSort",           sample, arr -> mergeSort(arr));
        demo("mergeSortBottomUp",   sample, arr -> mergeSortBottomUp(arr));
        demo("quickSort",           sample, arr -> quickSort(arr));
        demo("heapSort",            sample, arr -> heapSort(arr));
        demo("countingSort",        sample, arr -> countingSort(arr));
        demo("radixSort",           sample, arr -> radixSort(arr));

        // Bucket sort — double array [0,1)
        double[] dbls = {0.78, 0.17, 0.39, 0.26, 0.72, 0.94, 0.21, 0.12, 0.23, 0.68};
        System.out.println("bucketSort");
        System.out.println("  Input:  " + Arrays.toString(dbls));
        double[] sorted = bucketSort(dbls);
        System.out.println("  Output: " + Arrays.toString(sorted));
        System.out.println();

        System.out.println();
        benchmark();
    }

    private static void demo(String name, int[] sample, java.util.function.Consumer<int[]> sorter) {
        int[] copy = sample.clone();
        System.out.println(name);
        System.out.println("  Input:  " + Arrays.toString(copy));
        sorter.accept(copy);
        System.out.println("  Output: " + Arrays.toString(copy));
        System.out.println();
    }
}
