package advanced;

import java.util.ArrayList;
import java.util.List;

/**
 * B-Tree of minimum degree {@code t}.
 *
 * <p>A B-Tree of degree {@code t} satisfies:
 * <ol>
 *   <li>Every node has at most {@code 2t - 1} keys.</li>
 *   <li>Every non-root node has at least {@code t - 1} keys.</li>
 *   <li>Every internal node with {@code k} keys has {@code k + 1} children.</li>
 *   <li>All leaves are at the same depth.</li>
 * </ol>
 *
 * <p>Time complexities (n = total keys, h = height ≈ log_t(n)):
 * <ul>
 *   <li>search – O(t * log_t(n)) = O(log n)</li>
 *   <li>insert – O(t * log_t(n)) = O(log n)</li>
 *   <li>delete – O(t * log_t(n)) = O(log n)</li>
 * </ul>
 *
 * <p>Space complexity: O(n).
 */
public class BTree {

    // -------------------------------------------------------------------------
    // BTreeNode inner class
    // -------------------------------------------------------------------------

    /**
     * A node in the B-Tree.
     */
    static class BTreeNode {
        int[]       keys;
        BTreeNode[] children;
        int         n;        // current number of keys
        boolean     leaf;

        BTreeNode(int t, boolean leaf) {
            this.leaf     = leaf;
            this.keys     = new int[2 * t - 1];
            this.children = new BTreeNode[2 * t];
            this.n        = 0;
        }
    }

    // -------------------------------------------------------------------------
    // Fields
    // -------------------------------------------------------------------------

    private BTreeNode root;
    private final int t; // minimum degree

    // -------------------------------------------------------------------------
    // Constructor
    // -------------------------------------------------------------------------

    /**
     * Creates an empty B-Tree with minimum degree {@code t}.
     *
     * @param t minimum degree (t >= 2); a common choice is t = 3 (order 5)
     */
    public BTree(int t) {
        if (t < 2) throw new IllegalArgumentException("Minimum degree must be >= 2");
        this.t = t;
        root = new BTreeNode(t, true);
    }

    // -------------------------------------------------------------------------
    // Search
    // -------------------------------------------------------------------------

    /**
     * Returns {@code true} if {@code key} is present in the B-Tree.
     *
     * <p>Time: O(t * log_t(n)) | Space: O(log_t(n)) recursive stack.
     *
     * @param key the key to find
     * @return {@code true} if found
     */
    public boolean search(int key) {
        return searchRec(root, key);
    }

    private boolean searchRec(BTreeNode node, int key) {
        int i = 0;
        while (i < node.n && key > node.keys[i]) i++;
        if (i < node.n && key == node.keys[i]) return true;
        if (node.leaf) return false;
        return searchRec(node.children[i], key);
    }

    // -------------------------------------------------------------------------
    // Insert
    // -------------------------------------------------------------------------

    /**
     * Inserts {@code key} into the B-Tree.  Duplicate keys are ignored.
     *
     * <p>Uses a single top-down pass (pre-emptive splits), so at most one root
     * split can occur per insertion.
     *
     * <p>Time: O(t * log_t(n)) | Space: O(log_t(n)).
     *
     * @param key the key to insert
     */
    public void insert(int key) {
        if (search(key)) return; // duplicate

        BTreeNode r = root;
        if (r.n == 2 * t - 1) {
            // Root is full – split it
            BTreeNode s = new BTreeNode(t, false);
            s.children[0] = r;
            root = s;
            splitChild(s, 0, r);
            insertNonFull(s, key);
        } else {
            insertNonFull(r, key);
        }
    }

    /**
     * Inserts {@code key} into a non-full node {@code node}.
     */
    private void insertNonFull(BTreeNode node, int key) {
        int i = node.n - 1;

        if (node.leaf) {
            // Shift keys right to make room
            while (i >= 0 && key < node.keys[i]) {
                node.keys[i + 1] = node.keys[i];
                i--;
            }
            node.keys[i + 1] = key;
            node.n++;
        } else {
            // Find child to descend into
            while (i >= 0 && key < node.keys[i]) i--;
            i++;
            if (node.children[i].n == 2 * t - 1) {
                splitChild(node, i, node.children[i]);
                if (key > node.keys[i]) i++;
            }
            insertNonFull(node.children[i], key);
        }
    }

    // -------------------------------------------------------------------------
    // splitChild
    // -------------------------------------------------------------------------

    /**
     * Splits the {@code i}-th child of {@code parent} (which must be full).
     *
     * <p>The median key of the full child is promoted to {@code parent}, and the
     * right half of the child becomes a new sibling to its right.
     *
     * <p>Time: O(t) | Space: O(t).
     *
     * @param parent the parent node (must not be full)
     * @param i      index of the child to split
     * @param child  the full child node
     */
    public void splitChild(BTreeNode parent, int i, BTreeNode child) {
        BTreeNode newNode = new BTreeNode(t, child.leaf);
        newNode.n = t - 1;

        // Copy right half of child's keys to newNode
        for (int j = 0; j < t - 1; j++) {
            newNode.keys[j] = child.keys[j + t];
        }
        // Copy right half of child's children (if not a leaf)
        if (!child.leaf) {
            for (int j = 0; j < t; j++) {
                newNode.children[j] = child.children[j + t];
            }
        }
        child.n = t - 1;

        // Shift parent's children right to insert newNode
        for (int j = parent.n; j >= i + 1; j--) {
            parent.children[j + 1] = parent.children[j];
        }
        parent.children[i + 1] = newNode;

        // Shift parent's keys right to insert median
        for (int j = parent.n - 1; j >= i; j--) {
            parent.keys[j + 1] = parent.keys[j];
        }
        parent.keys[i] = child.keys[t - 1];
        parent.n++;
    }

    // -------------------------------------------------------------------------
    // Delete
    // -------------------------------------------------------------------------

    /**
     * Deletes {@code key} from the B-Tree.  Handles all cases:
     * <ol>
     *   <li>Key is in a leaf node – remove directly.</li>
     *   <li>Key is in an internal node:<br>
     *       2a. left child has &ge;t keys – replace with predecessor.<br>
     *       2b. right child has &ge;t keys – replace with successor.<br>
     *       2c. both children have exactly t-1 keys – merge, then delete.</li>
     *   <li>Key is not in the current node – ensure child has &ge;t keys before descending
     *       (rotate from sibling or merge).</li>
     * </ol>
     *
     * <p>Time: O(t * log_t(n)) | Space: O(log_t(n)).
     *
     * @param key the key to delete
     */
    public void delete(int key) {
        if (!search(key)) return;
        deleteRec(root, key);
        // If root has 0 keys, its first child becomes the new root
        if (root.n == 0 && !root.leaf) {
            root = root.children[0];
        }
    }

    private void deleteRec(BTreeNode node, int key) {
        int i = findKeyIndex(node, key);

        if (i < node.n && node.keys[i] == key) {
            // Key found in this node
            if (node.leaf) {
                // Case 1: leaf – remove directly
                removeFromLeaf(node, i);
            } else {
                // Case 2: internal node
                if (node.children[i].n >= t) {
                    // 2a: predecessor
                    int pred = getPredecessor(node, i);
                    node.keys[i] = pred;
                    deleteRec(node.children[i], pred);
                } else if (node.children[i + 1].n >= t) {
                    // 2b: successor
                    int succ = getSuccessor(node, i);
                    node.keys[i] = succ;
                    deleteRec(node.children[i + 1], succ);
                } else {
                    // 2c: merge children[i] and children[i+1]
                    merge(node, i);
                    deleteRec(node.children[i], key);
                }
            }
        } else {
            // Key not in this node – descend
            if (node.leaf) return; // key not in tree

            boolean isLastChild = (i == node.n);
            // Ensure the child we're about to descend into has >= t keys
            if (node.children[i].n < t) {
                fill(node, i);
            }
            // After fill, merging might have shifted index
            if (isLastChild && i > node.n) {
                deleteRec(node.children[i - 1], key);
            } else {
                deleteRec(node.children[i], key);
            }
        }
    }

    /** Index of the first key >= key in node. */
    private int findKeyIndex(BTreeNode node, int key) {
        int i = 0;
        while (i < node.n && node.keys[i] < key) i++;
        return i;
    }

    private void removeFromLeaf(BTreeNode node, int i) {
        for (int j = i + 1; j < node.n; j++) node.keys[j - 1] = node.keys[j];
        node.n--;
    }

    private int getPredecessor(BTreeNode node, int i) {
        BTreeNode cur = node.children[i];
        while (!cur.leaf) cur = cur.children[cur.n];
        return cur.keys[cur.n - 1];
    }

    private int getSuccessor(BTreeNode node, int i) {
        BTreeNode cur = node.children[i + 1];
        while (!cur.leaf) cur = cur.children[0];
        return cur.keys[0];
    }

    /**
     * Merges child {@code i} and child {@code i+1} of {@code node},
     * pulling down node.keys[i] as the median.
     */
    public void merge(BTreeNode node, int i) {
        BTreeNode left  = node.children[i];
        BTreeNode right = node.children[i + 1];

        // Pull median key down into left
        left.keys[t - 1] = node.keys[i];

        // Copy right's keys into left
        for (int j = 0; j < right.n; j++) left.keys[j + t] = right.keys[j];
        // Copy right's children into left
        if (!left.leaf) {
            for (int j = 0; j <= right.n; j++) left.children[j + t] = right.children[j];
        }
        left.n = 2 * t - 1;

        // Remove median key and right child from parent
        for (int j = i + 1; j < node.n; j++) node.keys[j - 1] = node.keys[j];
        for (int j = i + 2; j <= node.n; j++) node.children[j - 1] = node.children[j];
        node.n--;
    }

    /** Ensures node.children[i] has at least t keys by borrowing or merging. */
    private void fill(BTreeNode node, int i) {
        if (i > 0 && node.children[i - 1].n >= t) {
            borrowFromPrev(node, i);
        } else if (i < node.n && node.children[i + 1].n >= t) {
            borrowFromNext(node, i);
        } else {
            if (i < node.n) merge(node, i);
            else           merge(node, i - 1);
        }
    }

    private void borrowFromPrev(BTreeNode node, int i) {
        BTreeNode child  = node.children[i];
        BTreeNode sibling = node.children[i - 1];

        // Shift child's keys right
        for (int j = child.n - 1; j >= 0; j--) child.keys[j + 1] = child.keys[j];
        if (!child.leaf) {
            for (int j = child.n; j >= 0; j--) child.children[j + 1] = child.children[j];
        }
        child.keys[0] = node.keys[i - 1];
        if (!child.leaf) child.children[0] = sibling.children[sibling.n];
        node.keys[i - 1] = sibling.keys[sibling.n - 1];
        child.n++;
        sibling.n--;
    }

    private void borrowFromNext(BTreeNode node, int i) {
        BTreeNode child   = node.children[i];
        BTreeNode sibling = node.children[i + 1];

        child.keys[child.n] = node.keys[i];
        if (!child.leaf) child.children[child.n + 1] = sibling.children[0];
        node.keys[i] = sibling.keys[0];

        for (int j = 1; j < sibling.n; j++) sibling.keys[j - 1] = sibling.keys[j];
        if (!sibling.leaf) {
            for (int j = 1; j <= sibling.n; j++) sibling.children[j - 1] = sibling.children[j];
        }
        child.n++;
        sibling.n--;
    }

    // -------------------------------------------------------------------------
    // toString – level-by-level
    // -------------------------------------------------------------------------

    /**
     * Returns a level-by-level string representation of the B-Tree.
     *
     * <p>Time: O(n) | Space: O(n).
     *
     * @return multi-line tree string
     */
    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append("B-Tree (t=").append(t).append("):\n");
        printLevel(sb, root, 0);
        return sb.toString();
    }

    private void printLevel(StringBuilder sb, BTreeNode node, int level) {
        if (node == null) return;
        sb.append("  ".repeat(level));
        sb.append("[");
        for (int i = 0; i < node.n; i++) {
            sb.append(node.keys[i]);
            if (i < node.n - 1) sb.append("|");
        }
        sb.append("]").append(node.leaf ? " (leaf)" : "").append("\n");
        if (!node.leaf) {
            for (int i = 0; i <= node.n; i++) {
                printLevel(sb, node.children[i], level + 1);
            }
        }
    }

    // -------------------------------------------------------------------------
    // Main – demo
    // -------------------------------------------------------------------------

    public static void main(String[] args) {
        System.out.println("=== B-Tree Demo (t=3, max 5 keys/node) ===\n");

        BTree bt = new BTree(3);

        // Insert
        int[] keys = {10, 20, 5, 6, 12, 30, 7, 17, 3, 1, 22, 25, 28, 15, 18};
        System.out.println("Inserting: ");
        for (int k : keys) {
            bt.insert(k);
            System.out.print(k + " ");
        }
        System.out.println("\n");
        System.out.println(bt);

        // Search
        System.out.println("search(6)  : " + bt.search(6));
        System.out.println("search(99) : " + bt.search(99));

        // Delete – leaf case
        System.out.println("\nDelete 6 (leaf):");
        bt.delete(6);
        System.out.println(bt);

        // Delete – internal node case
        System.out.println("Delete 12 (internal):");
        bt.delete(12);
        System.out.println(bt);

        // Delete – key requiring merge
        System.out.println("Delete 20 (may trigger merge):");
        bt.delete(20);
        System.out.println(bt);

        // Delete all remaining
        System.out.println("Deleting remaining keys one by one...");
        for (int k : keys) {
            bt.delete(k);
        }
        System.out.println("After deleting all: search(10) = " + bt.search(10));
        System.out.println(bt);
    }
}
