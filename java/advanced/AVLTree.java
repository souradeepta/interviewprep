package advanced;

/**
 * Self-balancing AVL Tree with {@code int} keys.
 *
 * <p>An AVL tree maintains the <em>height-balance property</em>: for every node the
 * difference between the heights of its left and right subtrees (the balance factor)
 * is at most 1.  Rotations (LL, RR, LR, RL) restore the property after mutations.
 *
 * <p>Time complexities:
 * <ul>
 *   <li>insert  – O(log n)</li>
 *   <li>delete  – O(log n)</li>
 *   <li>search  – O(log n)</li>
 *   <li>height  – O(1) (cached per node)</li>
 * </ul>
 *
 * <p>Space complexity: O(n) for the tree; O(log n) auxiliary for recursive calls.
 */
public class AVLTree {

    // -------------------------------------------------------------------------
    // Inner Node
    // -------------------------------------------------------------------------

    private static class Node {
        int key;
        int height;   // height of subtree rooted at this node (leaf = 0)
        Node left, right;

        Node(int key) {
            this.key = key;
            this.height = 0;
        }
    }

    // -------------------------------------------------------------------------
    // Fields
    // -------------------------------------------------------------------------

    private Node root;
    private int size;

    // -------------------------------------------------------------------------
    // Height helpers
    // -------------------------------------------------------------------------

    /**
     * Returns the cached height of {@code node}, or -1 for null.
     *
     * <p>Time: O(1).
     *
     * @param node the node (may be null)
     * @return height
     */
    public int height(Node node) {
        return node == null ? -1 : node.height;
    }

    /** Returns the height of the root (whole tree). */
    public int height() {
        return height(root);
    }

    private void updateHeight(Node node) {
        node.height = 1 + Math.max(height(node.left), height(node.right));
    }

    // -------------------------------------------------------------------------
    // Balance factor
    // -------------------------------------------------------------------------

    /**
     * Returns the balance factor of {@code node}: height(left) - height(right).
     *
     * <p>Time: O(1).
     *
     * @param node the node
     * @return balance factor in [-2, 2] during rebalancing
     */
    public int getBalance(Node node) {
        return node == null ? 0 : height(node.left) - height(node.right);
    }

    // -------------------------------------------------------------------------
    // Rotations
    // -------------------------------------------------------------------------

    /**
     * Performs a <em>left rotation</em> around {@code y}.
     *
     * <pre>
     *    y                  x
     *   / \               /   \
     *  T1   x    -->    y      xR
     *      / \         / \
     *    xL   xR      T1  xL
     * </pre>
     *
     * <p>Time: O(1).
     *
     * @param y the pivot node
     * @return the new root of this subtree
     */
    public Node rotateLeft(Node y) {
        Node x  = y.right;
        Node xL = x.left;

        x.left  = y;
        y.right = xL;

        updateHeight(y);
        updateHeight(x);

        return x;
    }

    /**
     * Performs a <em>right rotation</em> around {@code y}.
     *
     * <pre>
     *      y              x
     *     / \           /   \
     *    x   T3  -->  xL     y
     *   / \                 / \
     * xL   xR             xR   T3
     * </pre>
     *
     * <p>Time: O(1).
     *
     * @param y the pivot node
     * @return the new root of this subtree
     */
    public Node rotateRight(Node y) {
        Node x  = y.left;
        Node xR = x.right;

        x.right = y;
        y.left  = xR;

        updateHeight(y);
        updateHeight(x);

        return x;
    }

    // -------------------------------------------------------------------------
    // Rebalance
    // -------------------------------------------------------------------------

    private Node rebalance(Node node) {
        updateHeight(node);
        int balance = getBalance(node);

        // Left Heavy
        if (balance > 1) {
            if (getBalance(node.left) < 0) {          // LR case
                node.left = rotateLeft(node.left);
            }
            return rotateRight(node);                  // LL case
        }

        // Right Heavy
        if (balance < -1) {
            if (getBalance(node.right) > 0) {         // RL case
                node.right = rotateRight(node.right);
            }
            return rotateLeft(node);                   // RR case
        }

        return node; // already balanced
    }

    // -------------------------------------------------------------------------
    // Insert
    // -------------------------------------------------------------------------

    /**
     * Inserts {@code key} into the AVL tree.  Duplicate keys are ignored.
     *
     * <p>Time: O(log n) | Space: O(log n).
     *
     * @param key the key to insert
     */
    public void insert(int key) {
        root = insertRec(root, key);
    }

    private Node insertRec(Node node, int key) {
        if (node == null) {
            size++;
            return new Node(key);
        }
        if (key < node.key)      node.left  = insertRec(node.left,  key);
        else if (key > node.key) node.right = insertRec(node.right, key);
        else return node; // duplicate

        return rebalance(node);
    }

    // -------------------------------------------------------------------------
    // Delete
    // -------------------------------------------------------------------------

    /**
     * Deletes {@code key} from the AVL tree, rebalancing as necessary.
     *
     * <p>Time: O(log n) | Space: O(log n).
     *
     * @param key the key to delete
     */
    public void delete(int key) {
        root = deleteRec(root, key);
    }

    private Node deleteRec(Node node, int key) {
        if (node == null) return null;

        if (key < node.key) {
            node.left = deleteRec(node.left, key);
        } else if (key > node.key) {
            node.right = deleteRec(node.right, key);
        } else {
            size--;
            // Case 1 & 2: zero or one child
            if (node.left == null) return node.right;
            if (node.right == null) return node.left;
            // Case 3: two children – replace with in-order successor
            Node successor = findMin(node.right);
            node.key = successor.key;
            size++; // deleteRec will decrement again
            node.right = deleteRec(node.right, successor.key);
        }
        return rebalance(node);
    }

    private Node findMin(Node node) {
        while (node.left != null) node = node.left;
        return node;
    }

    // -------------------------------------------------------------------------
    // Search
    // -------------------------------------------------------------------------

    /**
     * Returns {@code true} if {@code key} is present in the AVL tree.
     *
     * <p>Time: O(log n) | Space: O(1).
     *
     * @param key the key to search for
     * @return {@code true} if found
     */
    public boolean search(int key) {
        Node cur = root;
        while (cur != null) {
            if      (key < cur.key) cur = cur.left;
            else if (key > cur.key) cur = cur.right;
            else return true;
        }
        return false;
    }

    // -------------------------------------------------------------------------
    // Size
    // -------------------------------------------------------------------------

    /**
     * Returns the number of keys in the AVL tree.
     *
     * <p>Time: O(1).
     *
     * @return size
     */
    public int size() { return size; }

    // -------------------------------------------------------------------------
    // ASCII tree print (toString)
    // -------------------------------------------------------------------------

    /**
     * Returns a multi-line ASCII representation showing keys and balance factors.
     *
     * <p>Time: O(n) | Space: O(n).
     *
     * @return ASCII tree string
     */
    @Override
    public String toString() {
        if (root == null) return "(empty tree)";
        StringBuilder sb = new StringBuilder();
        buildAscii(sb, root, "", "");
        return sb.toString();
    }

    private void buildAscii(StringBuilder sb, Node node, String prefix, String childPrefix) {
        if (node == null) return;
        sb.append(prefix)
          .append(node.key)
          .append(" (h=").append(node.height)
          .append(", bf=").append(getBalance(node))
          .append(")\n");
        if (node.left != null || node.right != null) {
            buildAscii(sb, node.right, childPrefix + "├── R: ", childPrefix + "│   ");
            buildAscii(sb, node.left,  childPrefix + "└── L: ", childPrefix + "    ");
        }
    }

    // -------------------------------------------------------------------------
    // Main – demo
    // -------------------------------------------------------------------------

    public static void main(String[] args) {
        AVLTree avl = new AVLTree();

        System.out.println("=== AVL Tree Demo ===\n");

        // Insert – triggers various rotations
        int[] keys = {10, 20, 30, 40, 50, 25};
        for (int k : keys) {
            avl.insert(k);
            System.out.println("After insert(" + k + "):");
            System.out.println(avl);
        }

        System.out.println("Size  : " + avl.size());
        System.out.println("Height: " + avl.height());

        // Search
        System.out.println("\nSearch 25 : " + avl.search(25));
        System.out.println("Search 99 : " + avl.search(99));

        // Delete
        System.out.println("\nDelete 10:");
        avl.delete(10);
        System.out.println(avl);

        System.out.println("Delete 30:");
        avl.delete(30);
        System.out.println(avl);

        System.out.println("Delete 40 (two children case):");
        avl.delete(40);
        System.out.println(avl);

        // Stress test – insert descending (would degenerate in plain BST)
        AVLTree avl2 = new AVLTree();
        System.out.println("Descending insert 20..1 – height should be ~4:");
        for (int i = 20; i >= 1; i--) avl2.insert(i);
        System.out.println("Height: " + avl2.height() + "  (log2(20) ≈ 4.3)");
        System.out.println(avl2);
    }
}
