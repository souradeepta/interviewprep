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

### 📚 **Find Any Guide by Level, Topic, or Time?**
→ **[docs/INDEX.md](docs/INDEX.md)** — Master index: find any guide by level, topic, or time-to-read

---

## 📦 What's Included

| Component | Coverage | Status |
|-----------|----------|--------|
| **Interview Frameworks** | 44 comprehensive guides (coding, system design, behavioral, databases, networking) | ✅ Complete |
| **Algorithms** | 11 mastery guides + 5 pattern modules (40+ problems) | ✅ Complete |
| **Data Structures** | 17 core structures with implementations | ✅ Complete |
| **System Design** | 39+ real-world case studies with architecture | ✅ Complete |
| **AI/ML/LLMs** | 9 guides (ML fundamentals, transformers, prompt engineering, RAG, fine-tuning) | ✅ Complete |
| **Code Examples** | Python + Java implementations, fully tested | ✅ Complete |
| **Test Suite** | 218 tests passing (patterns, DS, algorithms) | ✅ 218 passing |
| **Learning Paths** | 13 structured paths (timeline, stage, company-specific, style) | ✅ Ready |
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

### By Company
- **[Google](learning-paths/company-specific/google-interview-prep.md)** — Focus on graph algorithms, optimization, system design
- **[Meta](learning-paths/company-specific/meta-interview-prep.md)** — Speed & optimization, array/string focus
- **[Amazon](learning-paths/company-specific/amazon-interview-prep.md)** — Leadership principles, balanced coverage
- **[Microsoft & Apple](learning-paths/company-specific/microsoft-and-apple.md)** — Fundamentals & efficiency

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

## 🤖 AI/ML/LLMs Learning Path

Master modern AI systems:

- **[ML Fundamentals](docs/04-ai-ml-llms/01-ml-fundamentals.md)** — Core concepts, algorithms, metrics
- **[Neural Networks](docs/04-ai-ml-llms/02-neural-networks-basics.md)** — Perceptrons, backpropagation, optimization
- **[Deep Learning](docs/04-ai-ml-llms/03-deep-learning-essentials.md)** — CNNs, RNNs, LSTMs, attention
- **[LLM Architecture](docs/04-ai-ml-llms/04-llm-architecture.md)** — Transformers, attention mechanisms, scaling laws
- **[Prompt Engineering](docs/04-ai-ml-llms/05-prompt-engineering.md)** — Techniques, chain-of-thought, few-shot learning
- **[RAG Systems](docs/04-ai-ml-llms/06-rag-systems.md)** — Retrieval-augmented generation, vector databases
- **[Fine-tuning](docs/04-ai-ml-llms/07-fine-tuning-training.md)** — LoRA, instruction tuning, RLHF
- **[Model Serving](docs/04-ai-ml-llms/08-model-serving-inference.md)** — Quantization, batching, inference optimization
- **[ML Systems Design](docs/04-ai-ml-llms/10-ml-systems-design.md)** — End-to-end pipelines, monitoring, retraining

Each guide includes:
- 📖 Detailed explanations with examples
- 💡 Interview-style Q&A
- 🎯 Real-world applications
- ✅ Checklists for verification

---

## 📊 Fundamentals Coverage

Beyond algorithms and data structures:

- **[Database Fundamentals](docs/01-interview-frameworks/database-fundamentals.md)** — SQL, NoSQL, indexing, optimization, ACID
- **[Networking Fundamentals](docs/01-interview-frameworks/networking-fundamentals.md)** — HTTP, TCP/IP, DNS, latency, bandwidth

---

## 📂 Repository Structure (Reorganized)

**Topics on the outside, code implementations inside** ✨

```
interviewprep/
├── GETTING_STARTED.md           # 👈 START HERE (new visitors)
├── AGENTS.md                    # Mock interview agents
├── README.md                    # This file
├── conftest.py                  # pytest configuration
│
├── 📖 docs/                     # Complete documentation & code
│   ├── 00-resources/            # Utilities and helper materials
│   ├── 01-interview-frameworks/ # 42 interview guides (unchanged)
│   ├── 02-databases/            # Database systems (unchanged)
│   ├── 03-system-design/        # System design patterns (unchanged)
│   ├── 04-ai-ml-llms/           # AI/ML/LLM guides (unchanged)
│   │
│   ├── 05-algorithms/ 🆕        # Algorithms organized by type
│   │   ├── README.md            # Algorithm overview
│   │   ├── sorting/
│   │   │   ├── README.md        # Sorting guide
│   │   │   └── code/
│   │   │       ├── python/      # Python implementations & tests
│   │   │       └── java/        # Java implementations & tests
│   │   ├── searching/
│   │   ├── dp/
│   │   ├── graphs/
│   │   ├── string-algorithms/
│   │   ├── greedy/
│   │   ├── math/
│   │   ├── bit-manipulation/
│   │   └── geometry/
│   │
│   ├── 06-data-structures/ 🆕  # Data structures by type
│   │   ├── README.md            # DS overview
│   │   ├── arrays/
│   │   │   ├── README.md        # Arrays guide
│   │   │   └── code/
│   │   │       ├── python/      # Implementations & tests
│   │   │       └── java/
│   │   ├── linked-lists/
│   │   ├── stacks/
│   │   ├── queues/
│   │   ├── trees/
│   │   ├── heaps/
│   │   ├── hash-tables/
│   │   ├── tries/
│   │   ├── graphs/
│   │   └── dsu/
│   │
│   ├── 07-patterns/ 🆕          # Interview patterns (40+ problems)
│   │   ├── README.md            # Patterns overview
│   │   ├── two-pointer/
│   │   │   ├── README.md        # Two-pointer guide
│   │   │   ├── code/
│   │   │   │   ├── python/      # Implementations & tests
│   │   │   │   └── java/
│   │   │   └── problems.md      # LeetCode problems
│   │   ├── sliding-window/
│   │   ├── binary-search/
│   │   ├── monotonic-stack/
│   │   └── prefix-sum/
│   │
│   ├── 08-learning-paths/       # Structured learning journeys
│   ├── _NAVIGATION.md           # Quick navigation guide
│   ├── STRUCTURE.md             # Full documentation map
│   └── REORGANIZATION_GUIDE.md  # Migration guide (what changed)
│
├── 🧪 tests/                    # 218+ passing tests
│   ├── algorithms/              # Tests for algorithms
│   ├── data-structures/         # Tests for data structures
│   ├── patterns/                # Tests for patterns
│   └── system_design/           # Tests for system design
│
├── 📚 learning-paths/           # Learning tracks (also in docs/08-learning-paths/)
│
├── 💻 python/ (deprecated)      # Old location (use docs/*/code/python/ instead)
├── 🎯 java/ (deprecated)        # Old location (use docs/*/code/java/ instead)
└── ...
```

---

### **Key Benefits of New Structure**

✅ **Topics Centered** — All info about one topic in one place  
✅ **Code with Docs** — Guide, implementation, and tests together  
✅ **Easy Navigation** — Documentation first, code second  
✅ **Self-Contained** — Learn → code → practice in one directory  
✅ **Multi-Language** — Python and Java side-by-side  

See [REORGANIZATION_GUIDE.md](docs/REORGANIZATION_GUIDE.md) for details.

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
