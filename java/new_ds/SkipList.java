package new_ds;

import java.util.Random;

/**
 * Skip List — a probabilistic data structure that allows O(log n) average-case
 * search, insertion, and deletion by maintaining multiple linked-list "levels".
 *
 * <p>Each node at level {@code i} is also present at level {@code i-1}.
 * A coin flip (p = 0.5) determines how many levels a new node is promoted to.
 *
 * <pre>
 * Time Complexity (average):
 *   insert   – O(log n)
 *   search   – O(log n)
 *   delete   – O(log n)
 *
 * Time Complexity (worst):
 *   insert   – O(n)
 *   search   – O(n)
 *   delete   – O(n)
 *
 * Space Complexity: O(n log n) expected
 * </pre>
 *
 * @param <T> the type of values stored in the list
 */
public class SkipList<T> {

    // -------------------------------------------------------------------------
    // Constants
    // -------------------------------------------------------------------------

    /** Maximum number of levels in the skip list. */
    private static final int MAX_LEVEL = 16;

    /** Probability of promoting a node to the next level. */
    private static final double P = 0.5;

    // -------------------------------------------------------------------------
    // Inner node class
    // -------------------------------------------------------------------------

    /**
     * A node in the skip list.
     *
     * <p>Each node stores a key-value pair and an array of {@code forward}
     * pointers — one per level at which this node participates.
     * {@code forward[0]} is the ordinary next pointer (level 0).
     *
     * @param <V> value type
     */
    @SuppressWarnings("unchecked")
    public static class SkipListNode<V> {

        /** Integer search key. */
        final int key;

        /** User-supplied value; may be {@code null} for sentinel nodes. */
        V value;

        /**
         * Forward pointers indexed by level.
         * {@code forward[i]} points to the next node at level {@code i}.
         */
        final SkipListNode<V>[] forward;

        /** Number of levels at which this node participates (its "height"). */
        final int level;

        /**
         * Constructs a node with the given key, value, and level.
         *
         * @param key   the integer key
         * @param value the associated value
         * @param level the height of this node (number of forward pointers)
         */
        SkipListNode(int key, V value, int level) {
            this.key     = key;
            this.value   = value;
            this.level   = level;
            this.forward = new SkipListNode[level + 1];
        }

        @Override
        public String toString() {
            return "(" + key + ":" + value + ")";
        }
    }

    // -------------------------------------------------------------------------
    // Fields
    // -------------------------------------------------------------------------

    /** Sentinel header node (key = Integer.MIN_VALUE, not visible to callers). */
    private final SkipListNode<T> head;

    /** Current highest level in use (0-indexed). */
    private int currentLevel;

    /** Number of key-value pairs stored. */
    private int size;

    /** Source of randomness for level generation. */
    private final Random random;

    // -------------------------------------------------------------------------
    // Constructor
    // -------------------------------------------------------------------------

    /**
     * Creates an empty skip list.
     */
    public SkipList() {
        head         = new SkipListNode<>(Integer.MIN_VALUE, null, MAX_LEVEL);
        currentLevel = 0;
        size         = 0;
        random       = new Random();
    }

    // -------------------------------------------------------------------------
    // Private helpers
    // -------------------------------------------------------------------------

    /**
     * Generates a random level for a new node using geometric distribution.
     *
     * <p>Starting at level 1, each successive level is included with
     * probability {@link #P} until {@link #MAX_LEVEL} is reached.
     *
     * @return a level in [1, MAX_LEVEL]
     */
    private int randomLevel() {
        int level = 1;
        while (random.nextDouble() < P && level < MAX_LEVEL) {
            level++;
        }
        return level;
    }

    /**
     * Builds the {@code update} array used by insert and delete.
     *
     * <p>{@code update[i]} is the rightmost node at level {@code i} whose key
     * is strictly less than {@code key}.
     *
     * @param key the target key
     * @return update array of length MAX_LEVEL + 1
     */
    @SuppressWarnings("unchecked")
    private SkipListNode<T>[] buildUpdate(int key) {
        SkipListNode<T>[] update = new SkipListNode[MAX_LEVEL + 1];
        SkipListNode<T>   curr   = head;

        for (int i = currentLevel; i >= 0; i--) {
            while (curr.forward[i] != null && curr.forward[i].key < key) {
                curr = curr.forward[i];
            }
            update[i] = curr;
        }
        return update;
    }

    // -------------------------------------------------------------------------
    // Public API
    // -------------------------------------------------------------------------

    /**
     * Inserts or updates a key-value pair.
     *
     * <p>If {@code key} already exists the value is overwritten.
     * Otherwise a new node is created at a randomly chosen level.
     *
     * <p>Time: O(log n) average &nbsp;|&nbsp; Space: O(log n) average (new node)
     *
     * @param key   the integer key
     * @param value the value to associate with {@code key}
     */
    public void insert(int key, T value) {
        SkipListNode<T>[] update = buildUpdate(key);

        // The candidate node immediately to the right at level 0.
        SkipListNode<T> curr = update[0].forward[0];

        // Key already exists — update in place.
        if (curr != null && curr.key == key) {
            curr.value = value;
            return;
        }

        int newLevel = randomLevel();

        // If new node is taller than anything seen so far, extend update array.
        if (newLevel > currentLevel) {
            for (int i = currentLevel + 1; i <= newLevel; i++) {
                update[i] = head;
            }
            currentLevel = newLevel;
        }

        SkipListNode<T> newNode = new SkipListNode<>(key, value, newLevel);

        // Splice new node into each level.
        for (int i = 0; i <= newLevel; i++) {
            newNode.forward[i]   = update[i].forward[i];
            update[i].forward[i] = newNode;
        }

        size++;
    }

    /**
     * Searches for a key and returns its associated value, or {@code null}
     * if the key is not present.
     *
     * <p>Time: O(log n) average
     *
     * @param key the integer key to look up
     * @return the associated value, or {@code null}
     */
    public T search(int key) {
        SkipListNode<T> curr = head;

        for (int i = currentLevel; i >= 0; i--) {
            while (curr.forward[i] != null && curr.forward[i].key < key) {
                curr = curr.forward[i];
            }
        }

        curr = curr.forward[0];
        if (curr != null && curr.key == key) {
            return curr.value;
        }
        return null;
    }

    /**
     * Deletes the node with the given key.
     *
     * <p>Time: O(log n) average
     *
     * @param key the integer key to remove
     * @return {@code true} if the key was found and removed, {@code false} otherwise
     */
    public boolean delete(int key) {
        SkipListNode<T>[] update = buildUpdate(key);

        SkipListNode<T> curr = update[0].forward[0];

        if (curr == null || curr.key != key) {
            return false; // Key not found.
        }

        // Unlink the node from each level.
        for (int i = 0; i <= currentLevel; i++) {
            if (update[i].forward[i] != curr) {
                break; // Node doesn't reach this level.
            }
            update[i].forward[i] = curr.forward[i];
        }

        // Lower currentLevel if top levels became empty.
        while (currentLevel > 0 && head.forward[currentLevel] == null) {
            currentLevel--;
        }

        size--;
        return true;
    }

    /**
     * Returns the number of key-value pairs stored.
     *
     * @return size
     */
    public int size() {
        return size;
    }

    /**
     * Returns a multi-line string showing every level of the skip list.
     *
     * <p>Level 0 is the base (all nodes); higher levels contain fewer nodes.
     * Example output:
     * <pre>
     * Level 3: HEAD -> (7:G)
     * Level 2: HEAD -> (3:C) -> (7:G)
     * Level 1: HEAD -> (1:A) -> (3:C) -> (7:G)
     * Level 0: HEAD -> (1:A) -> (3:C) -> (5:E) -> (7:G)
     * </pre>
     *
     * @return multi-line string representation
     */
    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        for (int i = currentLevel; i >= 0; i--) {
            sb.append(String.format("Level %2d: HEAD", i));
            SkipListNode<T> curr = head.forward[i];
            while (curr != null) {
                sb.append(" -> ").append(curr);
                curr = curr.forward[i];
            }
            sb.append('\n');
        }
        return sb.toString();
    }

    // -------------------------------------------------------------------------
    // Demo main
    // -------------------------------------------------------------------------

    /**
     * Demonstrates insert, search, delete, and the multi-level toString.
     *
     * @param args unused
     */
    public static void main(String[] args) {
        SkipList<String> sl = new SkipList<>();

        System.out.println("=== Skip List Demo ===\n");

        // Insert
        int[] keys = {3, 6, 7, 9, 12, 19, 17, 26, 21, 25};
        String[] vals = {"C", "F", "G", "I", "L", "S", "Q", "Z", "U", "Y"};
        for (int i = 0; i < keys.length; i++) {
            sl.insert(keys[i], vals[i]);
            System.out.printf("Inserted (%d, %s)%n", keys[i], vals[i]);
        }

        System.out.println("\nSkip list after insertions:");
        System.out.println(sl);

        // Search
        System.out.println("Search  9 -> " + sl.search(9));
        System.out.println("Search 17 -> " + sl.search(17));
        System.out.println("Search 99 -> " + sl.search(99));

        // Update
        sl.insert(9, "IX");
        System.out.println("\nAfter updating key 9 to 'IX':");
        System.out.println(sl);

        // Delete
        System.out.println("Delete 12 -> " + sl.delete(12));
        System.out.println("Delete 99 -> " + sl.delete(99));
        System.out.println("\nSkip list after deleting 12:");
        System.out.println(sl);

        System.out.println("Size: " + sl.size());
    }
}
