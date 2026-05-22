# Public Repo Discoverability & Navigation Design

**Date:** May 22, 2026  
**Goal:** Make the interview prep repo more discoverable and friendly for first-time public visitors (students/juniors)  
**Approach:** Create a "Guided Tour Landing" with minimal changes to existing structure  

---

## Overview

### Problem Statement
The repo is comprehensive (218 tests, 40 interview patterns, 6 doc sections) but **structure is unclear**. First-time visitors face:
- Multiple starting points (README, learning paths, docs, code)
- Unclear which path is "right" for them
- Overwhelm from breadth of content

### Solution
Create a **frictionless entry point** (GETTING_STARTED.md) that routes new visitors to personalized learning paths based on 3 simple questions:
1. Time available (2/4/8 weeks)
2. Interview stage (phone screen / technical / system design)
3. Learning style (step-by-step / dive deep / learn by doing)

### User Journey
```
lands on GitHub repo 
→ README (what is this?) 
→ GETTING_STARTED.md (who am I? answer 3 Qs) 
→ personalized path (frameworks → code → practice) 
→ AGENTS.md (mock interview practice)
```

---

## Design Details

### 1. Modified README.md (~200 lines, down from 276)

**Goals:**
- Elevator pitch + value proposition
- Social proof (test count, quality signals)
- Single clear CTA to GETTING_STARTED.md
- Links for power users (STRUCTURE.md, AGENTS.md)

**Structure:**
```
# InterviewPrep — Complete SDE Interview Preparation

[1-sentence hook + badges: 218 tests, patterns, agents]

## Why This Repo Stands Out
- Tested code, not just docs (218 passing tests)
- Pattern-focused learning (5 patterns, 40+ problems)
- Multiple learning paths (2/4/8 weeks, 3 styles)
- Mock interview agents (live practice with Claude)

## Quick Navigation
- New here? → [GETTING_STARTED.md](GETTING_STARTED.md) ⭐
- Ready to code? → [python/patterns/](python/patterns/)
- Want to practice interviews? → [AGENTS.md](AGENTS.md)
- Exploring the full repo? → [docs/STRUCTURE.md](docs/STRUCTURE.md)

## What's Included (condensed table)
| Component | Coverage |
|-----------|----------|
| Interview Frameworks | 42 comprehensive guides |
| Algorithms | 11 mastery guides + 5 pattern modules |
| Data Structures | 17 structures with implementations |
| System Design | 39+ real-world case studies |
| Code Examples | Python + Java, fully tested |
| Test Suite | 218 tests passing |
| Learning Paths | 9 structured paths |
```

**Changes:** Condense content, add "Why This Repo" section, emphasize GETTING_STARTED CTA

---

### 2. New File: GETTING_STARTED.md (~150 lines)

**Purpose:** Quiz-based router that personalizes the learning experience

**Content Structure:**
```
# Getting Started — Find Your Path in 2 Minutes

## Answer 3 Quick Questions
(no wrong answers—we route to the right place)

### Q1: How much time do you have?
- [ ] 2 weeks (intensive sprint)
- [ ] 4 weeks (balanced, recommended)
- [ ] 8 weeks (comprehensive deep dive)

### Q2: What's your interview stage?
- [ ] Phone screen / coding challenges
- [ ] Technical round (medium-hard problems)
- [ ] System design round
- [ ] Not sure yet

### Q3: How do you learn best?
- [ ] Step-by-step guidance (read frameworks, then code)
- [ ] Dive deep (master topics thoroughly)
- [ ] Learn by doing (code first, understand after)

---

## Your Personalized Path

[Based on quiz combo, show:]

**Path Name:** e.g., "4-Week Balanced Technical Interview Path"
**Estimated Commitment:** 24-28 hours over 4 weeks
**What You'll Master:** [2-3 sentence summary]

### Week-by-Week Breakdown
- Week 1: Coding Fundamentals → read [framework link], practice [pattern link]
- Week 2: Algorithms Deep Dive → implement [code], run tests
- etc.

### Your Resources
- 📖 Frameworks: [curated list]
- 💻 Code Examples: [links to python/patterns/]
- 🧪 Practice: [which tests to run in what order]
- 🤖 Mock Interviews: [AGENTS.md](AGENTS.md)

---

## Other Paths

[Show brief list of alternative paths if user's combo isn't covered]

## Not Sure? 
→ [Explore the full repository](docs/STRUCTURE.md)
→ [Jump straight to coding](python/patterns/)
→ [Practice with agents](AGENTS.md)
```

**Routing table (internal reference for GETTING_STARTED logic):**

| Time | Stage | Style | → Suggested Path |
|------|-------|-------|------------------|
| 2w | Phone | Step-by-step | "Coding Fundamentals Sprint" |
| 2w | Phone | Deep | "Algorithms Mastery Sprint" |
| 2w | Phone | Doing | "2-Week Code-First Challenge" |
| 4w | Tech | Step-by-step | "4-Week Balanced Path" (recommended) |
| 4w | Tech | Deep | "Algorithms + Patterns Deep Dive" |
| 4w | Tech | Doing | "4-Week Build & Test Path" |
| 8w | SD | Step-by-step | "8-Week Full-Stack Journey" |
| 8w | SD | Deep | "System Design Mastery" |
| 8w | SD | Doing | "8-Week Project-Based Learning" |

---

### 3. New File: docs/_NAVIGATION.md (~80 lines)

**Purpose:** Quick glossary for "where is X?" questions

**Content:**
```
# Quick Navigation Guide

## By Topic
- **Two-pointer problems** → python/patterns/two_pointer.py + tests/patterns/test_two_pointer.py
- **Sliding window** → python/patterns/sliding_window.py + tests/patterns/test_sliding_window.py
- **Binary search** → python/patterns/binary_search.py + tests/patterns/test_binary_search.py
- [etc. for all patterns]

## By Concept
- **Interview frameworks** → docs/01-interview-frameworks/
- **Algorithm mastery guides** → docs/02-algorithms/
- **System design case studies** → docs/03-system-design/
- [etc.]

## By Learning Style
- **Read frameworks first** → docs/01-interview-frameworks/
- **Learn by coding** → python/patterns/ + python/algorithms/
- **Run tests immediately** → tests/ (and see GETTING_STARTED for curated order)
```

---

### 4. GitHub Repo Metadata

**Repository Description** (GitHub settings → About → Description):
```
Complete SDE interview prep: 218 passing tests, 40+ algorithm patterns, 
system design case studies, 9 learning paths, and mock interview agents. 
Master in 2-8 weeks. Python + Java implementations.
```

**Topics/Tags** (GitHub settings → About → Topics):
```
interview-prep, algorithms, data-structures, system-design, 
python, java, leetcode, interview-questions, learning-path
```

**README Badges** (top of README, after title):
```markdown
![Tests](https://img.shields.io/badge/tests-218%20passing-brightgreen)
![Python](https://img.shields.io/badge/python-3.12+-blue)
![Patterns](https://img.shields.io/badge/interview%20patterns-40%2B-brightgreen)
```

---

### 5. AGENTS.md — No changes needed
Remains the entry point for those who want to jump straight to live practice.

---

## Information Architecture

### Navigation Hierarchy
```
README.md (landing)
├── GETTING_STARTED.md (quiz-based routing)
│   ├── → specific learning path (in docs/)
│   │   ├── frameworks to read
│   │   ├── code to study (python/patterns/)
│   │   ├── tests to run
│   │   └── practice problems
│   └── → fallback: docs/STRUCTURE.md
├── AGENTS.md (live practice)
└── docs/STRUCTURE.md (power user navigation)
    ├── docs/_NAVIGATION.md (quick glossary)
    └── existing docs (unchanged)
```

### Files Modified
- `README.md` — condense, add "Why This Repo", emphasize GETTING_STARTED CTA
- Add GitHub metadata (description, topics)

### Files Created
- `GETTING_STARTED.md` (new routing guide)
- `docs/_NAVIGATION.md` (new quick glossary)
- `docs/superpowers/specs/2026-05-22-public-repo-discoverability-design.md` (this doc)

### Files Unchanged
- `AGENTS.md`
- All code (python/, java/, tests/)
- All existing docs (docs/01-06/)
- `docs/STRUCTURE.md`

---

## Success Criteria

✅ **Discoverability:**
- New visitor can find their learning path in <2 minutes
- GitHub search finds the repo via keywords (interview-prep, algorithms, etc.)
- README clearly explains what makes this repo unique

✅ **Retention:**
- Each learning path provides clear week-by-week guidance
- Every path includes code examples + tests (actionable, not just reading)
- Path includes path to mock interview practice (AGENTS.md)

✅ **Public Friendliness:**
- No jargon in navigation (GETTING_STARTED is plain English)
- Clear progression (understand → learn → practice)
- Visual signals of quality (test badges, clear structure)

---

## Implementation Notes

**Low risk:**
- GETTING_STARTED.md is additive (no changes to existing content)
- README changes are cosmetic (clarify and condense, no removal of info)
- GitHub metadata is external (repo content unchanged)

**Testing:**
- Manual: simulate new visitor journey (README → GETTING_STARTED → path → code)
- Verify all links are correct (broken links break the experience)
- Check that referenced code examples and tests exist

**Future Iterations:**
- Gather feedback from first 10 new users (which paths were most clicked?)
- Refine routing logic based on data
- Add video walkthroughs (optional enhancement)

---

## Summary

This design transforms the repo from a **comprehensive resource** (good for power users) into a **beginner-friendly, discoverable resource** (good for students + public). By adding a thin routing layer (GETTING_STARTED.md) and clarifying GitHub metadata, we make the repo much more accessible without disrupting existing structure or links.

The approach is **minimal, low-risk, and focused** on the core pain point: *"I found this repo, but where do I start?"*
