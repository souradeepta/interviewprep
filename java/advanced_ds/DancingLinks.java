package advanced_ds;

import java.util.*;

/**
 * Dancing Links (DLX) - Algorithm X by Knuth
 *
 * Time Complexity:
 * - Construction: O(nm) where n = rows, m = columns
 * - Solving exact cover: O(n!) worst case, much faster in practice
 * - Space Complexity: O(nm)
 *
 * Use Cases:
 * - Exact cover problem (find sets that partition a universe)
 * - Sudoku solver
 * - N-queens problem
 * - Polyomino tiling
 * - Crossword puzzle construction
 *
 * Key Insight:
 * - Use circular doubly-linked lists for efficient row/column removal
 * - Backtracking with efficient constraint propagation
 * - Removing/restoring nodes is O(1) with linked lists
 * - Cover column = remove all rows that have 1 in that column
 * - Efficient branching on columns with fewest options
 */
public class DancingLinks {

    static class Node {
        Node left = this;
        Node right = this;
        Node up = this;
        Node down = this;
        Node colHeader;
        int count = 0;  // For column headers: number of nodes
    }

    private int[][] matrix;
    private int rows;
    private int cols;
    private String[] names;
    private Node root;
    private List<Node> colHeaders;

    /**
     * Initialize Dancing Links structure.
     *
     * @param matrix 2D binary matrix where 1 indicates membership
     */
    public DancingLinks(int[][] matrix) {
        this(matrix, null);
    }

    /**
     * Initialize Dancing Links structure with column names.
     *
     * @param matrix 2D binary matrix where 1 indicates membership
     * @param names Optional column names
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public DancingLinks(int[][] matrix, String[] names) {
        this.matrix = matrix;
        this.rows = matrix.length;
        this.cols = rows > 0 ? matrix[0].length : 0;

        this.names = names;
        if (names == null) {
            this.names = new String[cols];
            for (int i = 0; i < cols; i++) {
                this.names[i] = "C" + i;
            }
        }

        this.colHeaders = new ArrayList<>();
        this.root = new Node();

        buildStructure();
    }

    /**
     * Build the Dancing Links structure.
     */
    private void buildStructure() {
        // Create column headers
        Node current = root;
        for (int i = 0; i < cols; i++) {
            Node colHeader = new Node();
            colHeader.count = 0;
            colHeader.colHeader = colHeader;

            // Insert to the right
            colHeader.right = current.right;
            colHeader.left = current;
            current.right.left = colHeader;
            current.right = colHeader;

            colHeaders.add(colHeader);
        }

        // Insert row nodes
        for (int r = 0; r < rows; r++) {
            List<Node> rowNodes = new ArrayList<>();

            for (int c = 0; c < cols; c++) {
                if (matrix[r][c] == 1) {
                    Node node = new Node();
                    node.colHeader = colHeaders.get(c);
                    colHeaders.get(c).count++;

                    // Add to column (bottom)
                    node.down = colHeaders.get(c);
                    node.up = colHeaders.get(c).up;
                    colHeaders.get(c).up.down = node;
                    colHeaders.get(c).up = node;

                    rowNodes.add(node);
                }
            }

            // Link nodes in row
            for (int i = 0; i < rowNodes.size(); i++) {
                rowNodes.get(i).right = rowNodes.get((i + 1) % rowNodes.size());
                rowNodes.get(i).left = rowNodes.get(i - 1 < 0 ? rowNodes.size() - 1 : i - 1);
            }
        }
    }

    /**
     * Cover a column.
     */
    private void cover(Node colHeader) {
        colHeader.right.left = colHeader.left;
        colHeader.left.right = colHeader.right;

        Node node = colHeader.down;
        while (node != colHeader) {
            Node rowNode = node.right;
            while (rowNode != node) {
                rowNode.down.up = rowNode.up;
                rowNode.up.down = rowNode.down;
                rowNode.colHeader.count--;
                rowNode = rowNode.right;
            }
            node = node.down;
        }
    }

    /**
     * Uncover a column.
     */
    private void uncover(Node colHeader) {
        Node node = colHeader.up;
        while (node != colHeader) {
            Node rowNode = node.left;
            while (rowNode != node) {
                rowNode.colHeader.count++;
                rowNode.down.up = rowNode;
                rowNode.up.down = rowNode;
                rowNode = rowNode.left;
            }
            node = node.up;
        }

        colHeader.right.left = colHeader;
        colHeader.left.right = colHeader;
    }

    private List<Node> solution = new ArrayList<>();

    /**
     * Recursively find exact cover using Algorithm X.
     */
    private boolean solve() {
        if (root.right == root) {
            return true;  // All columns covered
        }

        // Choose column with minimum size (heuristic)
        Node minCol = null;
        int minCount = Integer.MAX_VALUE;

        Node col = root.right;
        while (col != root) {
            if (col.count < minCount) {
                minCount = col.count;
                minCol = col;
            }
            col = col.right;
        }

        if (minCount == 0) {
            return false;  // No solution
        }

        cover(minCol);

        Node row = minCol.down;
        while (row != minCol) {
            solution.add(row);

            // Cover all columns in this row
            Node colNode = row.right;
            while (colNode != row) {
                cover(colNode.colHeader);
                colNode = colNode.right;
            }

            // Recursively solve
            if (solve()) {
                return true;
            }

            // Backtrack
            colNode = row.left;
            while (colNode != row) {
                uncover(colNode.colHeader);
                colNode = colNode.left;
            }

            solution.remove(solution.size() - 1);
            row = row.down;
        }

        uncover(minCol);
        return false;
    }

    /**
     * Find exact cover.
     *
     * @return List of row indices that form exact cover, or null if no solution
     */
    public List<Integer> solve() {
        solution.clear();
        if (solve()) {
            List<Integer> result = new ArrayList<>();
            for (Node node : solution) {
                result.add(getRowIndex(node));
            }
            return result;
        }
        return null;
    }

    /**
     * Get original row index from a node.
     */
    private int getRowIndex(Node node) {
        // Find which row this node belongs to by checking colHeader position
        int colIndex = 0;
        Node colNode = root.right;
        while (colNode != root) {
            if (colNode == node.colHeader) {
                break;
            }
            colIndex++;
            colNode = colNode.right;
        }

        // Count occurrences in column to find row
        Node current = node.colHeader.down;
        int row = 0;
        while (current != node && current != node.colHeader) {
            row++;
            current = current.down;
        }

        return row;
    }

    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public static void main(String[] args) {
        // Example 1: Simple exact cover
        System.out.println("=== Example 1: Simple Exact Cover ===");
        int[][] matrix = {
                {1, 0, 0, 1, 0, 0, 0},
                {0, 1, 1, 0, 0, 0, 0},
                {0, 0, 1, 0, 0, 1, 0},
                {0, 0, 0, 1, 1, 0, 1},
                {1, 0, 0, 0, 1, 0, 0},
                {0, 0, 0, 0, 1, 0, 1},
        };

        DancingLinks dlx = new DancingLinks(matrix);
        List<Integer> solution = dlx.solve();

        if (solution != null) {
            System.out.println("Solution found: rows " + solution);
            for (int rowIdx : solution) {
                System.out.println("  Row " + rowIdx + ": " + Arrays.toString(matrix[rowIdx]));
            }
        } else {
            System.out.println("No solution found");
        }

        // Example 2: 4-Queens problem
        System.out.println("\n=== Example 2: 4-Queens Problem ===");
        int n = 4;
        int[][] queenMatrix = new int[n * n][n + n];  // n rows + n cols

        for (int row = 0; row < n; row++) {
            for (int col = 0; col < n; col++) {
                int idx = row * n + col;
                queenMatrix[idx][row] = 1;      // Row constraint
                queenMatrix[idx][n + col] = 1;  // Column constraint
            }
        }

        DancingLinks dlx2 = new DancingLinks(queenMatrix);
        List<Integer> solution2 = dlx2.solve();

        if (solution2 != null) {
            System.out.println("4-Queens solution found: positions " + solution2);
        }
    }
}
