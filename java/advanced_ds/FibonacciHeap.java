package advanced_ds;

import java.util.*;

/**
 * Fibonacci Heap
 *
 * Time Complexity (Amortized):
 * - Insert: O(1)
 * - Find Min: O(1)
 * - Delete Min: O(log n)
 * - Decrease Key: O(1)
 * - Delete: O(log n)
 * - Merge: O(1)
 *
 * Space Complexity: O(n)
 *
 * Use Cases:
 * - Dijkstra's algorithm (faster for sparse graphs)
 * - Prim's algorithm
 * - Dynamic connectivity
 * - Network algorithms with decrease-key
 *
 * Key Insight:
 * - Collection of min-heaps organized as forest of Fibonacci trees
 * - O(1) decrease-key via cascading cuts
 * - Lazy consolidation in delete-min
 * - Better amortized complexity than binary heaps for key operations
 * - Not practical for small inputs due to high constants
 */
public class FibonacciHeap {

    static class Node {
        int key;
        Node parent, child, left, right;
        int degree;
        boolean marked;

        Node(int key) {
            this.key = key;
            this.left = this;
            this.right = this;
            this.degree = 0;
            this.marked = false;
        }
    }

    private Node min;
    private int numNodes;

    /**
     * Initialize empty Fibonacci heap.
     */
    public FibonacciHeap() {
        this.min = null;
        this.numNodes = 0;
    }

    /**
     * Insert key and return node.
     *
     * @param key Key to insert
     * @return Node containing key
     */
    public Node insert(int key) {
        Node newNode = new Node(key);
        numNodes++;

        if (min == null) {
            min = newNode;
        } else {
            link(min, newNode);
            if (newNode.key < min.key) {
                min = newNode;
            }
        }

        return newNode;
    }

    /**
     * Find minimum element.
     *
     * @return Minimum key
     */
    public Integer findMin() {
        return min != null ? min.key : null;
    }

    /**
     * Merge with another Fibonacci heap.
     *
     * @param other Other heap to merge
     */
    public void merge(FibonacciHeap other) {
        if (other.min == null) {
            return;
        }

        if (min == null) {
            min = other.min;
            numNodes = other.numNodes;
        } else {
            link(min, other.min);
            if (other.min.key < min.key) {
                min = other.min;
            }
            numNodes += other.numNodes;
        }
    }

    /**
     * Delete and return minimum element.
     *
     * @return Minimum key
     */
    public Integer deleteMin() {
        if (min == null) {
            return null;
        }

        int minVal = min.key;

        if (min.right == min) {
            min = null;
        } else {
            removeFromList(min);
            min = min.right;
        }

        if (min != null) {
            Node child = min.child;
            if (child != null) {
                List<Node> children = new ArrayList<>();
                Node current = child;
                do {
                    children.add(current);
                    current = current.right;
                } while (current != child);

                for (Node c : children) {
                    c.parent = null;
                    link(min, c);
                }
            }

            consolidate();
        }

        numNodes--;
        return minVal;
    }

    /**
     * Decrease key of node.
     *
     * @param node Node to update
     * @param newKey New key (must be <= current)
     */
    public void decreaseKey(Node node, int newKey) {
        if (newKey > node.key) {
            throw new IllegalArgumentException("New key greater than current");
        }

        node.key = newKey;

        if (node.parent == null) {
            if (newKey < min.key) {
                min = node;
            }
        } else {
            if (node.key < node.parent.key) {
                cut(node, node.parent);
                cascadingCut(node.parent);
            }
        }
    }

    /**
     * Delete a node.
     *
     * @param node Node to delete
     */
    public void delete(Node node) {
        decreaseKey(node, Integer.MIN_VALUE);
        deleteMin();
    }

    private void link(Node a, Node b) {
        a.right.left = b;
        b.right = a.right;
        a.right = b;
        b.left = a;
    }

    private void removeFromList(Node node) {
        node.left.right = node.right;
        node.right.left = node.left;
    }

    private void consolidate() {
        int maxDegree = (int) (Math.log(numNodes) / Math.log(2)) + 1;
        Node[] degreeTable = new Node[maxDegree + 1];

        List<Node> rootList = new ArrayList<>();
        if (min != null) {
            Node current = min;
            do {
                rootList.add(current);
                current = current.right;
            } while (current != min);
        }

        for (Node root : rootList) {
            int degree = root.degree;
            while (degree < degreeTable.length && degreeTable[degree] != null) {
                Node other = degreeTable[degree];
                if (root.key > other.key) {
                    Node temp = root;
                    root = other;
                    other = temp;
                }

                heapifyLink(root, other);
                degreeTable[degree] = null;
                degree++;
            }

            if (degree < degreeTable.length) {
                degreeTable[degree] = root;
            }
        }

        min = null;
        for (Node node : degreeTable) {
            if (node != null) {
                if (min == null) {
                    min = node;
                    min.left = min;
                    min.right = min;
                } else {
                    link(min, node);
                    if (node.key < min.key) {
                        min = node;
                    }
                }
            }
        }
    }

    private void heapifyLink(Node parent, Node child) {
        removeFromList(child);

        if (parent.child == null) {
            parent.child = child;
            child.left = child;
            child.right = child;
        } else {
            link(parent.child, child);
        }

        child.parent = parent;
        parent.degree++;
        child.marked = false;
    }

    private void cut(Node node, Node parent) {
        if (parent.child == node) {
            if (node.right == node) {
                parent.child = null;
            } else {
                parent.child = node.right;
            }
        }

        removeFromList(node);
        link(min, node);
        node.parent = null;
        node.marked = false;
    }

    private void cascadingCut(Node node) {
        while (node.parent != null) {
            if (!node.marked) {
                node.marked = true;
                return;
            }
            Node parent = node.parent;
            cut(node, parent);
            node = parent;
        }
    }

    public static void main(String[] args) {
        // Example 1: Basic operations
        System.out.println("=== Example 1: Basic Operations ===");
        FibonacciHeap fib = new FibonacciHeap();

        int[] elements = {7, 3, 9, 1, 5, 11, 2};
        System.out.print("Inserting: [");
        Map<Integer, Node> nodes = new HashMap<>();
        for (int i = 0; i < elements.length; i++) {
            if (i > 0) System.out.print(", ");
            System.out.print(elements[i]);
            nodes.put(elements[i], fib.insert(elements[i]));
        }
        System.out.println("]");

        System.out.println("Min: " + fib.findMin());

        System.out.println("\nExtract min in order:");
        while (fib.min != null) {
            System.out.println("  " + fib.deleteMin());
        }

        // Example 2: Decrease key
        System.out.println("\n=== Example 2: Decrease Key ===");
        FibonacciHeap fib2 = new FibonacciHeap();
        Map<Integer, Node> nodes2 = new HashMap<>();
        for (int x : new int[]{10, 20, 30, 40, 50}) {
            nodes2.put(x, fib2.insert(x));
        }

        System.out.println("Initial min: " + fib2.findMin());

        System.out.println("Decrease 40 to 5");
        fib2.decreaseKey(nodes2.get(40), 5);
        System.out.println("New min: " + fib2.findMin());

        System.out.println("Decrease 50 to 3");
        fib2.decreaseKey(nodes2.get(50), 3);
        System.out.println("New min: " + fib2.findMin());

        // Example 3: Merge
        System.out.println("\n=== Example 3: Heap Merge ===");
        FibonacciHeap fib3a = new FibonacciHeap();
        FibonacciHeap fib3b = new FibonacciHeap();

        for (int x : new int[]{1, 5, 9}) {
            fib3a.insert(x);
        }
        for (int x : new int[]{2, 3, 7}) {
            fib3b.insert(x);
        }

        System.out.println("Heap A min: " + fib3a.findMin());
        System.out.println("Heap B min: " + fib3b.findMin());

        fib3a.merge(fib3b);
        System.out.println("After merge min: " + fib3a.findMin());
    }
}
