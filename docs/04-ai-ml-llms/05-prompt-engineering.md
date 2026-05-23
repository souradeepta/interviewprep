# Prompt Engineering & Design — Techniques & Patterns

How to get the best results from LLMs without retraining.

---

## 📝 Core Principles

### Be Specific, Not Vague

❌ Bad:
```
Write about cats
```

✅ Good:
```
Write a 200-word blog post about why cats make good indoor pets, including 3 benefits
and a brief care tip. Target audience: first-time pet owners.
```

### Provide Context

```
Role: You are an expert AWS architect
Task: Design a system for 1M concurrent users
Constraint: Budget < $100k/month
Format: Provide architecture diagram, trade-offs, and scaling strategy
```

### Show Examples (Few-Shot Learning)

```
Classify sentiment: positive, negative, or neutral

Examples:
"Great product!" → positive
"Terrible experience" → negative  
"It's okay" → neutral

Classify: "Pretty good, could be better"
```

### Specify Output Format

```
Generate a JSON object with fields: name, age, email
For this person: John, 28 years old, john@example.com

Expected output:
{
  "name": "John",
  "age": 28,
  "email": "john@example.com"
}
```

---

## 🎯 Prompting Techniques

### Chain-of-Thought (CoT)

Ask model to explain reasoning before answering.

```
Question: A store sells apples at $1.50 each. Sarah buys 5 apples.
How much does she spend?

CoT Prompt:
Q: A store sells apples at $1.50 each. Sarah buys 5 apples.
How much does she spend?

A: Let me think through this step by step:
1. Price per apple: $1.50
2. Number of apples: 5
3. Total: 1.50 × 5 = $7.50

Answer: $7.50
```

**When to use:** Complex reasoning, math, logic
**Effect:** Improves accuracy, especially on harder problems

### Zero-Shot vs. Few-Shot

**Zero-Shot** (no examples):
```
Translate to French: Hello, how are you?
```

**Few-Shot** (with examples):
```
Translate to French:
- Hello → Bonjour
- Goodbye → Au revoir
- How are you? → Comment allez-vous?

Translate: Good morning → 
```

**Tradeoff:** Few-shot more accurate, uses more tokens

### Role-Based Prompting

```
Role: You are a senior software engineer with 10 years of experience
Task: Review this code for performance issues

[code here]

Provide:
1. 3 main performance issues
2. Fixes with complexity analysis
3. Trade-offs of each fix
```

### Tree-of-Thought

Explore multiple reasoning paths:

```
Question: Should we launch a startup?

Consider from perspectives:
1. Financial: Initial costs, runway, revenue potential
2. Market: Competitive landscape, timing, demand
3. Team: Skills, experience, commitment required
4. Risk: What could go wrong? How to mitigate?

Evaluate each path, then synthesize final recommendation.
```

---

## 🔄 Advanced Patterns

### Retrieval-Augmented Prompting

Include relevant context from knowledge base:

```
Context from knowledge base:
[relevant documents about topic]

Question: [user query]

Answer based on the provided context. If not in context, say "not found".
```

### Step-Back Prompting

First ask clarifying questions:

```
Before answering, consider:
1. What is the fundamental question here?
2. What assumptions am I making?
3. What additional context would help?
4. What are different perspectives on this?

Now answer the question.
```

### Iterative Refinement

```
Initial prompt → Model response → Refine prompt → Better response

Example:
1st: "Write code to sort an array"
→ Returns simple bubble sort

2nd: "Write optimized Python code using built-in functions to sort integers.
Include complexity analysis and one alternative approach."
→ Returns sorted() with explanation of O(n log n)
```

---

## 🚀 System Prompts & Instructions

### Persona Definition

```
You are Claude, an AI assistant made by Anthropic.
You are helpful, harmless, and honest.
You acknowledge limitations and uncertainties.
You think step-by-step before answering complex questions.
```

### Behavioral Instructions

```
Guidelines:
- Always show your reasoning
- Admit when you're unsure
- Ask clarifying questions if needed
- Provide examples for complex concepts
- Suggest follow-up questions if relevant
```

### Constraint Definition

```
Constraints:
- Response limited to 500 words
- Use only technical terms appropriate for beginners
- Provide both theoretical explanation and practical example
- Format as markdown with clear sections
```

---

## 💡 Real Interview Examples

### System Design Question

```
You are a system design expert.

Question: Design an LLM inference serving system for 10k concurrent users
with <100ms latency requirement.

Required:
1. Architecture diagram (text format)
2. Key components and their roles
3. Bottlenecks and how to address
4. Scaling strategy
5. Cost considerations
```

### Coding Interview

```
Language: Python
Style: Clean, production-ready code
Include: Type hints, docstrings, error handling, unit tests
Problem: Implement LRU cache with get and put operations

Expected format:
```python
class LRUCache:
    def __init__(self, capacity: int):
        pass
    
    def get(self, key: int) -> int:
        pass
    
    def put(self, key: int, value: int) -> None:
        pass
```

---

## 🔧 Optimization Techniques

### Temperature Control

```python
# Conservative (more deterministic)
response = model.generate(prompt, temperature=0.2)

# Balanced (good for most tasks)  
response = model.generate(prompt, temperature=0.7)

# Creative (more diverse)
response = model.generate(prompt, temperature=1.0)
```

### Top-K & Top-P Sampling

```python
# Top-K: Sample from top K tokens
response = model.generate(prompt, top_k=50)

# Top-P (nucleus sampling): Sample from smallest set of tokens 
# that achieve cumulative probability P
response = model.generate(prompt, top_p=0.9)
```

### Token Optimization

```
💭 Always think about token count:
- Input tokens: 1000 tokens = maybe $0.01 input
- Output tokens: 500 tokens = maybe $0.05 output

Long system prompts with lots of context are expensive!

Solution: Token compression, caching, summarization
```

---

## ❌ Common Mistakes

### Mistake 1: Too Vague Prompts
```
❌ "Explain machine learning"
✅ "Explain supervised vs. unsupervised learning with 2 examples each"
```

### Mistake 2: Contradictory Instructions
```
❌ "Be concise but thorough"
✅ "Provide concise explanation (3 sentences) then detailed breakdown"
```

### Mistake 3: Not Providing Format
```
❌ "List your thoughts"
✅ "Provide your thoughts as a numbered list with 1-2 sentences each"
```

### Mistake 4: Ignoring Context Length
```
❌ Including 10,000 token document in every request
✅ Summarize document, use RAG for relevant sections
```

---

## ❓ Interview Q&A

**Q: How does prompt engineering differ from fine-tuning?**
A: Prompt engineering uses words to guide model (in-context), fine-tuning updates weights. Engineering is fast/cheap, fine-tuning is better for specific tasks/style.

**Q: When would you use chain-of-thought prompting?**
A: For problems requiring reasoning (math, logic, complex analysis). Shows work step-by-step, improves accuracy on hard problems.

**Q: How do you optimize prompts for cost and speed?**
A: Be concise (fewer tokens), avoid redundancy, cache system prompts, use lower temperature (faster generation), batch requests.

**Q: What's the difference between few-shot and zero-shot?**
A: Zero-shot: No examples. Few-shot: Include 2-5 examples. Few-shot more accurate but uses more tokens. Use based on task complexity.

---

## ✅ Checklist

- [ ] Write specific, detailed prompts
- [ ] Know when to use zero-shot vs. few-shot
- [ ] Understand chain-of-thought prompting
- [ ] Use role-based prompting for better context
- [ ] Specify output format explicitly
- [ ] Understand temperature and sampling strategies
- [ ] Think about token costs
- [ ] Use iterative refinement
- [ ] Avoid common prompt engineering mistakes

---

**Last updated:** 2026-05-22
