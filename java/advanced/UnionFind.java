package advanced;

import java.util.Arrays;

/**
 * Disjoint Set Union (Union-Find) with path compression and union by rank.
 *
 * <p>Supports {@code n} elements identified by integers in [0, n-1].
 *
 * <p>Both optimisations together yield an inverse-Ackermann amortised cost:
 * <ul>
 *   <li>find  – O(α(n)) amortised ≈ O(1) practically</li>
 *   <li>union – O(α(n)) amortised ≈ O(1) practically</li>
 * </ul>
 *
 * <p>Space complexity: O(n).
 */
public class UnionFind {

    // -------------------------------------------------------------------------
    // Fields
    // -------------------------------------------------------------------------

    private final int[] parent; // parent[i] = parent of element i; parent[root] = root
    private final int[] rank;   // rank[i] = upper bound on the height of the subtree rooted at i
    private int numComponents;  // number of disjoint components

    // -------------------------------------------------------------------------
    // Constructor
    // -------------------------------------------------------------------------

    /**
     * Creates a Union-Find structure for {@code n} elements.
     * Initially every element is its own component (n components).
     *
     * <p>Time: O(n) | Space: O(n).
     *
     * @param n number of elements (n >= 1)
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public UnionFind(int n) {
        if (n < 1) throw new IllegalArgumentException("n must be >= 1");
        parent = new int[n];
        rank   = new int[n];
        numComponents = n;
        for (int i = 0; i < n; i++) parent[i] = i; // each element is its own root
    }

    // -------------------------------------------------------------------------
    // find (with path compression)
    // -------------------------------------------------------------------------

    /**
     * Returns the representative (root) of the component containing element {@code x}.
     *
     * <p><em>Path compression</em>: every node on the path from {@code x} to the root
     * is directly attached to the root, flattening the tree for future calls.
     *
     * <p>Time: O(α(n)) amortised | Space: O(1) iterative.
     *
     * @param x element index (0-indexed)
     * @return root representative of x's component
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public int find(int x) {
        checkElement(x);
        // Path compression – iterative two-pass variant
        int root = x;
        while (parent[root] != root) root = parent[root];
        // Second pass: point everything on the path directly to root
        while (parent[x] != root) {
            int next = parent[x];
            parent[x] = root;
            x = next;
        }
        return root;
    }

    // -------------------------------------------------------------------------
    // union (by rank)
    // -------------------------------------------------------------------------

    /**
     * Merges the components containing {@code x} and {@code y}.
     *
     * <p><em>Union by rank</em>: the root of the smaller-rank tree is attached under
     * the root of the larger-rank tree, keeping the trees shallow.
     *
     * <p>Time: O(α(n)) amortised | Space: O(1).
     *
     * @param x first element
     * @param y second element
     * @return {@code true} if the two elements were in different components (a merge occurred)
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public boolean union(int x, int y) {
        int rootX = find(x);
        int rootY = find(y);
        if (rootX == rootY) return false; // already in same component

        // Attach smaller-rank tree under larger-rank tree
        if (rank[rootX] < rank[rootY]) {
            parent[rootX] = rootY;
        } else if (rank[rootX] > rank[rootY]) {
            parent[rootY] = rootX;
        } else {
            // Same rank: pick one as root, increment its rank
            parent[rootY] = rootX;
            rank[rootX]++;
        }
        numComponents--;
        return true;
    }

    // -------------------------------------------------------------------------
    // connected
    // -------------------------------------------------------------------------

    /**
     * Returns {@code true} if {@code x} and {@code y} belong to the same component.
     *
     * <p>Time: O(α(n)) amortised | Space: O(1).
     *
     * @param x first element
     * @param y second element
     * @return {@code true} if connected
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public boolean connected(int x, int y) {
        return find(x) == find(y);
    }

    // -------------------------------------------------------------------------
    // getNumComponents
    // -------------------------------------------------------------------------

    /**
     * Returns the current number of disjoint components.
     *
     * <p>Time: O(1) | Space: O(1).
     *
     * @return number of components
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public int getNumComponents() {
        return numComponents;
    }

    // -------------------------------------------------------------------------
    // size of a component
    // -------------------------------------------------------------------------

    /**
     * Returns the number of elements in the component containing {@code x}.
     *
     * <p>Time: O(n) | Space: O(1).  (For O(α(n)) maintain a size[] array instead.)
     *
     * @param x element index
     * @return size of x's component
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public int componentSize(int x) {
        int root = find(x);
        int count = 0;
        for (int i = 0; i < parent.length; i++) {
            if (find(i) == root) count++;
        }
        return count;
    }

    // -------------------------------------------------------------------------
    // Helpers
    // -------------------------------------------------------------------------

    private void checkElement(int x) {
        if (x < 0 || x >= parent.length)
            throw new IndexOutOfBoundsException("Element " + x + " out of range [0, " + (parent.length - 1) + "]");
    }

    // -------------------------------------------------------------------------
    // toString
    // -------------------------------------------------------------------------

    /**
     * Returns a string showing the parent array, rank array, and component groups.
     *
     * <p>Time: O(n log n) | Space: O(n).
     *
     * @return multi-line Union-Find state string
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
        int n = parent.length;
        StringBuilder sb = new StringBuilder();
        sb.append("UnionFind (n=").append(n)
          .append(", components=").append(numComponents).append("):\n");

        // Compute current roots (after path compression may update parent)
        int[] roots = new int[n];
        for (int i = 0; i < n; i++) roots[i] = find(i);

        sb.append("  index  : ");
        for (int i = 0; i < n; i++) sb.append(String.format("%3d", i));
        sb.append("\n  parent : ");
        for (int i = 0; i < n; i++) sb.append(String.format("%3d", parent[i]));
        sb.append("\n  rank   : ");
        for (int i = 0; i < n; i++) sb.append(String.format("%3d", rank[i]));
        sb.append("\n  root   : ");
        for (int i = 0; i < n; i++) sb.append(String.format("%3d", roots[i]));
        sb.append("\n");

        // Group elements by component
        sb.append("  Components:\n");
        java.util.Map<Integer, java.util.List<Integer>> groups = new java.util.TreeMap<>();
        for (int i = 0; i < n; i++) {
            groups.computeIfAbsent(roots[i], k -> new java.util.ArrayList<>()).add(i);
        }
        for (java.util.Map.Entry<Integer, java.util.List<Integer>> e : groups.entrySet()) {
            sb.append("    root=").append(e.getKey()).append(" -> ").append(e.getValue()).append("\n");
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
        System.out.println("=== Union-Find Demo ===\n");

        UnionFind uf = new UnionFind(10);
        System.out.println("Initial state (10 elements):");
        System.out.println(uf);

        // Union operations
        System.out.println("union(0,1), union(2,3), union(4,5)");
        uf.union(0, 1);
        uf.union(2, 3);
        uf.union(4, 5);
        System.out.println(uf);

        System.out.println("union(6,7), union(8,9)");
        uf.union(6, 7);
        uf.union(8, 9);
        System.out.println(uf);

        System.out.println("union(0,2), union(4,6)");
        uf.union(0, 2);
        uf.union(4, 6);
        System.out.println(uf);

        System.out.println("union(0,4) -- merges two big components");
        uf.union(0, 4);
        System.out.println(uf);

        // Queries
        System.out.println("connected(1, 5) : " + uf.connected(1, 5) + "  (expected true)");
        System.out.println("connected(1, 8) : " + uf.connected(1, 8) + "  (expected false)");
        System.out.println("find(3)         : " + uf.find(3));
        System.out.println("getNumComponents: " + uf.getNumComponents() + "  (expected 3)");
        System.out.println("componentSize(0): " + uf.componentSize(0) + "  (expected 8)");

        // Path compression visible
        System.out.println("\nAfter find calls (path compression flattens parent array):");
        System.out.println(uf);
    }
}
