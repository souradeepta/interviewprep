# Tree Problems

## BST Search/Insert/Delete
**When to use:** Ordered set operations, range queries, self-balancing needed

**Best DS:** Binary Search Tree, AVL Tree, Red-Black Tree

**Key Algorithms:** In-order traversal for sorted, search left/right, delete with 0/1/2 children

**Example Problems:**
1. "Kth smallest element in BST" → In-order traversal, return kth element. Your repo: `python/advanced/bst.py`. Time: O(n)
2. "Validate BST" → In-order traversal should be increasing. Time: O(n)

---

## Tree Traversal (In/Pre/Post/Level)
**When to use:** Different processing orders depending on child-parent dependency

**Best DS:** Recursion, Explicit stack/queue

**Key Algorithms:** Inorder (left, process, right), Preorder (process, left, right), Postorder (left, right, process)

**Example Problems:**
1. "Binary tree inorder traversal" → Recursive helper or explicit stack. Your repo: `python/advanced/bst.py`. Time: O(n)
2. "Binary tree level order traversal" → Queue-based BFS. Time: O(n)

---

## LCA (Lowest Common Ancestor)
**When to use:** Finding deepest common ancestor, path-related queries

**Best DS:** BST, General tree

**Key Algorithms:** BST LCA (go left/right based on values), General tree LCA (DFS to find paths)

**Example Problems:**
1. "LCA of binary search tree" → If both p, q < node, go left; if both > node, go right; else node is LCA. Your repo: `python/advanced/bst.py`. Time: O(h)
2. "LCA of binary tree" → Recursively find in left/right; if both exist, current is LCA. Time: O(n)

---

## Subtree Problems
**When to use:** Comparing subtrees, matching patterns within tree, aggregating by subtree

**Best DS:** Tree, Recursion

**Key Algorithms:** Post-order DFS, subtree encoding and hashing

**Example Problems:**
1. "Subtree of another tree" → For each node in main tree, check if subtree matches. Your repo: `python/advanced/bst.py`. Time: O(n × m)
2. "Maximum path sum" → Post-order DFS; track max at each node. Time: O(n)

---

## Tree Serialization/Deserialization
**When to use:** Persistence, transmission, compression

**Best DS:** String, Tree

**Key Algorithms:** Pre-order with null markers, level-order with null markers

**Example Problems:**
1. "Serialize and deserialize binary tree" → Pre-order with nulls, deserialize by reconstructing. Your repo: `python/advanced/bst.py`. Time: O(n)

---

See [Master Index](problem-to-pattern-matcher.md) for all 50+ patterns.
