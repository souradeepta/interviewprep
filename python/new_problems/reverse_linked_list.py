"""
Reverse Linked List

Problem: Reverse a singly linked list in-place.

Input: 1 → 2 → 3 → 4 → 5 → None
Output: 5 → 4 → 3 → 2 → 1 → None

Approach:
- Iterative with three pointers: prev, curr, next
- Reverse the direction of each link
- Time: O(n), Space: O(1)
"""

class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def reverseList(head):
    """
    Reverse a singly linked list.

    Args:
        head: Head of the linked list

    Returns:
        New head (previously the tail)

    Time: O(n)
    Space: O(1)
    """
    prev = None
    curr = head

    while curr:
        # Store next node before we change curr.next
        next_temp = curr.next
        # Reverse the link
        curr.next = prev
        # Move prev and curr one step forward
        prev = curr
        curr = next_temp

    return prev

def _build_list(values):
    """Helper: build linked list from list of values."""
    if not values:
        return None
    head = ListNode(values[0])
    curr = head
    for val in values[1:]:
        curr.next = ListNode(val)
        curr = curr.next
    return head

def _list_to_array(head):
    """Helper: convert linked list to array."""
    result = []
    curr = head
    while curr:
        result.append(curr.val)
        curr = curr.next
    return result

if __name__ == "__main__":
    # Test case 1: Normal list
    head1 = _build_list([1, 2, 3, 4, 5])
    result1 = reverseList(head1)
    print(f"Test 1: {_list_to_array(result1)} == [5, 4, 3, 2, 1]")

    # Test case 2: Single element
    head2 = _build_list([1])
    result2 = reverseList(head2)
    print(f"Test 2: {_list_to_array(result2)} == [1]")

    # Test case 3: Empty list
    head3 = _build_list([])
    result3 = reverseList(head3)
    print(f"Test 3: {_list_to_array(result3)} == []")

    # Test case 4: Two elements
    head4 = _build_list([1, 2])
    result4 = reverseList(head4)
    print(f"Test 4: {_list_to_array(result4)} == [2, 1]")
