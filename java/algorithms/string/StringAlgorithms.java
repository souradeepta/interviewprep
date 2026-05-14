package algorithms.string;

import java.util.*;

/**
 * Comprehensive collection of string algorithm implementations for SDE interview preparation.
 *
 * <p>Algorithms included:
 * <ol>
 *   <li>{@link #kmpSearch}              — O(n+m) KMP pattern matching</li>
 *   <li>{@link #buildFailureFunction}   — O(m) KMP failure function</li>
 *   <li>{@link #rabinKarpSearch}        — O(n+m) avg rolling hash pattern matching</li>
 *   <li>{@link #rabinKarpMulti}         — O(n+m) avg multi-pattern search</li>
 *   <li>{@link #zAlgorithm}             — O(n+m) Z-array pattern matching</li>
 *   <li>{@link #manacher}               — O(n) longest palindromic substring</li>
 *   <li>{@link #findAnagrams}           — O(n) sliding window anagram detection</li>
 *   <li>{@link #longestCommonSubstring} — O(nm) DP longest common substring</li>
 *   <li>{@link #runLengthEncode}        — O(n) run-length encoding</li>
 *   <li>{@link #runLengthDecode}        — O(n) run-length decoding</li>
 * </ol>
 *
 * <p>Summary of complexities (n = text length, m = pattern length):
 * <pre>
 * Algorithm                  | Time          | Space   | Notes
 * ---------------------------+---------------+---------+---------------------
 * kmpSearch                  | O(n+m)        | O(m)    | failure function
 * rabinKarpSearch            | O(n+m) avg    | O(1)    | rolling hash
 * rabinKarpMulti             | O(n+m) avg    | O(k)    | k patterns
 * zAlgorithm                 | O(n+m)        | O(n+m)  | Z-box trick
 * manacher                   | O(n)          | O(n)    | '#' transform
 * findAnagrams               | O(n)          | O(1)    | 26-char freq array
 * longestCommonSubstring     | O(n*m)        | O(n*m)  | DP table
 * runLengthEncode            | O(n)          | O(n)    | consecutive runs
 * runLengthDecode            | O(n)          | O(n)    | multi-digit counts
 * </pre>
 */
public class StringAlgorithms {

    // -----------------------------------------------------------------------
    // Rolling hash constants (used by Rabin-Karp)
    // -----------------------------------------------------------------------
    private static final long RK_BASE = 256L;
    private static final long RK_MOD  = 2_147_483_647L; // 2^31 - 1 (Mersenne prime)

    // -----------------------------------------------------------------------
    // 1. KMP — Failure Function
    // -----------------------------------------------------------------------

    /**
     * Builds the KMP failure function (prefix function / partial match table) for {@code pattern}.
     *
     * <p>{@code failure[i]} = length of the longest proper prefix of {@code pattern[0..i]}
     * that is also a suffix of {@code pattern[0..i]}.
     *
     * <p>Example: pattern = "ABABCABAB" → failure = [0, 0, 1, 2, 0, 1, 2, 3, 4]
     *
     * <ul>
     *   <li>Time:  O(m)
     *   <li>Space: O(m)
     * </ul>
     *
     * @param pattern the pattern string
     * @return the failure (prefix) function array of length {@code pattern.length()}
     */
    public static int[] buildFailureFunction(String pattern) {
        int m = pattern.length();
        int[] failure = new int[m];
        int length = 0; // length of previous longest prefix-suffix
        int i = 1;

        while (i < m) {
            if (pattern.charAt(i) == pattern.charAt(length)) {
                length++;
                failure[i] = length;
                i++;
            } else {
                if (length != 0) {
                    length = failure[length - 1]; // fall back (don't advance i)
                } else {
                    failure[i] = 0;
                    i++;
                }
            }
        }
        return failure;
    }

    // -----------------------------------------------------------------------
    // 2. KMP Search
    // -----------------------------------------------------------------------

    /**
     * KMP (Knuth-Morris-Pratt) Pattern Matching.
     *
     * <p>Finds all starting indices where {@code pattern} occurs in {@code text} using the
     * failure function to avoid redundant character comparisons. The text pointer never
     * backtracks — each character is processed at most twice total.
     *
     * <p>Key insight: after a mismatch at {@code pattern[j]}, fall back to
     * {@code pattern[failure[j-1]]} instead of restarting from {@code pattern[0]}.
     *
     * <ul>
     *   <li>Time:  O(n + m) — O(m) preprocessing + O(n) search
     *   <li>Space: O(m)     — failure function array
     * </ul>
     *
     * @param text    the string to search within
     * @param pattern the pattern to find
     * @return list of 0-based starting indices where pattern occurs (overlapping matches included)
     *
     * <p>Interview Notes:
     * <ul>
     *   <li>LeetCode 28 (Find the Index of the First Occurrence in a String).
     *   <li>The failure function encodes the self-similarity structure of the pattern.
     *   <li>Never backtracks in the text — {@code i} (text pointer) only moves forward.
     * </ul>
     */
    public static List<Integer> kmpSearch(String text, String pattern) {
        List<Integer> matches = new ArrayList<>();
        if (text == null || pattern == null || pattern.isEmpty() || pattern.length() > text.length()) {
            return matches;
        }

        int n = text.length();
        int m = pattern.length();
        int[] failure = buildFailureFunction(pattern);

        int i = 0; // index into text
        int j = 0; // index into pattern

        while (i < n) {
            if (text.charAt(i) == pattern.charAt(j)) {
                i++;
                j++;
            }
            if (j == m) {
                matches.add(i - j);       // match found starting at i-j
                j = failure[j - 1];        // look for next (possibly overlapping) match
            } else if (i < n && text.charAt(i) != pattern.charAt(j)) {
                if (j != 0) {
                    j = failure[j - 1];   // fall back
                } else {
                    i++;
                }
            }
        }
        return matches;
    }

    // -----------------------------------------------------------------------
    // 3. Rabin-Karp Single Pattern
    // -----------------------------------------------------------------------

    /**
     * Rabin-Karp Rolling Hash Pattern Matching.
     *
     * <p>Computes a polynomial hash of the pattern, then slides a same-length window over the
     * text recomputing the hash in O(1) per step. Character-by-character verification is only
     * done on hash matches, making the average case O(n+m).
     *
     * <p>Rolling hash formula (removing leading char, adding trailing char):
     * <pre>
     *   newHash = (BASE * (oldHash - text[i] * h) + text[i+m]) mod MOD
     *   where h = BASE^(m-1) mod MOD
     * </pre>
     *
     * <ul>
     *   <li>Time:  O(n + m) average, O(n * m) worst case (all spurious collisions)
     *   <li>Space: O(1)
     * </ul>
     *
     * @param text    the string to search within
     * @param pattern the pattern to find
     * @return list of 0-based starting indices where pattern occurs
     *
     * <p>Interview Notes:
     * <ul>
     *   <li>LeetCode 187 (Repeated DNA Sequences) is a canonical rolling hash problem.
     *   <li>Double hashing (two independent base/mod pairs) reduces collision probability.
     *   <li>Rabin-Karp's real advantage over KMP: trivially extends to multi-pattern search.
     * </ul>
     */
    public static List<Integer> rabinKarpSearch(String text, String pattern) {
        List<Integer> matches = new ArrayList<>();
        if (text == null || pattern == null || pattern.isEmpty() || pattern.length() > text.length()) {
            return matches;
        }

        int n = text.length();
        int m = pattern.length();

        // h = BASE^(m-1) mod MOD — coefficient of the leading character
        long h = 1;
        for (int i = 0; i < m - 1; i++) {
            h = (h * RK_BASE) % RK_MOD;
        }

        long patternHash = 0;
        long windowHash  = 0;

        // Compute initial hashes
        for (int i = 0; i < m; i++) {
            patternHash = (patternHash * RK_BASE + pattern.charAt(i)) % RK_MOD;
            windowHash  = (windowHash  * RK_BASE + text.charAt(i))    % RK_MOD;
        }

        for (int i = 0; i <= n - m; i++) {
            if (windowHash == patternHash) {
                // Verify character by character to rule out collisions
                if (text.regionMatches(i, pattern, 0, m)) {
                    matches.add(i);
                }
            }
            // Roll the window
            if (i < n - m) {
                windowHash = (RK_BASE * (windowHash - text.charAt(i) * h) + text.charAt(i + m)) % RK_MOD;
                if (windowHash < 0) windowHash += RK_MOD;
            }
        }
        return matches;
    }

    // -----------------------------------------------------------------------
    // 4. Rabin-Karp Multi-Pattern
    // -----------------------------------------------------------------------

    /**
     * Rabin-Karp Multi-Pattern Search.
     *
     * <p>Groups patterns by length and runs one rolling-hash pass per unique length. All patterns
     * of the same length are hashed into a set, so a single O(n) pass can detect any of them.
     *
     * <ul>
     *   <li>Time:  O(n * L + total_pattern_chars) where L = number of unique pattern lengths
     *   <li>Space: O(k) — k = total number of patterns
     * </ul>
     *
     * @param text     the string to search within
     * @param patterns list of patterns to find
     * @return map from each pattern to its list of start indices in text
     *
     * <p>Interview Notes:
     * <ul>
     *   <li>When all patterns have the same length this achieves a true O(n) scan for all patterns.
     *   <li>For mixed lengths, Aho-Corasick is the asymptotically optimal choice: O(n + total_m + matches).
     * </ul>
     */
    public static Map<String, List<Integer>> rabinKarpMulti(String text, List<String> patterns) {
        Map<String, List<Integer>> result = new LinkedHashMap<>();
        if (text == null || patterns == null || text.isEmpty()) {
            return result;
        }

        for (String p : patterns) {
            result.put(p, new ArrayList<>());
        }

        // Group patterns by length
        Map<Integer, List<String>> byLength = new HashMap<>();
        for (String p : patterns) {
            if (p != null && !p.isEmpty()) {
                byLength.computeIfAbsent(p.length(), k -> new ArrayList<>()).add(p);
            }
        }

        int n = text.length();

        for (Map.Entry<Integer, List<String>> entry : byLength.entrySet()) {
            int m = entry.getKey();
            if (m > n) continue;

            // Build hash → patterns map for this length group
            Map<Long, List<String>> hashToPatterns = new HashMap<>();
            for (String p : entry.getValue()) {
                long ph = 0;
                for (char c : p.toCharArray()) {
                    ph = (ph * RK_BASE + c) % RK_MOD;
                }
                hashToPatterns.computeIfAbsent(ph, k -> new ArrayList<>()).add(p);
            }

            long h = 1;
            for (int i = 0; i < m - 1; i++) h = (h * RK_BASE) % RK_MOD;

            long windowHash = 0;
            for (int i = 0; i < m; i++) {
                windowHash = (windowHash * RK_BASE + text.charAt(i)) % RK_MOD;
            }

            for (int i = 0; i <= n - m; i++) {
                if (hashToPatterns.containsKey(windowHash)) {
                    String window = text.substring(i, i + m);
                    for (String p : hashToPatterns.get(windowHash)) {
                        if (window.equals(p)) {
                            result.get(p).add(i);
                        }
                    }
                }
                if (i < n - m) {
                    windowHash = (RK_BASE * (windowHash - text.charAt(i) * h) + text.charAt(i + m)) % RK_MOD;
                    if (windowHash < 0) windowHash += RK_MOD;
                }
            }
        }
        return result;
    }

    // -----------------------------------------------------------------------
    // 5. Z-Algorithm
    // -----------------------------------------------------------------------

    /**
     * Z-Algorithm Pattern Matching.
     *
     * <p>Concatenates pattern + '$' + text into a string S, then builds the Z-array where
     * {@code Z[i]} = length of the longest substring starting at {@code S[i]} that is also a
     * prefix of S. Positions where {@code Z[i] == pattern.length()} indicate a full match.
     *
     * <p>The Z-box {@code [L, R]} tracks the rightmost match window and enables O(1) initialisation
     * for positions inside the box, yielding an overall O(n+m) algorithm.
     *
     * <ul>
     *   <li>Time:  O(n + m)
     *   <li>Space: O(n + m) — concatenated string and Z-array
     * </ul>
     *
     * @param text    the string to search within
     * @param pattern the pattern to find
     * @return list of 0-based starting indices in {@code text} where pattern occurs
     *
     * <p>Interview Notes:
     * <ul>
     *   <li>Z-array also helps find the shortest period of a string and count distinct substrings.
     *   <li>The '$' sentinel must not appear in text or pattern; any unused character works.
     *   <li>{@code Z[0]} is undefined (the whole string trivially equals itself); conventionally 0.
     * </ul>
     */
    public static List<Integer> zAlgorithm(String text, String pattern) {
        List<Integer> matches = new ArrayList<>();
        if (text == null || pattern == null || pattern.isEmpty() || pattern.length() > text.length()) {
            return matches;
        }

        int m = pattern.length();
        String concat = pattern + '$' + text;
        int nc = concat.length();
        int[] z = new int[nc];

        int lBox = 0, rBox = 0;
        for (int i = 1; i < nc; i++) {
            if (i < rBox) {
                z[i] = Math.min(rBox - i, z[i - lBox]);
            }
            while (i + z[i] < nc && concat.charAt(z[i]) == concat.charAt(i + z[i])) {
                z[i]++;
            }
            if (i + z[i] > rBox) {
                lBox = i;
                rBox = i + z[i];
            }
        }

        int offset = m + 1; // length of "pattern + '$'"
        for (int i = offset; i < nc; i++) {
            if (z[i] == m) {
                matches.add(i - offset);
            }
        }
        return matches;
    }

    // -----------------------------------------------------------------------
    // 6. Manacher's Algorithm
    // -----------------------------------------------------------------------

    /**
     * Manacher's Algorithm — Longest Palindromic Substring in O(n).
     *
     * <p>Transforms the string by inserting '#' separators to unify odd and even length cases:
     * {@code "abba"} becomes {@code "#a#b#b#a#"}. Then computes {@code p[i]} = palindrome radius
     * at position {@code i} in the transformed string.
     *
     * <p>The centre-expansion is amortised O(n) using the right-boundary mirror trick: if the
     * current position is inside a known palindrome, initialise its radius from the mirror and
     * skip redundant comparisons.
     *
     * <ul>
     *   <li>Time:  O(n) — each character expanded at most once total
     *   <li>Space: O(n) — transformed string and radius array
     * </ul>
     *
     * @param s the input string
     * @return the longest palindromic substring; the leftmost one if there are ties
     *
     * <p>Interview Notes:
     * <ul>
     *   <li>LeetCode 5. Classic O(n) solution; naive expand-around-centre is O(n²).
     *   <li>In the transformed string, {@code p[i]} equals the palindrome length in the original.
     *   <li>Start index in original: {@code (centerIdx - maxLen) / 2}.
     * </ul>
     */
    public static String manacher(String s) {
        if (s == null || s.isEmpty()) return "";

        // Transform: "abc" → "#a#b#c#"
        StringBuilder sb = new StringBuilder();
        sb.append('#');
        for (char c : s.toCharArray()) {
            sb.append(c);
            sb.append('#');
        }
        String t = sb.toString();
        int n = t.length();
        int[] p = new int[n];

        int center = 0, right = 0;

        for (int i = 0; i < n; i++) {
            int mirror = 2 * center - i;
            if (i < right) {
                p[i] = Math.min(right - i, p[mirror]);
            }
            // Expand around i
            int li = i - (p[i] + 1);
            int ri = i + (p[i] + 1);
            while (li >= 0 && ri < n && t.charAt(li) == t.charAt(ri)) {
                p[i]++;
                li--;
                ri++;
            }
            // Update rightmost boundary
            if (i + p[i] > right) {
                center = i;
                right  = i + p[i];
            }
        }

        // Find max radius and map back to original string
        int maxLen = 0, centerIdx = 0;
        for (int i = 0; i < n; i++) {
            if (p[i] > maxLen) {
                maxLen    = p[i];
                centerIdx = i;
            }
        }
        int start = (centerIdx - maxLen) / 2;
        return s.substring(start, start + maxLen);
    }

    // -----------------------------------------------------------------------
    // 7. Find All Anagrams — Sliding Window
    // -----------------------------------------------------------------------

    /**
     * Find All Anagram Starting Positions — Sliding Window, O(n).
     *
     * <p>Maintains frequency arrays for the pattern and the current window. A {@code matches}
     * counter tracks how many of the 26 letter frequencies are equal in both arrays. When
     * {@code matches == 26} the current window is an anagram of the pattern.
     *
     * <ul>
     *   <li>Time:  O(n)  — single pass; window adjustment is O(1)
     *   <li>Space: O(1)  — two fixed-length arrays of 26 integers
     * </ul>
     *
     * @param text    the string to search within (lowercase ASCII letters assumed)
     * @param pattern the pattern whose anagrams are sought
     * @return sorted list of start indices in {@code text} where an anagram of pattern begins
     *
     * <p>Interview Notes:
     * <ul>
     *   <li>LeetCode 438 (Find All Anagrams in a String). Very common interview problem.
     *   <li>The "match counter" trick avoids an O(26) array comparison each step.
     *   <li>LC 567 (Permutation in String) is essentially the same problem.
     * </ul>
     */
    public static List<Integer> findAnagrams(String text, String pattern) {
        List<Integer> result = new ArrayList<>();
        if (text == null || pattern == null || pattern.length() > text.length()) {
            return result;
        }

        int[] pFreq = new int[26];
        int[] wFreq = new int[26];
        int m = pattern.length();

        for (char c : pattern.toCharArray()) pFreq[c - 'a']++;
        for (int i = 0; i < m; i++)          wFreq[text.charAt(i) - 'a']++;

        // Count how many characters are balanced between pattern and window
        int matches = 0;
        for (int i = 0; i < 26; i++) {
            if (pFreq[i] == wFreq[i]) matches++;
        }

        if (matches == 26) result.add(0);

        for (int i = m; i < text.length(); i++) {
            // Add right character
            int rightIdx = text.charAt(i) - 'a';
            wFreq[rightIdx]++;
            if (wFreq[rightIdx] == pFreq[rightIdx])         matches++;
            else if (wFreq[rightIdx] == pFreq[rightIdx] + 1) matches--;

            // Remove left character
            int leftIdx = text.charAt(i - m) - 'a';
            wFreq[leftIdx]--;
            if (wFreq[leftIdx] == pFreq[leftIdx])           matches++;
            else if (wFreq[leftIdx] == pFreq[leftIdx] - 1)  matches--;

            if (matches == 26) result.add(i - m + 1);
        }
        return result;
    }

    // -----------------------------------------------------------------------
    // 8. Longest Common Substring — DP
    // -----------------------------------------------------------------------

    /**
     * Longest Common Substring — Dynamic Programming.
     *
     * <p>Builds a 2D DP table where {@code dp[i][j]} = length of the longest common substring
     * ending at {@code s1[i-1]} and {@code s2[j-1]}. Recurrence:
     * <pre>
     *   dp[i][j] = dp[i-1][j-1] + 1   if s1[i-1] == s2[j-1]
     *              0                   otherwise
     * </pre>
     *
     * <p>Note: This is the <em>Longest Common Substring</em> (contiguous), not the
     * Longest Common Subsequence (which allows gaps).
     *
     * <ul>
     *   <li>Time:  O(n * m)   n = s1.length(), m = s2.length()
     *   <li>Space: O(n * m)   DP table (reducible to O(min(n,m)) with rolling array)
     * </ul>
     *
     * @param s1 first string
     * @param s2 second string
     * @return the longest substring common to both strings, or {@code ""} if none
     *
     * <p>Interview Notes:
     * <ul>
     *   <li>Space optimisation: only the previous row is needed — reduces to O(m).
     *   <li>The suffix array approach solves this in O((n+m) log(n+m)) and generalises to k strings.
     *   <li>Common follow-up: return ALL longest common substrings.
     * </ul>
     */
    public static String longestCommonSubstring(String s1, String s2) {
        if (s1 == null || s2 == null || s1.isEmpty() || s2.isEmpty()) return "";

        int n = s1.length();
        int m = s2.length();
        int[][] dp = new int[n + 1][m + 1];
        int maxLen = 0;
        int endIdx = 0; // end index in s1 (exclusive) of the best match

        for (int i = 1; i <= n; i++) {
            for (int j = 1; j <= m; j++) {
                if (s1.charAt(i - 1) == s2.charAt(j - 1)) {
                    dp[i][j] = dp[i - 1][j - 1] + 1;
                    if (dp[i][j] > maxLen) {
                        maxLen = dp[i][j];
                        endIdx = i;
                    }
                }
                // else dp[i][j] remains 0
            }
        }
        return s1.substring(endIdx - maxLen, endIdx);
    }

    // -----------------------------------------------------------------------
    // 9. Run-Length Encoding
    // -----------------------------------------------------------------------

    /**
     * Run-Length Encoding — compress consecutive repeated characters.
     *
     * <p>Replaces each run of identical consecutive characters with the character followed by its
     * count. Runs of length 1 are written as the character only (no "1" suffix) to avoid
     * expanding short strings.
     *
     * <ul>
     *   <li>Time:  O(n)
     *   <li>Space: O(n) — output
     * </ul>
     *
     * @param s the input string (any characters)
     * @return the run-length encoded string, or {@code ""} for empty input
     *
     * <p>Examples:
     * <ul>
     *   <li>{@code "AAABBBCCDDDDEE"} → {@code "A3B3C2D4E2"}
     *   <li>{@code "ABCD"}          → {@code "ABCD"}
     *   <li>{@code "AABBA"}         → {@code "A2B2A"}
     * </ul>
     *
     * <p>Interview Notes:
     * <ul>
     *   <li>LeetCode 443 (String Compression) is the in-place variant.
     *   <li>Encoding can EXPAND strings that have no repeated characters.
     *   <li>Pair with {@link #runLengthDecode} for a round-trip test.
     * </ul>
     */
    public static String runLengthEncode(String s) {
        if (s == null || s.isEmpty()) return "";

        StringBuilder sb = new StringBuilder();
        int count = 1;

        for (int i = 1; i < s.length(); i++) {
            if (s.charAt(i) == s.charAt(i - 1)) {
                count++;
            } else {
                sb.append(s.charAt(i - 1));
                if (count > 1) sb.append(count);
                count = 1;
            }
        }
        // Append last run
        sb.append(s.charAt(s.length() - 1));
        if (count > 1) sb.append(count);

        return sb.toString();
    }

    // -----------------------------------------------------------------------
    // 10. Run-Length Decoding
    // -----------------------------------------------------------------------

    /**
     * Run-Length Decoding — inverse of {@link #runLengthEncode}.
     *
     * <p>Parses the encoded string: each character may optionally be followed by one or more
     * digit characters representing its repeat count. Characters without a count are emitted once.
     * Multi-digit counts (e.g., "A12") are handled correctly.
     *
     * <ul>
     *   <li>Time:  O(n + output_length)
     *   <li>Space: O(output_length) — decoded string
     * </ul>
     *
     * @param s the run-length encoded string
     * @return the decoded original string, or {@code ""} for empty input
     *
     * <p>Examples:
     * <ul>
     *   <li>{@code "A3B3C2D4E2"} → {@code "AAABBBCCDDDDEE"}
     *   <li>{@code "ABCD"}        → {@code "ABCD"}
     *   <li>{@code "A12"}         → {@code "AAAAAAAAAAAA"} (12 A's)
     * </ul>
     *
     * <p>Interview Notes:
     * <ul>
     *   <li>Multi-digit counts require accumulating digits before parsing — a common edge case.
     *   <li>A state-machine (CHAR state → DIGIT state) cleanly handles the parsing logic.
     * </ul>
     */
    public static String runLengthDecode(String s) {
        if (s == null || s.isEmpty()) return "";

        StringBuilder sb = new StringBuilder();
        int i = 0;
        int n = s.length();

        while (i < n) {
            char ch = s.charAt(i++);
            // Collect consecutive digits following this character
            int j = i;
            while (j < n && Character.isDigit(s.charAt(j))) j++;
            int count = (j > i) ? Integer.parseInt(s.substring(i, j)) : 1;
            i = j;
            // Append ch repeated count times
            for (int k = 0; k < count; k++) sb.append(ch);
        }
        return sb.toString();
    }

    // -----------------------------------------------------------------------
    // main — demos for all methods
    // -----------------------------------------------------------------------

    /**
     * Demonstrates every algorithm with representative test cases.
     *
     * @param args unused
     */
    public static void main(String[] args) {
        System.out.println("=".repeat(70));
        System.out.println("  String Algorithms — SDE Interview Prep Demo");
        System.out.println("=".repeat(70));

        // ---- KMP ----------------------------------------------------------------
        System.out.println("\n1. KMP Pattern Matching");
        String[][] kmpCases = {
            {"ABABDABACDABABCABAB", "ABABCABAB"},
            {"AAAAAA",             "AA"},
            {"GEEKS FOR GEEKS",    "GEEKS"},
            {"hello",              "world"},
        };
        for (String[] tc : kmpCases) {
            List<Integer> res = kmpSearch(tc[0], tc[1]);
            System.out.printf("  kmpSearch(%s, %s) -> %s%n", tc[0], tc[1], res);
        }

        // ---- Rabin-Karp ---------------------------------------------------------
        System.out.println("\n2. Rabin-Karp Pattern Matching");
        String[][] rkCases = {
            {"GEEKS FOR GEEKS", "GEEKS"},
            {"AABAACAADAABAABA", "AABA"},
            {"abcdef",          "xyz"},
        };
        for (String[] tc : rkCases) {
            List<Integer> res = rabinKarpSearch(tc[0], tc[1]);
            System.out.printf("  rabinKarpSearch(%s, %s) -> %s%n", tc[0], tc[1], res);
        }

        // ---- Rabin-Karp Multi ---------------------------------------------------
        System.out.println("\n3. Rabin-Karp Multi-Pattern");
        Map<String, List<Integer>> multiResult = rabinKarpMulti(
            "abcabcabc", Arrays.asList("abc", "cab", "xyz")
        );
        System.out.println("  text='abcabcabc', patterns=[abc, cab, xyz]");
        multiResult.forEach((k, v) -> System.out.printf("    %s -> %s%n", k, v));

        // ---- Z-Algorithm --------------------------------------------------------
        System.out.println("\n4. Z-Algorithm Pattern Matching");
        String[][] zCases = {
            {"aabxaaabxaaabxacb", "aabx"},
            {"AABAACAADAABAABA",  "AABA"},
            {"hello",             "ll"},
        };
        for (String[] tc : zCases) {
            List<Integer> res = zAlgorithm(tc[0], tc[1]);
            System.out.printf("  zAlgorithm(%s, %s) -> %s%n", tc[0], tc[1], res);
        }

        // ---- Manacher -----------------------------------------------------------
        System.out.println("\n5. Manacher's Algorithm — Longest Palindromic Substring");
        String[] manCases = {"babad", "cbbd", "racecar", "a", "ac"};
        for (String tc : manCases) {
            System.out.printf("  manacher(%s) -> %s%n", tc, manacher(tc));
        }

        // ---- Find Anagrams ------------------------------------------------------
        System.out.println("\n6. Find All Anagrams — Sliding Window");
        String[][] anagramCases = {
            {"cbaebabacd", "abc"},
            {"abab",       "ab"},
            {"hello",      "oell"},
        };
        for (String[] tc : anagramCases) {
            List<Integer> res = findAnagrams(tc[0], tc[1]);
            System.out.printf("  findAnagrams(%s, %s) -> %s%n", tc[0], tc[1], res);
        }

        // ---- Longest Common Substring -------------------------------------------
        System.out.println("\n7. Longest Common Substring — DP");
        String[][] lcsCases = {
            {"abcdef",  "bcdfgh"},
            {"ABABC",   "BABCAB"},
            {"abcde",   "xyz"},
            {"abcabc",  "abc"},
        };
        for (String[] tc : lcsCases) {
            String res = longestCommonSubstring(tc[0], tc[1]);
            System.out.printf("  longestCommonSubstring(%s, %s) -> \"%s\"%n", tc[0], tc[1], res);
        }

        // ---- Run-Length Encoding / Decoding -------------------------------------
        System.out.println("\n8 & 9. Run-Length Encoding / Decoding");
        String[] rleCases = {"AAABBBCCDDDDEE", "ABCD", "AABBA", "AAAAAAAAAAAA", ""};
        for (String original : rleCases) {
            String encoded = runLengthEncode(original);
            String decoded = runLengthDecode(encoded);
            String status  = decoded.equals(original) ? "[PASS]" : "[FAIL]";
            System.out.printf("  encode(%s) -> %s  decode -> %s  %s%n",
                original, encoded, decoded, status);
        }

        System.out.println("\n" + "=".repeat(70));
        System.out.println("  All demos complete.");
        System.out.println("=".repeat(70));
    }
}
