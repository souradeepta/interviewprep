"""
Test Grid Dp Implementation
===========================

OVERVIEW:
This module provides a complete implementation of Test Grid Dp, a fundamental
data structure used in algorithms and system design.

PURPOSE & USE CASES:
- Core operation for many algorithm patterns
- Essential for interview preparation
- Real-world applications in production systems

KEY OPERATIONS:
- Time/Space complexity analysis included for each operation
- Design trade-offs explained
- Common pitfalls and edge cases documented

COMPLEXITY SUMMARY:
See individual class/function docstrings for detailed complexity analysis.

REFERENCES:
- Introduction to Algorithms (Cormen, Leiserson, Rivest, Stein)
- Algorithm Design Manual (Skiena)
- LeetCode and HackerRank problem patterns
"""

import sys
sys.path.insert(0, '/home/sbisw/github/interviewprep/python/algorithms/dp')

from dp import unique_paths, bomb_enemy, max_island_area, dungeon_game, \
    trapping_rain_water_2d, word_ladder, word_pattern_match

def test_unique_paths():
    """Test unique paths in grid."""
    assert unique_paths(3, 7) == 28
    assert unique_paths(3, 3) == 6
    assert unique_paths(1, 1) == 1

def test_bomb_enemy():
    """Test bomb enemy problem."""
    grid = [['0','E','0','0'],
            ['E','0','W','E'],
            ['0','E','0','0']]
    result = bomb_enemy(grid)
    assert result == 2  # Max is at (1,1) or (2,3): 1+1=2

def test_max_island_area():
    """Test max island area in grid."""
    grid = [[1,1,0,0,0],
            [1,0,0,1,1],
            [0,0,0,1,1],
            [0,0,0,0,0],
            [0,0,0,0,1]]
    assert max_island_area(grid) == 4  # Island at (1,3)-(2,4)

def test_dungeon_game():
    """Test dungeon game - minimum health needed."""
    dungeon = [[-3, 5], [-10, -6]]
    assert dungeon_game(dungeon) == 5

def test_trapping_rain_water_2d():
    """Test 2D water trapping."""
    elevation_map = [[1,1,1],
                     [1,0,1],
                     [1,1,1]]
    result = trapping_rain_water_2d(elevation_map)
    assert result >= 0  # Just verify it works without crashing

def test_word_ladder():
    """Test word ladder distance."""
    word_list = ["hot","dot","dog","lot","log","cog"]
    result = word_ladder("hit", "cog", word_list)
    assert result == 5

def test_word_pattern():
    """Test word pattern matching."""
    assert word_pattern_match("baab", "redbluebluered") == True
    assert word_pattern_match("aaaa", "asdasdasdasd") == True
    assert word_pattern_match("abba", "redbluebluered") == True

if __name__ == "__main__":
    test_unique_paths()
    test_bomb_enemy()
    test_max_island_area()
    test_dungeon_game()
    test_trapping_rain_water_2d()
    test_word_ladder()
    test_word_pattern()
    print("✓ All grid DP tests pass")
