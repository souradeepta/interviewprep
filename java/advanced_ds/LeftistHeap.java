package advanced_ds;

import java.util.*;

/**
 * Leftist Heap (Leftist Tree)
 *
 * Time Complexity:
 * - Insert: O(log n)
 * - Delete Min: O(log n)
 * - Merge: O(log n) amortized
 * - Find Min: O(1)
 *
 * Space Complexity: O(n)
 *
 * Use Cases:
 * - Mergeable priority queue
 * - Heap merge operations
 * - Dijkstra's algorithm with merge operation
 * - Scheduling problems
 *
 * Key Insight:
 * - Merge-based heap (vs. array-based binary heap)
 * - Left path always >= right path (guarantees log n height)
 * - Efficiently merge two heaps
 * - Can implement in-place without array reallocation
 * - Null path length: min dist from node to None node in right-heavy subtree
 */
public class LeftistHeap {

    static class Node {
        int key;
        Node left, right;
        int npl;  // Null path length

        Node(int key) {
            this.key = key;
            this.npl = 0;
        }

        void updateNPL() {
            int rightNPL = right != null ? right.npl : -1;
            this.npl = rightNPL + 1;
        }
    }

    private Node root;

    /**
     * Initialize empty leftist heap.
     */
    public LeftistHeap() {
        this.root = null;
    }

    /**
     * Insert key into heap.
     *
     * @param key Key to insert
     */
    public void insert(int key) {
        Node newNode = new Node(key);
        root = merge(root, newNode);
    }

    /**
     * Merge with another leftist heap.
     *
     * @param other Other heap to merge
     */
    public void merge(LeftistHeap other) {
        root = merge(root, other.root);
    }

    /**
     * Merge two heaps.
     */
    private Node merge(Node h1, Node h2) {
        if (h1 == null) return h2;
        if (h2 == null) return h1;

        // Ensure h1.key <= h2.key
        if (h1.key > h2.key) {
            Node temp = h1;
            h1 = h2;
            h2 = temp;
        }

        // Recursively merge h2 with h1's right subtree
        h1.right = merge(h1.right, h2);

        // Swap left and right to maintain leftist property
        if (h1.left == null) {
            h1.left = h1.right;
            h1.right = null;
        } else if (h1.right != null && h1.left.npl < h1.right.npl) {
            Node temp = h1.left;
            h1.left = h1.right;
            h1.right = temp;
        }

        // Update null path length
        h1.updateNPL();

        return h1;
    }

    /**
     * Delete and return minimum element.
     *
     * @return Minimum element, or null if heap is empty
     */
    public Integer deleteMin() {
        if (root == null) {
            return null;
        }

        int minVal = root.key;
        root = merge(root.left, root.right);
        return minVal;
    }

    /**
     * Find minimum element without deleting.
     *
     * @return Minimum element, or null if heap is empty
     */
    public Integer findMin() {
        return root != null ? root.key : null;
    }

    /**
     * Check if heap is empty.
     *
     * @return true if empty
     */
    public boolean isEmpty() {
        return root == null;
    }

    /**
     * Get size of heap.
     *
     * @return Number of elements
     */
    public int size() {
        return size(root);
    }

    private int size(Node node) {
        if (node == null) return 0;
        return 1 + size(node.left) + size(node.right);
    }

    /**
     * Get elements in inorder (not sorted).
     *
     * @return List of elements
     */
    public List<Integer> inorder() {
        List<Integer> result = new ArrayList<>();
        inorder(root, result);
        return result;
    }

    private void inorder(Node node, List<Integer> result) {
        if (node != null) {
            inorder(node.left, result);
            result.add(node.key);
            inorder(node.right, result);
        }
    }

    public static void main(String[] args) {
        // Example 1: Basic operations
        System.out.println("=== Example 1: Basic Operations ===");
        LeftistHeap heap = new LeftistHeap();

        int[] elements = {7, 3, 9, 1, 5, 11, 2};
        System.out.print("Inserting: [");
        for (int i = 0; i < elements.length; i++) {
            if (i > 0) System.out.print(", ");
            System.out.print(elements[i]);
            heap.insert(elements[i]);
        }
        System.out.println("]");

        System.out.println("Min: " + heap.findMin());
        System.out.println("Size: " + heap.size());

        System.out.println("\nExtract min in order:");
        while (!heap.isEmpty()) {
            System.out.println("  " + heap.deleteMin());
        }

        // Example 2: Heap merge
        System.out.println("\n=== Example 2: Heap Merge ===");
        LeftistHeap heap1 = new LeftistHeap();
        LeftistHeap heap2 = new LeftistHeap();

        for (int x : new int[]{1, 5, 9}) {
            heap1.insert(x);
        }

        for (int x : new int[]{2, 3, 7}) {
            heap2.insert(x);
        }

        List<Integer> h1 = new ArrayList<>(heap1.inorder());
        Collections.sort(h1);
        List<Integer> h2 = new ArrayList<>(heap2.inorder());
        Collections.sort(h2);

        System.out.println("Heap 1: " + h1);
        System.out.println("Heap 2: " + h2);

        heap1.merge(heap2);
        List<Integer> merged = new ArrayList<>(heap1.inorder());
        Collections.sort(merged);
        System.out.println("After merge: " + merged);
        System.out.println("Min: " + heap1.findMin());

        // Example 3: Large scale operations
        System.out.println("\n=== Example 3: Delete Min Operations ===");
        LeftistHeap heap3 = new LeftistHeap();
        int[] elements3 = {15, 10, 20, 8, 2, 16};
        for (int elem : elements3) {
            heap3.insert(elem);
        }

        System.out.println("Initial size: " + heap3.size());
        while (!heap3.isEmpty()) {
            System.out.println("Delete min: " + heap3.deleteMin() + ", Size: " + heap3.size());
        }
    }
}
