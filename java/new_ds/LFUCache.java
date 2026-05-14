package new_ds;

import java.util.HashMap;
import java.util.Map;

/**
 * LFU (Least Frequently Used) Cache — evicts the item that has been accessed
 * the fewest number of times. When multiple items share the minimum frequency,
 * the <em>least recently used</em> (LRU) among them is evicted.
 *
 * <h3>Data structures (O(1) get and put)</h3>
 * <ul>
 *   <li>{@code keyMap} — {@code key → Node} for O(1) node lookup.</li>
 *   <li>{@code freqMap} — {@code freq → FreqBucket} (a doubly linked list of
 *       nodes sharing that frequency), ordered LRU → MRU.</li>
 *   <li>{@code minFreq} — tracks the current minimum frequency so the eviction
 *       victim is found in O(1).</li>
 * </ul>
 *
 * <h3>Invariants</h3>
 * <ul>
 *   <li>Every node in {@code keyMap} lives in exactly one {@code freqMap} bucket.</li>
 *   <li>{@code minFreq} always points to the frequency of the LFU item(s).</li>
 *   <li>A new item always enters at {@code freq = 1}, so after any eviction the
 *       next insertion resets {@code minFreq} to 1.</li>
 * </ul>
 *
 * <pre>
 * Time Complexity:
 *   get(key)   – O(1)
 *   put(key,v) – O(1)
 *
 * Space Complexity: O(capacity)
 * </pre>
 *
 * @param <K> the type of keys
 * @param <V> the type of values
 */
public class LFUCache<K, V> {

    // -------------------------------------------------------------------------
    // Inner types
    // -------------------------------------------------------------------------

    /**
     * A doubly-linked list node holding one cache entry.
     *
     * <p>The node stores its own {@code freq} so it can be moved between
     * frequency buckets in O(1) without additional lookups.
     */
    private class Node {
        K key;
        V val;
        int freq;
        Node prev;
        Node next;

        Node(K key, V val, int freq) {
            this.key  = key;
            this.val  = val;
            this.freq = freq;
        }
    }

    /**
     * A doubly-linked list that holds all nodes with the same access frequency.
     *
     * <p>Nodes are ordered from LRU (closest to {@code head}) to MRU
     * (closest to {@code tail}).  New nodes are appended at the MRU end;
     * eviction removes from the LRU end.
     */
    private class FreqBucket {
        /** Sentinel head (not a real cache entry). */
        final Node head = new Node(null, null, 0);
        /** Sentinel tail (not a real cache entry). */
        final Node tail = new Node(null, null, 0);
        int size;

        FreqBucket() {
            head.next = tail;
            tail.prev = head;
            size = 0;
        }

        /** Appends {@code node} at the MRU (tail) end. */
        void append(Node node) {
            node.prev       = tail.prev;
            node.next       = tail;
            tail.prev.next  = node;
            tail.prev       = node;
            size++;
        }

        /** Removes {@code node} from anywhere in the list in O(1). */
        void remove(Node node) {
            node.prev.next = node.next;
            node.next.prev = node.prev;
            node.prev      = null;
            node.next      = null;
            size--;
        }

        /**
         * Removes and returns the LRU node ({@code head.next}),
         * or {@code null} if empty.
         */
        Node popLru() {
            if (size == 0) return null;
            Node lru = head.next;
            remove(lru);
            return lru;
        }

        boolean isEmpty() {
            return size == 0;
        }
    }

    // -------------------------------------------------------------------------
    // Fields
    // -------------------------------------------------------------------------

    /** Maximum number of entries the cache can hold. */
    private final int capacity;

    /** Current number of entries. */
    private int size;

    /** Current minimum access frequency among all cached entries. */
    private int minFreq;

    /** Maps each key to its node for O(1) access. */
    private final Map<K, Node> keyMap;

    /** Maps each frequency to its bucket of nodes. */
    private final Map<Integer, FreqBucket> freqMap;

    // -------------------------------------------------------------------------
    // Constructor
    // -------------------------------------------------------------------------

    /**
     * Creates an LFU cache with the specified capacity.
     *
     * @param capacity maximum number of entries (must be &gt; 0)
     * @throws IllegalArgumentException if capacity &le; 0
     */
    public LFUCache(int capacity) {
        if (capacity <= 0) {
            throw new IllegalArgumentException("Capacity must be a positive integer");
        }
        this.capacity = capacity;
        this.size     = 0;
        this.minFreq  = 0;
        this.keyMap   = new HashMap<>();
        this.freqMap  = new HashMap<>();
    }

    // -------------------------------------------------------------------------
    // Private helpers
    // -------------------------------------------------------------------------

    /**
     * Returns (creating if absent) the {@link FreqBucket} for {@code freq}.
     */
    private FreqBucket bucketFor(int freq) {
        return freqMap.computeIfAbsent(freq, f -> new FreqBucket());
    }

    /**
     * Moves {@code node} from its current frequency bucket to the next one,
     * updating {@code minFreq} if the old bucket is now empty and was the minimum.
     *
     * <p>Time: O(1)
     */
    private void incrementFreq(Node node) {
        int f = node.freq;
        bucketFor(f).remove(node);
        if (freqMap.get(f).isEmpty() && f == minFreq) {
            minFreq++;
        }
        node.freq++;
        bucketFor(node.freq).append(node);
    }

    // -------------------------------------------------------------------------
    // Public API
    // -------------------------------------------------------------------------

    /**
     * Returns the value associated with {@code key}, or {@code null} if absent.
     *
     * <p>Also increments the access frequency of the key.
     *
     * <p>Time: O(1)
     *
     * @param key the key to look up
     * @return the cached value, or {@code null} if not present
     */
    public V get(K key) {
        Node node = keyMap.get(key);
        if (node == null) return null;
        incrementFreq(node);
        return node.val;
    }

    /**
     * Inserts or updates {@code key} with {@code value}.
     *
     * <p>On capacity overflow the LFU item (LRU tiebreaker) is evicted first.
     * New items always start with frequency 1.
     *
     * <p>Time: O(1)
     *
     * @param key   the key
     * @param value the value to associate with the key
     */
    public void put(K key, V value) {
        if (keyMap.containsKey(key)) {
            Node node = keyMap.get(key);
            node.val  = value;
            incrementFreq(node);
            return;
        }

        if (size >= capacity) {
            // Evict the LRU node from the minimum-frequency bucket.
            FreqBucket minBucket = freqMap.get(minFreq);
            if (minBucket != null) {
                Node evicted = minBucket.popLru();
                if (evicted != null) {
                    keyMap.remove(evicted.key);
                    size--;
                }
            }
        }

        Node newNode = new Node(key, value, 1);
        keyMap.put(key, newNode);
        bucketFor(1).append(newNode);
        minFreq = 1;  // new item always has the lowest possible frequency
        size++;
    }

    /**
     * Returns the current number of entries in the cache.
     *
     * @return current size
     */
    public int size() {
        return size;
    }

    /**
     * Returns the maximum capacity of the cache.
     *
     * @return capacity
     */
    public int capacity() {
        return capacity;
    }

    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append("LFUCache(capacity=").append(capacity)
          .append(", size=").append(size)
          .append(", minFreq=").append(minFreq)
          .append(", entries={");
        for (Map.Entry<K, Node> e : keyMap.entrySet()) {
            sb.append(e.getKey()).append(":(").append(e.getValue().val)
              .append(",f=").append(e.getValue().freq).append(") ");
        }
        sb.append("})");
        return sb.toString();
    }

    // -------------------------------------------------------------------------
    // Demo main
    // -------------------------------------------------------------------------

    /**
     * Demonstrates O(1) LFU cache semantics: frequency-based eviction with
     * LRU tiebreaking.
     *
     * @param args unused
     */
    public static void main(String[] args) {
        System.out.println("=== LFU Cache Demo ===\n");

        // --- Basic scenario: capacity 3 ---
        System.out.println("--- Capacity = 3. Put keys 1, 2, 3. ---");
        LFUCache<Integer, String> cache = new LFUCache<>(3);
        cache.put(1, "one");
        cache.put(2, "two");
        cache.put(3, "three");
        System.out.println(cache);

        System.out.println("\nAccess key 1 twice, key 2 once:");
        System.out.println("  get(1) -> " + cache.get(1));
        System.out.println("  get(1) -> " + cache.get(1));
        System.out.println("  get(2) -> " + cache.get(2));
        System.out.println("  Frequencies now: 1->3, 2->2, 3->1");
        System.out.println(cache);

        System.out.println("\nPut key 4 (should evict key 3 — LFU with freq=1):");
        cache.put(4, "four");
        System.out.println("  get(3) -> " + cache.get(3) + "  (expected null — evicted)");
        System.out.println("  get(4) -> " + cache.get(4) + "  (expected 'four')");
        System.out.println(cache);

        System.out.println("\nPut key 5 (key 4 has freq=1, is LFU; evict it):");
        cache.put(5, "five");
        System.out.println("  get(4) -> " + cache.get(4) + "  (expected null — evicted)");
        System.out.println("  get(5) -> " + cache.get(5) + "  (expected 'five')");
        System.out.println(cache);

        // --- Frequency eviction showcase ---
        System.out.println("\n--- Frequency eviction showcase (capacity=4) ---");
        LFUCache<String, String> c = new LFUCache<>(4);
        c.put("a", "alpha");
        c.put("b", "beta");
        c.put("c", "gamma");
        c.put("d", "delta");

        // Boost frequencies
        c.get("a"); c.get("a"); c.get("a");  // a -> freq 4
        c.get("b"); c.get("b");              // b -> freq 3
        c.get("c");                          // c -> freq 2
        // d stays at freq 1 — will be evicted

        System.out.println("After accesses: a->freq4, b->freq3, c->freq2, d->freq1");
        c.put("e", "epsilon");               // should evict d
        System.out.println("Put 'e' (evicts 'd'):");
        System.out.println("  get('d') -> " + c.get("d") + "  (expected null)");
        System.out.println("  get('e') -> " + c.get("e") + "  (expected 'epsilon')");
        System.out.println(c);

        // --- Update existing key ---
        System.out.println("\n--- Updating an existing key ---");
        LFUCache<String, Integer> scores = new LFUCache<>(3);
        scores.put("alice", 10);
        scores.put("bob",   20);
        scores.put("alice", 30);  // update — should increment freq, not evict
        System.out.println("  get('alice') -> " + scores.get("alice") + "  (expected 30)");
        System.out.println("  get('bob')   -> " + scores.get("bob")   + "  (expected 20)");
        System.out.println(scores);

        System.out.println("\nDone.");
    }
}
