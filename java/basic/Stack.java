package basic;

/**
 * A generic stack backed by a resizable array.
 *
 * <p>Elements are pushed and popped from the top (the logical "right" end of
 * the backing array), giving O(1) push and pop.
 *
 * <p>Time complexities:
 * <ul>
 *   <li>push(T)    – O(1) amortised (array doubles when full)</li>
 *   <li>pop()      – O(1)</li>
 *   <li>peek()     – O(1)</li>
 *   <li>isEmpty()  – O(1)</li>
 *   <li>size()     – O(1)</li>
 * </ul>
 *
 * <p>Also includes an inner class {@link StackWithMin} that tracks the running
 * minimum in O(1) time using a secondary min-stack.
 *
 * @param <T> the element type
 */
@SuppressWarnings("unchecked")
public class Stack<T> {

    // -----------------------------------------------------------------------
    // Fields
    // -----------------------------------------------------------------------

    /** Default initial capacity. */
    private static final int DEFAULT_CAPACITY = 8;

    /** Backing array. Top-of-stack is at index {@code size - 1}. */
    private Object[] data;

    /** Number of elements currently on the stack. */
    private int size;

    // -----------------------------------------------------------------------
    // Constructor
    // -----------------------------------------------------------------------

    /**
     * Creates an empty stack with the default initial capacity (8).
     */
    public Stack() {
        data = new Object[DEFAULT_CAPACITY];
        size = 0;
    }

    /**
     * Creates an empty stack with the specified initial capacity.
     *
     * @param initialCapacity must be &gt; 0
     * @throws IllegalArgumentException if initialCapacity &lt;= 0
     */
    public Stack(int initialCapacity) {
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
     * Pushes {@code element} onto the top of the stack.
     *
     * <p>Time complexity: O(1) amortised.
     *
     * @param element the value to push
     */
    public void push(T element) {
        ensureCapacity();
        data[size++] = element;
    }

    /**
     * Removes and returns the top element.
     *
     * <p>Time complexity: O(1).
     *
     * @return the top element
     * @throws java.util.EmptyStackException if the stack is empty
     */
    public T pop() {
        checkNotEmpty();
        T val = (T) data[--size];
        data[size] = null; // allow GC
        return val;
    }

    /**
     * Returns the top element without removing it.
     *
     * <p>Time complexity: O(1).
     *
     * @return the top element
     * @throws java.util.EmptyStackException if the stack is empty
     */
    public T peek() {
        checkNotEmpty();
        return (T) data[size - 1];
    }

    /**
     * Returns {@code true} if the stack has no elements.
     *
     * <p>Time complexity: O(1).
     *
     * @return {@code true} if empty
     */
    public boolean isEmpty() {
        return size == 0;
    }

    /**
     * Returns the number of elements on the stack.
     *
     * <p>Time complexity: O(1).
     *
     * @return current size
     */
    public int size() {
        return size;
    }

    // -----------------------------------------------------------------------
    // toString
    // -----------------------------------------------------------------------

    /**
     * Returns a string showing stack contents from bottom to top.
     *
     * <p>Example: {@code bottom [1, 2, 3] top}
     *
     * @return string representation
     */
    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder("bottom [");
        for (int i = 0; i < size; i++) {
            sb.append(data[i]);
            if (i < size - 1) sb.append(", ");
        }
        sb.append("] top");
        return sb.toString();
    }

    // -----------------------------------------------------------------------
    // Private helpers
    // -----------------------------------------------------------------------

    /** Doubles the backing array when it is full. */
    private void ensureCapacity() {
        if (size == data.length) {
            Object[] newData = new Object[data.length * 2];
            System.arraycopy(data, 0, newData, 0, size);
            data = newData;
        }
    }

    /** Throws if the stack is empty. */
    private void checkNotEmpty() {
        if (isEmpty()) {
            throw new java.util.EmptyStackException();
        }
    }

    // -----------------------------------------------------------------------
    // StackWithMin — inner class
    // -----------------------------------------------------------------------

    /**
     * A stack of {@link Integer} values that additionally tracks the current
     * minimum in O(1) time.
     *
     * <p>A secondary "min stack" mirrors the main stack. Each entry in the min
     * stack stores the minimum value seen so far at-or-below that level.
     * When an element is popped, the corresponding min entry is also popped,
     * so the running minimum is always the top of the min stack.
     *
     * <p>Time complexities:
     * <ul>
     *   <li>push(int) – O(1) amortised</li>
     *   <li>pop()     – O(1)</li>
     *   <li>min()     – O(1)</li>
     * </ul>
     */
    public static class StackWithMin {

        /** Main stack holding the actual values. */
        private final Stack<Integer> main;

        /**
         * Auxiliary stack. Top always holds the minimum of the main stack
         * at the corresponding depth.
         */
        private final Stack<Integer> minStack;

        /**
         * Creates an empty StackWithMin.
         */
        public StackWithMin() {
            main = new Stack<>();
            minStack = new Stack<>();
        }

        /**
         * Pushes {@code value} onto the stack and updates the running minimum.
         *
         * <p>Time complexity: O(1) amortised.
         *
         * @param value the integer to push
         */
        public void push(int value) {
            main.push(value);
            if (minStack.isEmpty() || value <= minStack.peek()) {
                minStack.push(value);
            } else {
                minStack.push(minStack.peek()); // propagate current min
            }
        }

        /**
         * Removes and returns the top element, keeping the minimum current.
         *
         * <p>Time complexity: O(1).
         *
         * @return the top element
         * @throws java.util.EmptyStackException if the stack is empty
         */
        public int pop() {
            minStack.pop();
            return main.pop();
        }

        /**
         * Returns the top element without removing it.
         *
         * <p>Time complexity: O(1).
         *
         * @return the top element
         * @throws java.util.EmptyStackException if the stack is empty
         */
        public int peek() {
            return main.peek();
        }

        /**
         * Returns the minimum value currently in the stack in O(1) time.
         *
         * <p>Time complexity: O(1).
         *
         * @return the minimum value
         * @throws java.util.EmptyStackException if the stack is empty
         */
        public int min() {
            return minStack.peek();
        }

        /**
         * Returns {@code true} if the stack has no elements.
         *
         * @return {@code true} if empty
         */
        public boolean isEmpty() {
            return main.isEmpty();
        }

        /**
         * Returns the number of elements on the stack.
         *
         * @return current size
         */
        public int size() {
            return main.size();
        }

        /**
         * Returns the stack contents (bottom to top) and the current minimum.
         *
         * @return string representation
         */
        @Override
        public String toString() {
            return main.toString() + "  (min=" + (isEmpty() ? "N/A" : min()) + ")";
        }
    }

    // -----------------------------------------------------------------------
    // Demo main
    // -----------------------------------------------------------------------

    /**
     * Demonstrates Stack and StackWithMin operations.
     *
     * @param args unused
     */
    public static void main(String[] args) {
        System.out.println("=== Stack Demo ===\n");

        Stack<Integer> stack = new Stack<>();

        System.out.println("-- push --");
        for (int v : new int[]{5, 3, 7, 1, 4}) {
            stack.push(v);
            System.out.println("push(" + v + "): " + stack);
        }

        System.out.println("\n-- peek --");
        System.out.println("peek() = " + stack.peek());

        System.out.println("\n-- pop --");
        while (!stack.isEmpty()) {
            System.out.println("pop() = " + stack.pop() + " | " + stack);
        }

        System.out.println("\n-- isEmpty after all pops --");
        System.out.println("isEmpty = " + stack.isEmpty());

        System.out.println("\n=== StackWithMin Demo ===\n");

        StackWithMin swm = new StackWithMin();
        int[] values = {5, 3, 7, 2, 8, 1, 4};
        System.out.println("-- push with min tracking --");
        for (int v : values) {
            swm.push(v);
            System.out.println("push(" + v + "): " + swm);
        }

        System.out.println("\n-- pop with min tracking --");
        while (!swm.isEmpty()) {
            System.out.println("pop()=" + swm.pop() + " | " + swm);
        }
    }
}
