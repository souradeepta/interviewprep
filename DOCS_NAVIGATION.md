# 📚 Documentation Navigation Guide

Lost in the docs? Start here to find exactly what you're looking for.

---

## 🎯 I Want To...

### **...Get Started with Interview Prep**
1. [LEARNING_PATHS_QUICK_START.md](LEARNING_PATHS_QUICK_START.md) ← Start here (2 min read)
2. [learning-paths/index.md](learning-paths/index.md) ← Choose your path
3. Pick a path and follow the weekly schedule

### **...Practice with Mock Interviews**
→ [AGENTS.md](AGENTS.md) — Set up and use the mock interviewer and candidate agents

### **...Learn a Specific Data Structure**
→ [docs/basic/](docs/basic/) — Quick explanations with Python + Java code  
→ [docs/advanced/](docs/advanced/) — For complex structures  
→ [docs/new_ds/](docs/new_ds/) — For specialized/rare structures

### **...Master an Algorithm**
→ [docs/algorithms/](docs/algorithms/) — Sorting, searching, DP, graph algorithms

### **...Understand System Design**
→ [docs/system_design/README.md](docs/system_design/README.md) — 39 system design problems  
→ [learning-paths/interview-playbooks/system-design-round.md](learning-paths/interview-playbooks/system-design-round.md) — Interview playbook

### **...Learn Design Patterns**
→ [docs/patterns/design-patterns-guide.md](docs/patterns/design-patterns-guide.md) — 23 Gang of Four patterns  
→ [learning-paths/domains/design-patterns.md](learning-paths/domains/design-patterns.md) — Integrated with interview prep

### **...Find a Specific Problem or Topic**
→ [INDEX.md](INDEX.md) — Complete index of all problems and topics

### **...Prepare for a Specific Interview Stage**
- **Phone Screen (30-45 min)** → [learning-paths/interview-playbooks/phone-screen.md](learning-paths/interview-playbooks/phone-screen.md)
- **Technical Interview (45-60 min)** → [learning-paths/interview-playbooks/technical-round.md](learning-paths/interview-playbooks/technical-round.md)
- **System Design (45-60 min)** → [learning-paths/interview-playbooks/system-design-round.md](learning-paths/interview-playbooks/system-design-round.md)

### **...Review Quick Reference Materials**
→ [QUICK_REFERENCE.md](QUICK_REFERENCE.md) — Complexity tables, common patterns, quick lookups

### **...See What Problems Are Available**
→ [docs/new_problems/PROBLEM_DEFINITIONS.md](docs/new_problems/PROBLEM_DEFINITIONS.md) — All 58 new problems with specs

### **...Check the Full Learning Paths Directory**
→ [learning-paths/README.md](learning-paths/README.md) — Complete overview

---

## 📂 Documentation Structure

### **Root Level** (Customer-Facing)
```
README.md                                  # Main entry point
LEARNING_PATHS_QUICK_START.md             # Quick start (2 min)
AGENTS.md                                 # Mock interview setup
QUICK_REFERENCE.md                        # Complexity & quick ref
INDEX.md                                  # Complete index
DOCS_NAVIGATION.md                        # This file
```

### **learning-paths/** (Interview Prep Paths)
```
learning-paths/
├── index.md                              # Path selector
├── README.md                             # Master guide
├── sequential-tracks/                   # Time-based paths
│   ├── 2-week-sprint.md
│   ├── 4-week-focused.md
│   └── 8-week-comprehensive.md
├── interview-playbooks/                 # Stage-specific
│   ├── phone-screen.md
│   ├── technical-round.md
│   └── system-design-round.md
├── domains/                             # 13 deep dives
│   ├── arrays.md
│   ├── strings.md
│   └── ... (11 more)
└── skill-trees/                         # Learning styles
    ├── depth-first.md
    └── breadth-first.md
```

### **docs/** (Reference Material)
```
docs/
├── README.md                            # Docs overview
├── basic/                               # 6 basic data structures
├── advanced/                            # 10 advanced structures
├── new_ds/                              # 12 specialized structures
├── algorithms/                          # Sorting, DP, graph, etc.
├── patterns/
│   ├── problem-to-pattern-matcher.md   # Recognize problem types
│   ├── design-patterns-guide.md        # 23 Gang of Four
│   └── {domain}-problems.md            # Problem patterns per domain
├── system_design/
│   ├── README.md                       # 39 system design problems
│   └── {problem-name}/                 # Detailed designs
└── new_problems/
    ├── PROBLEM_DEFINITIONS.md          # All 58 new problems
    ├── TEMPLATE.md                     # Code structure template
    └── README.md                       # Implementation guide
```

### **python/ and java/**
```
python/                                 # Python implementations
├── basic/                              # Basic structures
├── advanced/                           # Advanced structures
├── new_ds/                             # Specialized structures
├── algorithms/                         # Algorithm implementations
└── new_problems/                       # New problem solutions

java/                                   # Java implementations (mirrors python/)
```

### **.claude/** (Internal - Hidden)
```
.claude/
├── agents/                             # Mock interview agents
│   ├── sde2-interviewer.md
│   └── sde-candidate.md
├── scripts/                            # Internal utility scripts
│   ├── enhance_docs_local.py
│   ├── enhance_with_docs.py
│   └── fix_system_design_docs.py
└── superpowers/                        # Planning & design specs
    ├── specs/                          # Design specifications
    └── plans/                          # Implementation plans
```

---

## 🗺️ Navigation by Use Case

### **I'm Preparing for Interviews (Most Users)**
1. Start: [LEARNING_PATHS_QUICK_START.md](LEARNING_PATHS_QUICK_START.md)
2. Choose: [learning-paths/index.md](learning-paths/index.md)
3. Follow: Weekly path from sequential tracks or playbook
4. Reference: [docs/basic/](docs/basic/), [docs/advanced/](docs/advanced/)
5. Practice: [AGENTS.md](AGENTS.md)

### **I'm Looking for Reference Material**
1. Check: [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for quick lookups
2. Deep dive: [docs/](docs/) for specific topics
3. Index: [INDEX.md](INDEX.md) to find anything

### **I'm Implementing Solutions**
1. See examples: [python/basic/](python/basic/) or [java/basic/](java/basic/)
2. Understand first: Read the corresponding [docs/basic/](docs/basic/) file
3. Implement: Code along with the documentation

### **I'm Teaching or Mentoring**
1. Reference: [docs/patterns/design-patterns-guide.md](docs/patterns/design-patterns-guide.md)
2. Problems: [docs/patterns/problem-to-pattern-matcher.md](docs/patterns/problem-to-pattern-matcher.md)
3. System design: [docs/system_design/README.md](docs/system_design/README.md)

---

## 📑 Key Documents at a Glance

| Document | Purpose | Read Time |
|----------|---------|-----------|
| [README.md](README.md) | Main entry point | 3 min |
| [LEARNING_PATHS_QUICK_START.md](LEARNING_PATHS_QUICK_START.md) | Get started fast | 2 min |
| [learning-paths/index.md](learning-paths/index.md) | Choose your path | 3 min |
| [AGENTS.md](AGENTS.md) | Set up mock interviews | 5 min |
| [QUICK_REFERENCE.md](QUICK_REFERENCE.md) | Quick lookups | 5 min |
| [INDEX.md](INDEX.md) | Complete index | 10 min |
| [docs/README.md](docs/README.md) | Documentation overview | 5 min |
| [LEARNING_PATHS_COMPLETION_CHECKLIST.md](LEARNING_PATHS_COMPLETION_CHECKLIST.md) | What's included | 10 min |

---

## 💡 Pro Tips

1. **First time?** → Start with [LEARNING_PATHS_QUICK_START.md](LEARNING_PATHS_QUICK_START.md)
2. **Overwhelmed?** → [learning-paths/index.md](learning-paths/index.md) has a recommendation
3. **Need reference?** → [QUICK_REFERENCE.md](QUICK_REFERENCE.md) has cheat sheets
4. **Can't find something?** → [INDEX.md](INDEX.md) is your friend
5. **Want to practice?** → [AGENTS.md](AGENTS.md) sets up mock interviews

---

## 🔍 Search Tips

- **"How do I..."** → Check [learning-paths/README.md](learning-paths/README.md)
- **"What is..."** → Search in [docs/README.md](docs/README.md)
- **"Show me an example..."** → Look in [python/](python/) or [java/](java/)
- **"When should I use..."** → Check [docs/patterns/](docs/patterns/)
- **"Complexity of..."** → See [QUICK_REFERENCE.md](QUICK_REFERENCE.md)

---

**Still lost?** Open [INDEX.md](INDEX.md) and search for your topic!
