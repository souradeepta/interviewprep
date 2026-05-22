# Archived Temporary & Working Files

This folder contains temporary files, working documents, logs, and analysis artifacts that were generated during repo development and enhancement.

## Files Index

### CSV & Data Files

- **`_problem_map.csv`** (14 KB)
  - Data structure and problem inventory
  - Columns: name, domain, language, path, difficulty, time_estimate, stages, notes
  - Lists: B-trees, AVL trees, LRU cache, graphs, segment trees, tries, heaps, design patterns, etc.
  - Status: Superseded by actual implementations in python/ and java/ directories

### Text Reports & Checklists

- **`ENHANCEMENT_REPORT.txt`** (16 KB)
  - Summary of repo enhancement work
  - Lists completed tasks and improvements
  - Working document from development process

- **`DOCUMENTATION_ENHANCEMENT_REPORT.txt`** (4.7 KB)
  - Report on documentation improvements
  - Lists doc enhancements and additions

- **`ADVANCED_DS_IMPLEMENTATIONS.txt`** (6.4 KB)
  - Checklist of advanced data structure implementations
  - Status of complex DS (segment trees, Fenwick trees, etc.)

- **`ALGORITHMS_CHECKLIST.txt`** (9 KB)
  - Checklist of algorithm implementations
  - Coverage tracking for sorting, searching, DP, graph algorithms

- **`_gap_analysis.txt`** (2.5 KB)
  - Analysis of gaps in original repo
  - Features/topics that were missing

### Logs

- **`logs/`** directory
  - `enhancement_20260515_105436.log` — Enhancement process logs (May 15, 2026)
  - `enhancement_20260515_105518.log` — Enhancement process logs (May 15, 2026)
  - Timestamped logs from repo enhancement and script execution

---

## Why These Are Archived

These files represent:
- **Intermediate work products** — Created during development, now superseded by final implementations
- **Analysis snapshots** — Gap analysis and planning documents from earlier phases
- **Build artifacts** — Logs and reports from enhancement scripts

The actual source code (in `python/` and `java/`) and final documentation (in docs/01-06/) are the canonical versions.

---

## When to Reference

- **Development history:** Check logs if debugging why certain changes were made
- **Coverage tracking:** Use checklists to understand what was originally planned vs. implemented
- **Problem inventory:** Reference `_problem_map.csv` to see the original problem/DS mapping before reorganization

---

## Moving Forward

These files are kept for historical reference but don't need to be in the main repo view. New visitors should focus on:
- 📖 `docs/` — Current documentation
- 💻 `python/` and `java/` — Actual implementations
- 📚 `learning-paths/` — Structured learning resources
- 🧪 `tests/` — Test suite

