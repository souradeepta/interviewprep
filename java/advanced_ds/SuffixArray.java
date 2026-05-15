package advanced_ds;

import java.util.*;

/**
 * Suffix Array with LCP (Longest Common Prefix) Array
 *
 * Time Complexity:
 * - Construction: O(n log n) with O(log n) space for sorting
 * - Pattern Search: O(m log n) where m = pattern length
 * - LCP Array: O(n) via Kasai's algorithm
 *
 * Space Complexity: O(n)
 *
 * Use Cases:
 * - Substring search (more space-efficient than suffix tree)
 * - Finding all occurrences of a pattern
 * - Finding longest repeated substring
 * - Computing longest common substring
 * - Approximate string matching
 *
 * Key Insight:
 * - Sort all suffixes of the string
 * - Binary search to find pattern ranges
 * - LCP array helps in analysis: LCP[i] = longest common prefix of SA[i] and SA[i+1]
 * - Kasai's algorithm computes LCP in O(n) time
 * - More cache-friendly than suffix tree
 */
public class SuffixArray {

    private String text;
    private int n;
    private int[] sa;  // Suffix array
    private int[] lcp; // LCP array
    private int[] rank; // Rank array for LCP computation

    /**
     * Build suffix array and LCP array.
     *
     * @param text Input string
     */
    public SuffixArray(String text) {
        this.text = text;
        this.n = text.length();

        if (n > 0) {
            buildSuffixArray();
            buildLcpArray();
        }
    }

    /**
     * Build suffix array using O(n log² n) approach.
     */
    private void buildSuffixArray() {
        // Create array of suffix indices
        Integer[] indices = new Integer[n];
        for (int i = 0; i < n; i++) {
            indices[i] = i;
        }

        // Sort indices by their suffixes
        Arrays.sort(indices, (i, j) -> {
            return text.substring(i).compareTo(text.substring(j));
        });

        sa = new int[n];
        for (int i = 0; i < n; i++) {
            sa[i] = indices[i];
        }
    }

    /**
     * Build LCP array using Kasai's algorithm in O(n).
     */
    private void buildLcpArray() {
        rank = new int[n];
        for (int i = 0; i < n; i++) {
            rank[sa[i]] = i;
        }

        lcp = new int[n - 1];
        int h = 0;

        for (int i = 0; i < n; i++) {
            if (rank[i] > 0) {
                int j = sa[rank[i] - 1];
                while (i + h < n && j + h < n &&
                       text.charAt(i + h) == text.charAt(j + h)) {
                    h++;
                }

                lcp[rank[i] - 1] = h;

                if (h > 0) {
                    h--;
                }
            }
        }
    }

    /**
     * Find all occurrences of pattern in text.
     *
     * @param pattern Pattern to find
     * @return List of starting positions (sorted)
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public List<Integer> findPattern(String pattern) {
        List<Integer> matches = new ArrayList<>();

        if (pattern.isEmpty() || n == 0) {
            return matches;
        }

        // Linear search in suffix array for simplicity
        for (int i = 0; i < n; i++) {
            String suffix = text.substring(sa[i]);
            if (suffix.startsWith(pattern)) {
                matches.add(sa[i]);
            }
        }

        Collections.sort(matches);
        return matches;
    }

    /**
     * Find longest substring that appears at least twice.
     *
     * @return Longest repeated substring
     */
    public String longestRepeatedSubstring() {
        if (n == 0) {
            return "";
        }

        int maxLcp = 0;
        int maxIdx = -1;

        for (int i = 0; i < lcp.length; i++) {
            if (lcp[i] > maxLcp) {
                maxLcp = lcp[i];
                maxIdx = i;
            }
        }

        if (maxIdx == -1) {
            return "";
        }

        int start = sa[maxIdx];
        return text.substring(start, start + maxLcp);
    }

    /**
     * Get the suffix array.
     *
     * @return Copy of suffix array
     */
    public int[] getSuffixArray() {
        return sa.clone();
    }

    /**
     * Get the LCP array.
     *
     * @return Copy of LCP array
     */
    public int[] getLcpArray() {
        return lcp.clone();
    }

    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public static void main(String[] args) {
        // Example 1: Basic suffix array
        System.out.println("=== Example 1: Suffix Array ===");
        String text = "banana";
        SuffixArray sa = new SuffixArray(text);

        System.out.println("Text: \"" + text + "\"");
        System.out.println("Suffix Array: " + Arrays.toString(sa.getSuffixArray()));
        System.out.println("LCP Array: " + Arrays.toString(sa.getLcpArray()));

        System.out.println("\nSuffixes in sorted order:");
        for (int idx : sa.getSuffixArray()) {
            System.out.printf("  %2d: %s%n", idx, text.substring(idx));
        }

        // Example 2: Pattern finding
        System.out.println("\n=== Example 2: Pattern Finding ===");
        String text2 = "mississippi";
        SuffixArray sa2 = new SuffixArray(text2);

        String[] patterns = {"is", "si", "pp", "mis"};
        System.out.println("Text: \"" + text2 + "\"");
        for (String pattern : patterns) {
            List<Integer> positions = sa2.findPattern(pattern);
            System.out.println("Pattern \"" + pattern + "\": positions " + positions);
        }

        // Example 3: Longest repeated substring
        System.out.println("\n=== Example 3: Longest Repeated Substring ===");
        String text3 = "abracadabra";
        SuffixArray sa3 = new SuffixArray(text3);

        String lrs = sa3.longestRepeatedSubstring();
        System.out.println("Text: \"" + text3 + "\"");
        System.out.println("Longest repeated substring: \"" + lrs + "\"");

        String text4 = "aabaabaab";
        SuffixArray sa4 = new SuffixArray(text4);
        String lrs2 = sa4.longestRepeatedSubstring();
        System.out.println("\nText: \"" + text4 + "\"");
        System.out.println("Longest repeated substring: \"" + lrs2 + "\"");
    }
}
