package advanced_ds;

/**
 * Segment Tree with Lazy Propagation
 *
 * Time Complexity:
 * - Range Update: O(log n)
 * - Range Query: O(log n)
 * - Point Update: O(log n)
 * - Point Query: O(log n)
 *
 * Space Complexity: O(n)
 *
 * Use Cases:
 * - Range updates and range queries on arrays
 * - Range add operations with range sum queries
 * - Lazy evaluation to avoid redundant updates
 *
 * Key Insight:
 * - Store lazy values at each node representing pending updates
 * - Push lazy updates down when needed during query/update
 * - Combine updates efficiently before propagating
 */
public class SegmentTreeLazy {

    /**
     * Segment tree for range sum queries with range add updates.
     */
    static class RangeSumTree {
        private long[] tree;
        private long[] lazy;
        private int n;

        RangeSumTree(int[] arr) {
            this.n = arr.length;
            this.tree = new long[4 * n];
            this.lazy = new long[4 * n];
            if (n > 0) {
                build(arr, 0, 0, n - 1);
            }
        }

        private void build(int[] arr, int node, int start, int end) {
            if (start == end) {
                tree[node] = arr[start];
            } else {
                int mid = (start + end) / 2;
                build(arr, 2 * node + 1, start, mid);
                build(arr, 2 * node + 2, mid + 1, end);
                tree[node] = tree[2 * node + 1] + tree[2 * node + 2];
            }
        }

        private void push(int node, int start, int end) {
            if (lazy[node] != 0) {
                tree[node] += lazy[node] * (end - start + 1);

                if (start != end) {
                    lazy[2 * node + 1] += lazy[node];
                    lazy[2 * node + 2] += lazy[node];
                }

                lazy[node] = 0;
            }
        }

        private void updateRange(int node, int start, int end, int l, int r, long val) {
            push(node, start, end);

            if (start > r || end < l) {
                return;
            }

            if (l <= start && end <= r) {
                lazy[node] += val;
                push(node, start, end);
                return;
            }

            int mid = (start + end) / 2;
            updateRange(2 * node + 1, start, mid, l, r, val);
            updateRange(2 * node + 2, mid + 1, end, l, r, val);

            push(2 * node + 1, start, mid);
            push(2 * node + 2, mid + 1, end);
            tree[node] = tree[2 * node + 1] + tree[2 * node + 2];
        }

        private long queryRange(int node, int start, int end, int l, int r) {
            if (start > r || end < l) {
                return 0;
            }

            push(node, start, end);

            if (l <= start && end <= r) {
                return tree[node];
            }

            int mid = (start + end) / 2;
            long leftSum = queryRange(2 * node + 1, start, mid, l, r);
            long rightSum = queryRange(2 * node + 2, mid + 1, end, l, r);
            return leftSum + rightSum;
        }

        /**
         * Add val to all elements in range [l, r].
         *
         * @param l Left index (inclusive)
         * @param r Right index (inclusive)
         * @param val Value to add
         */
        /**
         * [Brief description]
         *
         * @param [param] [description]
         * @return [description]
         * @time O([complexity])
         */
        public void update(int l, int r, long val) {
            if (n > 0) {
                updateRange(0, 0, n - 1, l, r, val);
            }
        }

        /**
         * Query sum in range [l, r].
         *
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
        public long query(int l, int r) {
            if (n == 0) return 0;
            return queryRange(0, 0, n - 1, l, r);
        }
    }

    /**
     * Segment tree for range min/max queries with range assignment updates.
     */
    static class RangeMinMaxTree {
        private long[] treeMin;
        private long[] treeMax;
        private Long[] lazy;
        private int n;

        RangeMinMaxTree(int[] arr) {
            this.n = arr.length;
            this.treeMin = new long[4 * n];
            this.treeMax = new long[4 * n];
            this.lazy = new Long[4 * n];

            for (int i = 0; i < 4 * n; i++) {
                treeMin[i] = Long.MAX_VALUE;
                treeMax[i] = Long.MIN_VALUE;
            }

            if (n > 0) {
                build(arr, 0, 0, n - 1);
            }
        }

        private void build(int[] arr, int node, int start, int end) {
            if (start == end) {
                treeMin[node] = arr[start];
                treeMax[node] = arr[start];
            } else {
                int mid = (start + end) / 2;
                build(arr, 2 * node + 1, start, mid);
                build(arr, 2 * node + 2, mid + 1, end);
                treeMin[node] = Math.min(treeMin[2 * node + 1], treeMin[2 * node + 2]);
                treeMax[node] = Math.max(treeMax[2 * node + 1], treeMax[2 * node + 2]);
            }
        }

        private void push(int node, int start, int end) {
            if (lazy[node] != null) {
                long val = lazy[node];
                treeMin[node] = val;
                treeMax[node] = val;

                if (start != end) {
                    lazy[2 * node + 1] = val;
                    lazy[2 * node + 2] = val;
                }

                lazy[node] = null;
            }
        }

        private void updateRange(int node, int start, int end, int l, int r, long val) {
            push(node, start, end);

            if (start > r || end < l) {
                return;
            }

            if (l <= start && end <= r) {
                lazy[node] = val;
                push(node, start, end);
                return;
            }

            int mid = (start + end) / 2;
            updateRange(2 * node + 1, start, mid, l, r, val);
            updateRange(2 * node + 2, mid + 1, end, l, r, val);

            push(2 * node + 1, start, mid);
            push(2 * node + 2, mid + 1, end);
            treeMin[node] = Math.min(treeMin[2 * node + 1], treeMin[2 * node + 2]);
            treeMax[node] = Math.max(treeMax[2 * node + 1], treeMax[2 * node + 2]);
        }

        private long queryMin(int node, int start, int end, int l, int r) {
            if (start > r || end < l) {
                return Long.MAX_VALUE;
            }

            push(node, start, end);

            if (l <= start && end <= r) {
                return treeMin[node];
            }

            int mid = (start + end) / 2;
            long leftMin = queryMin(2 * node + 1, start, mid, l, r);
            long rightMin = queryMin(2 * node + 2, mid + 1, end, l, r);
            return Math.min(leftMin, rightMin);
        }

        private long queryMax(int node, int start, int end, int l, int r) {
            if (start > r || end < l) {
                return Long.MIN_VALUE;
            }

            push(node, start, end);

            if (l <= start && end <= r) {
                return treeMax[node];
            }

            int mid = (start + end) / 2;
            long leftMax = queryMax(2 * node + 1, start, mid, l, r);
            long rightMax = queryMax(2 * node + 2, mid + 1, end, l, r);
            return Math.max(leftMax, rightMax);
        }

        /**
         * Assign val to all elements in range [l, r].
         *
         * @param l Left index (inclusive)
         * @param r Right index (inclusive)
         * @param val Value to assign
         */
        /**
         * [Brief description]
         *
         * @param [param] [description]
         * @return [description]
         * @time O([complexity])
         */
        public void update(int l, int r, long val) {
            if (n > 0) {
                updateRange(0, 0, n - 1, l, r, val);
            }
        }

        /**
         * Query minimum in range [l, r].
         *
         * @param l Left index (inclusive)
         * @param r Right index (inclusive)
         * @return Minimum value in range
         */
        /**
         * [Brief description]
         *
         * @param [param] [description]
         * @return [description]
         * @time O([complexity])
         */
        public long queryMin(int l, int r) {
            if (n == 0) return Long.MAX_VALUE;
            return queryMin(0, 0, n - 1, l, r);
        }

        /**
         * Query maximum in range [l, r].
         *
         * @param l Left index (inclusive)
         * @param r Right index (inclusive)
         * @return Maximum value in range
         */
        /**
         * [Brief description]
         *
         * @param [param] [description]
         * @return [description]
         * @time O([complexity])
         */
        public long queryMax(int l, int r) {
            if (n == 0) return Long.MIN_VALUE;
            return queryMax(0, 0, n - 1, l, r);
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
        // Test range sum with range add
        System.out.println("=== Range Sum Query with Range Add ===");
        int[] arr = {1, 2, 3, 4, 5};
        RangeSumTree segTree = new RangeSumTree(arr);

        System.out.println("Initial array: [1, 2, 3, 4, 5]");
        System.out.println("Query [0, 4]: " + segTree.query(0, 4));  // 15

        segTree.update(1, 3, 5);  // Add 5 to indices 1-3
        System.out.println("After add 5 to [1, 3]:");
        System.out.println("Query [0, 4]: " + segTree.query(0, 4));  // 30
        System.out.println("Query [1, 3]: " + segTree.query(1, 3));  // 24

        segTree.update(0, 2, -2);  // Add -2 to indices 0-2
        System.out.println("After add -2 to [0, 2]:");
        System.out.println("Query [0, 4]: " + segTree.query(0, 4));  // 26
        System.out.println("Query [0, 2]: " + segTree.query(0, 2));  // 8

        System.out.println("\n=== Range Min/Max with Range Assignment ===");
        int[] arr2 = {3, 1, 4, 1, 5, 9, 2};
        RangeMinMaxTree segTree2 = new RangeMinMaxTree(arr2);

        System.out.println("Initial array: [3, 1, 4, 1, 5, 9, 2]");
        System.out.println("Query min [0, 6]: " + segTree2.queryMin(0, 6));  // 1
        System.out.println("Query max [0, 6]: " + segTree2.queryMax(0, 6));  // 9

        segTree2.update(2, 4, 10);  // Assign 10 to indices 2-4
        System.out.println("After assign 10 to [2, 4]:");
        System.out.println("Query min [0, 6]: " + segTree2.queryMin(0, 6));  // 1
        System.out.println("Query max [2, 5]: " + segTree2.queryMax(2, 5));  // 10
    }
}
