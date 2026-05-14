package advanced_ds;

import java.util.*;

/**
 * Cartesian Tree (Min/Max + RMQ)
 *
 * Time Complexity:
 * - Construction: O(n) using stack-based algorithm
 * - RMQ Query: O(log n) or O(1) with preprocessing (LCA)
 * - Space Complexity: O(n)
 *
 * Use Cases:
 * - Range Minimum Query (RMQ)
 * - Range Maximum Query
 * - Finding nearest smaller/larger element
 * - Lowest Common Ancestor queries
 * - Split representation for persistent structures
 *
 * Key Insight:
 * - BST on values with heap property on array indices
 * - Subtree root is minimum element in range
 * - Linear construction with stack
 * - Can be converted to RMQ via LCA reduction
 * - Each element has unique position: left subtree = elements to left, smaller than root
 */
public class CartesianTree {

    static class Node {
        int val, idx;
        Node left, right, parent;

        Node(int val, int idx) {
            this.val = val;
            this.idx = idx;
        }
    }

    private int[] arr;
    private int n;
    private Node root;

    /**
     * Build Cartesian tree from array.
     *
     * @param arr Input array
     */
    public CartesianTree(int[] arr) {
        this.arr = arr;
        this.n = arr.length;
        this.root = buildTree(arr);
    }

    /**
     * Build tree using stack in O(n) time.
     */
    private Node buildTree(int[] arr) {
        if (arr.length == 0) {
            return null;
        }

        Stack<Node> stack = new Stack<>();
        Node root = null;

        for (int i = 0; i < arr.length; i++) {
            Node node = new Node(arr[i], i);
            Node lastPopped = null;

            // Pop elements greater than current
            while (!stack.isEmpty() && stack.peek().val > arr[i]) {
                lastPopped = stack.pop();
            }

            // If we popped something, it becomes left child
            if (lastPopped != null) {
                node.left = lastPopped;
                lastPopped.parent = node;
            }

            // Current node becomes right child of stack top
            if (!stack.isEmpty()) {
                stack.peek().right = node;
                node.parent = stack.peek();
            } else {
                root = node;
            }

            stack.push(node);
        }

        return root;
    }

    /**
     * Find minimum value in range [l, r].
     *
     * @param l Left index (inclusive)
     * @param r Right index (inclusive)
     * @return Minimum value
     */
    public int queryMin(int l, int r) {
        if (l > r || l < 0 || r >= n) {
            return Integer.MAX_VALUE;
        }

        return queryMin(root, l, r);
    }

    private int queryMin(Node node, int l, int r) {
        if (node == null) {
            return Integer.MAX_VALUE;
        }

        if (node.idx < l || node.idx > r) {
            if (node.idx < l) {
                return queryMin(node.right, l, r);
            } else {
                return queryMin(node.left, l, r);
            }
        }

        int leftMin = queryMin(node.left, l, r);
        int rightMin = queryMin(node.right, l, r);

        return Math.min(node.val, Math.min(leftMin, rightMin));
    }

    /**
     * Find maximum value in range [l, r].
     *
     * @param l Left index (inclusive)
     * @param r Right index (inclusive)
     * @return Maximum value
     */
    public int queryMax(int l, int r) {
        if (l > r || l < 0 || r >= n) {
            return Integer.MIN_VALUE;
        }

        return queryMax(root, l, r);
    }

    private int queryMax(Node node, int l, int r) {
        if (node == null) {
            return Integer.MIN_VALUE;
        }

        if (node.idx < l || node.idx > r) {
            if (node.idx < l) {
                return queryMax(node.right, l, r);
            } else {
                return queryMax(node.left, l, r);
            }
        }

        int leftMax = queryMax(node.left, l, r);
        int rightMax = queryMax(node.right, l, r);

        return Math.max(node.val, Math.max(leftMax, rightMax));
    }

    /**
     * Get preorder traversal (value, index).
     *
     * @return List of (value, index) pairs
     */
    public List<String> preorder() {
        List<String> result = new ArrayList<>();
        preorder(root, result);
        return result;
    }

    private void preorder(Node node, List<String> result) {
        if (node != null) {
            result.add("(" + node.val + "," + node.idx + ")");
            preorder(node.left, result);
            preorder(node.right, result);
        }
    }

    /**
     * Get inorder traversal.
     *
     * @return Values in inorder
     */
    public List<Integer> inorder() {
        List<Integer> result = new ArrayList<>();
        inorder(root, result);
        return result;
    }

    private void inorder(Node node, List<Integer> result) {
        if (node != null) {
            inorder(node.left, result);
            result.add(node.val);
            inorder(node.right, result);
        }
    }

    public static void main(String[] args) {
        // Example 1: RMQ on simple array
        System.out.println("=== Example 1: Range Minimum Query ===");
        int[] arr = {7, 3, 9, 2, 5, 1, 8};
        CartesianTree tree = new CartesianTree(arr);

        System.out.println("Array: " + Arrays.toString(arr));
        System.out.println("Preorder (structure): " + tree.preorder());

        int[][] queries = {{0, 4}, {1, 5}, {2, 6}, {0, 6}};
        for (int[] q : queries) {
            int minVal = tree.queryMin(q[0], q[1]);
            System.out.println("Min in [" + q[0] + ", " + q[1] + "]: " + minVal);
        }

        // Example 2: Range maximum query
        System.out.println("\n=== Example 2: Range Maximum Query ===");
        for (int[] q : queries) {
            int maxVal = tree.queryMax(q[0], q[1]);
            System.out.println("Max in [" + q[0] + ", " + q[1] + "]: " + maxVal);
        }

        // Example 3: Larger array
        System.out.println("\n=== Example 3: Larger Array ===");
        int[] arr2 = {3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5};
        CartesianTree tree2 = new CartesianTree(arr2);

        System.out.println("Array: " + Arrays.toString(arr2));
        System.out.println("Min in [2, 8]: " + tree2.queryMin(2, 8));
        System.out.println("Max in [2, 8]: " + tree2.queryMax(2, 8));
        System.out.println("Min in [0, 4]: " + tree2.queryMin(0, 4));
    }
}
