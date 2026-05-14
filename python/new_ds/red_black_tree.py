"""
Red-Black Tree
==============
A self-balancing binary search tree where every node carries a color bit
(RED or BLACK). The five invariants guarantee O(log n) height:

  1. Every node is RED or BLACK.
  2. The root is BLACK.
  3. Every leaf (NIL sentinel) is BLACK.
  4. If a node is RED, both its children are BLACK (no two consecutive reds).
  5. For each node, all simple paths from that node to descendant leaves
     contain the same number of BLACK nodes (black-height is uniform).

Time Complexity
---------------
| Operation          | Average   | Worst    |
|--------------------|-----------|----------|
| search             | O(log n)  | O(log n) |
| insert             | O(log n)  | O(log n) |
| delete             | O(log n)  | O(log n) |
| inorder traversal  | O(n)      | O(n)     |

Space Complexity
----------------
O(n) for storage; O(log n) call-stack for recursive operations.

Design notes
------------
- A single shared NIL sentinel replaces all leaf-null pointers.  Its color
  is always BLACK (satisfies invariant 3 automatically).
- Rotations restructure the tree in O(1) without violating the BST property.
- Insert fixup handles 3 cases (and their mirrors) to restore invariant 4.
- Delete fixup handles 4 cases (and their mirrors) to restore invariant 5.
"""

from typing import Any, List, Optional

RED = "R"
BLACK = "B"


class RBNode:
    """
    A node in the Red-Black Tree.

    Attributes
    ----------
    key    : Comparable key.
    val    : Satellite data.
    color  : RED ('R') or BLACK ('B').
    left   : Left child (RBNode or NIL sentinel).
    right  : Right child (RBNode or NIL sentinel).
    parent : Parent node (RBNode or NIL sentinel; root's parent == NIL).
    """

    __slots__ = ("key", "val", "color", "left", "right", "parent")

    def __init__(self, key: Any, val: Any, color: str = RED) -> None:
        self.key = key
        self.val = val
        self.color = color
        self.left: "RBNode" = None   # type: ignore[assignment]
        self.right: "RBNode" = None  # type: ignore[assignment]
        self.parent: "RBNode" = None # type: ignore[assignment]

    def __repr__(self) -> str:
        return f"RBNode(key={self.key!r}, color={self.color})"


class RedBlackTree:
    """
    Red-Black Tree with insert, delete, and search.

    Uses a shared NIL sentinel for all leaf/null positions so that fixup
    routines never have to guard against None explicitly.

    Example
    -------
    >>> rbt = RedBlackTree()
    >>> for k in [10, 20, 30, 15, 25]:
    ...     rbt.insert(k, k)
    >>> rbt.search(15)
    15
    >>> rbt.inorder()
    [10, 15, 20, 25, 30]
    >>> rbt.delete(20)
    >>> rbt.inorder()
    [10, 15, 25, 30]
    """

    def __init__(self) -> None:
        # NIL sentinel: color BLACK, all pointers self-referential
        self.NIL = RBNode(key=None, val=None, color=BLACK)
        self.NIL.left = self.NIL
        self.NIL.right = self.NIL
        self.NIL.parent = self.NIL
        self.root: RBNode = self.NIL
        self.size: int = 0

    # ------------------------------------------------------------------
    # Rotations (O(1) pointer manipulations)
    # ------------------------------------------------------------------

    def _left_rotate(self, x: RBNode) -> None:
        """
        Left-rotate around node x.

             x                 y
            / \\     -->      / \\
           a   y            x   c
              / \\          / \\
             b   c        a   b
        """
        y = x.right
        x.right = y.left             # turn y's left subtree into x's right subtree

        if y.left is not self.NIL:
            y.left.parent = x

        y.parent = x.parent          # link y's parent to x's old parent

        if x.parent is self.NIL:
            self.root = y
        elif x is x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y

        y.left = x                   # place x on y's left
        x.parent = y

    def _right_rotate(self, y: RBNode) -> None:
        """
        Right-rotate around node y (symmetric to left-rotate).

             y                 x
            / \\     -->      / \\
           x   c            a   y
          / \\                  / \\
         a   b                b   c
        """
        x = y.left
        y.left = x.right

        if x.right is not self.NIL:
            x.right.parent = y

        x.parent = y.parent

        if y.parent is self.NIL:
            self.root = x
        elif y is y.parent.left:
            y.parent.left = x
        else:
            y.parent.right = x

        x.right = y
        y.parent = x

    # ------------------------------------------------------------------
    # Insert
    # ------------------------------------------------------------------

    def insert(self, key: Any, val: Any) -> None:
        """
        Insert a key-value pair into the tree.

        Standard BST insert followed by _insert_fixup to restore RB properties.

        Time: O(log n)
        """
        # Check for duplicate: update value and return
        existing = self._search_node(key)
        if existing is not self.NIL:
            existing.val = val
            return

        z = RBNode(key=key, val=val, color=RED)
        z.left = self.NIL
        z.right = self.NIL
        z.parent = self.NIL

        # Standard BST insert to find position
        y: RBNode = self.NIL
        x: RBNode = self.root
        while x is not self.NIL:
            y = x
            if z.key < x.key:
                x = x.left
            else:
                x = x.right

        z.parent = y
        if y is self.NIL:
            self.root = z          # tree was empty
        elif z.key < y.key:
            y.left = z
        else:
            y.right = z

        self.size += 1
        self._insert_fixup(z)

    def _insert_fixup(self, z: RBNode) -> None:
        """
        Restore Red-Black properties after inserting node z (colored RED).

        Loop invariant: z is RED and at most one RB violation exists — the
        potential double-red between z and z.parent.

        Three cases when z.parent is a LEFT child (mirrored for RIGHT child):

        Case 1 — Uncle is RED:
            Recolor parent and uncle to BLACK, grandparent to RED.
            Move z up to grandparent and continue.

        Case 2 — Uncle is BLACK, z is a RIGHT child:
            Left-rotate on z.parent to transform into Case 3.

        Case 3 — Uncle is BLACK, z is a LEFT child:
            Recolor parent BLACK, grandparent RED, then right-rotate on
            grandparent. Loop terminates.
        """
        while z.parent.color == RED:
            if z.parent is z.parent.parent.left:
                # z's parent is a LEFT child
                uncle = z.parent.parent.right

                if uncle.color == RED:
                    # --- Case 1: uncle is RED — recolor, move z up ---
                    z.parent.color = BLACK
                    uncle.color = BLACK
                    z.parent.parent.color = RED
                    z = z.parent.parent  # move z up two levels

                else:
                    # Uncle is BLACK
                    if z is z.parent.right:
                        # --- Case 2: z is a RIGHT child — left-rotate to make it left ---
                        z = z.parent
                        self._left_rotate(z)
                    # --- Case 3: z is a LEFT child — recolor and right-rotate ---
                    z.parent.color = BLACK
                    z.parent.parent.color = RED
                    self._right_rotate(z.parent.parent)

            else:
                # z's parent is a RIGHT child (mirror of above)
                uncle = z.parent.parent.left

                if uncle.color == RED:
                    # --- Case 1 (mirror) ---
                    z.parent.color = BLACK
                    uncle.color = BLACK
                    z.parent.parent.color = RED
                    z = z.parent.parent

                else:
                    if z is z.parent.left:
                        # --- Case 2 (mirror) ---
                        z = z.parent
                        self._right_rotate(z)
                    # --- Case 3 (mirror) ---
                    z.parent.color = BLACK
                    z.parent.parent.color = RED
                    self._left_rotate(z.parent.parent)

        self.root.color = BLACK  # invariant 2: root is always BLACK

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------

    def delete(self, key: Any) -> bool:
        """
        Delete the node with the given key.

        Returns True if found and deleted, False if key absent.

        Time: O(log n)
        """
        z = self._search_node(key)
        if z is self.NIL:
            return False
        self._delete_node(z)
        self.size -= 1
        return True

    def _transplant(self, u: RBNode, v: RBNode) -> None:
        """Replace subtree rooted at u with subtree rooted at v."""
        if u.parent is self.NIL:
            self.root = v
        elif u is u.parent.left:
            u.parent.left = v
        else:
            u.parent.right = v
        v.parent = u.parent  # valid even when v is NIL (NIL.parent updated)

    def _delete_node(self, z: RBNode) -> None:
        """
        Core delete: splice out z, then fixup if a BLACK node was removed.

        y        = node actually removed or moved.
        x        = node that occupies y's original position afterwards.
        x_parent = saved parent of x (needed when x is NIL).
        """
        y = z
        y_original_color = y.color
        x_parent: RBNode

        if z.left is self.NIL:
            # z has no left child — replace with right child
            x = z.right
            x_parent = z.parent
            self._transplant(z, z.right)

        elif z.right is self.NIL:
            # z has no right child — replace with left child
            x = z.left
            x_parent = z.parent
            self._transplant(z, z.left)

        else:
            # z has two children — find in-order successor (leftmost in right subtree)
            y = self._minimum(z.right)
            y_original_color = y.color
            x = y.right
            x_parent = y  # default: x's parent is y

            if y.parent is z:
                # y is z's direct right child; x stays, x_parent is y
                x.parent = y  # keep NIL.parent valid
            else:
                x_parent = y.parent
                self._transplant(y, y.right)
                y.right = z.right
                y.right.parent = y

            self._transplant(z, y)
            y.left = z.left
            y.left.parent = y
            y.color = z.color

        # Fixup only needed when a BLACK node was removed (breaks black-height)
        if y_original_color == BLACK:
            self._delete_fixup(x, x_parent)

    def _delete_fixup(self, x: RBNode, x_parent: RBNode) -> None:
        """
        Restore Red-Black properties after removing a BLACK node.

        x carries an "extra BLACK" that must be pushed up or absorbed.

        Four cases when x is a LEFT child (mirrored for RIGHT child):

        Case 1 — Sibling w is RED:
            Recolor w BLACK, x.parent RED, left-rotate on x.parent.
            Converts to Case 2, 3, or 4.

        Case 2 — Sibling w is BLACK, both of w's children are BLACK:
            Recolor w RED, move extra BLACK up to x.parent.
            If x.parent was RED, color it BLACK and done (absorbed).

        Case 3 — Sibling w is BLACK, w's right child is BLACK, left child is RED:
            Recolor w RED, w.left BLACK, right-rotate on w.
            Converts to Case 4.

        Case 4 — Sibling w is BLACK, w's right child is RED:
            Recolor: w gets x.parent's color, x.parent and w.right go BLACK.
            Left-rotate on x.parent. Extra BLACK is absorbed. Done.
        """
        while x is not self.root and x.color == BLACK:
            if x is x_parent.left:
                w = x_parent.right  # sibling

                # --- Case 1: sibling is RED ---
                if w.color == RED:
                    w.color = BLACK
                    x_parent.color = RED
                    self._left_rotate(x_parent)
                    w = x_parent.right  # new sibling after rotation

                # Now w is BLACK
                if w.left.color == BLACK and w.right.color == BLACK:
                    # --- Case 2: both of w's children are BLACK ---
                    w.color = RED
                    x = x_parent
                    x_parent = x.parent
                else:
                    if w.right.color == BLACK:
                        # --- Case 3: w's right child is BLACK (left child is RED) ---
                        w.left.color = BLACK
                        w.color = RED
                        self._right_rotate(w)
                        w = x_parent.right

                    # --- Case 4: w's right child is RED ---
                    w.color = x_parent.color
                    x_parent.color = BLACK
                    w.right.color = BLACK
                    self._left_rotate(x_parent)
                    x = self.root  # done — break loop

            else:
                # Mirror: x is a RIGHT child
                w = x_parent.left

                # --- Case 1 (mirror) ---
                if w.color == RED:
                    w.color = BLACK
                    x_parent.color = RED
                    self._right_rotate(x_parent)
                    w = x_parent.left

                if w.right.color == BLACK and w.left.color == BLACK:
                    # --- Case 2 (mirror) ---
                    w.color = RED
                    x = x_parent
                    x_parent = x.parent
                else:
                    if w.left.color == BLACK:
                        # --- Case 3 (mirror) ---
                        w.right.color = BLACK
                        w.color = RED
                        self._left_rotate(w)
                        w = x_parent.left

                    # --- Case 4 (mirror) ---
                    w.color = x_parent.color
                    x_parent.color = BLACK
                    w.left.color = BLACK
                    self._right_rotate(x_parent)
                    x = self.root  # done

        x.color = BLACK  # absorb the extra BLACK

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def _search_node(self, key: Any) -> RBNode:
        """Return the RBNode with the given key, or NIL if not found."""
        current = self.root
        while current is not self.NIL:
            if key == current.key:
                return current
            elif key < current.key:
                current = current.left
            else:
                current = current.right
        return self.NIL

    def search(self, key: Any) -> Optional[Any]:
        """
        Search for a key and return its value, or None if absent.

        Time: O(log n)
        """
        node = self._search_node(key)
        return node.val if node is not self.NIL else None

    # ------------------------------------------------------------------
    # Traversal helpers
    # ------------------------------------------------------------------

    def _minimum(self, node: RBNode) -> RBNode:
        """Return the leftmost (minimum key) node in the subtree."""
        while node.left is not self.NIL:
            node = node.left
        return node

    def inorder(self) -> List[Any]:
        """
        Return all keys in sorted order via in-order traversal.

        Time: O(n)
        """
        result: List[Any] = []
        self._inorder_helper(self.root, result)
        return result

    def _inorder_helper(self, node: RBNode, result: List[Any]) -> None:
        if node is self.NIL:
            return
        self._inorder_helper(node.left, result)
        result.append(node.key)
        self._inorder_helper(node.right, result)

    # ------------------------------------------------------------------
    # Pretty print
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        """
        Display the tree structure with color labels (R/B) per node.

        Uses a sideways tree layout (right subtree at top).
        """
        if self.root is self.NIL:
            return "<empty tree>"
        lines: List[str] = []
        self._print_helper(self.root, "", True, lines)
        return "\n".join(lines)

    def _print_helper(self, node: RBNode, indent: str, last: bool, lines: List[str]) -> None:
        if node is self.NIL:
            return
        lines.append(indent + ("└── " if last else "├── ") + f"{node.key}({node.color})")
        child_indent = indent + ("    " if last else "│   ")
        children = []
        if node.right is not self.NIL:
            children.append((node.right, False))
        if node.left is not self.NIL:
            children.append((node.left, True))
        for i, (child, is_last) in enumerate(children):
            self._print_helper(child, child_indent, is_last, lines)

    def __len__(self) -> int:
        return self.size


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("RED-BLACK TREE DEMO")
    print("=" * 60)

    rbt = RedBlackTree()

    keys = [41, 38, 31, 12, 19, 8, 50, 45, 65, 60, 72]
    print(f"\nInserting keys: {keys}")
    for k in keys:
        rbt.insert(k, k * 10)

    print("\nTree structure (key(color)):")
    print(rbt)

    print(f"\nIn-order traversal (should be sorted): {rbt.inorder()}")
    print(f"Root: {rbt.root.key} (always BLACK: {rbt.root.color == 'B'})")
    print(f"Tree size: {len(rbt)}")

    # Search
    print(f"\nsearch(19) -> {rbt.search(19)}")
    print(f"search(99) -> {rbt.search(99)}  (not present)")

    # Update
    rbt.insert(19, 999)
    print(f"After insert(19, 999): search(19) -> {rbt.search(19)}")

    # Delete
    for del_key in [19, 38, 50]:
        success = rbt.delete(del_key)
        print(f"\ndelete({del_key}) -> {success}")

    print("\nTree after deletions:")
    print(rbt)
    print(f"In-order: {rbt.inorder()}")

    # Verify BST + RB properties
    def verify_rb(tree: RedBlackTree) -> bool:
        """Quick sanity check: root is BLACK and inorder is sorted."""
        if tree.root is tree.NIL:
            return True
        if tree.root.color != BLACK:
            return False
        keys = tree.inorder()
        return keys == sorted(keys)

    print(f"\nRB properties hold: {verify_rb(rbt)}")
    print("\nDone.")
