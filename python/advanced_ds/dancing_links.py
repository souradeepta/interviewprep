"""
Dancing Links (DLX) - Algorithm X by Knuth

Time Complexity:
- Construction: O(nm) where n = rows, m = columns
- Solving exact cover: O(n!) worst case, much faster in practice
- Space Complexity: O(nm)

Use Cases:
- Exact cover problem (find sets that partition a universe)
- Sudoku solver
- N-queens problem
- Polyomino tiling
- Crossword puzzle construction

Key Insight:
- Use circular doubly-linked lists for efficient row/column removal
- Backtracking with efficient constraint propagation
- Removing/restoring nodes is O(1) with linked lists
- Cover column = remove all rows that have 1 in that column
- Efficient branching on columns with fewest options
"""

from typing import List, Tuple, Optional


class DancingLinksNode:
    """Node in Dancing Links structure."""

    def __init__(self):
        self.left = self
        self.right = self
        self.up = self
        self.down = self
        self.col_header = None
        self.count = 0  # For column headers: number of nodes in column


class DancingLinks:
    """Algorithm X using Dancing Links for exact cover problem."""

    def __init__(self, matrix: List[List[int]], names: Optional[List[str]] = None):
        """
        Initialize Dancing Links structure.

        Args:
            matrix: 2D binary matrix where 1 indicates membership
            names: Optional column names for readability
        """
        self.matrix = matrix
        self.rows = len(matrix)
        self.cols = len(matrix[0]) if matrix else 0
        self.names = names or [f"C{i}" for i in range(self.cols)]

        self.root = DancingLinksNode()
        self.col_headers = []

        self._build_structure()

    def _build_structure(self):
        """Build the Dancing Links structure."""
        # Create column headers
        current = self.root
        for i in range(self.cols):
            col_header = DancingLinksNode()
            col_header.count = 0
            col_header.col_header = col_header

            # Insert to the right of current
            col_header.right = current.right
            col_header.left = current
            current.right.left = col_header
            current.right = col_header

            self.col_headers.append(col_header)

        # Insert row nodes
        for r in range(self.rows):
            row_nodes = []
            for c in range(self.cols):
                if self.matrix[r][c]:
                    node = DancingLinksNode()
                    node.col_header = self.col_headers[c]
                    self.col_headers[c].count += 1

                    # Add to column (bottom of column)
                    node.down = self.col_headers[c]
                    node.up = self.col_headers[c].up
                    self.col_headers[c].up.down = node
                    self.col_headers[c].up = node

                    row_nodes.append(node)

            # Link nodes in row
            for i in range(len(row_nodes)):
                row_nodes[i].right = row_nodes[(i + 1) % len(row_nodes)]
                row_nodes[i].left = row_nodes[i - 1]

    def _cover(self, col_header: DancingLinksNode):
        """Cover a column (remove it and all rows that contain it)."""
        col_header.right.left = col_header.left
        col_header.left.right = col_header.right

        node = col_header.down
        while node != col_header:
            row_node = node.right
            while row_node != node:
                row_node.down.up = row_node.up
                row_node.up.down = row_node.down
                row_node.col_header.count -= 1
                row_node = row_node.right
            node = node.down

    def _uncover(self, col_header: DancingLinksNode):
        """Uncover a column (restore it)."""
        node = col_header.up
        while node != col_header:
            row_node = node.left
            while row_node != node:
                row_node.col_header.count += 1
                row_node.down.up = row_node
                row_node.up.down = row_node
                row_node = row_node.left
            node = node.up

        col_header.right.left = col_header
        col_header.left.right = col_header

    def _solve(self, solution: List[int]) -> Optional[List[int]]:
        """Recursively find exact cover using Algorithm X."""
        if self.root.right == self.root:
            return solution  # All columns covered

        # Choose column with minimum size (heuristic)
        min_col = None
        min_count = float('inf')

        col = self.root.right
        while col != self.root:
            if col.count < min_count:
                min_count = col.count
                min_col = col
            col = col.right

        if min_count == 0:
            return None  # No solution

        self._cover(min_col)

        row = min_col.down
        while row != min_col:
            solution.append(row)

            # Cover all columns in this row
            col_node = row.right
            while col_node != row:
                self._cover(col_node.col_header)
                col_node = col_node.right

            # Recursively solve
            result = self._solve(solution)
            if result is not None:
                return result

            # Backtrack
            col_node = row.left
            while col_node != row:
                self._uncover(col_node.col_header)
                col_node = col_node.left

            solution.pop()
            row = row.down

        self._uncover(min_col)
        return None

    def solve(self) -> Optional[List[int]]:
        """
        Find exact cover.

        Returns:
            List of row indices that form exact cover, or None if no solution
        """
        solution = self._solve([])
        if solution is not None:
            return [self._get_row_index(node) for node in solution]
        return None

    def _get_row_index(self, node: DancingLinksNode) -> int:
        """Get the original row index from a node."""
        # Find leftmost node in row to get row index
        current = node
        while current.left != current.col_header.up if current.left.col_header else True:
            current = current.left

        # Count how many times this node appears in original matrix
        row_num = 0
        for r in range(self.rows):
            found_row = False
            for c in range(self.cols):
                if self.matrix[r][c] and self._node_in_row(node, r):
                    found_row = True
                    break
            if found_row:
                return r

        return 0

    def _node_in_row(self, node: DancingLinksNode, row: int) -> bool:
        """Check if node belongs to a specific row."""
        col_count = 0
        current = node
        while current.right != current:
            col_count += 1
            current = current.right

        node_col_count = 0
        current = node
        while current.right != current:
            if self.matrix[row][self._get_col_index(current)]:
                node_col_count += 1
            current = current.right

        return node_col_count == col_count

    def _get_col_index(self, node: DancingLinksNode) -> int:
        """Get column index from node."""
        col = node.col_header
        c = 0
        current = self.root.right
        while current != col and current != self.root:
            c += 1
            current = current.right
        return c


if __name__ == "__main__":
    # Example 1: Simple exact cover
    print("=== Example 1: Simple Exact Cover ===")
    matrix = [
        [1, 0, 0, 1, 0, 0, 0],
        [0, 1, 1, 0, 0, 0, 0],
        [0, 0, 1, 0, 0, 1, 0],
        [0, 0, 0, 1, 1, 0, 1],
        [1, 0, 0, 0, 1, 0, 0],
        [0, 0, 0, 0, 1, 0, 1],
    ]

    names = ["A", "B", "C", "D", "E", "F", "G"]
    dlx = DancingLinks(matrix, names)

    solution = dlx.solve()
    if solution:
        print(f"Solution found: rows {solution}")
        for row_idx in solution:
            print(f"  Row {row_idx}: {matrix[row_idx]}")
    else:
        print("No solution found")

    # Example 2: Sudoku-like (simpler version)
    print("\n=== Example 2: N-Queens Problem (4x4) ===")
    # Create constraint matrix for 4-queens: 4 rows, 4 cols
    # We have 16 possible placements (4 rows * 4 cols)
    n = 4
    matrix2 = []

    # Each row placement covers: row constraint, column constraint, and two diagonals
    for row in range(n):
        for col in range(n):
            constraint = [0] * (4 * n)
            constraint[row] = 1  # Row constraint
            constraint[n + col] = 1  # Column constraint

            # Diagonal constraints
            # Main diagonal: constraint[2*n + (row-col+n-1)] (optional for full)

            matrix2.append(constraint)

    dlx2 = DancingLinks(matrix2)
    solution2 = dlx2.solve()
    if solution2:
        print(f"N-Queens solution found: positions {solution2}")
