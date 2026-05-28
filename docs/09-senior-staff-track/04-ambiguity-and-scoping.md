# Ambiguity and Scoping

**Level:** L5+  
**Time:** 40 min to read + 30 min exercise  
**Interview weight:** Medium-high — evaluated in system design (scope definition) and behavioral ("tell me about defining a problem")

---

## Quick Summary

At L4 and below, the job is to solve clearly defined problems correctly. At L5+, a large part of the job is deciding which problems to solve and what "solved" means. Ambiguity is not a barrier to doing your job — it is your job. This guide teaches the mechanics of moving from a vague problem to a scoped, actionable proposal.

---

## Why Ambiguity Is the Job at L5+

There is a reason junior engineers work from detailed tickets and senior engineers do not. Detailed tickets require someone to have already done the work of:

1. Determining what the problem actually is
2. Deciding what "done" looks like
3. Estimating the scope and effort
4. Identifying the dependencies and risks

That work is not glamorous, it does not show up in lines of code, and it is invisible when done well. But it is where the most leverage is.

Consider two scenarios:

**Scenario A:** PM says "We need to improve checkout conversion." The team gets a ticket: "Add a progress bar to the checkout flow." The engineer implements the progress bar. The metric does not move. The PM writes another ticket.

**Scenario B:** PM says "We need to improve checkout conversion." The Staff engineer asks: "What do we know about where users are dropping off? Do we have funnel data?" The answer is: 60% of drops happen at the payment step, and user research shows confusion about whether the order submitted successfully. The Staff engineer proposes: redesign the payment confirmation UX, add an order status email with a clear CTA, and add a duplicate submission guard. That is a scoped, evidence-based proposal — not a ticket, but a problem definition.

Scenario B is not harder technically. It is harder *before* the technical work begins. That pre-technical work is what L5+ is responsible for.

---

## Scoping Rubric: MoSCoW for Technical Work

Every project has a scope problem. The scoping rubric separates what is essential from what is valuable from what is distracting.

| Category | Definition | Example (checkout project) |
|----------|------------|---------------------------|
| **Must-have** | Required for the project to deliver its core value; without this, the project fails | Payment confirmation redesign; duplicate submission guard |
| **Should-have** | Significant value; should be included if time permits; project is still useful without it | Order status email; estimated delivery date |
| **Nice-to-have** | Low effort or low impact; include only after Must and Should are done | Progress bar animation; confetti on order complete |
| **Out-of-scope** | Excluded explicitly; writing this down prevents scope creep | Full checkout redesign; new payment methods; mobile app changes |

The most important column is "Out-of-scope." Explicitly naming what you are not doing is one of the most valuable things a Staff engineer can do. Without it, every stakeholder adds their favorite feature to the project until it is undeliverable.

### How to Use the Rubric in Practice

When you receive a vague mandate:

1. Write down everything the mandate could possibly mean (5-10 items)
2. Sort each item into Must / Should / Nice-to-have / Out-of-scope
3. Share the sorting with stakeholders before you start building
4. Adjust based on feedback, then treat the resulting rubric as a commitment

Step 3 is where most engineers skip. They scope internally and then are surprised when stakeholders expect something different. The scoping conversation is the product — making it explicit is the point.

---

## Step-by-Step Worked Example: "Improve the Checkout Experience"

This is an intentionally vague mandate. Here is how to move from vague to actionable.

### Step 1: Resist the urge to immediately propose solutions

When you hear "improve the checkout experience," your brain will immediately generate solutions: faster loading, fewer form fields, Apple Pay. Suppress that. You do not know what "improve" means yet.

### Step 2: Ask scoping questions

Good scoping questions:
- "What does success look like? How will we know it worked?"
- "What data do we have about the current experience? Drop-off rates, error rates, user research?"
- "What is the timeline and business context? Is there a seasonal deadline?"
- "What is the one thing that, if we fixed it, would have the most impact?"
- "What has already been tried and did not work?"

Bad scoping questions:
- "Do you want a progress bar?" (Solution, not problem)
- "How fast do you want it?" (Feature, not metric)
- "Can we redesign the whole thing?" (Negotiating scope before understanding the problem)

### Step 3: Synthesize what you learn

Suppose the answers are:
- Success: 5% improvement in checkout conversion rate (currently 68%)
- Data: 60% of drop-offs happen at payment step; user research shows users are uncertain whether their order went through
- Timeline: Pre-holiday, so 8 weeks
- Priority: Fix the payment step; everything else is secondary
- History: A/B test of a simpler form in 2024 showed no improvement; the uncertainty-at-payment hypothesis is new and untested

Now you have a problem: users are uncertain whether their payment succeeded, which causes them to abandon or retry (which causes duplicate orders).

That is a very different problem from "the checkout experience is not good."

### Step 4: Define scope using the rubric

| Category | Items |
|----------|-------|
| **Must-have** | Payment confirmation screen redesign; order ID prominently displayed; duplicate submission prevention |
| **Should-have** | Transactional email with order summary; 24/7 order status page |
| **Nice-to-have** | Estimated delivery date; "Save my address" feature |
| **Out-of-scope** | Cart redesign; mobile app changes; new payment methods (PayPal, Crypto); shipping speed options |

### Step 5: Communicate the scope as a proposal

Write it down and share it with the PM and team lead before starting work. Frame it as a proposal, not a decision you made unilaterally:

> "Based on the funnel data and user research, the hypothesis is that users are uncertain whether their payment succeeded. I am proposing we scope to: [Must-haves]. This should move the conversion rate at the payment step. Out of scope for this project: [Out-of-scope items]. Does this match your expectation? What am I missing?"

### Step 6: Say no to scope creep — gracefully

Halfway through the project, the PM asks: "While we are in checkout, can we add PayPal?"

Response: "PayPal is a meaningful feature, but adding it to this project would push us past the pre-holiday deadline and distract from the conversion hypothesis we are testing. I want to make sure we measure whether the payment confirmation redesign actually moves the metric before we add more. Can we plan PayPal as the next checkout project once we have the conversion data from this one?"

This is not "no." It is "yes, and here is the right time and context."

---

## Reversibility Matrix: Making Decisions With Incomplete Information

A common failure mode at L5+ is waiting for perfect information before making a decision. The problem is that in complex systems, perfect information never arrives — and the cost of waiting is real.

The reversibility matrix helps you calibrate how much information you need before deciding.

| Reversibility | Decision Speed | Examples |
|---------------|----------------|---------|
| **High** — can undo in < 1 week | Decide now, iterate | Feature flag rollout; configuration changes; UI copy |
| **Medium** — can undo in 1-3 months | Decide after a 1-2 week spike | API contract; database schema; library adoption |
| **Low** — can undo in 6-18 months | Invest in research first | Cloud provider; core data model; team structure |
| **Near-irreversible** — years to undo | Full analysis, leadership alignment | Public API compatibility; regulatory commitments; data deletion policies |

The heuristic: if you make a high-reversibility decision wrong, the cost is a week of rework. If you make a low-reversibility decision wrong, the cost is 18 months. Invest in research proportional to the reversal cost.

### Applying This in Practice

When you are stuck on a decision, ask: "What is the cheapest way to test this assumption?"

- "Should we use Postgres or Cassandra?" → Reversibility: medium. Run a 2-week PoC with realistic data volumes. Decide based on evidence.
- "Should we break this API?" → Reversibility: low (API consumers need time to migrate). Write an RFC, run a 6-week deprecation period, provide migration tooling.
- "Should we add a feature flag to this rollout?" → Reversibility: high. Just add it. The cost of adding is low; the cost of a bad rollout without it is high.

---

## Common Failure Modes

### Over-scoping

Taking on more than can be delivered in the time available. Usually driven by wanting to solve the "whole problem" in one project.

**Symptom:** The project is 3 months in and "we need two more months."  
**Fix:** Apply the MoSCoW rubric at the start. Force the conversation about what happens if only the Must-haves ship.

### Under-scoping

Solving a symptom instead of the underlying problem, requiring multiple follow-up projects to close the gap.

**Symptom:** "We fixed the bug, but the metric did not move."  
**Fix:** Ask "is this the root cause, or a symptom?" before scoping the solution. Use the "5 Whys" to get to the actual problem.

### Waiting for Perfect Information

The project does not start because "we need more data." The data collection becomes its own multi-month project.

**Symptom:** Q1 planning: "We need to do research first." Q2 planning: "We are still analyzing the research." Q3 planning: the project gets canceled because the business context changed.  
**Fix:** Apply the reversibility matrix. If the decision is medium-reversibility, 2 weeks of research is enough. Make a decision, ship it, measure, iterate.

### Scope Creep Acceptance

Saying yes to every addition because it feels collaborative.

**Symptom:** Sprint 1 scope is 5 stories. Sprint 5 scope is 20 stories. Nobody knows when it will ship.  
**Fix:** Treat scope changes as trade-offs: "We can add that, but what do we remove?" Or: "That is not in this project. Here is how we will track it for the next one."

---

## Interview Scenario

**"Tell me about a time you had to define the problem before solving it."**

**Model answer structure:**

1. **The vague mandate:** What were you asked to do, and what was wrong/unclear about it?
2. **The discovery process:** What questions did you ask? What data did you look at? Who did you talk to?
3. **What you found:** How was the actual problem different from the initial framing? (This is the story — if the problem was exactly as described, it is not a strong example.)
4. **How you scoped it:** What did you include? What did you explicitly exclude? How did you get stakeholder alignment on the scope?
5. **What you built:** What was the outcome of the scoped work?
6. **The impact:** How did you measure success? Did the hypothesis hold?

**Example answer:**

"My team was asked to 'improve API performance.' The initial framing was: our P95 latency is too high, we should add more caching. I started by looking at the data: P95 latency was 800ms. That is bad. But when I segmented by endpoint, 90% of the latency was concentrated in a single endpoint that processed large batch exports — an endpoint used by 3 customers, each once a week. Our standard transactional endpoints were performing at P95 < 50ms.

The actual problem was: a batch workload was running on the same infrastructure as transactional workloads and occasionally consuming all available database connections, which spiked latency for everyone else.

So instead of a caching project, I scoped the work as: separate the batch export infrastructure from the transactional infrastructure. A connection pool for batch work; a separate connection pool for transactional. 2 weeks of work instead of 3 months. P95 dropped from 800ms to 55ms.

The mis-scope in the original mandate was that 'improve API performance' implied caching, but the real cause was resource contention. If I had built the caching layer without the data analysis, we would have spent 3 months on a solution to the wrong problem."

---

*Next:* [Cross-Team Influence](05-cross-team-influence.md) — leading without authority
