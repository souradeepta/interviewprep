import sys
sys.path.insert(0, '/home/sbisw/github/datastructures/python/algorithms/graph')

from graph_algorithms import TreeNode, lca, path_sum, all_paths_sum, tree_diameter, \
    rob_tree, build_tree_preorder_inorder, serialize_tree, deserialize_tree, \
    count_islands, is_bipartite, has_cycle_directed, has_cycle_undirected

def test_lca():
    """Test Lowest Common Ancestor."""
    root = TreeNode(3)
    root.left = TreeNode(5)
    root.right = TreeNode(1)
    root.left.left = TreeNode(6)
    root.left.right = TreeNode(2)

    p, q = root.left, root.right  # 5, 1
    result = lca(root, p, q)
    assert result.val == 3

def test_path_sum():
    """Test path sum verification."""
    root = TreeNode(5)
    root.left = TreeNode(4)
    root.right = TreeNode(8)
    root.left.left = TreeNode(11)
    root.left.left.left = TreeNode(7)
    root.left.left.right = TreeNode(2)

    assert path_sum(root, 22) == True
    assert path_sum(root, 100) == False

def test_all_paths_sum():
    """Test all root-to-leaf paths."""
    root = TreeNode(1)
    root.left = TreeNode(2)
    root.right = TreeNode(3)

    paths = all_paths_sum(root)
    assert len(paths) == 2

def test_tree_diameter():
    """Test tree diameter (longest path)."""
    root = TreeNode(1)
    root.left = TreeNode(2)
    root.left.left = TreeNode(4)
    root.left.right = TreeNode(5)
    root.right = TreeNode(3)

    assert tree_diameter(root) == 3

def test_rob_tree():
    """Test house robber on tree."""
    root = TreeNode(3)
    root.left = TreeNode(2)
    root.right = TreeNode(3)
    root.left.right = TreeNode(3)
    root.right.right = TreeNode(1)

    assert rob_tree(root) == 7

def test_serialize_deserialize():
    """Test tree serialization."""
    root = TreeNode(1)
    root.left = TreeNode(2)
    root.right = TreeNode(3)

    serialized = serialize_tree(root)
    deserialized = deserialize_tree(serialized)
    assert deserialized.val == 1
    assert deserialized.left.val == 2

def test_build_tree():
    """Test building tree from preorder and inorder."""
    preorder = [3, 9, 20, 15, 7]
    inorder = [9, 3, 15, 20, 7]
    root = build_tree_preorder_inorder(preorder, inorder)
    assert root.val == 3
    assert root.left.val == 9
    assert root.right.val == 20

def test_count_islands():
    """Test island counting."""
    grid = [
        ['1', '1', '0', '0', '0'],
        ['1', '1', '0', '0', '0'],
        ['0', '0', '1', '0', '0'],
        ['0', '0', '0', '1', '1']
    ]
    assert count_islands(grid) == 3

def test_is_bipartite():
    """Test bipartite detection."""
    graph = [[1, 3], [0, 2], [1, 3], [0, 2]]
    assert is_bipartite(graph) == True

    graph_not_bip = [[1, 2, 3], [0, 2], [0, 1, 3], [0, 2]]
    assert is_bipartite(graph_not_bip) == False

def test_has_cycle_directed():
    """Test cycle detection in directed graph."""
    graph_acyclic = [[1, 2], [3], [], []]
    assert has_cycle_directed(graph_acyclic) == False

    graph_cyclic = [[1], [2], [0]]
    assert has_cycle_directed(graph_cyclic) == True

def test_has_cycle_undirected():
    """Test cycle detection in undirected graph."""
    n = 4
    edges_acyclic = [[0, 1], [1, 2], [2, 3]]
    assert has_cycle_undirected(n, edges_acyclic) == False

    edges_cyclic = [[0, 1], [1, 2], [2, 3], [3, 0]]
    assert has_cycle_undirected(n, edges_cyclic) == True

if __name__ == "__main__":
    test_lca()
    test_path_sum()
    test_all_paths_sum()
    test_tree_diameter()
    test_rob_tree()
    test_serialize_deserialize()
    test_build_tree()
    test_count_islands()
    test_is_bipartite()
    test_has_cycle_directed()
    test_has_cycle_undirected()
    print("✓ All tree DP and graph traversal tests pass")
