# 📚 Comprehensive SDE Interview Learning Guide

**A complete, structured system for mastering algorithms and data structures in preparation for FAANG interviews.**

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Learning Path Selection](#learning-path-selection)
3. [Daily Schedules](#daily-schedules)
4. [Topic Mastery Checklist](#topic-mastery-checklist)
5. [Company-Specific Paths](#company-specific-paths)
6. [Interview Stage Preparation](#interview-stage-preparation)
7. [Weak Area Recovery](#weak-area-recovery)
8. [Mock Interview Guide](#mock-interview-guide)
9. [Progress Tracking](#progress-tracking)
10. [Common Mistakes & How to Avoid](#common-mistakes--how-to-avoid)

---

## Getting Started

### Step 1: Self-Assessment (1 hour)

Before choosing a path, honestly assess yourself:

**Take the self-assessment:**
```
For each topic (1-5 scale):
1 = Never heard of it
2 = Heard of it, no practice
3 = Some practice, confused
4 = Comfortable, can solve
5 = Expert, teach others

[] Arrays & Strings
[] Linked Lists  
[] Stacks & Queues
[] Trees & BSTs
[] Graphs
[] Heaps & Priority Queues
[] Hash Tables & Sets
[] Dynamic Programming
[] Sorting & Searching
[] Bit Manipulation
[] System Design
[] Design Patterns
```

**Scoring:**
- **Average 4-5:** Light refresh path (2 weeks)
- **Average 3-4:** Balanced path (4 weeks)
- **Average 2-3:** Comprehensive path (8 weeks)
- **Average 1-2:** Intensive path (12 weeks)

### Step 2: Define Your Goal

**What interview are you preparing for?**
- [ ] FAANG (Facebook, Apple, Amazon, Netflix, Google)
- [ ] Other Big Tech (Microsoft, Adobe, etc.)
- [ ] Startup
- [ ] Specific company: ___________

**Interview type?**
- [ ] Phone Screen (30-45 min)
- [ ] Technical Round (45-90 min)
- [ ] System Design (60 min)
- [ ] Multiple rounds

**Time available?**
- [ ] 2 weeks (urgent)
- [ ] 4 weeks (standard)
- [ ] 8 weeks (thorough)
- [ ] 12+ weeks (deep mastery)

---

## Learning Path Selection

### Quick Decision Tree

```
TIMELINE?
├─ 2 weeks → URGENT SPRINT
│           └─ Focus: Arrays, Strings, Trees
│           └─ Time: 15 hours/week
│           └─ Path: learning-paths/sequential-tracks/2-week-sprint.md
│
├─ 4 weeks → BALANCED (RECOMMENDED)
│           └─ Focus: All core topics
│           └─ Time: 6-7 hours/week
│           └─ Path: learning-paths/sequential-tracks/4-week-focused.md
│
├─ 8 weeks → COMPREHENSIVE
│           └─ Focus: All topics + depth
│           └─ Time: 4-5 hours/week
│           └─ Path: learning-paths/sequential-tracks/8-week-comprehensive.md
│
└─ 12+ weeks → DEEP MASTERY
            └─ Focus: Everything + rare topics
            └─ Time: 3-4 hours/week
            └─ Path: Create custom from domains/
```

### Learning Style Preference

**I prefer structure and timelines**
→ [Sequential Tracks](#learning-paths-by-timeline)

**I prefer targeted by interview round**
→ [Interview Playbooks](#interview-stage-preparation)

**I prefer focused topic mastery**
→ [Domain Deep-Dives](#domain-deep-dives)

**I prefer customized based on company**
→ [Company-Specific Paths](#company-specific-paths)

---

## Daily Schedules

### 2-Week Sprint Daily Schedule

**Time Commitment:** 15 hours/week = ~2 hours/day + 1 long session/week

```
MONDAY-FRIDAY (2 hours each)
├─ 0:00-0:45 → Read concept (15 min) + Study examples (30 min)
├─ 0:45-1:45 → Solve 1-2 problems (60 min)
└─ 1:45-2:00 → Review + note patterns (15 min)

SATURDAY (4-5 hours)
├─ Long problem session OR
└─ Review weak areas

SUNDAY (2-3 hours)
└─ Weekly review + mock interview
```

**Example Week 1, Day 1 (Monday) - Arrays**
```
9:00-9:15  | Read: Two-pointer technique explanation
9:15-9:45  | Study: 3 two-pointer examples
9:45-10:45 | Solve: "Container With Most Water" (LeetCode 11)
10:45-11:00| Review: Pattern matching, edge cases
```

### 4-Week Focused Daily Schedule

**Time Commitment:** 6-7 hours/week = ~1 hour/day + 1-2 long sessions/week

```
MONDAY-FRIDAY (1 hour each)
├─ 0:00-0:20 → Read concept (20 min)
├─ 0:20-0:50 → Solve 1 problem (30 min)
└─ 0:50-1:00 → Pattern review (10 min)

WEDNESDAY (1.5 hours)
├─ Extended session for complex topics
└─ 2-3 problems

SATURDAY (2-3 hours)
└─ Weekly domain review + harder problems

SUNDAY (1-2 hours)
└─ Mock interview OR weak area practice
```

### 8-Week Comprehensive Daily Schedule

**Time Commitment:** 4-5 hours/week = ~1 hour/2-3 days + weekend sessions

```
MONDAY, WEDNESDAY, FRIDAY (1-1.5 hours each)
├─ Read topic (20 min)
├─ Solve 1-2 problems (30-50 min)
└─ Pattern analysis (10 min)

SATURDAY (2-3 hours)
├─ Domain review (30 min)
├─ 3-4 medium problems (90 min)
└─ Reflection on patterns (30 min)

SUNDAY (1 hour)
└─ Weekly summary + weak areas
```

---

## Topic Mastery Checklist

For each topic, verify you can:

### Arrays & Strings
- [ ] Solve with two pointers
- [ ] Implement sliding window
- [ ] Handle edge cases (empty, single element, duplicates)
- [ ] Explain time/space complexity
- [ ] Code in both Python and Java
- [ ] Solve at least 3 medium problems
- [ ] Solve at least 1 hard problem
- [ ] Recognize when to use vs alternatives

### Linked Lists
- [ ] Traverse forward/backward
- [ ] Insert/delete at any position
- [ ] Detect cycle (Floyd's algorithm)
- [ ] Reverse linked list
- [ ] Handle dummy nodes
- [ ] Solve at least 5 problems (easy to hard)

### Trees & BSTs
- [ ] Understand tree properties
- [ ] DFS (preorder, inorder, postorder)
- [ ] BFS (level order)
- [ ] BST operations (insert, delete, search)
- [ ] Lowest Common Ancestor
- [ ] Path sum problems
- [ ] Solve at least 8 problems across difficulties

### Graphs
- [ ] Represent as adjacency list/matrix
- [ ] DFS traversal
- [ ] BFS traversal
- [ ] Topological sort
- [ ] Shortest path (Dijkstra, BFS)
- [ ] Connected components
- [ ] Bipartite checking
- [ ] Solve at least 8 problems

### Dynamic Programming
- [ ] Identify overlapping subproblems
- [ ] Define state correctly
- [ ] Memoization (top-down)
- [ ] Tabulation (bottom-up)
- [ ] Space optimization
- [ ] Solve DP on:
  - [ ] 1D sequences
  - [ ] 2D grids
  - [ ] Tree structures
  - [ ] Strings
  - [ ] At least 10 problems total

### Sorting & Searching
- [ ] Binary search (and variants)
- [ ] Merge sort (understand and code)
- [ ] Quick sort (understand and code)
- [ ] Heap sort (understand)
- [ ] Counting sort (understand)
- [ ] When to use each
- [ ] Solve at least 5 problems

### Hash Tables & Sets
- [ ] Understand hash collisions
- [ ] Design hash functions
- [ ] Two-sum variant problems
- [ ] Duplicate detection
- [ ] Frequency counting
- [ ] Solve at least 6 problems

### Heaps & Priority Queues
- [ ] Min/max heap properties
- [ ] Heapify operations
- [ ] Heap sort
- [ ] K-largest/smallest
- [ ] Merge K sorted lists
- [ ] Solve at least 5 problems

### Bit Manipulation
- [ ] Bitwise operations (&, |, ^, ~, <<, >>)
- [ ] Check bit, set bit, clear bit
- [ ] Count set bits
- [ ] Power of 2 check
- [ ] XOR swap/pairs
- [ ] Solve at least 4 problems

### System Design Fundamentals
- [ ] Scalability concepts
- [ ] Load balancing
- [ ] Caching strategies
- [ ] Database design
- [ ] API design
- [ ] Trade-offs (consistency vs availability, latency vs throughput)
- [ ] Design at least 2 simple systems

---

## Company-Specific Paths

### Google Interview Path (4 weeks)

**Focus Areas:**
- Arrays & Strings (40%)
- Trees & Graphs (30%)
- DP (20%)
- Math & Bit Manipulation (10%)

**Week 1:** Arrays, Strings, Hashing
**Week 2:** Trees, Graphs, DFS/BFS
**Week 3:** DP (1D, 2D, Tree)
**Week 4:** Mixed problems + System Design

**Special Prep:**
- Bit manipulation tricks
- Prime number problems
- Matrix problems
- Trie problems (less common but possible)

### Facebook/Meta Interview Path (4 weeks)

**Focus Areas:**
- Arrays & Strings (35%)
- Trees & Graphs (35%)
- DP (20%)
- Stacks & Queues (10%)

**Week 1:** Arrays, Strings, Stack/Queue problems
**Week 2:** Trees (especially binary trees), Graphs
**Week 3:** DP, Backtracking
**Week 4:** Mixed + harder problems

**Special Prep:**
- Backtracking problems
- Interval problems
- LCA (Lowest Common Ancestor)
- All paths problems

### Amazon Interview Path (4 weeks)

**Focus Areas:**
- Arrays & Strings (40%)
- Trees (25%)
- Graphs (20%)
- DP & Others (15%)

**Week 1:** Arrays, Strings, Recursion
**Week 2:** Trees, BST operations
**Week 3:** Graphs, DFS/BFS
**Week 4:** DP + mixed

**Special Prep:**
- OOD (Object-Oriented Design)
- Tree modification problems
- Graph connectivity problems
- Word ladder, word search patterns

### Microsoft Interview Path (4 weeks)

**Focus Areas:**
- Arrays & Strings (35%)
- Trees & Graphs (30%)
- DP (20%)
- Design (15%)

**Week 1:** Arrays, Strings, Hash Tables
**Week 2:** Trees, Graphs
**Week 3:** DP, Sorting
**Week 4:** Design + mixed

**Special Prep:**
- OOD problems
- Interval/range problems
- Paint/fill problems
- Two-pointer variations

### Apple Interview Path (4 weeks)

**Focus Areas:**
- Arrays & Strings (40%)
- Trees (25%)
- DP (20%)
- System Design (15%)

**Week 1:** Arrays, Strings
**Week 2:** Trees, Recursion
**Week 3:** DP, Sorting
**Week 4:** Design + mixed

**Special Prep:**
- Array manipulation edge cases
- Tree/graph with constraints
- Performance optimization
- System design (more emphasis than others)

---

## Interview Stage Preparation

### Phone Screen Preparation (30-45 min)

**What to Expect:**
- 1-2 easy-medium problems
- Only arrays, strings, hash tables
- Focus on coding speed, not algorithm novelty
- Usually no system design

**What to Study:**
```
Week 1:
□ Two-pointer technique
□ Sliding window
□ Hash table patterns
□ Solve 5 array/string problems (all easy)

Week 2:
□ Solve 5 more array/string problems
□ Mix of easy/medium
□ Focus on edge cases
□ Practice articulating out loud
```

**Sample Problems:**
- Two Sum, Valid Palindrome, Longest Substring Without Repeating
- Container With Most Water, Merge Sorted Array
- Valid Parentheses, Majority Element

**What to Do:**
1. **Read problem carefully** (2 min)
2. **Clarify with interviewer** (1 min)
3. **Explain approach before coding** (2-3 min)
4. **Code cleanly** (15-20 min)
5. **Test with examples** (5 min)

**Common Mistakes:**
- ❌ Jumping into code without planning
- ❌ Not testing edge cases
- ❌ Sloppy variable naming
- ✅ Slow down, think out loud, explain approach first

### Technical Interview Preparation (45-90 min)

**What to Expect:**
- 1-2 medium-hard problems
- Can include any data structure/algorithm
- May ask for optimization after first solution
- Sometimes ask about trade-offs

**What to Study:**
```
Weeks 1-2:
□ Master all basic data structures
□ Solve 2-3 problems from each domain

Weeks 3-4:
□ Practice on harder problems
□ Focus on explaining approaches
□ Practice with time limits (45 min per problem)
□ Do mock interviews
```

**Time Breakdown (per problem):**
- 0:00-3:00 → Understand & clarify (ask questions!)
- 3:00-5:00 → Discuss approach & complexity
- 5:00-25:00 → Code first solution
- 25:00-35:00 → Test & debug
- 35:00-45:00 → Optimize (if needed) + discuss trade-offs

### System Design Interview Preparation (60 min)

**What to Expect:**
- Design a system (URL shortener, cache, feed, etc.)
- Asked to make trade-off decisions
- Should ask clarifying questions
- No single "right" answer

**What to Study:**
```
Week 1:
□ Read: Scalability fundamentals (docs/system_design/)
□ Understand: Load balancing, caching, DBs, APIs
□ Learn: CAP theorem, consistency, availability, partition tolerance

Week 2:
□ Study: 3-4 system design examples
□ Design: URL shortener, LRU cache, chat system
□ Practice: Explain approach to friend/colleague
□ Review: Trade-offs for each

Week 3:
□ Deep-dive: Your weakest area
□ Practice: Mock system design interviews
□ Refine: Ability to pivot based on follow-up questions
```

**Structure of Answer:**
1. **Clarifying Questions** (5 min)
   - Scale? (DAU, QPS, storage?)
   - Features? (exact requirements?)
   - Constraints? (latency, availability?)

2. **High-Level Design** (10 min)
   - Architecture diagram
   - Key components
   - Data flow

3. **Deep-Dive** (30 min)
   - Pick bottleneck to optimize
   - Discuss solutions
   - Explain trade-offs

4. **Follow-up** (15 min)
   - Interviewer asks follow-up
   - Adjust design accordingly

---

## Weak Area Recovery

### Identify Weak Areas

**Take a diagnostic test:**
- Solve 20 problems across all domains (1 easy, 1 medium from each)
- Track which ones you struggled with
- Mark by domain and difficulty

**Weak Area Signs:**
- Took >30 min on easy problem
- Completely stuck on logic
- Couldn't optimize to good complexity
- Forgot basic operations

### Recovery Plan (1-2 weeks)

**Daily:** 
- 30 min: Study weak domain concepts
- 30 min: Solve 2 problems in weak domain
- 30 min: Review patterns/solutions

**Weekly:**
- 2 hours: Solve 5-6 problems in weak domain
- 1 hour: Review with explanations

**Key Rules:**
1. **Don't skip, don't rush** - Go slow until it clicks
2. **Pattern recognition** - After 3-4 problems, you'll see patterns
3. **Understand WHY** - Not just memorize solutions
4. **Teach it** - Explain to someone else or write explanation

### Example: DP Recovery (1 week)

**Day 1-2:** Fundamentals
- [ ] Read: State definition, memoization, tabulation
- [ ] Solve: Fibonacci (3 ways), Climbing Stairs
- [ ] Understand: Why each approach works

**Day 3-4:** 1D DP
- [ ] Solve: House Robber, Coin Change, Longest Increasing Subsequence
- [ ] Pattern: "For each position, consider previous states"

**Day 5:** 2D DP
- [ ] Solve: Unique Paths, Longest Common Subsequence
- [ ] Pattern: "Grid-based state transitions"

**Day 6-7:** Mixed
- [ ] Solve: Harder DP problems
- [ ] Identify: Which DP pattern applies?

---

## Mock Interview Guide

### Self-Conducted Mock (30-45 min)

**Setup:**
1. Pick a random problem from your target domain
2. Set timer for 45 minutes
3. **No peeking at solutions**
4. Code on paper or IDE

**Execution:**
- Spend 2-3 min understanding
- Spend 2-3 min discussing approach (write it down)
- Code for 20-30 min
- Test for 10 min

**Grading:**
- Problem solved correctly? (50%)
- Good complexity? (25%)
- Clean code? (15%)
- Explained well? (10%)

### Peer-Conducted Mock (1 hour)

**Best practice:** Interview with friend/colleague

**Interviewer should:**
1. Give problem without hints
2. Ask clarifying questions if you're vague
3. Point out bugs during testing
4. Ask "Can you optimize?" after first solution
5. Give feedback after

**Candidate should:**
1. Think out loud
2. Ask clarifying questions
3. Explain approach before coding
4. Code neatly
5. Test edge cases

### AI Mock Interview

**Using agents:** See [AGENTS.md](AGENTS.md)

- `/sde2-interviewer` - Full mock technical interview
- Realistic interviewer behavior
- Feedback on approach and code

**How to use:**
1. Run: `/sde2-interviewer`
2. Get random LeetCode-style problem
3. Solve in 45 minutes
4. Receive structured feedback

---

## Progress Tracking

### Weekly Progress Template

**Week #: [DATE - DATE]**

**Learning Goals:**
- [ ] Goal 1
- [ ] Goal 2
- [ ] Goal 3

**Problems Solved This Week:**
| Problem | Domain | Difficulty | Time | Status |
|---------|--------|-----------|------|--------|
| Two Sum | Array | Easy | 10 min | ✓ |
| ... | ... | ... | ... | ... |

**Weak Areas Identified:**
- Area 1: Why difficult?
- Area 2: Why difficult?

**Next Week's Focus:**
- Strengthen area 1
- Strengthen area 2
- Move forward with new domain

**Confidence Level (1-5):**
- Overall: 3/5
- Arrays: 4/5
- Trees: 2/5

---

## Common Mistakes & How to Avoid

### Coding Mistakes

| Mistake | Example | Fix |
|---------|---------|-----|
| Off-by-one errors | Loop: `for i in range(len(arr))` when should be `range(n-1)` | Think about boundary |
| Null pointer | Access node.next without checking if node is None | Always check before access |
| Modifying while iterating | Delete from list while looping | Iterate over copy or use different approach |
| Integer overflow | Sum of large nums without considering overflow | Use long/64-bit integers |
| Shadowed variables | `for i in ...: for i in ...` | Use different variable names |

**Prevention:**
- Use IDE that catches these (VSCode, PyCharm)
- Test with edge cases: empty, single element, negatives
- Review code before submitting

### Algorithm Mistakes

| Mistake | Example | Fix |
|---------|---------|-----|
| Wrong complexity choice | Using bubble sort O(n²) when should use merge sort O(n log n) | Understand when each applies |
| Greedy doesn't work | Greedy coin change fails for some denominations | Verify greedy choice property first |
| DP recurrence wrong | Forgot a case in state transition | Write out recurrence clearly |
| Base case missing | DP doesn't handle n=0 | Explicitly handle all base cases |

**Prevention:**
- Write recurrence relation before coding
- Trace through example by hand
- Verify with simple test cases

### Interview Mistakes

| Mistake | Example | Fix |
|---------|---------|-----|
| Not asking questions | Assume requirements unclear in problem | Ask: "Constraints? Duplicates? Range?" |
| Jumping to code | Start coding without explaining approach | Spend 2-3 min planning first |
| Not testing | Submit without testing edge cases | Test: empty, single, duplicates, negatives |
| Poor variable names | `a`, `b`, `c` | Use descriptive names: `left`, `right`, `count` |
| Not explaining | Silently code for 30 minutes | Talk through your thinking |

**Prevention:**
- Practice explaining to friend
- Do mock interviews
- Record yourself and watch

### Learning Mistakes

| Mistake | Impact | Fix |
|---------|--------|-----|
| Trying to memorize solutions | False confidence, fails on new problems | Understand patterns, not solutions |
| Skipping weak areas | Get these in interview, fail | Don't skip, do recovery plan |
| Not doing both languages | Only know Python, can't code Java | Practice both, even if slower in one |
| Ignoring complexity | Think solution is correct, fails tests | Always calculate O(time) and O(space) |
| Practicing same type repeatedly | Good at array problems, fail at graphs | Practice all domains equally |

**Prevention:**
- Do weak area recovery immediately
- Practice both Python and Java
- Always think about complexity
- Do variety of problem types

---

## Final Tips for Success

### The Day Before Interview

**Do:**
- ✓ Review 3-4 key patterns from domains you struggle with
- ✓ Get good sleep (8 hours)
- ✓ Prepare: pen, paper, water, coffee
- ✓ Test: camera, microphone, IDE/compiler
- ✓ Arrive 10 min early

**Don't:**
- ✗ Learn new algorithms (too late!)
- ✗ Solve new problems (might confuse)
- ✗ Stay up late cramming
- ✗ Try extremely hard problems (confidence killer)

### During Interview

**Do:**
- ✓ Read problem carefully
- ✓ Ask clarifying questions
- ✓ Explain approach before coding
- ✓ Think out loud
- ✓ Test with examples
- ✓ Ask for hints if stuck (>10 min)

**Don't:**
- ✗ Jump into code immediately
- ✗ Assume requirements you're unsure about
- ✗ Code silently for 30 minutes
- ✗ Submit without testing
- ✗ Give up if it's hard

### Post-Interview

**Do:**
- ✓ Send thank-you email
- ✓ Review your performance (what went well? what could improve?)
- ✓ Practice weak points before next round

**Don't:**
- ✗ Obsess over whether you'll get offer
- ✗ Skip preparation between rounds
- ✗ Make excuses

---

## Quick Links

- **Self-Assessment:** See "Getting Started" section above
- **Learning Paths:** [learning-paths/](learning-paths/)
- **All Algorithms:** [docs/algorithms/](docs/algorithms/)
- **System Design:** [docs/system_design/](docs/system_design/)
- **Mock Interviews:** [AGENTS.md](AGENTS.md)
- **Problem Database:** [docs/problems/](docs/problems/) (if exists)

---

## You've Got This! 🚀

Remember: Success comes from consistent practice, not cramming. Spend 30-60 min daily for 4-8 weeks, and you'll be ready for any FAANG interview.

Good luck! 💪
