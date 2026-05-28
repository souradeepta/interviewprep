# 07 — Amazon Bar Raiser Process and Leadership Principles

**Level:** L5+  
**Applicable to:** Amazon SDE III (L6), Senior SDE (L5), Principal SDE (L7)  
**Time to read:** ~20 minutes

---

## What Is a Bar Raiser?

The bar raiser is a specially trained Amazon interviewer who is **not on the hiring team** and has no stake in headcount. Their sole mandate: determine whether the candidate raises the overall quality bar of Amazon's engineering organization — not just whether they can do the job.

A hiring manager wants to fill a role. The bar raiser asks a different question: "Is this person in the top 50% of all Amazonians at this level, globally?" If the answer is no, the bar raiser votes No Hire regardless of team enthusiasm.

**Key structural facts:**
- Bar raisers are senior ICs or managers who volunteered, passed training, and have conducted many loops
- They can override a hiring manager's Yes vote — their No is effectively a veto
- They write a detailed debrief focusing on LP signals, not just technical competency
- They often conduct the "behavioral" or "leadership" round but sometimes shadow a technical round

**Why this matters for L5+ candidates:** At L5, you are being evaluated not on "can they code" but on "will this person make Amazon better?" The bar raiser probes harder and goes deeper than any other interviewer.

---

## The Bar Raiser's Interviewing Style

Expect probing 3-4 levels deep. A bar raiser who asks "tell me about a time you led a complex project" will follow up with:

1. "What specifically did YOU do?" (vs. what your team did)
2. "What was the hardest decision you made?" (vs. the hardest technical challenge)
3. "What did you get wrong?" (vs. what you accomplished)
4. "What would you do differently now?" (vs. would you do it again)

**Quantitative impact is non-negotiable.** At L5+, "improved performance" is a red flag. "Reduced p99 latency from 480ms to 120ms, enabling the team to launch to a 2nd region 6 weeks earlier than planned" is a green flag. The bar raiser documents whether your impact is measurable and credible.

**STAR is baseline, not ceiling.** At L3 or L4, a clean STAR answer demonstrates competence. At L5+, the bar raiser is looking for the layers underneath STAR: What was the organizational context? Who pushed back and why? What did you trade off? What did you not do?

---

## The 16 Leadership Principles at L5+ Depth

### 1. Customer Obsession
**What it means at L5+:** You don't just build what customers ask for. You represent customers when nobody else in the room is.

**Story angle:** A time you delayed a feature launch because you discovered customers would be confused or harmed by it — even though the roadmap, PM, and leadership wanted to ship. What data did you surface? What happened as a result?

**Failure mode:** Describing features you built without connecting to how customers experienced them.

---

### 2. Ownership
**What it means at L5+:** You took on a problem that was nobody's job — an org-wide gap, a platform failure, a broken process — and drove it to resolution even though it wasn't your team's charter.

**Story angle:** A time you identified a problem in another team's domain, engaged that team, aligned stakeholders, and drove resolution. Bonus points if you did it without being asked.

**Failure mode:** Describing ownership within your own team's charter. That's expected at L4.

---

### 3. Invent and Simplify
**What it means at L5+:** You found a technically simpler solution to a problem that others had given up on, or that conventional wisdom said required complexity.

**Story angle:** A technical design that removed 40% of the code, eliminated an entire component, or solved a 3-year-old problem with a 2-week solution. Ideally, others told you it couldn't be done.

**Failure mode:** Describing a feature you invented without discussing the simplification angle.

---

### 4. Are Right, A Lot
**What it means at L5+:** You make good decisions under uncertainty with incomplete data. You know when to trust your intuition and when to validate.

**Story angle:** A major architectural decision you made with limited data, the reasoning process you used, and how it turned out. Also valuable: a time you changed your mind based on new evidence.

**Failure mode:** Only sharing decisions that worked out. Changing your mind based on data is a positive signal, not a weakness.

---

### 5. Learn and Be Curious
**What it means at L5+:** You actively seek out knowledge outside your domain, apply learnings from adjacent fields, and model intellectual curiosity for your team.

**Story angle:** A time you learned something in a completely different area (networking, economics, HCI, statistics) and applied it to a hard engineering problem.

**Failure mode:** Describing courses you took or certifications earned. Learning must connect to impact.

---

### 6. Hire and Develop the Best
**What it means at L5+:** You changed someone's career trajectory through mentorship — not just helped them ship a feature.

**Story angle:** An L4 you identified as a future L5, the gap you diagnosed, the coaching approach you used (stretch assignments, pairing, feedback), and the outcome (they got promoted, they unblocked a critical project, they started mentoring others).

**Failure mode:** Describing interviewing or hiring activities. "I mentored" without specifics on what you did and how the person grew.

---

### 7. Insist on the Highest Standards
**What it means at L5+:** You raised the bar for the team — code quality, operational excellence, documentation — even when it created friction.

**Story angle:** A time you pushed back on a team norm that was creating technical debt or operational risk. How did you make the case? What changed? What was the pushback?

**Failure mode:** Describing your own high-quality work. This principle is about raising others' standards, not your own.

---

### 8. Think Big
**What it means at L5+:** You proposed or championed an initiative that changed the direction of a product or platform beyond your team's immediate roadmap.

**Story angle:** A time you proposed a 2-3 year technical vision, got stakeholder buy-in, and drove early milestones. The vision should be larger than one team's scope.

**Failure mode:** Describing a feature roadmap or quarterly plan. Think Big means multi-year, multi-team impact.

---

### 9. Bias for Action
**What it means at L5+:** You made a significant decision with incomplete information, accepted the risk, and moved fast because waiting was more expensive than being wrong.

**Story angle:** A high-stakes technical decision you made in < 48 hours with 60% of the data you wanted. What was the reversible/irreversible calculation? What was the outcome?

**Failure mode:** Describing speed without risk acknowledgment. The bar raiser is testing whether you understood what you were trading off.

---

### 10. Frugality
**What it means at L5+:** You solved a problem with fewer resources than the organization expected — fewer engineers, less infrastructure, shorter timeline.

**Story angle:** A project the team thought needed 6 engineers for 6 months that you designed to need 3 engineers for 3 months. What was your approach? What did you cut, automate, or reuse?

**Failure mode:** Describing cost optimization work. Frugality is about constraints enabling creativity, not just saving money.

---

### 11. Earn Trust
**What it means at L5+:** You built credibility with skeptical stakeholders — another team, a skeptical VP, a partner org — through demonstrated competence and transparency.

**Story angle:** A time you had to rebuild trust after a failure (an incident, a missed deadline, a bad estimate). What did you communicate? What changed in your behavior?

**Failure mode:** Only describing trust-building successes. A story that includes a stumble and recovery is far more credible.

---

### 12. Dive Deep
**What it means at L5+:** You found the real root cause of a problem by going 3 levels deeper than anyone else was willing to go — and the real cause was not what anyone expected.

**Story angle:** An incident or bug where the first three hypotheses were wrong, and you found the actual root cause through systematic investigation. The root cause should be surprising (e.g., "we had a single-threaded event loop in a service nobody had read the code for in 4 years").

**Failure mode:** Describing debugging work without emphasizing the investigation methodology and the unexpected discovery.

---

### 13. Have Backbone; Disagree and Commit
**What it means at L5+:** You pushed back on leadership — a VP, a director, a principal — with data and conviction, were overruled or chose to commit after a fair hearing, and then executed 100%.

**Story angle:** A technical direction you believed was wrong, the case you made (with data), the outcome of the discussion, and how you committed to and executed the decision you disagreed with. Critically: there should be no passive-aggressive undermining after the decision.

**Failure mode:** Only sharing times you disagreed AND were proven right. The LP is about the commitment after losing, not just the disagreement.

---

### 14. Deliver Results
**What it means at L5+:** You delivered a critical outcome in a difficult situation — staffing crisis, scope explosion, infrastructure failure, partner dependency delays.

**Story angle:** A high-visibility project where something went wrong mid-stream that threatened delivery. What was the pivot? What was the outcome? What did you cut, add, or change?

**Failure mode:** Describing smooth project deliveries. Deliver Results at L5+ is specifically about delivering *despite* adversity.

---

### 15. Strive to be Earth's Best Employer
**What it means at L5+:** You created an environment where your team members could do their best work, felt psychologically safe, and were growing.

**Story angle:** A specific team culture change you drove — blameless postmortems, no-interruption deep work hours, explicit feedback norms, rotating oncall rotations that reduced burnout.

**Failure mode:** Generic statements about caring about your team. Specific changes with specific outcomes.

---

### 16. Success and Scale Bring Broad Responsibility
**What it means at L5+:** You thought about the second and third-order effects of your technical decisions — on other teams, on customers, on society.

**Story angle:** A technical design decision where you identified potential harms (security risks, bias in ML, accessibility gaps, environmental cost) and adjusted the approach before launch.

**Failure mode:** Describing compliance work or legal requirements. This LP is about proactive responsibility, not required governance.

---

## The 50% Calibration Heuristic

Bar raisers use an internal calibration question: "Is this person in the top 50% of all Amazonians at this level?" This is deliberately relative, not absolute. It means:

- A candidate who is "good enough" is a No Hire
- A candidate who excels on 8 LPs and is mediocre on 8 is borderline at best
- A candidate who demonstrates genuine depth on 5-6 LPs is stronger than one who is surface-level on all 16

**Implications for your preparation:** Don't try to cover all 16 equally. Identify your 6-8 strongest LP stories and prepare them to L5+ depth. Know your weaker LPs and have honest, growth-oriented answers for them.

---

## Common L5+ Bar Raiser Failure Modes

| Failure Mode | What It Signals | What to Do Instead |
|---|---|---|
| Using "we" throughout | No individual ownership | Start with "I decided...", "I drove...", "I recommended..." |
| No numbers on impact | Vague contribution | Prepare specific metrics: latency, cost, headcount, timeline |
| No failure or setback | Low self-awareness | Include what went wrong and what you learned |
| Describing L4 scope | Not yet L5 | Scope stories to cross-team or org-level impact |
| Agreeing with every follow-up | Conflict avoidance | Hold your position when you believe you are right |
| LP answers that contradict each other | No coherent leadership identity | Review all stories for consistency as a whole |

---

## Quick Reference: Story Preparation Template

For each of your top 6-8 LPs, prepare:

1. **Context (2 sentences):** What was the situation? Why did it matter?
2. **Your specific action (3-4 sentences):** What did YOU decide and do?
3. **Obstacle or resistance (1-2 sentences):** What pushed back?
4. **Quantified outcome (1-2 sentences):** What changed, measured?
5. **What you'd do differently (1 sentence):** Shows growth, not defensiveness

Practice delivering each story in 90 seconds. The bar raiser will probe from there.
