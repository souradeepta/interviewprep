package new_ds;

/**
 * Sparse Table — static data structure for O(1) Range Minimum / Maximum Queries.
 *
 * <h3>Core idea</h3>
 * For each position {@code i} and each power-of-two length {@code 2^j}, precompute:
 * <pre>
 *   table[j][i] = min (or max) of arr[i .. i + 2^j - 1]
 * </pre>
 * Because min/max are <em>idempotent</em>, a query {@code [l, r]} of length
 * {@code len = r - l + 1} can be answered by two possibly-overlapping windows
 * of length {@code 2^k} where {@code k = floor(log2(len))}:
 * <pre>
 *   query(l, r) = min( table[k][l], table[k][r - 2^k + 1] )
 * </pre>
 *
 * <h3>Why O(1) query?</h3>
 * The query requires only one precomputed log2 lookup, two table accesses, and
 * one comparison — all constant-time steps.
 *
 * <p><b>Note:</b> Sparse Table only supports <em>static</em> arrays (no updates).
 * For dynamic arrays use a Segment Tree instead.
 *
 * <pre>
 * Time Complexity:
 *   build(arr)       – O(n log n)
 *   query(l, r)      – O(1)        (min or max)
 *   queryIndex(l, r) – O(1)        (index of min)
 *
 * Space Complexity: O(n log n)
 * </pre>
 */
public class SparseTable {

    // -------------------------------------------------------------------------
    // Fields
    // -------------------------------------------------------------------------

    /** Number of elements in the input array. */
    private final int n;

    /** Original input array (kept for display and brute-force checks). */
    private final int[] arr;

    /**
     * Precomputed floor(log2(i)) for i in [0, n].
     * {@code log2[0] = log2[1] = 0}; {@code log2[i] = log2[i/2] + 1} for i >= 2.
     */
    private final int[] log2;

    /**
     * {@code minTable[j][i]} = minimum of {@code arr[i .. i + 2^j - 1]}.
     * Indexed {@code [level][position]}.
     */
    private final int[][] minTable;

    /**
     * {@code minIdxTable[j][i]} = index of the minimum element in
     * {@code arr[i .. i + 2^j - 1]}.
     * Stored alongside min values for O(1) {@link #queryIndex} support.
     */
    private final int[][] minIdxTable;

    /**
     * {@code maxTable[j][i]} = maximum of {@code arr[i .. i + 2^j - 1]}.
     */
    private final int[][] maxTable;

    /** Number of levels in the table: {@code floor(log2(n)) + 1}. */
    private final int levels;

    // -------------------------------------------------------------------------
    // Constructor — builds the table
    // -------------------------------------------------------------------------

    /**
     * Builds the sparse table from the given integer array.
     *
     * <p>Time: O(n log n) &nbsp;|&nbsp; Space: O(n log n)
     *
     * @param arr the input array (must be non-empty)
     * @throws IllegalArgumentException if arr is null or empty
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public SparseTable(int[] arr) {
        if (arr == null || arr.length == 0) {
            throw new IllegalArgumentException("Cannot build SparseTable on a null or empty array");
        }

        this.n   = arr.length;
        this.arr = arr.clone();

        // Number of levels: bit_length(n) = floor(log2(n)) + 1 for n >= 1
        this.levels = 32 - Integer.numberOfLeadingZeros(n);  // == floor(log2(n)) + 1

        // Precompute floor(log2(i)) for i in [0, n]
        this.log2 = new int[n + 1];
        for (int i = 2; i <= n; i++) {
            log2[i] = log2[i / 2] + 1;
        }

        // Allocate tables
        this.minTable    = new int[levels][n];
        this.minIdxTable = new int[levels][n];
        this.maxTable    = new int[levels][n];

        // Level 0: each window is a single element
        for (int i = 0; i < n; i++) {
            minTable[0][i]    = arr[i];
            minIdxTable[0][i] = i;
            maxTable[0][i]    = arr[i];
        }

        // Fill higher levels using the recurrence:
        //   table[j][i] = min( table[j-1][i], table[j-1][i + 2^(j-1)] )
        for (int j = 1; j < levels; j++) {
            int half = 1 << (j - 1);                      // 2^(j-1)
            int limit = n - (1 << j) + 1;                 // last valid starting position
            for (int i = 0; i < limit; i++) {
                // Min
                if (minTable[j - 1][i] <= minTable[j - 1][i + half]) {
                    minTable[j][i]    = minTable[j - 1][i];
                    minIdxTable[j][i] = minIdxTable[j - 1][i];
                } else {
                    minTable[j][i]    = minTable[j - 1][i + half];
                    minIdxTable[j][i] = minIdxTable[j - 1][i + half];
                }
                // Max
                maxTable[j][i] = Math.max(maxTable[j - 1][i], maxTable[j - 1][i + half]);
            }
        }
    }

    // -------------------------------------------------------------------------
    // Validation helper
    // -------------------------------------------------------------------------

    /**
     * Validates that {@code [l, r]} is a legal range for this table.
     *
     * @throws IndexOutOfBoundsException if the range is invalid
     */
    private void validateRange(int l, int r) {
        if (l < 0 || r >= n || l > r) {
            throw new IndexOutOfBoundsException(
                    String.format("Invalid range [%d, %d] for array of size %d", l, r, n));
        }
    }

    // -------------------------------------------------------------------------
    // Public API
    // -------------------------------------------------------------------------

    /**
     * Returns the minimum value in {@code arr[l..r]} (inclusive).
     *
     * <p>Algorithm:
     * <pre>
     *   k = floor(log2(r - l + 1))
     *   return min( table[k][l], table[k][r - 2^k + 1] )
     * </pre>
     * The two windows {@code [l, l+2^k-1]} and {@code [r-2^k+1, r]} together
     * cover {@code [l, r]}.  Overlap is harmless because min is idempotent.
     *
     * <p>Time: O(1)
     *
     * @param l left bound (inclusive, 0-indexed)
     * @param r right bound (inclusive, 0-indexed)
     * @return minimum value in the range
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public int query(int l, int r) {
        validateRange(l, r);
        int k      = log2[r - l + 1];
        int window = 1 << k;
        return Math.min(minTable[k][l], minTable[k][r - window + 1]);
    }

    /**
     * Returns the index of the minimum value in {@code arr[l..r]} (inclusive).
     *
     * <p>When multiple positions share the minimum value the leftmost index is returned.
     *
     * <p>Time: O(1)
     *
     * @param l left bound (inclusive, 0-indexed)
     * @param r right bound (inclusive, 0-indexed)
     * @return index of the minimum element in the range
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public int queryIndex(int l, int r) {
        validateRange(l, r);
        int k      = log2[r - l + 1];
        int window = 1 << k;
        int idxL   = minIdxTable[k][l];
        int idxR   = minIdxTable[k][r - window + 1];
        return (arr[idxL] <= arr[idxR]) ? idxL : idxR;
    }

    /**
     * Returns the maximum value in {@code arr[l..r]} (inclusive).
     *
     * <p>Uses the same two-overlapping-windows technique as {@link #query}.
     *
     * <p>Time: O(1)
     *
     * @param l left bound (inclusive, 0-indexed)
     * @param r right bound (inclusive, 0-indexed)
     * @return maximum value in the range
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public int queryMax(int l, int r) {
        validateRange(l, r);
        int k      = log2[r - l + 1];
        int window = 1 << k;
        return Math.max(maxTable[k][l], maxTable[k][r - window + 1]);
    }

    /**
     * Returns the size of the input array.
     *
     * @return n
     */
    public int size() {
        return n;
    }

    @Override
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append(String.format("SparseTable(n=%d, levels=%d)%n", n, levels));
        sb.append("Array: [");
        for (int i = 0; i < n; i++) {
            sb.append(arr[i]);
            if (i < n - 1) sb.append(", ");
        }
        sb.append("]\n");
        sb.append("Min table (level j covers windows of length 2^j):\n");
        for (int j = 0; j < levels; j++) {
            int limit = n - (1 << j) + 1;
            sb.append(String.format("  Level %d (len=%4d): [", j, 1 << j));
            for (int i = 0; i < limit; i++) {
                sb.append(minTable[j][i]);
                if (i < limit - 1) sb.append(", ");
            }
            sb.append("]\n");
        }
        return sb.toString();
    }

    // -------------------------------------------------------------------------
    // Demo main
    // -------------------------------------------------------------------------

    /**
     * Demonstrates build, O(1) query, queryIndex, and exhaustive correctness check.
     *
     * @param args unused
     */
    public static void main(String[] args) {
        System.out.println("=== Sparse Table Demo ===\n");

        int[] arr = {2, 4, 3, 1, 6, 7, 8, 9, 1, 7};
        System.out.print("Array: [");
        for (int i = 0; i < arr.length; i++) {
            System.out.print(arr[i] + (i < arr.length - 1 ? ", " : ""));
        }
        System.out.println("]");

        SparseTable st = new SparseTable(arr);
        System.out.println(st);

        // --- Range queries ---
        int[][] queries = {{0,9},{0,4},{2,7},{3,5},{0,0},{4,4},{1,8}};
        System.out.printf("%-12s %6s %6s %8s %9s  %s%n",
                "Query", "Min", "Max", "MinIdx", "BruteMin", "Check");
        System.out.println("-".repeat(60));
        for (int[] q : queries) {
            int l = q[0], r = q[1];
            int gotMin  = st.query(l, r);
            int gotMax  = st.queryMax(l, r);
            int gotIdx  = st.queryIndex(l, r);

            // Brute-force check
            int expMin = arr[l], expMax = arr[l];
            for (int i = l + 1; i <= r; i++) {
                expMin = Math.min(expMin, arr[i]);
                expMax = Math.max(expMax, arr[i]);
            }
            String ok = (gotMin == expMin && gotMax == expMax && arr[gotIdx] == expMin)
                    ? "OK" : "FAIL";
            System.out.printf("[%d, %d]      %6d %6d %8d %9d  %s%n",
                    l, r, gotMin, gotMax, gotIdx, expMin, ok);
        }

        // --- Exhaustive correctness check ---
        System.out.println("\nExhaustive correctness check (all O(n^2) range pairs):");
        boolean allPass = true;
        int n = arr.length;
        for (int l = 0; l < n; l++) {
            for (int r = l; r < n; r++) {
                int expMin = arr[l];
                for (int i = l + 1; i <= r; i++) expMin = Math.min(expMin, arr[i]);
                if (st.query(l, r) != expMin) {
                    allPass = false;
                    System.out.printf("  FAIL min [%d,%d]%n", l, r);
                }
                int idx = st.queryIndex(l, r);
                if (arr[idx] != expMin) {
                    allPass = false;
                    System.out.printf("  FAIL minIdx [%d,%d]%n", l, r);
                }
            }
        }
        System.out.printf("  All %d queries correct: %b%n", n * (n + 1) / 2, allPass);

        // --- Larger array benchmark ---
        System.out.println("\n--- Build time for n=100,000 ---");
        int N = 100_000;
        int[] big = new int[N];
        java.util.Random rng = new java.util.Random(42);
        for (int i = 0; i < N; i++) big[i] = rng.nextInt(1_000_000);

        long t0 = System.nanoTime();
        SparseTable stBig = new SparseTable(big);
        long buildMs = (System.nanoTime() - t0) / 1_000_000;
        System.out.printf("Build time for n=%,d: %d ms  (O(n log n))%n", N, buildMs);

        int Q = 10_000;
        t0 = System.nanoTime();
        for (int i = 0; i < Q; i++) {
            int l = rng.nextInt(N - 1);
            int r = l + rng.nextInt(N - l);
            stBig.query(l, r);
        }
        long queryUs = (System.nanoTime() - t0) / 1000;
        System.out.printf("Sparse Table — %,d queries: %.2f ms  (%.2f µs avg)%n",
                Q, queryUs / 1000.0, (double) queryUs / Q);

        System.out.println("\nDone.");
    }
}
