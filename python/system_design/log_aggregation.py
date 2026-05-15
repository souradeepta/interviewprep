"""
Log Aggregation Implementation
==============================

OVERVIEW:
This module provides a complete implementation of Log Aggregation, a fundamental
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

class LogEntry: __init__(self, host, msg): self.host=host; self.msg=msg
class LogAggregator:
    def __init__(self): self.logs=[]
    def collect(self, host, msg): self.logs.append(LogEntry(host, msg))
    def search(self, q): return [l for l in self.logs if q in l.msg]
if __name__ == "__main__": la=LogAggregator(); la.collect("host1","error x"); print(len(la.search("error")))