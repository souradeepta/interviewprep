package advanced_ds;

import java.util.*;

/**
 * Suffix Tree
 *
 * Time Complexity:
 * - Construction: O(n) with Ukkonen's algorithm (simplified: O(n²) here)
 * - Pattern search: O(m) where m = pattern length
 * - Longest repeated substring: O(n)
 * - Substring counting: O(n)
 * - Space Complexity: O(n)
 *
 * Use Cases:
 * - Pattern matching and substring search (faster than regex)
 * - Finding longest repeated substring
 * - Longest common substring of multiple strings
 * - String compression
 * - Palindrome detection
 *
 * Key Insight:
 * - Compact trie of all suffixes
 * - Each edge has substring, not single character
 * - Linear space and time with Ukkonen's algorithm
 * - More complex to implement than suffix array
 * - Better for multiple queries on same string
 */
public class SuffixTree {

    static class Node {
        Map<Character, Node> children = new HashMap<>();
        Node suffixLink;
        int start, end;
        int suffixIdx;

        Node() {
            this.start = -1;
            this.end = -1;
            this.suffixIdx = -1;
        }
    }

    private String text;
    private int n;
    private Node root;

    /**
     * Build suffix tree from text.
     *
     * @param text Input string
     */
    public SuffixTree(String text) {
        this.text = text + "$";  // Add sentinel
        this.n = this.text.length();
        this.root = new Node();
        this.root.start = -1;
        this.root.end = 0;

        buildTree();
    }

    /**
     * Build suffix tree by inserting all suffixes.
     */
    private void buildTree() {
        for (int i = 0; i < n; i++) {
            insertSuffix(i);
        }
    }

    /**
     * Insert suffix starting at suffixIdx.
     */
    private void insertSuffix(int suffixIdx) {
        Node node = root;
        int i = suffixIdx;

        while (i < n) {
            char c = text.charAt(i);

            if (!node.children.containsKey(c)) {
                // Create new leaf
                Node leaf = new Node();
                leaf.start = i;
                leaf.end = n;
                leaf.suffixIdx = suffixIdx;
                node.children.put(c, leaf);
                break;
            } else {
                Node edgeNode = node.children.get(c);
                int edgeLen = edgeNode.end - edgeNode.start;

                // Check if suffix matches this edge
                int matchLen = 0;
                while (matchLen < edgeLen && i + matchLen < n) {
                    if (text.charAt(edgeNode.start + matchLen) != text.charAt(i + matchLen)) {
                        break;
                    }
                    matchLen++;
                }

                if (matchLen == edgeLen) {
                    // Full edge match
                    node = edgeNode;
                    i += edgeLen;
                } else {
                    // Partial match, split edge
                    Node splitNode = new Node();
                    splitNode.start = edgeNode.start;
                    splitNode.end = edgeNode.start + matchLen;
                    splitNode.suffixIdx = -1;

                    // Old edge becomes child
                    char oldChar = text.charAt(edgeNode.start + matchLen);
                    splitNode.children.put(oldChar, edgeNode);
                    edgeNode.start = splitNode.end;

                    // New leaf
                    Node leaf = new Node();
                    leaf.start = i + matchLen;
                    leaf.end = n;
                    leaf.suffixIdx = suffixIdx;
                    splitNode.children.put(text.charAt(i + matchLen), leaf);

                    // Replace edge
                    node.children.put(c, splitNode);
                    break;
                }
            }
        }
    }

    /**
     * Find all occurrences of pattern.
     *
     * @param pattern Pattern to search
     * @return List of starting positions
     */
    public List<Integer> search(String pattern) {
        List<Integer> positions = new ArrayList<>();
        Node node = root;
        int i = 0;

        // Traverse tree following pattern
        while (i < pattern.length()) {
            char c = pattern.charAt(i);

            if (!node.children.containsKey(c)) {
                return positions;
            }

            Node edgeNode = node.children.get(c);
            String edgeStr = text.substring(edgeNode.start, edgeNode.end);
            int edgeLen = edgeStr.length();

            // Check if pattern matches this edge
            String patternRemaining = pattern.substring(i);
            int matchLen = 0;

            while (matchLen < edgeLen && matchLen < patternRemaining.length()) {
                if (edgeStr.charAt(matchLen) != patternRemaining.charAt(matchLen)) {
                    return positions;
                }
                matchLen++;
            }

            i += matchLen;
            node = edgeNode;
        }

        // Collect all leaf positions under this node
        collectPositions(node, positions);
        Collections.sort(positions);
        return positions;
    }

    /**
     * Collect suffix indices from all leaves under node.
     */
    private void collectPositions(Node node, List<Integer> positions) {
        if (node.suffixIdx != -1) {
            positions.add(node.suffixIdx);
        } else {
            for (Node child : node.children.values()) {
                collectPositions(child, positions);
            }
        }
    }

    /**
     * Find longest substring that appears at least twice.
     *
     * @return Longest repeated substring
     */
    public String longestRepeatedSubstring() {
        int[] maxLen = {0};
        Node[] maxNode = {null};

        dfs(root, 0, maxLen, maxNode);

        if (maxNode[0] != null && maxLen[0] > 0) {
            return text.substring(0, maxLen[0]);
        }

        return "";
    }

    private void dfs(Node node, int depth, int[] maxLen, Node[] maxNode) {
        if (node.suffixIdx != -1) {
            if (depth > maxLen[0]) {
                maxLen[0] = depth;
                maxNode[0] = node;
            }
        } else {
            int leafCount = countLeaves(node);
            if (leafCount >= 2 && depth > maxLen[0]) {
                maxLen[0] = depth;
                maxNode[0] = node;
            }
        }

        for (Node child : node.children.values()) {
            int childDepth = depth + (child.end - child.start);
            dfs(child, childDepth, maxLen, maxNode);
        }
    }

    /**
     * Count leaves under node.
     */
    private int countLeaves(Node node) {
        if (node.suffixIdx != -1) {
            return 1;
        }

        int count = 0;
        for (Node child : node.children.values()) {
            count += countLeaves(child);
        }

        return count;
    }

    public static void main(String[] args) {
        // Example 1: Pattern search
        System.out.println("=== Example 1: Pattern Search ===");
        String text = "banana";
        SuffixTree tree = new SuffixTree(text);

        String[] patterns = {"ana", "na", "ban", "nana"};
        System.out.println("Text: \"" + text + "\"");
        for (String pattern : patterns) {
            List<Integer> positions = tree.search(pattern);
            System.out.println("Pattern \"" + pattern + "\": positions " + positions);
        }

        // Example 2: Longest repeated substring
        System.out.println("\n=== Example 2: Longest Repeated Substring ===");
        String[] texts = {"banana", "abracadabra", "mississippi"};
        for (String t : texts) {
            SuffixTree t2 = new SuffixTree(t);
            String lrs = t2.longestRepeatedSubstring();
            System.out.println("Text \"" + t + "\": longest repeated = \"" + lrs + "\"");
        }

        // Example 3: Complex text
        System.out.println("\n=== Example 3: Complex Text ===");
        String text3 = "hello world hello";
        SuffixTree tree3 = new SuffixTree(text3);

        String[] patterns3 = {"hello", "world", "ll", "o w"};
        System.out.println("Text: \"" + text3 + "\"");
        for (String pattern : patterns3) {
            List<Integer> positions = tree3.search(pattern);
            System.out.println("Pattern \"" + pattern + "\": positions " + positions);
        }
    }
}
