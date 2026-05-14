package basic;

/**
 * A generic doubly linked list.
 *
 * <p>Each node holds a value and references to both the previous and next
 * nodes. A sentinel {@code head} and {@code tail} node simplify edge-case
 * handling (no special cases for empty list or first/last element).
 *
 * <p>Time complexities:
 * <ul>
 *   <li>addFirst(T)         – O(1)</li>
 *   <li>addLast(T)          – O(1)</li>
 *   <li>add(int, T)         – O(n)</li>
 *   <li>removeFirst()       – O(1)</li>
 *   <li>removeLast()        – O(1)</li>
 *   <li>remove(int)         – O(n)</li>
 *   <li>get(int)            – O(n)</li>
 *   <li>size()              – O(1)</li>
 * </ul>
 *
 * @param <T> the element type
 */
public class DoublyLinkedList<T> {

    // -----------------------------------------------------------------------
    // Inner Node class
    // -----------------------------------------------------------------------

    /**
     * A single node in the doubly linked list.
     *
     * @param <T> the element type
     */
    public static class Node<T> {
        /** The value stored in this node. */
        T data;
        /** Reference to the previous node. */
        Node<T> prev;
        /** Reference to the next node. */
        Node<T> next;

        /**
         * Constructs a node with the given data and no neighbours.
         *
         * @param data the value to store
         */
        Node(T data) {
            this.data = data;
            this.prev = null;
            this.next = null;
        }
    }

    // -----------------------------------------------------------------------
    // Fields
    // -----------------------------------------------------------------------

    /**
     * Sentinel head node. {@code head.next} is the first real node.
     * Its {@code data} is always {@code null}.
     */
    private final Node<T> head;

    /**
     * Sentinel tail node. {@code tail.prev} is the last real node.
     * Its {@code data} is always {@code null}.
     */
    private final Node<T> tail;

    /** Number of real (non-sentinel) nodes. */
    private int size;

    // -----------------------------------------------------------------------
    // Constructor
    // -----------------------------------------------------------------------

    /**
     * Creates an empty DoublyLinkedList with sentinel head/tail nodes.
     */
    public DoublyLinkedList() {
        head = new Node<>(null);
        tail = new Node<>(null);
        head.next = tail;
        tail.prev = head;
        size = 0;
    }

    // -----------------------------------------------------------------------
    // Add operations
    // -----------------------------------------------------------------------

    /**
     * Inserts {@code data} at the front of the list (after the head sentinel).
     *
     * <p>Time complexity: O(1).
     *
     * @param data the value to prepend
     */
    public void addFirst(T data) {
        insertAfter(head, new Node<>(data));
    }

    /**
     * Appends {@code data} at the end of the list (before the tail sentinel).
     *
     * <p>Time complexity: O(1).
     *
     * @param data the value to append
     */
    public void addLast(T data) {
        insertBefore(tail, new Node<>(data));
    }

    /**
     * Inserts {@code data} at position {@code index} (0-based).
     *
     * <p>Time complexity: O(n).
     *
     * @param index position in [0, size]
     * @param data  the value to insert
     * @throws IndexOutOfBoundsException if index is out of [0, size]
     */
    public void add(int index, T data) {
        checkIndexForAdd(index);
        // Walk to the node currently at that index (or tail sentinel if index==size)
        Node<T> successor = nodeAt(index);
        insertBefore(successor, new Node<>(data));
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
        return unlink(head.next);
    }

    /**
     * Removes and returns the last element.
     *
     * <p>Time complexity: O(1).
     *
     * @return the removed value
     * @throws java.util.NoSuchElementException if the list is empty
     */
    public T removeLast() {
        checkNotEmpty();
        return unlink(tail.prev);
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
        return unlink(nodeAt(index));
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
    // toString — both directions
    // -----------------------------------------------------------------------

    /**
     * Returns a forward representation of the list.
     *
     * <p>Example: {@code null <-> 1 <-> 2 <-> 3 <-> null}
     *
     * @return string representation (forward direction)
     */
    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder("null <-> ");
        Node<T> curr = head.next;
        while (curr != tail) {
            sb.append(curr.data).append(" <-> ");
            curr = curr.next;
        }
        sb.append("null");
        return sb.toString();
    }

    /**
     * Returns a reverse representation of the list, traversing from tail to head.
     *
     * <p>Example: {@code null <-> 3 <-> 2 <-> 1 <-> null}
     *
     * @return string representation (reverse / backward direction)
     */
    public String toStringReverse() {
        StringBuilder sb = new StringBuilder("null <-> ");
        Node<T> curr = tail.prev;
        while (curr != head) {
            sb.append(curr.data).append(" <-> ");
            curr = curr.prev;
        }
        sb.append("null");
        return sb.toString();
    }

    // -----------------------------------------------------------------------
    // Private helpers
    // -----------------------------------------------------------------------

    /**
     * Inserts {@code newNode} directly after {@code predecessor}.
     * Updates all four pointers and increments size.
     */
    private void insertAfter(Node<T> predecessor, Node<T> newNode) {
        Node<T> successor = predecessor.next;
        newNode.prev = predecessor;
        newNode.next = successor;
        predecessor.next = newNode;
        successor.prev = newNode;
        size++;
    }

    /**
     * Inserts {@code newNode} directly before {@code successor}.
     * Delegates to {@link #insertAfter(Node, Node)}.
     */
    private void insertBefore(Node<T> successor, Node<T> newNode) {
        insertAfter(successor.prev, newNode);
    }

    /**
     * Removes {@code node} from the list and returns its data.
     * Updates the two neighbouring pointers and decrements size.
     */
    private T unlink(Node<T> node) {
        node.prev.next = node.next;
        node.next.prev = node.prev;
        node.prev = null;
        node.next = null;
        size--;
        return node.data;
    }

    /**
     * Returns the real node at 0-based {@code index}, or the tail sentinel
     * when {@code index == size}.  Chooses forward/backward traversal based
     * on which end is closer.
     */
    private Node<T> nodeAt(int index) {
        // index == size returns the tail sentinel (used by add)
        if (index <= size / 2) {
            // Walk forward from head sentinel
            Node<T> curr = head.next;
            for (int i = 0; i < index; i++) curr = curr.next;
            return curr;
        } else {
            // Walk backward from tail sentinel
            Node<T> curr = tail;
            for (int i = size; i > index; i--) curr = curr.prev;
            return curr;
        }
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
     * Demonstrates all DoublyLinkedList operations.
     *
     * @param args unused
     */
    public static void main(String[] args) {
        System.out.println("=== DoublyLinkedList Demo ===\n");

        DoublyLinkedList<Integer> list = new DoublyLinkedList<>();

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

        System.out.println("\n-- Reverse traversal --");
        System.out.println("reverse: " + list.toStringReverse());

        System.out.println("\n-- get(index) --");
        System.out.println("get(0) = " + list.get(0));
        System.out.println("get(3) = " + list.get(3));

        System.out.println("\n-- removeFirst --");
        System.out.println("removeFirst() = " + list.removeFirst() + " | " + list);

        System.out.println("\n-- removeLast --");
        System.out.println("removeLast() = " + list.removeLast() + " | " + list);

        System.out.println("\n-- remove(index) --");
        System.out.println("remove(2) = " + list.remove(2) + " | " + list);

        System.out.println("\n-- size / isEmpty --");
        System.out.println("size=" + list.size() + ", isEmpty=" + list.isEmpty());
    }
}
