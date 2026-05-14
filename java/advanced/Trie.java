package advanced;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;

/**
 * Prefix Trie (radix-1) supporting lowercase English letters.
 *
 * <p>Each edge is labeled with a single character.  {@link TrieNode} stores
 * children in a {@link TreeMap} (sorted) for deterministic output; for
 * maximum performance replace with an array of size 26.
 *
 * <p>Time complexities (k = length of the key):
 * <ul>
 *   <li>insert     – O(k)</li>
 *   <li>search     – O(k)</li>
 *   <li>startsWith – O(k)</li>
 *   <li>delete     – O(k)</li>
 *   <li>getAllWords – O(n * k_avg)</li>
 * </ul>
 *
 * <p>Space complexity: O(ALPHABET_SIZE * n * k_avg) worst case.
 */
public class Trie {

    // -------------------------------------------------------------------------
    // Inner TrieNode
    // -------------------------------------------------------------------------

    /**
     * A single node in the Trie.
     */
    public static class TrieNode {
        /** Child nodes keyed by character. */
        Map<Character, TrieNode> children = new TreeMap<>();
        /** Marks this node as the end of a valid word. */
        boolean isEndOfWord;
        /** Count of words that pass through this node (useful for delete). */
        int passCount;

        TrieNode() {
            passCount = 0;
            isEndOfWord = false;
        }
    }

    // -------------------------------------------------------------------------
    // Fields
    // -------------------------------------------------------------------------

    private final TrieNode root;
    private int wordCount;

    // -------------------------------------------------------------------------
    // Constructor
    // -------------------------------------------------------------------------

    /** Creates an empty Trie. */
    public Trie() {
        root = new TrieNode();
    }

    // -------------------------------------------------------------------------
    // Insert
    // -------------------------------------------------------------------------

    /**
     * Inserts {@code word} into the Trie.
     * Inserting a word already present is a no-op.
     *
     * <p>Time: O(k) | Space: O(k) new nodes in the worst case.
     *
     * @param word the word to insert (non-null, non-empty)
     * @throws IllegalArgumentException if {@code word} is null or empty
     */
    public void insert(String word) {
        if (word == null || word.isEmpty())
            throw new IllegalArgumentException("Word must be non-null and non-empty");

        TrieNode cur = root;
        for (char c : word.toCharArray()) {
            cur.children.putIfAbsent(c, new TrieNode());
            cur = cur.children.get(c);
            cur.passCount++;
        }
        if (!cur.isEndOfWord) {
            cur.isEndOfWord = true;
            wordCount++;
        }
    }

    // -------------------------------------------------------------------------
    // Search
    // -------------------------------------------------------------------------

    /**
     * Returns {@code true} if {@code word} is present in the Trie as a complete word.
     *
     * <p>Time: O(k) | Space: O(1).
     *
     * @param word the word to look up
     * @return {@code true} if found
     */
    public boolean search(String word) {
        TrieNode node = walkTo(word);
        return node != null && node.isEndOfWord;
    }

    // -------------------------------------------------------------------------
    // startsWith
    // -------------------------------------------------------------------------

    /**
     * Returns {@code true} if any word in the Trie starts with {@code prefix}.
     *
     * <p>Time: O(k) | Space: O(1).
     *
     * @param prefix the prefix to check
     * @return {@code true} if at least one word has this prefix
     */
    public boolean startsWith(String prefix) {
        return walkTo(prefix) != null;
    }

    // -------------------------------------------------------------------------
    // Delete
    // -------------------------------------------------------------------------

    /**
     * Deletes {@code word} from the Trie, pruning now-unreachable nodes.
     *
     * <p>Algorithm: walk down marking the path, then walk back up and remove
     * any node whose {@code passCount} reaches zero after decrement.
     *
     * <p>Time: O(k) | Space: O(k) recursive stack.
     *
     * @param word the word to delete
     * @return {@code true} if the word was present and deleted
     */
    public boolean delete(String word) {
        if (!search(word)) return false;
        deleteRec(root, word, 0);
        wordCount--;
        return true;
    }

    /**
     * Returns {@code true} if the child for {@code word.charAt(depth)} should be removed
     * (its {@code passCount} dropped to 0).
     */
    private boolean deleteRec(TrieNode node, String word, int depth) {
        if (depth == word.length()) {
            node.isEndOfWord = false;
            return node.passCount == 0; // prune leaf
        }
        char c = word.charAt(depth);
        TrieNode child = node.children.get(c);
        child.passCount--;
        if (deleteRec(child, word, depth + 1)) {
            node.children.remove(c);
        }
        return !node.isEndOfWord && node.passCount == 0;
    }

    // -------------------------------------------------------------------------
    // getAllWords
    // -------------------------------------------------------------------------

    /**
     * Returns all words stored in the Trie in lexicographic order.
     *
     * <p>Time: O(n * k_avg) | Space: O(n * k_avg).
     *
     * @return sorted list of all words
     */
    public List<String> getAllWords() {
        List<String> result = new ArrayList<>();
        collectWords(root, new StringBuilder(), result);
        return result;
    }

    private void collectWords(TrieNode node, StringBuilder prefix, List<String> result) {
        if (node.isEndOfWord) result.add(prefix.toString());
        for (Map.Entry<Character, TrieNode> entry : node.children.entrySet()) {
            prefix.append(entry.getKey());
            collectWords(entry.getValue(), prefix, result);
            prefix.deleteCharAt(prefix.length() - 1);
        }
    }

    // -------------------------------------------------------------------------
    // Accessors
    // -------------------------------------------------------------------------

    /** Returns the number of distinct words in the Trie. */
    public int wordCount() { return wordCount; }

    // -------------------------------------------------------------------------
    // Helpers
    // -------------------------------------------------------------------------

    /** Walks to the node at the end of {@code s}, returning null if the path doesn't exist. */
    private TrieNode walkTo(String s) {
        TrieNode cur = root;
        for (char c : s.toCharArray()) {
            cur = cur.children.get(c);
            if (cur == null) return null;
        }
        return cur;
    }

    // -------------------------------------------------------------------------
    // toString
    // -------------------------------------------------------------------------

    /**
     * Returns a multi-line string showing the Trie structure as an indented tree.
     *
     * <p>Time: O(n * k_avg) | Space: O(n * k_avg).
     *
     * @return Trie structure string
     */
    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append("Trie (").append(wordCount).append(" words):\n");
        buildString(sb, root, "", "");
        return sb.toString();
    }

    private void buildString(StringBuilder sb, TrieNode node, String label, String indent) {
        sb.append(indent)
          .append(label.isEmpty() ? "(root)" : "'" + label + "'")
          .append(node.isEndOfWord ? " [END]" : "")
          .append("\n");
        List<Map.Entry<Character, TrieNode>> entries = new ArrayList<>(node.children.entrySet());
        for (int i = 0; i < entries.size(); i++) {
            boolean last = (i == entries.size() - 1);
            Map.Entry<Character, TrieNode> e = entries.get(i);
            buildString(sb,
                    e.getValue(),
                    String.valueOf(e.getKey()),
                    indent + (last ? "    " : "│   "));
        }
    }

    // -------------------------------------------------------------------------
    // Main – demo
    // -------------------------------------------------------------------------

    public static void main(String[] args) {
        System.out.println("=== Trie Demo ===\n");

        Trie trie = new Trie();

        // Insert
        String[] words = {"apple", "app", "application", "apply", "apt",
                          "banana", "band", "bandana", "can", "cannot"};
        System.out.println("Inserting words: ");
        for (String w : words) {
            trie.insert(w);
            System.out.print(w + " ");
        }
        System.out.println("\n");
        System.out.println(trie);

        // Search
        System.out.println("search(\"app\")         : " + trie.search("app"));
        System.out.println("search(\"apple\")       : " + trie.search("apple"));
        System.out.println("search(\"ap\")          : " + trie.search("ap"));
        System.out.println("search(\"mango\")       : " + trie.search("mango"));

        // startsWith
        System.out.println("\nstartsWith(\"app\")     : " + trie.startsWith("app"));
        System.out.println("startsWith(\"ban\")     : " + trie.startsWith("ban"));
        System.out.println("startsWith(\"xyz\")     : " + trie.startsWith("xyz"));

        // getAllWords
        System.out.println("\nAll words: " + trie.getAllWords());

        // Delete
        System.out.println("\nDeleting \"app\"...");
        trie.delete("app");
        System.out.println("search(\"app\")   after delete: " + trie.search("app"));
        System.out.println("search(\"apple\") after delete: " + trie.search("apple"));
        System.out.println("All words after delete: " + trie.getAllWords());

        System.out.println("\nDeleting \"apple\"...");
        trie.delete("apple");
        System.out.println("All words after delete: " + trie.getAllWords());
        System.out.println("\nFinal Trie:");
        System.out.println(trie);
    }
}
