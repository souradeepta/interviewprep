import pytest
from python.basic.linked_list import SinglyLinkedList, DoublyLinkedList


class TestSinglyLinkedList:
    def test_append_and_to_list(self):
        sll = SinglyLinkedList()
        sll.append(1)
        sll.append(2)
        sll.append(3)
        assert sll.to_list() == [1, 2, 3]

    def test_prepend(self):
        sll = SinglyLinkedList()
        sll.prepend(2)
        sll.prepend(1)
        assert sll.to_list() == [1, 2]

    def test_delete_value(self):
        sll = SinglyLinkedList()
        for v in [1, 2, 3, 2]:
            sll.append(v)
        sll.delete(2)
        assert sll.to_list() == [1, 3, 2]

    def test_delete_head(self):
        sll = SinglyLinkedList()
        sll.append(1)
        sll.append(2)
        sll.delete(1)
        assert sll.to_list() == [2]

    def test_delete_nonexistent(self):
        sll = SinglyLinkedList()
        sll.append(1)
        sll.delete(99)
        assert sll.to_list() == [1]

    def test_search_found(self):
        sll = SinglyLinkedList()
        sll.append(10)
        sll.append(20)
        node = sll.search(20)
        assert node is not None and node.val == 20

    def test_search_not_found(self):
        sll = SinglyLinkedList()
        sll.append(1)
        assert sll.search(99) is None

    def test_reverse(self):
        sll = SinglyLinkedList()
        for v in [1, 2, 3]:
            sll.append(v)
        sll.reverse()
        assert sll.to_list() == [3, 2, 1]

    def test_len(self):
        sll = SinglyLinkedList()
        assert len(sll) == 0
        sll.append(1)
        assert len(sll) == 1

    def test_empty_list(self):
        sll = SinglyLinkedList()
        assert sll.to_list() == []


class TestDoublyLinkedList:
    def test_append_and_to_list(self):
        dll = DoublyLinkedList()
        dll.append(1)
        dll.append(2)
        dll.append(3)
        assert dll.to_list() == [1, 2, 3]

    def test_prepend(self):
        dll = DoublyLinkedList()
        dll.prepend(2)
        dll.prepend(1)
        assert dll.to_list() == [1, 2]

    def test_delete(self):
        dll = DoublyLinkedList()
        dll.append(1)
        dll.append(2)
        dll.append(3)
        dll.delete(2)
        assert dll.to_list() == [1, 3]
