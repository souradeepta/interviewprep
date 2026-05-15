# Trie (Prefix Tree)

## Problem Statement

Stores strings with common prefixes. Used in autocomplete and IP routing.

## Design

### Key Concepts

```
Tree of characters. Each node = character, edges = next chars. Leaf = end of word.
```

### Architecture

```
[Visual representation showing architecture]
```

## Architecture Diagram

```
Trie for {cat, car, card, dog}:
      root
     /    \
    c      d
   / \      \
  a   a     o
 / \  |      \
 t r  r      g
 |\  |\     (word)
 * d  d
   *  |\
```

## Common Questions & Answers

**Q: Autocomplete?** A: Start from user input chars, traverse trie, return all leaf words.

**Q: Space complexity?** A: O(ALPHABET_SIZE * N) where N = total chars in all words.

**Q: Prefix queries?** A: O(m) where m = prefix length, returns all matches.

## Back-of-Envelope Calculations

- English vocabulary: 170K words, avg 5 chars = 850K characters
- Trie storage: ~10 bytes/node × 850K = 8.5MB
- Autocomplete lookup: <1ms for typical prefixes

## Design Choice Comparison

| Approach | Pros | Cons |
|----------|------|------|
| Trie | Efficient prefix search | More memory than hash table |
| Hash table + sort | Simple | O(n log n) for prefix queries |
| Prefix tree + cache | Fast with caching | Cache invalidation complexity |

## Follow-up Interview Questions

1. How would you implement this at scale (1M+ operations/sec)?
2. What happens if the [key component] fails?
3. How to ensure [important property] in this system?
4. What's the bottleneck at 10x current scale?
5. How would you monitor and debug [specific aspect]?

## Example Scenario Walkthrough

Scenario: [Concrete example with 5-10 steps showing system in action]

## Implementation

### Python Implementation

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
        node = self._find_node(word)
        return node is not None and node.is_end

    def autocomplete(self, prefix):
        node = self._find_node(prefix)
        if node is None:
            return []
        return self._dfs(node, prefix)

    def _find_node(self, prefix):
        node = self.root
        for char in prefix:
            if char not in node.children:
                return None
            node = node.children[char]
        return node

    def _dfs(self, node, word):
        results = []
        if node.is_end:
            results.append(word)
        for char, child in node.children.items():
            results.extend(self._dfs(child, word + char))
        return results
```

### Java Implementation

```java
class TrieNode {
    Map<Character, TrieNode> children = new HashMap<>();
    boolean isEnd = false;
}

class Trie {
    private TrieNode root = new TrieNode();

    public void insert(String word) {
        TrieNode node = root;
        for (char c : word.toCharArray()) {
            node = node.children.computeIfAbsent(c, k -> new TrieNode());
        }
        node.isEnd = true;
    }

    public boolean search(String word) {
        TrieNode node = findNode(word);
        return node != null && node.isEnd;
    }

    public List<String> autocomplete(String prefix) {
        TrieNode node = findNode(prefix);
        if (node == null) return new ArrayList<>();
        return dfs(node, prefix);
    }

    private TrieNode findNode(String prefix) {
        TrieNode node = root;
        for (char c : prefix.toCharArray()) {
            if (!node.children.containsKey(c)) return null;
            node = node.children.get(c);
        }
        return node;
    }

    private List<String> dfs(TrieNode node, String word) {
        List<String> results = new ArrayList<>();
        if (node.isEnd) results.add(word);
        for (Map.Entry<Character, TrieNode> entry : node.children.entrySet()) {
            results.addAll(dfs(entry.getValue(), word + entry.getKey()));
        }
        return results;
    }
}
```

### Production Considerations

- **Concurrency**: Thread safety and synchronization
- **Error Handling**: Fault tolerance and recovery
- **Monitoring**: Observability and metrics
- **Performance**: Optimization strategies

## Complexity Analysis

| Operation | Complexity | Notes |
|-----------|-----------|-------|
| [Key Op 1] | O(n) | [Explanation] |
| [Key Op 2] | O(log n) | [Explanation] |
| [Key Op 3] | O(1) | [Explanation] |

## Real-world Applications

- Use case 1
- Use case 2
- Use case 3

## Related Concepts

- Concept A (see documentation)
- Concept B (see documentation)
- Concept C (see documentation)

## Further Reading

- Academic papers
- System design references
- Implementation guides
