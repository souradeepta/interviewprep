/**
 * Reverse Linked List
 *
 * Problem: Reverse a singly linked list in-place.
 *
 * Input: 1 → 2 → 3 → 4 → 5 → null
 * Output: 5 → 4 → 3 → 2 → 1 → null
 *
 * Approach:
 * - Iterative with three pointers: prev, curr, next
 * - Reverse the direction of each link
 * - Time: O(n), Space: O(1)
 */
public class ReverseLinkedList {

    public static class ListNode {
        int val;
        ListNode next;
        ListNode(int x) { val = x; }
    }

    /**
     * Reverse a singly linked list.
     *
     * @param head Head of the linked list
     * @return New head (previously the tail)
     *
     * Time: O(n)
     * Space: O(1)
     */
    public ListNode reverseList(ListNode head) {
        ListNode prev = null;
        ListNode curr = head;

        while (curr != null) {
            // Store next node before we change curr.next
            ListNode nextTemp = curr.next;
            // Reverse the link
            curr.next = prev;
            // Move prev and curr one step forward
            prev = curr;
            curr = nextTemp;
        }

        return prev;
    }

    private static ListNode buildList(int[] values) {
        if (values.length == 0) return null;
        ListNode head = new ListNode(values[0]);
        ListNode curr = head;
        for (int i = 1; i < values.length; i++) {
            curr.next = new ListNode(values[i]);
            curr = curr.next;
        }
        return head;
    }

    private static String listToString(ListNode head) {
        StringBuilder sb = new StringBuilder();
        ListNode curr = head;
        while (curr != null) {
            sb.append(curr.val).append(" → ");
            curr = curr.next;
        }
        sb.append("null");
        return sb.toString();
    }

    public static void main(String[] args) {
        ReverseLinkedList solver = new ReverseLinkedList();

        // Test case 1: Normal list
        ListNode head1 = buildList(new int[]{1, 2, 3, 4, 5});
        ListNode result1 = solver.reverseList(head1);
        System.out.println("Test 1: " + listToString(result1));

        // Test case 2: Single element
        ListNode head2 = buildList(new int[]{1});
        ListNode result2 = solver.reverseList(head2);
        System.out.println("Test 2: " + listToString(result2));

        // Test case 3: Empty list
        ListNode head3 = buildList(new int[]{});
        ListNode result3 = solver.reverseList(head3);
        System.out.println("Test 3: " + listToString(result3));

        // Test case 4: Two elements
        ListNode head4 = buildList(new int[]{1, 2});
        ListNode result4 = solver.reverseList(head4);
        System.out.println("Test 4: " + listToString(result4));
    }
}
