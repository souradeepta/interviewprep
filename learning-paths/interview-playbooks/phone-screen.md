---
title: "Phone Screen Interview Playbook"
interview_type: "Phone Screening"
duration: "30-45 minutes"
difficulty: "Easy to Medium"
focus: "Arrays, Strings, Basic Problem-Solving"
---

# Phone Screen Interview Playbook

**Level:** L3-L5
**Time to read:** ~10 min

**Duration:** 30-45 minutes  
**Expected Problems:** 1 easy problem + 1 quick follow-up  
**Goal:** Solve quickly, communicate clearly, verify edge cases

---

## Interview Format

### Time Breakdown (45 min total)
- **0-2 min:** Greeting & problem explanation
- **2-5 min:** Clarify requirements
- **5-20 min:** Whiteboard/code solution
- **20-25 min:** Test with examples
- **25-30 min:** Optimize (if time permits)
- **30-45 min:** Follow-up questions OR behavioral

---

## What to Expect

**Problem Type:** Usually ONE easy problem, sometimes with a quick variant.

**Topics:** Arrays, strings, hash tables (what you can solve in 15-20 minutes).

**Evaluation:** Can you:
- Understand the problem quickly?
- Come up with a solution?
- Code it cleanly?
- Test with examples?
- Communicate throughout?

---

## Must-Master Problems

Pick these canonical problems and master them:

1. **Two Sum** (Arrays)
   - Find two numbers that sum to target
   - Pattern: Hash map
   - See: [Arrays Domain](../domains/arrays.md)

2. **Valid Parentheses** (Stack pattern)
   - Check if brackets are balanced
   - Pattern: Stack
   - See: [Stacks/Queues Domain](../domains/stacks-queues.md)

3. **Reverse String** (Arrays)
   - Reverse a string in-place
   - Pattern: Two pointers
   - See: [Strings Domain](../domains/strings.md)

4. **Remove Duplicates** (Arrays)
   - Remove duplicates from sorted array
   - Pattern: Two pointers
   - See: [Arrays Domain](../domains/arrays.md)

5. **Contains Duplicate** (Hash Tables)
   - Check if array has duplicates
   - Pattern: Hash set
   - See: [Hash Tables Domain](../domains/hash-tables.md)

---

## Key Patterns

### Two Pointers
Use when: Find pair, reverse, remove duplicates  
How: One pointer at start, one at end, move inward

```python
def reverse(arr):
    left, right = 0, len(arr) - 1
    while left < right:
        arr[left], arr[right] = arr[right], arr[left]
        left += 1
        right -= 1
```

### Hash Map / Set
Use when: Deduplication, lookups, frequency  
How: Store what you've seen, check before processing

```python
def two_sum(arr, target):
    seen = {}
    for num in arr:
        complement = target - num
        if complement in seen:
            return [seen[complement], arr.index(num)]
        seen[num] = arr.index(num)
```

### Stack
Use when: Reverse, matching pairs, LIFO  
How: Push when entering, pop when exiting

```python
def is_valid(s):
    stack = []
    pairs = {'(': ')', '[': ']', '{': '}'}
    for char in s:
        if char in pairs:
            stack.append(char)
        else:
            if not stack or pairs[stack.pop()] != char:
                return False
    return not stack
```

---

## Interview Flow

### 🎯 Phase 1: Clarify (2 min)
- Repeat the problem in your own words
- Ask: "Can the array be empty?" "Can there be duplicates?" "What's the range?"
- Get YES/NO on edge cases

### 💭 Phase 2: Approach (3 min)
- **Explain your idea first**, don't code yet
- "I'm thinking of using a hash map to store seen values..."
- Wait for feedback

### 💻 Phase 3: Code (15 min)
- Write pseudocode first (1 min)
- Then write actual code (10 min)
- Use clean, readable code
- Add comments for non-obvious steps

### ✅ Phase 4: Test (5 min)
- Test with PROVIDED example
- Test with EDGE CASES:
  - Empty input
  - Single element
  - All same elements

### 🚀 Phase 5: Optimize (5 min, if time)
- "Can we do better than O(n) time?" (Usually: no)
- "Can we use less space?" (Sometimes: yes)

---

## Red Flags to Avoid

❌ **Don't:**
- Code before explaining your approach
- Test only the happy path
- Use unexplained variable names (arr, x, y)
- Say "this is obvious" when it's not
- Panic when you make a mistake

✅ **Do:**
- Communicate every step
- Test edge cases
- Ask clarifying questions
- Correct mistakes calmly
- Explain your logic

---

## Quick Reference

| Pattern | Time | Example |
|---------|------|---------|
| Two Pointers | O(n) | Remove duplicates |
| Hash Map | O(1) lookup | Two Sum |
| Stack | O(n) | Valid parentheses |

---

## After the Interview

- Send thank you email within 2 hours
- If asked for follow-ups, have them ready:
  - "How would this change with negative numbers?"
  - "What if we needed to return all pairs?"
  - "Can we solve this without extra space?"

---

## Resources

- [Arrays Domain](../domains/arrays.md)
- [Strings Domain](../domains/strings.md)
- [Stacks/Queues Domain](../domains/stacks-queues.md)
- [Hash Tables Domain](../domains/hash-tables.md)
