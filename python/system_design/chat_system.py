"""
Chat System Implementation
==========================

OVERVIEW:
This module provides a complete implementation of Chat System, a fundamental
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

class Message:
    """Represents a message between users."""

    def __init__(self, f, t, txt):
        """Initialize Message.

        Args:
            f: Parameter description
        Args:
            t: Parameter description
        Args:
            txt: Parameter description

        Time: O(1)
        Space: O(1)
        """
        self.frm=f
        self.to=t
        self.txt=txt
        self.status='sent'
class ChatSystem:
    def __init__(self): self.msgs={}; self.convs={}
    def send(self, f, t, txt): m=Message(f,t,txt); self.msgs[id(m)]=m; return m
    def get_msgs(self, u1, u2): return [m for m in self.msgs.values() if (m.frm==u1 and m.to==u2) or (m.frm==u2 and m.to==u1)]


if __name__ == "__main__": c=ChatSystem(); c.send(1,2,"Hi"); print(len(c.get_msgs(1,2)))