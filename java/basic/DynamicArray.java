package basic;

/**
 * A generic resizable array (similar to ArrayList).
 *
 * <p>Internally backed by a plain Object array. When capacity is exhausted the
 * backing array is doubled, giving amortised O(1) appends.
 *
 * <p>Time complexities:
 * <ul>
 *   <li>add(T)              – O(1) amortised</li>
 *   <li>add(int, T)         – O(n)</li>
 *   <li>remove(int)         – O(n)</li>
 *   <li>get(int)            – O(1)</li>
 *   <li>set(int, T)         – O(1)</li>
 *   <li>resize()            – O(n)</li>
 * </ul>
 *
 * @param <T> the element type
 */
@SuppressWarnings("unchecked")
public class DynamicArray<T> {

    // -----------------------------------------------------------------------
    // Fields
    // -----------------------------------------------------------------------

    /** Default initial capacity. */
    private static final int DEFAULT_CAPACITY = 4;

    /** The backing array. Elements are stored at indices [0, size). */
    private Object[] data;

    /** Number of elements currently stored. */
    private int size;

    // -----------------------------------------------------------------------
    // Constructors
    // -----------------------------------------------------------------------

    /**
     * Creates a DynamicArray with the default initial capacity (4).
     */
    public DynamicArray() {
        data = new Object[DEFAULT_CAPACITY];
        size = 0;
    }

    /**
     * Creates a DynamicArray with the specified initial capacity.
     *
     * @param initialCapacity must be &gt; 0
     * @throws IllegalArgumentException if initialCapacity &lt;= 0
     */
    public DynamicArray(int initialCapacity) {
        if (initialCapacity <= 0) {
            throw new IllegalArgumentException("Capacity must be positive, got: " + initialCapacity);
        }
        data = new Object[initialCapacity];
        size = 0;
    }

    // -----------------------------------------------------------------------
    // Core operations
    // -----------------------------------------------------------------------

    /**
     * Appends {@code element} to the end of the array.
     *
     * <p>Time complexity: O(1) amortised.
     *
     * @param element the value to append
     */
    public void add(T element) {
        ensureCapacity();
        data[size++] = element;
    }

    /**
     * Inserts {@code element} at position {@code index}, shifting all
     * subsequent elements one position to the right.
     *
     * <p>Time complexity: O(n).
     *
     * @param index   position in [0, size]
     * @param element the value to insert
     * @throws IndexOutOfBoundsException if index is out of [0, size]
     */
    public void add(int index, T element) {
        checkIndexForAdd(index);
        ensureCapacity();
        // Shift elements right
        System.arraycopy(data, index, data, index + 1, size - index);
        data[index] = element;
        size++;
    }

    /**
     * Removes and returns the element at position {@code index}, shifting
     * subsequent elements one position to the left.
     *
     * <p>Time complexity: O(n).
     *
     * @param index position in [0, size)
     * @return the removed element
     * @throws IndexOutOfBoundsException if index is out of [0, size)
     */
    public T remove(int index) {
        checkIndex(index);
        T removed = (T) data[index];
        int numMoved = size - index - 1;
        if (numMoved > 0) {
            System.arraycopy(data, index + 1, data, index, numMoved);
        }
        data[--size] = null; // allow GC
        return removed;
    }

    /**
     * Returns the element at position {@code index}.
     *
     * <p>Time complexity: O(1).
     *
     * @param index position in [0, size)
     * @return the element
     * @throws IndexOutOfBoundsException if index is out of [0, size)
     */
    public T get(int index) {
        checkIndex(index);
        return (T) data[index];
    }

    /**
     * Replaces the element at position {@code index} with {@code element}.
     *
     * <p>Time complexity: O(1).
     *
     * @param index   position in [0, size)
     * @param element new value
     * @return the old element that was replaced
     * @throws IndexOutOfBoundsException if index is out of [0, size)
     */
    public T set(int index, T element) {
        checkIndex(index);
        T old = (T) data[index];
        data[index] = element;
        return old;
    }

    /**
     * Returns the number of elements stored.
     *
     * <p>Time complexity: O(1).
     *
     * @return current size
     */
    public int size() {
        return size;
    }

    /**
     * Returns {@code true} if this array contains no elements.
     *
     * @return {@code true} if empty
     */
    public boolean isEmpty() {
        return size == 0;
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
    // Internal resize
    // -----------------------------------------------------------------------

    /**
     * Doubles the capacity of the backing array, copying all existing elements.
     *
     * <p>Called automatically by {@link #add} when the array is full.
     * May also be called explicitly.
     *
     * <p>Time complexity: O(n).
     */
    public void resize() {
        int newCapacity = data.length * 2;
        Object[] newData = new Object[newCapacity];
        System.arraycopy(data, 0, newData, 0, size);
        data = newData;
    }

    // -----------------------------------------------------------------------
    // toString
    // -----------------------------------------------------------------------

    /**
     * Returns a visual representation of the array showing its contents,
     * current size, and current capacity.
     *
     * <p>Example: {@code [10, 20, 30]  (size=3, capacity=4)}
     *
     * @return string representation
     */
    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder("[");
        for (int i = 0; i < size; i++) {
            sb.append(data[i]);
            if (i < size - 1) sb.append(", ");
        }
        sb.append("]  (size=").append(size).append(", capacity=").append(data.length).append(")");
        return sb.toString();
    }

    // -----------------------------------------------------------------------
    // Private helpers
    // -----------------------------------------------------------------------

    /** Ensures there is room for at least one more element. */
    private void ensureCapacity() {
        if (size == data.length) {
            resize();
        }
    }

    /** Validates an index for read / update operations. */
    private void checkIndex(int index) {
        if (index < 0 || index >= size) {
            throw new IndexOutOfBoundsException("Index: " + index + ", Size: " + size);
        }
    }

    /** Validates an index for insert operations (allows index == size). */
    private void checkIndexForAdd(int index) {
        if (index < 0 || index > size) {
            throw new IndexOutOfBoundsException("Index: " + index + ", Size: " + size);
        }
    }

    // -----------------------------------------------------------------------
    // Demo main
    // -----------------------------------------------------------------------

    /**
     * Demonstrates all DynamicArray operations.
     *
     * @param args unused
     */
    public static void main(String[] args) {
        System.out.println("=== DynamicArray Demo ===\n");

        DynamicArray<Integer> arr = new DynamicArray<>();

        System.out.println("-- add(T) --");
        for (int i = 10; i <= 50; i += 10) {
            arr.add(i);
            System.out.println("add(" + i + ") -> " + arr);
        }

        System.out.println("\n-- add(index, T) --");
        arr.add(2, 99);
        System.out.println("add(2, 99) -> " + arr);

        System.out.println("\n-- get(index) --");
        System.out.println("get(0) = " + arr.get(0));
        System.out.println("get(2) = " + arr.get(2));

        System.out.println("\n-- set(index, T) --");
        int old = arr.set(2, 77);
        System.out.println("set(2, 77), old=" + old + " -> " + arr);

        System.out.println("\n-- remove(index) --");
        int removed = arr.remove(0);
        System.out.println("remove(0)=" + removed + " -> " + arr);
        removed = arr.remove(arr.size() - 1);
        System.out.println("remove(last)=" + removed + " -> " + arr);

        System.out.println("\n-- resize() (manual) --");
        System.out.println("Before: " + arr);
        arr.resize();
        System.out.println("After : " + arr);

        System.out.println("\n-- size / isEmpty --");
        System.out.println("size=" + arr.size() + ", isEmpty=" + arr.isEmpty());

        System.out.println("\n-- Boundary: add until several resizes --");
        DynamicArray<String> strs = new DynamicArray<>(2);
        String[] words = {"alpha", "beta", "gamma", "delta", "epsilon"};
        for (String w : words) {
            strs.add(w);
            System.out.println("add(\"" + w + "\") -> " + strs);
        }
    }
}
