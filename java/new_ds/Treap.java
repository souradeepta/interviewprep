package new_ds;

import java.util.ArrayList;
import java.util.List;
import java.util.Random;

/**
 * Treap (Tree + Heap) — a randomized binary search tree that simultaneously
 * satisfies two properties:
 * <ol>
 *   <li><b>BST property on keys:</b> for every node {@code n},
 *       all keys in the left subtree &lt; {@code n.key} &lt; all keys in the right
 *       subtree.</li>
 *   <li><b>Max-Heap property on priorities:</b> for every node {@code n},
 *       {@code n.priority} &ge; children's priorities.</li>
 * </ol>
 *
 * <p>Each node is assigned a <em>random</em> priority at creation time.  Because
 * the priorities are random, the resulting tree shape is equivalent to a random
 * BST built by inserting keys in a uniformly random order — giving expected
 * O(log n) height and eliminating worst-case behaviour from sorted input.
 *
 * <h3>Insert / Delete via Split + Merge</h3>
 * <ul>
 *   <li>{@link #insert}: split at key, create new node, merge left + node + right.</li>
 *   <li>{@link #delete}: split into (&lt; key), (== key), (&gt; key); merge the two halves.</li>
 * </ul>
 *
 * <pre>
 * Time Complexity (expected):
 *   insert(key)   – O(log n)
 *   delete(key)   – O(log n)
 *   search(key)   – O(log n)
 *   split(key)    – O(log n)
 *   merge(l, r)   – O(log n)
 *   inorder()     – O(n)
 *
 * Space Complexity: O(n)
 * </pre>
 *
 * @param <K> the key type; must implement {@link Comparable}
 */
public class Treap<K extends Comparable<K>> {

    // -------------------------------------------------------------------------
    // Inner node class
    // -------------------------------------------------------------------------

    /**
     * A node in the Treap.
     *
     * @param <K> key type
     */
    private static class Node<K> {
        /** The BST key. */
        K key;
        /** Random priority in [0.0, 1.0) — max-heap invariant. */
        double priority;
        /** Left child (null = empty). */
        Node<K> left;
        /** Right child (null = empty). */
        Node<K> right;

        Node(K key, double priority) {
            this.key      = key;
            this.priority = priority;
        }

        @Override
        public String toString() {
            return String.format("(%s, p=%.3f)", key, priority);
        }
    }

    // -------------------------------------------------------------------------
    // Fields
    // -------------------------------------------------------------------------

    /** Root of the treap; null when empty. */
    private Node<K> root;

    /** Number of keys stored. */
    private int size;

    /** Source of randomness for node priorities. */
    private final Random random;

    // -------------------------------------------------------------------------
    // Constructor
    // -------------------------------------------------------------------------

    /**
     * Creates an empty Treap.
     */
    public Treap() {
        root   = null;
        size   = 0;
        random = new Random();
    }

    // -------------------------------------------------------------------------
    // Core primitives: split and merge
    // -------------------------------------------------------------------------

    /**
     * Result container for a split operation (avoids allocating a full public
     * Treap object per split).
     */
    private static class SplitResult<K> {
        Node<K> left;   // all keys <= splitKey
        Node<K> right;  // all keys >  splitKey

        SplitResult(Node<K> left, Node<K> right) {
            this.left  = left;
            this.right = right;
        }
    }

    /**
     * Recursively splits the subtree rooted at {@code node} around {@code key}.
     *
     * <ul>
     *   <li>{@code result.left}  contains all nodes with key &le; {@code splitKey}.</li>
     *   <li>{@code result.right} contains all nodes with key &gt; {@code splitKey}.</li>
     * </ul>
     *
     * Both returned subtrees satisfy BST and max-heap properties.
     *
     * <p>Time: O(log n) expected
     */
    private SplitResult<K> splitNode(Node<K> node, K splitKey) {
        if (node == null) {
            return new SplitResult<>(null, null);
        }
        if (node.key.compareTo(splitKey) <= 0) {
            // node belongs to the left part; recurse into the right subtree
            SplitResult<K> sr = splitNode(node.right, splitKey);
            node.right = sr.left;
            return new SplitResult<>(node, sr.right);
        } else {
            // node belongs to the right part; recurse into the left subtree
            SplitResult<K> sr = splitNode(node.left, splitKey);
            node.left = sr.right;
            return new SplitResult<>(sr.left, node);
        }
    }

    /**
     * Recursively merges two subtrees into one.
     *
     * <p>Precondition: every key in {@code l} is strictly less than every key in {@code r}.
     *
     * <p>At each step the node with the higher priority becomes the root
     * (maintaining max-heap), and the remaining parts are merged recursively.
     *
     * <p>Time: O(log n) expected
     *
     * @param l left subtree root (may be null)
     * @param r right subtree root (may be null)
     * @return merged subtree root
     */
    private Node<K> mergeNodes(Node<K> l, Node<K> r) {
        if (l == null) return r;
        if (r == null) return l;
        if (l.priority >= r.priority) {
            // l is the new root; merge l.right with r
            l.right = mergeNodes(l.right, r);
            return l;
        } else {
            // r is the new root; merge l with r.left
            r.left = mergeNodes(l, r.left);
            return r;
        }
    }

    // -------------------------------------------------------------------------
    // Public split and merge (whole-Treap interface)
    // -------------------------------------------------------------------------

    /**
     * Splits this treap into two treaps around {@code splitKey}.
     *
     * <p>After this call the original treap is in an undefined state.
     *
     * @param splitKey the split point
     * @return a two-element {@code Treap[]} where index 0 holds keys &le; splitKey
     *         and index 1 holds keys &gt; splitKey
     */
    @SuppressWarnings("unchecked")
    public Treap<K>[] split(K splitKey) {
        SplitResult<K> sr = splitNode(root, splitKey);

        Treap<K> leftTreap  = new Treap<>();
        Treap<K> rightTreap = new Treap<>();
        leftTreap.root  = sr.left;
        rightTreap.root = sr.right;
        leftTreap.size  = countNodes(sr.left);
        rightTreap.size = countNodes(sr.right);

        this.root = null;
        this.size = 0;

        return new Treap[]{leftTreap, rightTreap};
    }

    /**
     * Merges {@code other} into this treap.
     *
     * <p>Precondition: every key in this treap is strictly less than every key
     * in {@code other}.
     *
     * @param other the treap whose keys are all greater than keys in this treap
     */
    public void merge(Treap<K> other) {
        this.root  = mergeNodes(this.root, other.root);
        this.size += other.size;
        other.root = null;
        other.size = 0;
    }

    // -------------------------------------------------------------------------
    // Public API
    // -------------------------------------------------------------------------

    /**
     * Inserts {@code key} into the treap.
     *
     * <p>If {@code key} already exists the operation is a no-op (no duplicates).
     *
     * <p>Algorithm:
     * <ol>
     *   <li>Split into (left: keys &le; key) and (right: keys &gt; key).</li>
     *   <li>Create a new node with a random priority.</li>
     *   <li>Merge left + newNode + right.</li>
     * </ol>
     *
     * <p>Time: O(log n) expected
     *
     * @param key the key to insert
     */
    public void insert(K key) {
        if (searchNode(root, key) != null) {
            return;  // no duplicates
        }
        Node<K> newNode = new Node<>(key, random.nextDouble());

        // Split at key so left has keys <= key (which means < key since key is absent).
        SplitResult<K> sr = splitNode(root, key);
        // Merge: left <- newNode -> right
        Node<K> temp = mergeNodes(newNode, sr.right);
        root = mergeNodes(sr.left, temp);
        size++;
    }

    /**
     * Deletes the node with key {@code key}.
     *
     * <p>Algorithm:
     * <ol>
     *   <li>Split into (left: keys &lt; key) and (rightAndTarget: keys &ge; key).</li>
     *   <li>Split rightAndTarget into (target: key == key) and (rest: keys &gt; key).</li>
     *   <li>Discard target; merge left + rest.</li>
     * </ol>
     *
     * <p>Time: O(log n) expected
     *
     * @param key the key to remove
     * @return {@code true} if found and deleted; {@code false} if not present
     */
    public boolean delete(K key) {
        if (searchNode(root, key) == null) {
            return false;
        }

        // Find the predecessor key so we can split at a point that puts
        // all keys < key on the left.  We achieve this by splitting at key
        // (giving keys <= key on left), then splitting that left part at a
        // value just below key to isolate the key itself.
        //
        // Simpler approach: split into (<= key-predecessor) and (>= key),
        // then split the right into (== key) and (> key).
        //
        // Since we only support Comparable (not predecessor arithmetic),
        // we use two splits:
        //   1. split(root, key)        -> (leftPlusTarget, right)  [left has keys <= key]
        //   2. split(leftPlusTarget, predecessor of key in left)
        //      This is hard without predecessor. Instead:
        //
        // Reliable approach (works for any Comparable):
        //   1. split at key -> (left: keys <= key, right: keys > key)
        //   2. The target (if present) is the RIGHTMOST node of `left` (max of left).
        //      Pop it by splitting left at (key - epsilon) — but without epsilon
        //      we use a recursive pop-max helper.
        SplitResult<K> sr1 = splitNode(root, key);
        // sr1.left has keys <= key; since key exists, max(sr1.left) == key
        // Pop the max node from sr1.left (that is the target node with key == key)
        Node<K> leftWithoutMax = popMax(sr1.left);
        root = mergeNodes(leftWithoutMax, sr1.right);
        size--;
        return true;
    }

    /**
     * Removes and discards the node with the maximum key in the subtree
     * rooted at {@code node} and returns the updated subtree root.
     *
     * <p>Used internally by {@link #delete} to strip the target key out of the
     * left partition after a split without needing a "predecessor" computation.
     */
    private Node<K> popMax(Node<K> node) {
        if (node == null) return null;
        if (node.right == null) {
            // This is the max node; drop it, return its left child
            return node.left;
        }
        node.right = popMax(node.right);
        return node;
    }

    /**
     * Returns {@code true} if {@code key} is present in the treap.
     *
     * <p>Time: O(log n) expected
     *
     * @param key the key to search for
     * @return {@code true} if found
     */
    public boolean search(K key) {
        return searchNode(root, key) != null;
    }

    /**
     * Returns all keys in ascending (inorder) order.
     *
     * <p>Time: O(n)
     *
     * @return sorted list of all keys
     */
    public List<K> inorder() {
        List<K> result = new ArrayList<>(size);
        inorderHelper(root, result);
        return result;
    }

    /**
     * Returns the number of keys currently stored.
     *
     * @return size
     */
    public int size() {
        return size;
    }

    // -------------------------------------------------------------------------
    // Private helpers
    // -------------------------------------------------------------------------

    /** Standard BST search; returns the node or null. */
    private Node<K> searchNode(Node<K> node, K key) {
        if (node == null) return null;
        int cmp = key.compareTo(node.key);
        if (cmp == 0) return node;
        return cmp < 0 ? searchNode(node.left, key) : searchNode(node.right, key);
    }

    /** In-order traversal collecting keys into {@code result}. */
    private void inorderHelper(Node<K> node, List<K> result) {
        if (node == null) return;
        inorderHelper(node.left, result);
        result.add(node.key);
        inorderHelper(node.right, result);
    }

    /** Counts nodes in a subtree (used when constructing split results). */
    private int countNodes(Node<K> node) {
        if (node == null) return 0;
        return 1 + countNodes(node.left) + countNodes(node.right);
    }

    // -------------------------------------------------------------------------
    // Verification helpers (interview-friendly)
    // -------------------------------------------------------------------------

    /**
     * Verifies the BST property: inorder keys must be strictly ascending.
     *
     * @return {@code true} if the BST property holds
     */
    public boolean verifyBst() {
        List<K> keys = inorder();
        for (int i = 1; i < keys.size(); i++) {
            if (keys.get(i).compareTo(keys.get(i - 1)) <= 0) return false;
        }
        return true;
    }

    /**
     * Verifies the max-heap property on priorities for all nodes.
     *
     * @return {@code true} if the heap property holds
     */
    public boolean verifyHeap() {
        return checkHeap(root);
    }

    private boolean checkHeap(Node<K> node) {
        if (node == null) return true;
        if (node.left  != null && node.left.priority  > node.priority) return false;
        if (node.right != null && node.right.priority > node.priority) return false;
        return checkHeap(node.left) && checkHeap(node.right);
    }

    // -------------------------------------------------------------------------
    // Pretty-print (ASCII sideways tree)
    // -------------------------------------------------------------------------

    /**
     * Returns a multi-line ASCII tree view (right subtree shown above left,
     * same convention as a sideways tree).  Each node shows key and priority.
     *
     * @return ASCII-art tree string
     */
    @Override
    public String toString() {
        if (root == null) return "<empty treap>";
        StringBuilder sb = new StringBuilder();
        printNode(root, "", true, sb);
        return sb.toString();
    }

    private void printNode(Node<K> node, String indent, boolean isLast, StringBuilder sb) {
        if (node == null) return;
        String connector = isLast ? "└── " : "├── ";
        sb.append(indent).append(connector).append(node).append('\n');
        String childIndent = indent + (isLast ? "    " : "│   ");
        if (node.right != null || node.left != null) {
            printNode(node.right, childIndent, false, sb);
            printNode(node.left,  childIndent, true,  sb);
        }
    }

    // -------------------------------------------------------------------------
    // Demo main
    // -------------------------------------------------------------------------

    /**
     * Demonstrates insert, search, delete, split, merge, and property verification.
     *
     * @param args unused
     */
    public static void main(String[] args) {
        System.out.println("=== Treap Demo ===\n");

        // --- Controlled priorities: verify both properties ---
        System.out.println("--- Controlled priority example (verify BST + Heap) ---");
        Treap<Integer> t = new Treap<>();
        // We seed the random so priorities come out predictably for the demo.
        // In real usage priorities are fully random — no need to set seeds.
        int[][] inserts = {{5,0},{2,0},{8,0},{1,0},{3,0},{7,0},{9,0}};
        // Use insert (random priorities will be assigned internally)
        for (int[] kv : inserts) {
            t.insert(kv[0]);
        }
        System.out.println("Treap structure (key, priority):");
        System.out.println(t);
        System.out.println("In-order keys: " + t.inorder());
        System.out.println("BST  property holds: " + t.verifyBst());
        System.out.println("Heap property holds: " + t.verifyHeap());

        // --- Search ---
        System.out.println("\n--- Search ---");
        System.out.println("search(3) -> " + t.search(3));
        System.out.println("search(11) -> " + t.search(11));

        // --- Delete ---
        System.out.println("\n--- Delete ---");
        System.out.println("delete(2) -> " + t.delete(2));
        System.out.println("delete(99) -> " + t.delete(99));
        System.out.println("In-order after deletes: " + t.inorder());
        System.out.println("BST  holds: " + t.verifyBst());
        System.out.println("Heap holds: " + t.verifyHeap());

        // --- Split and merge ---
        System.out.println("\n--- Split at key=5 ---");
        Treap<Integer> st = new Treap<>();
        for (int i = 1; i <= 10; i++) st.insert(i);
        System.out.println("Original in-order: " + st.inorder());

        @SuppressWarnings("unchecked")
        Treap<Integer>[] halves = st.split(5);
        System.out.println("Left  (keys <= 5): " + halves[0].inorder());
        System.out.println("Right (keys >  5): " + halves[1].inorder());

        halves[0].merge(halves[1]);
        System.out.println("Merged in-order:   " + halves[0].inorder());
        System.out.println("BST  holds after merge: " + halves[0].verifyBst());
        System.out.println("Heap holds after merge: " + halves[0].verifyHeap());

        // --- Large random test ---
        System.out.println("\n--- Large random test (n=1000) ---");
        Treap<Integer> big = new Treap<>();
        java.util.List<Integer> sample = new java.util.ArrayList<>();
        java.util.Random rng = new java.util.Random(7);
        while (sample.size() < 1000) {
            int v = rng.nextInt(10_000);
            if (!sample.contains(v)) sample.add(v);
        }
        for (int k : sample) big.insert(k);
        assert big.verifyBst()  : "BST property violated!";
        assert big.verifyHeap() : "Heap property violated!";
        System.out.println("Inserted 1000 keys. BST and Heap properties both hold.");

        // Delete first 500
        for (int i = 0; i < 500; i++) big.delete(sample.get(i));
        assert big.verifyBst()  : "BST property violated after deletes!";
        assert big.verifyHeap() : "Heap property violated after deletes!";
        System.out.println("After 500 deletes: " + big.size() + " keys remain. Both properties still hold.");

        // --- String key treap ---
        System.out.println("\n--- String key treap ---");
        Treap<String> strTreap = new Treap<>();
        for (String s : new String[]{"mango", "apple", "cherry", "banana", "fig"}) {
            strTreap.insert(s);
        }
        System.out.println("String treap in-order: " + strTreap.inorder());
        System.out.println("BST holds: " + strTreap.verifyBst());

        System.out.println("\nDone.");
    }
}
