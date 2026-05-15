package advanced_ds;

import java.util.*;

/**
 * Splay Tree - Self-Adjusting Binary Search Tree
 *
 * Time Complexity (Amortized):
 * - Insert: O(log n)
 * - Delete: O(log n)
 * - Search: O(log n)
 * - Access: O(log n)
 *
 * Space Complexity: O(n)
 *
 * Use Cases:
 * - Recently accessed elements are faster to retrieve
 * - Cache-like behavior
 * - Adaptive performance for skewed access patterns
 * - Competitive with other balanced BSTs asymptotically
 *
 * Key Insight:
 * - After each operation, splay the accessed node to root
 * - Splaying uses zig, zig-zig, and zig-zag rotations
 * - Self-balancing without explicit balance factors
 * - Amortized analysis gives O(log n) per operation
 */
public class SplayTree {

    static class Node {
        int key;
        Node left, right, parent;

        Node(int key) {
            this.key = key;
        }
    }

    private Node root;

    /**
     * Initialize empty splay tree.
     */
    public SplayTree() {
        this.root = null;
    }

    /**
     * Right rotation around node x.
     */
    private void rotateRight(Node x) {
        Node y = x.left;
        x.left = y.right;
        if (y.right != null) {
            y.right.parent = x;
        }
        y.parent = x.parent;
        if (x.parent == null) {
            root = y;
        } else if (x == x.parent.right) {
            x.parent.right = y;
        } else {
            x.parent.left = y;
        }
        y.right = x;
        x.parent = y;
    }

    /**
     * Left rotation around node x.
     */
    private void rotateLeft(Node x) {
        Node y = x.right;
        x.right = y.left;
        if (y.left != null) {
            y.left.parent = x;
        }
        y.parent = x.parent;
        if (x.parent == null) {
            root = y;
        } else if (x == x.parent.left) {
            x.parent.left = y;
        } else {
            x.parent.right = y;
        }
        y.left = x;
        x.parent = y;
    }

    /**
     * Splay node x to root.
     */
    private void splay(Node x) {
        while (x.parent != null) {
            Node parent = x.parent;
            Node grandparent = parent.parent;

            if (grandparent == null) {
                // Zig: node is child of root
                if (x == parent.left) {
                    rotateRight(parent);
                } else {
                    rotateLeft(parent);
                }
            } else if (parent == grandparent.left) {
                if (x == parent.left) {
                    // Zig-zig (left-left)
                    rotateRight(grandparent);
                    rotateRight(parent);
                } else {
                    // Zig-zag (left-right)
                    rotateLeft(parent);
                    rotateRight(grandparent);
                }
            } else {
                if (x == parent.right) {
                    // Zig-zig (right-right)
                    rotateLeft(grandparent);
                    rotateLeft(parent);
                } else {
                    // Zig-zag (right-left)
                    rotateRight(parent);
                    rotateLeft(grandparent);
                }
            }
        }
    }

    /**
     * Insert key into splay tree.
     *
     * @param key Key to insert
     * @return true if key was inserted, false if duplicate
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public boolean insert(int key) {
        if (root == null) {
            root = new Node(key);
            return true;
        }

        Node curr = root;
        while (true) {
            if (key == curr.key) {
                splay(curr);
                return false;  // Duplicate
            }

            if (key < curr.key) {
                if (curr.left != null) {
                    curr = curr.left;
                } else {
                    curr.left = new Node(key);
                    curr.left.parent = curr;
                    splay(curr.left);
                    return true;
                }
            } else {
                if (curr.right != null) {
                    curr = curr.right;
                } else {
                    curr.right = new Node(key);
                    curr.right.parent = curr;
                    splay(curr.right);
                    return true;
                }
            }
        }
    }

    /**
     * Search for key in splay tree.
     *
     * @param key Key to search for
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
        Node curr = root;
        while (curr != null) {
            if (key == curr.key) {
                splay(curr);
                return true;
            } else if (key < curr.key) {
                curr = curr.left;
            } else {
                curr = curr.right;
            }
        }
        return false;
    }

    /**
     * Delete key from splay tree.
     *
     * @param key Key to delete
     * @return true if key was deleted
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public boolean delete(int key) {
        if (!search(key)) {
            return false;
        }

        // key is now at root
        Node leftSubtree = root.left;
        Node rightSubtree = root.right;

        if (leftSubtree == null) {
            root = rightSubtree;
            if (root != null) {
                root.parent = null;
            }
            return true;
        }

        // Find max in left subtree and splay it
        Node maxNode = leftSubtree;
        while (maxNode.right != null) {
            maxNode = maxNode.right;
        }

        root = leftSubtree;
        root.parent = null;
        splay(maxNode);

        // Attach right subtree
        root.right = rightSubtree;
        if (rightSubtree != null) {
            rightSubtree.parent = root;
        }

        return true;
    }

    /**
     * Get inorder traversal of tree.
     *
     * @return List of keys in sorted order
     */
    public List<Integer> inorder() {
        List<Integer> result = new ArrayList<>();
        inorderHelper(root, result);
        return result;
    }

    private void inorderHelper(Node node, List<Integer> result) {
        if (node != null) {
            inorderHelper(node.left, result);
            result.add(node.key);
            inorderHelper(node.right, result);
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
        SplayTree tree = new SplayTree();

        // Test insertions
        int[] keys = {50, 30, 70, 20, 40, 60, 80, 10, 25, 35, 65};
        System.out.print("Inserting keys: [");
        for (int i = 0; i < keys.length; i++) {
            if (i > 0) System.out.print(", ");
            System.out.print(keys[i]);
            tree.insert(keys[i]);
        }
        System.out.println("]");

        System.out.println("Inorder traversal: " + tree.inorder());

        // Test search
        System.out.println("\nSearching for 35: " + tree.search(35));
        System.out.println("Inorder after search(35): " + tree.inorder());

        // Test search not found
        System.out.println("\nSearching for 100: " + tree.search(100));

        // Test deletion
        System.out.println("\nDeleting 30...");
        tree.delete(30);
        System.out.println("Inorder after delete(30): " + tree.inorder());

        System.out.println("\nDeleting 50 (root)...");
        tree.delete(50);
        System.out.println("Inorder after delete(50): " + tree.inorder());

        // Test search after delete
        System.out.println("\n35 in tree: " + tree.search(35));
        System.out.println("30 in tree: " + tree.search(30));
    }
}
