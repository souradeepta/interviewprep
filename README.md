# 📚 InterviewPrep — Complete SDE Interview Preparation

A **comprehensive, tested** repository for software engineering interview preparation. Master **algorithms, system design, and interview frameworks** with **218 passing tests, 40+ interview patterns, and 2 mock interview agents**. Choose your learning path: **2 weeks, 4 weeks, or 8 weeks**.

---

## 🎯 Why This Repo Stands Out

✅ **Tested code, not just docs** — 218 passing tests across data structures, algorithms, and interview patterns. Run locally, see it work.

✅ **Pattern-focused learning** — Master 5 interview-winning patterns (two-pointer, sliding window, binary search, monotonic stack, prefix sum) with 40+ problems + complete solutions.

✅ **Multiple learning paths** — Choose by timeline (2/4/8 weeks), interview stage (phone screen, technical, system design), or learning style (step-by-step, dive deep, learn by doing).

✅ **Mock interview agents** — Practice live with AI interviewer & candidate agents via Claude ([AGENTS.md](AGENTS.md)). Real-time feedback and coaching.

---

## 🚀 Quick Start

### 🆕 **New Here?** (2 minutes)
→ **[GETTING_STARTED.md](GETTING_STARTED.md)** — Answer 3 questions, get your personalized learning path

### 💻 **Ready to Code?**
→ **[python/patterns/](python/patterns/)** — 40+ problems, fully tested. Pick a pattern and start solving.

### 🤖 **Want to Practice Interviews?**
→ **[AGENTS.md](AGENTS.md)** — Schedule a mock interview with Claude

### 🗺️ **Exploring the Full Repo?**
→ **[docs/STRUCTURE.md](docs/STRUCTURE.md)** — Complete navigation guide with visual maps

---

## 📦 What's Included

| Component | Coverage | Status |
|-----------|----------|--------|
| **Interview Frameworks** | 42 comprehensive guides (coding, system design, behavioral) | ✅ Complete |
| **Algorithms** | 11 mastery guides + 5 pattern modules (40+ problems) | ✅ Complete |
| **Data Structures** | 17 core structures with implementations | ✅ Complete |
| **System Design** | 39+ real-world case studies with architecture | ✅ Complete |
| **Code Examples** | Python + Java implementations, fully tested | ✅ Complete |
| **Test Suite** | 218 tests passing (patterns, DS, algorithms) | ✅ 218 passing |
| **Learning Paths** | 9 structured paths by timeline & style | ✅ Ready |
| **Mock Interviews** | 2 AI agents (interviewer, candidate) | ✅ Ready |

---

## 📚 Learning Paths

### By Timeline
- **[2-Week Intensive Sprint](learning-paths/sequential-tracks/2-week-sprint.md)** — 20 focused hours, phone screen prep
- **[4-Week Balanced Path](learning-paths/sequential-tracks/4-week-focused.md)** — 24-28 hours, technical round ← **Recommended**
- **[8-Week Comprehensive](learning-paths/sequential-tracks/8-week-comprehensive.md)** — 32-40 hours, system design deep dive

### By Interview Stage
- **[Phone Screen](learning-paths/interview-playbooks/phone-screen.md)** — Quick coding challenges
- **[Technical Round](learning-paths/interview-playbooks/technical-round.md)** — Medium-hard problems
- **[System Design](learning-paths/interview-playbooks/system-design-round.md)** — Architecture & trade-offs

### By Learning Style
- **[Depth-First](learning-paths/skill-trees/depth-first.md)** — Master each domain completely
- **[Breadth-First](learning-paths/skill-trees/breadth-first.md)** — Sample all domains, then specialize
- **[Learn by Doing](learning-paths/learn-by-doing.md)** — Code + tests guide you

---

## 🎯 Interview Patterns (40+ Problems)

Master these patterns and solve 80% of interview questions:

- **[Two-Pointer](python/patterns/two_pointer.py)** — 10 problems (arrays, linked lists, strings)
- **[Sliding Window](python/patterns/sliding_window.py)** — 9 problems (substrings, subarrays)
- **[Binary Search](python/patterns/binary_search.py)** — 8 problems (rotated arrays, boundaries)
- **[Monotonic Stack](python/patterns/monotonic_stack.py)** — 6 problems (next/previous element, histograms)
- **[Prefix Sum](python/patterns/prefix_sum.py)** — 6 problems (range queries, subarrays)

Each pattern includes:
- 📖 Concept explanation
- 💻 Multiple solution approaches
- 🧪 Test cases (run `pytest tests/patterns/ -v`)
- 🎯 LeetCode-style problems with difficulty

---

## 📂 Repository Structure

```
interviewprep/
├── GETTING_STARTED.md           # 👈 START HERE (new visitors)
├── AGENTS.md                    # Mock interview agents
├── README.md                    # This file
├── conftest.py                  # pytest configuration
│
├── 💻 python/                   # Python implementations
│   ├── patterns/                # 40+ interview pattern problems
│   │   ├── two_pointer.py       # 10 problems
│   │   ├── sliding_window.py    # 9 problems
│   │   ├── binary_search.py     # 8 problems
│   │   ├── monotonic_stack.py   # 6 problems
│   │   └── prefix_sum.py        # 6 problems
│   ├── basic/                   # Data structures (linked list, stack, queue, hashmap)
│   ├── algorithms/              # Sorting, searching, DP, graph algorithms
│   └── system_design/           # LRU cache, URL shortener, parking lot
│
├── 📖 docs/                     # Complete documentation
│   ├── _NAVIGATION.md           # Quick "where is X?" glossary
│   ├── STRUCTURE.md             # Full repo navigation (visual maps)
│   ├── 01-interview-frameworks/ # 42 interview guides
│   ├── 02-algorithms/           # Algorithm mastery & patterns
│   ├── 03-system-design/        # Real-world system designs
│   ├── 04-ai-ml-llms/           # AI/ML fundamentals (expanding)
│   └── 05-learning-paths/       # Structured learning tracks
│
├── 🧪 tests/                    # 218 passing tests
│   ├── patterns/                # Tests for 40+ pattern problems
│   ├── basic/                   # Tests for data structures
│   ├── algorithms/              # Tests for algorithms
│   └── system_design/           # Tests for system design
│
├── 📚 learning-paths/           # Structured learning journeys
│   ├── sequential-tracks/       # 2-week, 4-week, 8-week paths
│   ├── interview-playbooks/     # Stage-specific (phone, technical, SD)
│   └── skill-trees/             # Learning style options
│
└── 🎯 java/                     # Java implementations (same topics)
```

---

## 🧪 Run Tests Locally

```bash
# Clone the repo
git clone https://github.com/yourusername/interviewprep.git
cd interviewprep

# Run all tests (218 passing)
pytest -v

# Run just the interview patterns (40+ problems)
pytest tests/patterns/ -v

# Run a specific pattern
pytest tests/patterns/test_two_pointer.py -v
```

**All tests should pass** ✅ — that's how you know the solutions are correct.

---

## 🤖 Mock Interview Agents

Practice with two AI-powered agents:
- **Interviewer Agent** — Asks you questions, provides feedback
- **Candidate Agent** — You ask it questions, it codes

See [AGENTS.md](AGENTS.md) for setup and usage.

---

## 🎓 For Students & Juniors

This repo is **built for you**:
- ✅ Pathways for every timeline (2, 4, or 8 weeks)
- ✅ Frameworks that demystify interviews
- ✅ 40+ pattern problems with solutions
- ✅ Test cases show you the "right" answer
- ✅ Mock agents for live practice
- ✅ No paywalls, no upsells — completely free

---

## ❓ FAQ

**Q: Where do I start?**  
A: Go to [GETTING_STARTED.md](GETTING_STARTED.md) and answer 3 quick questions. Takes 2 minutes.

**Q: How long does this take?**  
A: Pick your timeline: 2 weeks (intensive), 4 weeks (balanced), or 8 weeks (deep).

**Q: Can I just code without reading docs?**  
A: Absolutely. Start with [python/patterns/](python/patterns/) and run the tests. Learning happens by doing.

**Q: Are these real interview problems?**  
A: Yes — all problems are from LeetCode, real company interviews, or common patterns. 40+ problems, fully tested.

**Q: Can I contribute?**  
A: Yes! See [CONTRIBUTING.md](CONTRIBUTING.md) (link TBD).

---

## 📊 Stats

- **218 passing tests** across all modules
- **40+ interview pattern problems** with full solutions
- **42 interview frameworks** covering coding, system design, behavioral
- **9 learning paths** for different timelines and goals
- **39+ system design case studies** with real architecture
- **Python + Java** implementations for every topic

---

## 🚀 Next Steps

1. **Go to [GETTING_STARTED.md](GETTING_STARTED.md)** — Find your learning path (2 min)
2. **Pick a pattern** — Start with [two-pointer](python/patterns/two_pointer.py) or [sliding window](python/patterns/sliding_window.py)
3. **Run tests** — `pytest tests/patterns/test_two_pointer.py -v` (verify solutions work)
4. **Solve problems** — Implement each one, compare with tests
5. **Practice interviews** — [AGENTS.md](AGENTS.md) (live mock rounds)

---

## 📄 License

Open source. Free to use, modify, share.

---

**Questions?** Check [docs/STRUCTURE.md](docs/STRUCTURE.md) for detailed navigation or open an issue.

**Ready?** [Get started →](GETTING_STARTED.md)
