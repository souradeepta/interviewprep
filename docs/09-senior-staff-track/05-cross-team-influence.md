# Cross-Team Influence

**Level:** L5+-L6+  
**Time:** 45 min to read + 30 min exercise  
**Interview weight:** Very high at L6+; a primary evaluation axis in every Staff loop

---

## Quick Summary

The most common question in a Staff engineer interview is some version of "tell me about a time you influenced without authority." This is not a soft-skills question — it is an evaluation of whether you can operate effectively in the org structures that most large companies use, where technical decisions span team boundaries and no single person has authority over all of them. This guide gives you the concrete levers for doing this, with a case study worked end-to-end.

---

## The 4 Influence Levers

Influence without authority comes from four sources. The most effective engineers use all four, situationally.

### Lever 1: Expertise

People follow the person who knows the most about a problem. Expertise creates influence when:
- You have deep knowledge that others do not have and cannot easily get
- You use that knowledge to help others solve their problems, not to gate-keep

Expertise is the most common lever used by engineers and the most easily squandered. If you are the person who always says "actually, that approach has a flaw" without proposing an alternative, you are spending expertise on friction rather than influence.

Build expertise influence by: solving hard problems publicly, writing documents that circulate, and being the person others come to before making technical decisions.

### Lever 2: Relationships

People work harder for people they respect and trust. Relationships create influence when:
- You have invested in people before you needed anything from them
- You have a track record of delivering on commitments to the other team
- The other team knows you will give credit when it is due

Relationships are the slowest lever to build and the most durable. You cannot create relationship leverage in a meeting — it accumulates over time.

Build relationship influence by: being a reliable technical partner across team boundaries, celebrating other teams' successes in public forums, and not taking credit for work others contributed to.

### Lever 3: Reciprocity

People feel obligated to help people who have helped them. Reciprocity creates influence when:
- You have done something valuable for the other team recently
- The help was given without an explicit quid pro quo
- The ask you are now making is proportional to the help you gave

Reciprocity is often miscalculated. Engineers think: "I helped Team B debug their database last month; they should adopt my library." But the proportionality matters — debugging a 2-hour incident does not create the same reciprocity as blocking your own team's roadmap to help them hit a deadline.

Build reciprocity influence by: volunteering your team for cross-team work when it creates value for others, even when it is not on your roadmap.

### Lever 4: Framing

How you present a proposal dramatically affects whether people support it. Framing creates influence when:
- You present the proposal as solving the other team's problem, not your problem
- You make the cost of inaction visible
- You give people ownership of the outcome, not just execution of your plan

Framing is the most tactical lever and the most commonly misused. "You need to adopt my auth library" frames the other team as a recipient of your work. "If you adopt this shared library, your team stops maintaining your own auth code and your on-call burden decreases by ~30%" frames it as solving their problem.

---

## Case Study: Get 3 Teams to Adopt a Shared Auth Library

This is a realistic scenario that appears in staff interviews frequently. Here it is worked through with all four levers applied.

### The Situation

You are a Staff engineer on the Platform team. You have built a shared Go library for JWT authentication (`internal/auth`) that centralizes token validation, secret rotation, and rate limiting. It is superior to what the three product teams (Checkout, Identity-as-a-Service, Inventory) each maintain independently. You need all three teams to adopt it by Q3 to support a company-wide security audit.

### Why Command Does Not Work

You do not manage any of these teams. You cannot file a ticket for them and expect it to be done. Even if an executive sends a mandate, mandate-driven adoptions typically result in:
- Shallow adoption (technically compliant but not maintained)
- Resentment that poisons future cross-team work
- Teams waiting for you to do the migration for them, then complaining about the result

The only durable adoption is one where teams want to use the library because it is obviously better for them.

### Step 1: Identify Stakeholders and Their Incentives

Before any meeting or proposal, spend a week understanding each team's situation.

| Team | Current pain | What they care about | Potential objection |
|------|-------------|---------------------|---------------------|
| **Checkout** | Auth bugs causing checkout failures; high on-call load | Reliability, reducing incidents | "Migration will break checkout during peak traffic" |
| **Identity-as-a-Service** | Their auth library is most sophisticated — they feel ownership | Being recognized as the auth experts | "Your library is less capable than ours" |
| **Inventory** | Small team, stretched thin | Not taking on more work | "We don't have bandwidth" |

Now you have a different proposal for each team, based on their actual incentives.

### Step 2: Pre-Alignment — 1:1s Before the All-Hands

Never announce a cross-team proposal in a group meeting without having already talked to each affected team individually.

**Checkout 1:1 (with their Staff engineer):**
> "I looked at your on-call data from last quarter. 8 of your 22 incidents were auth-related — session validation failures, token replay issues. The library we built addresses all 8 of those failure classes. I would love to pilot it with Checkout first because you have the clearest motivation and I want your feedback on the migration experience before we ask other teams to go through it."

This framing: flattery (first to adopt = high status), clear value (incident reduction), and reciprocity (your feedback shapes the library).

**Identity-as-a-Service 1:1 (with their tech lead):**
> "Your auth implementation is the most sophisticated in the company — we actually based the library's token structure on your approach. I want to make sure the library reflects what your team built. I am proposing that your team co-owns the library with Platform — you would be the reviewers for any auth-related changes. This also means your approach becomes the company standard."

This framing: genuine credit (their design did influence the library), ownership (co-maintainer, not just consumer), and legacy (their work becomes the standard).

**Inventory 1:1 (with their EM):**
> "I know your team is stretched. I am not asking you to do the migration yourselves — I will embed one of my engineers with you for 2 weeks to do it. All I need is a designated point of contact who can answer questions about your service's auth flow. The outcome is that you stop maintaining auth code entirely — that reduces your team's surface area."

This framing: reduce work, not add work. The migration is done for them. The outcome is a net decrease in their team's maintenance burden.

### Step 3: The All-Hands Proposal

Only after you have pre-alignment from all three teams do you bring it to a broader audience. At this point, the all-hands meeting is a formality, not a negotiation.

Present with:
1. The problem (auth fragmentation, security audit, incident data)
2. The proposal (shared library with clear migration support)
3. The teams that are already on board (social proof — if Checkout is doing it, it is legitimate)
4. The ask (specific: your team adopts by a specific date, with platform support)

### Step 4: Handling Objections

**"Our auth requirements are unique."**
Response: "Tell me more about what you need that the library does not support. I want to understand the specific requirement." (Not: "No they're not.") Usually the requirement is either already in the library or can be added. If it genuinely cannot be added, that is useful information and you should acknowledge it: "That is a real gap. I will add it to the Q2 library roadmap. Can we move forward with the 90% of your auth surface area that is covered and add the custom piece in 8 weeks?"

**"We tried something like this 2 years ago and it was a mess."**
Response: "What went wrong then? I want to make sure we do not repeat it." Listen carefully. Often the failure was in process (no migration support, incompatible interfaces) not in the concept. Address the specific failure, not the general skepticism.

**"We don't have bandwidth until Q4."**
Response: "I understand. The security audit deadline is Q3. Here is what I can do: my team does the migration, you review and sign off. Estimated ask on your team is 4 hours total. Does that work?"

### Step 5: Framing the Proposal as Solving Their Problem

The language matters. Compare:

| Wrong framing | Right framing |
|---------------|---------------|
| "You need to adopt our library" | "You get to stop maintaining your own auth code" |
| "This is required for the security audit" | "This eliminates the auth-related incident class from your on-call rotation" |
| "Platform is standardizing on JWTs" | "Your team's implementation is the basis for the standard — we want you as co-owners" |
| "Other teams are already doing this" | "Checkout piloted it and reduced auth incidents by 73% in 8 weeks" |

The content is the same. The framing is about the other team's interests, not your team's interests.

---

## Presenting to Leadership: The 3-Slide Rule

When you need leadership support for a cross-team initiative, you have limited time and attention. The 3-slide rule:

**Slide 1: Context (1 min)**
- What is the current state?
- What is the cost of doing nothing? (In terms leadership cares about: engineer time, incidents, revenue risk, compliance)

**Slide 2: Recommendation (2 min)**
- What are you proposing?
- What is the expected outcome?
- What is the timeline and resource ask?

**Slide 3: Ask (30 sec)**
- What specific decision do you need from the room?
- "I need you to unblock 2 engineer-weeks from Checkout team for the migration"
- "I need you to set a Q3 compliance deadline for all teams"

The most common mistake: bringing a decision to leadership that could have been made at a lower level. If you can make the decision yourself, make it. Go to leadership only when you genuinely need their authority or resources.

---

## Negotiating Trade-offs: The Minimum Viable Agreement (MVA)

When teams have conflicting interests, the goal is not to find a solution that everyone loves — it is to find the minimum commitment that unblocks progress while preserving each team's ability to pursue its interests.

### MVA Framework

1. **What does each team need at minimum to move forward?** (Not: what would they ideally want?)
2. **What can each team give up with minimal cost?** (Not: what should they give up ideally?)
3. **Draft an agreement from those two lists.** It will be smaller than you hoped and larger than each team's minimum — that is correct.
4. **Write it down and get sign-off.** Verbal agreements about team boundaries evaporate.

Example: Platform team wants Inventory to fully adopt the auth library. Inventory cannot spare the bandwidth. MVA: Inventory adopts the library for all new endpoints (zero extra migration work). Existing endpoints migrate at their pace over 6 months. Platform provides a template PR to make it trivial. Inventory agrees to use the library for anything written after a specific date.

Neither team got exactly what they wanted. The platform team wanted full adoption now. Inventory wanted to not be involved at all. The MVA is a commitment they can both keep.

---

## Interview Scenario

**"Tell me about a time you influenced without authority."**

**Model STAR answer:**

**Situation:** "I was a Staff engineer on the data platform team. We had a situation where four product teams were each building their own analytics pipelines. The result was 4 different data models for the same business concepts, which meant our BI dashboards showed different numbers depending on which pipeline you queried. Finance was losing trust in the data."

**Task:** "I needed to get four teams, none of which reported to me, to converge on a single canonical data model and retire their custom pipelines."

**Action:** "I started by doing 1:1s with the tech lead or EM from each team before I proposed anything publicly. I wanted to understand their pipelines, their roadmaps, and what problems they were trying to solve. What I found: three of the four teams did not want to own a pipeline — they had built one because there was no alternative. Only one team (Analytics) had an opinion on the data model.

I made Analytics the co-owner of the canonical model. Their tech lead became the approver for schema changes. That removed their biggest objection — fear that Platform would make decisions about data definitions without their input.

For the other three teams, I made the value proposition explicit: 'You get to delete your pipeline. My team maintains the canonical one. Your on-call rotation shrinks.' I also offered to do the migrations for two of the three teams, because I knew they were bandwidth-constrained.

The one team that genuinely had custom requirements — they needed sub-minute latency that the canonical pipeline did not support — I scoped out a real-time layer on top of the canonical model that satisfied their requirement without requiring a separate pipeline.

I wrote an RFC that documented all of this, got sign-off from all four tech leads, and then presented it to VP Engineering as a fait accompli. I was not asking for approval — I was reporting what the teams had agreed to do and asking for engineering time to execute."

**Result:** "All four pipelines migrated to the canonical model over 8 months. Finance dashboard discrepancies went from a weekly occurrence to zero. Three teams deleted ~15K lines of pipeline code. The Analytics tech lead is now co-owner of the platform's data model, which he takes seriously."

**What makes this answer strong:** It is specific (4 teams, 8 months, 15K lines deleted). It shows all four influence levers: expertise (understood the pipelines), relationships (1:1s before the proposal), reciprocity (offered to do the migrations), framing (positioned as "delete your pipeline" not "adopt mine"). It acknowledges a real objection that required a real solution (the real-time latency requirement). And it ends with a specific outcome.

---

*Next:* [Incident Management](06-incident-management.md) — managing production incidents and writing blameless post-mortems
