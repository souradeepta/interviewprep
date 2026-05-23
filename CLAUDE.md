# CLAUDE.md — Collaboration Guidelines

This file documents how to work with Claude on the datastructures repository.

## Project Context

**Goal:** Comprehensive SDE interview preparation with 218+ tests, 40+ patterns, and complete guides.

**Repository Structure:** Topic-centric (docs/) with code implementations nested inside:
- `docs/01-interview-frameworks/` — 44+ interview frameworks
- `docs/02-databases/` — 10+ database guides
- `docs/03-system-design/` — 39+ system design patterns
- `docs/04-ai-ml-llms/` — 20 AI/ML guides
- `docs/05-algorithms/` — Algorithm implementations
- `docs/06-data-structures/` — Data structure implementations
- `docs/07-patterns/` — 40+ interview pattern problems
- `docs/08-learning-paths/` — Structured learning journeys

## Documentation Best Practices (Learned)

### Structure for Technical Guides

Each guide should include:

1. **Quick Summary** (50 words max)
   - What is it?
   - When to use?
   - Key benefit?

2. **Fundamentals** (Clear explanations)
   - Concepts with examples
   - Visual diagrams (ASCII art is fine)
   - Real-world analogies

3. **Trade-offs Section** (Critical!)
   - Feature comparison table
   - When to choose each option
   - Cost vs. performance graph
   - Consistency/availability trade-offs

4. **Architecture Patterns** (Diagrams + explanation)
   - ASCII diagrams showing flow
   - Real-world deployment patterns
   - Scaling strategies
   - Example: Master-Replica, Sharding, CQRS

5. **Interview Q&A** (Must-haves)
   - Start easy, progress to hard
   - Include common follow-ups
   - Explain "why" not just "what"
   - Real numbers and scenarios
   - Example: "Design for 1B users", "Handle failures"

6. **Practical Exercises** (With solutions!)
   - 4-5 exercises per guide
   - Easy → Medium → Hard progression
   - Complete working code/SQL
   - Real-world use cases
   - Explanation of trade-offs

### Content Depth

**Trade-offs > Length**
- Prefer focused trade-off analysis over generic comparisons
- Include specific numbers (latency, throughput, cost)
- Show when each option wins

**Diagrams > Words**
- ASCII diagrams for architecture
- Decision trees for "when to use"
- Comparison matrices instead of prose
- Performance graphs with axes

**Examples > Theory**
- Show complete working code
- Include sample data and output
- Demonstrate with real scenarios
- Real interview problems, not hypotheticals

**Exercises > Q&A**
- Move beyond questions to practical problems
- Provide solutions with explanations
- Progressive difficulty (Easy → Hard)
- Real-world scale (1M users, 1B events)

### How We Enhanced Database Section

**Phase 1: Trade-offs & Comparisons**
```
✓ Added comparison matrices (SQL vs. NoSQL, Columnar vs. Row-based)
✓ Included CAP theorem visualization
✓ Cost vs. performance graphs
✓ Decision frameworks (when to use each)
```

**Phase 2: Diagrams & Visualization**
```
✓ Architecture patterns (30+ ASCII diagrams)
✓ Data flow diagrams
✓ Compression technique examples
✓ Cardinality and scaling visualizations
```

**Phase 3: Interview Q&A**
```
✓ 5-10 comprehensive questions per guide
✓ Real-world scenarios (1M users, 1B events/day)
✓ Code examples and implementation details
✓ Performance analysis and optimization strategies
```

**Phase 4: Practical Exercises**
```
✓ 4-5 exercises per guide (21 total)
✓ Easy → Medium → Hard progression
✓ Complete working solutions (code/SQL)
✓ Real-world use cases and performance metrics
```

### Example: Good Database Guide Structure

```
# Topic Name

## ⚖️ Trade-offs Section
- Comparison table (features vs. cost vs. performance)
- When to use decision matrix
- Real numbers (latency, throughput, scale)

## 🏗️ Architecture Patterns
- Visual ASCII diagrams
- Real-world deployments
- Scaling strategies

## 📊 Comparison
- vs. competitors (side-by-side)
- Performance characteristics
- Use case matrix

## ❓ Interview Q&A
- 5-10 questions (easy → hard)
- Real scenarios
- Follow-ups
- Code examples

## 🧪 Practical Exercises
- 4-5 exercises
- Easy → Medium → Hard
- Complete solutions
- Trade-off analysis

## 💡 Interview Tips
- What interviewer is asking
- How to answer
- Key concepts
```

## Working Style Preferences

**One-Shot Execution**
- User prefers clear direction over planning
- Avoid lengthy "would you like me to..." questions
- Get to work quickly
- Report results, not process

**Concise Output**
- Terminal-focused feedback
- Focus on what changed
- Minimize verbosity
- Results over narration

**Practical Focus**
- Real code over theory
- Working examples over concepts
- Trade-off analysis over features
- Interview-ready content

## Communication Style

**With User:**
- Direct and concise
- Problem → Solution → Impact
- Avoid planning ceremonies
- Move fast

**In Code Comments:**
- None (well-named code is self-documenting)
- Only add if WHY is non-obvious
- No multi-paragraph docstrings
- No referencing issues/PRs

**In Documentation:**
- Examples first, explanation second
- Real numbers and metrics
- Decision trees when applicable
- "When to use" not "features"

## Git Practices

**Commit Style:**
- Descriptive commit messages
- Focus on "why" not "what"
- Batching related changes is OK
- One commit per logical unit

**Pushing:**
- Push after commits (don't hold changes)
- Use main branch (no unnecessary branching)
- Large changes OK if cohesive

## Content Quality Checklist

Before finishing a guide:

- [ ] **Trade-offs:** Included comparison table with real metrics
- [ ] **Diagrams:** At least 3 ASCII diagrams for complex topics
- [ ] **Q&A:** 5-10 questions spanning easy to hard
- [ ] **Exercises:** 4-5 practical exercises with solutions
- [ ] **Examples:** Real numbers (1M users, 1B events, etc.)
- [ ] **Performance:** Time/space complexity included
- [ ] **When-to-use:** Clear decision framework
- [ ] **Code:** Working solutions, not pseudocode
- [ ] **Trade-offs Explained:** Why each choice, not just how

## Section Completion Status

| Section | Status | Notes |
|---------|--------|-------|
| `docs/02-databases/` | ✅ Complete | 30 guides, 35 real interview Q&As, exercises |
| `docs/04-ai-ml-llms/` | ✅ Complete | 19 guides, all expanded 2026-05-23 |
| `docs/01-interview-frameworks/` | 🔲 Not expanded | 44+ frameworks, needs exercises |
| `docs/03-system-design/` | 🔲 Not expanded | 39+ patterns, needs failure scenarios |
| `docs/05-algorithms/` | 🔲 Not expanded | Needs trade-offs + complexity |
| `docs/06-data-structures/` | 🔲 Not expanded | Needs optimization examples |
| `docs/07-patterns/` | 🔲 Not expanded | 40+ problems, needs full solutions |
| `docs/08-learning-paths/` | 🔲 Not expanded | Needs exercise links |

## For Future Work

**Database Guides Still Need:**
- Vector Databases: Add more exercises
- GraphQL: Add caching/performance exercises
- Data Warehousing: Add pipeline exercises
- Time-Series: Add cardinality management examples

**Next Priority Sections:**
- `docs/03-system-design/` — Add failure scenario exercises (highest interview value)
- `docs/07-patterns/` — Add complete solutions with complexity analysis
- `docs/05-algorithms/` — Add trade-off comparisons (BFS vs. DFS, Dijkstra vs. A*)
- `docs/06-data-structures/` — Add optimization examples and real-world use cases

**AI/ML Section Patterns (2026-05-23):**
- LLMOps: deployment cost models ($0.001/1K self-host vs $0.01/1K API), circuit breaker,
  canary deploy, semantic cache (40-60% cost reduction), model router (80% savings),
  Redis rate limiter, LLM-as-judge eval pipeline
- Multimodal: CLIP contrastive loss, LLaVA (ViT → MLP projection → LLM),
  Whisper (mel spectrogram → encoder-decoder), zero-shot CLIP, multimodal RAG with RRF

**Documentation Enhancement Potential:**
- Add video transcripts (mock interviews)
- Add whiteboard diagrams (real diagrams)
- Add code sandbox (interactive examples)
- Add community solutions (different approaches)

---

**Last Updated:** 2026-05-23
**Key Insight:** Trade-offs + Diagrams + Exercises = Interview-Ready Documentation
**Completed:** Database (30 guides) + AI/ML (19 guides) = 49 guides fully expanded
