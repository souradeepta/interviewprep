package basic;

/**
 * A generic double-ended queue (deque) backed by a circular array.
 *
 * <p>Supports O(1) amortised insertion and removal from both the front and the
 * back. Internally the same circular-buffer technique used by {@link Queue} is
 * applied, but the {@code front} pointer is moved <em>backwards</em> on
 * {@code pushFront} (and the {@code back} pointer forward on {@code pushBack}).
 *
 * <p>Time complexities:
 * <ul>
 *   <li>pushFront(T)   – O(1) amortised</li>
 *   <li>pushBack(T)    – O(1) amortised</li>
 *   <li>popFront()     – O(1)</li>
 *   <li>popBack()      – O(1)</li>
 *   <li>peekFront()    – O(1)</li>
 *   <li>peekBack()     – O(1)</li>
 *   <li>isEmpty()      – O(1)</li>
 *   <li>size()         – O(1)</li>
 * </ul>
 *
 * @param <T> the element type
 */
@SuppressWarnings("unchecked")
public class Deque<T> {

    // -----------------------------------------------------------------------
    // Fields
    // -----------------------------------------------------------------------

    /** Default initial capacity. */
    private static final int DEFAULT_CAPACITY = 8;

    /**
     * Circular backing array. Valid elements occupy
     * {@code front, (front+1)%cap, ..., (front+size-1)%cap}.
     */
    private Object[] data;

    /**
     * Index of the current front element.
     * Moves left (decrements) on {@code pushFront},
     * moves right (increments) on {@code popFront}.
     */
    private int front;

    /** Number of elements currently in the deque. */
    private int size;

    // -----------------------------------------------------------------------
    // Constructors
    // -----------------------------------------------------------------------

    /**
     * Creates an empty Deque with the default initial capacity (8).
     */
    public Deque() {
        this(DEFAULT_CAPACITY);
    }

    /**
     * Creates an empty Deque with the specified initial capacity.
     *
     * @param initialCapacity must be &gt; 0
     * @throws IllegalArgumentException if initialCapacity &lt;= 0
     */
    public Deque(int initialCapacity) {
        if (initialCapacity <= 0) {
            throw new IllegalArgumentException("Capacity must be positive, got: " + initialCapacity);
        }
        data = new Object[initialCapacity];
        front = 0;
        size = 0;
    }

    // -----------------------------------------------------------------------
    // Push (insert) operations
    // -----------------------------------------------------------------------

    /**
     * Inserts {@code element} at the front of the deque.
     *
     * <p>The front pointer wraps around to the end of the backing array when
     * needed. The array doubles if already full.
     *
     * <p>Time complexity: O(1) amortised.
     *
     * @param element the value to prepend
     */
    public void pushFront(T element) {
        if (size == data.length) grow();
        // Move front one step to the left (wrapping around)
        front = (front - 1 + data.length) % data.length;
        data[front] = element;
        size++;
    }

    /**
     * Appends {@code element} at the back of the deque.
     *
     * <p>Time complexity: O(1) amortised.
     *
     * @param element the value to append
     */
    public void pushBack(T element) {
        if (size == data.length) grow();
        int back = (front + size) % data.length;
        data[back] = element;
        size++;
    }

    // -----------------------------------------------------------------------
    // Pop (remove) operations
    // -----------------------------------------------------------------------

    /**
     * Removes and returns the front element.
     *
     * <p>Time complexity: O(1).
     *
     * @return the front element
     * @throws java.util.NoSuchElementException if the deque is empty
     */
    public T popFront() {
        checkNotEmpty();
        T val = (T) data[front];
        data[front] = null; // allow GC
        front = (front + 1) % data.length;
        size--;
        return val;
    }

    /**
     * Removes and returns the back element.
     *
     * <p>Time complexity: O(1).
     *
     * @return the back element
     * @throws java.util.NoSuchElementException if the deque is empty
     */
    public T popBack() {
        checkNotEmpty();
        int backIdx = (front + size - 1) % data.length;
        T val = (T) data[backIdx];
        data[backIdx] = null; // allow GC
        size--;
        return val;
    }

    // -----------------------------------------------------------------------
    // Peek operations
    // -----------------------------------------------------------------------

    /**
     * Returns the front element without removing it.
     *
     * <p>Time complexity: O(1).
     *
     * @return the front element
     * @throws java.util.NoSuchElementException if the deque is empty
     */
    public T peekFront() {
        checkNotEmpty();
        return (T) data[front];
    }

    /**
     * Returns the back element without removing it.
     *
     * <p>Time complexity: O(1).
     *
     * @return the back element
     * @throws java.util.NoSuchElementException if the deque is empty
     */
    public T peekBack() {
        checkNotEmpty();
        return (T) data[(front + size - 1) % data.length];
    }

    // -----------------------------------------------------------------------
    // Query operations
    // -----------------------------------------------------------------------

    /**
     * Returns {@code true} if the deque has no elements.
     *
     * <p>Time complexity: O(1).
     *
     * @return {@code true} if empty
     */
    public boolean isEmpty() {
        return size == 0;
    }

    /**
     * Returns the number of elements in the deque.
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
     * Returns a string showing deque contents from front to back, plus the
     * current size and capacity.
     *
     * <p>Example: {@code front [1, 2, 3, 4] back  (size=4, capacity=8)}
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
     * Doubles the capacity of the backing array, re-laying elements from
     * index 0 in front-to-back order.
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
    }

    /** Throws if the deque is empty. */
    private void checkNotEmpty() {
        if (isEmpty()) {
            throw new java.util.NoSuchElementException("Deque is empty");
        }
    }

    // -----------------------------------------------------------------------
    // Demo main
    // -----------------------------------------------------------------------

    /**
     * Demonstrates all Deque operations.
     *
     * @param args unused
     */
    public static void main(String[] args) {
        System.out.println("=== Deque Demo ===\n");

        Deque<Integer> dq = new Deque<>(4);

        System.out.println("-- pushBack --");
        for (int v : new int[]{10, 20, 30}) {
            dq.pushBack(v);
            System.out.println("pushBack(" + v + "): " + dq);
        }

        System.out.println("\n-- pushFront --");
        dq.pushFront(5);
        System.out.println("pushFront(5): " + dq);
        dq.pushFront(1);
        System.out.println("pushFront(1): " + dq);

        System.out.println("\n-- pushBack triggers grow --");
        dq.pushBack(40);
        System.out.println("pushBack(40): " + dq);

        System.out.println("\n-- peekFront / peekBack --");
        System.out.println("peekFront() = " + dq.peekFront());
        System.out.println("peekBack()  = " + dq.peekBack());

        System.out.println("\n-- popFront --");
        System.out.println("popFront() = " + dq.popFront() + " | " + dq);
        System.out.println("popFront() = " + dq.popFront() + " | " + dq);

        System.out.println("\n-- popBack --");
        System.out.println("popBack() = " + dq.popBack() + " | " + dq);
        System.out.println("popBack() = " + dq.popBack() + " | " + dq);

        System.out.println("\n-- drain remaining --");
        while (!dq.isEmpty()) {
            System.out.println("popFront() = " + dq.popFront() + " | " + dq);
        }

        System.out.println("\n-- isEmpty after drain --");
        System.out.println("isEmpty = " + dq.isEmpty());

        System.out.println("\n-- Use as stack (LIFO via pushBack/popBack) --");
        Deque<String> stack = new Deque<>();
        for (String s : new String[]{"a", "b", "c"}) {
            stack.pushBack(s);
        }
        System.out.println("stack: " + stack);
        System.out.println("popBack() = " + stack.popBack());
        System.out.println("popBack() = " + stack.popBack());

        System.out.println("\n-- Use as queue (FIFO via pushBack/popFront) --");
        Deque<String> queue = new Deque<>();
        for (String s : new String[]{"x", "y", "z"}) {
            queue.pushBack(s);
        }
        System.out.println("queue: " + queue);
        System.out.println("popFront() = " + queue.popFront());
        System.out.println("popFront() = " + queue.popFront());
    }
}
