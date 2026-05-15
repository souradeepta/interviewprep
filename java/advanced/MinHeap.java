package advanced;

import java.util.Arrays;

/**
 * Min Heap backed by a resizable int array.
 *
 * <p>The heap property: {@code heap[parent(i)] <= heap[i]} for every index {@code i > 0}.
 * Index arithmetic (0-based):
 * <ul>
 *   <li>parent(i)      = (i - 1) / 2</li>
 *   <li>leftChild(i)   = 2 * i + 1</li>
 *   <li>rightChild(i)  = 2 * i + 2</li>
 * </ul>
 *
 * <p>Time complexities:
 * <ul>
 *   <li>insert       – O(log n) amortized</li>
 *   <li>extractMin   – O(log n)</li>
 *   <li>peek         – O(1)</li>
 *   <li>buildHeap    – O(n)  (Floyd's algorithm)</li>
 *   <li>heapSort     – O(n log n)</li>
 * </ul>
 *
 * <p>Space complexity: O(n).
 */
public class MinHeap {

    // -------------------------------------------------------------------------
    // Fields
    // -------------------------------------------------------------------------

    private int[] heap;
    private int size;
    private static final int DEFAULT_CAPACITY = 16;

    // -------------------------------------------------------------------------
    // Constructors
    // -------------------------------------------------------------------------

    /** Creates an empty MinHeap with default initial capacity. */
    public MinHeap() {
        heap = new int[DEFAULT_CAPACITY];
        size = 0;
    }

    /** Creates a MinHeap pre-populated from an array using Floyd's buildHeap (O(n)). */
    public MinHeap(int[] arr) {
        buildHeap(arr);
    }

    // -------------------------------------------------------------------------
    // Core helpers
    // -------------------------------------------------------------------------

    private int parent(int i)     { return (i - 1) / 2; }
    private int leftChild(int i)  { return 2 * i + 1; }
    private int rightChild(int i) { return 2 * i + 2; }

    private void swap(int i, int j) {
        int tmp = heap[i];
        heap[i] = heap[j];
        heap[j] = tmp;
    }

    private void grow() {
        heap = Arrays.copyOf(heap, heap.length * 2);
    }

    // -------------------------------------------------------------------------
    // Insert
    // -------------------------------------------------------------------------

    /**
     * Inserts {@code val} into the heap.
     *
     * <p>Time: O(log n) | Space: O(1).
     *
     * @param val the value to insert
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public void insert(int val) {
        if (size == heap.length) grow();
        heap[size] = val;
        heapifyUp(size);
        size++;
    }

    // -------------------------------------------------------------------------
    // heapifyUp
    // -------------------------------------------------------------------------

    /**
     * Restores the heap property upward from index {@code i}.
     * Called after insertion at the last position.
     *
     * <p>Time: O(log n) | Space: O(1).
     *
     * @param i the starting index
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public void heapifyUp(int i) {
        while (i > 0 && heap[parent(i)] > heap[i]) {
            swap(i, parent(i));
            i = parent(i);
        }
    }

    // -------------------------------------------------------------------------
    // extractMin
    // -------------------------------------------------------------------------

    /**
     * Removes and returns the minimum element (the root).
     *
     * <p>Time: O(log n) | Space: O(1).
     *
     * @return the minimum value
     * @throws IllegalStateException if the heap is empty
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public int extractMin() {
        if (size == 0) throw new IllegalStateException("Heap is empty");
        int min = heap[0];
        heap[0] = heap[size - 1];
        size--;
        if (size > 0) heapifyDown(0);
        return min;
    }

    // -------------------------------------------------------------------------
    // heapifyDown
    // -------------------------------------------------------------------------

    /**
     * Restores the heap property downward from index {@code i}.
     * Called after replacing the root with the last element during extraction.
     *
     * <p>Time: O(log n) | Space: O(1).
     *
     * @param i the starting index
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public void heapifyDown(int i) {
        int smallest = i;
        int l = leftChild(i);
        int r = rightChild(i);

        if (l < size && heap[l] < heap[smallest]) smallest = l;
        if (r < size && heap[r] < heap[smallest]) smallest = r;

        if (smallest != i) {
            swap(i, smallest);
            heapifyDown(smallest);
        }
    }

    // -------------------------------------------------------------------------
    // peek
    // -------------------------------------------------------------------------

    /**
     * Returns (but does not remove) the minimum element.
     *
     * <p>Time: O(1) | Space: O(1).
     *
     * @return the minimum value
     * @throws IllegalStateException if the heap is empty
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public int peek() {
        if (size == 0) throw new IllegalStateException("Heap is empty");
        return heap[0];
    }

    // -------------------------------------------------------------------------
    // buildHeap (Floyd's O(n) algorithm)
    // -------------------------------------------------------------------------

    /**
     * Replaces the heap contents with those of {@code arr}, building the heap
     * in-place using Floyd's algorithm.
     *
     * <p>Floyd's insight: leaves already satisfy the heap property, so we only
     * need to heapify-down from the last internal node upward.
     *
     * <p>Time: O(n) | Space: O(1) auxiliary (plus the array copy).
     *
     * @param arr the source array (not modified)
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public void buildHeap(int[] arr) {
        heap = Arrays.copyOf(arr, Math.max(arr.length, DEFAULT_CAPACITY));
        size = arr.length;
        // Start from the last internal node
        for (int i = size / 2 - 1; i >= 0; i--) {
            heapifyDown(i);
        }
    }

    // -------------------------------------------------------------------------
    // heapSort (returns a sorted copy; does NOT modify this heap)
    // -------------------------------------------------------------------------

    /**
     * Returns a new array containing all current elements in ascending order.
     *
     * <p>Implementation: copies the internal array into a temporary max-heap
     * (by negating values), then extracts min repeatedly.  Alternatively, a
     * standard in-place heap-sort on a max-heap is shown in the comment below.
     *
     * <p>Time: O(n log n) | Space: O(n).
     *
     * @return sorted array (ascending)
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public int[] heapSort() {
        // Work on a snapshot so this heap is unchanged
        int[] snapshot = Arrays.copyOf(heap, size);
        int n = size;

        // Build a max-heap from the snapshot
        for (int i = n / 2 - 1; i >= 0; i--) {
            siftDownMax(snapshot, i, n);
        }
        // Repeatedly extract max to end of array
        for (int end = n - 1; end > 0; end--) {
            int tmp = snapshot[0];
            snapshot[0] = snapshot[end];
            snapshot[end] = tmp;
            siftDownMax(snapshot, 0, end);
        }
        return snapshot;
    }

    /** Max-heap sift-down on a raw array slice [0, limit). */
    private void siftDownMax(int[] a, int i, int limit) {
        int largest = i;
        int l = 2 * i + 1, r = 2 * i + 2;
        if (l < limit && a[l] > a[largest]) largest = l;
        if (r < limit && a[r] > a[largest]) largest = r;
        if (largest != i) {
            int tmp = a[i]; a[i] = a[largest]; a[largest] = tmp;
            siftDownMax(a, largest, limit);
        }
    }

    // -------------------------------------------------------------------------
    // Accessors
    // -------------------------------------------------------------------------

    /** Returns the number of elements in the heap. */
    public int size() { return size; }

    /** Returns {@code true} if the heap contains no elements. */
    public boolean isEmpty() { return size == 0; }

    // -------------------------------------------------------------------------
    // toString
    // -------------------------------------------------------------------------

    /**
     * Returns a string showing both the underlying array and a tree-level view.
     *
     * <p>Time: O(n) | Space: O(n).
     *
     * @return multi-line heap representation
     */
    @Override
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public String toString() {
        if (size == 0) return "(empty heap)";
        StringBuilder sb = new StringBuilder();

        // Array view
        sb.append("Array : [");
        for (int i = 0; i < size; i++) {
            sb.append(heap[i]);
            if (i < size - 1) sb.append(", ");
        }
        sb.append("]\n");

        // Tree view – level order
        sb.append("Tree  :\n");
        int level = 0;
        int levelStart = 0;
        int levelSize = 1;
        while (levelStart < size) {
            sb.append("  L").append(level).append(": ");
            for (int i = levelStart; i < Math.min(levelStart + levelSize, size); i++) {
                sb.append(heap[i]);
                if (i < Math.min(levelStart + levelSize, size) - 1) sb.append("  ");
            }
            sb.append("\n");
            levelStart += levelSize;
            levelSize  *= 2;
            level++;
        }
        return sb.toString();
    }

    // -------------------------------------------------------------------------
    // Main – demo
    // -------------------------------------------------------------------------

    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public static void main(String[] args) {
        System.out.println("=== MinHeap Demo ===\n");

        MinHeap mh = new MinHeap();

        // Insert
        int[] vals = {15, 10, 30, 5, 7, 2, 20, 1};
        System.out.println("Inserting: " + Arrays.toString(vals));
        for (int v : vals) mh.insert(v);
        System.out.println(mh);

        // Peek
        System.out.println("Peek (min): " + mh.peek());

        // extractMin x3
        System.out.println("\nExtractMin: " + mh.extractMin());
        System.out.println("ExtractMin: " + mh.extractMin());
        System.out.println("ExtractMin: " + mh.extractMin());
        System.out.println("\nHeap after 3 extractions:");
        System.out.println(mh);

        // buildHeap
        int[] arr = {9, 4, 7, 1, -2, 6, 3};
        MinHeap mh2 = new MinHeap(arr);
        System.out.println("buildHeap(" + Arrays.toString(arr) + "):");
        System.out.println(mh2);

        // heapSort
        int[] sorted = mh2.heapSort();
        System.out.println("heapSort result: " + Arrays.toString(sorted));
        System.out.println("Original heap intact:");
        System.out.println(mh2);
    }
}
