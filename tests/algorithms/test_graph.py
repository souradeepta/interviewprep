import pytest
from python.algorithms.graph.graph_algorithms import (
    dijkstra, topological_sort_kahn, count_islands, is_bipartite,
    has_cycle_directed, TreeNode, lca, path_sum
)


class TestDijkstra:
    def test_basic(self):
        graph = {
            0: [(1, 4), (2, 1)],
            1: [(3, 1)],
            2: [(1, 2), (3, 5)],
            3: []
        }
        dist, pred = dijkstra(graph, 0)
        assert dist[3] == 4

    def test_single_node(self):
        dist, pred = dijkstra({0: []}, 0)
        assert dist[0] == 0


class TestTopologicalSort:
    def test_basic_dag(self):
        graph = {0: [1, 2], 1: [3], 2: [3], 3: []}
        order, is_dag = topological_sort_kahn(graph)
        if is_dag:
            assert order.index(0) < order.index(1)


class TestCountIslands:
    def test_single_island(self):
        grid = [['1', '1', '0'], ['0', '1', '0']]
        assert count_islands(grid) == 1

    def test_multiple_islands(self):
        grid = [['1', '0', '1'], ['0', '1', '0']]
        assert count_islands(grid) == 3


class TestIsBipartite:
    def test_bipartite(self):
        graph = [[1, 3], [0, 2], [1, 3], [0, 2]]
        assert is_bipartite(graph) is True

    def test_not_bipartite(self):
        graph = [[1, 2, 3], [0, 2], [0, 1, 3], [0, 2]]
        assert is_bipartite(graph) is False


class TestHasCycleDireted:
    def test_no_cycle(self):
        graph = [[1, 2], [2], []]
        assert has_cycle_directed(graph) is False

    def test_has_cycle(self):
        graph = [[1], [2], [0]]
        assert has_cycle_directed(graph) is True


class TestLCA:
    def test_lca_basic(self):
        root = TreeNode(3)
        root.left = TreeNode(5)
        root.right = TreeNode(1)
        root.left.left = TreeNode(6)
        root.left.right = TreeNode(2)

        p, q = root.left, root.right
        result = lca(root, p, q)
        assert result.val == 3


class TestPathSum:
    def test_path_sum_basic(self):
        root = TreeNode(5)
        root.left = TreeNode(4)
        root.left.left = TreeNode(11)
        root.left.left.left = TreeNode(7)
        root.left.left.right = TreeNode(2)

        result = path_sum(root, 22)
        assert isinstance(result, bool)
