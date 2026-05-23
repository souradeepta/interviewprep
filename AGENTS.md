# Using the Interview Agents

This repo includes two Claude Code agents for mock interview practice.

## Agents

### `sde2-interviewer` — Alex, SDE2 Interviewer

Alex conducts realistic technical interviews. Use this when you want to practice **being the candidate**.

**Start a session:**
```
/agent sde2-interviewer
```

Alex will introduce the format, ask a data structures problem, probe your approach, check edge cases and complexity, and give structured feedback at the end.

**Tips for getting the most out of it:**
- Treat it like a real interview — think out loud
- Ask clarifying questions before jumping to code
- State your brute-force first, then optimize
- When you finish, ask Alex "how did I do?" for detailed feedback

---

### `sde-candidate` — Jordan, SDE Candidate

Jordan is a candidate you can interview. Use this when you want to practice **being the interviewer**.

**Start a session:**
```
/agent sde-candidate
```

Give Jordan a problem — "implement a stack that supports getMin in O(1)" — and see how they think. Practice asking follow-up questions, giving hints, and evaluating their answer.

**Configuring skill level:**
- Start with "Junior candidate:" to get a less experienced Jordan
- Start with "Senior candidate:" to get a more experienced Jordan
- Default is mid-level (SDE1/SDE2)

---

## Example Flows

### Flow 1: Full mock interview (you = candidate)

```
You: /agent sde2-interviewer

Alex: Hi, I'm Alex. We'll spend about 45 minutes on a coding problem today.
      Feel free to think out loud — I care about your process.
      Ready? Here's your problem: Given a linked list, detect if it has a cycle.

You: Sure! Can the list be empty? What should I return — a boolean?

Alex: Good questions. Yes, it can be empty. Return a boolean.

You: My first thought is to use a hash set — track visited nodes...
     But I know there's a more space-efficient approach with two pointers.
     Floyd's cycle detection: fast pointer moves 2 steps, slow moves 1.
     If they meet, there's a cycle.

Alex: Good. What's the time and space complexity?

You: Time O(n), space O(1) — much better than the hash set approach.

Alex: What if the list is very long and the cycle starts near the end?
      Does your algorithm still work?

You: Yes — the fast and slow pointers will always meet if there's a cycle,
     regardless of where it starts. [explains why]

Alex: Nice. Code it up.

You: [writes code]

Alex: ## Interview Feedback
      Overall Score: 4/5
      ...
```

---

### Flow 2: Practice as interviewer (you = interviewer)

```
You: /agent sde-candidate
     Junior candidate: I want you to implement an LRU Cache.

Jordan: Oh, an LRU Cache! Okay... before I start, can I ask —
        what operations do I need to support? Just get and put?
        And what should I return if a key doesn't exist?

You: Yes, get and put. Return -1 if key doesn't exist.
     I also need both to run in O(1).

Jordan: O(1)... hmm. A hash map gives O(1) lookup but I need
        to track usage order too. Maybe I use a list?

You: [hint] What if you combined a hash map with something
     that supports O(1) insertion and deletion at arbitrary positions?

Jordan: Oh! A doubly linked list — I can remove and re-insert
        nodes in O(1) if I have pointers. And the hash map
        stores key → node pointer. Let me draw this out...
```

---

## Documentation Standards for Agents

The agents should evaluate and test knowledge against these documentation standards:

### Trade-off Knowledge
Agents should ask: "What are the trade-offs between X and Y?"
- Candidates should identify cost/performance/consistency trade-offs
- Expect comparison tables in good answers
- Real numbers (latency, throughput, scale) matter
- "It depends" is good if followed by "depends on..."

### Architectural Thinking
Agents should probe: "Design this system..."
- Candidates should draw diagrams (ASCII or described)
- Include scaling patterns (Sharding, Master-Replica, CQRS)
- Consider failures and recovery
- Justify architecture choices with trade-offs

### Interview-Ready Depth
Agents should test:
- **Theory:** Fundamentals, concepts, algorithms
- **Practice:** Real code, working solutions, edge cases
- **Scale:** 1M users, 1B events, how does design change?
- **Trade-offs:** Cost vs. performance, consistency vs. availability

### Exercise-Based Learning
Agents should reference exercises:
- "Have you tried the distributed counter exercise?"
- "What about handling concurrent writes like in Exercise 3?"
- "Show me code like the solutions in the exercises section"

### Documentation Quality
When agents give feedback, they should mention:
- "Your answer has good theory but needs trade-offs"
- "Consider architectural diagrams like in the guides"
- "Walk through a practical exercise to solidify this"

---

## Problem Difficulty Guide

| Topic | Easy | Medium | Hard |
|---|---|---|---|
| Array | Two Sum | Container With Most Water | Median of Two Sorted Arrays |
| Linked List | Reverse LL | LRU Cache | Merge K Sorted Lists |
| Stack | Valid Parentheses | Daily Temperatures | Largest Rectangle in Histogram |
| BST | Validate BST | K-th Smallest in BST | Serialize/Deserialize BST |
| Heap | K Largest Elements | Top K Frequent Words | Find Median from Data Stream |
| Graph | Number of Islands | Course Schedule | Alien Dictionary |
| Trie | Implement Trie | Word Search II | — |
| Segment Tree | Range Sum Query | Range Min Query | Count of Range Sum |
| Union Find | Number of Provinces | Redundant Connection | Accounts Merge |
