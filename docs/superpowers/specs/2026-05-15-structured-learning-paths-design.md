# Structured Learning Paths Design Spec

**Date:** 2026-05-15  
**Scope:** Comprehensive interview prep curriculum with domain-based learning, interview-phase playbooks, and skill trees  
**Status:** Design Phase

---

## 1. Overview

Transform the datastructures repository into a complete interview prep system with **structured learning paths**. Combine curated existing problems (~200+) with new problems (~50-100) into cohesive learning tracks that guide students from basics through system design.

### Goals
- ✅ Multiple entry points (choose by timeline, interview stage, learning style)
- ✅ Clear sequencing with time estimates and milestones
- ✅ Full curriculum: Data Structures → Algorithms → System Design → Design Patterns
- ✅ Beginner-friendly navigation while supporting depth exploration

---

## 2. Architecture

### 2.1 Directory Structure

```
learning-paths/
├── README.md                    # Master guide + quick start
├── index.md                     # "Choose your path" navigator
├── sequential-tracks/           # Time-based learning paths
│   ├── 2-week-sprint.md        # Intensive, focused prep
│   ├── 4-week-focused.md       # Balanced coverage
│   └── 8-week-comprehensive.md # Deep mastery
├── interview-playbooks/         # Stage-specific preparation
│   ├── phone-screen.md         # 30-45 min screening
│   ├── technical-round.md      # 45-60 min coding round
│   └── system-design-round.md  # 45-60 min system design
├── domains/                     # Deep dives by topic
│   ├── arrays.md
│   ├── strings.md
│   ├── linked-lists.md
│   ├── stacks-queues.md
│   ├── trees.md
│   ├── graphs.md
│   ├── heaps.md
│   ├── hash-tables.md
│   ├── dynamic-programming.md
│   ├── sorting-searching.md
│   ├── bit-manipulation.md
│   ├── design-patterns.md
│   └── system-design-fundamentals.md
└── skill-trees/                 # Branching paths
    ├── depth-first.md          # Master each domain fully
    └── breadth-first.md        # Sample all domains first
```

### 2.2 Content Format: Markdown with YAML Frontmatter

Each domain file includes metadata for discoverability and sequencing:

```yaml
---
domain: arrays
difficulty: "⭐-⭐⭐"
estimated_time: "6-8 hours"
prerequisites: []
covered_in_stages: [phone-screen, technical-round]
problem_count: 8
key_concepts: [prefix-sums, two-pointers, sliding-window, binary-search]
---

# Arrays

## Overview
[1-2 sentences on domain relevance]

## Key Concepts
- Two Pointers: [link to doc with explanation]
- Sliding Window: [link]
- Binary Search on Arrays: [link]

## Problem Sequence
1. [Name] — Easy, 30min
   Link: [to solution in repo]
   Pattern: Two pointers
   
2. [Name] — Medium, 45min
   Link: [to solution]
   Pattern: Sliding window
   
...

## Advanced Topics
[Optional deep dives for breadth-first learners]
```

---

## 3. Content Components

### 3.1 Sequential Tracks

**Purpose:** Time-boxed learning paths for students with different schedules.

Each track specifies:
- **Total commitment:** hours/week and total duration
- **Domain sequence:** order to learn topics (respects prerequisites)
- **Time allocation:** % breakdown across DS, algorithms, system design
- **Weekly milestones:** concrete progress targets
- **Daily/weekly schedule:** recommended study cadence

**Example: 4-week-focused.md**
```
# 4-Week Focused Interview Prep

Total: ~24-28 hours (6-7 hours/week)

## Week 1: Foundations (Arrays & Strings)
- Arrays (6-8h): links to problems 1-3
- Strings (4-6h): links to problems 1-3
- Milestone: Solve 6 problems, understand two-pointers + sliding-window

## Week 2: Complex Structures (Trees & Graphs)
- Trees (6-8h): links to problems 1-4
- Graphs (4-6h): links to problems 1-3
- Milestone: Solve 7 problems, master DFS/BFS

## Week 3: Algorithms (DP & Sorting)
- Dynamic Programming (6-8h): links to problems 1-4
- Sorting & Searching (4-6h): links to problems 1-3
- Milestone: Solve 7 problems, understand memoization patterns

## Week 4: System Design Intro + Review
- System Design Fundamentals (4-6h): links to 2-3 easy system designs
- Review (2-4h): revisit weak areas from weeks 1-3
- Milestone: Complete 1 mini system design, pass mock interview
```

**Variants:**
- 2-week-sprint: Covers only phone-screen + early technical-round domains
- 8-week-comprehensive: Deeper problems, design patterns, advanced system design

### 3.2 Interview Playbooks

**Purpose:** Stage-specific preparation (what matters most for each interview phase).

Each playbook:
- **Interview format:** Duration, problem types, typical difficulty
- **Must-know domains:** What to focus on (e.g., phone screen = arrays, strings, easy problems)
- **Curated problems:** Top 3-5 canonical problems to master completely
- **Common patterns:** Recurring question types in that stage
- **Interview flow:** How to spend the 45-60 minutes
- **Quick reference:** 1-page cheat sheet before interview

**Example: phone-screen.md**
```
# Phone Screen Interview Prep

**Format:** 30-45 min interview, 1 easy problem, often 1 simple follow-up

**Must-Master Domains:** Arrays, Strings
**Secondary:** Hash Tables (common follow-ups)

**Top 5 Problems to Ace:**
1. Two Sum (Easy) → [solution link]
2. Valid Parentheses (Easy) → [solution link]
3. Reverse String (Easy) → [solution link]
4. Remove Duplicates from Sorted Array (Easy) → [solution link]
5. Majority Element (Easy) → [solution link]

**Common Patterns:**
- Two pointers: [explanation + examples]
- Hash maps for deduplication: [explanation + examples]

**Interview Flow:**
- 0-2 min: Clarify problem
- 2-5 min: Whiteboard approach
- 5-20 min: Implement
- 20-25 min: Test edge cases
- 25-30 min: Optimize (if time)

**Quick Reference Cheat Sheet:**
[1-page summary of key patterns, gotchas, time complexities]
```

### 3.3 Domains

**Purpose:** Deep dives for learners who want to master a single topic.

Each domain file covers:
- **Overview:** What the data structure/topic is, why it matters
- **Key concepts:** Core ideas with links to implementations in repo
- **Problem sequence:** 5-10 canonical problems, ordered by difficulty
- **Variants & extensions:** Related problems (e.g., "2-sum variants" for arrays)
- **Common mistakes:** Pitfalls to avoid
- **Advanced topics:** (optional) Deeper exploration for ambitious learners

**Metadata:**
- Difficulty range (e.g., ⭐-⭐⭐)
- Estimated time to master (6-8 hours)
- Prerequisites (e.g., arrays before trees)
- Interview stages where this domain appears (phone-screen, technical-round, system-design)

### 3.4 Skill Trees

**Purpose:** Alternative learning paths (depth vs. breadth trade-off).

**Depth-First Tree:**
- "Become an expert in one domain before moving to the next"
- Start with arrays → complete all problems & understand theory → move to strings
- Recommended for: Deep preparation, one specific interview round

**Breadth-First Tree:**
- "Sample all domains, then deepen weaknesses"
- Week 1: One easy problem from each of 12 domains
- Week 2: One medium from each domain (or focus on top 6)
- Week 3-4: Deep dive into weakest 3 domains
- Recommended for: Balanced coverage, last-minute prep

Each skill tree:
- Maps to sequential tracks (which week to complete which domain)
- Explains the philosophy and when to choose it
- Provides explicit branching points (where learners can customize)

---

## 4. Content Population Strategy

### 4.1 Phase 1: Audit & Curate Existing Content

**Actions:**
1. Scan existing repo for ~200+ implemented problems:
   - Data structure implementations (17 DS files)
   - System design problems (39 documented)
   - Algorithm implementations (sorting, DP, graph algorithms)
   - Design patterns (23 Gang of Four patterns)

2. Map each to:
   - Domain (which category: arrays, trees, graphs, etc.)
   - Difficulty (easy/medium/hard based on problem complexity)
   - Time estimate (based on solution length and complexity)
   - Interview stage (phone-screen, technical-round, system-design, or design-patterns)
   - Solution link (where to find it in repo)

3. Create a mapping document (internal reference, not public):
   ```
   problems.csv:
   name, domain, difficulty, time_est_min, stages, link, description
   Two Sum, arrays, easy, 30, phone-screen;technical-round, python/basic/..., ...
   ```

### 4.2 Phase 2: Identify Gaps & Plan New Content

**Analysis:**
1. Count problems per domain in current repo
2. Identify underrepresented domains (target: 5-10 problems per domain)
3. Identify missing problem variants (e.g., "2-sum with target" missing)
4. Identify missing difficulty tiers (e.g., medium problems sparse in some domains)

**Planned new problems:** 
- **Target:** 8-10 problems per domain (minimum viable)
- **Stretch:** 20-30 per domain (comprehensive coverage)
- **Priority:** Canonical problems (high-value, widely-asked in interviews)
- **Delivery:** Python + Java solutions, added to existing domain folders
- **Decision point:** Start with 8-10 per domain; expand if time permits

*Recommendation:* Begin with 8-10 per domain (~50-80 new problems total). This covers 2-week sprint through 4-week focused tracks. 8-week comprehensive can use existing variants and advanced topics without adding many new problems.

### 4.3 Phase 3: Sequence Problems & Populate Tracks

**Actions:**
1. Sort problems within each domain by difficulty
2. Assign to sequential tracks:
   - 2-week sprint: 30-40 problems total (focus: easy + essential mediums)
   - 4-week focused: 50-60 problems (full range, essential only)
   - 8-week comprehensive: 80-100 problems (all tiers, all variants)

3. Assign to interview playbooks:
   - Phone screen: Easy problems, arrays/strings/hashes (top 5 per domain)
   - Technical round: Medium problems, all domains (top 7 per domain)
   - System design: System design fundamentals + advanced patterns

4. Populate skill trees:
   - Depth-first: Full problem sequence per domain
   - Breadth-first: One easy + one medium from each domain

---

## 5. Navigation & Cross-Linking

### 5.1 Entry Points

**index.md** ("Choose Your Path")
- "Learning for the first time?" → sequential-tracks/4-week-focused.md
- "Have a phone screen next week?" → interview-playbooks/phone-screen.md
- "Want to master one topic?" → domains/ (picker)
- "Prefer depth or breadth?" → skill-trees/ (picker)

### 5.2 Internal Links

- **Sequential tracks** → Link to domain files for deep dives
- **Interview playbooks** → Link to curated problem sequences in domain files
- **Domains** → Link to related algorithms, design patterns, system design concepts
- **Skill trees** → Explicit mapping to sequential tracks with branching recommendations

### 5.3 Cross-References

- Problems link to: data structure docs, algorithm explanations, design patterns
- System design fundamentals link to: caching, databases, networks (in system-design/)
- Design patterns link to: where they're used in real system designs

---

## 6. File Format & Conventions

### 6.1 Markdown Conventions

- **Headers:** `#` for domain, `##` for sections, `###` for subsections
- **Code blocks:** Language-tagged (python, java, bash)
- **Links:** Relative links to files in repo (e.g., `../../../python/basic/array.py`)
- **Metadata:** YAML frontmatter at top of each file

### 6.2 Problem Links

Each problem entry follows this format:
```markdown
1. **Two Sum** (Easy, 30 min)
   - **Pattern:** Hash map, two pointers
   - **Interview Stages:** Phone screen, technical round
   - **Solutions:** 
     - [Python](../../python/basic/array.py#two_sum)
     - [Java](../../java/basic/TwoSum.java)
   - **Follow-ups:** Sorted array variant, three-sum, k-sum
```

### 6.3 Time Estimates

- Format: "X-Y hours" or "X-Y minutes" depending on granularity
- Includes: reading time + implementation time + testing
- Assumes: No prior knowledge of the pattern

---

## 7. Success Criteria

✅ **Navigability:** Beginner can follow index.md → chosen path → domain → problem → solution without confusion  
✅ **Completeness:** All major interview topics covered (DS, algorithms, system design, patterns)  
✅ **Sequencing:** Problems within each domain are ordered by difficulty; domains are ordered by prerequisite dependency  
✅ **Time Accuracy:** Estimates match actual time taken by target audience (±20%)  
✅ **Discoverability:** Every problem appears in at least 2 paths (sequential track + playbook OR playbook + skill tree)  
✅ **Scalability:** Easy to add new problems without restructuring  

---

## 8. Future Enhancements (Out of Scope)

- Interactive progress tracking (checkboxes, completion %)
- Spaced repetition / reminder system
- Video explanations
- Community notes / discussion threads
- Auto-generated learning dashboard from YAML config

---

## 9. Design Decisions

1. **Problem count per domain:** 8-10 canonical problems per domain (meets 2-week through 4-week tracks). 8-week comprehensive uses existing variants + advanced topics without requiring many new problems.

2. **New problem authorship:** Identify gaps first via audit (Phase 1). For missing problems, AI drafts solutions; user reviews for quality/relevance.

3. **Time estimate granularity:** Domain-level estimates in sequential tracks (e.g., "Arrays: 6-8 hours"). Problem-level estimates in domain deep-dives.

4. **System design coverage:** Fundamentals only in learning-paths (core concepts + 2-3 easy problems per stage). Full 39-problem coverage remains in system_design/ directory and linked from 8-week track.

---

## 10. Implementation Plan (Next Step)

1. Write `index.md` (choose-your-path navigator)
2. Write `README.md` (master guide)
3. Create 13 domain files with problem sequences
4. Populate 3 sequential tracks
5. Populate 3 interview playbooks
6. Create 2 skill tree files
7. Add 50-100 new curated problems (fill gaps)
8. Validate all links and metadata

**Estimated effort:** 40-60 hours (including new problem creation)

---

## Appendix A: Example Domain File Structure

See section 3.3 for complete format.

## Appendix B: Example Sequential Track Structure

See section 3.1 for complete format.

## Appendix C: Problem Mapping Template

```yaml
Problem:
  name: "Two Sum"
  domain: "arrays"
  difficulty: "easy"
  time_estimate: "30 min"
  interview_stages:
    - phone-screen
    - technical-round
  key_patterns:
    - hash-map
    - two-pointers
  solutions:
    python: "python/basic/array.py#two_sum"
    java: "java/basic/TwoSum.java"
  follow_ups:
    - "Sorted array variant"
    - "Three-sum"
    - "K-sum"
```
