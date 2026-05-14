package advanced;

import java.util.Arrays;

/**
 * Fenwick Tree (Binary Indexed Tree) for dynamic prefix-sum queries.
 *
 * <p>The Fenwick Tree stores partial sums in an array {@code bit[]} indexed from 1.
 * The "responsible range" of node {@code i} is determined by the lowest set bit of {@code i}:
 * {@code LSB(i) = i & (-i)}.  Node {@code i} accumulates the sum of elements
 * {@code [i - LSB(i) + 1, i]}.
 *
 * <p>Time complexities:
 * <ul>
 *   <li>update     – O(log n)</li>
 *   <li>prefixSum  – O(log n)</li>
 *   <li>rangeQuery – O(log n)</li>
 *   <li>build      – O(n log n) naive, O(n) with the optimised constructor</li>
 * </ul>
 *
 * <p>Space complexity: O(n).
 */
public class FenwickTree {

    // -------------------------------------------------------------------------
    // Fields
    // -------------------------------------------------------------------------

    private final int[] bit; // 1-indexed Fenwick array
    private final int   n;   // size of the logical array

    // -------------------------------------------------------------------------
    // Constructors
    // -------------------------------------------------------------------------

    /**
     * Creates a Fenwick Tree of size {@code n} with all values set to zero.
     *
     * <p>Time: O(n) | Space: O(n).
     *
     * @param n the number of elements (1-indexed up to n)
     */
    public FenwickTree(int n) {
        if (n <= 0) throw new IllegalArgumentException("Size must be positive");
        this.n   = n;
        this.bit = new int[n + 1];
    }

    /**
     * Creates a Fenwick Tree initialised from {@code arr} (0-indexed).
     *
     * <p>Uses an O(n) construction: copy values into {@code bit} and propagate
     * each node's value up to its parent exactly once.
     *
     * <p>Time: O(n) | Space: O(n).
     *
     * @param arr source array (0-indexed)
     */
    public FenwickTree(int[] arr) {
        this(arr.length);
        // O(n) build: set bit[i] = arr[i-1], then propagate
        for (int i = 1; i <= n; i++) {
            bit[i] += arr[i - 1];
            int parent = i + (i & -i);
            if (parent <= n) bit[parent] += bit[i];
        }
    }

    // -------------------------------------------------------------------------
    // update
    // -------------------------------------------------------------------------

    /**
     * Adds {@code delta} to the element at 1-indexed position {@code i}.
     * To set a value: call {@code update(i, newVal - oldVal)}.
     *
     * <p>Time: O(log n) | Space: O(1).
     *
     * @param i     1-indexed position (1 &le; i &le; n)
     * @param delta the amount to add
     */
    public void update(int i, int delta) {
        checkIndex(i);
        for (; i <= n; i += i & (-i)) {
            bit[i] += delta;
        }
    }

    // -------------------------------------------------------------------------
    // prefixSum
    // -------------------------------------------------------------------------

    /**
     * Returns the prefix sum of elements {@code [1, i]} (1-indexed).
     *
     * <p>Time: O(log n) | Space: O(1).
     *
     * @param i 1-indexed upper bound (1 &le; i &le; n)
     * @return sum of elements from index 1 to i
     */
    public int prefixSum(int i) {
        checkIndex(i);
        int sum = 0;
        for (; i > 0; i -= i & (-i)) {
            sum += bit[i];
        }
        return sum;
    }

    // -------------------------------------------------------------------------
    // rangeQuery
    // -------------------------------------------------------------------------

    /**
     * Returns the sum of elements in the range {@code [l, r]} (1-indexed, inclusive).
     *
     * <p>Time: O(log n) | Space: O(1).
     *
     * @param l left bound (1-indexed, inclusive)
     * @param r right bound (1-indexed, inclusive)
     * @return sum of elements from index l to r
     */
    public int rangeQuery(int l, int r) {
        if (l < 1 || r > n || l > r)
            throw new IndexOutOfBoundsException("Invalid range [" + l + ", " + r + "]");
        return prefixSum(r) - (l > 1 ? prefixSum(l - 1) : 0);
    }

    // -------------------------------------------------------------------------
    // Helpers
    // -------------------------------------------------------------------------

    private void checkIndex(int i) {
        if (i < 1 || i > n)
            throw new IndexOutOfBoundsException("Index " + i + " out of range [1, " + n + "]");
    }

    /** Returns the size of the Fenwick Tree. */
    public int size() { return n; }

    // -------------------------------------------------------------------------
    // toString
    // -------------------------------------------------------------------------

    /**
     * Returns a string showing the internal {@code bit[]} array and the logical
     * values it represents, with each node's responsible range.
     *
     * <p>Time: O(n log n) | Space: O(n).
     *
     * @return multi-line Fenwick Tree representation
     */
    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append("FenwickTree (n=").append(n).append("):\n");

        // Reconstruct logical array via prefix sums
        int[] logical = new int[n + 1];
        for (int i = 1; i <= n; i++) {
            logical[i] = rangeQuery(i, i);
        }
        sb.append("  Logical array (1-indexed): ");
        sb.append("[_, ");
        for (int i = 1; i <= n; i++) {
            sb.append(logical[i]);
            if (i < n) sb.append(", ");
        }
        sb.append("]\n");

        sb.append("  bit[] (1-indexed)         : ");
        sb.append("[_, ");
        for (int i = 1; i <= n; i++) {
            sb.append(bit[i]);
            if (i < n) sb.append(", ");
        }
        sb.append("]\n");

        // Node details
        sb.append("  Node details:\n");
        for (int i = 1; i <= n; i++) {
            int lsb = i & (-i);
            int rangeStart = i - lsb + 1;
            sb.append("    bit[").append(i).append("] = ").append(bit[i])
              .append("  (covers [").append(rangeStart).append(", ").append(i).append("])\n");
        }
        return sb.toString();
    }

    // -------------------------------------------------------------------------
    // Main – demo
    // -------------------------------------------------------------------------

    public static void main(String[] args) {
        System.out.println("=== Fenwick Tree (BIT) Demo ===\n");

        // Build from array (1-indexed usage: positions 1..8)
        int[] arr = {1, 3, 5, 7, 9, 11, 13, 15}; // 1-indexed: pos 1..8
        FenwickTree ft = new FenwickTree(arr);
        System.out.println(ft);

        // Prefix sums
        System.out.println("prefixSum(4) = " + ft.prefixSum(4) + "  (expected 16: 1+3+5+7)");
        System.out.println("prefixSum(8) = " + ft.prefixSum(8) + "  (expected 64: sum all)");
        System.out.println("prefixSum(1) = " + ft.prefixSum(1) + "  (expected 1)");

        // Range queries
        System.out.println("\nrangeQuery(2, 5) = " + ft.rangeQuery(2, 5) + "  (expected 24: 3+5+7+9)");
        System.out.println("rangeQuery(1, 8) = " + ft.rangeQuery(1, 8) + "  (expected 64)");
        System.out.println("rangeQuery(3, 3) = " + ft.rangeQuery(3, 3) + "  (expected 5)");

        // Update
        System.out.println("\nupdate(3, 4)  -- add 4 to index 3 (5 -> 9)");
        ft.update(3, 4);
        System.out.println("prefixSum(4) = " + ft.prefixSum(4) + "  (expected 20: 1+3+9+7)");
        System.out.println("rangeQuery(2, 5) = " + ft.rangeQuery(2, 5) + "  (expected 28: 3+9+7+9)");

        System.out.println("\nAfter update:");
        System.out.println(ft);

        // Build from size and individual updates
        System.out.println("Fresh FenwickTree(5), updating positions 1..5:");
        FenwickTree ft2 = new FenwickTree(5);
        for (int i = 1; i <= 5; i++) ft2.update(i, i * 2);
        System.out.println(ft2);
        System.out.println("prefixSum(5) = " + ft2.prefixSum(5) + "  (expected 30: 2+4+6+8+10)");
    }
}
