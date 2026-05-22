# Repo Comprehensive Enhancement Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform this SDE interview prep repo into a fully tested, pattern-organized codebase with comprehensive pytest coverage, LeetCode-style pattern problems, and fixed broken infrastructure.

**Architecture:** Fix broken test imports via `conftest.py`, add test suites for all existing DS/algorithms, and add a new `python/patterns/` module of LeetCode-style problems organized by interview pattern — each with tests. Java code kept as-is (no JUnit test runner configured).

**Tech Stack:** Python 3.12, pytest 9.x, existing stdlib (no new deps needed)

---

## File Structure

### New files to create
- `conftest.py` — pytest root config that adds repo root to `sys.path`
- `tests/basic/test_array.py` — tests for `python/basic/array.py`
- `tests/basic/test_stack.py` — tests for `python/basic/stack.py`
- `tests/basic/test_queue.py` — tests for `python/basic/queue_ds.py`
- `tests/basic/test_linked_list.py` — tests for `python/basic/linked_list.py`
- `tests/basic/test_hashmap.py` — tests for `python/basic/hashmap.py`
- `tests/basic/test_deque.py` — tests for `python/basic/deque_ds.py`
- `tests/algorithms/test_sorting.py` — tests for `python/algorithms/sorting/sorting.py`
- `tests/algorithms/test_searching.py` — tests for `python/algorithms/searching/searching.py`
- `tests/algorithms/test_string.py` — tests for `python/algorithms/string/string_algorithms.py`
- `tests/algorithms/test_dp.py` — tests for `python/algorithms/dp/dp.py`
- `tests/algorithms/test_graph.py` — tests for `python/algorithms/graph/graph_algorithms.py`
- `python/patterns/two_pointer.py` — 10 two-pointer interview problems
- `python/patterns/sliding_window.py` — 10 sliding window interview problems
- `python/patterns/binary_search.py` — 8 binary search interview problems
- `python/patterns/monotonic_stack.py` — 6 monotonic stack interview problems
- `python/patterns/prefix_sum.py` — 6 prefix sum / range query problems
- `python/patterns/__init__.py` — empty init
- `tests/patterns/test_two_pointer.py` — tests for two_pointer.py
- `tests/patterns/test_sliding_window.py` — tests for sliding_window.py
- `tests/patterns/test_binary_search.py` — tests for binary_search.py
- `tests/patterns/test_monotonic_stack.py` — tests for monotonic_stack.py
- `tests/patterns/test_prefix_sum.py` — tests for prefix_sum.py
- `tests/basic/__init__.py`, `tests/algorithms/__init__.py`, `tests/patterns/__init__.py` — empty inits

### Files to modify
- `python/algorithms/dp/test_backtracking.py` — fix broken `sys.path` import (line 2)
- `python/algorithms/graph/test_tree_graph_patterns.py` — fix broken `sys.path` import (line 2)
- `python/system_design/lru_cache.py` — remove stray docstring inside `Node` class (lines 8-14)
- `tests/system_design/test_lru_cache.py` — remove malformed docstrings injected inside test methods

---

## Task 1: Fix pytest infrastructure

**Files:**
- Create: `conftest.py`
- Modify: `python/algorithms/dp/test_backtracking.py:1-3`
- Modify: `python/algorithms/graph/test_tree_graph_patterns.py:1-3`

- [ ] **Step 1: Create conftest.py at repo root**

```python
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
```

Save as `/home/sbisw/github/datastructures/conftest.py`.

- [ ] **Step 2: Fix broken import in test_backtracking.py**

Replace lines 1-3 of `python/algorithms/dp/test_backtracking.py`:
```python
# old (broken):
import sys
sys.path.insert(0, '/home/sbisw/github/interviewprep/python/algorithms/dp')
```
with:
```python
# new (no path hack needed — conftest.py handles it):
```
(Delete those two lines; the file starts directly with `from dp import ...` — but since conftest.py adds the repo root, we need to use the full module path)

Replace the import line:
```python
from dp import solve_nqueens, solve_sudoku, word_search, permute, combine, \
    letter_combinations, subsets, generate_parentheses
```
with:
```python
from python.algorithms.dp.dp import solve_nqueens, solve_sudoku, word_search, permute, combine, \
    letter_combinations, subsets, generate_parentheses
```

- [ ] **Step 3: Fix broken import in test_tree_graph_patterns.py**

Replace lines 1-3 of `python/algorithms/graph/test_tree_graph_patterns.py`:
```python
import sys
sys.path.insert(0, '/home/sbisw/github/interviewprep/python/algorithms/graph')
```
with nothing, and fix the import to:
```python
from python.algorithms.graph.graph_algorithms import (
    TreeNode, lca, path_sum, all_paths_sum, tree_diameter,
    rob_tree, build_tree_preorder_inorder, serialize_tree, deserialize_tree,
    count_islands, is_bipartite, has_cycle_directed, has_cycle_undirected
)
```

- [ ] **Step 4: Verify all three tests now pass**

```bash
cd /home/sbisw/github/datastructures
pytest python/algorithms/dp/test_backtracking.py python/algorithms/graph/test_tree_graph_patterns.py python/algorithms/dp/test_grid_dp.py -v
```

Expected: All tests PASS (no import errors).

- [ ] **Step 5: Commit**

```bash
git add conftest.py python/algorithms/dp/test_backtracking.py python/algorithms/graph/test_tree_graph_patterns.py
git commit -m "fix: repair broken sys.path imports in test files via conftest.py"
```

---

## Task 2: Fix malformed source files

**Files:**
- Modify: `python/system_design/lru_cache.py`
- Modify: `tests/system_design/test_lru_cache.py`

- [ ] **Step 1: Remove stray docstring in lru_cache.py Node class**

In `python/system_design/lru_cache.py`, the `Node` class has a stray docstring block after the class docstring, before `__init__`. Remove it so the file reads:

```python
"""LRU Cache - Least Recently Used eviction policy"""

class Node:
    """Doubly linked list node"""
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None
```

- [ ] **Step 2: Remove malformed docstrings injected in test_lru_cache.py**

In `tests/system_design/test_lru_cache.py`, several test methods have a stray multi-line docstring inserted between the method signature and body. Remove all occurrences of this pattern:
```
    """

    [Brief description of what this function does]
    ...
    Time: O([complexity])
    Space: O([complexity])

    """
```
so each test method starts directly with its body (e.g., `cache = LRUCache(2)`).

- [ ] **Step 3: Run system_design tests to verify they pass**

```bash
cd /home/sbisw/github/datastructures
pytest tests/system_design/ -v
```

Expected: All 5 test files PASS.

- [ ] **Step 4: Commit**

```bash
git add python/system_design/lru_cache.py tests/system_design/test_lru_cache.py
git commit -m "fix: remove stray injected docstrings from lru_cache and test file"
```

---

## Task 3: Tests for basic data structures

**Files:**
- Create: `tests/basic/__init__.py`
- Create: `tests/basic/test_linked_list.py`
- Create: `tests/basic/test_stack.py`
- Create: `tests/basic/test_queue.py`
- Create: `tests/basic/test_hashmap.py`

- [ ] **Step 1: Create empty init**

```python
# tests/basic/__init__.py
```

- [ ] **Step 2: Write linked list tests**

Create `tests/basic/test_linked_list.py`:

```python
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
```

- [ ] **Step 3: Write stack tests**

Create `tests/basic/test_stack.py`:

```python
import pytest
from python.basic.stack import Stack


class TestStack:
    def test_push_and_pop(self):
        s = Stack()
        s.push(1)
        s.push(2)
        assert s.pop() == 2
        assert s.pop() == 1

    def test_peek(self):
        s = Stack()
        s.push(42)
        assert s.peek() == 42
        assert s.size() == 1

    def test_is_empty(self):
        s = Stack()
        assert s.is_empty()
        s.push(1)
        assert not s.is_empty()

    def test_pop_empty_raises(self):
        s = Stack()
        with pytest.raises((IndexError, Exception)):
            s.pop()

    def test_size(self):
        s = Stack()
        for i in range(5):
            s.push(i)
        assert s.size() == 5
```

- [ ] **Step 4: Write queue tests**

Create `tests/basic/test_queue.py`:

```python
import pytest
from python.basic.queue_ds import Queue


class TestQueue:
    def test_enqueue_dequeue(self):
        q = Queue()
        q.enqueue(1)
        q.enqueue(2)
        assert q.dequeue() == 1
        assert q.dequeue() == 2

    def test_peek(self):
        q = Queue()
        q.enqueue(10)
        assert q.peek() == 10
        assert q.size() == 1

    def test_is_empty(self):
        q = Queue()
        assert q.is_empty()
        q.enqueue(1)
        assert not q.is_empty()

    def test_dequeue_empty_raises(self):
        q = Queue()
        with pytest.raises((IndexError, Exception)):
            q.dequeue()

    def test_fifo_order(self):
        q = Queue()
        for i in range(5):
            q.enqueue(i)
        result = [q.dequeue() for _ in range(5)]
        assert result == [0, 1, 2, 3, 4]
```

- [ ] **Step 5: Write hashmap tests**

Create `tests/basic/test_hashmap.py`:

```python
import pytest
from python.basic.hashmap import HashMap


class TestHashMap:
    def test_put_and_get(self):
        h = HashMap()
        h.put("a", 1)
        assert h.get("a") == 1

    def test_overwrite_key(self):
        h = HashMap()
        h.put("x", 10)
        h.put("x", 20)
        assert h.get("x") == 20

    def test_get_missing_key(self):
        h = HashMap()
        assert h.get("missing") is None

    def test_delete(self):
        h = HashMap()
        h.put("k", 5)
        h.delete("k")
        assert h.get("k") is None

    def test_multiple_keys(self):
        h = HashMap()
        for i in range(20):
            h.put(str(i), i * 2)
        for i in range(20):
            assert h.get(str(i)) == i * 2

    def test_contains(self):
        h = HashMap()
        h.put("z", 99)
        assert h.contains("z")
        assert not h.contains("missing")
```

- [ ] **Step 6: Run all basic tests**

```bash
cd /home/sbisw/github/datastructures
pytest tests/basic/ -v
```

Expected: All tests PASS.

- [ ] **Step 7: Commit**

```bash
git add tests/basic/
git commit -m "test: add comprehensive tests for basic data structures"
```

---

## Task 4: Tests for sorting and searching algorithms

**Files:**
- Create: `tests/algorithms/__init__.py`
- Create: `tests/algorithms/test_sorting.py`
- Create: `tests/algorithms/test_searching.py`

- [ ] **Step 1: Check what sorting functions exist**

```bash
grep "^def " /home/sbisw/github/datastructures/python/algorithms/sorting/sorting.py
```

Expected output: bubble_sort, selection_sort, insertion_sort, merge_sort, quick_sort, heap_sort, counting_sort, radix_sort, bucket_sort, tim_sort (or similar names).

- [ ] **Step 2: Write sorting tests**

Create `tests/algorithms/test_sorting.py`:

```python
import pytest
from python.algorithms.sorting.sorting import (
    bubble_sort, selection_sort, insertion_sort,
    merge_sort, quick_sort, heap_sort,
    counting_sort, radix_sort
)

CASES = [
    ([3, 1, 4, 1, 5, 9, 2, 6], [1, 1, 2, 3, 4, 5, 6, 9]),
    ([], []),
    ([1], [1]),
    ([2, 1], [1, 2]),
    ([5, 5, 5], [5, 5, 5]),
    (list(range(10, 0, -1)), list(range(1, 11))),
]


@pytest.mark.parametrize("arr,expected", CASES)
def test_bubble_sort(arr, expected):
    result = bubble_sort(arr[:])
    assert result == expected


@pytest.mark.parametrize("arr,expected", CASES)
def test_selection_sort(arr, expected):
    result = selection_sort(arr[:])
    assert result == expected


@pytest.mark.parametrize("arr,expected", CASES)
def test_insertion_sort(arr, expected):
    result = insertion_sort(arr[:])
    assert result == expected


@pytest.mark.parametrize("arr,expected", CASES)
def test_merge_sort(arr, expected):
    result = merge_sort(arr[:])
    assert result == expected


@pytest.mark.parametrize("arr,expected", CASES)
def test_quick_sort(arr, expected):
    result = quick_sort(arr[:])
    assert result == expected


@pytest.mark.parametrize("arr,expected", CASES)
def test_heap_sort(arr, expected):
    result = heap_sort(arr[:])
    assert result == expected


@pytest.mark.parametrize("arr,expected", [
    ([3, 1, 4, 1, 5, 9], [1, 1, 3, 4, 5, 9]),
    ([], []),
    ([0, 0, 0], [0, 0, 0]),
])
def test_counting_sort(arr, expected):
    result = counting_sort(arr[:])
    assert result == expected


@pytest.mark.parametrize("arr,expected", [
    ([170, 45, 75, 90, 802, 24, 2, 66], [2, 24, 45, 66, 75, 90, 170, 802]),
    ([], []),
    ([1], [1]),
])
def test_radix_sort(arr, expected):
    result = radix_sort(arr[:])
    assert result == expected
```

- [ ] **Step 3: Check what searching functions exist**

```bash
grep "^def " /home/sbisw/github/datastructures/python/algorithms/searching/searching.py
```

- [ ] **Step 4: Write searching tests**

Create `tests/algorithms/test_searching.py`:

```python
import pytest
from python.algorithms.searching.searching import (
    linear_search, binary_search, binary_search_recursive
)


class TestLinearSearch:
    def test_found(self):
        assert linear_search([3, 1, 4, 1, 5], 4) == 2

    def test_not_found(self):
        assert linear_search([1, 2, 3], 99) == -1

    def test_empty(self):
        assert linear_search([], 1) == -1

    def test_first_element(self):
        assert linear_search([7, 2, 3], 7) == 0

    def test_last_element(self):
        assert linear_search([1, 2, 7], 7) == 2


class TestBinarySearch:
    def test_found_middle(self):
        assert binary_search([1, 3, 5, 7, 9], 5) == 2

    def test_found_left(self):
        assert binary_search([1, 3, 5, 7, 9], 1) == 0

    def test_found_right(self):
        assert binary_search([1, 3, 5, 7, 9], 9) == 4

    def test_not_found(self):
        assert binary_search([1, 3, 5, 7, 9], 4) == -1

    def test_empty(self):
        assert binary_search([], 1) == -1

    def test_single_element_found(self):
        assert binary_search([5], 5) == 0

    def test_single_element_not_found(self):
        assert binary_search([5], 3) == -1


class TestBinarySearchRecursive:
    def test_found(self):
        assert binary_search_recursive([2, 4, 6, 8], 6) == 2

    def test_not_found(self):
        assert binary_search_recursive([2, 4, 6, 8], 5) == -1
```

- [ ] **Step 5: Run sorting and searching tests**

```bash
cd /home/sbisw/github/datastructures
pytest tests/algorithms/test_sorting.py tests/algorithms/test_searching.py -v
```

Expected: All tests PASS.

- [ ] **Step 6: Commit**

```bash
git add tests/algorithms/
git commit -m "test: add parametrized tests for sorting (8 algorithms) and searching"
```

---

## Task 5: Tests for DP and graph algorithms

**Files:**
- Modify: `tests/algorithms/test_dp.py` (create)
- Modify: `tests/algorithms/test_graph.py` (create)

- [ ] **Step 1: Check DP functions available**

```bash
grep "^def " /home/sbisw/github/datastructures/python/algorithms/dp/dp.py | head -20
```

- [ ] **Step 2: Write DP algorithm tests**

Create `tests/algorithms/test_dp.py`:

```python
import pytest
from python.algorithms.dp.dp import (
    fibonacci, coin_change, longest_common_subsequence,
    knapsack_01, longest_increasing_subsequence,
    edit_distance, matrix_chain_multiplication
)


class TestFibonacci:
    def test_base_cases(self):
        r = fibonacci(0)
        assert r["memoization"] == 0 and r["tabulation"] == 0
        r = fibonacci(1)
        assert r["memoization"] == 1 and r["tabulation"] == 1

    def test_fib_10(self):
        r = fibonacci(10)
        assert r["memoization"] == 55
        assert r["tabulation"] == 55
        assert r["space_optimized"] == 55

    def test_all_three_match(self):
        r = fibonacci(20)
        assert r["memoization"] == r["tabulation"] == r["space_optimized"]


class TestCoinChange:
    def test_basic(self):
        assert coin_change([1, 5, 6, 9], 11) == 2  # 2+9 or 5+6

    def test_impossible(self):
        assert coin_change([2], 3) == -1

    def test_zero_amount(self):
        assert coin_change([1, 5], 0) == 0

    def test_single_coin(self):
        assert coin_change([5], 10) == 2


class TestLCS:
    def test_basic(self):
        assert longest_common_subsequence("abcde", "ace") == 3

    def test_no_common(self):
        assert longest_common_subsequence("abc", "xyz") == 0

    def test_identical(self):
        assert longest_common_subsequence("abc", "abc") == 3

    def test_empty(self):
        assert longest_common_subsequence("", "abc") == 0


class TestKnapsack:
    def test_basic(self):
        weights = [2, 3, 4, 5]
        values = [3, 4, 5, 6]
        assert knapsack_01(weights, values, 5) == 7  # items 0+1

    def test_empty(self):
        assert knapsack_01([], [], 10) == 0

    def test_capacity_zero(self):
        assert knapsack_01([1, 2], [3, 4], 0) == 0


class TestLIS:
    def test_basic(self):
        assert longest_increasing_subsequence([10, 9, 2, 5, 3, 7, 101, 18]) == 4

    def test_sorted(self):
        assert longest_increasing_subsequence([1, 2, 3, 4, 5]) == 5

    def test_reverse_sorted(self):
        assert longest_increasing_subsequence([5, 4, 3, 2, 1]) == 1

    def test_single(self):
        assert longest_increasing_subsequence([42]) == 1


class TestEditDistance:
    def test_basic(self):
        assert edit_distance("horse", "ros") == 3

    def test_empty_strings(self):
        assert edit_distance("", "") == 0

    def test_one_empty(self):
        assert edit_distance("abc", "") == 3
        assert edit_distance("", "abc") == 3

    def test_identical(self):
        assert edit_distance("abc", "abc") == 0
```

- [ ] **Step 3: Write graph algorithm tests**

Create `tests/algorithms/test_graph.py`:

```python
import pytest
from python.algorithms.graph.graph_algorithms import (
    bfs, dfs, dijkstra, bellman_ford, detect_cycle_undirected,
    topological_sort, count_connected_components, minimum_spanning_tree
)


class TestBFS:
    def test_basic_traversal(self):
        graph = {0: [1, 2], 1: [3], 2: [3], 3: []}
        result = bfs(graph, 0)
        assert result[0] == 0
        assert set(result) == {0, 1, 2, 3}

    def test_single_node(self):
        assert bfs({0: []}, 0) == [0]

    def test_disconnected(self):
        graph = {0: [1], 1: [], 2: [3], 3: []}
        result = bfs(graph, 0)
        assert set(result) == {0, 1}


class TestDFS:
    def test_basic_traversal(self):
        graph = {0: [1, 2], 1: [3], 2: [], 3: []}
        result = dfs(graph, 0)
        assert result[0] == 0
        assert set(result) == {0, 1, 2, 3}

    def test_single_node(self):
        assert dfs({0: []}, 0) == [0]


class TestDijkstra:
    def test_basic(self):
        graph = {
            0: [(1, 4), (2, 1)],
            1: [(3, 1)],
            2: [(1, 2), (3, 5)],
            3: []
        }
        dist = dijkstra(graph, 0)
        assert dist[3] == 4  # 0->2->1->3 = 1+2+1

    def test_single_node(self):
        dist = dijkstra({0: []}, 0)
        assert dist[0] == 0


class TestTopologicalSort:
    def test_basic_dag(self):
        graph = {0: [1, 2], 1: [3], 2: [3], 3: []}
        order = topological_sort(graph)
        assert order.index(0) < order.index(1)
        assert order.index(0) < order.index(2)
        assert order.index(1) < order.index(3)

    def test_linear_chain(self):
        graph = {0: [1], 1: [2], 2: []}
        order = topological_sort(graph)
        assert order == [0, 1, 2]
```

- [ ] **Step 4: Run DP and graph tests**

```bash
cd /home/sbisw/github/datastructures
pytest tests/algorithms/test_dp.py tests/algorithms/test_graph.py -v
```

Expected: All tests PASS (fix any minor API mismatches by checking function signatures).

- [ ] **Step 5: Commit**

```bash
git add tests/algorithms/test_dp.py tests/algorithms/test_graph.py
git commit -m "test: add tests for DP and graph algorithm modules"
```

---

## Task 6: Two-pointer and sliding window pattern problems

**Files:**
- Create: `python/patterns/__init__.py`
- Create: `python/patterns/two_pointer.py`
- Create: `python/patterns/sliding_window.py`
- Create: `tests/patterns/__init__.py`
- Create: `tests/patterns/test_two_pointer.py`
- Create: `tests/patterns/test_sliding_window.py`

- [ ] **Step 1: Create __init__ files**

```python
# python/patterns/__init__.py
# tests/patterns/__init__.py
```

- [ ] **Step 2: Write two_pointer.py**

Create `python/patterns/two_pointer.py`:

```python
"""
Two-Pointer Pattern Problems
============================
Classic interview problems solved with the two-pointer technique.
All solutions: Time O(n) or O(n log n), Space O(1) unless noted.
"""
from typing import List


def two_sum_sorted(numbers: List[int], target: int) -> List[int]:
    """LeetCode 167. Two Sum II — Input Array Is Sorted.
    Returns 1-indexed [left, right] pair that sums to target.
    Time: O(n), Space: O(1)
    """
    left, right = 0, len(numbers) - 1
    while left < right:
        s = numbers[left] + numbers[right]
        if s == target:
            return [left + 1, right + 1]
        elif s < target:
            left += 1
        else:
            right -= 1
    return []


def remove_duplicates(nums: List[int]) -> int:
    """LeetCode 26. Remove Duplicates from Sorted Array.
    Returns new length; modifies nums in-place.
    Time: O(n), Space: O(1)
    """
    if not nums:
        return 0
    slow = 0
    for fast in range(1, len(nums)):
        if nums[fast] != nums[slow]:
            slow += 1
            nums[slow] = nums[fast]
    return slow + 1


def container_with_most_water(height: List[int]) -> int:
    """LeetCode 11. Container With Most Water.
    Time: O(n), Space: O(1)
    """
    left, right = 0, len(height) - 1
    max_area = 0
    while left < right:
        area = min(height[left], height[right]) * (right - left)
        max_area = max(max_area, area)
        if height[left] < height[right]:
            left += 1
        else:
            right -= 1
    return max_area


def three_sum(nums: List[int]) -> List[List[int]]:
    """LeetCode 15. 3Sum — find all unique triplets summing to zero.
    Time: O(n^2), Space: O(1) output excluded
    """
    nums.sort()
    result = []
    for i in range(len(nums) - 2):
        if i > 0 and nums[i] == nums[i - 1]:
            continue
        left, right = i + 1, len(nums) - 1
        while left < right:
            s = nums[i] + nums[left] + nums[right]
            if s == 0:
                result.append([nums[i], nums[left], nums[right]])
                while left < right and nums[left] == nums[left + 1]:
                    left += 1
                while left < right and nums[right] == nums[right - 1]:
                    right -= 1
                left += 1
                right -= 1
            elif s < 0:
                left += 1
            else:
                right -= 1
    return result


def is_palindrome(s: str) -> bool:
    """LeetCode 125. Valid Palindrome (alphanumeric only, case-insensitive).
    Time: O(n), Space: O(1)
    """
    left, right = 0, len(s) - 1
    while left < right:
        while left < right and not s[left].isalnum():
            left += 1
        while left < right and not s[right].isalnum():
            right -= 1
        if s[left].lower() != s[right].lower():
            return False
        left += 1
        right -= 1
    return True


def sort_colors(nums: List[int]) -> None:
    """LeetCode 75. Sort Colors — Dutch National Flag.
    Sort 0s, 1s, 2s in-place using three pointers.
    Time: O(n), Space: O(1)
    """
    low, mid, high = 0, 0, len(nums) - 1
    while mid <= high:
        if nums[mid] == 0:
            nums[low], nums[mid] = nums[mid], nums[low]
            low += 1
            mid += 1
        elif nums[mid] == 1:
            mid += 1
        else:
            nums[mid], nums[high] = nums[high], nums[mid]
            high -= 1


def trap_rain_water(height: List[int]) -> int:
    """LeetCode 42. Trapping Rain Water.
    Time: O(n), Space: O(1)
    """
    left, right = 0, len(height) - 1
    left_max = right_max = 0
    water = 0
    while left < right:
        if height[left] < height[right]:
            if height[left] >= left_max:
                left_max = height[left]
            else:
                water += left_max - height[left]
            left += 1
        else:
            if height[right] >= right_max:
                right_max = height[right]
            else:
                water += right_max - height[right]
            right -= 1
    return water


def move_zeroes(nums: List[int]) -> None:
    """LeetCode 283. Move Zeroes — maintain relative order of non-zeros.
    Time: O(n), Space: O(1)
    """
    slow = 0
    for fast in range(len(nums)):
        if nums[fast] != 0:
            nums[slow], nums[fast] = nums[fast], nums[slow]
            slow += 1


def squares_of_sorted_array(nums: List[int]) -> List[int]:
    """LeetCode 977. Squares of a Sorted Array.
    Time: O(n), Space: O(n)
    """
    n = len(nums)
    result = [0] * n
    left, right = 0, n - 1
    pos = n - 1
    while left <= right:
        if abs(nums[left]) > abs(nums[right]):
            result[pos] = nums[left] ** 2
            left += 1
        else:
            result[pos] = nums[right] ** 2
            right -= 1
        pos -= 1
    return result


def remove_element(nums: List[int], val: int) -> int:
    """LeetCode 27. Remove Element in-place.
    Returns new length. Time: O(n), Space: O(1)
    """
    slow = 0
    for fast in range(len(nums)):
        if nums[fast] != val:
            nums[slow] = nums[fast]
            slow += 1
    return slow
```

- [ ] **Step 3: Write sliding_window.py**

Create `python/patterns/sliding_window.py`:

```python
"""
Sliding Window Pattern Problems
================================
Fixed-size and variable-size window problems.
"""
from typing import List
from collections import defaultdict, Counter


def max_subarray_sum_k(nums: List[int], k: int) -> int:
    """Maximum sum of any subarray of exactly length k.
    Time: O(n), Space: O(1)
    """
    window_sum = sum(nums[:k])
    max_sum = window_sum
    for i in range(k, len(nums)):
        window_sum += nums[i] - nums[i - k]
        max_sum = max(max_sum, window_sum)
    return max_sum


def length_of_longest_substring(s: str) -> int:
    """LeetCode 3. Longest Substring Without Repeating Characters.
    Time: O(n), Space: O(min(n,alphabet))
    """
    char_index: dict[str, int] = {}
    max_len = 0
    left = 0
    for right, ch in enumerate(s):
        if ch in char_index and char_index[ch] >= left:
            left = char_index[ch] + 1
        char_index[ch] = right
        max_len = max(max_len, right - left + 1)
    return max_len


def min_window_substring(s: str, t: str) -> str:
    """LeetCode 76. Minimum Window Substring.
    Time: O(|s| + |t|), Space: O(|s| + |t|)
    """
    if not t:
        return ""
    need = Counter(t)
    have: dict[str, int] = defaultdict(int)
    formed = 0
    required = len(need)
    left = 0
    best = (float("inf"), 0, 0)
    for right, ch in enumerate(s):
        have[ch] += 1
        if ch in need and have[ch] == need[ch]:
            formed += 1
        while formed == required:
            if right - left + 1 < best[0]:
                best = (right - left + 1, left, right)
            have[s[left]] -= 1
            if s[left] in need and have[s[left]] < need[s[left]]:
                formed -= 1
            left += 1
    return "" if best[0] == float("inf") else s[best[1]: best[2] + 1]


def longest_substring_k_distinct(s: str, k: int) -> int:
    """LeetCode 340. Longest Substring with At Most K Distinct Characters.
    Time: O(n), Space: O(k)
    """
    freq: dict[str, int] = defaultdict(int)
    left = max_len = 0
    for right, ch in enumerate(s):
        freq[ch] += 1
        while len(freq) > k:
            freq[s[left]] -= 1
            if freq[s[left]] == 0:
                del freq[s[left]]
            left += 1
        max_len = max(max_len, right - left + 1)
    return max_len


def max_consecutive_ones_iii(nums: List[int], k: int) -> int:
    """LeetCode 1004. Max Consecutive Ones III (flip at most k zeros).
    Time: O(n), Space: O(1)
    """
    left = zeros = max_len = 0
    for right in range(len(nums)):
        if nums[right] == 0:
            zeros += 1
        while zeros > k:
            if nums[left] == 0:
                zeros -= 1
            left += 1
        max_len = max(max_len, right - left + 1)
    return max_len


def permutation_in_string(s1: str, s2: str) -> bool:
    """LeetCode 567. Permutation in String.
    Returns True if any permutation of s1 is a substring of s2.
    Time: O(|s2|), Space: O(1)
    """
    if len(s1) > len(s2):
        return False
    need = Counter(s1)
    window = Counter(s2[:len(s1)])
    if window == need:
        return True
    for i in range(len(s1), len(s2)):
        add_ch = s2[i]
        remove_ch = s2[i - len(s1)]
        window[add_ch] += 1
        window[remove_ch] -= 1
        if window[remove_ch] == 0:
            del window[remove_ch]
        if window == need:
            return True
    return False


def find_all_anagrams(s: str, p: str) -> List[int]:
    """LeetCode 438. Find All Anagrams in a String.
    Returns start indices of all anagram substrings.
    Time: O(|s|), Space: O(1)
    """
    result = []
    need = Counter(p)
    window = Counter(s[:len(p)])
    if window == need:
        result.append(0)
    for i in range(len(p), len(s)):
        window[s[i]] += 1
        old_ch = s[i - len(p)]
        window[old_ch] -= 1
        if window[old_ch] == 0:
            del window[old_ch]
        if window == need:
            result.append(i - len(p) + 1)
    return result


def subarray_product_less_than_k(nums: List[int], k: int) -> int:
    """LeetCode 713. Subarray Product Less Than K.
    Count subarrays with product strictly less than k.
    Time: O(n), Space: O(1)
    """
    if k <= 1:
        return 0
    product = 1
    left = count = 0
    for right in range(len(nums)):
        product *= nums[right]
        while product >= k:
            product //= nums[left]
            left += 1
        count += right - left + 1
    return count


def longest_repeating_char_replacement(s: str, k: int) -> int:
    """LeetCode 424. Longest Repeating Character Replacement.
    Time: O(n), Space: O(1)
    """
    freq: dict[str, int] = defaultdict(int)
    max_freq = left = max_len = 0
    for right, ch in enumerate(s):
        freq[ch] += 1
        max_freq = max(max_freq, freq[ch])
        window_size = right - left + 1
        if window_size - max_freq > k:
            freq[s[left]] -= 1
            left += 1
        max_len = max(max_len, right - left + 1)
    return max_len
```

- [ ] **Step 4: Write test_two_pointer.py**

Create `tests/patterns/test_two_pointer.py`:

```python
import pytest
from python.patterns.two_pointer import (
    two_sum_sorted, remove_duplicates, container_with_most_water,
    three_sum, is_palindrome, sort_colors, trap_rain_water,
    move_zeroes, squares_of_sorted_array, remove_element
)


def test_two_sum_sorted():
    assert two_sum_sorted([2, 7, 11, 15], 9) == [1, 2]
    assert two_sum_sorted([2, 3, 4], 6) == [1, 3]


def test_remove_duplicates():
    nums = [1, 1, 2, 3, 3]
    assert remove_duplicates(nums) == 3
    assert nums[:3] == [1, 2, 3]


def test_remove_duplicates_empty():
    assert remove_duplicates([]) == 0


def test_container_with_most_water():
    assert container_with_most_water([1, 8, 6, 2, 5, 4, 8, 3, 7]) == 49
    assert container_with_most_water([1, 1]) == 1


def test_three_sum():
    result = three_sum([-1, 0, 1, 2, -1, -4])
    assert sorted([sorted(t) for t in result]) == [[-1, -1, 2], [-1, 0, 1]]


def test_three_sum_no_result():
    assert three_sum([1, 2, 3]) == []


def test_is_palindrome():
    assert is_palindrome("A man, a plan, a canal: Panama") is True
    assert is_palindrome("race a car") is False
    assert is_palindrome(" ") is True


def test_sort_colors():
    nums = [2, 0, 2, 1, 1, 0]
    sort_colors(nums)
    assert nums == [0, 0, 1, 1, 2, 2]


def test_trap_rain_water():
    assert trap_rain_water([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]) == 6
    assert trap_rain_water([4, 2, 0, 3, 2, 5]) == 9
    assert trap_rain_water([]) == 0


def test_move_zeroes():
    nums = [0, 1, 0, 3, 12]
    move_zeroes(nums)
    assert nums == [1, 3, 12, 0, 0]


def test_squares_of_sorted_array():
    assert squares_of_sorted_array([-4, -1, 0, 3, 10]) == [0, 1, 9, 16, 100]
    assert squares_of_sorted_array([-7, -3, 2, 3, 11]) == [4, 9, 9, 49, 121]


def test_remove_element():
    nums = [3, 2, 2, 3]
    assert remove_element(nums, 3) == 2
    assert nums[:2] == [2, 2]
```

- [ ] **Step 5: Write test_sliding_window.py**

Create `tests/patterns/test_sliding_window.py`:

```python
import pytest
from python.patterns.sliding_window import (
    max_subarray_sum_k, length_of_longest_substring,
    min_window_substring, longest_substring_k_distinct,
    max_consecutive_ones_iii, permutation_in_string,
    find_all_anagrams, subarray_product_less_than_k,
    longest_repeating_char_replacement
)


def test_max_subarray_sum_k():
    assert max_subarray_sum_k([2, 1, 5, 1, 3, 2], 3) == 9
    assert max_subarray_sum_k([2, 3, 4, 1, 5], 2) == 7


def test_length_of_longest_substring():
    assert length_of_longest_substring("abcabcbb") == 3
    assert length_of_longest_substring("bbbbb") == 1
    assert length_of_longest_substring("pwwkew") == 3
    assert length_of_longest_substring("") == 0


def test_min_window_substring():
    assert min_window_substring("ADOBECODEBANC", "ABC") == "BANC"
    assert min_window_substring("a", "a") == "a"
    assert min_window_substring("a", "aa") == ""


def test_longest_substring_k_distinct():
    assert longest_substring_k_distinct("eceba", 2) == 3
    assert longest_substring_k_distinct("aa", 1) == 2


def test_max_consecutive_ones_iii():
    assert max_consecutive_ones_iii([1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0], 2) == 6
    assert max_consecutive_ones_iii([0, 0, 1, 1, 0, 0, 1, 1, 1, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1], 3) == 10


def test_permutation_in_string():
    assert permutation_in_string("ab", "eidbaooo") is True
    assert permutation_in_string("ab", "eidboaoo") is False


def test_find_all_anagrams():
    assert find_all_anagrams("cbaebabacd", "abc") == [0, 6]
    assert find_all_anagrams("abab", "ab") == [0, 1, 2]


def test_subarray_product_less_than_k():
    assert subarray_product_less_than_k([10, 5, 2, 6], 100) == 8
    assert subarray_product_less_than_k([1, 2, 3], 0) == 0


def test_longest_repeating_char_replacement():
    assert longest_repeating_char_replacement("ABAB", 2) == 4
    assert longest_repeating_char_replacement("AABABBA", 1) == 4
```

- [ ] **Step 6: Run pattern tests**

```bash
cd /home/sbisw/github/datastructures
pytest tests/patterns/test_two_pointer.py tests/patterns/test_sliding_window.py -v
```

Expected: All tests PASS.

- [ ] **Step 7: Commit**

```bash
git add python/patterns/ tests/patterns/test_two_pointer.py tests/patterns/test_sliding_window.py
git commit -m "feat: add two-pointer (10 problems) and sliding window (9 problems) pattern modules with tests"
```

---

## Task 7: Binary search, monotonic stack, and prefix sum patterns

**Files:**
- Create: `python/patterns/binary_search.py`
- Create: `python/patterns/monotonic_stack.py`
- Create: `python/patterns/prefix_sum.py`
- Create: `tests/patterns/test_binary_search.py`
- Create: `tests/patterns/test_monotonic_stack.py`
- Create: `tests/patterns/test_prefix_sum.py`

- [ ] **Step 1: Write binary_search.py**

Create `python/patterns/binary_search.py`:

```python
"""
Binary Search Pattern Problems
================================
All problems exploit the sorted/monotone property for O(log n) search.
"""
from typing import List


def search_in_rotated_sorted_array(nums: List[int], target: int) -> int:
    """LeetCode 33. Search in Rotated Sorted Array.
    Time: O(log n), Space: O(1)
    """
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = (left + right) // 2
        if nums[mid] == target:
            return mid
        if nums[left] <= nums[mid]:
            if nums[left] <= target < nums[mid]:
                right = mid - 1
            else:
                left = mid + 1
        else:
            if nums[mid] < target <= nums[right]:
                left = mid + 1
            else:
                right = mid - 1
    return -1


def find_minimum_in_rotated_sorted_array(nums: List[int]) -> int:
    """LeetCode 153. Find Minimum in Rotated Sorted Array.
    Time: O(log n), Space: O(1)
    """
    left, right = 0, len(nums) - 1
    while left < right:
        mid = (left + right) // 2
        if nums[mid] > nums[right]:
            left = mid + 1
        else:
            right = mid
    return nums[left]


def find_first_and_last_position(nums: List[int], target: int) -> List[int]:
    """LeetCode 34. Find First and Last Position of Element in Sorted Array.
    Time: O(log n), Space: O(1)
    """
    def find_bound(is_first: bool) -> int:
        left, right = 0, len(nums) - 1
        bound = -1
        while left <= right:
            mid = (left + right) // 2
            if nums[mid] == target:
                bound = mid
                if is_first:
                    right = mid - 1
                else:
                    left = mid + 1
            elif nums[mid] < target:
                left = mid + 1
            else:
                right = mid - 1
        return bound

    return [find_bound(True), find_bound(False)]


def search_a_2d_matrix(matrix: List[List[int]], target: int) -> bool:
    """LeetCode 74. Search a 2D Matrix (sorted rows, first of each row > last of prev).
    Time: O(log(m*n)), Space: O(1)
    """
    if not matrix or not matrix[0]:
        return False
    m, n = len(matrix), len(matrix[0])
    left, right = 0, m * n - 1
    while left <= right:
        mid = (left + right) // 2
        val = matrix[mid // n][mid % n]
        if val == target:
            return True
        elif val < target:
            left = mid + 1
        else:
            right = mid - 1
    return False


def koko_eating_bananas(piles: List[int], h: int) -> int:
    """LeetCode 875. Koko Eating Bananas — find minimum eating speed.
    Binary search on the answer space.
    Time: O(n log max_pile), Space: O(1)
    """
    import math
    left, right = 1, max(piles)
    while left < right:
        mid = (left + right) // 2
        hours = sum(math.ceil(p / mid) for p in piles)
        if hours <= h:
            right = mid
        else:
            left = mid + 1
    return left


def capacity_to_ship_packages(weights: List[int], days: int) -> int:
    """LeetCode 1011. Capacity To Ship Packages Within D Days.
    Binary search on capacity.
    Time: O(n log(sum(weights))), Space: O(1)
    """
    def can_ship(capacity: int) -> bool:
        day_count, current = 1, 0
        for w in weights:
            if current + w > capacity:
                day_count += 1
                current = 0
            current += w
        return day_count <= days

    left, right = max(weights), sum(weights)
    while left < right:
        mid = (left + right) // 2
        if can_ship(mid):
            right = mid
        else:
            left = mid + 1
    return left


def peak_element(nums: List[int]) -> int:
    """LeetCode 162. Find Peak Element (nums[-1] = nums[n] = -inf).
    Time: O(log n), Space: O(1)
    """
    left, right = 0, len(nums) - 1
    while left < right:
        mid = (left + right) // 2
        if nums[mid] < nums[mid + 1]:
            left = mid + 1
        else:
            right = mid
    return left


def sqrt_floor(x: int) -> int:
    """LeetCode 69. Sqrt(x) — return floor of square root.
    Time: O(log x), Space: O(1)
    """
    if x < 2:
        return x
    left, right = 1, x // 2
    while left <= right:
        mid = (left + right) // 2
        if mid * mid == x:
            return mid
        elif mid * mid < x:
            left = mid + 1
        else:
            right = mid - 1
    return right
```

- [ ] **Step 2: Write monotonic_stack.py**

Create `python/patterns/monotonic_stack.py`:

```python
"""
Monotonic Stack Pattern Problems
==================================
A monotonic stack maintains elements in increasing or decreasing order.
Typical use: next/previous greater/smaller element, histogram area.
"""
from typing import List


def next_greater_element(nums: List[int]) -> List[int]:
    """LeetCode 496 variant. For each element, find next greater to its right.
    Returns -1 if none exists. Time: O(n), Space: O(n)
    """
    result = [-1] * len(nums)
    stack: List[int] = []  # stores indices
    for i, val in enumerate(nums):
        while stack and nums[stack[-1]] < val:
            idx = stack.pop()
            result[idx] = val
        stack.append(i)
    return result


def daily_temperatures(temperatures: List[int]) -> List[int]:
    """LeetCode 739. Daily Temperatures.
    Returns how many days until a warmer temperature.
    Time: O(n), Space: O(n)
    """
    result = [0] * len(temperatures)
    stack: List[int] = []  # stores indices
    for i, temp in enumerate(temperatures):
        while stack and temperatures[stack[-1]] < temp:
            idx = stack.pop()
            result[idx] = i - idx
        stack.append(i)
    return result


def largest_rectangle_in_histogram(heights: List[int]) -> int:
    """LeetCode 84. Largest Rectangle in Histogram.
    Time: O(n), Space: O(n)
    """
    stack: List[int] = []
    max_area = 0
    for i, h in enumerate(heights + [0]):
        while stack and heights[stack[-1]] > h:
            height = heights[stack.pop()]
            width = i if not stack else i - stack[-1] - 1
            max_area = max(max_area, height * width)
        stack.append(i)
    return max_area


def trapping_rain_water_stack(height: List[int]) -> int:
    """LeetCode 42. Trapping Rain Water (monotonic stack approach).
    Time: O(n), Space: O(n)
    """
    stack: List[int] = []
    water = 0
    for i, h in enumerate(height):
        while stack and height[stack[-1]] < h:
            bottom = stack.pop()
            if not stack:
                break
            left = stack[-1]
            width = i - left - 1
            bounded_height = min(height[left], h) - height[bottom]
            water += width * bounded_height
        stack.append(i)
    return water


def remove_k_digits(num: str, k: int) -> str:
    """LeetCode 402. Remove K Digits to form smallest number.
    Time: O(n), Space: O(n)
    """
    stack: List[str] = []
    for digit in num:
        while k and stack and stack[-1] > digit:
            stack.pop()
            k -= 1
        stack.append(digit)
    stack = stack[:-k] if k else stack
    return "".join(stack).lstrip("0") or "0"


def asteroid_collision(asteroids: List[int]) -> List[int]:
    """LeetCode 735. Asteroid Collision.
    Positive = right, negative = left. Equal size both explode.
    Time: O(n), Space: O(n)
    """
    stack: List[int] = []
    for a in asteroids:
        alive = True
        while alive and a < 0 and stack and stack[-1] > 0:
            if stack[-1] < -a:
                stack.pop()
            elif stack[-1] == -a:
                stack.pop()
                alive = False
            else:
                alive = False
        if alive:
            stack.append(a)
    return stack
```

- [ ] **Step 3: Write prefix_sum.py**

Create `python/patterns/prefix_sum.py`:

```python
"""
Prefix Sum / Range Query Pattern Problems
==========================================
Preprocessing the array for O(1) range queries.
"""
from typing import List


def subarray_sum_equals_k(nums: List[int], k: int) -> int:
    """LeetCode 560. Subarray Sum Equals K.
    Count subarrays that sum to k. Time: O(n), Space: O(n)
    """
    count = 0
    prefix_sum = 0
    freq: dict[int, int] = {0: 1}
    for num in nums:
        prefix_sum += num
        count += freq.get(prefix_sum - k, 0)
        freq[prefix_sum] = freq.get(prefix_sum, 0) + 1
    return count


def range_sum_query(nums: List[int]) -> "RangeSum":
    """LeetCode 303. Range Sum Query - Immutable."""
    class RangeSum:
        def __init__(self, nums: List[int]):
            self.prefix = [0] * (len(nums) + 1)
            for i, n in enumerate(nums):
                self.prefix[i + 1] = self.prefix[i] + n

        def sum_range(self, left: int, right: int) -> int:
            return self.prefix[right + 1] - self.prefix[left]

    return RangeSum(nums)


def product_of_array_except_self(nums: List[int]) -> List[int]:
    """LeetCode 238. Product of Array Except Self.
    Time: O(n), Space: O(1) output excluded
    """
    n = len(nums)
    result = [1] * n
    left_product = 1
    for i in range(n):
        result[i] = left_product
        left_product *= nums[i]
    right_product = 1
    for i in range(n - 1, -1, -1):
        result[i] *= right_product
        right_product *= nums[i]
    return result


def pivot_index(nums: List[int]) -> int:
    """LeetCode 724. Find Pivot Index.
    Return index where left sum == right sum. Returns -1 if none.
    Time: O(n), Space: O(1)
    """
    total = sum(nums)
    left_sum = 0
    for i, n in enumerate(nums):
        if left_sum == total - left_sum - n:
            return i
        left_sum += n
    return -1


def contiguous_array(nums: List[int]) -> int:
    """LeetCode 525. Contiguous Array.
    Find max length subarray with equal 0s and 1s.
    Time: O(n), Space: O(n)
    """
    prefix_map: dict[int, int] = {0: -1}
    count = max_len = 0
    for i, n in enumerate(nums):
        count += 1 if n == 1 else -1
        if count in prefix_map:
            max_len = max(max_len, i - prefix_map[count])
        else:
            prefix_map[count] = i
    return max_len


def minimum_size_subarray_sum(target: int, nums: List[int]) -> int:
    """LeetCode 209. Minimum Size Subarray Sum.
    Find minimum length subarray with sum >= target.
    Time: O(n), Space: O(1)
    """
    left = 0
    current_sum = 0
    min_len = float("inf")
    for right in range(len(nums)):
        current_sum += nums[right]
        while current_sum >= target:
            min_len = min(min_len, right - left + 1)
            current_sum -= nums[left]
            left += 1
    return 0 if min_len == float("inf") else min_len
```

- [ ] **Step 4: Write test_binary_search.py**

Create `tests/patterns/test_binary_search.py`:

```python
from python.patterns.binary_search import (
    search_in_rotated_sorted_array, find_minimum_in_rotated_sorted_array,
    find_first_and_last_position, search_a_2d_matrix,
    koko_eating_bananas, capacity_to_ship_packages,
    peak_element, sqrt_floor
)


def test_search_rotated():
    assert search_in_rotated_sorted_array([4, 5, 6, 7, 0, 1, 2], 0) == 4
    assert search_in_rotated_sorted_array([4, 5, 6, 7, 0, 1, 2], 3) == -1
    assert search_in_rotated_sorted_array([1], 0) == -1


def test_find_minimum_rotated():
    assert find_minimum_in_rotated_sorted_array([3, 4, 5, 1, 2]) == 1
    assert find_minimum_in_rotated_sorted_array([4, 5, 6, 7, 0, 1, 2]) == 0
    assert find_minimum_in_rotated_sorted_array([11, 13, 15, 17]) == 11


def test_find_first_and_last():
    assert find_first_and_last_position([5, 7, 7, 8, 8, 10], 8) == [3, 4]
    assert find_first_and_last_position([5, 7, 7, 8, 8, 10], 6) == [-1, -1]
    assert find_first_and_last_position([], 0) == [-1, -1]


def test_search_2d_matrix():
    m = [[1, 3, 5, 7], [10, 11, 16, 20], [23, 30, 34, 60]]
    assert search_a_2d_matrix(m, 3) is True
    assert search_a_2d_matrix(m, 13) is False


def test_koko_eating():
    assert koko_eating_bananas([3, 6, 7, 11], 8) == 4
    assert koko_eating_bananas([30, 11, 23, 4, 20], 5) == 30


def test_capacity_to_ship():
    assert capacity_to_ship_packages([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 5) == 15
    assert capacity_to_ship_packages([3, 2, 2, 4, 1, 4], 3) == 6


def test_peak_element():
    idx = peak_element([1, 2, 3, 1])
    assert idx == 2
    idx = peak_element([1, 2, 1, 3, 5, 6, 4])
    assert idx in (1, 5)


def test_sqrt_floor():
    assert sqrt_floor(4) == 2
    assert sqrt_floor(8) == 2
    assert sqrt_floor(0) == 0
    assert sqrt_floor(1) == 1
    assert sqrt_floor(9) == 3
```

- [ ] **Step 5: Write test_monotonic_stack.py**

Create `tests/patterns/test_monotonic_stack.py`:

```python
from python.patterns.monotonic_stack import (
    next_greater_element, daily_temperatures,
    largest_rectangle_in_histogram, trapping_rain_water_stack,
    remove_k_digits, asteroid_collision
)


def test_next_greater_element():
    assert next_greater_element([2, 1, 2, 4, 3]) == [4, 2, 4, -1, -1]
    assert next_greater_element([1, 2, 3]) == [2, 3, -1]


def test_daily_temperatures():
    assert daily_temperatures([73, 74, 75, 71, 69, 72, 76, 73]) == [1, 1, 4, 2, 1, 1, 0, 0]


def test_largest_rectangle():
    assert largest_rectangle_in_histogram([2, 1, 5, 6, 2, 3]) == 10
    assert largest_rectangle_in_histogram([2, 4]) == 4
    assert largest_rectangle_in_histogram([]) == 0


def test_trapping_rain_stack():
    assert trapping_rain_water_stack([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]) == 6
    assert trapping_rain_water_stack([4, 2, 0, 3, 2, 5]) == 9


def test_remove_k_digits():
    assert remove_k_digits("1432219", 3) == "1219"
    assert remove_k_digits("10200", 1) == "200"
    assert remove_k_digits("10", 2) == "0"


def test_asteroid_collision():
    assert asteroid_collision([5, 10, -5]) == [5, 10]
    assert asteroid_collision([8, -8]) == []
    assert asteroid_collision([10, 2, -5]) == [10]
    assert asteroid_collision([-2, -1, 1, 2]) == [-2, -1, 1, 2]
```

- [ ] **Step 6: Write test_prefix_sum.py**

Create `tests/patterns/test_prefix_sum.py`:

```python
from python.patterns.prefix_sum import (
    subarray_sum_equals_k, range_sum_query,
    product_of_array_except_self, pivot_index,
    contiguous_array, minimum_size_subarray_sum
)


def test_subarray_sum_equals_k():
    assert subarray_sum_equals_k([1, 1, 1], 2) == 2
    assert subarray_sum_equals_k([1, 2, 3], 3) == 2
    assert subarray_sum_equals_k([1], 0) == 0


def test_range_sum_query():
    rs = range_sum_query([-2, 0, 3, -5, 2, -1])
    assert rs.sum_range(0, 2) == 1
    assert rs.sum_range(2, 5) == -1
    assert rs.sum_range(0, 5) == -3


def test_product_except_self():
    assert product_of_array_except_self([1, 2, 3, 4]) == [24, 12, 8, 6]
    assert product_of_array_except_self([-1, 1, 0, -3, 3]) == [0, 0, 9, 0, 0]


def test_pivot_index():
    assert pivot_index([1, 7, 3, 6, 5, 6]) == 3
    assert pivot_index([1, 2, 3]) == -1
    assert pivot_index([2, 1, -1]) == 0


def test_contiguous_array():
    assert contiguous_array([0, 1]) == 2
    assert contiguous_array([0, 1, 0]) == 2
    assert contiguous_array([0, 0, 0, 1, 1, 1, 0]) == 6


def test_minimum_size_subarray_sum():
    assert minimum_size_subarray_sum(7, [2, 3, 1, 2, 4, 3]) == 2
    assert minimum_size_subarray_sum(4, [1, 4, 4]) == 1
    assert minimum_size_subarray_sum(11, [1, 1, 1, 1, 1, 1, 1, 1]) == 0
```

- [ ] **Step 7: Run all pattern tests**

```bash
cd /home/sbisw/github/datastructures
pytest tests/patterns/ -v
```

Expected: All tests PASS.

- [ ] **Step 8: Commit**

```bash
git add python/patterns/binary_search.py python/patterns/monotonic_stack.py python/patterns/prefix_sum.py tests/patterns/
git commit -m "feat: add binary search (8), monotonic stack (6), prefix sum (6) pattern modules with tests"
```

---

## Task 8: Full test suite run and README update

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Run the full test suite**

```bash
cd /home/sbisw/github/datastructures
pytest --tb=short -q
```

Expected: All tests pass. Fix any failures by inspecting actual function signatures and adjusting test imports.

- [ ] **Step 2: Update README.md test coverage section**

In `README.md`, find the `| Component | Coverage | Status |` table and update the "Code Examples" row:

```markdown
| **Code Examples** | Python + Java implementations + 39 pattern problems | ✅ Complete |
| **Test Suite** | pytest — basic DS, algorithms, 39 pattern problems (~200 tests) | ✅ Complete |
```

- [ ] **Step 3: Final commit**

```bash
git add README.md
git commit -m "docs: update README to reflect new test suite and pattern problems"
```

---

## Self-Review Checklist

**Spec coverage:**
- [x] Fix broken sys.path imports → Task 1
- [x] Fix malformed docstrings in source and tests → Task 2
- [x] Tests for basic DS (linked_list, stack, queue, hashmap) → Task 3
- [x] Tests for sorting (8 algorithms) and searching → Task 4
- [x] Tests for DP and graph algorithms → Task 5
- [x] Two-pointer problems (10) + sliding window (9) → Task 6
- [x] Binary search (8) + monotonic stack (6) + prefix sum (6) → Task 7
- [x] Full suite run + README → Task 8

**Placeholder scan:** No TBD or "implement later" found.

**Type consistency:** All function names used in tests match definitions in pattern files.
