# Meta (Facebook) Interview Preparation Path

Complete guide for Meta SDE interviews (E3-E5).

---

## 🎯 Interview Format

| Round | Duration | Focus | Style |
|-------|----------|-------|-------|
| **Phone Screen** | 45 min | Data structures, algorithms | Collaborative |
| **Coding Round 1** | 45 min | Algorithm, coding style | Performance |
| **Coding Round 2** | 45 min | Medium-hard problem | Optimization |
| **System Design** | 45 min | Design thinking, trade-offs | For senior |
| **Behavioral** | 30 min | Culture fit, impact | Growth mindset |

---

## 🔍 Meta-Specific Focus Areas

### Meta Emphasis: Speed & Optimization

Meta values:
- **Fast shipping** (Facebook move fast culture)
- **Optimization** (scale to billions of users)
- **Problem-solving** (unique challenges)

This translates to:

1. **Algorithm Optimization**
   - Can you improve O(n²) to O(n log n)?
   - Space-time trade-offs
   - Practical optimizations

2. **System Design**
   - Handling 2B+ users
   - Caching strategies
   - Feed algorithms, ranking

3. **Code Quality**
   - Clean, optimizable code
   - Comments where needed
   - Testing mindset

---

## 📚 Knowledge Requirements

### Tier 1: Must Know (70%)

**1. Array/String Manipulation** (25%)
- Two-pointer, sliding window
- Sorting, binary search
- Substring/subarray problems
- String transformations

**2. Hash Maps & Data Structures** (20%)
- Hash maps, sets
- Using DS to optimize solutions
- Collisions, load factors

**3. Trees & Graphs** (15%)
- Traversals (BFS, DFS)
- Binary search trees
- Shortest path algorithms
- Trees specifically (Meta uses them heavily)

**4. Linked Lists** (10%)
- Operations: insert, delete, reverse
- Two-pointer technique
- Fast/slow pointers

### Tier 2: Important (25%)

**5. Dynamic Programming** (10%)
- 1D DP problems
- Basic optimization

**6. System Design** (10%)
- For E4+
- Focus on scale and trade-offs
- Case studies

**7. Behavioral** (5%)
- Impact stories
- Teamwork examples

---

## 📅 Preparation Timeline

### 3-Week Program (Recommended)

**Week 1: Foundational Patterns**
```
- Two-pointer techniques (3 hours)
- Solve 10 problems
- Sliding window (2 hours)
- Solve 8 problems
- Hash maps (2 hours)
- Solve 8 problems
Total: 30 problems, mastery of core patterns
```

**Week 2: Complex Data Structures**
```
- Trees and graphs (4 hours)
- Solve 15 problems
- Linked lists (2 hours)
- Solve 8 problems
- Mixed problems (3 hours)
- Solve 10 problems
Total: 33 problems, deep understanding
```

**Week 3: Integration & Practice**
```
- DP basics (2 hours)
- Solve 5 problems
- Mock interviews (3 sessions)
- Weak area review
- System design prep (2 hours, if E4+)
- Behavioral stories (2 hours)
Total: 3 mocks, well-rounded preparation
```

---

## 🎯 Meta's Favorite Topics

```
HIGHLY LIKELY (appear in 70%+ of interviews):
✅ Array/String problems (fundamental)
✅ Trees (important for Meta's infrastructure)
✅ Hash maps (optimization tool)
✅ Graphs (for social connections)
✅ Two-pointer, sliding window

LIKELY (30-50%):
⚠️ Linked lists (classic)
⚠️ Stack/Queue (in complex problems)
⚠️ Basic DP (optimization)

LESS COMMON (<20%):
❌ Bit manipulation
❌ Complex math
❌ Heap (rarely pure heap problem)
```

---

## 💡 Meta Interview Tips

### What Interviewers Look For

1. **Problem Understanding**
   - Ask clarifying questions
   - Confirm constraints
   - Discuss approach before coding

2. **Coding Efficiency**
   - How fast you write bug-free code
   - Can you parallelize thinking (code + talk)?
   - Comfortable with language idioms

3. **Optimization Mindset**
   - "Can we do better?"
   - Trade-offs explicitly discussed
   - Practical vs. theoretical

4. **Testing Mentality**
   - Consider edge cases
   - Walk through examples
   - Simple test during coding

### During the Interview

```
Recommended flow:
1. Repeat problem (2 min)
2. Clarifying questions (2 min)
3. Discuss approach (3 min)
4. Code implementation (25 min)
5. Test & optimize (8 min)
6. Discuss trade-offs (5 min)
```

---

## 🚀 Difficulty Guidance

| Level | Easy | Medium | Hard |
|-------|------|--------|------|
| **E3** | 20% | 70% | 10% |
| **E4** | 10% | 70% | 20% |
| **E5** | 0% | 60% | 40% |

Focus on medium problems for E3-E4 (most interviews).

---

## 📊 Study Guide

**Essential to master:**

| Topic | Hours | Problems | Complexity |
|-------|-------|----------|------------|
| Two-pointer | 3 | 10 | 1-5 |
| Sliding window | 2 | 8 | 2-4 |
| Hash maps | 2 | 8 | 1-4 |
| Trees | 4 | 15 | 2-5 |
| Graphs | 3 | 12 | 2-5 |
| Linked lists | 2 | 8 | 2-4 |
| DP (basics) | 2 | 5 | 3-4 |
| **Total** | **18** | **66** | - |

---

## 🧪 Mock Interview Strategy

**Do 3-4 mock interviews spread across final 2 weeks**

```
Mock 1: Full interview, identify weak areas
Mock 2: Focus on weak areas
Mock 3: Full interview again, gauge improvement
Mock 4: (Optional) Different problem type
```

Focus areas:
- Communication (explain before coding)
- Optimization (improve naive solution)
- Edge cases (handle all scenarios)
- Time management (finish on time)

---

## 🎯 Final Week Prep

Before interview:

- [ ] Solved 50+ problems easily
- [ ] Can solve medium in 25-30 min
- [ ] 3+ mock interviews done
- [ ] Weak areas reviewed
- [ ] Behavioral stories prepared (3-4)
- [ ] System design overview (if E4+)
- [ ] Practice whiteboarding (if coding on board)

---

## 📖 Resources

| Topic | Doc | Code | Practice |
|-------|-----|------|----------|
| Two-pointer | `two-pointer-techniques.md` | `two_pointer.py` | 10 |
| Sliding window | `sliding-window-patterns.md` | `sliding_window.py` | 8 |
| Trees | `graph-algorithms-mastery.md` | `graph.py` | 15 |
| Graphs | `graph-algorithms-mastery.md` | `graph.py` | 12 |
| DP | `dynamic-programming-mastery.md` | `dp.py` | 5 |

---

## ✅ Pre-Interview Checklist

- [ ] Can solve 2-3 medium problems per hour
- [ ] Explain approach before coding
- [ ] Write clean, bug-free code quickly
- [ ] Optimize solutions naturally
- [ ] Handle edge cases without prompting
- [ ] Ask good clarifying questions
- [ ] Done 3+ mock interviews
- [ ] Have 3-4 behavioral stories ready

---

**Last updated:** 2026-05-22

Good luck with Meta! 🚀
