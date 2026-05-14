package basic;

/**
 * A generic hash map using separate chaining for collision resolution.
 *
 * <p>Each bucket in the backing array holds the head of a singly linked list
 * of {@link Entry} nodes. When the load factor exceeds 0.75 the table is
 * resized to double its current number of buckets and all entries are
 * rehashed.
 *
 * <p>Time complexities (average case with a good hash function):
 * <ul>
 *   <li>put(K, V)        – O(1) amortised</li>
 *   <li>get(K)           – O(1)</li>
 *   <li>remove(K)        – O(1)</li>
 *   <li>containsKey(K)   – O(1)</li>
 *   <li>resize()         – O(n)</li>
 * </ul>
 * Worst-case (all keys collide): O(n) for get / put / remove.
 *
 * @param <K> the key type
 * @param <V> the value type
 */
public class HashMap<K, V> {

    // -----------------------------------------------------------------------
    // Inner Entry class
    // -----------------------------------------------------------------------

    /**
     * A key-value pair node used in each bucket's linked list.
     *
     * @param <K> the key type
     * @param <V> the value type
     */
    public static class Entry<K, V> {
        /** The key stored in this entry. */
        final K key;
        /** The value associated with the key. */
        V value;
        /** Pointer to the next entry in the same bucket. */
        Entry<K, V> next;

        /**
         * Constructs a new Entry.
         *
         * @param key   the key
         * @param value the value
         */
        Entry(K key, V value) {
            this.key = key;
            this.value = value;
            this.next = null;
        }

        /**
         * Returns a {@code key=value} string representation.
         *
         * @return string representation of this entry
         */
        @Override
        public String toString() {
            return key + "=" + value;
        }
    }

    // -----------------------------------------------------------------------
    // Fields
    // -----------------------------------------------------------------------

    /** Default number of buckets at construction time. */
    private static final int DEFAULT_CAPACITY = 16;

    /** Resize when size / numBuckets exceeds this threshold. */
    private static final double LOAD_FACTOR = 0.75;

    /** The bucket array. Each slot is the head of a chain, or {@code null}. */
    private Entry<K, V>[] buckets;

    /** Total number of key-value pairs stored. */
    private int size;

    // -----------------------------------------------------------------------
    // Constructors
    // -----------------------------------------------------------------------

    /**
     * Creates a HashMap with the default initial capacity (16 buckets).
     */
    @SuppressWarnings("unchecked")
    public HashMap() {
        buckets = new Entry[DEFAULT_CAPACITY];
        size = 0;
    }

    /**
     * Creates a HashMap with the specified initial number of buckets.
     *
     * @param initialCapacity number of buckets, must be &gt; 0
     * @throws IllegalArgumentException if initialCapacity &lt;= 0
     */
    @SuppressWarnings("unchecked")
    public HashMap(int initialCapacity) {
        if (initialCapacity <= 0) {
            throw new IllegalArgumentException("Capacity must be positive, got: " + initialCapacity);
        }
        buckets = new Entry[initialCapacity];
        size = 0;
    }

    // -----------------------------------------------------------------------
    // Core operations
    // -----------------------------------------------------------------------

    /**
     * Associates {@code value} with {@code key} in the map.
     *
     * <p>If the key already exists its value is replaced and the old value is
     * returned. Otherwise a new entry is prepended to the bucket chain and
     * {@code null} is returned.
     *
     * <p>Resizes the table when the load factor is exceeded.
     *
     * <p>Time complexity: O(1) amortised.
     *
     * @param key   the key (must not be {@code null})
     * @param value the value to associate
     * @return the previous value for this key, or {@code null} if none
     * @throws IllegalArgumentException if {@code key} is {@code null}
     */
    public V put(K key, V value) {
        checkKey(key);
        if ((double) size / buckets.length > LOAD_FACTOR) {
            resize();
        }
        int idx = bucketIndex(key);
        Entry<K, V> curr = buckets[idx];
        // Walk the chain to find an existing entry with this key
        while (curr != null) {
            if (curr.key.equals(key)) {
                V old = curr.value;
                curr.value = value;
                return old;
            }
            curr = curr.next;
        }
        // Key not found — prepend new entry to the chain
        Entry<K, V> newEntry = new Entry<>(key, value);
        newEntry.next = buckets[idx];
        buckets[idx] = newEntry;
        size++;
        return null;
    }

    /**
     * Returns the value associated with {@code key}, or {@code null} if the
     * key is not present.
     *
     * <p>Time complexity: O(1) average.
     *
     * @param key the key to look up
     * @return the associated value, or {@code null}
     * @throws IllegalArgumentException if {@code key} is {@code null}
     */
    public V get(K key) {
        checkKey(key);
        Entry<K, V> entry = findEntry(key);
        return entry == null ? null : entry.value;
    }

    /**
     * Removes the entry for {@code key} and returns its value, or
     * {@code null} if the key was not present.
     *
     * <p>Time complexity: O(1) average.
     *
     * @param key the key to remove
     * @return the removed value, or {@code null}
     * @throws IllegalArgumentException if {@code key} is {@code null}
     */
    public V remove(K key) {
        checkKey(key);
        int idx = bucketIndex(key);
        Entry<K, V> prev = null;
        Entry<K, V> curr = buckets[idx];
        while (curr != null) {
            if (curr.key.equals(key)) {
                if (prev == null) {
                    buckets[idx] = curr.next;
                } else {
                    prev.next = curr.next;
                }
                size--;
                return curr.value;
            }
            prev = curr;
            curr = curr.next;
        }
        return null; // key not found
    }

    /**
     * Returns {@code true} if the map contains a mapping for {@code key}.
     *
     * <p>Time complexity: O(1) average.
     *
     * @param key the key to test
     * @return {@code true} if the key is present
     * @throws IllegalArgumentException if {@code key} is {@code null}
     */
    public boolean containsKey(K key) {
        checkKey(key);
        return findEntry(key) != null;
    }

    /**
     * Returns the number of key-value pairs stored in the map.
     *
     * <p>Time complexity: O(1).
     *
     * @return current size
     */
    public int size() {
        return size;
    }

    /**
     * Returns {@code true} if the map contains no entries.
     *
     * @return {@code true} if empty
     */
    public boolean isEmpty() {
        return size == 0;
    }

    // -----------------------------------------------------------------------
    // Resize / rehash
    // -----------------------------------------------------------------------

    /**
     * Doubles the number of buckets and rehashes all existing entries into the
     * new table.
     *
     * <p>Called automatically by {@link #put} when the load factor is
     * exceeded. May also be called explicitly.
     *
     * <p>Time complexity: O(n).
     */
    @SuppressWarnings("unchecked")
    public void resize() {
        Entry<K, V>[] oldBuckets = buckets;
        buckets = new Entry[oldBuckets.length * 2];
        size = 0; // put() will re-increment
        for (Entry<K, V> head : oldBuckets) {
            Entry<K, V> curr = head;
            while (curr != null) {
                Entry<K, V> next = curr.next;
                put(curr.key, curr.value); // rehash into new buckets
                curr = next;
            }
        }
    }

    // -----------------------------------------------------------------------
    // toString — shows all buckets
    // -----------------------------------------------------------------------

    /**
     * Returns a visual representation of the hash map showing every bucket
     * with its chain of entries.
     *
     * <p>Example output (4-bucket map with two entries):
     * <pre>
     * HashMap (size=2, buckets=4, load=0.50):
     *   [0]: empty
     *   [1]: "b"=20 -> null
     *   [2]: empty
     *   [3]: "a"=10 -> null
     * </pre>
     *
     * @return string representation
     */
    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append(String.format("HashMap (size=%d, buckets=%d, load=%.2f):%n",
                size, buckets.length, (double) size / buckets.length));
        for (int i = 0; i < buckets.length; i++) {
            sb.append(String.format("  [%d]: ", i));
            if (buckets[i] == null) {
                sb.append("empty");
            } else {
                Entry<K, V> curr = buckets[i];
                while (curr != null) {
                    sb.append(curr);
                    if (curr.next != null) sb.append(" -> ");
                    curr = curr.next;
                }
            }
            sb.append("\n");
        }
        return sb.toString();
    }

    // -----------------------------------------------------------------------
    // Private helpers
    // -----------------------------------------------------------------------

    /**
     * Computes the bucket index for the given key using its {@code hashCode}.
     * Uses {@code & 0x7FFFFFFF} to strip the sign bit before taking the modulus.
     */
    private int bucketIndex(K key) {
        return (key.hashCode() & 0x7FFFFFFF) % buckets.length;
    }

    /**
     * Walks the chain at the appropriate bucket and returns the entry whose
     * key equals {@code key}, or {@code null} if not found.
     */
    private Entry<K, V> findEntry(K key) {
        int idx = bucketIndex(key);
        Entry<K, V> curr = buckets[idx];
        while (curr != null) {
            if (curr.key.equals(key)) return curr;
            curr = curr.next;
        }
        return null;
    }

    /** Validates that the key is non-null. */
    private void checkKey(K key) {
        if (key == null) {
            throw new IllegalArgumentException("Null keys are not supported");
        }
    }

    // -----------------------------------------------------------------------
    // Demo main
    // -----------------------------------------------------------------------

    /**
     * Demonstrates all HashMap operations.
     *
     * @param args unused
     */
    public static void main(String[] args) {
        System.out.println("=== HashMap Demo ===\n");

        // Small capacity to show chaining and resize clearly
        HashMap<String, Integer> map = new HashMap<>(4);

        System.out.println("-- put --");
        String[] keys = {"apple", "banana", "cherry", "date", "elderberry"};
        for (int i = 0; i < keys.length; i++) {
            Integer old = map.put(keys[i], (i + 1) * 10);
            System.out.println("put(\"" + keys[i] + "\", " + (i + 1) * 10 + ")  prev=" + old);
        }
        System.out.println("\n" + map);

        System.out.println("-- update existing key --");
        Integer old = map.put("banana", 999);
        System.out.println("put(\"banana\", 999)  prev=" + old);
        System.out.println("get(\"banana\") = " + map.get("banana") + "\n");

        System.out.println("-- get --");
        System.out.println("get(\"apple\")       = " + map.get("apple"));
        System.out.println("get(\"cherry\")      = " + map.get("cherry"));
        System.out.println("get(\"notAKey\")     = " + map.get("notAKey"));

        System.out.println("\n-- containsKey --");
        System.out.println("containsKey(\"date\")   = " + map.containsKey("date"));
        System.out.println("containsKey(\"mango\")  = " + map.containsKey("mango"));

        System.out.println("\n-- remove --");
        System.out.println("remove(\"cherry\")  = " + map.remove("cherry"));
        System.out.println("remove(\"mango\")   = " + map.remove("mango")); // missing key
        System.out.println("size after removes = " + map.size());

        System.out.println("\n-- state after operations --");
        System.out.println(map);

        System.out.println("-- manual resize --");
        map.resize();
        System.out.println("After resize():\n" + map);
    }
}
