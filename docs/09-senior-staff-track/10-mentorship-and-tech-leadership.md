# 10 — Mentorship and Technical Leadership Day-to-Day

**Level:** L5+  
**Applicable to:** Staff, senior staff, principal engineers  
**Time to read:** ~20 minutes

---

## What Technical Leadership Actually Is

Technical leadership is not writing the best code on the team. It is creating the conditions under which the team consistently writes better code than it could without you.

The test is not "how good is the code you write?" It is "how good is the code the team writes when you're on vacation?"

This distinction separates L4 from L5+. An L4 is a high-performing individual contributor. An L5+ is a multiplier: their presence permanently raises the level of the people around them.

This guide covers the concrete, day-to-day practices that constitute technical leadership — the things that show up in promotion cases, that interviewers probe for, and that distinguish high-performing staff engineers from senior engineers who write a lot of code.

---

## Code Review at Scale

### When to Approve, Request Changes, or Block

Staff engineers often become de facto code review gatekeepers. Left unstructured, this creates a bottleneck. The decision framework:

| Situation | Response |
|---|---|
| Code is correct, style preferences differ | Approve + note your preference; don't block |
| Code works but has a latent bug or edge case | Request changes with specific reproduction scenario |
| Code introduces security risk | Block; explain the exact risk vector |
| Code will create technical debt that takes >1 month to clean up | Request changes + discuss trade-off synchronously if blocking is contentious |
| Code violates team standards that are codified | Request changes + link to the standard |
| Code violates team standards you have in your head but haven't written down | Approve + write the standard this week |

**The key insight:** If you're blocking code because of a standard you haven't written down, that's a leadership failure, not a code quality problem.

---

### Review Comments That Grow Engineers

Most code review comments tell engineers what to change. Staff-level review comments teach engineers *why*.

**L4 review comment:**
```
Change this to use a HashMap instead of iterating.
```

**L5+ review comment:**
```
What's the access pattern here? If we're doing lookup-by-key more than once,
a HashMap gives O(1) vs O(n) each time. If this is a one-time iteration,
the linear scan is fine. What does the call site tell you about frequency?
```

The second comment:
- Forces the engineer to think about the access pattern
- Explains the trade-off principle (not just the solution)
- Teaches a reusable mental model (time complexity of access patterns)
- Asks a question rather than issuing a directive

Over time, engineers who receive teaching-style reviews start asking these questions themselves before writing the code. That's leverage.

**Templates for growing-style review comments:**

```
"What assumption is this code making about [X]?
 What happens when that assumption breaks?"

"Why is this the right abstraction here?
 What alternatives did you consider?"

"This works correctly. Is there a version that's
 easier for the next engineer to understand?"

"What will happen to this code at 10x current load?"
```

---

### Batch Review Patterns

A staff engineer who reviews every PR on the team is a bottleneck, not an asset. The goal is to establish a review culture where every engineer can review effectively, and you are not on the critical path for every merge.

**Practical approach:**

1. **Define what needs your review vs. what doesn't.** Establish team norms: infrastructure changes and new service boundaries require staff review; bug fixes and feature flags within existing code do not.

2. **Create PR review rotations.** Rotate who is responsible for reviewing which areas of the codebase. This builds ownership and distributes knowledge.

3. **Shadow review at first.** For engineers you're growing, do shadow reviews: you review a PR alongside the designated reviewer, then compare notes. The engineer learns by comparing their review to yours, not by receiving your corrections.

4. **Set review SLA expectations explicitly.** "PRs under 200 lines should get first review within 24 hours" is a team norm that prevents the anxiety of "my PR has been up for 3 days with no review." Staff engineers often need to initiate and enforce this norm.

---

## Growing Engineers

### The Delegate-and-Debrief Pattern

The most common mistake senior engineers make when growing others: doing the work themselves when they could delegate.

**The pattern:**
1. **Assign the problem** — give the engineer a problem just beyond their current level, with enough context to start but not enough to coast
2. **Set a check-in cadence** — "Let's sync in 3 days; if you're stuck before then, come find me"
3. **Resist the urge to solve it** — when they come to you stuck, ask questions rather than giving answers: "What have you tried?" "What does the error tell you?" "What would you expect to happen?"
4. **Debrief after completion** — not "good job" but "what was the hardest part? What would you do differently? What did you learn that you'll use next time?"

**Why productive struggle matters:** Engineers who solve problems with heavy guidance learn the solution. Engineers who struggle productively learn the problem-solving process. The second is far more valuable.

**The hardest part:** Watching someone struggle for two days with a problem you can solve in 30 minutes. The correct response is usually to let them struggle until they've genuinely exhausted their approaches, then ask a single guiding question rather than revealing the answer.

---

### Stretch Assignments: Calibrating the Right Challenge Level

A stretch assignment that's too easy doesn't grow the engineer. One that's too hard damages their confidence and creates a support burden.

**Calibration heuristic:**
- The engineer should be able to start the work independently (they understand the domain and tools)
- They should hit at least one significant obstacle they haven't encountered before
- They should be able to complete it in 2-4 weeks with occasional guidance

**Good stretch assignments by growth area:**

| Growth area | Good stretch assignment |
|---|---|
| Technical breadth | Own the operational aspect of a system they've never run (oncall, capacity planning) |
| Technical depth | Root-cause analysis on a complex incident in their area |
| Leadership | Run a design review for a feature their team owns |
| Communication | Write the technical RFC for a project, present it to stakeholders |
| Cross-team work | Represent the team in a cross-org planning meeting |
| Project management | Own the delivery of a 4-6 week feature end to end |

Assign one growth area at a time. Engineers growing in two directions simultaneously often grow in neither.

---

### The Difference Between Mentoring and Managing

This distinction matters especially for staff engineers who mentor engineers outside their reporting chain.

| Dimension | Mentoring | Managing |
|---|---|---|
| Authority | Advisory — engineer decides | Formal — manager directs |
| Accountability | Engineer owns outcomes | Manager is accountable |
| Feedback style | Invited perspective | Performance assessment |
| Relationship initiation | Often engineer-initiated | Role-defined |
| Scope | Career, craft, problem-solving | Work delivery, behavior, growth plans |

**Practical implication:** When you mentor an engineer who doesn't report to you, be explicit about which mode you're in. "I'm offering you my perspective as someone who's been through this — take it or leave it" is mentor mode. Directing their work or making judgments that affect their performance review crosses into manager territory, which is both inappropriate and confusing.

---

### How to Identify When Someone Is Ready for the Next Level

The promotion question should never be a surprise — neither to you nor to the engineer. Staff engineers are often asked to provide input on promotions, and sometimes to write promotion cases. The signals:

**Readiness for L4 → L5:**
- Consistently delivers without close supervision
- Code reviews show they're raising quality, not just approving
- Takes ownership of problems that aren't assigned to them
- Is the person others go to when stuck

**Readiness for L5 → L6:**
- Impact regularly extends beyond their team
- Drives initiatives others weren't driving
- Has grown at least one other engineer measurably
- Can articulate why they're making technical decisions, not just how

**The feedback test:** Can you give specific, observable evidence for each claim? "She's ready for L5" is not evidence. "In Q2, she independently designed and delivered the rate limiting service, identified a capacity risk that wasn't in her scope, and mentored two engineers through their first system design reviews" is evidence.

---

### Writing Strong Promotion Cases

Promotion cases are often the most important writing a staff engineer does. They directly affect careers.

**Structure that works:**

1. **Opening statement of readiness** (1-2 sentences): "N is operating at L5 and has been for 6 months."

2. **Evidence across dimensions** (the bulk of the document):
   - Technical contribution: specific projects, specific impact
   - Scope and ownership: where they took initiative beyond their assigned work
   - Growing others: specific engineers they helped, specific outcomes
   - Communication: specific times they explained complex things to non-technical stakeholders

3. **Comparison to level bar** (explicit): "The L5 bar requires sustained cross-team influence. In Q3, N [specific example]. In Q4, N [specific example]."

4. **What would be different at next level** (optional but strong): "As an L6, N would be expected to define technical strategy for the whole platform. Based on [specific evidence], I believe they're ready for that scope."

**What not to do:**
- Vague praise: "N is a great engineer and a team player" — every promotion case has this, it signals nothing
- Recapping their job description: "N delivered features on time" — that's expected at their current level
- Technical-only evidence: if the promotion requires leadership signals and you only have technical evidence, either gather more evidence or the case isn't ready

---

## When to Do vs. Delegate

### Decision Matrix

Use this matrix for any significant task:

```
                        HIGH urgency
                             |
                    Do it yourself (critical path)
                             |
    LOW             ---------|--------         HIGH
    criticality          Delegate        criticality
                    (growth opportunity) |
                             |
                    Delegate with coaching
                             |
                        LOW urgency
```

More precisely: the correct action depends on three factors:
- **Urgency:** Does this need to be done in hours or days?
- **Criticality:** Is there a high cost to getting this wrong?
- **Growth opportunity:** Is there an engineer ready for this stretch?

**If urgency is high AND criticality is high:** Do it yourself. This is not a hero moment; it's triage. Document it for delegation next time.

**If urgency is low AND there's a growth opportunity:** Delegate and coach, even if it takes longer. The time investment in the engineer is worth more than the time saved.

**If criticality is low:** Delegate regardless. Low-stakes work is exactly where engineers should learn.

---

### The Bus Factor Problem

If you are the only person who can do something critical on your team, that is a leadership failure, not a badge of honor.

Single points of knowledge are technical debt. They create:
- Blocking dependencies when you're on vacation or sick
- Anxiety for the engineer who holds the knowledge (always on call mentally)
- Missed growth opportunities for others
- Organizational fragility

**Concretely:** Identify the 3-5 things only you know how to do on your team. For each one, choose someone to transfer the knowledge to, and build a plan to make that transfer happen in the next 60 days.

---

### Avoiding Hero Mode

Hero mode is when the staff engineer is the one who saves every critical situation. It feels good. It is bad leadership.

**Signs you're in hero mode:**
- You are always on the critical path for incidents
- Engineers stop making decisions without you
- You are the bottleneck for code reviews
- Your vacation backlog is noticeably larger than others'
- You feel indispensable

**Why it's bad:** Hero mode optimizes for short-term outcomes at the cost of team capability. Every time you swoop in and fix it yourself, you prevent an engineer from developing the skill to fix it themselves.

**Breaking out of hero mode:**
1. Identify the 3 situations where you most often hero. Write them down.
2. For each, name the engineer who should be able to handle it 90 days from now.
3. Next time that situation arises, bring that engineer with you instead of handling it alone.
4. The time after that, bring them and let them lead while you observe.
5. The time after that, let them handle it without you.

---

## Building a Tech Culture

### Setting Coding Standards the Team Owns

Standards imposed by the staff engineer are followed. Standards built by the team are owned.

**Process for building owned standards:**
1. Identify a recurring pain point (unclear error handling patterns, inconsistent API naming, variable PR size)
2. Bring it to the team as a question: "How should we handle this? What have you seen work elsewhere?"
3. Let the team draft the standard, with you contributing as one voice
4. Document it in the team's wiki, not in your head
5. Reference it in code reviews: "This is covered in our error handling guide (link)"

**The key insight:** When an engineer gets a code review comment saying "this violates our error handling standard" and they can read that standard and see their own suggestion in it, the comment lands very differently than when it says "this violates what I think is best."

---

### Running Effective Architecture Reviews

Architecture reviews fail when they become judgment hearings. They succeed when they function as collective risk reduction.

**What makes an architecture review effective:**

1. **Presenter state their uncertainty first.** "Here are the 3 things I'm most unsure about in this design." This focuses the review and models intellectual humility.

2. **Reviewers ask questions before making claims.** "Why did you choose X?" before "I would have chosen Y."

3. **Document decisions and the reasons for them.** "We chose eventual consistency over strong consistency because our read latency budget is 50ms and our write volume is 1000 RPS." Future engineers reading this understand the reasoning.

4. **Explicit risk register.** End each review with: "What are the top 3 risks in this design and how are we mitigating them?" If you can't answer this, the design isn't ready.

---

### Blameless Incident Reviews

How a team conducts incident reviews reveals its psychological safety.

A blame-ful review: "Who approved this change without testing it?"  
A blameless review: "What conditions made it possible for this change to reach production without catching this bug? What would need to change in our process so that this class of change is caught?"

**The blameless review script:**

1. **Timeline reconstruction** (5-10 min): What happened, in order, with timestamps. Stick to facts.
2. **Contributing factors** (15-20 min): Not who, but what conditions made this possible? (lack of staging environment, missing alert, unclear runbook, etc.)
3. **What went well** (5 min): Even in bad incidents, something worked — detection was fast, escalation was clear, rollback succeeded.
4. **Action items** (10 min): Specific, assigned, time-bound actions that reduce the probability of recurrence. Not "be more careful."

**The staff engineer's role in this:** Model blameless language consistently. When someone slips into blame ("well, if X had done Y..."), redirect: "Let's focus on what process changes would have caught this. What would X have needed to know, and how would they have known it?"

---

## Interview Q: "How Do You Grow Engineers on Your Team?"

**What the interviewer is testing:** Not whether you care about growth, but whether you have a concrete, evidence-based approach that has produced measurable outcomes.

**Model answer (STAR):**

"I use a pattern I call delegate-and-debrief. When I see an engineer who is ready to stretch, I identify a problem just beyond their current level and hand it to them with enough context to start but not enough to coast.

On my last team, I identified an L4 who was technically strong but had never owned a cross-team dependency. I gave her the task of leading our integration with the data platform team — something that required negotiations about API contracts, alignment on a migration timeline, and driving a weekly sync with engineers who didn't report to us.

The first two weeks were rocky: the other team was resistant to our proposed API, and she came to me ready to escalate. Instead of resolving it myself, I asked her: 'What do you think they're worried about that they're not saying?' That reframe shifted the conversation entirely. She went back, asked more questions, discovered they had a hard dependency on the old API format from a downstream service she hadn't known about, and redesigned the contract to accommodate both.

Six months later, she was the one engineers on her team came to when cross-team negotiations hit friction. She's now an L5.

What I watch for: engineers who come back to me with solutions, not just problems. That's the signal that the delegation is working."

**What makes this answer strong:**
- Specific pattern (delegate-and-debrief), not generic philosophy
- Specific engineer story with a named challenge
- Specific intervention (one reframing question, not a lecture)
- Measurable outcome (L5 promotion, became a resource for others)
- Observable signal for evaluating whether the approach is working
