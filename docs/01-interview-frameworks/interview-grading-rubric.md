# Interview Grading Rubric: What Interviewers Look For

Understanding how technical interviews are graded helps you understand what matters during the interview.

---

## Coding Interview Rubric

### Scoring Scale

**4 = Excellent:** Hiring signal
**3 = Proficient:** Weak hire or strong hold signal depending on role
**2 = Below Average:** Not recommended
**1 = Poor:** No hire

### Rubric Breakdown (4-point scale)

#### 1. Problem Understanding (1-4 points)

**4 - Excellent:**
- Asked clarifying questions about input, output, constraints
- Verified understanding with examples
- Identified edge cases proactively
- Stated assumptions clearly

**3 - Proficient:**
- Asked some clarifying questions
- Understood basic problem statement
- Minor assumptions not stated

**2 - Below Average:**
- Minimal clarification
- Misunderstood constraints
- Skipped edge cases

**1 - Poor:**
- Coded without understanding
- Solved wrong problem
- No questions asked

---

#### 2. Approach & Communication (1-4 points)

**4 - Excellent:**
- Explained approach clearly before coding
- Discussed multiple solutions (brute force → optimal)
- Explained trade-offs (time vs space)
- Thought aloud throughout

**3 - Proficient:**
- Explained general approach
- Mentioned complexity
- Some reasoning aloud
- Could explain decisions when asked

**2 - Below Average:**
- Vague approach explanation
- Jumped to code without planning
- Complexity analysis incomplete or wrong

**1 - Poor:**
- Silent coding
- No explanation of approach
- Guessing at complexity

---

#### 3. Code Quality (1-4 points)

**4 - Excellent:**
- Clean, readable code
- Good variable names (not `x`, `temp`)
- Proper data structures chosen
- Handles edge cases in code
- No off-by-one errors
- Modular (breaks into functions if complex)

**3 - Proficient:**
- Code works and is mostly readable
- Some naming could be better
- Handles common cases
- One or two small bugs/issues

**2 - Below Average:**
- Code has bugs or doesn't run
- Hard to follow logic
- Poor variable names
- Missing edge cases

**1 - Poor:**
- Code doesn't work
- Syntax errors
- Incomprehensible

---

#### 4. Verification & Testing (1-4 points)

**4 - Excellent:**
- Traced through example while coding
- Tested on happy path
- Tested edge cases (empty, single, boundary)
- Fixed issues independently

**3 - Proficient:**
- Tested on provided example
- Caught and fixed most bugs
- Some edge cases covered

**2 - Below Average:**
- Minimal testing
- Didn't catch obvious bugs
- Only tested happy path

**1 - Poor:**
- No testing
- Didn't verify code works
- Bugs left unfixed

---

#### 5. Complexity Analysis (1-4 points)

**4 - Excellent:**
- Correct time complexity stated
- Correct space complexity stated
- Explained how derived (loop analysis, etc.)
- Discussed optimizations if time permitted

**3 - Proficient:**
- Time complexity correct
- Space complexity mostly correct
- Could explain with hints

**2 - Below Average:**
- Complexity estimate wrong
- Missing space complexity
- Incomplete reasoning

**1 - Poor:**
- No complexity analysis
- Complexity completely wrong

---

#### 6. Optimization (1-4 points)

**4 - Excellent:**
- Identified optimal approach first time
- If brute force: optimized to O(n log n) or O(n)
- Explained why optimal (can't do better)
- Trade-offs understood

**3 - Proficient:**
- Found decent approach
- Could optimize with hints
- Understands trade-offs

**2 - Below Average:**
- Only brute force approach
- Didn't see optimization even with hints
- Premature optimization

**1 - Poor:**
- Approach is severely suboptimal O(n³) when O(n) possible
- Refused to optimize

---

### Typical Scoring Distribution

For a Leetcode Medium problem in 45 minutes:

| Score | Outcome |
|-------|---------|
| 20-24 (all 4s) | Strong hire |
| 17-19 (mix of 3-4) | Hire |
| 14-16 (mostly 3s) | Weak hire or hold |
| 11-13 (mix of 2-3) | Lean no hire |
| < 11 (2s and 1s) | No hire |

**Threshold varies by company:**
- Google: typically 18+
- Microsoft: 16+
- Amazon: 15+
- Startups: 14+

---

## System Design Interview Rubric

### Scoring Scale

Same 4-point scale, but different criteria.

#### 1. Requirements Gathering (1-4 points)

**4 - Excellent:**
- Asked about DAU, QPS, peak load
- Discussed read/write patterns
- Identified latency and availability targets
- Asked about geographic distribution
- Prioritized features

**3 - Proficient:**
- Asked about scale
- Understood basic requirements
- Missed some clarifications

**2 - Below Average:**
- Minimal questions
- Skipped scale questions
- Assumed requirements

**1 - Poor:**
- No clarification
- Designed system without understanding constraints

---

#### 2. Architecture Design (1-4 points)

**4 - Excellent:**
- Clear diagram with major components
- Data flow explained
- Component relationships shown
- Scalability considered
- Proper layering (load balancer, compute, data)

**3 - Proficient:**
- High-level architecture drawn
- Main components identified
- Some data flow unclear
- Mostly sensible design

**2 - Below Average:**
- Incomplete architecture
- Missing key components
- Unclear how pieces fit

**1 - Poor:**
- No clear design
- Monolithic thinking at scale

---

#### 3. Deep Dive (1-4 points)

**4 - Excellent:**
- Chose 2-3 critical components for deep dive
- Explained caching strategy with specific tools
- Database design with indexes and partitioning
- Message queue flow for async tasks
- Trade-offs discussed

**3 - Proficient:**
- Deep dived into 1-2 components
- Explained general approach
- Some design details missing

**2 - Below Average:**
- Shallow deep dive
- Missed critical details
- No specific technologies

**1 - Poor:**
- No deep dive
- Only high-level design

---

#### 4. Handling Scale (1-4 points)

**4 - Excellent:**
- Discussed 10x and 100x scaling
- Sharding strategy explained
- Read replica deployment
- Cache invalidation at scale
- Database partitioning

**3 - Proficient:**
- Addressed scaling with hints
- General strategies mentioned
- Some details missing

**2 - Below Average:**
- Scaling not well thought through
- Vague scaling approach

**1 - Poor:**
- No scaling consideration
- "We'll add more servers" (insufficient)

---

#### 5. Trade-offs (1-4 points)

**4 - Excellent:**
- CAP theorem discussed with context
- Consistency vs latency trade-off
- Cost vs performance trade-off
- Mentioned alternatives and why chosen

**3 - Proficient:**
- Discussed some trade-offs
- Explained reasoning

**2 - Below Average:**
- Minimal trade-off discussion
- Decisions not well justified

**1 - Poor:**
- No trade-off consideration

---

#### 6. Communication & Knowledge (1-4 points)

**4 - Excellent:**
- Clear explanations, no jargon without context
- Confident in decisions
- Handled follow-ups smoothly
- Asked clarifying questions when needed
- Admitted uncertainty on some topics (OK)

**3 - Proficient:**
- Generally clear
- Mostly confident
- Could explain with hints

**2 - Below Average:**
- Unclear explanations
- Lack of confidence
- Struggled with follow-ups

**1 - Poor:**
- Incomprehensible design
- Not knowledgeable

---

### Typical System Design Scoring

For a 1-hour system design interview:

| Score | Outcome |
|-------|---------|
| 20-24 | Definite hire |
| 18-19 | Hire |
| 16-17 | Lean hire |
| 14-15 | Lean no hire |
| < 14 | No hire |

---

## Behavioral Interview Rubric

### Scoring Scale

Same 4-point scale.

#### 1. Story Structure & Clarity (1-4 points)

**4 - Excellent:**
- Clear STAR structure (Situation, Task, Action, Result)
- 2-3 minutes, not rambling
- Easy to follow with concrete details
- Data/metrics included

**3 - Proficient:**
- Mostly STAR structure
- Some irrelevant details
- Somewhat clear

**2 - Below Average:**
- Unclear story
- Rambling (5+ minutes)
- Missing key details

**1 - Poor:**
- Incoherent story
- Can't follow narrative

---

#### 2. Ownership & Leadership (1-4 points)

**4 - Excellent:**
- Uses "I" statements
- Shows personal agency and decision-making
- Took responsibility, not blamed others
- Led/influenced outcomes

**3 - Proficient:**
- Mostly uses "I"
- Shows some ownership
- Mentioned team work appropriately

**2 - Below Average:**
- Often says "we" (unclear contribution)
- Passive role
- Some blame on others

**1 - Poor:**
- All "we", no personal contribution
- Victim mentality, all external factors

---

#### 3. Impact & Results (1-4 points)

**4 - Excellent:**
- Quantifiable impact (30% improvement, shipped 2 months early)
- Clear business or team impact
- Understood why action mattered

**3 - Proficient:**
- Some metrics
- Clear positive outcome
- Impact somewhat vague

**2 - Below Average:**
- Vague results ("it went well")
- No numbers
- Limited impact

**1 - Poor:**
- No clear result
- Story ended in failure with no learning

---

#### 4. Growth & Learning (1-4 points)

**4 - Excellent:**
- Clear lesson learned
- Self-aware about mistakes
- Growth mindset ("I should have...")
- Applied learning to later decisions

**3 - Proficient:**
- Some learning mentioned
- Reasonable reflection
- Constructive takeaway

**2 - Below Average:**
- Minimal learning discussed
- Defensive about failure

**1 - Poor:**
- No learning
- Blamed others entirely

---

#### 5. Relevance to Company Values (1-4 points)

**4 - Excellent:**
- Story demonstrates company value directly
- Examples align with stated mission
- Shows cultural fit

**3 - Proficient:**
- Story is relevant
- Somewhat aligned
- Competence shown

**2 - Below Average:**
- Weak relevance
- Off-topic stories
- Doesn't match values

**1 - Poor:**
- Story contradicts values
- No connection to company culture

---

### Typical Behavioral Scoring

| Score | Outcome |
|-------|---------|
| 18-20 | Strong hire (shows leadership, growth) |
| 16-17 | Hire (solid performer) |
| 14-15 | Weak hire or hold |
| < 14 | No hire (culture mismatch or low impact) |

---

## Overall Interview Scoring

### Final Decision Framework

**Committee typically reviews:**
1. Coding interview score
2. System design score (if applicable)
3. Behavioral interview score
4. Manager interview (culture fit)

**Overall Recommendation:**

```
Strong Hire (Approve):
- All rounds: 3-4 on rubric
- Consensus among interviewers
- No red flags

Hire (Lean Yes):
- Most rounds: 3+
- 1-2 weak areas, but compensated by strengths
- No major red flags

Hold / Maybe:
- Mixed signals
- Stronger candidate needed, but not disqualified
- Often reconsider with new skills

Lean No (Likely Reject):
- Multiple rounds: 2s
- Critical gap (can't code but could learn design)
- Culture concern

No Hire (Reject):
- Multiple rounds: 1-2
- Critical missing skills
- Red flag (integrity, communication)
```

---

## Red Flags That Lower Scores

| Red Flag | Impact |
|----------|--------|
| **Dishonest about knowledge** | Automatic no hire (trust issue) |
| **Arrogant/dismissive** | Culture issue, team concern |
| **Blames others entirely** | Lack of accountability |
| **Can't explain reasoning** | Communication or knowledge gap |
| **Gives up easily** | Persistence concern |
| **Negative about current role** | Culture concern (will be negative here) |

---

## Green Flags That Raise Scores

| Green Flag | Impact |
|-----------|--------|
| **Admits uncertainty** | Confidence + humility |
| **Asks good questions** | Curiosity, learning mindset |
| **Handles feedback well** | Growth mindset |
| **Shows trade-off thinking** | Strategic thinking |
| **Mentions testing & edge cases** | Quality focus |
| **References past learning** | Growth and self-improvement |

---

## Interview Rubric Checklist

**Before Interview:**
- ✓ Know evaluation criteria
- ✓ Understand what "excellent" looks like
- ✓ Practice asking clarifying questions
- ✓ Practice communicating approach

**During Interview:**
- ✓ Ask questions (shows engagement)
- ✓ Explain reasoning aloud (can't grade silence)
- ✓ Verify understanding before coding
- ✓ Test and trace examples
- ✓ Use "I" in behavioral (show ownership)
- ✓ Discuss trade-offs (shows depth)

**Goal:**
- Aim for all 3-4s on rubric
- Minimum passing is typically 14-18 out of 24 depending on company
- Red flags matter more than minor weaknesses

