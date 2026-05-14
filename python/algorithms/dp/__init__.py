"""Dynamic Programming algorithms package."""
from .dp import (
    # Classic DP
    fibonacci,
    knapsack_01,
    lcs,
    lis,
    edit_distance,
    coin_change,
    matrix_chain_mult,
    longest_palindromic_substr,
    # Backtracking
    solve_nqueens,
    solve_sudoku,
    word_search,
    permute,
    combine,
    letter_combinations,
    subsets,
    generate_parentheses,
    # Grid & 2D DP
    unique_paths,
    bomb_enemy,
    max_island_area,
    dungeon_game,
    trapping_rain_water_2d,
    word_ladder,
    word_pattern_match,
)

__all__ = [
    # Classic DP
    "fibonacci",
    "knapsack_01",
    "lcs",
    "lis",
    "edit_distance",
    "coin_change",
    "matrix_chain_mult",
    "longest_palindromic_substr",
    # Backtracking
    "solve_nqueens",
    "solve_sudoku",
    "word_search",
    "permute",
    "combine",
    "letter_combinations",
    "subsets",
    "generate_parentheses",
    # Grid & 2D DP
    "unique_paths",
    "bomb_enemy",
    "max_island_area",
    "dungeon_game",
    "trapping_rain_water_2d",
    "word_ladder",
    "word_pattern_match",
]
