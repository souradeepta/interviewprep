# Mock Coding Interview — Strong Candidate Signal

**Problem:** Longest Substring Without Repeating Characters (LC #3)
**Level:** L4 (mid-level)
**Duration:** ~35 minutes

---

## Transcript

**Interviewer:** I'd like you to solve a string problem. Given a string `s`, find the length of the longest substring without repeating characters. For example, given `"abcabcbb"`, the answer is `3` because `"abc"` is the longest. Ready?

**Candidate:** Yes, sounds good. Before I dive in, I have a few quick questions. First, is the input ASCII only, or could it include Unicode characters? Second, should the comparison be case-sensitive — so `'A'` and `'a'` are treated as different? And third, what should I return for an empty string?

> **[Annotation: Clarifying Questions]:** Asking about ASCII vs. Unicode is a senior-level instinct — it directly affects whether a fixed-size array (size 128) works as the character set, or whether a hash map is required. Case-sensitivity and empty-string behavior close off ambiguity before writing a single line. Strong candidates spend 60-90 seconds here; weak ones skip straight to code.

**Interviewer:** Good questions. Assume ASCII printable characters only. Case-sensitive, yes. Return 0 for an empty string.

**Candidate:** Perfect. Let me think through this out loud. The brute-force approach would be to check every possible substring — that's O(n²) substrings, each taking O(n) to validate for uniqueness, so O(n³) overall, or O(n²) if I use a set per substring. That's too slow for large inputs.

> **[Annotation: Brute Force First]:** Naming the brute force — and its complexity — before jumping to the optimal solution shows structured thinking. Interviewers want to see that the candidate understands *why* we're optimizing, not just that they memorized a pattern.

**Candidate:** The better approach is a sliding window. I'll maintain two pointers, `left` and `right`, defining the current window. I'll use a set to track characters currently in the window. When I move `right` and the new character is already in the set, I shrink from the left until the duplicate is gone. At each step I record the maximum window size. That's O(n) time — each character enters and exits the window at most once — and O(min(n, 128)) space for the set, which is effectively O(1) for ASCII.

> **[Annotation: Algorithm Narration Before Coding]:** Explaining the approach in plain English before writing code is a strong signal. It proves the candidate has a mental model, not just pattern recall. It also gives the interviewer a chance to course-correct before 10 minutes of code are written.

**Candidate:** Let me code that up.

```python
def length_of_longest_substring(s: str) -> int:
    seen = set()
    left = 0
    max_len = 0

    for right in range(len(s)):
        # Shrink window from left until no duplicate
        while s[right] in seen:
            seen.remove(s[left])
            left += 1
        seen.add(s[right])
        max_len = max(max_len, right - left + 1)

    return max_len
```

> **[Annotation: Clean Code Structure]:** The variable names are semantically meaningful (`seen`, `left`, `right`, `max_len`). The logic maps directly to the stated algorithm. No magic numbers. This makes the code easy to trace through with the interviewer.

**Candidate:** Let me trace through the example. For `"abcabcbb"`: `right=0`, add `'a'`, window is `"a"`, length 1. `right=1`, add `'b'`, window `"ab"`, length 2. `right=2`, add `'c'`, window `"abc"`, length 3 — that's our max so far. `right=3`, `'a'` is in seen, so we remove `'a'` and move left to 1. Now add `'a'`, window is `"bca"`, length 3. The max stays at 3. Continuing... `right=6`, `'b'` hits again, we shrink... final answer is 3.

> **[Annotation: Dry Run with Example]:** Walking through the provided example before claiming the code is correct shows intellectual honesty. It catches off-by-one bugs and reassures the interviewer the candidate understands their own code. This is not optional — always trace at least one example.

**Interviewer:** Nice. What are some edge cases?

**Candidate:** A few I want to handle: empty string returns 0 — the for loop never executes, so `max_len` stays 0. Correct. All unique characters like `"abcde"` — the while loop never fires, window grows to the full length, returns 5. All same characters like `"aaaa"` — every step hits the while loop, left chases right, window is always size 1, returns 1. I think those are the main cases.

> **[Annotation: Proactive Edge Case Coverage]:** Naming specific edge cases and reasoning through them without being prompted is an L4+ signal. The candidate doesn't just say "I'd test edge cases" — they actually enumerate them and verify correctness against the algorithm mentally.

**Interviewer:** What's the complexity?

**Candidate:** Time is O(n) — each index is visited by `right` once and by `left` at most once, so at most 2n iterations. Space is O(k) where k is the character set size; for ASCII it's bounded at 128, so effectively O(1).

> **[Annotation: Precise Complexity Analysis]:** Giving O(n) without explanation is acceptable. Explaining *why* it's O(n) — specifically that each pointer moves at most n steps — is the difference between reciting an answer and demonstrating understanding.

**Interviewer:** Could you optimize the space or time further?

**Candidate:** The set tells us whether a character is in the window, but it forces us to remove characters one at a time from the left when there's a duplicate — that's why we have the inner while loop. If I replace the set with a dictionary mapping each character to its most recent index, I can jump `left` directly to `last_seen[char] + 1` instead of advancing one step at a time. That makes duplicate removal O(1) instead of potentially O(n) in pathological cases, though the amortized complexity of the set version is already O(n). The dict version is slightly cleaner:

```python
def length_of_longest_substring_v2(s: str) -> int:
    last_seen = {}
    left = 0
    max_len = 0

    for right, char in enumerate(s):
        if char in last_seen and last_seen[char] >= left:
            left = last_seen[char] + 1
        last_seen[char] = right
        max_len = max(max_len, right - left + 1)

    return max_len
```

> **[Annotation: Proactive Optimization Offer]:** Volunteering the dictionary optimization — and explaining the trade-off precisely ("amortized already O(n), but the dict version avoids the inner loop entirely") — is a strong L5 signal. Note the candidate also correctly adds the `>= left` guard to avoid moving left backwards when a character was last seen before the current window.

**Interviewer:** Great. One last thing — why the `last_seen[char] >= left` guard?

**Candidate:** Good catch to double-check. Consider `"abba"`. When we reach the second `'a'` at index 3, `last_seen['a']` is 0. But our left pointer has already moved to 2 (past the first `'b'`). Without the guard, we'd set `left = 0 + 1 = 1`, which moves it *backwards* — that would incorrectly include `'b'` again. The guard ensures we only jump forward.

> **[Annotation: Handles Follow-Up Correctly]:** When challenged, the candidate doesn't backpedal or guess — they walk through a concrete counterexample (`"abba"`) that directly demonstrates why the guard matters. This is the hallmark of someone who understands, not memorized.

---

## Summary of Strong Signals

- Asked targeted clarifying questions (ASCII range, case sensitivity, empty string) before writing any code
- Named and dismissed the brute-force approach with correct complexity before proposing the optimal solution
- Narrated the algorithm in English before writing code, enabling course-correction
- Used semantically clear variable names throughout
- Traced the provided example step-by-step to verify correctness
- Proactively enumerated three meaningful edge cases and verified each
- Offered an unprompted optimization (set → dict) with a precise explanation of the trade-off
- Correctly handled a follow-up challenge with a concrete counterexample

## What This Answer Would Score

- L3 bar: ✅ Passes (correct solution, handles edge cases)
- L4 bar: ✅ Passes (optimization offered, complexity explained, narrated approach)
- L5 bar: ⚠️ Borderline (needs deeper discussion of production concerns, e.g., Unicode streaming input, or a harder follow-up problem)
