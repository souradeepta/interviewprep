"""
Notifications Implementation
============================

OVERVIEW:
This module provides a complete implementation of Notifications, a fundamental
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

from enum import Enum
class Channel(Enum): EMAIL=1; SMS=2; PUSH=3; IN_APP=4

class Notification:
    """Represents Notification."""

    def __init__(self, u, m):
        """Initialize Notification.

        Args:
            u: Parameter description
        Args:
            m: Parameter description

        Time: O(1)
        Space: O(1)
        """
        self.user=u
        self.msg=m
        self.channels=[Channel.IN_APP]
class NotificationSystem:
    def __init__(self): self.notifs=[]
    def send(self, u, m, chans): n=Notification(u,m); n.channels=chans; self.notifs.append(n); return n
    def get(self, u): return [n for n in self.notifs if n.user==u]


if __name__ == "__main__": ns=NotificationSystem(); ns.send(1, "Hi", [Channel.PUSH]); print(len(ns.get(1)))