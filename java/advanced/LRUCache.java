package advanced;

import java.util.LinkedHashMap;
import java.util.Map;

/**
 * LRU (Least Recently Used) Cache — two implementations in one file:
 *
 * <ol>
 *   <li>{@link SimpleLRUCache} — leverages {@link LinkedHashMap} in access-order mode.
 *       One-liner {@code removeEldestEntry} handles eviction.</li>
 *   <li>{@link LRUCacheManual} — interview-style implementation using a doubly-linked
 *       list (DLL) + {@link java.util.HashMap}.  O(1) guaranteed for both get and put.</li>
 * </ol>
 *
 * <p>Time complexities (both versions):
 * <ul>
 *   <li>get – O(1)</li>
 *   <li>put – O(1)</li>
 * </ul>
 *
 * <p>Space complexity: O(capacity).
 */
public class LRUCache {

    // =========================================================================
    // 1. Simple version – LinkedHashMap
    // =========================================================================

    /**
     * Simple LRU Cache backed by a {@link LinkedHashMap} in access-order mode.
     *
     * <p>{@code LinkedHashMap(capacity, loadFactor, accessOrder=true)} keeps entries
     * in most-recently-accessed order.  Overriding {@link LinkedHashMap#removeEldestEntry}
     * enforces the capacity bound.
     */
    public static class SimpleLRUCache {

        private final int capacity;
        private final LinkedHashMap<Integer, Integer> map;

        /**
         * Creates a SimpleLRUCache with the given capacity.
         *
         * @param capacity maximum number of entries (>= 1)
         */
        public SimpleLRUCache(int capacity) {
            if (capacity < 1) throw new IllegalArgumentException("Capacity must be >= 1");
            this.capacity = capacity;
            // accessOrder=true: iterating visits LRU->MRU
            this.map = new LinkedHashMap<Integer, Integer>(capacity, 0.75f, true) {
                @Override
                protected boolean removeEldestEntry(Map.Entry<Integer, Integer> eldest) {
                    return size() > capacity;
                }
            };
        }

        /**
         * Returns the value for {@code key}, or -1 if not present.
         * Marks the entry as most recently used.
         *
         * <p>Time: O(1) | Space: O(1).
         *
         * @param key the cache key
         * @return cached value or -1
         */
        public int get(int key) {
            return map.getOrDefault(key, -1);
        }

        /**
         * Inserts or updates the entry for {@code key} with {@code value}.
         * Evicts the least recently used entry when over capacity.
         *
         * <p>Time: O(1) | Space: O(1).
         *
         * @param key   cache key
         * @param value cache value
         */
        public void put(int key, int value) {
            map.put(key, value);
        }

        /** Returns the current number of entries. */
        public int size() { return map.size(); }

        /** Returns the cache capacity. */
        public int capacity() { return capacity; }

        @Override
        public String toString() {
            return "SimpleLRUCache" + map.toString() + " (LRU->MRU order)";
        }
    }

    // =========================================================================
    // 2. Manual version – DoublyLinkedList + HashMap (interview style)
    // =========================================================================

    /**
     * Manual LRU Cache using an explicit doubly-linked list and a HashMap.
     *
     * <p>Design:
     * <ul>
     *   <li>The DLL is kept in MRU order: {@code head.next} = most recently used,
     *       {@code tail.prev} = least recently used.</li>
     *   <li>Sentinel {@code head} and {@code tail} nodes simplify boundary conditions.</li>
     *   <li>The HashMap maps keys to their DLL nodes for O(1) access.</li>
     * </ul>
     *
     * <p>On {@code get}: move the accessed node to the front (MRU end).<br>
     * On {@code put}: if key exists, update value and move to front; otherwise
     * insert at front.  If over capacity, evict from the tail (LRU end).
     */
    public static class LRUCacheManual {

        // ----- Inner doubly-linked list node -----

        private static class DLLNode {
            int key, value;
            DLLNode prev, next;

            DLLNode(int key, int value) {
                this.key   = key;
                this.value = value;
            }
        }

        // ----- Fields -----

        private final int capacity;
        private final Map<Integer, DLLNode> map;
        private final DLLNode head; // sentinel MRU end
        private final DLLNode tail; // sentinel LRU end
        private int size;

        /**
         * Creates an LRUCacheManual with the given capacity.
         *
         * @param capacity maximum number of key-value pairs (>= 1)
         */
        public LRUCacheManual(int capacity) {
            if (capacity < 1) throw new IllegalArgumentException("Capacity must be >= 1");
            this.capacity = capacity;
            map  = new java.util.HashMap<>();
            head = new DLLNode(-1, -1); // dummy head (MRU side)
            tail = new DLLNode(-1, -1); // dummy tail (LRU side)
            head.next = tail;
            tail.prev = head;
        }

        // ----- Public API -----

        /**
         * Returns the value for {@code key}, or -1 if not present.
         * Marks the entry as most recently used.
         *
         * <p>Time: O(1) | Space: O(1).
         *
         * @param key the cache key
         * @return cached value or -1
         */
        public int get(int key) {
            DLLNode node = map.get(key);
            if (node == null) return -1;
            moveToFront(node);
            return node.value;
        }

        /**
         * Inserts or updates the entry for {@code key}.
         * Evicts the LRU entry if the cache would exceed capacity.
         *
         * <p>Time: O(1) | Space: O(1).
         *
         * @param key   cache key
         * @param value cache value
         */
        public void put(int key, int value) {
            DLLNode existing = map.get(key);
            if (existing != null) {
                existing.value = value;
                moveToFront(existing);
                return;
            }
            if (size == capacity) {
                // Evict LRU (node just before tail)
                DLLNode lru = tail.prev;
                removeNode(lru);
                map.remove(lru.key);
                size--;
            }
            DLLNode newNode = new DLLNode(key, value);
            addToFront(newNode);
            map.put(key, newNode);
            size++;
        }

        /** Returns the current number of entries. */
        public int size() { return size; }

        /** Returns the cache capacity. */
        public int capacity() { return capacity; }

        // ----- DLL helpers -----

        /** Detaches {@code node} from its current position. */
        private void removeNode(DLLNode node) {
            node.prev.next = node.next;
            node.next.prev = node.prev;
        }

        /** Inserts {@code node} right after {@code head} (MRU position). */
        private void addToFront(DLLNode node) {
            node.next      = head.next;
            node.prev      = head;
            head.next.prev = node;
            head.next      = node;
        }

        /** Moves an existing {@code node} to the MRU position. */
        private void moveToFront(DLLNode node) {
            removeNode(node);
            addToFront(node);
        }

        @Override
        public String toString() {
            StringBuilder sb = new StringBuilder("LRUCacheManual [MRU->LRU]: ");
            DLLNode cur = head.next;
            while (cur != tail) {
                sb.append("(").append(cur.key).append("=").append(cur.value).append(")");
                if (cur.next != tail) sb.append(" -> ");
                cur = cur.next;
            }
            sb.append("  | size=").append(size).append("/").append(capacity);
            return sb.toString();
        }
    }

    // =========================================================================
    // Main – demo for both implementations
    // =========================================================================

    public static void main(String[] args) {
        System.out.println("=== LRU Cache Demo ===\n");

        // ------------------------------------------------------------------
        // Simple version
        // ------------------------------------------------------------------
        System.out.println("--- SimpleLRUCache (capacity=3) ---");
        SimpleLRUCache simple = new SimpleLRUCache(3);

        simple.put(1, 10);
        simple.put(2, 20);
        simple.put(3, 30);
        System.out.println("After put(1,10) put(2,20) put(3,30): " + simple);

        System.out.println("get(1) = " + simple.get(1) + "  (accesses key 1 -> moves to MRU)");
        System.out.println("After get(1): " + simple);

        simple.put(4, 40); // evicts key 2 (LRU after get(1) made 1 MRU)
        System.out.println("After put(4,40) (evicts LRU): " + simple);
        System.out.println("get(2) = " + simple.get(2) + "  (expected -1, was evicted)");

        simple.put(5, 50);
        System.out.println("After put(5,50): " + simple);

        // ------------------------------------------------------------------
        // Manual version
        // ------------------------------------------------------------------
        System.out.println("\n--- LRUCacheManual (capacity=3) ---");
        LRUCacheManual lru = new LRUCacheManual(3);

        lru.put(1, 10);
        lru.put(2, 20);
        lru.put(3, 30);
        System.out.println("After put(1,10) put(2,20) put(3,30): " + lru);

        System.out.println("get(1) = " + lru.get(1) + "  (moves 1 to MRU)");
        System.out.println("After get(1): " + lru);

        lru.put(4, 40); // evicts key 2 (LRU)
        System.out.println("After put(4,40) (evicts 2): " + lru);
        System.out.println("get(2) = " + lru.get(2) + "  (expected -1)");
        System.out.println("get(3) = " + lru.get(3) + "  (expected 30)");
        System.out.println("After get(3): " + lru);

        lru.put(5, 50); // evicts LRU (currently key 1 or 4)
        System.out.println("After put(5,50): " + lru);

        lru.put(3, 300); // update existing – moves to front
        System.out.println("After put(3,300) [update]: " + lru);
        System.out.println("get(3) = " + lru.get(3) + "  (expected 300)");

        // ------------------------------------------------------------------
        // Classic LeetCode 146 sequence
        // ------------------------------------------------------------------
        System.out.println("\n--- LeetCode 146 sequence on LRUCacheManual ---");
        LRUCacheManual lc = new LRUCacheManual(2);
        lc.put(1, 1); System.out.println("put(1,1): " + lc);
        lc.put(2, 2); System.out.println("put(2,2): " + lc);
        System.out.println("get(1)=" + lc.get(1));      // 1
        lc.put(3, 3); System.out.println("put(3,3) evicts 2: " + lc);
        System.out.println("get(2)=" + lc.get(2));      // -1
        lc.put(4, 4); System.out.println("put(4,4) evicts 1: " + lc);
        System.out.println("get(1)=" + lc.get(1));      // -1
        System.out.println("get(3)=" + lc.get(3));      // 3
        System.out.println("get(4)=" + lc.get(4));      // 4
    }
}
