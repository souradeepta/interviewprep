# SDE Interview Prep — Complete Resource

> Comprehensive interview preparation for engineers at all levels: intern through principal.
> 49 fully-built guides, 218 passing test cases, 5 coding pattern libraries.

---

## I am preparing for...

### A FAANG/top-tier onsite in the next 2 weeks
→ [2-week sprint plan](learning-paths/sequential-tracks/2-week-sprint.md) + company-specific prep: [Google](learning-paths/company-specific/google-interview-prep.md) · [Meta](learning-paths/company-specific/meta-interview-prep.md) · [Amazon](learning-paths/company-specific/amazon-interview-prep.md) · [more](learning-paths/company-specific/)

### My first serious tech interview (new grad / intern)
→ [8-week comprehensive plan](learning-paths/sequential-tracks/8-week-comprehensive.md) — start with [coding patterns](docs/07-patterns/README.md) and [interview framework](docs/01-interview-frameworks/coding-interview-framework.md)

### A senior (L5) system design round
→ [System design playbook](learning-paths/interview-playbooks/system-design-round.md) + [database deep dives](docs/02-databases/) + [AI/ML systems](docs/04-ai-ml-llms/)

### A staff / principal (L6+) loop
→ Senior/staff track *(coming soon)* — RFC writing, ambiguity, cross-team influence, bar-raiser prep

### Brushing up on a specific topic
→ [Master Index](docs/INDEX.md) — find any guide by level, topic, or time-to-read

---

## What's built

| Section | Status | What you get |
|---------|--------|--------------|
| [Databases](docs/02-databases/) | Complete | 30 guides: SQL through distributed, sharding, consensus. Exercises + Q&A. |
| [AI/ML & LLMs](docs/04-ai-ml-llms/) | Complete | 19 guides: fundamentals through LLMOps, RAG, fine-tuning. |
| [Interview Frameworks](docs/01-interview-frameworks/) | Partial | 52 tactical guides: how to approach coding, system design, behavioral rounds. Needs exercises. |
| [Coding Patterns](docs/07-patterns/) | In progress | README + problem lists. Full walkthroughs coming. |
| [Data Structures](docs/06-data-structures/) | In progress | Outline only. Full guides coming. |
| [Algorithms](docs/05-algorithms/) | In progress | Outline only. Full guides coming. |
| [System Design](docs/03-system-design/) | In progress | Outline only. 39 case studies coming. |

---

## Run the code

218 tests passing across 5 pattern libraries:

```bash
git clone <repo>
cd datastructures
pip install pytest
pytest tests/ -v
```

Coding patterns: two-pointer · sliding window · binary search · monotonic stack · prefix sum

Run a single pattern:
```bash
pytest tests/patterns/test_two_pointer.py -v
```

---

## Learning paths

| Goal | Time | Path |
|------|------|------|
| Quick prep | 2 weeks | [2-week sprint](learning-paths/sequential-tracks/2-week-sprint.md) |
| Solid foundation | 4 weeks | [4-week focused](learning-paths/sequential-tracks/4-week-focused.md) |
| Deep mastery | 8 weeks | [8-week comprehensive](learning-paths/sequential-tracks/8-week-comprehensive.md) |
| By interview stage | — | [Phone screen](learning-paths/interview-playbooks/phone-screen.md) · [Technical round](learning-paths/interview-playbooks/technical-round.md) · [System design](learning-paths/interview-playbooks/system-design-round.md) |
| Company-specific | Varies | [Amazon](learning-paths/company-specific/amazon-interview-prep.md) · [Google](learning-paths/company-specific/google-interview-prep.md) · [Meta](learning-paths/company-specific/meta-interview-prep.md) · [more](learning-paths/company-specific/) |

---

## Mock interview agents

Practice with two AI-powered agents:
- **Interviewer Agent** — Asks questions, gives real-time feedback
- **Candidate Agent** — You ask it questions, it codes

See [AGENTS.md](AGENTS.md) for setup and usage.

---

## Stats

- **49** fully interview-ready guides (databases + AI/ML)
- **218** passing test cases
- **5** coding pattern libraries (Python)
- **52** interview framework guides
- **7** topic sections
- **13** structured learning paths

---

## FAQ

**Where do I start?**
Go to [GETTING_STARTED.md](GETTING_STARTED.md) and answer 3 quick questions. Takes 2 minutes.

**Can I just code without reading docs?**
Yes. Start with the pattern files in `python/patterns/` and run the tests. Learning happens by doing.

**Are these real interview problems?**
Yes — all problems are from LeetCode, real company interviews, or common patterns. 40+ problems, fully tested.

---

Open source. Free to use, modify, share.
