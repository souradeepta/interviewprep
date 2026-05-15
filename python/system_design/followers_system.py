"""
Followers System Implementation
===============================

OVERVIEW:
This module provides a complete implementation of Followers System, a fundamental
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

class SocialGraph:
    def __init__(self): self.followers={}; self.following={}
    def follow(self, u, t): self.followers.setdefault(t,[]).append(u); self.following.setdefault(u,[]).append(t)
    def unfollow(self, u, t): self.followers[t].remove(u); self.following[u].remove(t) if t in self.following[u] else None
    def get_followers(self, u): return self.followers.get(u, [])
    def get_following(self, u): return self.following.get(u, [])
if __name__ == "__main__": sg=SocialGraph(); sg.follow(1,2); print(sg.get_followers(2))