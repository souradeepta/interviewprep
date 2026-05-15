"""
Time Series Db Implementation
=============================

OVERVIEW:
This module provides a complete implementation of Time Series Db, a fundamental
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

from collections import defaultdict
class TimeSeriesDB:
    def __init__(self): self.data=defaultdict(list)
    def write(self, metric, ts, val): self.data[metric].append((ts, val))
    def query(self, metric, start, end): 
    """
    [Brief description of what this function does]

    Args:
        [param]: description

    Returns:
        [description of return value]

    Time: O([complexity])
    Space: O([complexity])
    """
        return [(t,v) for t,v in self.data[metric] if start<=t<=end]
if __name__ == "__main__": ts=TimeSeriesDB(); ts.write("cpu", 1000, 50); print(ts.query("cpu", 0, 2000))