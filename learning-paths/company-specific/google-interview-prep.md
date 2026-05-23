# Google Interview Preparation Path

Complete preparation guide for Google SDE interviews (L3-L5).

---

## 🎯 Interview Format

| Round | Duration | Topics | Notes |
|-------|----------|--------|-------|
| **Phone Screen** | 45 min | 1-2 coding problems | Medium difficulty, real-time collaboration |
| **Coding Round 1** | 45 min | Algorithm + data structure | Medium-hard problems |
| **Coding Round 2** | 45 min | Algorithm + design | Similar difficulty |
| **System Design** | 45 min | Architecture & trade-offs | For senior (L4+) |
| **Behavioral** | 30 min | Leadership, collaboration | Google culture |

---

## 📚 Knowledge Areas by Priority

### Must Know (60% of questions)

**1. Array/String Problems** (25%)
- Two-pointer techniques
- Sliding window
- Sorting & binary search
- String manipulation (KMP, Z-algorithm)

**Path:** 
```
Start: docs/01-interview-frameworks/two-pointer-techniques.md
       docs/01-interview-frameworks/sliding-window-patterns.md
Practice: python/patterns/two_pointer.py + python/patterns/sliding_window.py
Resources: 15-20 LeetCode problems
```

**2. Tree/Graph Problems** (20%)
- Binary trees, BST, balanced trees
- BFS/DFS traversals
- Graph algorithms (Dijkstra, topological sort)
- Cycle detection, connected components

**Path:**
```
Start: docs/01-interview-frameworks/graph-algorithms-mastery.md
Practice: python/algorithms/graph/graph_algorithms.py
Resources: 15-20 LeetCode problems
```

**3. Dynamic Programming** (15%)
- Classic patterns (knapsack, LCS, edit distance)
- State transitions
- Optimization techniques

**Path:**
```
Start: docs/01-interview-frameworks/dynamic-programming-mastery.md
Practice: python/algorithms/dp/dp.py
Resources: 10-15 LeetCode problems
```

### Should Know (30% of questions)

**4. System Design** (15%, for L4+)
- Database design
- Caching strategies
- Load balancing
- Microservices architecture

**Path:**
```
Start: docs/01-interview-frameworks/system-design-interview-guide.md
Study: docs/03-system-design/ (pick 3-5 case studies)
Practice: Design 3-5 systems end-to-end
```

**5. Design Patterns & OOP** (10%)
- Common patterns (Singleton, Observer, Factory)
- SOLID principles
- Low-level design

**Path:**
```
Start: docs/01-interview-frameworks/design-patterns-reference.md
Practice: Design a parking lot system, LRU cache
```

**6. Behavioral & Leadership** (5%)
- Google culture emphasis
- Leadership, collaboration, impact
- Conflict resolution

**Path:**
```
Start: docs/01-interview-frameworks/behavioral-interview-framework.md
Prepare: 3-5 stories showing leadership/impact
```

---

## 📅 Preparation Timeline

### 2-Week Sprint (Phone Screen)
```
Week 1:
- Day 1-2: Two-pointer + sliding window frameworks
- Day 3-4: Solve 10 problems on each pattern
- Day 5-6: Binary search, string algorithms
- Day 7: Review, assess weak areas

Week 2:
- Day 1-3: Trees, graphs, basic BFS/DFS
- Day 4-6: DP fundamentals, 5 problems
- Day 7: Mock interview, review
```

### 4-Week Deep Dive (Onsite)
```
Week 1:
- Arrays, strings, two-pointer, sliding window (15 problems)

Week 2:
- Trees, graphs, BFS/DFS (15 problems)
- System design intro (read 2 case studies)

Week 3:
- Dynamic programming (10 problems)
- Design patterns, OOP (5 design problems)
- Behavioral prep (2-3 stories)

Week 4:
- Mock interviews (2-3)
- Weak areas review
- Final system design practice
```

---

## 🔑 Google-Specific Topics

### What Google Cares About

1. **Clear Communication**
   - Explain approach before coding
   - Ask clarifying questions
   - Walk through examples

2. **Optimal Solutions**
   - They'll ask "Can you do better?"
   - Expect time/space optimization discussion

3. **Code Quality**
   - Clean, readable code
   - Proper variable names
   - Handle edge cases

4. **Problem-Solving Process**
   - Naive approach first
   - Identify bottlenecks
   - Optimize step-by-step

### Google Favorite Topics

```
Highly likely (appears frequently):
✅ Graph algorithms (Google maps, search, social)
✅ Tree problems (Google's index structure)
✅ String problems (search ranking, NLP)
✅ System design (cloud infrastructure)
✅ Optimization problems (resource allocation)

Less common:
❌ Math-heavy problems (unless ML role)
❌ Bit manipulation (unless systems role)
```

---

## 🧪 Practice Plan

### Phase 1: Learn Patterns (Week 1-2)

For each pattern:
1. Read framework (2-3 hours)
2. Study implementation (1 hour)
3. Solve 5 problems step-by-step (2-3 hours)
4. Solve 5 more problems timed (1-2 hours)

Total per pattern: 6-8 hours

### Phase 2: Deep Practice (Week 3-4)

Mixed problems from all patterns:
- 20 problems in 2 weeks
- Solve under interview conditions (timed)
- Review after each

### Phase 3: Mock Interviews (Final week)

- Platform: Pramp, LeetCode Live
- 2-3 mock interviews
- Record and review
- Get feedback on communication

---

## 💡 Tips for Google

**During Interview:**

1. **Think out loud**
   - "I'm thinking about using a hash map..."
   - Helps interviewer follow your logic

2. **Ask questions**
   - "Can I modify the input?"
   - "What's the expected range of N?"
   - Shows problem-solving mindset

3. **Optimize step-by-step**
   - Brute force first (show thinking)
   - "The issue is..."
   - "Can I optimize by..."

4. **Test carefully**
   - Edge cases (empty input, single element)
   - Normal cases (typical input)
   - Large cases (performance)

---

## ✅ Pre-Interview Checklist

One week before:

- [ ] Solved 50+ problems comfortably
- [ ] Can explain approach without coding first
- [ ] Handle edge cases naturally
- [ ] Have 3-5 behavioral stories ready
- [ ] Did 2-3 mock interviews
- [ ] Review weak areas once more
- [ ] Understand system design at high level
- [ ] Know complexity analysis (time/space)

---

## 📊 Problem Difficulty Guide

**Easy (10 problems):**
- Two Sum, Reverse String, Valid Parentheses
- Helps build confidence

**Medium (40 problems):**
- Add Two Numbers, LCA, Word Ladder
- Core interview material

**Hard (10 problems):**
- Only if time, for additional challenge
- Not required for L3-L4

---

## Resources by Topic

| Topic | Framework | Code | Problems |
|-------|-----------|------|----------|
| Arrays/Strings | `two-pointer-techniques.md` | `two_pointer.py` | 10 |
| Sliding Window | `sliding-window-patterns.md` | `sliding_window.py` | 9 |
| Trees/Graphs | `graph-algorithms-mastery.md` | `graph_algorithms.py` | 15+ |
| DP | `dynamic-programming-mastery.md` | `dp.py` | 10+ |
| System Design | `system-design-interview-guide.md` | Case studies | 5 systems |

---

## 🎯 Success Metrics

By interview day, you should be able to:

- [ ] Solve medium problems in 20-30 minutes comfortably
- [ ] Write clean, bug-free code in real-time
- [ ] Explain approaches clearly before coding
- [ ] Optimize solutions (time, space)
- [ ] Handle edge cases
- [ ] Answer follow-up questions confidently
- [ ] Design a system for 1M users
- [ ] Answer behavioral questions with concrete examples

---

**Last updated:** 2026-05-22

Good luck with your Google interview! 🚀
