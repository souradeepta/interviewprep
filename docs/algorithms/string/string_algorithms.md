# String Algorithms

## Overview

String algorithms form a core pillar of SDE interviews. They combine clever preprocessing (failure functions, hash arrays, transformed strings) with linear-time scans to solve problems that naive approaches handle in O(n²) or worse.

**When to use:**
- Substring search (exact match, multiple patterns, approximate match)
- Palindrome detection and enumeration
- Duplicate/repeated substring detection
- Anagram / permutation detection in a stream
- Data compression (run-length encoding, LZ-family)
- String comparison and equality checks in O(1) after preprocessing

---

## Algorithms

### 1. KMP — Knuth-Morris-Pratt

**Core idea:** Preprocess the pattern into a *failure function* (prefix function) that, on a mismatch, tells us the farthest we can shift without missing a match. The text pointer never moves backward.

#### Failure Function Construction

```
pattern = "A B A B C A B A B"
index  =   0 1 2 3 4 5 6 7 8

i=1: B != A, length=0    → failure[1] = 0
i=2: A == A, length=1    → failure[2] = 1
i=3: B == B, length=2    → failure[3] = 2
i=4: C != A, fall back to failure[1]=0 → C != A → failure[4] = 0
i=5: A == A, length=1    → failure[5] = 1
i=6: B == B, length=2    → failure[6] = 2
i=7: A == A, length=3    → failure[7] = 3
i=8: B == B, length=4    → failure[8] = 4

failure = [0, 0, 1, 2, 0, 1, 2, 3, 4]
```

#### KMP Search Step-by-Step

```
text    = "A B A B D A B A C D A B A B C A B A B"
pattern = "A B A B C A B A B"
failure = [0, 0, 1, 2, 0, 1, 2, 3, 4]

i=0..3: A=A B=B A=A B=B  → j advances to 4
i=4: text[4]=D vs pattern[4]=C  → MISMATCH at j=4
       fall back: j = failure[3] = 2
       text[4]=D vs pattern[2]=A → MISMATCH at j=2
       fall back: j = failure[1] = 0
       text[4]=D vs pattern[0]=A → MISMATCH at j=0 → advance i

i=5..9: A=A B=B A=A B=B C=C  → j advances to 5
       (continuing...)
i=10..14: text[10..14] matches pattern[5..9]=ABAB... wait j restarts at
       failure[4]=0... pattern realigns...

... eventually at i=10, j=0:
i=10..18: A B A B C A B A B → FULL MATCH at start=10
          j = failure[8] = 4  (continue for overlapping)

Result: match at index 10
```

---

### 2. Rabin-Karp — Rolling Hash

**Core idea:** Hash the pattern once, then slide a same-length window over the text. Each slide recomputes the hash in O(1) by removing the leading character's contribution and adding the new trailing character.

#### Rolling Hash Computation

```
text    = "G E E K S   F O R   G E E K S"
pattern = "G E E K S"   (m=5)

BASE = 256, MOD = 2147483647

h = BASE^(m-1) mod MOD   (coefficient of leading char)

Initial window: "GEEKS"
  hash = G*256^4 + E*256^3 + E*256^2 + K*256 + S

Slide: remove 'G', add ' '
  new_hash = (BASE * (old_hash - G * h) + ' ') mod MOD
             ↑ O(1) — no loop needed

When window_hash == pattern_hash:
  → verify character-by-character (guard against collision)

Window:  G E E K S     hash match → verify → MATCH at i=0
         E E K S ' '   no match
         E K S ' ' F   no match
         ...
         G E E K S     hash match → verify → MATCH at i=10
```

---

### 3. Z-Algorithm

**Core idea:** Build the Z-array of the concatenated string `S = pattern + '$' + text`. `Z[i]` = length of the longest prefix of S that matches S[i..]. A Z-value equal to `|pattern|` signals a full match.

#### Z-Array Construction

```
S = "A A B $ A A B X A A B"
     0 1 2 3 4 5 6 7 8 9 10

i=1: expand: A==A → Z[1]=2  (AA matches prefix AA...)
             B!=$  stop  →  Z[1]=2, set box L=1,R=3
i=2: expand: B!=$  stop  →  Z[2]=0
i=3: '$'  always 0         →  Z[3]=0
i=4: i<R? No. expand: A==A B==A? No wait: S[4]=A,S[0]=A → match
         A==A,A==A,B==B → Z[4]=3, update L=4,R=7
i=5: i<R=7, mirror=i-L=1, Z[mirror]=2, min(R-i,Z[1])=min(2,2)=2
     expand from Z[5]=2: S[7]=X vs S[2]=B → stop → Z[5]=2
i=6: i<R=7, mirror=2, Z[2]=0, min(1,0)=0
     expand: S[6]=B vs S[0]=A → stop → Z[6]=0
i=7: i>=R. expand: S[7]=X vs S[0]=A → stop → Z[7]=0
i=8: expand: A=A,A=A,B=B → Z[8]=3, update L=8,R=11
i=9: i<R=11, mirror=i-L=1, Z[1]=2, min(2,2)=2
     expand from 2: S[11] out of bounds → Z[9]=2
i=10: mirror=2, Z[2]=0, min(1,0)=0 → expand → B!=A → Z[10]=0

Z = [0, 2, 0, 0, 3, 2, 0, 0, 3, 2, 0]

Z[4]=3 == |pattern|=3 → match at text index 4-(3+1)=0
Z[8]=3 == |pattern|=3 → match at text index 8-(3+1)=4
```

---

### 4. Manacher's Algorithm

**Core idea:** Insert `#` separators to unify odd/even palindromes. Maintain a right-boundary `R` and its center `C`. If position `i` is inside `[C - R, R]`, initialise its palindrome radius from the mirror position, avoiding redundant expansions.

#### '#' Transform and Radius Array

```
Original: "a b b a"
          0 1 2 3

Transformed T: "# a # b # b # a #"
               0 1 2 3 4 5 6 7 8

Compute p[i] = palindrome radius at i:
  i=0: '#', no expansion    → p[0]=0
  i=1: 'a', expand: T[0]='#'!=T[2]='#'? yes match, T[-1] OOB stop → p[1]=0
       Actually: expand T[0]='#' vs T[2]='#' → match,
                 T[-1] OOB → stop   → p[1]=1  [palindrome "#a#"]
  i=2: '#', mirror of center; expand T[1]='a' vs T[3]='b' → no → p[2]=0
  i=3: 'b', expand T[2]='#' vs T[4]='#' → match
            T[1]='a' vs T[5]='b' → no → p[3]=1  [palindrome "#b#"]
  i=4: '#', inside right boundary of i=3's palindrome?
       R=3+1=4, i=4 not < R. Expand:
       T[3]='b' vs T[5]='b' → match
       T[2]='#' vs T[6]='#' → match
       T[1]='a' vs T[7]='a' → match
       T[0]='#' vs T[8]='#' → match
       T[-1] OOB → stop → p[4]=4  ← new max, update C=4, R=8
  i=5: mirror of i=3: p[mirror]=1, R-i=8-5=3, min=1
       expand from 1: T[3]='b' vs T[7]='a' → no → p[5]=1
  i=6,7,8: similarly computed...

p = [0, 1, 0, 1, 4, 1, 0, 1, 0]
         ↑ max is p[4]=4 at center 4

start in original = (4 - 4) / 2 = 0,  length = 4 → "abba" ✓
```

---

### 5. String Hashing — Polynomial Rolling Hash

**Core idea:** Precompute prefix hashes so any substring hash can be retrieved in O(1):

```
prefix[i] = s[0]*BASE^(i-1) + s[1]*BASE^(i-2) + ... + s[i-1]

hash(l, r) = prefix[r+1] - prefix[l] * BASE^(r-l+1)   (mod MOD)
```

#### Prefix Hash Table

```
s = "a b c a b c"
     0 1 2 3 4 5

prefix[0] = 0
prefix[1] = ord('a') * BASE^0                = 97
prefix[2] = ord('a') * BASE^1 + ord('b')     = 97*131 + 98  = 12805
prefix[3] = ... (builds up)

Query hash(3,5) — substring "abc" starting at index 3:
  = prefix[6] - prefix[3] * BASE^3  (mod MOD)
  = same value as hash(0,2) — substring "abc" at index 0
  → they are equal  ✓

Double hashing: compute (h1, h2) with two independent (BASE, MOD) pairs.
Collision probability drops from ~1/MOD to ~1/(MOD1 * MOD2) ≈ 10^{-18}.
```

---

### 6. Anagram Detection — Sliding Window

**Core idea:** Maintain two frequency arrays (pattern and window) and a `matches` counter that tracks how many of the 26 character slots have equal counts. Slide the window: each step updates at most 2 entries and adjusts `matches` by at most ±2.

#### Sliding Window Trace

```
text    = "c b a e b a b a c d"
pattern = "a b c"
pFreq   = {a:1, b:1, c:1}

Initial window "cba" (i=0..2):
  wFreq = {c:1, b:1, a:1}
  matches = 26  (all 26 slots match)  → ANAGRAM at index 0

Slide: remove text[0]='c', add text[3]='e'
  remove 'c': wFreq[c] 1→0, was equal(1==1) now under → matches-- → 25
  add    'e': wFreq[e] 0→1, was 0!=1(pFreq[e]=0) now over → matches-- → 24
  matches=24 ≠ 26 → no anagram at index 1

Slide: remove text[1]='b', add text[4]='b'
  remove 'b': wFreq[b] 1→0, equal→under → matches-- → 23
  add    'b': wFreq[b] 0→1, under→equal → matches++ → 24
  matches=24 → no anagram at index 2

... (continuing)

Eventually at index 6, window="aba":
  But pFreq={a:1,b:1,c:1}, wFreq={a:2,b:1} → not 26 matches

At index 6, window "bac":
  wFreq={b:1,a:1,c:1} → matches=26 → ANAGRAM at index 6

Result: [0, 6]
```

---

### 7. Longest Common Substring — DP

**Core idea:** `dp[i][j]` = length of the longest common substring *ending* at `s1[i-1]` and `s2[j-1]`. Characters must be contiguous (unlike LCS subsequence).

#### DP Table Trace

```
s1 = "a b c d e f"
s2 = "b c d f g h"

     ""  b  c  d  f  g  h
  ""  0   0  0  0  0  0  0
  a   0   0  0  0  0  0  0
  b   0   1  0  0  0  0  0
  c   0   0  2  0  0  0  0
  d   0   0  0  3  0  0  0   ← dp[4][4]=3 = "bcd" (max so far)
  e   0   0  0  0  0  0  0   ← chain broken
  f   0   0  0  0  1  0  0

max_len = 3, end at s1[4] → LCS = s1[1..3] = "bcd"

Recurrence:
  dp[i][j] = dp[i-1][j-1] + 1   if s1[i-1] == s2[j-1]
              0                   otherwise
```

---

### 8. Run-Length Encoding / Decoding

**Core idea:** Scan left to right, counting consecutive identical characters. Emit the character followed by its count (omit count when 1 to save space).

#### Encoding Trace

```
Input:  A A A B B B C C D D D D E E
        ─────── ─────── ─── ───────── ───

Run 1: 'A' × 3  → "A3"
Run 2: 'B' × 3  → "B3"
Run 3: 'C' × 2  → "C2"
Run 4: 'D' × 4  → "D4"
Run 5: 'E' × 2  → "E2"

Encoded: "A3B3C2D4E2"

Decoding "A3B3C2D4E2":
  Read 'A', digits='3' → "AAA"
  Read 'B', digits='3' → "BBB"
  Read 'C', digits='2' → "CC"
  Read 'D', digits='4' → "DDDD"
  Read 'E', digits='2' → "EE"

Decoded: "AAABBBCCDDDDEE"  ✓

Edge case — no repetition:
  "ABCD" → "ABCD"  (no count emitted for runs of 1)

Edge case — multi-digit count:
  "AAAAAAAAAAAA" (12 A's) → "A12"
  Decode: read 'A', digits='1','2' → count=12 → "AAAAAAAAAAAA"  ✓
```

---

## Complexity Table

| Algorithm                 | Time           | Space    | Notes                              |
|---------------------------|:--------------:|:--------:|------------------------------------|
| KMP Search                | O(n + m)       | O(m)     | failure function preprocessing     |
| Rabin-Karp (single)       | O(n + m) avg   | O(1)     | O(nm) worst case (all collisions)  |
| Rabin-Karp (multi, k pats)| O(n·L + Σm)    | O(k)     | L = number of unique lengths       |
| Z-Algorithm               | O(n + m)       | O(n + m) | concatenated string + Z-array      |
| Manacher's                | O(n)           | O(n)     | '#' transform trick                |
| String Hashing (preproc)  | O(n)           | O(n)     | then O(1) per query                |
| Anagram Detection         | O(n)           | O(1)     | fixed 26-element arrays            |
| Longest Common Substring  | O(n × m)       | O(n × m) | space → O(min(n,m)) with rolling   |
| Run-Length Encode         | O(n)           | O(n)     |                                    |
| Run-Length Decode         | O(n)           | O(n)     | multi-digit counts supported       |

---

## When to Use

| Situation                                          | Algorithm                            |
|----------------------------------------------------|--------------------------------------|
| Single exact pattern in long text                  | KMP or Z-Algorithm                   |
| Multiple patterns at once                          | Rabin-Karp multi or Aho-Corasick     |
| Longest palindromic substring                      | Manacher's                           |
| Substring equality in O(1) after preprocessing    | String Hashing                       |
| All anagram positions                              | Sliding window frequency map         |
| Longest shared contiguous substring               | DP (LCS substring)                   |
| Compress data with long repeated runs              | Run-Length Encoding                  |
| Detect repeated substrings of fixed length         | Rabin-Karp + hash set                |

---

## Common Interview Questions

| Problem                                                  | Algorithm / Pattern                   |
|----------------------------------------------------------|---------------------------------------|
| Find the Index of the First Occurrence (LC 28)          | KMP                                   |
| Repeated DNA Sequences (LC 187)                          | Rabin-Karp rolling hash               |
| Longest Palindromic Substring (LC 5)                     | Manacher's / expand-around-centre     |
| Find All Anagrams in a String (LC 438)                   | Sliding window + frequency map        |
| Permutation in String (LC 567)                           | Sliding window + frequency map        |
| Longest Common Prefix (LC 14)                            | Trie or vertical scan                 |
| Minimum Window Substring (LC 76)                         | Sliding window + two pointers         |
| String Compression (LC 443)                              | Run-length encoding (in-place)        |
| Longest Repeating Character Replacement (LC 424)         | Sliding window                        |
| Shortest Palindrome (LC 214)                             | KMP failure function on reverse       |
| Count Distinct Substrings                                | Suffix array or rolling hash set      |
| Maximum XOR of Two Numbers (LC 421)                      | Binary Trie                           |

---

## Key Invariants & Tricks

### KMP Failure Function
- `failure[i]` = length of longest **proper** prefix of `pattern[0..i]` that is also a suffix.
- On mismatch at `j`, set `j = failure[j-1]` — do **not** reset `j` to 0 unless `j == 0`.
- The text pointer `i` never decreases — O(n) total across the entire search.

### Rabin-Karp Rolling Hash
- Precompute `h = BASE^(m-1) mod MOD` before the slide loop.
- After subtraction, always add MOD before taking `%` to avoid negative values.
- Collision = hash match but string mismatch — always verify with `==` on hash match.
- Double hashing (`(h1, h2)` pair) reduces collision probability to ~1/(MOD1 × MOD2).

### Z-Algorithm
- `Z[0]` is conventionally 0 (the whole string trivially matches itself).
- The sentinel character `'$'` must not appear in text or pattern.
- Z-box `[L, R]`: before expanding at `i`, initialise `Z[i] = min(R - i, Z[i - L])`.

### Manacher's
- Transformed string length: `2n + 1` (n chars + n+1 `#`s).
- `p[i]` in the transformed string = palindrome length in original.
- Start index in original: `(centerIdx - maxLen) / 2`.
- Mirror position of `i` w.r.t. center `C`: `mirror = 2*C - i`.

### String Hashing
- Use two independent `(BASE, MOD)` pairs to reduce collision risk.
- Subtraction in modular arithmetic: always `% MOD` after adding MOD (`(a - b % MOD + MOD) % MOD`).
- For adversarial inputs, use a random BASE chosen at runtime.

### Anagram Sliding Window
- Track a `matches` integer (count of chars with equal frequency in both arrays).
- On adding a right char: if new freq equals pattern freq → `matches++`, if one over → `matches--`.
- On removing a left char: if new freq equals pattern freq → `matches++`, if one under → `matches--`.
- Window is an anagram iff `matches == 26`.

---

## Python Quick Reference

```python
# ── KMP in 10 lines ───────────────────────────────────────────────────────────
def kmp(text, pattern):
    fail = [0] * len(pattern)
    j = 0
    for i in range(1, len(pattern)):
        while j and pattern[i] != pattern[j]: j = fail[j-1]
        if pattern[i] == pattern[j]: j += 1
        fail[i] = j
    j = 0
    out = []
    for i, c in enumerate(text):
        while j and c != pattern[j]: j = fail[j-1]
        if c == pattern[j]: j += 1
        if j == len(pattern): out.append(i - j + 1); j = fail[j-1]
    return out

# ── Manacher one-liner style ─────────────────────────────────────────────────
def longest_palindrome(s):
    t = '#' + '#'.join(s) + '#'
    p, c, r = [0]*len(t), 0, 0
    for i in range(len(t)):
        if i < r: p[i] = min(r - i, p[2*c - i])
        while i-p[i]-1 >= 0 and i+p[i]+1 < len(t) and t[i-p[i]-1] == t[i+p[i]+1]:
            p[i] += 1
        if i + p[i] > r: c, r = i, i + p[i]
    ml = max(p); ci = p.index(ml)
    return s[(ci - ml)//2:(ci + ml)//2]

# ── Sliding window anagrams ───────────────────────────────────────────────────
from collections import Counter
def find_anagrams(s, p):
    pc, wc = Counter(p), Counter(s[:len(p)])
    res = [0] if pc == wc else []
    for i in range(len(p), len(s)):
        wc[s[i]] += 1
        wc[s[i-len(p)]] -= 1
        if wc[s[i-len(p)]] == 0: del wc[s[i-len(p)]]
        if wc == pc: res.append(i - len(p) + 1)
    return res
```

---

## Java Quick Reference

```java
// ── KMP ───────────────────────────────────────────────────────────────────────
int[] fail = new int[m];
for (int i = 1, j = 0; i < m; i++) {
    while (j > 0 && pattern.charAt(i) != pattern.charAt(j)) j = fail[j-1];
    if (pattern.charAt(i) == pattern.charAt(j)) fail[i] = ++j;
}
List<Integer> matches = new ArrayList<>();
for (int i = 0, j = 0; i < n; i++) {
    while (j > 0 && text.charAt(i) != pattern.charAt(j)) j = fail[j-1];
    if (text.charAt(i) == pattern.charAt(j)) j++;
    if (j == m) { matches.add(i - m + 1); j = fail[j-1]; }
}

// ── Manacher ─────────────────────────────────────────────────────────────────
// (see StringAlgorithms.java for full implementation)

// ── Sliding window anagram ────────────────────────────────────────────────────
int[] p = new int[26], w = new int[26];
for (char c : pattern.toCharArray()) p[c-'a']++;
for (int i = 0; i < m; i++)         w[text.charAt(i)-'a']++;
// compare arrays each step — or use the matches-counter trick shown in StringAlgorithms.java
```
