import sys
sys.path.insert(0, '/home/sbisw/github/interviewprep/python/algorithms/dp')

from dp import solve_nqueens, solve_sudoku, word_search, permute, combine, \
    letter_combinations, subsets, generate_parentheses

def test_nqueens_4():
    """Test N-Queens for n=4 - should return valid solutions."""
    result = solve_nqueens(4)
    assert len(result) == 2  # 4-Queens has exactly 2 solutions
    # Verify first solution is valid (no conflicts)
    solution = result[0]
    assert len(solution) == 4
    assert len(set(solution)) == 4  # All different columns

def test_nqueens_1():
    """Edge case: single queen."""
    result = solve_nqueens(1)
    assert result == [[0]]

def test_nqueens_0():
    """Edge case: no queens."""
    result = solve_nqueens(0)
    assert result == [[]]

def test_sudoku():
    """Test Sudoku solver with a valid puzzle."""
    board = [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9]
    ]
    expected_solution = [
        [5, 3, 4, 6, 7, 8, 9, 1, 2],
        [6, 7, 2, 1, 9, 5, 3, 4, 8],
        [1, 9, 8, 3, 4, 2, 5, 6, 7],
        [8, 5, 9, 7, 6, 1, 4, 2, 3],
        [4, 2, 6, 8, 5, 3, 7, 9, 1],
        [7, 1, 3, 9, 2, 4, 8, 5, 6],
        [9, 6, 1, 5, 3, 7, 2, 8, 4],
        [2, 8, 7, 4, 1, 9, 6, 3, 5],
        [3, 4, 5, 2, 8, 6, 1, 7, 9]
    ]
    board_copy = [row[:] for row in board]
    solve_sudoku(board_copy)
    assert board_copy == expected_solution

def test_sudoku_empty_cell():
    """Test with minimal empty board (fast)."""
    board = [[5, 0, 0, 0, 0, 0, 0, 0, 0]] + [[0]*9 for _ in range(8)]
    solve_sudoku(board)
    # Just verify it's solvable (doesn't crash)
    assert board[0][0] == 5
    assert all(all(cell != 0 for cell in row) for row in board)

def test_word_search():
    """Test word search in 2D grid."""
    board = [['A', 'B', 'C', 'E'],
             ['S', 'F', 'C', 'S'],
             ['A', 'D', 'E', 'E']]
    assert word_search(board, "ABCCED") == True
    assert word_search(board, "SEE") == True
    assert word_search(board, "ABCB") == False

def test_permute():
    """Test permutations of a list."""
    result = permute([1, 2, 3])
    assert len(result) == 6
    assert [1, 2, 3] in result
    assert [3, 2, 1] in result

def test_permute_single():
    """Edge case: single element."""
    result = permute([1])
    assert result == [[1]]

def test_combine():
    """Test combinations C(n, k)."""
    result = combine(4, 2)
    assert len(result) == 6
    assert [1, 2] in result
    assert [3, 4] in result

def test_letter_combinations():
    """Test letter combinations from phone keypad."""
    result = letter_combinations("23")
    assert len(result) == 9  # 3 letters × 3 letters
    assert "ad" in result
    assert "cf" in result

def test_subsets():
    """Test all subsets (power set)."""
    result = subsets([1, 2, 3])
    assert len(result) == 8
    assert [] in result
    assert [1, 2, 3] in result

def test_generate_parentheses():
    """Test valid parentheses combinations."""
    result = generate_parentheses(3)
    assert len(result) == 5
    assert "((()))" in result
    assert "(()())" in result

if __name__ == "__main__":
    test_nqueens_4()
    test_nqueens_1()
    test_nqueens_0()
    test_sudoku()
    test_sudoku_empty_cell()
    test_word_search()
    test_permute()
    test_permute_single()
    test_combine()
    test_letter_combinations()
    test_subsets()
    test_generate_parentheses()
    print("✓ All backtracking tests pass")
