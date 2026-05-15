package advanced_ds;

/**
 * Van Emde Boas Tree (VEB Tree)
 *
 * Time Complexity:
 * - Insert: O(log log U) where U = universe size
 * - Delete: O(log log U)
 * - Search: O(log log U)
 * - Min/Max: O(1)
 * - Successor/Predecessor: O(log log U)
 *
 * Space Complexity: O(U)
 *
 * Use Cases:
 * - Dictionary operations on finite universe of integers [0, U)
 * - When keys are small integers (better than general BSTs)
 * - Finding next/previous element
 * - Bit-manipulation heavy algorithms
 *
 * Key Insight:
 * - Recursively partition universe into sqrt(U) blocks
 * - Each block is itself a VEB tree on universe of size sqrt(U)
 * - Track min/max globally for O(1) access
 * - Successor search only needs to check one block + recursive call
 */
public class VanEmdoBoasTree {

    private int u;
    private Integer min, max;
    private int sqrtU;
    private VanEmdoBoasTree summary;
    private VanEmdoBoasTree[] clusters;
    private boolean[] bits;  // For base case u <= 2

    /**
     * Initialize VEB tree.
     *
     * @param universeSize Size of universe [0, universeSize)
     */
    public VanEmdoBoasTree(int universeSize) {
        this.u = universeSize;
        this.min = null;
        this.max = null;

        if (universeSize <= 1) {
            return;
        }

        if (universeSize == 2) {
            this.bits = new boolean[2];
            return;
        }

        this.sqrtU = (int) Math.sqrt(universeSize) + 1;
        this.summary = new VanEmdoBoasTree(sqrtU);
        this.clusters = new VanEmdoBoasTree[sqrtU];
        for (int i = 0; i < sqrtU; i++) {
            this.clusters[i] = new VanEmdoBoasTree(sqrtU);
        }
    }

    private int high(int x) {
        return x / sqrtU;
    }

    private int low(int x) {
        return x % sqrtU;
    }

    private int index(int high, int low) {
        return high * sqrtU + low;
    }

    /**
     * Insert element x.
     *
     * @param x Element to insert
     */
    public void insert(int x) {
        if (x < 0 || x >= u) {
            return;
        }

        if (u == 1) {
            return;
        }

        if (u == 2) {
            bits[x] = true;
            if (min == null) {
                min = x;
            }
            max = x;
            return;
        }

        if (min == null) {
            min = x;
            max = x;
            return;
        }

        if (x == min || x == max) {
            return;
        }

        if (x < min) {
            int temp = x;
            x = min;
            min = temp;
        }

        if (x > max) {
            max = x;
        }

        int h = high(x);
        int l = low(x);

        if (clusters[h].min == null) {
            summary.insert(h);
        }

        clusters[h].insert(l);
    }

    /**
     * Delete element x.
     *
     * @param x Element to delete
     */
    public void delete(int x) {
        if (x < 0 || x >= u) {
            return;
        }

        if (u == 1) {
            return;
        }

        if (u == 2) {
            bits[x] = false;
            if ((bits[0] && !bits[1]) || (!bits[0] && bits[1])) {
                min = max = bits[0] ? 0 : 1;
            } else {
                min = max = null;
            }
            return;
        }

        if (min == max && min == x) {
            min = null;
            max = null;
            return;
        }

        if (x == min) {
            Integer firstCluster = summary.min;
            if (firstCluster != null) {
                x = index(firstCluster, clusters[firstCluster].min);
            }
            min = x;
            return;
        }

        int h = high(x);
        int l = low(x);

        clusters[h].delete(l);

        if (clusters[h].min == null) {
            summary.delete(h);
        }
    }

    /**
     * Check if x is in tree.
     *
     * @param x Element to check
     * @return true if x is in tree
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public boolean member(int x) {
        if (x < 0 || x >= u) {
            return false;
        }

        if (x == min || x == max) {
            return true;
        }

        if (u == 1) {
            return false;
        }

        if (u == 2) {
            return bits[x];
        }

        int h = high(x);
        int l = low(x);

        return clusters[h].member(l);
    }

    /**
     * Find successor of x.
     *
     * @param x Element
     * @return Successor of x, or null if none
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public Integer successor(int x) {
        if (u == 1) {
            return null;
        }

        if (u == 2) {
            if (x < 1 && bits[1]) {
                return 1;
            }
            return null;
        }

        if (x < min) {
            return min;
        }

        if (x >= max) {
            return null;
        }

        int h = high(x);
        int l = low(x);

        if (l < clusters[h].max) {
            Integer succ = clusters[h].successor(l);
            if (succ != null) {
                return index(h, succ);
            }
        }

        Integer nextCluster = summary.successor(h);
        if (nextCluster == null) {
            return null;
        }

        return index(nextCluster, clusters[nextCluster].min);
    }

    /**
     * Find predecessor of x.
     *
     * @param x Element
     * @return Predecessor of x, or null if none
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public Integer predecessor(int x) {
        if (u == 1) {
            return null;
        }

        if (u == 2) {
            if (x > 0 && bits[0]) {
                return 0;
            }
            return null;
        }

        if (x > max) {
            return max;
        }

        if (x <= min) {
            return null;
        }

        int h = high(x);
        int l = low(x);

        if (l > clusters[h].min) {
            Integer pred = clusters[h].predecessor(l);
            if (pred != null) {
                return index(h, pred);
            }
        }

        Integer prevCluster = summary.predecessor(h);
        if (prevCluster == null) {
            return min < x ? min : null;
        }

        return index(prevCluster, clusters[prevCluster].max);
    }

    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public static void main(String[] args) {
        // Example 1: Basic operations
        System.out.println("=== Example 1: Basic Operations ===");
        VanEmdoBoasTree veb = new VanEmdoBoasTree(16);

        int[] elements = {1, 3, 5, 7, 9, 12, 14};
        System.out.print("Inserting: [");
        for (int i = 0; i < elements.length; i++) {
            if (i > 0) System.out.print(", ");
            System.out.print(elements[i]);
            veb.insert(elements[i]);
        }
        System.out.println("]");

        System.out.println("Min: " + veb.min + ", Max: " + veb.max);

        for (int x : new int[]{0, 3, 5, 8, 14}) {
            System.out.println(x + " in tree: " + veb.member(x));
        }

        // Example 2: Successor/Predecessor
        System.out.println("\n=== Example 2: Successor/Predecessor ===");
        for (int x : new int[]{3, 5, 7, 12, 15}) {
            Integer succ = veb.successor(x);
            Integer pred = veb.predecessor(x);
            System.out.println("x=" + x + ": successor=" + succ + ", predecessor=" + pred);
        }

        // Example 3: Deletion
        System.out.println("\n=== Example 3: Deletion ===");
        System.out.println("Deleting 5...");
        veb.delete(5);
        System.out.println("5 in tree: " + veb.member(5));
        System.out.println("Successor of 3: " + veb.successor(3));

        // Example 4: Larger universe
        System.out.println("\n=== Example 4: Larger Universe (U=256) ===");
        VanEmdoBoasTree veb2 = new VanEmdoBoasTree(256);
        int[] elements2 = {10, 50, 100, 150, 200, 250};
        System.out.print("Elements: [");
        for (int i = 0; i < elements2.length; i++) {
            if (i > 0) System.out.print(", ");
            System.out.print(elements2[i]);
            veb2.insert(elements2[i]);
        }
        System.out.println("]");

        System.out.println("Min: " + veb2.min + ", Max: " + veb2.max);
        System.out.println("Successor of 100: " + veb2.successor(100));
        System.out.println("Predecessor of 150: " + veb2.predecessor(150));
    }
}
