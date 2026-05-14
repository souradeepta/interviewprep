package basic;

/**
 * A generic singly linked list.
 *
 * <p>Each node holds a value and a reference to the next node. A {@code head}
 * pointer tracks the first node; a {@code tail} pointer enables O(1) appends.
 *
 * <p>Time complexities:
 * <ul>
 *   <li>addFirst(T)         – O(1)</li>
 *   <li>addLast(T)          – O(1)</li>
 *   <li>add(int, T)         – O(n)</li>
 *   <li>removeFirst()       – O(1)</li>
 *   <li>removeLast()        – O(n)  – must walk to second-to-last node</li>
 *   <li>remove(int)         – O(n)</li>
 *   <li>get(int)            – O(n)</li>
 *   <li>reverse()           – O(n)</li>
 *   <li>size()              – O(1)</li>
 * </ul>
 *
 * @param <T> the element type
 */
public class SinglyLinkedList<T> {

    // -----------------------------------------------------------------------
    // Inner Node class
    // -----------------------------------------------------------------------

    /**
     * A single node in the linked list.
     *
     * @param <T> the element type
     */
    public static class Node<T> {
        /** The value stored in this node. */
        T data;
        /** Reference to the next node, or {@code null} if this is the tail. */
        Node<T> next;

        /**
         * Constructs a node with the given data and no successor.
         *
         * @param data the value to store
         */
        Node(T data) {
            this.data = data;
            this.next = null;
        }
    }

    // -----------------------------------------------------------------------
    // Fields
    // -----------------------------------------------------------------------

    /** First node in the list; {@code null} if the list is empty. */
    private Node<T> head;

    /** Last node in the list; {@code null} if the list is empty. */
    private Node<T> tail;

    /** Number of nodes currently in the list. */
    private int size;

    // -----------------------------------------------------------------------
    // Constructor
    // -----------------------------------------------------------------------

    /**
     * Creates an empty SinglyLinkedList.
     */
    public SinglyLinkedList() {
        head = null;
        tail = null;
        size = 0;
    }

    // -----------------------------------------------------------------------
    // Add operations
    // -----------------------------------------------------------------------

    /**
     * Inserts {@code data} at the front of the list.
     *
     * <p>Time complexity: O(1).
     *
     * @param data the value to prepend
     */
    public void addFirst(T data) {
        Node<T> node = new Node<>(data);
        node.next = head;
        head = node;
        if (tail == null) tail = head;
        size++;
    }

    /**
     * Appends {@code data} at the end of the list.
     *
     * <p>Time complexity: O(1).
     *
     * @param data the value to append
     */
    public void addLast(T data) {
        Node<T> node = new Node<>(data);
        if (tail == null) {
            head = tail = node;
        } else {
            tail.next = node;
            tail = node;
        }
        size++;
    }

    /**
     * Inserts {@code data} at position {@code index} (0-based).
     *
     * <p>Inserting at index 0 is equivalent to {@link #addFirst},
     * and inserting at index {@code size} is equivalent to {@link #addLast}.
     *
     * <p>Time complexity: O(n).
     *
     * @param index position in [0, size]
     * @param data  the value to insert
     * @throws IndexOutOfBoundsException if index is out of [0, size]
     */
    public void add(int index, T data) {
        checkIndexForAdd(index);
        if (index == 0) { addFirst(data); return; }
        if (index == size) { addLast(data); return; }
        Node<T> prev = nodeAt(index - 1);
        Node<T> node = new Node<>(data);
        node.next = prev.next;
        prev.next = node;
        size++;
    }

    // -----------------------------------------------------------------------
    // Remove operations
    // -----------------------------------------------------------------------

    /**
     * Removes and returns the first element.
     *
     * <p>Time complexity: O(1).
     *
     * @return the removed value
     * @throws java.util.NoSuchElementException if the list is empty
     */
    public T removeFirst() {
        checkNotEmpty();
        T val = head.data;
        head = head.next;
        if (head == null) tail = null;
        size--;
        return val;
    }

    /**
     * Removes and returns the last element.
     *
     * <p>Time complexity: O(n) — must walk to the second-to-last node.
     *
     * @return the removed value
     * @throws java.util.NoSuchElementException if the list is empty
     */
    public T removeLast() {
        checkNotEmpty();
        T val = tail.data;
        if (size == 1) {
            head = tail = null;
        } else {
            Node<T> prev = nodeAt(size - 2);
            prev.next = null;
            tail = prev;
        }
        size--;
        return val;
    }

    /**
     * Removes and returns the element at position {@code index}.
     *
     * <p>Time complexity: O(n).
     *
     * @param index position in [0, size)
     * @return the removed value
     * @throws IndexOutOfBoundsException if index is out of [0, size)
     */
    public T remove(int index) {
        checkIndex(index);
        if (index == 0) return removeFirst();
        if (index == size - 1) return removeLast();
        Node<T> prev = nodeAt(index - 1);
        T val = prev.next.data;
        prev.next = prev.next.next;
        size--;
        return val;
    }

    // -----------------------------------------------------------------------
    // Access operations
    // -----------------------------------------------------------------------

    /**
     * Returns the element at position {@code index} without removing it.
     *
     * <p>Time complexity: O(n).
     *
     * @param index position in [0, size)
     * @return the element
     * @throws IndexOutOfBoundsException if index is out of [0, size)
     */
    public T get(int index) {
        checkIndex(index);
        return nodeAt(index).data;
    }

    /**
     * Returns the number of elements in the list.
     *
     * <p>Time complexity: O(1).
     *
     * @return current size
     */
    public int size() {
        return size;
    }

    /**
     * Returns {@code true} if the list contains no elements.
     *
     * @return {@code true} if empty
     */
    public boolean isEmpty() {
        return size == 0;
    }

    // -----------------------------------------------------------------------
    // Reverse
    // -----------------------------------------------------------------------

    /**
     * Reverses the list in-place by re-linking all nodes.
     *
     * <p>Time complexity: O(n).
     * Space complexity: O(1).
     */
    public void reverse() {
        Node<T> prev = null;
        Node<T> curr = head;
        tail = head; // current head will become the new tail
        while (curr != null) {
            Node<T> next = curr.next;
            curr.next = prev;
            prev = curr;
            curr = next;
        }
        head = prev;
    }

    // -----------------------------------------------------------------------
    // toString
    // -----------------------------------------------------------------------

    /**
     * Returns a human-readable representation of the list using the classic
     * {@code value -> value -> null} format.
     *
     * <p>Example: {@code 1 -> 2 -> 3 -> null}
     *
     * @return string representation
     */
    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        Node<T> curr = head;
        while (curr != null) {
            sb.append(curr.data).append(" -> ");
            curr = curr.next;
        }
        sb.append("null");
        return sb.toString();
    }

    // -----------------------------------------------------------------------
    // Private helpers
    // -----------------------------------------------------------------------

    /** Returns the node at position {@code index} by walking from head. */
    private Node<T> nodeAt(int index) {
        Node<T> curr = head;
        for (int i = 0; i < index; i++) {
            curr = curr.next;
        }
        return curr;
    }

    /** Validates an index for read / remove operations. */
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

    /** Throws if the list is empty. */
    private void checkNotEmpty() {
        if (isEmpty()) {
            throw new java.util.NoSuchElementException("List is empty");
        }
    }

    // -----------------------------------------------------------------------
    // Demo main
    // -----------------------------------------------------------------------

    /**
     * Demonstrates all SinglyLinkedList operations.
     *
     * @param args unused
     */
    public static void main(String[] args) {
        System.out.println("=== SinglyLinkedList Demo ===\n");

        SinglyLinkedList<Integer> list = new SinglyLinkedList<>();

        System.out.println("-- addLast --");
        for (int v : new int[]{1, 2, 3, 4, 5}) {
            list.addLast(v);
            System.out.println("addLast(" + v + "): " + list);
        }

        System.out.println("\n-- addFirst --");
        list.addFirst(0);
        System.out.println("addFirst(0): " + list);

        System.out.println("\n-- add(index, T) --");
        list.add(3, 99);
        System.out.println("add(3, 99): " + list);

        System.out.println("\n-- get(index) --");
        System.out.println("get(0) = " + list.get(0));
        System.out.println("get(3) = " + list.get(3));

        System.out.println("\n-- removeFirst --");
        System.out.println("removeFirst() = " + list.removeFirst() + " | " + list);

        System.out.println("\n-- removeLast --");
        System.out.println("removeLast() = " + list.removeLast() + " | " + list);

        System.out.println("\n-- remove(index) --");
        System.out.println("remove(2) = " + list.remove(2) + " | " + list);

        System.out.println("\n-- reverse --");
        list.reverse();
        System.out.println("after reverse(): " + list);

        System.out.println("\n-- size / isEmpty --");
        System.out.println("size=" + list.size() + ", isEmpty=" + list.isEmpty());
    }
}
