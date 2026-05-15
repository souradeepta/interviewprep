package advanced_ds;

import java.util.*;

/**
 * Persistent Segment Tree (Structural Sharing)
 *
 * Time Complexity:
 * - Update: O(log n) per version
 * - Query: O(log n) per query
 * - Space Complexity: O((n + m) * log n) where m = number of updates
 *
 * Use Cases:
 * - Query array state at any previous version
 * - Historical queries on time-versioned data
 * - Undo/redo functionality
 * - Range queries with version history
 * - Counting distinct elements in range (via persistent data structures)
 *
 * Key Insight:
 * - Use structural sharing to avoid duplicating entire trees per update
 * - Only create new nodes along the path modified during update
 * - Reuse unmodified subtrees from previous versions
 * - Allows O(log n) access to any previous version
 */
public class PersistentSegmentTree {

    /**
     * Node for range sum version.
     */
    static class Node {
        long value;
        Node left, right;

        Node(long value) {
            this.value = value;
        }

        Node copy() {
            Node newNode = new Node(this.value);
            newNode.left = this.left;
            newNode.right = this.right;
            return newNode;
        }
    }

    private int n;
    private List<Node> versions;

    /**
     * Initialize persistent segment tree.
     *
     * @param arr Initial array
     */
    public PersistentSegmentTree(int[] arr) {
        this.n = arr.length;
        this.versions = new ArrayList<>();

        if (n > 0) {
            Node root = build(arr, 0, n - 1);
            versions.add(root);
        }
    }

    private Node build(int[] arr, int start, int end) {
        if (start == end) {
            return new Node(arr[start]);
        }

        int mid = (start + end) / 2;
        Node node = new Node(0);
        node.left = build(arr, start, mid);
        node.right = build(arr, mid + 1, end);
        node.value = node.left.value + node.right.value;
        return node;
    }

    private Node update(Node node, int start, int end, int idx, long val) {
        if (node == null) {
            return null;
        }

        if (start == end) {
            return new Node(val);
        }

        Node newNode = node.copy();
        int mid = (start + end) / 2;

        if (idx <= mid) {
            newNode.left = update(node.left, start, mid, idx, val);
        } else {
            newNode.right = update(node.right, mid + 1, end, idx, val);
        }

        long leftVal = newNode.left != null ? newNode.left.value : 0;
        long rightVal = newNode.right != null ? newNode.right.value : 0;
        newNode.value = leftVal + rightVal;

        return newNode;
    }

    /**
     * Create new version with update at index idx to val.
     *
     * @param idx Index to update
     * @param val New value
     * @return Version number (0-indexed)
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public int update(int idx, long val) {
        if (versions.isEmpty()) {
            return -1;
        }

        Node newRoot = update(versions.get(versions.size() - 1), 0, n - 1, idx, val);
        versions.add(newRoot);
        return versions.size() - 1;
    }

    private long query(Node node, int start, int end, int l, int r) {
        if (node == null || start > r || end < l) {
            return 0;
        }

        if (l <= start && end <= r) {
            return node.value;
        }

        int mid = (start + end) / 2;
        long leftSum = query(node.left, start, mid, l, r);
        long rightSum = query(node.right, mid + 1, end, l, r);
        return leftSum + rightSum;
    }

    /**
     * Query sum in range [l, r] for a specific version.
     *
     * @param version Version number
     * @param l Left index (inclusive)
     * @param r Right index (inclusive)
     * @return Sum of elements in range
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public long query(int version, int l, int r) {
        if (version < 0 || version >= versions.size()) {
            return 0;
        }

        return query(versions.get(version), 0, n - 1, l, r);
    }

    /**
     * Query value at index idx for a specific version.
     *
     * @param version Version number
     * @param idx Index
     * @return Value at index
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public long pointQuery(int version, int idx) {
        return query(version, idx, idx);
    }

    /**
     * Get number of versions.
     *
     * @return Number of versions
     */
    public int getNumVersions() {
        return versions.size();
    }

    /**
     * Node for range max version.
     */
    static class MaxNode {
        long value;
        MaxNode left, right;

        MaxNode(long value) {
            this.value = value;
        }

        MaxNode copy() {
            MaxNode newNode = new MaxNode(this.value);
            newNode.left = this.left;
            newNode.right = this.right;
            return newNode;
        }
    }

    /**
     * Persistent segment tree for range max queries.
     */
    static class RangeMaxTree {
        private int n;
        private List<MaxNode> versions;

        RangeMaxTree(int[] arr) {
            this.n = arr.length;
            this.versions = new ArrayList<>();

            if (n > 0) {
                MaxNode root = build(arr, 0, n - 1);
                versions.add(root);
            }
        }

        private MaxNode build(int[] arr, int start, int end) {
            if (start == end) {
                return new MaxNode(arr[start]);
            }

            int mid = (start + end) / 2;
            MaxNode node = new MaxNode(Long.MIN_VALUE);
            node.left = build(arr, start, mid);
            node.right = build(arr, mid + 1, end);
            node.value = Math.max(node.left.value, node.right.value);
            return node;
        }

        private MaxNode update(MaxNode node, int start, int end, int idx, long val) {
            if (node == null) {
                return null;
            }

            if (start == end) {
                return new MaxNode(val);
            }

            MaxNode newNode = node.copy();
            int mid = (start + end) / 2;

            if (idx <= mid) {
                newNode.left = update(node.left, start, mid, idx, val);
            } else {
                newNode.right = update(node.right, mid + 1, end, idx, val);
            }

            long leftVal = newNode.left != null ? newNode.left.value : Long.MIN_VALUE;
            long rightVal = newNode.right != null ? newNode.right.value : Long.MIN_VALUE;
            newNode.value = Math.max(leftVal, rightVal);

            return newNode;
        }

        /**
         * [Brief description]
         *
         * @param [param] [description]
         * @return [description]
         * @time O([complexity])
         */
        public int update(int idx, long val) {
            if (versions.isEmpty()) {
                return -1;
            }

            MaxNode newRoot = update(versions.get(versions.size() - 1), 0, n - 1, idx, val);
            versions.add(newRoot);
            return versions.size() - 1;
        }

        private long queryMax(MaxNode node, int start, int end, int l, int r) {
            if (node == null || start > r || end < l) {
                return Long.MIN_VALUE;
            }

            if (l <= start && end <= r) {
                return node.value;
            }

            int mid = (start + end) / 2;
            long leftMax = queryMax(node.left, start, mid, l, r);
            long rightMax = queryMax(node.right, mid + 1, end, l, r);
            return Math.max(leftMax, rightMax);
        }

        /**
         * [Brief description]
         *
         * @param [param] [description]
         * @return [description]
         * @time O([complexity])
         */
        public long queryMax(int version, int l, int r) {
            if (version < 0 || version >= versions.size()) {
                return Long.MIN_VALUE;
            }

            return queryMax(versions.get(version), 0, n - 1, l, r);
        }

        /**
         * [Brief description]
         *
         * @param [param] [description]
         * @return [description]
         * @time O([complexity])
         */
        public int getNumVersions() {
            return versions.size();
        }
    }

    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public static void main(String[] args) {
        // Example 1: Range sum with version history
        System.out.println("=== Range Sum with Version History ===");
        int[] arr = {1, 2, 3, 4, 5};
        PersistentSegmentTree pst = new PersistentSegmentTree(arr);

        System.out.println("Initial array: [1, 2, 3, 4, 5]");
        System.out.println("Version 0, Query [0, 4]: " + pst.query(0, 0, 4));  // 15

        int v1 = pst.update(2, 10);  // Change arr[2] from 3 to 10
        System.out.println("\nAfter update(2, 10):");
        System.out.println("Version 0, Query [0, 4]: " + pst.query(0, 0, 4));  // 15 (unchanged)
        System.out.println("Version " + v1 + ", Query [0, 4]: " + pst.query(v1, 0, 4));  // 22

        int v2 = pst.update(0, 100);  // Change arr[0] from 1 to 100
        System.out.println("\nAfter update(0, 100):");
        System.out.println("Version 0, Query [0, 4]: " + pst.query(0, 0, 4));  // 15 (unchanged)
        System.out.println("Version " + v1 + ", Query [0, 4]: " + pst.query(v1, 0, 4));  // 22 (unchanged)
        System.out.println("Version " + v2 + ", Query [0, 4]: " + pst.query(v2, 0, 4));  // 122

        // Example 2: Range max with version history
        System.out.println("\n=== Range Max with Version History ===");
        int[] arr2 = {3, 1, 4, 1, 5, 9, 2, 6};
        RangeMaxTree pst2 = new RangeMaxTree(arr2);

        System.out.println("Initial array: [3, 1, 4, 1, 5, 9, 2, 6]");
        System.out.println("Version 0, Query max [0, 7]: " + pst2.queryMax(0, 0, 7));  // 9

        int v3 = pst2.update(1, 100);
        System.out.println("\nAfter update(1, 100):");
        System.out.println("Version 0, Query max [0, 7]: " + pst2.queryMax(0, 0, 7));  // 9
        System.out.println("Version " + v3 + ", Query max [0, 7]: " + pst2.queryMax(v3, 0, 7));  // 100
        System.out.println("Version " + v3 + ", Query max [0, 3]: " + pst2.queryMax(v3, 0, 3));  // 100
    }
}
