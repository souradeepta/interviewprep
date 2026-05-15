package advanced_ds;

import java.util.*;

/**
 * Heavy-Light Decomposition for tree path queries.
 *
 * Time Complexity:
 * - Decomposition: O(n)
 * - Path Query/Update: O(log² n) with segment tree
 * - Point Update: O(log n) with segment tree
 *
 * Space Complexity: O(n)
 *
 * Use Cases:
 * - Answering min/max/sum queries on tree paths
 * - Updating values on tree paths
 * - LCA (Lowest Common Ancestor) queries with path info
 *
 * Key Insight:
 * - Decompose tree into heavy paths (heavy child = child with most vertices in subtree)
 * - Each vertex has exactly one heavy child
 * - Tree has O(log n) heavy paths from root to any node
 * - Use segment tree to query along paths
 */
public class HeavyLightDecomposition {
    static class SegmentTree {
        int[] tree;
        int n;

        SegmentTree(int[] arr) {
            this.n = arr.length;
            this.tree = new int[4 * n];
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
                tree[node] = Math.max(tree[2 * node + 1], tree[2 * node + 2]);
            }
        }

        void update(int idx, int val) {
            update(0, 0, n - 1, idx, val);
        }

        private void update(int node, int start, int end, int idx, int val) {
            if (start == end) {
                tree[node] = val;
            } else {
                int mid = (start + end) / 2;
                if (idx <= mid) {
                    update(2 * node + 1, start, mid, idx, val);
                } else {
                    update(2 * node + 2, mid + 1, end, idx, val);
                }
                tree[node] = Math.max(tree[2 * node + 1], tree[2 * node + 2]);
            }
        }

        int query(int l, int r) {
            if (l > r || n == 0) return 0;
            return query(0, 0, n - 1, l, r);
        }

        private int query(int node, int start, int end, int l, int r) {
            if (r < start || end < l) return 0;
            if (l <= start && end <= r) return tree[node];
            int mid = (start + end) / 2;
            int leftMax = query(2 * node + 1, start, mid, l, r);
            int rightMax = query(2 * node + 2, mid + 1, end, l, r);
            return Math.max(leftMax, rightMax);
        }
    }

    private int n;
    private int[] values;
    private List<Integer>[] adj;
    private int[] parent, depth, subtreeSize, heavyChild, chainId, posInChain, chainHead;
    private List<List<Integer>> chainNodes;
    private List<SegmentTree> segTrees;

    /**
     * Initialize HLD.
     *
     * @param n Number of vertices (0 to n-1)
     * @param edges List of edges (u, v)
     * @param values Vertex values
     */
    @SuppressWarnings("unchecked")
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public HeavyLightDecomposition(int n, List<int[]> edges, int[] values) {
        this.n = n;
        this.values = values.clone();
        this.adj = new ArrayList[n];
        for (int i = 0; i < n; i++) {
            this.adj[i] = new ArrayList<>();
        }

        for (int[] edge : edges) {
            this.adj[edge[0]].add(edge[1]);
            this.adj[edge[1]].add(edge[0]);
        }

        // Initialize HLD arrays
        this.parent = new int[n];
        this.depth = new int[n];
        this.subtreeSize = new int[n];
        this.heavyChild = new int[n];
        this.chainId = new int[n];
        this.posInChain = new int[n];
        this.chainHead = new int[n];
        this.chainNodes = new ArrayList<>();
        this.segTrees = new ArrayList<>();

        Arrays.fill(heavyChild, -1);
        Arrays.fill(chainId, -1);
        Arrays.fill(posInChain, -1);
        Arrays.fill(chainHead, -1);

        if (n > 0) {
            dfs1(0, -1, 0);
            dfs2(0, 0);
        }
    }

    private void dfs1(int u, int p, int d) {
        parent[u] = p;
        depth[u] = d;
        subtreeSize[u] = 1;

        for (int v : adj[u]) {
            if (v != p) {
                dfs1(v, u, d + 1);
                subtreeSize[u] += subtreeSize[v];

                if (heavyChild[u] == -1 || subtreeSize[v] > subtreeSize[heavyChild[u]]) {
                    heavyChild[u] = v;
                }
            }
        }
    }

    private void dfs2(int u, int cid) {
        chainId[u] = cid;

        while (cid >= chainNodes.size()) {
            chainNodes.add(new ArrayList<>());
        }

        if (chainNodes.get(cid).isEmpty()) {
            chainHead[cid] = u;
        }

        posInChain[u] = chainNodes.get(cid).size();
        chainNodes.get(cid).add(u);

        if (heavyChild[u] != -1) {
            dfs2(heavyChild[u], cid);
        }

        for (int v : adj[u]) {
            if (v != parent[u] && v != heavyChild[u]) {
                dfs2(v, chainNodes.size());
            }
        }
    }

    private void buildSegmentTrees() {
        segTrees.clear();
        for (List<Integer> chain : chainNodes) {
            int[] chainValues = new int[chain.size()];
            for (int i = 0; i < chain.size(); i++) {
                chainValues[i] = values[chain.get(i)];
            }
            segTrees.add(new SegmentTree(chainValues));
        }
    }

    /**
     * Update value at vertex u.
     *
     * @param u Vertex index
     * @param val New value
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public void update(int u, int val) {
        values[u] = val;
        buildSegmentTrees();
    }

    /**
     * Query max value on path from u to v.
     *
     * @param u Start vertex
     * @param v End vertex
     * @return Maximum value on path u-v
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public int queryPath(int u, int v) {
        if (segTrees.isEmpty()) {
            buildSegmentTrees();
        }

        int result = 0;

        // Bring u and v to same level
        while (depth[u] > depth[v]) {
            result = Math.max(result, queryUp(u));
            u = parent[u];
        }
        while (depth[v] > depth[u]) {
            result = Math.max(result, queryUp(v));
            v = parent[v];
        }

        // Move both up simultaneously
        while (u != v) {
            result = Math.max(result, queryUp(u));
            result = Math.max(result, queryUp(v));
            u = parent[u];
            v = parent[v];
        }

        result = Math.max(result, values[u]);
        return result;
    }

    private int queryUp(int u) {
        int cid = chainId[u];
        int start = posInChain[chainHead[cid]];
        int end = posInChain[u];
        return segTrees.get(cid).query(start, end);
    }

    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public static void main(String[] args) {
        // Example: Tree with path queries
        //     0
        //    / \
        //   1   2
        //  / \
        // 3   4

        int n = 5;
        List<int[]> edges = Arrays.asList(
                new int[]{0, 1}, new int[]{0, 2},
                new int[]{1, 3}, new int[]{1, 4}
        );
        int[] values = {10, 20, 30, 40, 50};

        HeavyLightDecomposition hld = new HeavyLightDecomposition(n, edges, values);

        System.out.println("Path 3->4 max value: " + hld.queryPath(3, 4));  // 40, 20
        System.out.println("Path 4->5 max value: " + hld.queryPath(4, 4));  // 50
        System.out.println("Path 2->4 max value: " + hld.queryPath(2, 4));  // 30, 10, 20, 50

        hld.update(1, 100);
        System.out.println("After update(1, 100):");
        System.out.println("Path 3->4 max value: " + hld.queryPath(3, 4));  // 40, 100
    }
}
