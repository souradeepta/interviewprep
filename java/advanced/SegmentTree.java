package advanced;

import java.util.Arrays;

/**
 * Segment Tree supporting range-sum queries and point updates on an integer array.
 *
 * <p>The tree is stored in a 1-indexed flat array of size {@code 4 * n}.
 * Node at index {@code i} covers a segment; its children are at {@code 2i} (left)
 * and {@code 2i + 1} (right).
 *
 * <p>Time complexities:
 * <ul>
 *   <li>build  – O(n)</li>
 *   <li>query  – O(log n)</li>
 *   <li>update – O(log n)</li>
 * </ul>
 *
 * <p>Space complexity: O(n).
 */
public class SegmentTree {

    // -------------------------------------------------------------------------
    // Fields
    // -------------------------------------------------------------------------

    private final int[] tree;   // 1-indexed segment tree array
    private final int   n;      // size of the original array
    private final int[] original; // kept for display purposes

    // -------------------------------------------------------------------------
    // Constructor
    // -------------------------------------------------------------------------

    /**
     * Builds a segment tree from {@code arr}.
     *
     * <p>Time: O(n) | Space: O(n).
     *
     * @param arr the source array (non-null, non-empty)
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public SegmentTree(int[] arr) {
        if (arr == null || arr.length == 0)
            throw new IllegalArgumentException("Array must be non-null and non-empty");
        n = arr.length;
        original = Arrays.copyOf(arr, n);
        tree = new int[4 * n];
        build(arr, 1, 0, n - 1);
    }

    // -------------------------------------------------------------------------
    // build
    // -------------------------------------------------------------------------

    /**
     * Recursively builds the segment tree.
     *
     * <p>Time: O(n).
     *
     * @param arr   the source array
     * @param node  current segment tree node index (1-based)
     * @param start left boundary of the segment
     * @param end   right boundary of the segment
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public void build(int[] arr, int node, int start, int end) {
        if (start == end) {
            tree[node] = arr[start];
        } else {
            int mid = (start + end) / 2;
            build(arr, 2 * node,     start, mid);
            build(arr, 2 * node + 1, mid + 1, end);
            tree[node] = tree[2 * node] + tree[2 * node + 1];
        }
    }

    // -------------------------------------------------------------------------
    // query
    // -------------------------------------------------------------------------

    /**
     * Returns the sum of elements in the range {@code [l, r]} (0-indexed, inclusive).
     *
     * <p>Time: O(log n) | Space: O(log n) recursive stack.
     *
     * @param l left index (inclusive, 0-based)
     * @param r right index (inclusive, 0-based)
     * @return sum of arr[l..r]
     * @throws IndexOutOfBoundsException if indices are out of range
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public int query(int l, int r) {
        checkRange(l, r);
        return queryRec(1, 0, n - 1, l, r);
    }

    private int queryRec(int node, int start, int end, int l, int r) {
        if (r < start || end < l) return 0;          // completely outside
        if (l <= start && end <= r) return tree[node]; // completely inside
        int mid = (start + end) / 2;
        return queryRec(2 * node,     start, mid,   l, r)
             + queryRec(2 * node + 1, mid + 1, end, l, r);
    }

    // -------------------------------------------------------------------------
    // update
    // -------------------------------------------------------------------------

    /**
     * Sets {@code arr[i] = val} and updates the tree accordingly.
     *
     * <p>Time: O(log n) | Space: O(log n) recursive stack.
     *
     * @param i   0-based index to update
     * @param val new value
     * @throws IndexOutOfBoundsException if {@code i} is out of range
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public void update(int i, int val) {
        if (i < 0 || i >= n)
            throw new IndexOutOfBoundsException("Index " + i + " out of range [0, " + (n - 1) + "]");
        original[i] = val;
        updateRec(1, 0, n - 1, i, val);
    }

    private void updateRec(int node, int start, int end, int i, int val) {
        if (start == end) {
            tree[node] = val;
            return;
        }
        int mid = (start + end) / 2;
        if (i <= mid) updateRec(2 * node,     start, mid,   i, val);
        else          updateRec(2 * node + 1, mid + 1, end, i, val);
        tree[node] = tree[2 * node] + tree[2 * node + 1];
    }

    // -------------------------------------------------------------------------
    // Helpers
    // -------------------------------------------------------------------------

    private void checkRange(int l, int r) {
        if (l < 0 || r >= n || l > r)
            throw new IndexOutOfBoundsException("Invalid range [" + l + ", " + r + "] for n=" + n);
    }

    /** Returns the number of elements in the original array. */
    public int size() { return n; }

    // -------------------------------------------------------------------------
    // toString
    // -------------------------------------------------------------------------

    /**
     * Returns a string showing the original array and the internal tree array,
     * plus a level-by-level view of tree node values.
     *
     * <p>Time: O(n) | Space: O(n).
     *
     * @return multi-line tree representation
     */
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
        sb.append("SegmentTree (n=").append(n).append("):\n");
        sb.append("  Original : ").append(Arrays.toString(original)).append("\n");

        // Internal array (1-indexed; index 0 unused)
        int used = 4 * n; // upper bound; actual nodes are at most 2*n+1 but we use 4*n to be safe
        sb.append("  tree[]   : [_, ");
        for (int i = 1; i < used; i++) {
            sb.append(tree[i]);
            if (i < used - 1) sb.append(", ");
        }
        sb.append("] (1-indexed, _ = unused index 0)\n");

        // Level view
        sb.append("  Levels (sum at each node):\n");
        int level = 0;
        int start = 1;
        while (start < used) {
            int end = Math.min(start * 2, used);
            sb.append("    L").append(level).append(": ");
            for (int i = start; i < end; i++) {
                sb.append(tree[i]);
                if (i < end - 1) sb.append("  ");
            }
            sb.append("\n");
            start = end;
            level++;
            if (level > 20) break; // safety cap
        }
        return sb.toString();
    }

    // -------------------------------------------------------------------------
    // Main – demo
    // -------------------------------------------------------------------------

    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public static void main(String[] args) {
        System.out.println("=== Segment Tree Demo ===\n");

        int[] arr = {1, 3, 5, 7, 9, 11};
        SegmentTree st = new SegmentTree(arr);
        System.out.println(st);

        // Range queries
        System.out.println("query(1, 3)  = " + st.query(1, 3) + "  (expected 15: 3+5+7)");
        System.out.println("query(0, 5)  = " + st.query(0, 5) + "  (expected 36: sum all)");
        System.out.println("query(2, 4)  = " + st.query(2, 4) + "  (expected 21: 5+7+9)");
        System.out.println("query(0, 0)  = " + st.query(0, 0) + "  (expected 1)");

        // Update
        System.out.println("\nupdate(1, 10)  -- change index 1 from 3 to 10");
        st.update(1, 10);
        System.out.println("query(1, 3)  = " + st.query(1, 3) + "  (expected 22: 10+5+7)");
        System.out.println("query(0, 5)  = " + st.query(0, 5) + "  (expected 43)");
        System.out.println("\nAfter update:");
        System.out.println(st);

        // Another update
        System.out.println("update(5, 100) -- change last element");
        st.update(5, 100);
        System.out.println("query(4, 5)  = " + st.query(4, 5) + "  (expected 109: 9+100)");
    }
}
