package advanced;

import java.util.ArrayList;
import java.util.LinkedList;
import java.util.List;
import java.util.Queue;

/**
 * Generic Binary Search Tree (BST).
 *
 * <p>Invariant: For every node N, all keys in the left subtree are less than N.key,
 * and all keys in the right subtree are greater than N.key.
 *
 * <p>Time complexities (average / worst):
 * <ul>
 *   <li>insert   – O(log n) / O(n)</li>
 *   <li>delete   – O(log n) / O(n)</li>
 *   <li>search   – O(log n) / O(n)</li>
 *   <li>findMin  – O(log n) / O(n)</li>
 *   <li>findMax  – O(log n) / O(n)</li>
 *   <li>height   – O(n)</li>
 *   <li>traversals – O(n)</li>
 * </ul>
 *
 * <p>Space complexity: O(n) for the tree; O(h) auxiliary for recursive calls where h = height.
 *
 * @param <T> a {@link Comparable} key type
 */
public class BST<T extends Comparable<T>> {

    // -------------------------------------------------------------------------
    // Inner Node class
    // -------------------------------------------------------------------------

    /**
     * A single node in the BST.
     *
     * @param <T> key type
     */
    private static class Node<T> {
        T key;
        Node<T> left, right;

        Node(T key) {
            this.key = key;
        }
    }

    // -------------------------------------------------------------------------
    // Fields
    // -------------------------------------------------------------------------

    private Node<T> root;
    private int size;

    // -------------------------------------------------------------------------
    // Insert
    // -------------------------------------------------------------------------

    /**
     * Inserts {@code key} into the BST. Duplicate keys are ignored.
     *
     * <p>Time: O(log n) average, O(n) worst | Space: O(h) recursive stack.
     *
     * @param key the key to insert
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public void insert(T key) {
        root = insertRec(root, key);
    }

    private Node<T> insertRec(Node<T> node, T key) {
        if (node == null) {
            size++;
            return new Node<>(key);
        }
        int cmp = key.compareTo(node.key);
        if (cmp < 0) node.left = insertRec(node.left, key);
        else if (cmp > 0) node.right = insertRec(node.right, key);
        // cmp == 0: duplicate – ignore
        return node;
    }

    // -------------------------------------------------------------------------
    // Delete (3 cases)
    // -------------------------------------------------------------------------

    /**
     * Deletes {@code key} from the BST.
     *
     * <p>Three cases handled:
     * <ol>
     *   <li>Node has no children – simply remove it.</li>
     *   <li>Node has one child – replace the node with its child.</li>
     *   <li>Node has two children – replace key with in-order successor (findMin of
     *       right subtree), then delete the successor.</li>
     * </ol>
     *
     * <p>Time: O(log n) average, O(n) worst | Space: O(h).
     *
     * @param key the key to delete
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public void delete(T key) {
        root = deleteRec(root, key);
    }

    private Node<T> deleteRec(Node<T> node, T key) {
        if (node == null) return null; // key not found
        int cmp = key.compareTo(node.key);
        if (cmp < 0) {
            node.left = deleteRec(node.left, key);
        } else if (cmp > 0) {
            node.right = deleteRec(node.right, key);
        } else {
            // Found the node to delete
            size--;
            // Case 1 & 2: zero or one child
            if (node.left == null) return node.right;
            if (node.right == null) return node.left;
            // Case 3: two children – find in-order successor
            Node<T> successor = findMinNode(node.right);
            node.key = successor.key;
            // Delete the successor from the right subtree
            // (we already decremented size above, so re-increment to avoid double-decrement)
            size++;
            node.right = deleteRec(node.right, successor.key);
        }
        return node;
    }

    // -------------------------------------------------------------------------
    // Search
    // -------------------------------------------------------------------------

    /**
     * Returns {@code true} if {@code key} exists in the BST.
     *
     * <p>Time: O(log n) average, O(n) worst | Space: O(h).
     *
     * @param key the key to search for
     * @return {@code true} if found
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public boolean search(T key) {
        return searchRec(root, key);
    }

    private boolean searchRec(Node<T> node, T key) {
        if (node == null) return false;
        int cmp = key.compareTo(node.key);
        if (cmp < 0) return searchRec(node.left, key);
        if (cmp > 0) return searchRec(node.right, key);
        return true;
    }

    // -------------------------------------------------------------------------
    // Traversals
    // -------------------------------------------------------------------------

    /**
     * Returns the in-order traversal (sorted order) as a list.
     *
     * <p>Time: O(n) | Space: O(n).
     *
     * @return sorted list of keys
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public List<T> inorder() {
        List<T> result = new ArrayList<>();
        inorderRec(root, result);
        return result;
    }

    private void inorderRec(Node<T> node, List<T> result) {
        if (node == null) return;
        inorderRec(node.left, result);
        result.add(node.key);
        inorderRec(node.right, result);
    }

    /**
     * Returns the pre-order traversal as a list.
     *
     * <p>Time: O(n) | Space: O(n).
     *
     * @return pre-order list of keys
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public List<T> preorder() {
        List<T> result = new ArrayList<>();
        preorderRec(root, result);
        return result;
    }

    private void preorderRec(Node<T> node, List<T> result) {
        if (node == null) return;
        result.add(node.key);
        preorderRec(node.left, result);
        preorderRec(node.right, result);
    }

    /**
     * Returns the post-order traversal as a list.
     *
     * <p>Time: O(n) | Space: O(n).
     *
     * @return post-order list of keys
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public List<T> postorder() {
        List<T> result = new ArrayList<>();
        postorderRec(root, result);
        return result;
    }

    private void postorderRec(Node<T> node, List<T> result) {
        if (node == null) return;
        postorderRec(node.left, result);
        postorderRec(node.right, result);
        result.add(node.key);
    }

    // -------------------------------------------------------------------------
    // findMin / findMax
    // -------------------------------------------------------------------------

    /**
     * Returns the minimum key in the BST.
     *
     * <p>Time: O(log n) average, O(n) worst | Space: O(1).
     *
     * @return minimum key
     * @throws IllegalStateException if the tree is empty
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public T findMin() {
        if (root == null) throw new IllegalStateException("Tree is empty");
        return findMinNode(root).key;
    }

    private Node<T> findMinNode(Node<T> node) {
        while (node.left != null) node = node.left;
        return node;
    }

    /**
     * Returns the maximum key in the BST.
     *
     * <p>Time: O(log n) average, O(n) worst | Space: O(1).
     *
     * @return maximum key
     * @throws IllegalStateException if the tree is empty
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public T findMax() {
        if (root == null) throw new IllegalStateException("Tree is empty");
        Node<T> node = root;
        while (node.right != null) node = node.right;
        return node.key;
    }

    // -------------------------------------------------------------------------
    // Height
    // -------------------------------------------------------------------------

    /**
     * Returns the height of the BST (number of edges on the longest root-to-leaf path).
     * An empty tree has height -1; a single-node tree has height 0.
     *
     * <p>Time: O(n) | Space: O(h).
     *
     * @return height of the tree
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public int height() {
        return heightRec(root);
    }

    private int heightRec(Node<T> node) {
        if (node == null) return -1;
        return 1 + Math.max(heightRec(node.left), heightRec(node.right));
    }

    // -------------------------------------------------------------------------
    // Size
    // -------------------------------------------------------------------------

    /**
     * Returns the number of keys stored in the BST.
     *
     * <p>Time: O(1) | Space: O(1).
     *
     * @return number of nodes
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public int size() {
        return size;
    }

    // -------------------------------------------------------------------------
    // ASCII tree print (toString)
    // -------------------------------------------------------------------------

    /**
     * Returns a multi-line ASCII representation of the BST.
     * The tree is printed level-by-level with visual connectors.
     *
     * <p>Time: O(n) | Space: O(n).
     *
     * @return ASCII tree string
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
        if (root == null) return "(empty tree)";
        StringBuilder sb = new StringBuilder();
        buildAscii(sb, root, "", "");
        return sb.toString();
    }

    /**
     * Recursive helper that builds an ASCII sideways tree (right subtree on top).
     */
    private void buildAscii(StringBuilder sb, Node<T> node, String prefix, String childPrefix) {
        if (node == null) return;
        sb.append(prefix).append(node.key).append("\n");
        if (node.left != null || node.right != null) {
            buildAscii(sb, node.right,
                    childPrefix + "├── R: ",
                    childPrefix + "│   ");
            buildAscii(sb, node.left,
                    childPrefix + "└── L: ",
                    childPrefix + "    ");
        }
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
        BST<Integer> bst = new BST<>();

        System.out.println("=== BST Demo ===\n");

        // Insert
        int[] keys = {50, 30, 70, 20, 40, 60, 80, 10, 25, 35, 45};
        for (int k : keys) bst.insert(k);

        System.out.println("Tree after insertions:");
        System.out.println(bst);

        System.out.println("Size   : " + bst.size());
        System.out.println("Height : " + bst.height());
        System.out.println("Min    : " + bst.findMin());
        System.out.println("Max    : " + bst.findMax());

        System.out.println("\nIn-order  : " + bst.inorder());
        System.out.println("Pre-order : " + bst.preorder());
        System.out.println("Post-order: " + bst.postorder());

        // Search
        System.out.println("\nSearch 40 : " + bst.search(40));
        System.out.println("Search 99 : " + bst.search(99));

        // Delete case 1 – leaf
        System.out.println("\nDelete 10 (leaf):");
        bst.delete(10);
        System.out.println(bst);

        // Delete case 2 – one child
        System.out.println("Delete 25 (one child):");
        bst.delete(25);
        System.out.println(bst);

        // Delete case 3 – two children
        System.out.println("Delete 30 (two children):");
        bst.delete(30);
        System.out.println(bst);

        System.out.println("In-order after deletions: " + bst.inorder());

        // Generic String BST
        BST<String> strBst = new BST<>();
        for (String s : new String[]{"mango", "apple", "orange", "banana", "kiwi"}) {
            strBst.insert(s);
        }
        System.out.println("\nString BST in-order: " + strBst.inorder());
        System.out.println(strBst);
    }
}
