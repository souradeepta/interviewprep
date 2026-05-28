# Red Flags & Common Rejection Reasons

**Level:** L3-L5+
**Time to read:** ~20 min

> This guide teaches what gets candidates **rejected** — the red flags interviewers flag in their debrief notes, by round and by company. Use it to audit your own practice sessions.

---

## Part 1: Rejection Reasons by Round

### Coding Round

#### 🚫 Jumping to code without clarifying
**What it looks like:** Interviewer says "find the longest palindromic substring" and the candidate immediately starts typing.
**Why it's a red flag:** Shows inability to handle ambiguity; often leads to solving the wrong problem.
**What good looks like:** Ask 2-3 clarifying questions first — input constraints, edge cases, expected output format. Then state your approach before coding.

#### 🚫 Silent thinking
**What it looks like:** Candidate stares at screen for 3+ minutes without speaking.
**Why it's a red flag:** Interviewer can't evaluate thinking process; feels like candidate is stuck.
**What good looks like:** Think out loud continuously. "I'm thinking about whether a hash map helps here... if I store each character's last seen index, then..."

#### 🚫 Jumping to the optimal solution without discussing brute force
**What it looks like:** "I'd use a monotonic stack." without explaining why or what problem it solves.
**Why it's a red flag:** Even if correct, it signals pattern-matching without understanding. Interviewers want to see how you think.
**What good looks like:** Start with brute force, identify its bottleneck, then improve. "Brute force is O(n²) because we recompute sums. If we precompute prefix sums, each query becomes O(1)."

#### 🚫 Ignoring edge cases until prompted
**What it looks like:** Writes solution, interviewer asks "what about an empty array?" and candidate says "oh, I didn't think about that."
**Why it's a red flag:** Production bugs come from edge cases. Candidates who miss them raise concerns.
**What good looks like:** Before coding, list edge cases: empty input, single element, all duplicates, negative numbers, integer overflow.

#### 🚫 Not testing your own code
**What it looks like:** Finishing the code and saying "I think that's correct."
**Why it's a red flag:** Shows lack of rigor. Almost everyone has at least one off-by-one or edge case bug.
**What good looks like:** Manually trace through a small example. "Let me test with [1, 2, 3]. l=0, r=2, sum=4 > target=3, so r becomes 1..."

#### 🚫 Fixing bugs by randomly changing things
**What it looks like:** Code fails test case, candidate changes `<` to `<=`, re-runs, changes `i+1` to `i`, etc. without reasoning.
**Why it's a red flag:** Shotgun debugging signals no mental model of correctness.
**What good looks like:** Say "let me trace through why this fails" before touching the code.

#### 🚫 Giving up or asking for hints too quickly
**What it looks like:** After 2 minutes: "I'm not sure how to proceed, can you give me a hint?"
**Why it's a red flag:** Signals low persistence and unfamiliarity with problem-solving under pressure.
**What good looks like:** Spend at least 5 minutes working through approaches yourself. Narrate what you've tried and ruled out before asking for guidance.

---

### System Design Round

#### 🚫 Designing without scoping
**What it looks like:** "Design Twitter" → immediately starts drawing boxes for frontend, backend, database.
**Why it's a red flag:** Real systems require requirements. Jumping straight to architecture shows cargo-cult thinking.
**What good looks like:** Spend 5 minutes establishing requirements: DAU, read/write ratio, latency requirements, consistency model. Then design to those constraints.

#### 🚫 No back-of-envelope calculations
**What it looks like:** "We'll need a database" without ever calculating storage, QPS, or bandwidth.
**Why it's a red flag:** Staff-level design is driven by numbers. Skipping math means you can't validate your design choices.
**What good looks like:** "100M DAU × 10 tweets/day = 1B writes/day = ~12K writes/sec peak. That's too high for a single SQL instance, so we shard."

#### 🚫 "I'd just use Kafka" / "I'd just use Redis" without justification
**What it looks like:** Dropping technology names without explaining the trade-offs.
**Why it's a red flag:** Anyone can name tools. Interviewers want to know WHY — what property of Kafka makes it right here.
**What good looks like:** "I'd use Kafka because we need at-least-once delivery with replay capability, and we can tolerate a few seconds of lag. If we needed lower latency, I'd consider SQS or a custom queue."

#### 🚫 Designing for a different scale than the prompt
**What it looks like:** Prompt says "10M users" and candidate designs a simple single-server setup as if it's a startup, or designs a 100-region active-active system as if it's a global platform.
**Why it's a red flag:** Not listening to the problem. Also shows inability to right-size solutions.
**What good looks like:** Use the stated scale in every decision. "At 10M users and 50 reads/write, a single PostgreSQL instance with read replicas is sufficient. No need for sharding yet."

#### 🚫 Ignoring failure modes
**What it looks like:** Design presented as a happy path only. No mention of what happens when the database goes down, cache is cold, or a service is slow.
**Why it's a red flag:** Production systems fail constantly. Candidates who don't think about failures raise reliability concerns.
**What good looks like:** For each critical component, address: "If this fails, what happens? How do we recover? What's the blast radius?"

#### 🚫 Over-engineering for the given scale
**What it looks like:** 100K user app with 5 microservices, 3 Kafka topics, separate read/write clusters.
**Why it's a red flag:** Complexity kills reliability. Premature optimization.
**What good looks like:** "At this scale, a monolith with a PostgreSQL database is the right starting point. I'd break it into services only if we hit specific scaling bottlenecks."

---

### Behavioral Round

#### 🚫 "We" instead of "I"
**What it looks like:** "We redesigned the auth service, we deployed it, we fixed the latency issue."
**Why it's a red flag:** Interviewers can't evaluate your specific contribution.
**What good looks like:** "I led the design review, proposed the JWT migration, and personally owned the deployment. My teammate handled the rollback scripts."

#### 🚫 Stories without measurable impact
**What it looks like:** "I improved the performance of the recommendation engine and users were happier."
**Why it's a red flag:** "Happier" is not a metric. Impact should be quantifiable.
**What good looks like:** "I reduced P99 latency from 800ms to 120ms, which resulted in a 15% increase in recommendation click-through rate."

#### 🚫 No conflict story or no failure story
**What it looks like:** All stories are positive, no friction, no difficulty.
**Why it's a red flag:** Every engineer has dealt with conflict and failure. Absence of these stories signals either dishonesty or lack of self-reflection.
**What good looks like:** Have 2-3 prepared stories about: a time you disagreed with a decision (and how it resolved), and a time something failed and what you learned.

#### 🚫 Criticizing former employers or teammates
**What it looks like:** "My manager was terrible, the codebase was a disaster, no one knew what they were doing."
**Why it's a red flag:** Strong signal for low EQ and team fit risk. You'll be working closely with these people.
**What good looks like:** Frame challenges structurally. "The team was moving fast and accumulated technical debt. I proposed a refactoring initiative that balanced new feature work with cleanup."

#### 🚫 STAR answer without specificity
**What it looks like:** "I was working on a project [Situation]. My task was to improve performance [Task]. I wrote some optimizations [Action]. It got better [Result]."
**Why it's a red flag:** Generic STAR answers don't differentiate. The detail is what makes the story credible and memorable.
**What good looks like:** Include specific technologies, specific constraints ("we had 2 weeks before the launch"), specific numbers ("reduced memory by 40%"), and specific decisions that were uniquely yours.

---

## Part 2: Red Flags by Company

### Amazon

Amazon interviews against 16 Leadership Principles. Every behavioral question is evaluated against LPs.

**Top rejection reasons at Amazon:**
- **Customer Obsession** stories about internal tools that never mention customers or users
- **Ownership** stories where you blame others for failures or say "that wasn't my responsibility"
- **Dive Deep** answers that stay at the surface level — Amazon interviewers will keep asking "why" and "how"
- **Bias for Action** stories that describe analysis paralysis or waiting for perfect information
- **Bar Raiser** failure: not raising the bar above "roughly equivalent to the team" on at least one dimension

**Amazon-specific signals to prepare:**
- "Tell me about a time you made a decision with incomplete data" → Bias for Action
- "Tell me about a technical mistake you made" → Ownership, Learn and Be Curious
- "Tell me about a time you disagreed with your manager" → Have Backbone; Disagree and Commit

**Bar-raiser note:** The bar raiser evaluates candidates against the company standard, not just the team's need. If you're "good enough for the team," you'll be rejected if you're not "raising the bar." Prepare to show something exceptional in at least one dimension.

---

### Google

Google values: Technical excellence, Googleyness (effective communication, humility, collaborative problem-solving).

**Top rejection reasons at Google:**
- **Code quality round**: messy variable names, no testing approach discussed, "it works" as justification
- **System design**: inability to estimate scale or back design decisions with numbers
- **Googleyness**: being dismissive, not considering others' perspectives, asking no questions
- **Leadership/Collaboration round**: stories that show individual heroics but no team enablement

**Google-specific patterns:**
- Expect follow-up questions to go very deep — "how would you scale this 10x?" is just the start
- "What's your biggest weakness?" — Google genuinely explores this; give a real one with an action plan
- Algorithm interviews often involve variants of the original problem — be ready to extend your solution

---

### Meta

Meta values: Move fast, direct communication, impact.

**Top rejection reasons at Meta:**
- **Coding**: taking too long on easy/medium problems; not completing the solution
- **System design**: no clear core product loop; designing infrastructure without connecting to user value
- **Execution and velocity**: stories that show you waited for consensus instead of moving
- **Cross-functional collaboration**: no evidence of working with PMs, designers, or other engineers

**Meta-specific patterns:**
- Coding bar is high — they expect clean, working code within 30-40 minutes
- "Design Instagram's notifications" — focus on product thinking, not just architecture
- Behavioral stories should demonstrate speed of execution and comfort with ambiguity

---

## Part 3: Solution Anti-Patterns

### Algorithmic
- **O(n²) when O(n log n) was obvious:** Nested loop for "find two numbers that sum to target" when a hash map gives O(n)
- **Using sort when you don't need the full ordering:** Heap or partial sort is cheaper for "find kth largest"
- **Modifying input when the problem says immutable:** Adds bugs and may violate constraints
- **Treating duplicates incorrectly:** Many two-pointer and sliding-window solutions break silently when duplicates exist
- **Off-by-one on boundary conditions:** Array access out of bounds, inclusive vs. exclusive range confusion
- **Not handling empty input:** `return nums[0]` crashes on empty array

### Code Quality
- **Magic numbers:** `if count > 3` without explaining what 3 means
- **Variable names like `x`, `y`, `temp`:** Especially in system design code sketches
- **No early returns for base cases:** Deep nesting when early returns would be cleaner
- **Global state mutation:** Functions with side effects that aren't obvious from the signature

### Communication
- **Answering a different question than asked:** Re-read the prompt before starting
- **Claiming you solved it before testing:** Hubris flag; always verify
- **Saying "I don't know" and stopping:** Better to say "I haven't seen this exact problem, but let me reason from first principles..."

---

## Quick Reference: Pre-Interview Checklist

Before your interview, verify you won't hit these:

### Coding
- [ ] I will ask 2-3 clarifying questions before coding
- [ ] I will explain my approach before typing
- [ ] I will trace through an example with my own code
- [ ] I will discuss time and space complexity unprompted
- [ ] I have stories ready for: conflict, failure, disagreement

### System Design
- [ ] I will calculate DAU, QPS, storage in the first 5 minutes
- [ ] I will justify every technology choice with a trade-off
- [ ] I will explicitly discuss what happens when components fail
- [ ] I will connect the design to the stated scale constraints

### Behavioral
- [ ] My stories all use "I" not "we"
- [ ] All results have a measurable number
- [ ] I have a genuine failure story ready
- [ ] I will not criticize former employers
