# String Algorithms Mastery: Pattern Matching and Advanced Techniques

Master string manipulation, pattern matching, and advanced string algorithms.

---

## String Matching Algorithms

### KMP (Knuth-Morris-Pratt)

```python
def build_lps(pattern):
    m = len(pattern)
    lps = [0] * m
    j = 0
    
    for i in range(1, m):
        while j > 0 and pattern[i] != pattern[j]:
            j = lps[j - 1]
        if pattern[i] == pattern[j]:
            j += 1
        lps[i] = j
    
    return lps

def kmp_search(text, pattern):
    n = len(text)
    m = len(pattern)
    lps = build_lps(pattern)
    
    matches = []
    j = 0
    
    for i in range(n):
        while j > 0 and text[i] != pattern[j]:
            j = lps[j - 1]
        if text[i] == pattern[j]:
            j += 1
        if j == m:
            matches.append(i - m + 1)
            j = lps[j - 1]
    
    return matches

# Time: O(n + m), Space: O(m)
# Use: Pattern matching in text, find all occurrences
```

### Boyer-Moore

```python
def build_bad_char(pattern):
    bad_char = {}
    for i in range(len(pattern)):
        bad_char[pattern[i]] = i
    return bad_char

def boyer_moore_search(text, pattern):
    n = len(text)
    m = len(pattern)
    bad_char = build_bad_char(pattern)
    
    matches = []
    i = 0
    
    while i <= n - m:
        j = m - 1
        while j >= 0 and text[i + j] == pattern[j]:
            j -= 1
        
        if j < 0:
            matches.append(i)
            i += 1
        else:
            bad_shift = max(1, j - bad_char.get(text[i + j], -1))
            i += bad_shift
    
    return matches

# Time: O(n/m) best, O(nm) worst, Space: O(|Σ|)
# Use: Fast pattern search with small patterns, practical choice
```

### Z-Algorithm

```python
def z_algorithm(s):
    n = len(s)
    z = [0] * n
    z[0] = n
    l, r = 0, 0
    
    for i in range(1, n):
        if i > r:
            l, r = i, i
            while r < n and s[r - l] == s[r]:
                r += 1
            z[i] = r - l
            r -= 1
        else:
            k = i - l
            if z[k] < r - i + 1:
                z[i] = z[k]
            else:
                l = i
                while r < n and s[r - l] == s[r]:
                    r += 1
                z[i] = r - l
                r -= 1
    
    return z

# Time: O(n), Space: O(n)
# Use: Pattern matching, finding all occurrences
```

---

## String Pattern Problems

### Longest Prefix Suffix (LPS) in KMP

```python
# LPS[i] = length of longest proper prefix that is also suffix

# Example: "AABAAB"
# LPS = [0, 1, 0, 1, 2, 2]
#        A A B A A B
#        0 1 0 1 2 2

# "AA": prefix "A" is suffix → LPS[1] = 1
# "AAB": no proper prefix-suffix → LPS[2] = 0
# "AABA": prefix "A" is suffix → LPS[3] = 1
# "AABAA": prefix "AA" is suffix → LPS[4] = 2
# "AABAAB": prefix "AA" is suffix → LPS[5] = 2
```

### Anagram Problems

```python
def are_anagrams(s1, s2):
    return sorted(s1) == sorted(s2)  # O(n log n)

def are_anagrams_fast(s1, s2):
    if len(s1) != len(s2):
        return False
    
    count = {}
    for c in s1:
        count[c] = count.get(c, 0) + 1
    
    for c in s2:
        if c not in count:
            return False
        count[c] -= 1
        if count[c] < 0:
            return False
    
    return all(v == 0 for v in count.values())  # O(n)
```

### Palindrome Problems

```python
def is_palindrome(s):
    return s == s[::-1]

def longest_palindrome_expand(s):
    def expand_around(l, r):
        while l >= 0 and r < len(s) and s[l] == s[r]:
            l -= 1
            r += 1
        return s[l+1:r]
    
    longest = ""
    for i in range(len(s)):
        p1 = expand_around(i, i)  # Odd length
        p2 = expand_around(i, i + 1)  # Even length
        
        if len(p1) > len(longest):
            longest = p1
        if len(p2) > len(longest):
            longest = p2
    
    return longest

# Time: O(n²), Space: O(1) for character expansion
```

---

## Advanced String Algorithms

### Rabin-Karp (Rolling Hash)

```python
def rabin_karp(text, pattern):
    n = len(text)
    m = len(pattern)
    base = 31
    mod = 10**9 + 7
    
    pattern_hash = 0
    text_hash = 0
    power = 1
    
    for i in range(m):
        pattern_hash = (pattern_hash * base + ord(pattern[i])) % mod
        text_hash = (text_hash * base + ord(text[i])) % mod
        if i < m - 1:
            power = (power * base) % mod
    
    matches = []
    for i in range(n - m + 1):
        if pattern_hash == text_hash:
            if text[i:i+m] == pattern:
                matches.append(i)
        
        if i < n - m:
            text_hash = (text_hash - ord(text[i]) * power) % mod
            text_hash = (text_hash * base + ord(text[i + m])) % mod
            text_hash = (text_hash + mod) % mod
    
    return matches

# Time: O(n + m), Space: O(1)
# Use: Multiple pattern matching, find all occurrences
```

### Trie Data Structure

```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False

class Trie:
    def __init__(self):
        self.root = TrieNode()
    
    def insert(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end = True
    
    def search(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                return False
            node = node.children[char]
        return node.is_end
    
    def starts_with(self, prefix):
        node = self.root
        for char in prefix:
            if char not in node.children:
                return False
            node = node.children[char]
        return True

# Time: O(m) per operation where m = word length
# Space: O(N·M·Σ) where N = # words, M = avg length, Σ = alphabet size
# Use: Autocomplete, spell checker, IP routing
```

---

## String Transformation Problems

### Edit Distance (Levenshtein)

```python
def edit_distance(s1, s2):
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i-1] == s2[j-1]:
                dp[i][j] = dp[i-1][j-1]
            else:
                dp[i][j] = 1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])
    
    return dp[m][n]

# Time: O(m·n), Space: O(m·n)
```

### Longest Common Subsequence

```python
def lcs(s1, s2):
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i-1] == s2[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    
    return dp[m][n]

# Time: O(m·n), Space: O(m·n)
```

---

## Common String Problems

| Problem | Algorithm | Time | Notes |
|---------|-----------|------|-------|
| Find pattern | KMP or Z-algo | O(n+m) | Efficient pattern matching |
| Multiple patterns | Aho-Corasick | O(n+m+z) | Find all occurrences |
| Rolling hash | Rabin-Karp | O(n+m) | Good for multiple searches |
| Autocomplete | Trie | O(m) | m = prefix length |
| Spell check | Trie | O(m) | Edit distance nearby |
| Longest palindrome | Expand around | O(n²) | Manacher = O(n) |
| Edit distance | DP | O(m·n) | Sequence alignment |
| LCS | DP | O(m·n) | Common subsequence |

---

## String Mastery Checklist

- ✓ Know when to use each algorithm (weighted by problem)
- ✓ KMP for single pattern efficient matching
- ✓ Trie for prefix-based queries
- ✓ Rolling hash for multiple patterns
- ✓ DP for string transformation (edit distance, LCS)
- ✓ Handle edge cases (empty strings, single char)
- ✓ Palindrome check with expand-around technique
- ✓ Anagram detection with character counts
- ✓ Tested on small examples before submitting

