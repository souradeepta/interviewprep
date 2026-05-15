package advanced_ds;

import java.util.*;

/**
 * B+ Tree (Database Index Structure)
 *
 * Time Complexity:
 * - Search: O(log n)
 * - Insert: O(log n)
 * - Delete: O(log n)
 * - Range scan: O(log n + k) where k = results
 *
 * Space Complexity: O(n)
 *
 * Use Cases:
 * - Database indexing (primary index)
 * - File system indexing
 * - Multi-level sorted data structure
 * - Disk-based searching (minimizes I/O)
 * - Range queries over large datasets
 *
 * Key Insight:
 * - All keys in leaves, internal nodes just guide search
 * - All leaves at same depth (balanced)
 * - Each node contains 60% to 100% of max capacity (t-1 to 2t-1 keys)
 * - Facilitates efficient range scans
 * - Leaf nodes can be linked for sequential access
 */
public class BPlusTree {

    static class Node {
        boolean isLeaf;
        List<Integer> keys;
        List<Node> children;
        Node next;  // For leaf nodes
        int t;      // Minimum degree

        Node(boolean isLeaf, int t) {
            this.isLeaf = isLeaf;
            this.t = t;
            this.keys = new ArrayList<>();
            this.children = new ArrayList<>();
        }

        boolean isFull() {
            return keys.size() == 2 * t - 1;
        }

        boolean hasMinKeys() {
            return keys.size() >= t - 1;
        }
    }

    private Node root;
    private int t;

    /**
     * Initialize B+ tree.
     *
     * @param t Minimum degree
     */
    public BPlusTree(int t) {
        this.root = new Node(true, t);
        this.t = t;
    }

    /**
     * Search for key in tree.
     *
     * @param key Key to search
     * @return true if key exists
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public boolean search(int key) {
        return search(root, key) != null;
    }

    /**
     * Search and return leaf node containing key.
     */
    private Node search(Node node, int key) {
        int i = 0;
        while (i < node.keys.size() && key > node.keys.get(i)) {
            i++;
        }

        if (node.isLeaf) {
            return (i < node.keys.size() && node.keys.get(i) == key) ? node : null;
        }

        if (i < node.keys.size() && key == node.keys.get(i)) {
            return search(node.children.get(i + 1), key);
        }

        return search(node.children.get(i), key);
    }

    /**
     * Insert key into tree.
     *
     * @param key Key to insert
     */
    public void insert(int key) {
        if (root.isFull()) {
            Node newRoot = new Node(false, t);
            newRoot.children.add(root);
            splitChild(newRoot, 0);
            root = newRoot;
        }

        insertNonFull(root, key);
    }

    private void insertNonFull(Node node, int key) {
        int i = node.keys.size() - 1;

        if (node.isLeaf) {
            node.keys.add(null);
            while (i >= 0 && key < node.keys.get(i)) {
                node.keys.set(i + 1, node.keys.get(i));
                i--;
            }
            node.keys.set(i + 1, key);
        } else {
            while (i >= 0 && key < node.keys.get(i)) {
                i--;
            }
            i++;

            if (node.children.get(i).isFull()) {
                splitChild(node, i);
                if (key > node.keys.get(i)) {
                    i++;
                }
            }

            insertNonFull(node.children.get(i), key);
        }
    }

    private void splitChild(Node parent, int idx) {
        Node fullChild = parent.children.get(idx);
        Node newChild = new Node(fullChild.isLeaf, t);

        int mid = t - 1;

        // Copy keys
        for (int i = mid + 1; i < fullChild.keys.size(); i++) {
            newChild.keys.add(fullChild.keys.get(i));
        }
        fullChild.keys = new ArrayList<>(fullChild.keys.subList(0, mid));

        // Copy children if not leaf
        if (!fullChild.isLeaf) {
            for (int i = mid + 1; i < fullChild.children.size(); i++) {
                newChild.children.add(fullChild.children.get(i));
            }
            fullChild.children = new ArrayList<>(fullChild.children.subList(0, mid + 1));
        } else {
            // Link leaf nodes
            newChild.next = fullChild.next;
            fullChild.next = newChild;
        }

        // Move median to parent
        int medianKey = newChild.keys.isEmpty() ?
                (fullChild.keys.isEmpty() ? -1 : fullChild.keys.get(fullChild.keys.size() - 1)) :
                newChild.keys.get(0);

        parent.keys.add(idx, medianKey);
        parent.children.add(idx + 1, newChild);
    }

    /**
     * Find all keys in range [lower, upper].
     *
     * @param lower Lower bound
     * @param upper Upper bound
     * @return Keys in range
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public List<Integer> rangeSearch(int lower, int upper) {
        List<Integer> result = new ArrayList<>();
        Node leaf = findLeaf(root, lower);

        while (leaf != null) {
            for (int key : leaf.keys) {
                if (lower <= key && key <= upper) {
                    result.add(key);
                } else if (key > upper) {
                    return result;
                }
            }
            leaf = leaf.next;
        }

        return result;
    }

    private Node findLeaf(Node node, int key) {
        int i = 0;
        while (i < node.keys.size() && key > node.keys.get(i)) {
            i++;
        }

        if (node.isLeaf) {
            return node;
        }

        return findLeaf(node.children.get(i), key);
    }

    /**
     * Get all keys in inorder.
     *
     * @return Sorted list of keys
     */
    public List<Integer> inorder() {
        List<Integer> result = new ArrayList<>();
        inorder(root, result);
        return result;
    }

    private void inorder(Node node, List<Integer> result) {
        if (node.isLeaf) {
            result.addAll(node.keys);
        } else {
            for (int i = 0; i < node.keys.size(); i++) {
                inorder(node.children.get(i), result);
                result.add(node.keys.get(i));
            }
            inorder(node.children.get(node.children.size() - 1), result);
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
        // Example 1: Basic operations
        System.out.println("=== Example 1: Basic B+ Tree Operations ===");
        BPlusTree tree = new BPlusTree(3);

        int[] keys = {10, 20, 5, 6, 12, 30, 7, 17};
        System.out.print("Inserting: [");
        for (int i = 0; i < keys.length; i++) {
            if (i > 0) System.out.print(", ");
            System.out.print(keys[i]);
            tree.insert(keys[i]);
        }
        System.out.println("]");

        System.out.println("Inorder: " + tree.inorder());

        for (int key : new int[]{5, 10, 12, 8, 100}) {
            System.out.println("Search " + key + ": " + tree.search(key));
        }

        // Example 2: Range search
        System.out.println("\n=== Example 2: Range Search ===");
        System.out.println("Range [5, 20]: " + tree.rangeSearch(5, 20));
        System.out.println("Range [7, 15]: " + tree.rangeSearch(7, 15));

        // Example 3: Larger tree
        System.out.println("\n=== Example 3: Larger Tree ===");
        BPlusTree tree2 = new BPlusTree(3);
        for (int i = 1; i <= 20; i++) {
            tree2.insert(i);
        }

        System.out.println("Inorder (1-20): " + tree2.inorder());
        System.out.println("Range [5, 15]: " + tree2.rangeSearch(5, 15));
    }
}
