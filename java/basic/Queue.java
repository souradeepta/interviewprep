package basic;

/**
 * A generic queue backed by a circular array (ring buffer).
 *
 * <p>Using a circular buffer avoids the O(n) shift on dequeue that a naive
 * array-backed queue would require. Both enqueue and dequeue are O(1)
 * amortised. When the array is full it is doubled and all elements are
 * re-laid out starting from index 0.
 *
 * <p>Time complexities:
 * <ul>
 *   <li>enqueue(T)  – O(1) amortised</li>
 *   <li>dequeue()   – O(1)</li>
 *   <li>peek()      – O(1)</li>
 *   <li>isEmpty()   – O(1)</li>
 *   <li>isFull()    – O(1)</li>
 *   <li>size()      – O(1)</li>
 * </ul>
 *
 * @param <T> the element type
 */
@SuppressWarnings("unchecked")
public class Queue<T> {

    // -----------------------------------------------------------------------
    // Fields
    // -----------------------------------------------------------------------

    /** Default initial capacity. */
    private static final int DEFAULT_CAPACITY = 8;

    /** The circular backing array. */
    private Object[] data;

    /**
     * Index of the front element (the next element to be dequeued).
     * Advances by 1 (mod capacity) on each dequeue.
     */
    private int front;

    /**
     * Index where the next enqueued element will be written.
     * Advances by 1 (mod capacity) on each enqueue.
     */
    private int back;

    /** Number of elements currently in the queue. */
    private int size;

    // -----------------------------------------------------------------------
    // Constructors
    // -----------------------------------------------------------------------

    /**
     * Creates an empty queue with the default initial capacity (8).
     */
    public Queue() {
        this(DEFAULT_CAPACITY);
    }

    /**
     * Creates an empty queue with the specified initial capacity.
     *
     * @param initialCapacity must be &gt; 0
     * @throws IllegalArgumentException if initialCapacity &lt;= 0
     */
    public Queue(int initialCapacity) {
        if (initialCapacity <= 0) {
            throw new IllegalArgumentException("Capacity must be positive, got: " + initialCapacity);
        }
        data = new Object[initialCapacity];
        front = 0;
        back = 0;
        size = 0;
    }

    // -----------------------------------------------------------------------
    // Core operations
    // -----------------------------------------------------------------------

    /**
     * Adds {@code element} to the back of the queue.
     *
     * <p>The backing array is doubled when it is already full.
     *
     * <p>Time complexity: O(1) amortised.
     *
     * @param element the value to enqueue
     */
    public void enqueue(T element) {
        if (isFull()) grow();
        data[back] = element;
        back = (back + 1) % data.length;
        size++;
    }

    /**
     * Removes and returns the front element.
     *
     * <p>Time complexity: O(1).
     *
     * @return the front element
     * @throws java.util.NoSuchElementException if the queue is empty
     */
    public T dequeue() {
        checkNotEmpty();
        T val = (T) data[front];
        data[front] = null; // allow GC
        front = (front + 1) % data.length;
        size--;
        return val;
    }

    /**
     * Returns the front element without removing it.
     *
     * <p>Time complexity: O(1).
     *
     * @return the front element
     * @throws java.util.NoSuchElementException if the queue is empty
     */
    public T peek() {
        checkNotEmpty();
        return (T) data[front];
    }

    /**
     * Returns {@code true} if the queue has no elements.
     *
     * <p>Time complexity: O(1).
     *
     * @return {@code true} if empty
     */
    public boolean isEmpty() {
        return size == 0;
    }

    /**
     * Returns {@code true} if the backing array is at full capacity.
     *
     * <p>Note: the queue will grow automatically on the next enqueue, so this
     * condition does not prevent enqueuing.
     *
     * <p>Time complexity: O(1).
     *
     * @return {@code true} if full
     */
    public boolean isFull() {
        return size == data.length;
    }

    /**
     * Returns the number of elements currently in the queue.
     *
     * <p>Time complexity: O(1).
     *
     * @return current size
     */
    public int size() {
        return size;
    }

    /**
     * Returns the current capacity of the backing array.
     *
     * @return backing-array length
     */
    public int capacity() {
        return data.length;
    }

    // -----------------------------------------------------------------------
    // toString
    // -----------------------------------------------------------------------

    /**
     * Returns a string showing queue contents in FIFO order (front to back),
     * the current size, and the current capacity.
     *
     * <p>Example: {@code front [1, 2, 3] back  (size=3, capacity=8)}
     *
     * @return string representation
     */
    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder("front [");
        for (int i = 0; i < size; i++) {
            sb.append(data[(front + i) % data.length]);
            if (i < size - 1) sb.append(", ");
        }
        sb.append("] back  (size=").append(size).append(", capacity=").append(data.length).append(")");
        return sb.toString();
    }

    // -----------------------------------------------------------------------
    // Private helpers
    // -----------------------------------------------------------------------

    /**
     * Doubles the capacity of the backing array and re-lays out all elements
     * starting from index 0, so the circular invariant is restored.
     *
     * <p>Time complexity: O(n).
     */
    private void grow() {
        Object[] newData = new Object[data.length * 2];
        for (int i = 0; i < size; i++) {
            newData[i] = data[(front + i) % data.length];
        }
        data = newData;
        front = 0;
        back = size;
    }

    /** Throws if the queue is empty. */
    private void checkNotEmpty() {
        if (isEmpty()) {
            throw new java.util.NoSuchElementException("Queue is empty");
        }
    }

    // -----------------------------------------------------------------------
    // Demo main
    // -----------------------------------------------------------------------

    /**
     * Demonstrates all Queue operations.
     *
     * @param args unused
     */
    public static void main(String[] args) {
        System.out.println("=== Queue Demo ===\n");

        // Use small initial capacity to show auto-grow
        Queue<Integer> queue = new Queue<>(3);

        System.out.println("-- enqueue --");
        for (int v : new int[]{10, 20, 30}) {
            queue.enqueue(v);
            System.out.println("enqueue(" + v + "): " + queue + "  isFull=" + queue.isFull());
        }

        System.out.println("\n-- peek --");
        System.out.println("peek() = " + queue.peek());

        System.out.println("\n-- enqueue triggers grow --");
        queue.enqueue(40);
        System.out.println("enqueue(40): " + queue);

        System.out.println("\n-- dequeue --");
        System.out.println("dequeue() = " + queue.dequeue() + " | " + queue);
        System.out.println("dequeue() = " + queue.dequeue() + " | " + queue);

        System.out.println("\n-- enqueue after dequeue (wrap-around test) --");
        queue.enqueue(50);
        queue.enqueue(60);
        System.out.println("after enqueue(50,60): " + queue);

        System.out.println("\n-- drain queue --");
        while (!queue.isEmpty()) {
            System.out.println("dequeue() = " + queue.dequeue() + " | " + queue);
        }

        System.out.println("\n-- isEmpty after drain --");
        System.out.println("isEmpty = " + queue.isEmpty());
    }
}
