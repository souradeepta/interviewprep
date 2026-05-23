# InterviewPrep Documentation Structure

A comprehensive guide to navigating this repository's documentation.

---

## 📚 Documentation Organization

```
docs/
├── 00-resources/          Resources, utilities, and helper materials
├── 01-interview-frameworks/  Interview preparation frameworks & guides
├── 02-databases/          Database systems (SQL, NoSQL, graphs, etc.)
├── 02-algorithms/         Algorithm patterns, data structures, problems
├── 03-system-design/      System design problems and patterns
├── 04-ai-ml-llms/         AI/ML/LLM systems and techniques
└── 05-learning-paths/     Structured learning paths and roadmaps
```

---

## 🎯 By Topic

### 💻 Algorithm Interview Prep
**Start here:** `docs/01-interview-frameworks/coding-interview-framework.md`

**Learn algorithms:** `docs/02-algorithms/`
- Patterns: sliding window, two pointers, binary search, DP, greedy
- Data structures: trees, graphs, heaps, tries
- Problems: sorted/unsorted arrays, strings, matrices, etc.

### 🏗️ System Design Interview Prep
**Start here:** `docs/01-interview-frameworks/system-design-interview-guide.md`

**Real case studies:** `docs/03-system-design/system-design-case-studies.md`

**Patterns:**
- API design, database design, caching, load balancing
- Microservices, distributed systems, messaging queues
- Security, monitoring, performance optimization

### 🗄️ Database Systems
**Start here:** `docs/02-databases/README.md`

**Database types:**
- SQL (PostgreSQL, MySQL): Relational, ACID, normalization
- NoSQL (MongoDB, DynamoDB): Document, key-value, sharding
- Graphs (Neo4j): Relationships, patterns, traversals
- Columnar (Snowflake, BigQuery): Analytics, OLAP, compression
- Time-Series (Prometheus, InfluxDB): Metrics, monitoring, downsampling
- Search (Elasticsearch): Full-text, ranking, aggregations
- Caching (Redis): Sessions, real-time, in-memory
- Vectors (Pinecone): Embeddings, RAG, similarity search
- APIs (GraphQL): Query language, resolvers, schema design
- Warehousing: ETL/ELT, lakehouses, medallion architecture

### 🤖 AI/ML/LLMs
**Start here:** `docs/04-ai-ml-llms/` (will expand with comprehensive guides)

Coming soon:
- LLM fundamentals and architecture
- Prompt engineering and fine-tuning
- RAG systems and agents
- Model serving and optimization
- ML platforms and infrastructure

### 📖 Behavioral Interview Prep
**Start here:** `docs/01-interview-frameworks/behavioral-interview-framework.md`

- STAR method for answering questions
- 20+ real interview story examples
- Company-specific culture signals

---

## 🚀 Quick Navigation by Goal

### "I have an interview this week"
1. `docs/01-interview-frameworks/` - Read the framework for your interview type
2. `docs/02-algorithms/` - Practice 3-5 problems matching the difficulty
3. `docs/03-system-design/` - For system design rounds: study case studies

### "I want to master algorithms"
1. Start with: `docs/02-algorithms/` - Pick a pattern
2. Understand the: "Key Points", "Time/Space", examples
3. Code it: Use Python implementation as template
4. Test it: Try the edge cases listed
5. Practice: Solve related problems in the same pattern

### "I want to learn system design"
1. Read: `docs/03-system-design/system-design-case-studies.md`
2. Study: Real design decisions and trade-offs
3. Practice: Pick a system (URL shortener, cache, messaging) and design it

### "I want to understand AI/ML/LLMs"
1. Start: `docs/04-ai-ml-llms/` fundamentals
2. Learn: LLM architecture, transformers, attention
3. Build: RAG system, fine-tuned model, LLM agent
4. Optimize: Model serving, inference optimization

### "I want a structured learning plan"
1. Check: `docs/05-learning-paths/` for your level
2. Follow: Daily practice schedule
3. Track: Progress with checklists
4. Interview: Mock interview guides

---

## 📂 Directory Details

### 00-resources/
- Utilities, scripts, and helper tools
- Superpowers and special resources
- Templates and reference materials

### 01-interview-frameworks/
**42 comprehensive interview guides:**
- Coding interview framework (5-phase approach)
- Behavioral interview framework (STAR method)
- System design interview guide
- Interview grading rubric
- 38 deep-dive algorithm and system design mastery guides

Each guide includes:
- Detailed explanations with examples
- Real interview dialogues and Q&A
- Common mistakes and how to avoid them
- Edge cases and complexity analysis
- Code templates in Python and Java

### 02-algorithms/
**Algorithm patterns and implementations:**
- Fundamentals: arrays, strings, linked lists, trees
- Patterns: sliding window, two pointers, binary search, DP, greedy
- Advanced: graph algorithms, dynamic programming, string matching
- Data structures: heaps, tries, segment trees, balanced BSTs
- Math: number theory, combinatorics, modular arithmetic

Structure by topic:
- `*-mastery.md` - Deep dive with examples (e.g., `binary-search-mastery.md`)
- `*-patterns.md` - Pattern recognition (e.g., `sliding-window-patterns.md`)
- Directories: `geometry/`, `graph/`, `math/`, `searching/`, `sorting/`, `string/`, `dp/`

### 03-system-design/
**System design patterns and case studies:**
- 01-caching: Cache design, invalidation strategies, patterns
- 02-core-algorithms: Load balancing, consensus, sharding
- 03-design-patterns: MVC, microservices, saga pattern
- 04-distributed-systems: Replication, failover, CAP theorem
- 05-real-world-apps: URL shortener, chat, payments, recommendations
- 06-data-systems: Time series, search indexing, analytics
- 07-social-features: Feeds, notifications, relationships
- 08-infrastructure: Containers, CI/CD, monitoring
- ... and more real-world topics

Each guide includes:
- Architecture decisions with trade-offs
- Failure modes and recovery strategies
- Scaling from 0 to millions of users
- Real numbers and back-of-envelope calculations

### 04-ai-ml-llms/
**AI/ML/LLM systems (being expanded):**
- Fundamentals: ML concepts, neural networks, transformers
- LLM Engineering: Prompt design, RAG, fine-tuning, agents
- System Design: Model serving, inference optimization, pipelines
- Production: MLOps, monitoring, deployment

### 05-learning-paths/
**Structured learning and interview prep:**
- Sequential tracks by level (beginner, intermediate, advanced)
- Interview playbooks (Google, Meta, Amazon, etc.)
- Company-specific preparation paths
- Daily practice schedules
- Progress tracking templates

---

## 🔍 How to Find Something

**By interview type:**
- Coding: `01-interview-frameworks/coding-interview-framework.md`
- System design: `01-interview-frameworks/system-design-interview-guide.md`
- Behavioral: `01-interview-frameworks/behavioral-interview-framework.md`

**By algorithm pattern:**
- `02-algorithms/*-mastery.md` or `*-patterns.md`
- E.g., "sliding window" → `02-algorithms/sliding-window-patterns.md`

**By system design topic:**
- `03-system-design/[01-09]/` numbered directories
- E.g., "caching" → `03-system-design/01-caching/`

**By company:**
- Check `05-learning-paths/` for company-specific guides

**By difficulty:**
- Check learning paths for guided progression
- Or read frameworks for fundamentals, then advanced guides

---

## 📖 Reading Tips

### For Interview Frameworks (Interview Prep)
1. Read the main framework (e.g., `coding-interview-framework.md`)
2. Study the templates and examples
3. Practice with real interview problems
4. Review common mistakes before your interview

### For Mastery Guides (Deep Learning)
1. Start with **Real Example** or **Core Concept** section
2. Understand the **Key Insights**
3. Study **Implementation** with comments
4. Trace through **Examples** by hand
5. Identify **Edge Cases** relevant to you
6. Reference **Complexity Analysis** for trade-offs

### For System Design (Design Interviews)
1. Read **Architecture** section first
2. Understand **Key Design Decisions** and trade-offs
3. Study **Scaling Deep Dives** for real bottlenecks
4. Review **Interview Follow-ups** for Q&A patterns
5. Practice with **Challenges** and solutions

### For Learning Paths (Structured Study)
1. Choose a path matching your goal and level
2. Follow the daily schedule
3. Use progress checklist to track completion
4. Review weak areas with focused guides
5. Practice mock interviews

---

## ✅ Contribution Guidelines

When adding new guides, follow the structure and conventions:

1. **Naming:** Use kebab-case for filenames (e.g., `api-design-framework.md`)
2. **Organization:** Place in appropriate numbered directory
3. **Format:** Use Markdown with clear headings, code blocks, checklists
4. **Content:** Include examples, edge cases, complexity analysis, and Q&A
5. **Navigation:** Update this file if adding a new major section

---

## 🎓 Best Practices for Studying

### Focused Learning (1-2 weeks)
- Pick 1 interview framework
- Study 3-5 relevant algorithm patterns
- Practice 10-15 problems
- Do 1-2 mock interviews

### Comprehensive Preparation (4-8 weeks)
- Master 3-4 interview frameworks
- Study all algorithm patterns in your weak areas
- Deep dive into system design patterns
- Complete learning path for your target company
- Do weekly mock interviews

### Long-term Mastery (Ongoing)
- Review complex algorithms weekly
- Stay updated with system design patterns
- Learn from each real interview
- Contribute improvements and new content

---

**Last updated:** 2026-05-16  
**Total guides:** 100+ comprehensive frameworks, algorithms, and system design guides  
**Coverage:** Algorithms, data structures, system design, behavioral interviews, LLMs

