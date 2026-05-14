package new_ds;

/**
 * Red-Black Tree — a self-balancing binary search tree that guarantees
 * O(log n) worst-case time for search, insertion, and deletion.
 *
 * <h3>Red-Black Properties</h3>
 * <ol>
 *   <li>Every node is RED or BLACK.</li>
 *   <li>The root is BLACK.</li>
 *   <li>Every leaf (NIL sentinel) is BLACK.</li>
 *   <li>If a node is RED, both its children are BLACK.</li>
 *   <li>All paths from any node to its descendant NIL leaves contain the
 *       same number of BLACK nodes (black-height).</li>
 * </ol>
 *
 * <pre>
 * Time Complexity:
 *   search  – O(log n) worst case
 *   insert  – O(log n) worst case
 *   delete  – O(log n) worst case
 *
 * Space Complexity: O(n)
 * </pre>
 *
 * <p>Implementation follows CLRS 4th ed., Chapter 13.
 */
public class RedBlackTree {

    // -------------------------------------------------------------------------
    // Color constants
    // -------------------------------------------------------------------------

    private static final boolean RED   = true;
    private static final boolean BLACK = false;

    // -------------------------------------------------------------------------
    // Inner node class
    // -------------------------------------------------------------------------

    /**
     * A node in the Red-Black Tree.
     *
     * <p>The sentinel {@code NIL} node is a shared BLACK node used as the
     * leaf / null replacement so that boundary checks remain uniform.
     */
    public static class RBNode {

        /** The integer search key. */
        int key;

        /** {@code RED} or {@code BLACK}. */
        boolean color;

        /** Left child (may be NIL sentinel). */
        RBNode left;

        /** Right child (may be NIL sentinel). */
        RBNode right;

        /** Parent node (NIL for root). */
        RBNode parent;

        /**
         * Constructs an RBNode.
         *
         * @param key   integer key
         * @param color {@link RedBlackTree#RED} or {@link RedBlackTree#BLACK}
         */
        RBNode(int key, boolean color) {
            this.key   = key;
            this.color = color;
        }

        /** Human-readable: "(key, R)" or "(key, B)". */
        @Override
        public String toString() {
            return "(" + key + "," + (color == RED ? "R" : "B") + ")";
        }
    }

    // -------------------------------------------------------------------------
    // Fields
    // -------------------------------------------------------------------------

    /**
     * Sentinel NIL node shared by all leaves and the parent of root.
     * Always BLACK; key is irrelevant.
     */
    private final RBNode NIL;

    /** Root of the tree; points to NIL when tree is empty. */
    private RBNode root;

    /** Number of internal (non-NIL) nodes. */
    private int size;

    // -------------------------------------------------------------------------
    // Constructor
    // -------------------------------------------------------------------------

    /**
     * Creates an empty Red-Black Tree.
     */
    public RedBlackTree() {
        NIL        = new RBNode(0, BLACK);
        NIL.left   = NIL;
        NIL.right  = NIL;
        NIL.parent = NIL;
        root       = NIL;
        size       = 0;
    }

    // -------------------------------------------------------------------------
    // Rotations
    // -------------------------------------------------------------------------

    /**
     * Performs a left rotation around node {@code x}.
     *
     * <pre>
     *     x                y
     *    / \      =>      / \
     *   a   y            x   c
     *      / \          / \
     *     b   c        a   b
     * </pre>
     *
     * @param x the pivot node
     */
    private void rotateLeft(RBNode x) {
        RBNode y = x.right;          // y is x's right child
        x.right  = y.left;           // turn y's left subtree into x's right subtree

        if (y.left != NIL) {
            y.left.parent = x;
        }

        y.parent = x.parent;         // link x's parent to y

        if (x.parent == NIL) {
            root = y;                // x was root
        } else if (x == x.parent.left) {
            x.parent.left  = y;
        } else {
            x.parent.right = y;
        }

        y.left   = x;                // put x on y's left
        x.parent = y;
    }

    /**
     * Performs a right rotation around node {@code x}.
     *
     * <pre>
     *       x              y
     *      / \    =>      / \
     *     y   c          a   x
     *    / \                / \
     *   a   b              b   c
     * </pre>
     *
     * @param x the pivot node
     */
    private void rotateRight(RBNode x) {
        RBNode y = x.left;           // y is x's left child
        x.left   = y.right;          // turn y's right subtree into x's left subtree

        if (y.right != NIL) {
            y.right.parent = x;
        }

        y.parent = x.parent;

        if (x.parent == NIL) {
            root = y;
        } else if (x == x.parent.right) {
            x.parent.right = y;
        } else {
            x.parent.left  = y;
        }

        y.right  = x;
        x.parent = y;
    }

    // -------------------------------------------------------------------------
    // Insert
    // -------------------------------------------------------------------------

    /**
     * Inserts {@code key} into the tree.  Duplicate keys are ignored.
     *
     * <p>Time: O(log n)
     *
     * @param key the integer key to insert
     */
    public void insert(int key) {
        // Standard BST insert.
        RBNode z = new RBNode(key, RED);
        z.left   = NIL;
        z.right  = NIL;
        z.parent = NIL;

        RBNode y = NIL;
        RBNode x = root;

        while (x != NIL) {
            y = x;
            if (z.key < x.key) {
                x = x.left;
            } else if (z.key > x.key) {
                x = x.right;
            } else {
                return; // duplicate — ignore
            }
        }

        z.parent = y;

        if (y == NIL) {
            root = z;
        } else if (z.key < y.key) {
            y.left  = z;
        } else {
            y.right = z;
        }

        size++;
        insertFixup(z);
    }

    /**
     * Restores Red-Black properties after inserting node {@code z}.
     *
     * <p>There are 6 cases (3 symmetric pairs depending on whether z's parent
     * is a left or right child).  Cases 1–3 handle the "parent is left child"
     * scenario; cases 4–6 are mirror images.
     *
     * @param z the newly inserted RED node
     */
    private void insertFixup(RBNode z) {
        while (z.parent.color == RED) {
            // ── Parent is the LEFT child of grandparent ───────────────────────
            if (z.parent == z.parent.parent.left) {
                RBNode uncle = z.parent.parent.right; // uncle = y

                // ── CASE 1 ────────────────────────────────────────────────────
                // Uncle is RED: recolor parent & uncle BLACK, grandparent RED,
                // then move z up to grandparent and repeat.
                if (uncle.color == RED) {
                    z.parent.color         = BLACK;
                    uncle.color            = BLACK;
                    z.parent.parent.color  = RED;
                    z                      = z.parent.parent;

                // ── CASE 2 ────────────────────────────────────────────────────
                // Uncle is BLACK and z is a RIGHT child: rotate left to turn
                // it into Case 3 (z becomes the new "left child" scenario).
                } else {
                    if (z == z.parent.right) {
                        z = z.parent;
                        rotateLeft(z);
                    }
                    // ── CASE 3 ──────────────────────────────────────────────
                    // Uncle is BLACK and z is a LEFT child: recolor and rotate
                    // right to fix the double-red violation.
                    z.parent.color        = BLACK;
                    z.parent.parent.color = RED;
                    rotateRight(z.parent.parent);
                }

            // ── Parent is the RIGHT child of grandparent (mirror of above) ───
            } else {
                RBNode uncle = z.parent.parent.left;

                // ── CASE 4 (mirror of Case 1) ─────────────────────────────────
                if (uncle.color == RED) {
                    z.parent.color        = BLACK;
                    uncle.color           = BLACK;
                    z.parent.parent.color = RED;
                    z                     = z.parent.parent;

                // ── CASE 5 (mirror of Case 2) ─────────────────────────────────
                } else {
                    if (z == z.parent.left) {
                        z = z.parent;
                        rotateRight(z);
                    }
                    // ── CASE 6 (mirror of Case 3) ───────────────────────────
                    z.parent.color        = BLACK;
                    z.parent.parent.color = RED;
                    rotateLeft(z.parent.parent);
                }
            }
        }
        root.color = BLACK; // Property 2: root is always BLACK.
    }

    // -------------------------------------------------------------------------
    // Delete
    // -------------------------------------------------------------------------

    /**
     * Replaces subtree rooted at {@code u} with subtree rooted at {@code v}.
     *
     * @param u node to replace
     * @param v replacement node
     */
    private void transplant(RBNode u, RBNode v) {
        if (u.parent == NIL) {
            root = v;
        } else if (u == u.parent.left) {
            u.parent.left  = v;
        } else {
            u.parent.right = v;
        }
        v.parent = u.parent; // Safe even when v == NIL because NIL.parent is writable.
    }

    /**
     * Returns the node with the minimum key in the subtree rooted at {@code x}.
     *
     * @param x subtree root
     * @return minimum node
     */
    private RBNode minimum(RBNode x) {
        while (x.left != NIL) {
            x = x.left;
        }
        return x;
    }

    /**
     * Deletes the node with the given key.
     *
     * <p>Time: O(log n)
     *
     * @param key the key to remove
     * @return {@code true} if the key was found and deleted
     */
    public boolean delete(int key) {
        RBNode z = searchNode(key);
        if (z == NIL) {
            return false;
        }

        RBNode y             = z;
        boolean yOrigColor   = y.color;
        RBNode  x;

        if (z.left == NIL) {
            // z has no left child.
            x = z.right;
            transplant(z, z.right);
        } else if (z.right == NIL) {
            // z has no right child.
            x = z.left;
            transplant(z, z.left);
        } else {
            // z has two children; y is z's in-order successor.
            y          = minimum(z.right);
            yOrigColor = y.color;
            x          = y.right;

            if (y != z.right) {
                transplant(y, y.right);
                y.right        = z.right;
                y.right.parent = y;
            } else {
                x.parent = y; // needed when x == NIL
            }

            transplant(z, y);
            y.left        = z.left;
            y.left.parent = y;
            y.color       = z.color;
        }

        if (yOrigColor == BLACK) {
            deleteFixup(x);
        }

        size--;
        return true;
    }

    /**
     * Restores Red-Black properties after deleting a BLACK node.
     *
     * <p>Node {@code x} has one extra "black" credit that must be pushed up.
     * There are again 6 cases (3 symmetric pairs).
     *
     * @param x the node that absorbed the extra black credit
     */
    private void deleteFixup(RBNode x) {
        while (x != root && x.color == BLACK) {
            // ── x is LEFT child ───────────────────────────────────────────────
            if (x == x.parent.left) {
                RBNode w = x.parent.right; // w = sibling of x

                // ── CASE 1 ────────────────────────────────────────────────────
                // Sibling w is RED: recolor + rotate to make w BLACK, turning
                // this into one of Cases 2–4.
                if (w.color == RED) {
                    w.color          = BLACK;
                    x.parent.color   = RED;
                    rotateLeft(x.parent);
                    w                = x.parent.right;
                }

                // ── CASE 2 ────────────────────────────────────────────────────
                // Sibling w is BLACK and both of w's children are BLACK:
                // remove one black from x and w, move the extra black up to
                // x's parent.
                if (w.left.color == BLACK && w.right.color == BLACK) {
                    w.color = RED;
                    x       = x.parent;

                } else {
                    // ── CASE 3 ──────────────────────────────────────────────
                    // Sibling w is BLACK, w's left child is RED, w's right is
                    // BLACK: recolor + rotate right to turn it into Case 4.
                    if (w.right.color == BLACK) {
                        w.left.color = BLACK;
                        w.color      = RED;
                        rotateRight(w);
                        w            = x.parent.right;
                    }
                    // ── CASE 4 ──────────────────────────────────────────────
                    // Sibling w is BLACK and w's right child is RED: rotate
                    // left and recolor to eliminate the extra black.
                    w.color          = x.parent.color;
                    x.parent.color   = BLACK;
                    w.right.color    = BLACK;
                    rotateLeft(x.parent);
                    x                = root; // done
                }

            // ── x is RIGHT child (symmetric) ─────────────────────────────────
            } else {
                RBNode w = x.parent.left;

                // ── CASE 5 (mirror of Case 1) ─────────────────────────────────
                if (w.color == RED) {
                    w.color        = BLACK;
                    x.parent.color = RED;
                    rotateRight(x.parent);
                    w              = x.parent.left;
                }

                // ── CASE 6 (mirror of Case 2) ─────────────────────────────────
                if (w.right.color == BLACK && w.left.color == BLACK) {
                    w.color = RED;
                    x       = x.parent;

                } else {
                    // ── CASE 7 (mirror of Case 3) ───────────────────────────
                    if (w.left.color == BLACK) {
                        w.right.color = BLACK;
                        w.color       = RED;
                        rotateLeft(w);
                        w             = x.parent.left;
                    }
                    // ── CASE 8 (mirror of Case 4) ───────────────────────────
                    w.color        = x.parent.color;
                    x.parent.color = BLACK;
                    w.left.color   = BLACK;
                    rotateRight(x.parent);
                    x              = root; // done
                }
            }
        }
        x.color = BLACK;
    }

    // -------------------------------------------------------------------------
    // Search
    // -------------------------------------------------------------------------

    /**
     * Returns the internal RBNode for {@code key}, or NIL if not found.
     * (For internal use by delete.)
     */
    private RBNode searchNode(int key) {
        RBNode curr = root;
        while (curr != NIL) {
            if (key == curr.key)      return curr;
            else if (key < curr.key)  curr = curr.left;
            else                      curr = curr.right;
        }
        return NIL;
    }

    /**
     * Returns {@code true} if {@code key} exists in the tree.
     *
     * <p>Time: O(log n)
     *
     * @param key the key to search for
     * @return {@code true} if found
     */
    public boolean search(int key) {
        return searchNode(key) != NIL;
    }

    // -------------------------------------------------------------------------
    // Traversal / toString
    // -------------------------------------------------------------------------

    /**
     * Appends an inorder traversal of the subtree rooted at {@code node} to
     * {@code sb}.
     */
    private void inorderHelper(RBNode node, StringBuilder sb) {
        if (node != NIL) {
            inorderHelper(node.left, sb);
            sb.append(node).append(" ");
            inorderHelper(node.right, sb);
        }
    }

    /**
     * Returns a string of all nodes in sorted (inorder) order.
     *
     * <p>Each node is printed as {@code (key, R/B)}.
     *
     * @return inorder traversal string
     */
    public String inorder() {
        StringBuilder sb = new StringBuilder();
        inorderHelper(root, sb);
        return sb.toString().trim();
    }

    /**
     * Returns a compact multi-line tree view using a recursive indentation.
     *
     * @return ASCII-art style tree string
     */
    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        toStringHelper(root, sb, "", "");
        return sb.toString();
    }

    private void toStringHelper(RBNode node, StringBuilder sb,
                                String prefix, String childPrefix) {
        if (node == NIL) {
            sb.append(prefix).append("[NIL]\n");
            return;
        }
        sb.append(prefix).append(node).append('\n');
        toStringHelper(node.left,  sb, childPrefix + "├─L─ ", childPrefix + "│    ");
        toStringHelper(node.right, sb, childPrefix + "└─R─ ", childPrefix + "     ");
    }

    /**
     * Returns the number of internal nodes.
     *
     * @return size
     */
    public int size() {
        return size;
    }

    // -------------------------------------------------------------------------
    // Demo main
    // -------------------------------------------------------------------------

    /**
     * Demonstrates insert, delete, search, and inorder traversal.
     *
     * @param args unused
     */
    public static void main(String[] args) {
        RedBlackTree rbt = new RedBlackTree();

        System.out.println("=== Red-Black Tree Demo ===\n");

        int[] keys = {41, 38, 31, 12, 19, 8};
        for (int k : keys) {
            rbt.insert(k);
            System.out.println("Inserted " + k);
        }

        System.out.println("\nTree structure (key, R/B):");
        System.out.println(rbt);

        System.out.println("Inorder: " + rbt.inorder());
        System.out.println("Search 19: " + rbt.search(19));
        System.out.println("Search 99: " + rbt.search(99));

        // Insert more
        for (int k : new int[]{50, 60, 70, 55}) {
            rbt.insert(k);
        }
        System.out.println("\nAfter inserting 50, 60, 70, 55:");
        System.out.println(rbt);
        System.out.println("Inorder: " + rbt.inorder());

        // Delete
        System.out.println("Delete 19 -> " + rbt.delete(19));
        System.out.println("Delete 38 -> " + rbt.delete(38));
        System.out.println("\nAfter deleting 19 and 38:");
        System.out.println(rbt);
        System.out.println("Inorder: " + rbt.inorder());
        System.out.println("Size: " + rbt.size());
    }
}
