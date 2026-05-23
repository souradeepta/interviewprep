# Repository Reorganization Guide

Complete guide to the new repository structure.

---

## 🎯 What Changed?

### Before
```
datastructures/
├── python/
│   ├── patterns/
│   ├── basic/
│   ├── algorithms/
│   └── system_design/
├── java/
│   └── (similar)
├── docs/
│   ├── 01-interview-frameworks/
│   ├── 02-databases/
│   ├── 03-system-design/
│   ├── 04-ai-ml-llms/
│   └── ...
└── tests/
    └── (parallel to code structure)
```

### After
```
datastructures/
├── docs/
│   ├── 00-resources/
│   ├── 01-interview-frameworks/     (SAME)
│   ├── 02-databases/                (SAME)
│   ├── 03-system-design/            (SAME)
│   ├── 04-ai-ml-llms/               (SAME)
│   ├── 05-algorithms/               (NEW - organized by topic)
│   │   ├── README.md
│   │   ├── sorting/
│   │   │   ├── README.md (sorting guide)
│   │   │   └── code/
│   │   │       ├── python/
│   │   │       │   ├── sorting.py
│   │   │       │   └── test_sorting.py
│   │   │       └── java/
│   │   ├── searching/
│   │   ├── dp/
│   │   ├── graphs/
│   │   ├── string-algorithms/
│   │   ├── greedy/
│   │   ├── math/
│   │   ├── bit-manipulation/
│   │   └── geometry/
│   ├── 06-data-structures/          (NEW - organized by DS type)
│   │   ├── README.md
│   │   ├── arrays/
│   │   │   ├── README.md
│   │   │   └── code/
│   │   │       ├── python/
│   │   │       └── java/
│   │   ├── linked-lists/
│   │   ├── stacks/
│   │   ├── queues/
│   │   ├── trees/
│   │   │   ├── bst/
│   │   │   └── advanced/
│   │   ├── heaps/
│   │   ├── hash-tables/
│   │   ├── tries/
│   │   ├── graphs/
│   │   └── dsu/
│   ├── 07-patterns/                 (NEW - organized by interview pattern)
│   │   ├── README.md
│   │   ├── two-pointer/
│   │   │   ├── README.md
│   │   │   └── code/
│   │   │       ├── python/
│   │   │       └── java/
│   │   ├── sliding-window/
│   │   ├── binary-search/
│   │   ├── monotonic-stack/
│   │   └── prefix-sum/
│   └── 08-learning-paths/
├── tests/ (top-level, cross-references new locations)
│   ├── algorithms/
│   ├── data-structures/
│   ├── patterns/
│   └── ...
├── learning-paths/
├── python/ (empty or symlinks to docs)
├── java/ (empty or symlinks to docs)
└── ...
```

---

## 📍 File Migration Map

### Algorithms

| Old Location | New Location | Notes |
|---|---|---|
| `python/algorithms/sorting/` | `docs/05-algorithms/sorting/code/python/` | Code moved to docs |
| `python/algorithms/searching/` | `docs/05-algorithms/searching/code/python/` | Code moved to docs |
| `python/algorithms/dp/` | `docs/05-algorithms/dp/code/python/` | Code moved to docs |
| `python/algorithms/graph/` | `docs/05-algorithms/graphs/code/python/` | Renamed to graphs |
| `docs/02-algorithms/` | `docs/05-algorithms/` | Docs moved up one level |

### Data Structures

| Old Location | New Location | Notes |
|---|---|---|
| `python/basic/arrays.py` | `docs/06-data-structures/arrays/code/python/` | Code moved to docs |
| `python/basic/linked_list.py` | `docs/06-data-structures/linked-lists/code/python/` | Code moved to docs |
| `python/basic/stack.py` | `docs/06-data-structures/stacks/code/python/` | Code moved to docs |
| `python/basic/queue_ds.py` | `docs/06-data-structures/queues/code/python/` | Code moved to docs |

### Patterns

| Old Location | New Location | Notes |
|---|---|---|
| `python/patterns/two_pointer.py` | `docs/07-patterns/two-pointer/code/python/` | Code moved to docs |
| `python/patterns/sliding_window.py` | `docs/07-patterns/sliding-window/code/python/` | Code moved to docs |
| `python/patterns/binary_search.py` | `docs/07-patterns/binary-search/code/python/` | Code moved to docs |
| `python/patterns/monotonic_stack.py` | `docs/07-patterns/monotonic-stack/code/python/` | Code moved to docs |
| `python/patterns/prefix_sum.py` | `docs/07-patterns/prefix-sum/code/python/` | Code moved to docs |

### Tests

| Old Location | New Location | Notes |
|---|---|---|
| `tests/algorithms/` | `tests/algorithms/` | Updated to point to new code locations |
| `tests/basic/` | `tests/data-structures/` | Reorganized |
| `tests/patterns/` | `tests/patterns/` | Updated to point to new code locations |

---

## 🚀 Benefits of New Structure

### 1. **Topic-Centric Organization**
- All information about a topic in one place
- Documentation, code, and tests together
- Easier to learn and practice

### 2. **Better Navigation**
- Clear hierarchy: Topic → Subtopic → Implementations
- Python and Java side-by-side
- No jumping between directories

### 3. **Self-Contained Learning**
- Read guide, see code, solve problems
- All in one directory

### 4. **Cleaner Root**
- Code directories (python, java) become secondary
- Documentation is primary interface

---

## 🔍 Finding Things

### Old Way (Finding sorting implementations)
```
python/algorithms/sorting/sorting.py
java/algorithms/sorting/Sorting.java
docs/02-algorithms/sorting-algorithms-mastery.md
tests/algorithms/test_sorting.py
```

### New Way (All in one place!)
```
docs/05-algorithms/sorting/
├── README.md                              (guide & explanation)
├── code/
│   ├── python/
│   │   ├── sorting.py                     (implementations)
│   │   └── test_sorting.py                (tests)
│   └── java/
│       ├── Sorting.java
│       └── SortingTest.java
└── problems.md                            (LeetCode problems)
```

---

## 📚 New Top-Level Structure

```
docs/
├── 00-resources/              External resources, utilities
├── 01-interview-frameworks/   Interview guides & frameworks (UNCHANGED)
├── 02-databases/              Database systems (UNCHANGED)
├── 03-system-design/          System design patterns (UNCHANGED)
├── 04-ai-ml-llms/             AI/ML/LLM guides (UNCHANGED)
├── 05-algorithms/             🆕 Algorithms with code
├── 06-data-structures/        🆕 Data structures with code
├── 07-patterns/               🆕 Interview patterns with code
├── 08-learning-paths/         📚 Learning paths (moved from root)
└── README.md
```

---

## 🔗 How Code Relates to Docs

### For Each Topic:
```
topic/
├── README.md
│   ├── Concept explanation
│   ├── Key insights
│   ├── Time/space complexity
│   └── When to use
├── code/python/
│   ├── Implementation
│   ├── Multiple approaches
│   └── Tests
├── code/java/
│   ├── Implementation
│   ├── Multiple approaches
│   └── Tests
└── problems.md (LeetCode-style problems to practice)
```

---

## ✅ How to Use New Structure

### Learning a Concept
```
1. Read docs/05-algorithms/sorting/README.md
2. Study code in docs/05-algorithms/sorting/code/python/
3. Run tests: pytest docs/05-algorithms/sorting/code/python/
4. Solve problems in docs/05-algorithms/sorting/problems.md
```

### Finding Code
```
Need sorting implementation?
→ docs/05-algorithms/sorting/code/python/sorting.py

Need linked list implementation?
→ docs/06-data-structures/linked-lists/code/python/

Need two-pointer pattern?
→ docs/07-patterns/two-pointer/code/python/
```

### Finding Tests
```
All tests now:
→ tests/algorithms/
→ tests/data-structures/
→ tests/patterns/

Each test file imports from new docs location:
from docs.algorithms.sorting.code.python import sorting
```

---

## 🎯 Navigation Changes

### README Updates
- Root README now points to `docs/05-algorithms`, `docs/06-data-structures`, `docs/07-patterns`
- `docs/_NAVIGATION.md` updated to reference new structure
- Each topic has its own README

### Learning Paths
- `learning-paths/` moved to `docs/08-learning-paths/`
- Links updated to point to new code locations

### GETTING_STARTED.md
- Updated to guide users to new structure

---

## 🔄 Backward Compatibility

### Option 1: Symlinks (keep old paths working)
```bash
python/ → symlink to docs/05-algorithms/code/python + docs/06-data-structures/code/python + docs/07-patterns/code/python
java/ → similar
```

### Option 2: Deprecation notice
```
python/ contains: "See docs/05-algorithms, docs/06-data-structures, docs/07-patterns"
java/ contains: "See docs/05-algorithms, docs/06-data-structures, docs/07-patterns"
```

---

## 📊 Summary of Changes

| Aspect | Before | After | Benefit |
|---|---|---|---|
| Code location | `python/`, `java/` | `docs/*/code/python/`, `docs/*/code/java/` | Topics centered |
| Documentation | Separate from code | With code | Easy to learn |
| Navigation | Topic → Path mapping | Topic → Location | Intuitive |
| Tests | `tests/` (separate) | `docs/*/code/test_*.py` | Colocated |
| Total files | Same | Same | Organization improved |

---

## 🚀 Migration Checklist

- [ ] Create `docs/05-algorithms/` structure
- [ ] Create `docs/06-data-structures/` structure
- [ ] Create `docs/07-patterns/` structure
- [ ] Move Python algorithm implementations
- [ ] Move Java algorithm implementations
- [ ] Move tests to new structure
- [ ] Update imports in tests
- [ ] Update README files
- [ ] Update navigation files
- [ ] Test all code still runs
- [ ] Verify all tests pass
- [ ] Update git ignore (if needed)

---

**Migration Status:** In Progress ✏️

**Last updated:** 2026-05-22
