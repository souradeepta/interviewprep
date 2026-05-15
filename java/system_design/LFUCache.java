import java.util.*;

/**
 * LFUCache - [Brief description]
 *
 * <p>OVERVIEW:
 * [Detailed explanation of what this class does]
 *
 * <p>COMPLEXITY:
 * <ul>
 *   <li>Time: [See method documentation]</li>
 *   <li>Space: O(n) where n is [the element count]</li>
 * </ul>
 *
 * <p>USAGE:
 * [How to use this class, with example]
 *
 * @author Interview Preparation
 * @since 1.0
 */

public class LFUCache {
    private int capacity, minFreq;
    private Map<Integer, Integer> cache;
    private Map<Integer, Integer> freq;
    private Map<Integer, LinkedHashSet<Integer>> freqList;

    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public LFUCache(int capacity) {
        this.capacity = capacity;
        this.cache = new HashMap<>();
        this.freq = new HashMap<>();
        this.freqList = new HashMap<>();
        this.minFreq = 0;
    }

    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public int get(int key) {
        if (!cache.containsKey(key)) return -1;
        incrementFreq(key);
        return cache.get(key);
    }

    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public void put(int key, int value) {
        if (capacity <= 0) return;
        if (cache.containsKey(key)) {
            cache.put(key, value);
            incrementFreq(key);
            return;
        }
        if (cache.size() >= capacity) {
            evictLFU();
        }
        cache.put(key, value);
        freq.put(key, 1);
        freqList.computeIfAbsent(1, k -> new LinkedHashSet<>()).add(key);
        minFreq = 1;
    }

    private void incrementFreq(int key) {
        int f = freq.get(key);
        freq.put(key, f + 1);
        freqList.get(f).remove(key);
        if (freqList.get(f).isEmpty() && f == minFreq) {
            minFreq = f + 1;
        }
        freqList.computeIfAbsent(f + 1, k -> new LinkedHashSet<>()).add(key);
    }

    private void evictLFU() {
        int evict = freqList.get(minFreq).iterator().next();
        freqList.get(minFreq).remove(evict);
        cache.remove(evict);
        freq.remove(evict);
    }

    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public static void main(String[] args) {
        LFUCache cache = new LFUCache(2);
        cache.put(1, 1);
        cache.put(2, 2);
        System.out.println("get(1): " + cache.get(1));
        cache.put(3, 3);
        System.out.println("get(2): " + cache.get(2));
    }
}
