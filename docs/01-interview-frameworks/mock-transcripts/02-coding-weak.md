# Mock Coding Interview — Weak Candidate Signal

**Problem:** Longest Substring Without Repeating Characters (LC #3)
**Level:** L4 (mid-level)
**Duration:** ~40 minutes (extra time due to debugging)

---

## Transcript

**Interviewer:** I'd like you to solve a string problem. Given a string `s`, find the length of the longest substring without repeating characters. For example, given `"abcabcbb"`, the answer is `3` because `"abc"` is the longest. Ready?

**Candidate:** Yeah, let me just code this up.

> **[Annotation: No Clarifying Questions]:** The candidate skips clarification entirely. What if the string has Unicode? What if it's empty? What does case-sensitivity mean here? A 60-second investment in questions prevents a wasted 10 minutes on the wrong implementation. This is a yellow flag at L3 and a red flag at L4+.

**Candidate:** Okay so I'm thinking I'll just use two for loops and check every substring.

```python
def longest(s):
    max_len = 0
    for i in range(len(s)):
        for j in range(i, len(s)):
            temp = s[i:j]
            arr = list(temp)
            if len(arr) == len(set(arr)):
                max_len = max(max_len, len(arr))
    return max_len
```

> **[Annotation: Nested Loops Without Framing]:** Jumping directly to a nested loop implementation without naming it as "brute force" and without mentioning complexity signals that the candidate doesn't have a plan — they're just trying things. The variable names `temp` and `arr` are redundant (both hold the same substring) and convey no intent. At L4, the interviewer expects the candidate to name the approach, state its complexity, and acknowledge its limitations before coding.

**Interviewer:** What's the time complexity of this?

**Candidate:** Um... it's like O(n²) I think? Because of the two loops.

> **[Annotation: Incorrect Complexity Analysis]:** The actual complexity is O(n³): O(n²) substrings × O(n) to convert to list and create a set. The candidate gave a wrong answer confidently, which is worse than saying "let me think through that." The `list(temp)` conversion is also unnecessary — `set(s[i:j])` works directly on strings in Python.

**Interviewer:** Can you think of a more efficient approach?

**Candidate:** Hmm... maybe use a sliding window? I've heard of that. Let me try.

> **[Annotation: Technique Recalled, Not Understood]:** Saying "I've heard of that" signals pattern recall rather than deep understanding. A strong candidate would explain the intuition: "We don't need to restart from scratch when we find a duplicate — we just shrink from the left." Lacking this explanation, the implementation is likely to have bugs.

**Candidate:** Okay, so I'll do something like this...

```python
def longest(s):
    x = 0
    y = 0
    best = 0
    seen = []

    while y < len(s):
        if s[y] not in seen:
            seen.append(s[y])
            y += 1
            best = max(best, y - x)
        else:
            seen.remove(s[x])
            x += 1

    return best
```

> **[Annotation: List Instead of Set, No Narration]:** Using a list for `seen` makes membership testing O(n) and removal O(n), pushing the overall complexity back to O(n²). A set would give O(1) for both. The candidate did not narrate while coding — the interviewer has to guess the intent from the variable names `x` and `y`, which give no semantic signal. `left` and `right` would have been clear immediately.

**Interviewer:** Walk me through a test case.

**Candidate:** Sure, let me try `"abcabcbb"`. So `x=0, y=0`... `'a'` not in seen, add it, y goes to 1, best is 1. Then `'b'`, add, y=2, best=2. `'c'`, add, y=3, best=3. Now `'a'`... it's in seen, so remove `seen[0]` which is `'a'`, x becomes 1. Next iteration, `'a'` not in seen, add it, y=4, best is... `4 - 1 = 3`, still 3. Okay I think it works.

> **[Annotation: Partial Trace, Happy-Path Only]:** The candidate only traced enough to confirm the example gives 3. They stopped before reaching the `"bb"` portion where the window shrinks aggressively. More importantly, they tested only the provided example — no edge cases, no adversarial input. A correct trace of `"bbbbb"` or `""` would have revealed issues.

**Interviewer:** What happens with an empty string?

**Candidate:** Oh... I guess the while loop just doesn't run. So it returns 0. Yeah that should be fine.

> **[Annotation: Edge Case Only When Prompted]:** The candidate didn't proactively think about the empty string — they relied on the interviewer to surface it. When prompted, the reasoning is correct, but the signal is that the candidate isn't scanning for failure modes independently. At L4, candidates are expected to enumerate edge cases without prompting.

**Interviewer:** What about the string `"abba"`?

**Candidate:** Let me trace it... `x=0, y=0`, add `'a'`, y=1, best=1. Add `'b'`, y=2, best=2. Add `'b'` — wait, `'b'` is already in seen. So remove `seen[0]` which is `'a'`, x=1. Now check again — `'b'` is still in seen. Remove `seen[0]` which is now `'b'`, x=2. Now add `'b'`, y=3, best is `3 - 2 = 1`. Add `'a'` — `'a'` is not in seen... wait, is it? Let me check. seen is `['b']` at this point. So add `'a'`, y=4, best is `4 - 2 = 2`. That's correct!

> **[Annotation: Slow Manual Trace, Uncertainty Visible]:** The candidate got the right answer but took too long and showed visible uncertainty ("wait, is it?"). This is a symptom of not having a clear mental model. The list-based `seen` makes it hard to reason about state because removal order matters and it's O(n). With a set, the state is simpler to reason about.

**Interviewer:** Any other improvements you can think of?

**Candidate:** I think the complexity is good now. O(n) maybe? I'm not sure about the list operations though.

> **[Annotation: Doesn't Identify Own Performance Bug]:** The candidate cannot confirm whether their solution is O(n) because they recognize the list operations might hurt — but they haven't worked through it. A list's `in` operator and `remove` are both O(n), making the overall solution O(n²). The candidate should have caught this themselves during the design phase, or at least flagged it as a concern to fix.

**Interviewer:** Alright, we're out of time. Do you have any questions?

**Candidate:** No, I think we're good.

> **[Annotation: No Questions for Interviewer]:** Asking no questions at the end is a missed signal. Good candidates ask about team, engineering culture, or what the hardest technical challenge has been recently. It's also a small but real data point — curiosity is a valued trait.

---

## Summary of Weak Signals

- Jumped to code without asking any clarifying questions
- Implemented brute force without naming it as such or stating its complexity
- Gave an incorrect complexity estimate (said O(n²), actual is O(n³))
- Used `temp` and `arr` as meaningless variable names in first attempt
- Used a list instead of a set for `seen`, making membership/removal O(n) — effectively undoing the sliding window optimization
- Named pointers `x` and `y` instead of `left` and `right`, making intent unclear
- Did not proactively test edge cases — only verified the provided example
- Could not confirm whether the final solution is O(n) due to uncertainty about list performance
- Asked no questions at the end of the interview

## What This Answer Would Score

- L3 bar: ⚠️ Borderline (got a working answer eventually, but with significant guidance and performance blind spots)
- L4 bar: ❌ Does not pass (no complexity analysis, poor variable naming, O(n²) implementation presented as O(n), no proactive edge case coverage)
