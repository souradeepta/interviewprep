"""
string_algorithms.py — Complete string algorithm implementations for SDE interview prep.

Algorithms included:
    1. kmp_search              — O(n+m), Knuth-Morris-Pratt pattern matching
    2. rabin_karp_search       — O(n+m) avg, rolling hash pattern matching
    3. rabin_karp_multi        — O(n+m) avg, multiple pattern search
    4. z_algorithm             — O(n+m), Z-array based pattern matching
    5. manacher                — O(n), longest palindromic substring
    6. string_hash             — O(n) preprocessing, O(1) substring hash queries
    7. find_anagrams           — O(n), sliding window anagram detection
    8. longest_common_substring — O(nm), DP longest common substring
    9. run_length_encode       — O(n), run-length encoding
   10. run_length_decode       — O(n), run-length decoding

All functions operate on standard Python str objects (Unicode safe for most
algorithms; note that KMP/Rabin-Karp/Z work on any hashable sequence).

Usage:
    python string_algorithms.py    # runs the full demo block
"""

from typing import List, Tuple


# ---------------------------------------------------------------------------
# 1. KMP (Knuth-Morris-Pratt) Pattern Matching
# ---------------------------------------------------------------------------

def _build_failure_function(pattern: str) -> List[int]:
    """
    Build the KMP failure function (partial match / prefix function).

    failure[i] = length of the longest proper prefix of pattern[0..i]
                 that is also a suffix of pattern[0..i].

    Used internally by kmp_search.

    Time Complexity : O(m)  where m = len(pattern)
    Space Complexity: O(m)

    Example:
        pattern = "ABABCABAB"
        failure = [0, 0, 1, 2, 0, 1, 2, 3, 4]
    """
    m = len(pattern)
    failure = [0] * m
    length = 0   # length of previous longest prefix-suffix
    i = 1

    while i < m:
        if pattern[i] == pattern[length]:
            length += 1
            failure[i] = length
            i += 1
        else:
            if length != 0:
                length = failure[length - 1]   # fall back (don't increment i)
            else:
                failure[i] = 0
                i += 1

    return failure


def kmp_search(text: str, pattern: str) -> List[int]:
    """
    KMP (Knuth-Morris-Pratt) Pattern Matching.

    Finds all (non-overlapping by default) starting indices where `pattern`
    appears in `text` by preprocessing the pattern into a failure function
    that avoids redundant character comparisons.

    Key insight: after a mismatch at pattern[j], we don't restart from
    pattern[0]. Instead we fall back to pattern[failure[j-1]], preserving
    the longest prefix that is still a valid suffix of the matched portion.

    Time Complexity:
        Preprocessing: O(m) — build failure function
        Searching     : O(n) — each character of text processed at most twice
        Total         : O(n + m)

    Space Complexity: O(m) — failure function array

    Args:
        text   : The string to search within.
        pattern: The pattern to find.

    Returns:
        Sorted list of starting indices (0-based) where pattern occurs in text.
        Returns [] if pattern is empty or not found.

    Example:
        kmp_search("ABABDABACDABABCABAB", "ABABCABAB") → [10]
        kmp_search("AAAAAA", "AA") → [0, 1, 2, 3, 4]  (overlapping)

    Interview Notes:
        - The failure function encodes the "self-similarity" of the pattern.
        - Never backtracks in the text — i (text pointer) only moves forward.
        - LeetCode 28 (Find the Index of the First Occurrence in a String) is
          the canonical problem.
        - When pattern length > text length: return [] immediately (O(1)).
    """
    if not pattern or not text:
        return []

    n, m = len(text), len(pattern)
    if m > n:
        return []

    failure = _build_failure_function(pattern)
    matches: List[int] = []

    i = 0   # index into text
    j = 0   # index into pattern

    while i < n:
        if text[i] == pattern[j]:
            i += 1
            j += 1
        if j == m:
            matches.append(i - j)   # found a match ending at i-1
            j = failure[j - 1]       # look for next match (overlapping allowed)
        elif i < n and text[i] != pattern[j]:
            if j != 0:
                j = failure[j - 1]   # fall back using failure function
            else:
                i += 1               # no fallback possible; advance text

    return matches


# ---------------------------------------------------------------------------
# 2. Rabin-Karp Pattern Matching (single pattern)
# ---------------------------------------------------------------------------

_RK_BASE  = 256   # number of characters (ASCII)
_RK_MOD   = (1 << 31) - 1   # large Mersenne prime (2^31 - 1)


def rabin_karp_search(text: str, pattern: str) -> List[int]:
    """
    Rabin-Karp Rolling Hash Pattern Matching.

    Computes a hash of the pattern and slides a same-length window over the
    text, recomputing the hash in O(1) per step using a rolling technique:

        new_hash = (old_hash - text[i] * base^(m-1)) * base + text[i+m]

    Only when hashes match do we verify character-by-character (to handle
    hash collisions), making the average case O(n+m).

    Time Complexity:
        Average: O(n + m)   — few spurious hash collisions
        Worst  : O(n * m)   — all hashes match (e.g., "aaa..." + pattern "aa")

    Space Complexity: O(1)  — no extra arrays beyond loop variables

    Args:
        text   : The string to search within.
        pattern: The pattern to find.

    Returns:
        Sorted list of starting indices where pattern occurs in text.

    Example:
        rabin_karp_search("GEEKS FOR GEEKS", "GEEKS") → [0, 10]

    Interview Notes:
        - Rabin-Karp's real power is multi-pattern search — compute all pattern
          hashes into a set, then a single O(n) pass checks all at once.
        - Two hashes (double hashing) reduce collision probability to ~1/MOD².
        - The leading coefficient removal uses modular arithmetic:
              h = pow(BASE, m-1, MOD)  precomputed before the slide loop.
        - LeetCode 187 (Repeated DNA Sequences) is a classic rolling hash problem.
    """
    if not pattern or not text:
        return []

    n, m = len(text), len(pattern)
    if m > n:
        return []

    # h = BASE^(m-1) mod MOD  — the coefficient of the leading character
    h = pow(_RK_BASE, m - 1, _RK_MOD)

    pattern_hash = 0
    window_hash  = 0

    # Compute initial hashes for pattern and first window
    for i in range(m):
        pattern_hash = (pattern_hash * _RK_BASE + ord(pattern[i])) % _RK_MOD
        window_hash  = (window_hash  * _RK_BASE + ord(text[i]))    % _RK_MOD

    matches: List[int] = []

    for i in range(n - m + 1):
        if window_hash == pattern_hash:
            # Hash match: verify character by character to rule out collisions
            if text[i:i + m] == pattern:
                matches.append(i)

        # Roll the window: remove leading char, add trailing char
        if i < n - m:
            window_hash = (
                (_RK_BASE * (window_hash - ord(text[i]) * h) + ord(text[i + m]))
                % _RK_MOD
            )
            if window_hash < 0:
                window_hash += _RK_MOD

    return matches


# ---------------------------------------------------------------------------
# 3. Rabin-Karp Multi-Pattern Search
# ---------------------------------------------------------------------------

def rabin_karp_multi(text: str, patterns: List[str]) -> dict:
    """
    Rabin-Karp Multi-Pattern Search.

    Hashes all patterns of the same length into a set, then slides a single
    window over the text. This lets us search for k patterns in O(n + total_m)
    time instead of O(k * (n + m)).

    Limitation of this simple version: handles only same-length patterns.
    For mixed lengths, run one pass per unique pattern length.

    Time Complexity:
        Preprocessing: O(sum of pattern lengths)
        Searching     : O(n * L) where L is number of unique pattern lengths
        Per-length    : O(n + m) average

    Space Complexity: O(k) for the hash set of k patterns

    Args:
        text    : The string to search within.
        patterns: List of patterns to find (may have mixed lengths).

    Returns:
        Dict mapping each pattern to its list of start indices in text.

    Example:
        rabin_karp_multi("abcabcabc", ["abc", "cab"])
        → {"abc": [0, 3, 6], "cab": [2, 5]}
    """
    if not text or not patterns:
        return {}

    result = {p: [] for p in patterns}

    # Group patterns by length to enable single-pass per length
    from collections import defaultdict
    by_length: dict = defaultdict(list)
    for p in patterns:
        if p:
            by_length[len(p)].append(p)

    for m, group in by_length.items():
        # Build hash → pattern mapping; collisions stored as list
        pattern_hashes: dict = defaultdict(list)
        for p in group:
            ph = 0
            for ch in p:
                ph = (ph * _RK_BASE + ord(ch)) % _RK_MOD
            pattern_hashes[ph].append(p)

        h = pow(_RK_BASE, m - 1, _RK_MOD)
        window_hash = 0
        n = len(text)

        for i in range(m):
            window_hash = (window_hash * _RK_BASE + ord(text[i])) % _RK_MOD

        for i in range(n - m + 1):
            if window_hash in pattern_hashes:
                window = text[i:i + m]
                for p in pattern_hashes[window_hash]:
                    if window == p:
                        result[p].append(i)
            if i < n - m:
                window_hash = (
                    (_RK_BASE * (window_hash - ord(text[i]) * h) + ord(text[i + m]))
                    % _RK_MOD
                )
                if window_hash < 0:
                    window_hash += _RK_MOD

    return result


# ---------------------------------------------------------------------------
# 4. Z-Algorithm
# ---------------------------------------------------------------------------

def z_algorithm(text: str, pattern: str) -> List[int]:
    """
    Z-Algorithm Pattern Matching.

    Constructs the Z-array of the concatenated string S = pattern + '$' + text
    where Z[i] = length of the longest substring starting at S[i] that is
    also a prefix of S. Positions where Z[i] == m indicate a full match.

    The '$' separator ensures no Z-value crosses the boundary between pattern
    and text (assuming '$' does not appear in either; any sentinel not in the
    alphabet works).

    Time Complexity : O(n + m) — single linear pass to build Z-array
    Space Complexity: O(n + m) — the concatenated string and Z-array

    Args:
        text   : The string to search within.
        pattern: The pattern to find.

    Returns:
        Sorted list of starting indices in `text` where pattern occurs.

    Example:
        z_algorithm("aabxaaabxaaabxacb", "aabx") → [0, 5, 10]

    Interview Notes:
        - Z-array is also useful for: finding the shortest period of a string,
          counting distinct substrings (with suffix arrays), and string compression.
        - The Z-box [L, R] tracks the rightmost matching window and avoids
          redundant comparisons — the key to achieving O(n) time.
        - Z[0] is undefined (the whole string matches itself); conventionally 0.
    """
    if not pattern or not text:
        return []

    m = len(pattern)
    concat = pattern + '$' + text
    n_c = len(concat)

    # Build Z-array
    z = [0] * n_c
    l_box, r_box = 0, 0

    for i in range(1, n_c):
        if i < r_box:
            z[i] = min(r_box - i, z[i - l_box])

        while i + z[i] < n_c and concat[z[i]] == concat[i + z[i]]:
            z[i] += 1

        if i + z[i] > r_box:
            l_box, r_box = i, i + z[i]

    # Collect matches: z[i] == m means full pattern match at position i-(m+1) in text
    offset = m + 1   # length of "pattern + '$'"
    return [i - offset for i in range(offset, n_c) if z[i] == m]


# ---------------------------------------------------------------------------
# 5. Manacher's Algorithm — Longest Palindromic Substring
# ---------------------------------------------------------------------------

def manacher(s: str) -> str:
    """
    Manacher's Algorithm — Longest Palindromic Substring in O(n).

    Transforms the string to handle even-length palindromes uniformly by
    inserting '#' separators:
        "abba" → "#a#b#b#a#"
    Then computes p[i] = radius of the palindrome centred at position i in
    the transformed string.

    The centre-expansion is amortised O(n) using a "right boundary" trick:
    if the current position is inside a known palindrome, we can initialise
    its radius from the mirror position and avoid redundant comparisons.

    Time Complexity : O(n) — each character is expanded at most once total
    Space Complexity: O(n) — transformed string and radius array

    Args:
        s: Input string (may be empty).

    Returns:
        The longest palindromic substring of `s`.
        If multiple palindromes of the same maximum length exist, returns
        the first (leftmost) one.

    Example:
        manacher("babad")   → "bab"  (or "aba"; leftmost returned)
        manacher("cbbd")    → "bb"
        manacher("racecar") → "racecar"

    Interview Notes:
        - LeetCode 5. Classic O(n) solution that trips many candidates.
        - The naive expand-around-centre is O(n²); Manacher adds the right-
          boundary mirror trick for O(n).
        - Even vs odd palindromes: the '#' transform unifies both cases.
        - p[i] in the transformed string corresponds to a palindrome of length
          p[i] in the original (the '#'s are not counted).
    """
    if not s:
        return ""

    # Transform: "abc" → "#a#b#c#"
    t = '#' + '#'.join(s) + '#'
    n = len(t)
    p = [0] * n          # p[i] = palindrome radius at i in transformed string
    center = right = 0   # rightmost palindrome: (center, right boundary)

    for i in range(n):
        mirror = 2 * center - i   # mirror of i w.r.t. current center

        if i < right:
            p[i] = min(right - i, p[mirror])

        # Expand around i
        left_i, right_i = i - (p[i] + 1), i + (p[i] + 1)
        while left_i >= 0 and right_i < n and t[left_i] == t[right_i]:
            p[i] += 1
            left_i -= 1
            right_i += 1

        # Update rightmost boundary
        if i + p[i] > right:
            center, right = i, i + p[i]

    # Find the maximum palindrome radius and map back to original string
    max_len = max(p)
    center_idx = p.index(max_len)

    # In the original string, start = (center_idx - max_len) // 2
    start = (center_idx - max_len) // 2
    return s[start: start + max_len]


# ---------------------------------------------------------------------------
# 6. String Hashing — Polynomial Rolling Hash
# ---------------------------------------------------------------------------

class StringHasher:
    """
    Polynomial Rolling Hash with prefix sums for O(1) substring hash queries.

    Computes hash[i] = s[0]*BASE^(i-1) + s[1]*BASE^(i-2) + ... + s[i-1]
    so that the hash of any substring s[l..r] can be retrieved in O(1) using
    the formula:

        hash(l, r) = (prefix[r+1] - prefix[l] * pow[r-l+1]) % MOD

    Two independent hash bases/mods are used (double hashing) to dramatically
    reduce collision probability to ~1/(MOD1 * MOD2).

    Time Complexity:
        Preprocessing: O(n)
        Query hash(l, r): O(1)
        Compare two substrings: O(1) with hashing vs O(m) naively

    Space Complexity: O(n) — prefix hash array and power array

    Typical use:
        - Substring equality checks in O(1) (e.g., for rolling comparisons)
        - Finding duplicate substrings
        - Comparing rotations
        - As a building block for suffix array construction

    Interview Notes:
        - Double hashing (two independent (base, mod) pairs) reduces collision
          probability from ~1/MOD to ~1/(MOD^2) ≈ 10^{-18} for MOD ~ 10^9.
        - Choosing a prime MOD and a random BASE further reduces adversarial
          collision attacks (Codeforces hack-resistant hashing).
        - Beware modular arithmetic subtraction: always add MOD before taking %.
    """

    _BASE1 = 131
    _MOD1  = (1 << 61) - 1   # Mersenne prime: 2^61 - 1
    _BASE2 = 137
    _MOD2  = (1 << 31) - 1   # Mersenne prime: 2^31 - 1

    def __init__(self, s: str) -> None:
        """
        Precompute prefix hashes and powers for string `s`.

        Args:
            s: The string to hash (supports any characters).
        """
        n = len(s)
        self._n = n

        # Prefix hash arrays (1-indexed: prefix[0] = 0)
        self._prefix1 = [0] * (n + 1)
        self._prefix2 = [0] * (n + 1)
        self._pow1    = [1] * (n + 1)
        self._pow2    = [1] * (n + 1)

        for i in range(n):
            c = ord(s[i])
            self._prefix1[i + 1] = (self._prefix1[i] * self._BASE1 + c) % self._MOD1
            self._prefix2[i + 1] = (self._prefix2[i] * self._BASE2 + c) % self._MOD2
            self._pow1[i + 1]    = (self._pow1[i]    * self._BASE1)      % self._MOD1
            self._pow2[i + 1]    = (self._pow2[i]    * self._BASE2)      % self._MOD2

    def query(self, l: int, r: int) -> Tuple[int, int]:
        """
        Return the double hash of s[l..r] (inclusive, 0-indexed) as (h1, h2).

        Args:
            l: Left index (inclusive).
            r: Right index (inclusive).

        Returns:
            (hash1, hash2) tuple uniquely identifying the substring with very
            high probability.

        Time Complexity: O(1)
        """
        length = r - l + 1
        h1 = (self._prefix1[r + 1] - self._prefix1[l] * self._pow1[length]) % self._MOD1
        h2 = (self._prefix2[r + 1] - self._prefix2[l] * self._pow2[length]) % self._MOD2
        return (h1 % self._MOD1, h2 % self._MOD2)

    def equal(self, l1: int, r1: int, l2: int, r2: int) -> bool:
        """
        Check whether s[l1..r1] == s[l2..r2] in O(1).

        Args:
            l1, r1: Range of first substring (0-indexed, inclusive).
            l2, r2: Range of second substring (0-indexed, inclusive).

        Returns:
            True if the two substrings are identical (with high probability).
        """
        if (r1 - l1) != (r2 - l2):
            return False
        return self.query(l1, r1) == self.query(l2, r2)


def find_duplicate_substrings(s: str, length: int) -> List[str]:
    """
    Find all distinct substrings of the given length that appear more than once.

    Uses StringHasher for O(n) hash computation and O(1) per comparison.

    Time Complexity : O(n)   — one pass with rolling hash
    Space Complexity: O(n)   — hash set

    Args:
        s     : Input string.
        length: Fixed substring length to check for duplicates.

    Returns:
        List of distinct substrings of the given length that appear >= 2 times.

    Example:
        find_duplicate_substrings("banana", 2) → ["an", "na"]
    """
    if not s or length <= 0 or length > len(s):
        return []

    hasher = StringHasher(s)
    seen: set = set()
    duplicates: set = set()

    for i in range(len(s) - length + 1):
        h = hasher.query(i, i + length - 1)
        if h in seen:
            duplicates.add(s[i: i + length])
        seen.add(h)

    return sorted(duplicates)


# ---------------------------------------------------------------------------
# 7. Anagram Detection — Sliding Window
# ---------------------------------------------------------------------------

def find_anagrams(text: str, pattern: str) -> List[int]:
    """
    Find All Anagram Starting Positions — Sliding Window, O(n).

    Maintains a frequency map of the pattern and a sliding window of the same
    length over the text. Uses a `matches` counter that tracks how many
    characters currently have equal frequency in both maps; when matches == 26
    (all characters balanced), the current window is an anagram.

    Time Complexity : O(n)       — single pass; window adjustments are O(1)
    Space Complexity: O(1)       — two fixed-size arrays of length 26

    Args:
        text   : The string to search within.
        pattern: The pattern whose anagrams we seek.

    Returns:
        Sorted list of start indices in `text` where an anagram of `pattern` begins.

    Example:
        find_anagrams("cbaebabacd", "abc") → [0, 6]
        find_anagrams("abab", "ab")        → [0, 1, 2]

    Interview Notes:
        - LeetCode 438 (Find All Anagrams in a String). Very common problem.
        - The "match counter" trick avoids O(26) dict comparison each step.
        - Equivalent to: count of characters with freq[c] == pattern_freq[c].
        - Sliding window with frequency maps is the template for many problems:
          LC 567 (Permutation in String), LC 3 (Longest Substring Without Repeat).
    """
    if not pattern or not text or len(pattern) > len(text):
        return []

    p_freq = [0] * 26
    w_freq = [0] * 26
    m = len(pattern)

    for ch in pattern:
        p_freq[ord(ch) - ord('a')] += 1

    # Initialise the first window
    for ch in text[:m]:
        w_freq[ord(ch) - ord('a')] += 1

    def _count_matches() -> int:
        return sum(1 for i in range(26) if p_freq[i] == w_freq[i])

    matches = _count_matches()
    result: List[int] = []

    if matches == 26:
        result.append(0)

    for i in range(m, len(text)):
        # Add right character
        right_idx = ord(text[i]) - ord('a')
        w_freq[right_idx] += 1
        if w_freq[right_idx] == p_freq[right_idx]:
            matches += 1
        elif w_freq[right_idx] == p_freq[right_idx] + 1:
            matches -= 1   # just went from equal to over

        # Remove left character
        left_idx = ord(text[i - m]) - ord('a')
        w_freq[left_idx] -= 1
        if w_freq[left_idx] == p_freq[left_idx]:
            matches += 1
        elif w_freq[left_idx] == p_freq[left_idx] - 1:
            matches -= 1   # just went from equal to under

        if matches == 26:
            result.append(i - m + 1)

    return result


# ---------------------------------------------------------------------------
# 8. Longest Common Substring — DP
# ---------------------------------------------------------------------------

def longest_common_substring(s1: str, s2: str) -> str:
    """
    Longest Common Substring — Dynamic Programming, O(n * m).

    Builds a 2D DP table where dp[i][j] = length of the longest common
    substring ending at s1[i-1] and s2[j-1]. The recurrence is:

        dp[i][j] = dp[i-1][j-1] + 1   if s1[i-1] == s2[j-1]
                   0                   otherwise

    Note: Unlike the Longest Common Subsequence, characters must be
    contiguous (no gaps).

    Time Complexity : O(n * m)   n = len(s1), m = len(s2)
    Space Complexity: O(n * m)   DP table (can be reduced to O(min(n,m)) with rolling array)

    Args:
        s1: First string.
        s2: Second string.

    Returns:
        The longest substring common to both s1 and s2.
        Returns "" if no common substring exists.

    Example:
        longest_common_substring("abcdef", "bcdfgh") → "bcd"
        longest_common_substring("ABABC",  "BABCAB") → "BABC"

    Interview Notes:
        - LCS (substring) vs LCS (subsequence): substring requires contiguity;
          subsequence allows gaps. Both use DP but the recurrence differs.
        - Space optimisation: only need the previous row, reducing space to O(m).
        - The suffix array approach solves this in O((n+m) log(n+m)) and also
          handles k-string generalisation.
        - Common follow-up: "find ALL longest common substrings" — track all
          positions that achieve max_len.
    """
    if not s1 or not s2:
        return ""

    n, m = len(s1), len(s2)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    max_len = 0
    end_idx = 0   # end index in s1 (exclusive) of the best match

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
                if dp[i][j] > max_len:
                    max_len = dp[i][j]
                    end_idx = i   # s1[end_idx - max_len : end_idx] is the LCS
            # else dp[i][j] remains 0 (no common substring ending here)

    return s1[end_idx - max_len: end_idx]


# ---------------------------------------------------------------------------
# 9. Run-Length Encoding
# ---------------------------------------------------------------------------

def run_length_encode(s: str) -> str:
    """
    Run-Length Encoding — compress consecutive repeated characters.

    Replaces each run of consecutive identical characters with the character
    followed by its count. Runs of length 1 are written as the character only
    (no "1" suffix) to keep short strings compact.

    Time Complexity : O(n)
    Space Complexity: O(n) — output string

    Args:
        s: Input string (any characters).

    Returns:
        Run-length encoded string.
        Returns "" for empty input.

    Example:
        run_length_encode("AAABBBCCDDDDEE") → "A3B3C2D4E2"
        run_length_encode("ABCD")           → "ABCD"  (no compression)
        run_length_encode("AABBA")          → "A2B2A"

    Interview Notes:
        - Useful for data with long runs (images, DNA sequences).
        - Does NOT help (or can expand) strings without repeated characters.
        - Common follow-up: decode the encoded string (see run_length_decode).
        - LeetCode 443 (String Compression) asks for in-place compression.
    """
    if not s:
        return ""

    result = []
    count = 1

    for i in range(1, len(s)):
        if s[i] == s[i - 1]:
            count += 1
        else:
            result.append(s[i - 1])
            if count > 1:
                result.append(str(count))
            count = 1

    # Append the last run
    result.append(s[-1])
    if count > 1:
        result.append(str(count))

    return "".join(result)


# ---------------------------------------------------------------------------
# 10. Run-Length Decoding
# ---------------------------------------------------------------------------

def run_length_decode(s: str) -> str:
    """
    Run-Length Decoding — inverse of run_length_encode.

    Parses the encoded string: each character may optionally be followed by
    a digit sequence representing its repeat count. Characters without a
    count are emitted once.

    Time Complexity : O(n + output_length)
    Space Complexity: O(output_length) — decoded string

    Args:
        s: Run-length encoded string as produced by run_length_encode.

    Returns:
        Original decoded string.
        Returns "" for empty input.

    Example:
        run_length_decode("A3B3C2D4E2") → "AAABBBCCDDDDEE"
        run_length_decode("ABCD")       → "ABCD"
        run_length_decode("A2B2A")      → "AABBA"

    Interview Notes:
        - The decoder must handle multi-digit counts (e.g., "A12" → "A" * 12).
        - Edge case: count immediately followed by another digit (e.g., "A12B3").
          Collect all consecutive digit characters before converting.
        - Validates cleanly using a two-pointer / state-machine approach.
    """
    if not s:
        return ""

    result = []
    i = 0
    n = len(s)

    while i < n:
        ch = s[i]
        i += 1
        # Collect digits following this character
        count_str = []
        while i < n and s[i].isdigit():
            count_str.append(s[i])
            i += 1
        count = int("".join(count_str)) if count_str else 1
        result.append(ch * count)

    return "".join(result)


# ---------------------------------------------------------------------------
# Demo / __main__
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 70)
    print("  String Algorithms — SDE Interview Prep Demo")
    print("=" * 70)

    # ---- KMP ----------------------------------------------------------------
    print("\n1. KMP Pattern Matching")
    cases_kmp = [
        ("ABABDABACDABABCABAB", "ABABCABAB", [10]),
        ("AAAAAA",              "AA",         [0, 1, 2, 3, 4]),
        ("GEEKS FOR GEEKS",     "GEEKS",      [0, 10]),
        ("hello",               "world",      []),
    ]
    for text, pat, expected in cases_kmp:
        got = kmp_search(text, pat)
        ok = "[PASS]" if got == expected else "[FAIL]"
        print(f"  kmp_search({text!r}, {pat!r})")
        print(f"    → {got}  (expected {expected})  {ok}")

    # ---- Rabin-Karp ---------------------------------------------------------
    print("\n2. Rabin-Karp Pattern Matching")
    cases_rk = [
        ("GEEKS FOR GEEKS", "GEEKS", [0, 10]),
        ("AABAACAADAABAABA", "AABA",  [0, 9, 12]),
        ("abcdef",           "xyz",   []),
    ]
    for text, pat, expected in cases_rk:
        got = rabin_karp_search(text, pat)
        ok = "[PASS]" if got == expected else "[FAIL]"
        print(f"  rabin_karp_search({text!r}, {pat!r})")
        print(f"    → {got}  (expected {expected})  {ok}")

    # ---- Rabin-Karp Multi ---------------------------------------------------
    print("\n3. Rabin-Karp Multi-Pattern")
    result_multi = rabin_karp_multi("abcabcabc", ["abc", "cab", "xyz"])
    print(f"  text='abcabcabc', patterns=['abc','cab','xyz']")
    print(f"  → {result_multi}")

    # ---- Z-Algorithm --------------------------------------------------------
    print("\n4. Z-Algorithm Pattern Matching")
    cases_z = [
        ("aabxaaabxaaabxacb", "aabx", [0, 5, 10]),
        ("AABAACAADAABAABA",   "AABA", [0, 9, 12]),
        ("hello",              "ll",   [2]),
    ]
    for text, pat, expected in cases_z:
        got = z_algorithm(text, pat)
        ok = "[PASS]" if got == expected else "[FAIL]"
        print(f"  z_algorithm({text!r}, {pat!r})")
        print(f"    → {got}  (expected {expected})  {ok}")

    # ---- Manacher -----------------------------------------------------------
    print("\n5. Manacher's Algorithm — Longest Palindromic Substring")
    cases_man = [
        ("babad",   {"bab", "aba"}),
        ("cbbd",    {"bb"}),
        ("racecar", {"racecar"}),
        ("a",       {"a"}),
        ("ac",      {"a", "c"}),
    ]
    for s, valid_set in cases_man:
        got = manacher(s)
        ok = "[PASS]" if got in valid_set else "[FAIL]"
        print(f"  manacher({s!r}) → {got!r}  (valid: {valid_set})  {ok}")

    # ---- String Hashing -----------------------------------------------------
    print("\n6. String Hashing")
    sh = StringHasher("abcabcabc")
    print(f"  StringHasher('abcabcabc')")
    print(f"  equal(0,2, 3,5) [abc==abc]: {sh.equal(0,2,3,5)}  (expected True)")
    print(f"  equal(0,2, 6,8) [abc==abc]: {sh.equal(0,2,6,8)}  (expected True)")
    print(f"  equal(0,1, 1,2) [ab==bc]:   {sh.equal(0,1,1,2)}  (expected False)")
    dups = find_duplicate_substrings("banana", 2)
    print(f"  find_duplicate_substrings('banana', 2) → {dups}  (expected ['an', 'na'])")

    # ---- Anagram Detection --------------------------------------------------
    print("\n7. Anagram Detection — Sliding Window")
    cases_anagram = [
        ("cbaebabacd", "abc",  [0, 6]),
        ("abab",        "ab",   [0, 1, 2]),
        ("hello",       "oell", [1]),
    ]
    for text, pat, expected in cases_anagram:
        got = find_anagrams(text, pat)
        ok = "[PASS]" if got == expected else "[FAIL]"
        print(f"  find_anagrams({text!r}, {pat!r})")
        print(f"    → {got}  (expected {expected})  {ok}")

    # ---- Longest Common Substring -------------------------------------------
    print("\n8. Longest Common Substring — DP")
    cases_lcs = [
        ("abcdef",  "bcdfgh", "bcd"),
        ("ABABC",   "BABCAB", "BABC"),
        ("abcde",   "xyz",    ""),
        ("abcabc",  "abc",    "abc"),
    ]
    for s1, s2, expected in cases_lcs:
        got = longest_common_substring(s1, s2)
        ok = "[PASS]" if got == expected else "[FAIL]"
        print(f"  longest_common_substring({s1!r}, {s2!r}) → {got!r}  (expected {expected!r})  {ok}")

    # ---- Run-Length Encoding / Decoding -------------------------------------
    print("\n9 & 10. Run-Length Encoding / Decoding")
    cases_rle = [
        "AAABBBCCDDDDEE",
        "ABCD",
        "AABBA",
        "AAAAAAAAAAAA",   # 12 A's
        "",
    ]
    for original in cases_rle:
        encoded = run_length_encode(original)
        decoded = run_length_decode(encoded)
        roundtrip_ok = "[PASS]" if decoded == original else "[FAIL]"
        print(f"  encode({original!r}) → {encoded!r}  decode → {decoded!r}  {roundtrip_ok}")

    # ---- Complexity Summary -------------------------------------------------
    print("\n" + "=" * 70)
    print("  Complexity Summary")
    print("=" * 70)
    rows = [
        ("Algorithm",                 "Time",          "Space",    "Notes"),
        ("-" * 26,                    "-" * 15,        "-" * 8,    "-" * 30),
        ("kmp_search",                "O(n+m)",        "O(m)",     "failure function"),
        ("rabin_karp_search",         "O(n+m) avg",    "O(1)",     "rolling hash"),
        ("rabin_karp_multi",          "O(n+m) avg",    "O(k)",     "k patterns"),
        ("z_algorithm",               "O(n+m)",        "O(n+m)",   "Z-box trick"),
        ("manacher",                  "O(n)",          "O(n)",     "palindrome"),
        ("StringHasher.query",        "O(1) / O(n)",   "O(n)",     "preprocess O(n)"),
        ("find_anagrams",             "O(n)",          "O(1)",     "26-char freq map"),
        ("longest_common_substring",  "O(n*m)",        "O(n*m)",   "DP table"),
        ("run_length_encode",         "O(n)",          "O(n)",     ""),
        ("run_length_decode",         "O(n)",          "O(n)",     "multi-digit counts"),
    ]
    for name, time_, space, notes in rows:
        print(f"  {name:<30} {time_:<16} {space:<10} {notes}")
