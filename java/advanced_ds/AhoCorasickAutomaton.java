package advanced_ds;

import java.util.*;

/**
 * Aho-Corasick Automaton (AC Automaton)
 *
 * Time Complexity:
 * - Construction: O(m * k) where m = total length of all patterns, k = alphabet size
 * - Searching: O(n + z) where n = text length, z = number of matches
 * - Space Complexity: O(m * k)
 *
 * Use Cases:
 * - Multi-pattern string matching (finding multiple patterns in text)
 * - Substring search
 * - Spam detection (multiple bad words)
 * - DNA sequence searching
 * - Dictionary lookup
 *
 * Key Insight:
 * - Build trie of all patterns
 * - Compute failure function (like KMP) for each node
 * - Use failure links to skip mismatches efficiently
 * - Process text in single pass finding all pattern occurrences
 */
public class AhoCorasickAutomaton {

    /**
     * Trie node with failure link.
     */
    static class Node {
        Map<Character, Node> children = new HashMap<>();
        Node failure;
        List<Integer> output = new ArrayList<>();  // Pattern IDs that end at this node
    }

    private Node root;
    private List<String> patterns;

    /**
     * Initialize Aho-Corasick automaton.
     */
    public AhoCorasickAutomaton() {
        this.root = new Node();
        this.patterns = new ArrayList<>();
    }

    /**
     * Add a pattern to the automaton.
     *
     * @param pattern Pattern to add
     */
    public void addPattern(String pattern) {
        Node node = root;
        for (char c : pattern.toCharArray()) {
            node.children.putIfAbsent(c, new Node());
            node = node.children.get(c);
        }

        // Store pattern ID at the end node
        int patternId = patterns.size();
        patterns.add(pattern);
        node.output.add(patternId);
    }

    /**
     * Build failure function using BFS.
     */
    public void build() {
        Queue<Node> queue = new LinkedList<>();

        // Set failure link for root children to root
        root.failure = root;
        for (Node child : root.children.values()) {
            child.failure = root;
            queue.add(child);
        }

        // BFS to compute failure links
        while (!queue.isEmpty()) {
            Node node = queue.poll();

            for (Map.Entry<Character, Node> entry : node.children.entrySet()) {
                char c = entry.getKey();
                Node child = entry.getValue();

                // Find failure node that has this character
                Node failureNode = node.failure;
                while (failureNode != root && !failureNode.children.containsKey(c)) {
                    failureNode = failureNode.failure;
                }

                if (failureNode.children.containsKey(c) && failureNode.children.get(c) != child) {
                    child.failure = failureNode.children.get(c);
                } else {
                    child.failure = root;
                }

                // Add patterns from failure node's output
                child.output.addAll(child.failure.output);
                queue.add(child);
            }
        }
    }

    /**
     * Result entry for a match.
     */
    public static class Match {
        public int position;
        public String pattern;

        Match(int pos, String pat) {
            this.position = pos;
            this.pattern = pat;
        }

        @Override
        /**
         * [Brief description]
         *
         * @param [param] [description]
         * @return [description]
         * @time O([complexity])
         */
        public String toString() {
            return String.format("(%d, \"%s\")", position, pattern);
        }
    }

    /**
     * Search for all patterns in text.
     *
     * @param text Text to search in
     * @return List of matches (position, pattern)
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public List<Match> search(String text) {
        List<Match> matches = new ArrayList<>();
        Node node = root;

        for (int i = 0; i < text.length(); i++) {
            char c = text.charAt(i);

            // Follow failure links until we find a match or reach root
            while (node != root && !node.children.containsKey(c)) {
                node = node.failure;
            }

            if (node.children.containsKey(c)) {
                node = node.children.get(c);
            } else {
                node = root;
            }

            // Report all patterns that match at this position
            for (int patternId : node.output) {
                String pattern = patterns.get(patternId);
                matches.add(new Match(i - pattern.length() + 1, pattern));
            }
        }

        return matches;
    }

    /**
     * Result entry for a match with pattern ID.
     */
    public static class MatchId {
        public int position;
        public int patternId;

        MatchId(int pos, int id) {
            this.position = pos;
            this.patternId = id;
        }

        @Override
        /**
         * [Brief description]
         *
         * @param [param] [description]
         * @return [description]
         * @time O([complexity])
         */
        public String toString() {
            return String.format("(%d, %d)", position, patternId);
        }
    }

    /**
     * Search for all patterns in text (returns pattern IDs).
     *
     * @param text Text to search in
     * @return List of matches (position, pattern_id)
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public List<MatchId> searchWithIds(String text) {
        List<MatchId> matches = new ArrayList<>();
        Node node = root;

        for (int i = 0; i < text.length(); i++) {
            char c = text.charAt(i);

            while (node != root && !node.children.containsKey(c)) {
                node = node.failure;
            }

            if (node.children.containsKey(c)) {
                node = node.children.get(c);
            } else {
                node = root;
            }

            for (int patternId : node.output) {
                String pattern = patterns.get(patternId);
                matches.add(new MatchId(i - pattern.length() + 1, patternId));
            }
        }

        return matches;
    }

    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public static void main(String[] args) {
        // Example 1: Basic pattern matching
        System.out.println("=== Example 1: Basic Pattern Matching ===");
        AhoCorasickAutomaton automaton = new AhoCorasickAutomaton();

        String[] patterns = {"he", "she", "his", "hers"};
        for (String pattern : patterns) {
            automaton.addPattern(pattern);
        }
        automaton.build();

        String text = "ushers";
        List<Match> matches = automaton.search(text);
        System.out.println("Text: \"" + text + "\"");
        System.out.println("Patterns: " + Arrays.toString(patterns));
        System.out.println("Matches: " + matches);

        // Example 2: More complex text
        System.out.println("\n=== Example 2: Complex Text ===");
        AhoCorasickAutomaton automaton2 = new AhoCorasickAutomaton();

        String[] patterns2 = {"cat", "car", "card", "care", "careful"};
        for (String pattern : patterns2) {
            automaton2.addPattern(pattern);
        }
        automaton2.build();

        String text2 = "a cat caring carefully with a card";
        List<Match> matches2 = automaton2.search(text2);
        System.out.println("Text: \"" + text2 + "\"");
        System.out.println("Patterns: " + Arrays.toString(patterns2));
        System.out.println("Matches: " + matches2);

        // Example 3: Overlapping patterns
        System.out.println("\n=== Example 3: Overlapping Patterns ===");
        AhoCorasickAutomaton automaton3 = new AhoCorasickAutomaton();

        String[] patterns3 = {"ab", "ba", "aaab", "abab", "baa"};
        for (String pattern : patterns3) {
            automaton3.addPattern(pattern);
        }
        automaton3.build();

        String text3 = "aabaab";
        List<Match> matches3 = automaton3.search(text3);
        System.out.println("Text: \"" + text3 + "\"");
        System.out.println("Patterns: " + Arrays.toString(patterns3));
        matches3.sort((a, b) -> Integer.compare(a.position, b.position));
        System.out.println("Matches (sorted by position): " + matches3);
    }
}
