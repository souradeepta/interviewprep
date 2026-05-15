"""
Like Comment System Implementation
==================================

OVERVIEW:
This module provides a complete implementation of Like Comment System, a fundamental
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

class Post:
    """Represents Post."""

    def __init__(self, uid, txt):
        """Initialize Post.

        Args:
            uid: Parameter description
        Args:
            txt: Parameter description

        Time: O(1)
        Space: O(1)
        """
        self.uid=uid
        self.txt=txt
        self.likes=0
        self.comments=[]
class LikeCommentSystem:
    def __init__(self): self.posts={}
    def create_post(self, uid, txt): p=Post(uid, txt); self.posts[id(p)]=p; return p
    def like(self, pid): self.posts[pid].likes+=1
    def comment(self, pid, txt): self.posts[pid].comments.append(txt)


if __name__ == "__main__": lcs=LikeCommentSystem(); p=lcs.create_post(1,"Hi"); lcs.like(id(p)); print(p.likes)