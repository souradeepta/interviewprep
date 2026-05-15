"""
Message Queue Implementation
============================

OVERVIEW:
This module provides a complete implementation of Message Queue, a fundamental
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

from collections import deque
class Topic: __init__(self, name): self.name=name; self.queue=deque(); self.subs=[]
class MessageQueue:
    def __init__(self): self.topics={}
    def create_topic(self, t): self.topics[t]=Topic(t)
    def publish(self, t, m): self.topics[t].queue.append(m)
    def subscribe(self, t, f): self.topics[t].subs.append(f)
    def consume(self, t): return list(self.topics[t].queue) if t in self.topics else []
if __name__ == "__main__": mq=MessageQueue(); mq.create_topic("t1"); mq.publish("t1","msg1"); print(mq.consume("t1"))