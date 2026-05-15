"""LRU Cache - Least Recently Used eviction policy"""

class Node:
    """Doubly linked list node"""
        """__init__ implementation.

        Time: O(n)
        Space: O(1)
        """
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:
    """O(1) LRU Cache using doubly linked list + hash map"""

    def __init__(self, capacity: int):
        """Initialize cache with fixed capacity."""
        self.capacity = capacity
        self.cache = {}  # key -> Node
        self.head = Node(0, 0)  # dummy head (most recent)
        self.tail = Node(0, 0)  # dummy tail (least recent)
        self.head.next = self.tail
        self.tail.prev = self.head

    def get(self, key: int) -> int:
        """Get value and mark as recently used. Returns -1 if not found."""
        if key not in self.cache:
            return -1

        node = self.cache[key]
        self._remove(node)
        self._add_to_front(node)
        return node.value

    def put(self, key: int, value: int) -> None:
        """Insert or update key-value pair."""
        if key in self.cache:
            node = self.cache[key]
            node.value = value
            self._remove(node)
            self._add_to_front(node)
        else:
            node = Node(key, value)
            self.cache[key] = node
            self._add_to_front(node)

            if len(self.cache) > self.capacity:
                lru = self.tail.prev
                self._remove(lru)
                del self.cache[lru.key]

    def _remove(self, node):
        """Remove node from linked list"""
        node.prev.next = node.next
        node.next.prev = node.prev

    def _add_to_front(self, node):
        """Add node after head (most recent)"""
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node


if __name__ == "__main__":
    cache = LRUCache(2)
    cache.put(1, 1)
    cache.put(2, 2)
    print(f"get(1): {cache.get(1)}")  # 1
    cache.put(3, 3)
    print(f"get(2): {cache.get(2)}")  # -1 (evicted)
    cache.put(4, 4)
    print(f"get(1): {cache.get(1)}")  # -1 (evicted)
    print(f"get(3): {cache.get(3)}")  # 3
    print(f"get(4): {cache.get(4)}")  # 4