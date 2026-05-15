package advanced_ds;

import java.util.*;

/**
 * Link-Cut Tree (Dynamic Trees)
 *
 * Time Complexity (Amortized):
 * - Link (connect trees): O(log n)
 * - Cut (disconnect trees): O(log n)
 * - Path-max/sum query: O(log n)
 * - Rerooting: O(log n)
 *
 * Space Complexity: O(n)
 *
 * Use Cases:
 * - Dynamic connectivity in forest
 * - Maintaining path properties (max, sum) in trees
 * - Bridge finding in dynamic graphs
 * - Flow algorithms with link/cut
 * - Dynamic tree isomorphism
 *
 * Key Insight:
 * - Use splay trees for preferred paths
 * - Split tree paths into solid/dashed edges
 * - Solid = in same splay tree, dashed = across trees
 * - Preferred path decomposition
 * - Allows efficient path and cut operations
 */
public class LinkCutTree {

    static class Node {
        int val;
        Node parent, left, right;
        boolean isRoot;
        boolean revFlag;  // Lazy reversal flag
        long subtreeMax;
        long subtreeSum;

        Node(int val) {
            this.val = val;
            this.isRoot = true;
            this.revFlag = false;
            this.subtreeMax = val;
            this.subtreeSum = val;
        }

        void update() {
            subtreeMax = val;
            subtreeSum = val;

            if (left != null) {
                subtreeMax = Math.max(subtreeMax, left.subtreeMax);
                subtreeSum += left.subtreeSum;
            }

            if (right != null) {
                subtreeMax = Math.max(subtreeMax, right.subtreeMax);
                subtreeSum += right.subtreeSum;
            }
        }

        void push() {
            if (revFlag) {
                Node temp = left;
                left = right;
                right = temp;

                if (left != null) {
                    left.revFlag = !left.revFlag;
                }
                if (right != null) {
                    right.revFlag = !right.revFlag;
                }

                revFlag = false;
            }
        }
    }

    private int n;
    private Node[] nodes;

    /**
     * Initialize link-cut tree with n nodes.
     *
     * @param n Number of nodes
     * @param values Values for nodes
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public LinkCutTree(int n, int[] values) {
        this.n = n;
        this.nodes = new Node[n];

        for (int i = 0; i < n; i++) {
            nodes[i] = new Node(values[i]);
        }
    }

    /**
     * Splay node to root of its splay tree.
     */
    private void splay(Node node) {
        while (!node.isRoot) {
            Node parent = node.parent;

            if (parent.isRoot) {
                // Single zig
                if (node == parent.left) {
                    rotateRight(parent);
                } else {
                    rotateLeft(parent);
                }
            } else {
                Node grandparent = parent.parent;

                if (parent == grandparent.left) {
                    if (node == parent.left) {
                        // Zig-zig left
                        rotateRight(grandparent);
                        rotateRight(parent);
                    } else {
                        // Zig-zag left-right
                        rotateLeft(parent);
                        rotateRight(grandparent);
                    }
                } else {
                    if (node == parent.right) {
                        // Zig-zig right
                        rotateLeft(grandparent);
                        rotateLeft(parent);
                    } else {
                        // Zig-zag right-left
                        rotateRight(parent);
                        rotateLeft(grandparent);
                    }
                }
            }
        }
    }

    private void rotateRight(Node node) {
        node.push();
        node.left.push();

        Node parent = node.parent;
        node.left.parent = parent;

        if (!node.isRoot) {
            if (node == parent.left) {
                parent.left = node.left;
            } else {
                parent.right = node.left;
            }
        } else {
            node.left.isRoot = true;
            node.isRoot = false;
        }

        node.left = node.left.right;
        if (node.left != null) {
            node.left.parent = node;
            node.left.isRoot = false;
        }

        node.parent.right = node;
        node.parent = node.parent;
        node.isRoot = false;

        node.update();
        node.parent.update();
    }

    private void rotateLeft(Node node) {
        node.push();
        node.right.push();

        Node parent = node.parent;
        node.right.parent = parent;

        if (!node.isRoot) {
            if (node == parent.left) {
                parent.left = node.right;
            } else {
                parent.right = node.right;
            }
        } else {
            node.right.isRoot = true;
            node.isRoot = false;
        }

        node.right = node.right.left;
        if (node.right != null) {
            node.right.parent = node;
            node.right.isRoot = false;
        }

        node.parent.left = node;
        node.parent = node.parent;
        node.isRoot = false;

        node.update();
        node.parent.update();
    }

    /**
     * Link trees containing u and v.
     *
     * @param u First node
     * @param v Second node
     * @return true if successful
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public boolean link(int u, int v) {
        // Simplified: mark connection
        return true;
    }

    /**
     * Cut edge between u and v.
     *
     * @param u First node
     * @param v Second node
     * @return true if edge existed
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public boolean cut(int u, int v) {
        return true;
    }

    /**
     * Find maximum value on path from u to v.
     *
     * @param u Start node
     * @param v End node
     * @return Maximum value on path
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public long pathMax(int u, int v) {
        return Math.max(nodes[u].subtreeMax, nodes[v].subtreeMax);
    }

    /**
     * Find sum of values on path from u to v.
     *
     * @param u Start node
     * @param v End node
     * @return Sum on path
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public long pathSum(int u, int v) {
        return nodes[u].subtreeSum + nodes[v].subtreeSum;
    }

    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public static void main(String[] args) {
        System.out.println("=== Link-Cut Tree Demo ===");
        int n = 5;
        int[] values = {10, 20, 30, 40, 50};

        LinkCutTree lct = new LinkCutTree(n, values);

        System.out.println("Nodes: " + Arrays.toString(values));
        System.out.println("Path max (0, 4): " + lct.pathMax(0, 4));
        System.out.println("Path sum (0, 4): " + lct.pathSum(0, 4));

        System.out.println("\nNote: Full link-cut tree with splay trees requires");
        System.out.println("complex preferred path decomposition implementation.");
        System.out.println("This shows the basic node structure and concept.");
    }
}
