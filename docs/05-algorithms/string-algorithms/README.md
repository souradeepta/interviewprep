---
Level: L5
Time: ~25 min
---

# String Algorithms

## Quick Summary

String matching finds occurrences of a pattern P (length m) inside text T (length n). Naive search is O(nm); KMP, Z-algorithm, and Rabin-Karp all reach O(n+m). Choose based on preprocessing needs, number of patterns, and space constraints.

---

## Comparative Trade-off Table

| Algorithm | Time | Space | Best for | When to use |
|-----------|------|-------|---------|-------------|
| Naive | O(nm) | O(1) | Short patterns, simple code | Never in interviews |
| KMP | O(n+m) | O(m) | Long patterns, no extra space | Pattern matching with preprocessing |
| Z-Algorithm | O(n+m) | O(n) | Finding all occurrences | Competitive programming |
| Rabin-Karp | O(n+m) avg | O(1) | Multiple patterns | Rolling hash, plagiarism detection |
| Suffix Array | O(n log n) | O(n) | Multiple queries on same text | Search engines, bioinformatics |

**Decision rule:**
- Single pattern, fixed text → KMP or Z-algorithm
- Multiple patterns → Rabin-Karp or Aho-Corasick
- Repeated substring questions → KMP failure function property
- Large-scale text search (search engine) → Suffix array

---

## Algorithms

### 1. KMP (Knuth-Morris-Pratt)

**Core idea:** Precompute a failure function `lps[]` (Longest Proper Prefix that is also Suffix) for the pattern. When a mismatch occurs, use `lps` to skip ahead instead of restarting.

**What `lps[i]` stores:** The length of the longest proper prefix of `pattern[0..i]` that is also a suffix. This is NOT the position to go back to — it is a length.

**Time:** O(n+m) | **Space:** O(m)

```python
def compute_lps(pattern: str) -> list[int]:
    m = len(pattern)
    lps = [0] * m
    length = 0  # length of previous longest prefix suffix
    i = 1
    while i < m:
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        else:
            if length != 0:
                # Don't increment i — try the shorter prefix
                length = lps[length - 1]
            else:
                lps[i] = 0
                i += 1
    return lps


def kmp_search(text: str, pattern: str) -> list[int]:
    """Returns list of all start indices where pattern occurs in text."""
    n, m = len(text), len(pattern)
    if m == 0:
        return []
    lps = compute_lps(pattern)
    matches = []
    i = j = 0  # i = text index, j = pattern index
    while i < n:
        if text[i] == pattern[j]:
            i += 1
            j += 1
        if j == m:
            matches.append(i - j)
            j = lps[j - 1]  # use failure function to continue
        elif i < n and text[i] != pattern[j]:
            if j != 0:
                j = lps[j - 1]
            else:
                i += 1
    return matches


# Example
text = "AABAACAADAABAABA"
pattern = "AABA"
print(kmp_search(text, pattern))  # [0, 9, 12]
```

---

### 2. Z-Algorithm

**Core idea:** Build a Z-array where `Z[i]` = length of the longest substring starting at `s[i]` that is also a prefix of `s`. Concatenate `pattern + '$' + text` and look for Z-values equal to `len(pattern)`.

**Time:** O(n+m) | **Space:** O(n+m)

```python
def z_function(s: str) -> list[int]:
    n = len(s)
    z = [0] * n
    z[0] = n
    l = r = 0
    for i in range(1, n):
        if i < r:
            z[i] = min(r - i, z[i - l])
        while i + z[i] < n and s[z[i]] == s[i + z[i]]:
            z[i] += 1
        if i + z[i] > r:
            l, r = i, i + z[i]
    return z


def z_search(text: str, pattern: str) -> list[int]:
    """Returns all start indices where pattern occurs in text."""
    combined = pattern + '$' + text
    z = z_function(combined)
    m = len(pattern)
    return [i - m - 1 for i in range(m + 1, len(combined)) if z[i] == m]


# Example
print(z_search("AABAACAADAABAABA", "AABA"))  # [0, 9, 12]
```

---

### 3. Rabin-Karp (Rolling Hash)

**Core idea:** Hash the pattern and the current window of text. Slide the window one character at a time, updating the hash in O(1). On a hash match, verify with direct comparison to handle collisions.

**Time:** O(n+m) average, O(nm) worst case | **Space:** O(1)

```python
def rabin_karp(text: str, pattern: str) -> list[int]:
    """Rolling hash search. Returns all match start indices."""
    n, m = len(text), len(pattern)
    if m > n:
        return []

    BASE = 26
    MOD = (1 << 31) - 1  # large prime-like modulus
    matches = []

    # Precompute BASE^(m-1) % MOD
    h = pow(BASE, m - 1, MOD)

    # Compute hash of pattern and first window
    pattern_hash = 0
    window_hash = 0
    for i in range(m):
        pattern_hash = (pattern_hash * BASE + ord(pattern[i])) % MOD
        window_hash  = (window_hash  * BASE + ord(text[i]))    % MOD

    for i in range(n - m + 1):
        if window_hash == pattern_hash:
            # Verify to avoid false positives
            if text[i:i + m] == pattern:
                matches.append(i)
        if i < n - m:
            # Roll: remove leftmost char, add next char
            window_hash = (window_hash - ord(text[i]) * h) % MOD
            window_hash = (window_hash * BASE + ord(text[i + m])) % MOD
            window_hash = (window_hash + MOD) % MOD  # keep positive

    return matches


# Example
print(rabin_karp("AABAACAADAABAABA", "AABA"))  # [0, 9, 12]
```

---

## Worked Problems

### Problem 1: Find the Index of the First Occurrence in a String — LC #28

**Section 1 — Understand the problem.**
Given `haystack` and `needle`, return the index of the first occurrence of `needle` in `haystack`, or `-1` if not present.

**Section 2 — Examples.**
```
haystack = "sadbutsad", needle = "sad" → 0
haystack = "leetcode",  needle = "leeto" → -1
```

**Section 3 — Constraints & edge cases.**
- Empty needle → return 0 (Python `str.find` behavior)
- Needle longer than haystack → -1
- 1 ≤ len(haystack), len(needle) ≤ 10^4

**Section 4 — Approach.**
Use KMP. Precompute `lps` for needle, then scan haystack.

**Section 5 — Code.**
```python
def strStr(haystack: str, needle: str) -> int:
    if not needle:
        return 0
    n, m = len(haystack), len(needle)
    lps = compute_lps(needle)
    i = j = 0
    while i < n:
        if haystack[i] == needle[j]:
            i += 1; j += 1
        if j == m:
            return i - j
        elif i < n and haystack[i] != needle[j]:
            j = lps[j - 1] if j else 0
            if j == 0:
                i += 1
    return -1
```

**Section 6 — Complexity.**
Time O(n+m), Space O(m).

---

### Problem 2: Repeated Substring Pattern — LC #459

**Section 1 — Understand the problem.**
Return `True` if string `s` can be constructed by repeating a substring.

**Section 2 — Examples.**
```
"abab"   → True  ("ab" repeated)
"aba"    → False
"abcabc" → True  ("abc" repeated)
```

**Section 3 — Constraints & edge cases.**
- 1 ≤ len(s) ≤ 10^4
- Single character → False

**Section 4 — Approach.**
KMP property: `s` has a repeated substring iff `len(s) % (len(s) - lps[-1]) == 0`. Equivalently, `s` is found in `(s+s)[1:-1]`.

```
lps[-1] = k means the string has a border of length k.
Period = n - k. If n % period == 0, it's a repeated pattern.
```

**Section 5 — Code.**
```python
def repeatedSubstringPattern(s: str) -> bool:
    lps = compute_lps(s)
    n = len(s)
    length = lps[-1]        # longest border
    period = n - length
    return length > 0 and n % period == 0
```

**Section 6 — Complexity.**
Time O(m), Space O(m).

---

### Problem 3: Longest Happy Prefix — LC #1392

**Section 1 — Understand the problem.**
Return the longest prefix of `s` that is also a suffix (but not `s` itself). Return `""` if none.

**Section 2 — Examples.**
```
"level"      → "l"
"ababab"     → "abab"
"leetcodeleet" → "leet"
```

**Section 3 — Constraints & edge cases.**
- 1 ≤ len(s) ≤ 10^5
- Return `""` if no proper prefix-suffix exists

**Section 4 — Approach.**
The KMP failure function directly gives the answer. `lps[-1]` is the length of the longest proper prefix that is also a suffix.

**Section 5 — Code.**
```python
def longestPrefix(s: str) -> str:
    lps = compute_lps(s)
    length = lps[-1]
    return s[:length]
```

**Section 6 — Complexity.**
Time O(m), Space O(m).

---

## Common Mistakes

1. **Misreading `lps[i]`:** It stores a *length*, not an index. `lps[i] = 3` means the first 3 characters equal the last 3 characters of `pattern[0..i]`. When a mismatch happens at `j`, you jump to `j = lps[j-1]`, not `j = lps[j]`.

2. **Rabin-Karp hash collisions:** Always verify with direct string comparison after a hash match. With a single modulus, collision probability is ~m/MOD. Use double hashing in competitive settings.

3. **Rolling hash arithmetic:** After subtraction the hash can go negative in Python too (`(-5) % 7 = 2` in Python but `-5 % 7 = -5` in C++). Always add `+ MOD` before `% MOD` after subtraction for portability.

4. **Z-algorithm separator:** Use a character not in the alphabet (e.g., `'$'`) between pattern and text. Without it, the Z-values from the text portion can bleed into the pattern length.

5. **Off-by-one in KMP loop:** The inner `if j == m` check must come before the `elif` mismatch check, otherwise you try to access `lps[m]` which is out of bounds.

---

## Interview Q&A

**Q1: Why does KMP run in O(n+m) even though there's a while loop inside?**
The pointer `j` can only increase at most `n` times total (once per `i` increment). Each time the inner fallback runs (`j = lps[j-1]`), `j` strictly decreases. So the total number of decrements is bounded by the total increments → amortized O(n) for the text scan plus O(m) for LPS construction.

**Q2: When would you use Rabin-Karp over KMP?**
When searching for multiple patterns simultaneously. You can hash all patterns into a set and check in O(1) per window. Aho-Corasick is better for large sets, but Rabin-Karp is simpler to implement under interview time pressure.

**Q3: What is the "border" of a string?**
A border is a string that is simultaneously a proper prefix and a proper suffix. `lps[i]` gives the length of the longest border of `pattern[0..i]`. Example: `"abacaba"` has border `"aba"` (length 3).

**Q4: How do you handle Unicode or large alphabets in string matching?**
KMP and Z-algorithm work unchanged — they compare characters directly. Rabin-Karp needs to use character ordinals; with large alphabets, pick a larger BASE and MOD to minimize collisions.

**Q5: What is the time complexity of building a suffix array?**
O(n log n) using prefix doubling (SA-IS is O(n) but harder to implement). Answering LCP queries on a suffix array takes O(1) after O(n) preprocessing with a sparse table.

**Q6: When does the naive algorithm beat KMP in practice?**
For very short patterns (m ≤ 4) or when the alphabet is large (low character repetition), the naive algorithm's branch prediction advantage and cache behavior often outperform KMP's indirection through `lps`. The Python `str.find` uses a hybrid Boyer-Moore + Horspool variant for this reason.

**Q7: Explain the Z-algorithm in one sentence.**
`Z[i]` is the length of the longest substring starting at position `i` that matches a prefix of the whole string; we exploit this on `pattern$text` to find all pattern occurrences in O(n+m).

**Q8: How would you find the shortest period of a string?**
The shortest period is `n - lps[n-1]` if `n % (n - lps[n-1]) == 0`, otherwise the period is `n` itself.
