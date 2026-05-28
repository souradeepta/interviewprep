# Tries (Prefix Trees) — O(m) Operations on String Keys

**Level:** L4-L5
**Time to read:** ~20 min

The data structure for autocomplete, spell-check, and prefix matching. Where hash maps fail on prefix queries, tries excel.

---

## Quick Summary

A trie (prefix tree) stores strings by sharing common prefixes. Each node represents one character; paths from root to end-of-word markers spell out stored strings. Every operation — insert, search, prefix search — takes O(m) where m is the key length, independent of the number of stored strings. Key trade-off: O(ALPHABET × m × n) space vs O(m) time; compressed tries reduce space at code complexity cost.

---

## Operations & Complexity Table

| Operation       | Time    | Space per op | Notes                                     |
|-----------------|---------|-------------|-------------------------------------------|
| Insert          | O(m)    | O(m) new    | m = key length; creates at most m nodes  |
| Search (exact)  | O(m)    | O(1)        | Traverse m levels; check is_end          |
| Prefix search   | O(m)    | O(1)        | Check if path exists; don't need is_end  |
| Delete          | O(m)    | O(1)        | Clear is_end; prune empty branches       |
| List all words  | O(n×m)  | O(n×m)      | DFS from root                            |
| Autocomplete    | O(m+k)  | O(k)        | Navigate to prefix, then DFS for k words |
| Space (total)   | —       | O(A×m×n)    | A=alphabet size, m=avg len, n=num words  |

---

## Memory Layout / Internal Structure

```
Trie storing: ["app", "apple", "apply", "apt", "bat"]

                root
               /    \
              a      b
              |      |
              p      a
             /|      |
            p  t     t (is_end=True: "bat")
            |  |
            l  (is_end=True: "apt")
           / \
          e   y
          |   |
         (T) (T)   T = is_end marker
         "apple" "apply"

         (is_end=True at 'p'→'p'→'p' = "app")

Node structure:
┌─────────────────────────────────────────────────┐
│ children: dict[char → TrieNode]  (or array[26]) │
│ is_end:   bool                                  │
└─────────────────────────────────────────────────┘

Array-based (26 lowercase letters):
  children: [None] × 26
  children[ord('a') - ord('a')] = node_for_a
  Fixed 26 pointers per node; faster but more memory

Dict-based:
  children: {}  (sparse — only stores actual children)
  Lower memory for large alphabets; slightly slower lookup
```

---

## Trade-offs vs Alternatives

| Feature               | Trie          | Hash Map     | Sorted Array  | Ternary Search Tree |
|-----------------------|---------------|--------------|---------------|---------------------|
| Exact lookup          | O(m)          | O(m) hash    | O(m log n)    | O(m)                |
| Prefix search         | O(m)          | O(n×m)       | O(m log n)    | O(m)                |
| Autocomplete (k words)| O(m + k)      | O(n)         | O(m log n+k)  | O(m + k)            |
| Insert                | O(m)          | O(m)         | O(m + n)      | O(m)                |
| Space (n words, len m)| O(A×m×n)      | O(m×n)       | O(m×n)        | O(m×n)              |
| Memory locality       | Poor (ptrs)   | Moderate     | Good          | Better than trie    |
| Wildcard search       | O(A^depth)    | O(n×m)       | O(n×m)        | O(A^depth)          |
| Sorted output         | O(n×m) DFS    | O(n m log n) | O(n×m)        | O(n×m)              |

```
When to choose trie:
┌─────────────────────────────────────────────────────────────────┐
│ Autocomplete / prefix matching?              → Trie             │
│ Many strings sharing common prefixes?        → Trie (shared)   │
│ Spell check (does prefix exist?)?            → Trie             │
│ Simple key-value, no prefix queries?         → Hash Map         │
│ Small dictionary (< 1000 words)?             → Hash Map simpler │
│ Memory critical, compressed needed?          → Radix/DAWG       │
└─────────────────────────────────────────────────────────────────┘
```

---

## When NOT to Use

- **No prefix queries needed** — a hash map gives O(m) lookup with far less code and space.
- **Small dictionary** — the overhead of trie nodes is not worth it for < ~100 words.
- **Memory constrained** — an array-based trie with 26 pointers per node uses 26×8 = 208 bytes per node; a 100k-word trie can use tens of MB. Use a compressed trie (radix tree) or DAWG (Directed Acyclic Word Graph) instead.
- **Unicode or large alphabet** — trie with 100k character alphabet explodes in space; use hash-map-based children (dict trie) or ternary search tree.
- **Sorted iteration is primary operation** — a sorted array beats trie for in-order traversal.

---

## Core Operations (Code)

```python
from typing import Optional

# ── Standard Trie (dict-based children) ──────────────────────────────────────

class TrieNode:
    def __init__(self):
        self.children: dict[str, 'TrieNode'] = {}
        self.is_end: bool = False

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        # O(m) time, O(m) space for new nodes
        node = self.root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        node.is_end = True

    def search(self, word: str) -> bool:
        # O(m) — exact match required
        node = self._traverse(word)
        return node is not None and node.is_end

    def starts_with(self, prefix: str) -> bool:
        # O(m) — prefix match only
        return self._traverse(prefix) is not None

    def _traverse(self, s: str) -> Optional[TrieNode]:
        node = self.root
        for ch in s:
            if ch not in node.children:
                return None
            node = node.children[ch]
        return node

    def delete(self, word: str) -> None:
        # O(m) — mark is_end=False, prune empty branches
        def _delete(node: TrieNode, word: str, depth: int) -> bool:
            if depth == len(word):
                node.is_end = False
                return len(node.children) == 0  # prune if leaf
            ch = word[depth]
            if ch not in node.children:
                return False
            should_delete = _delete(node.children[ch], word, depth + 1)
            if should_delete:
                del node.children[ch]
                return not node.is_end and len(node.children) == 0
            return False
        _delete(self.root, word, 0)

    def autocomplete(self, prefix: str, limit: int = 10) -> list[str]:
        # O(m + k) where k = number of matching words
        node = self._traverse(prefix)
        if node is None:
            return []
        results = []
        self._dfs(node, prefix, results, limit)
        return results

    def _dfs(self, node: TrieNode, current: str,
             results: list[str], limit: int) -> None:
        if len(results) >= limit:
            return
        if node.is_end:
            results.append(current)
        for ch, child in sorted(node.children.items()):  # sorted for alphabetical order
            self._dfs(child, current + ch, results, limit)


# ── Array-based Trie (faster, fixed alphabet) ─────────────────────────────────

class TrieNodeArray:
    def __init__(self):
        self.children = [None] * 26     # one slot per lowercase letter
        self.is_end   = False

class TrieArray:
    def __init__(self):
        self.root = TrieNodeArray()

    def _idx(self, ch: str) -> int:
        return ord(ch) - ord('a')

    def insert(self, word: str) -> None:
        node = self.root
        for ch in word:
            i = self._idx(ch)
            if not node.children[i]:
                node.children[i] = TrieNodeArray()
            node = node.children[i]
        node.is_end = True

    def search(self, word: str) -> bool:
        node = self.root
        for ch in word:
            i = self._idx(ch)
            if not node.children[i]:
                return False
            node = node.children[i]
        return node.is_end
```

---

## 3 Worked Problems

---

### Problem 1 — Implement Trie (LeetCode #208)

**Clarifying Questions**
- Only lowercase English letters? (Yes, a-z)
- Maximum word length? (Up to 2000 characters)
- Can duplicate words be inserted? (Yes — second insert is a no-op; is_end already true)
- Thread-safe required? (No for this problem)

**Brute Force**

Use a hash set — O(1) insert and search but no prefix support.

```python
class TrieBrute:
    def __init__(self):
        self.words = set()
    def insert(self, word):    self.words.add(word)
    def search(self, word):    return word in self.words
    def startsWith(self, prefix):
        return any(w.startswith(prefix) for w in self.words)   # O(n×m) — too slow
```

**Optimal**

```python
class Trie:
    def __init__(self):
        self.root = {}           # use dict as trie (concise interview version)

    def insert(self, word: str) -> None:
        node = self.root
        for ch in word:
            node = node.setdefault(ch, {})
        node['#'] = True         # end-of-word marker

    def search(self, word: str) -> bool:
        node = self.root
        for ch in word:
            if ch not in node: return False
            node = node[ch]
        return '#' in node

    def startsWith(self, prefix: str) -> bool:
        node = self.root
        for ch in prefix:
            if ch not in node: return False
            node = node[ch]
        return True
```

**Edge Cases**
- Insert "apple", search "app" → False (is_end not set at 'p')
- Insert "app", then "apple" → Both found independently
- Search empty string "" → True only if `#` in root (usually not inserted)

**Complexity**
- Time: O(m) per operation, m = word length
- Space: O(A × m × n) total — A=alphabet, m=avg length, n=words

**Follow-ups**
- "Space efficient trie?" → Compressed trie (radix tree): merge single-child chains.
- "Count words with prefix?" → Store count at each node instead of bool.

---

### Problem 2 — Word Search II (LeetCode #212)

**Clarifying Questions**
- Find all words from a dictionary that exist in the board? (Yes)
- Words can go in any direction (not just right/down)? (8 directions — up, down, left, right, diagonals — no, actually just 4)
- Can reuse same cell in one word? (No — each cell used at most once per word)
- Dictionary size? (Up to 10⁴ words, words up to 10 chars)

**Brute Force**

For each word, run DFS from every starting cell — O(W × M×N × 4^L) where W=words, M×N=board, L=word length.

**Optimization**

Build trie from dictionary. DFS from each cell, navigate trie simultaneously — prune when no trie prefix matches.

```python
def find_words(board: list[list[str]], words: list[str]) -> list[str]:
    # Build trie
    root = {}
    for word in words:
        node = root
        for ch in word:
            node = node.setdefault(ch, {})
        node['#'] = word                     # store word at end node

    rows, cols = len(board), len(board[0])
    result = []

    def dfs(node, r, c):
        ch = board[r][c]
        if ch not in node:
            return
        next_node = node[ch]
        if '#' in next_node:
            result.append(next_node.pop('#'))  # found word; pop to avoid duplicates

        board[r][c] = '#'                    # mark visited
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and board[nr][nc] != '#':
                dfs(next_node, nr, nc)
        board[r][c] = ch                     # restore

        # Pruning: remove empty branches from trie
        if not next_node:
            del node[ch]

    for r in range(rows):
        for c in range(cols):
            dfs(root, r, c)

    return result
```

**Edge Cases**
- Same word appears multiple times on board → `pop('#')` prevents duplicate output
- Empty board → no starting cells
- Word not in board → simply not added to result

**Complexity**
- Build trie: O(W × L)
- DFS: O(M × N × 4^L) — but trie pruning dramatically reduces constant
- Space: O(W × L) trie + O(L) recursion stack

**Follow-ups**
- "What if dictionary is updated frequently?" → Rebuild trie on update.
- "Return positions too?" → Store list of paths, not just words.

---

### Problem 3 — Design Add and Search Words (LeetCode #211)

**Clarifying Questions**
- `'.'` in search matches any character? (Yes — wildcard)
- Only lowercase letters and `'.'`? (Yes)
- How many searches vs adds? (Up to 10⁴ each)

**Brute Force**

Store all words, use regex for wildcard search — O(n × m) per search.

**Optimal**

Trie with recursive DFS for wildcard `'.'`.

```python
class WordDictionary:
    def __init__(self):
        self.root = {}

    def addWord(self, word: str) -> None:
        node = self.root
        for ch in word:
            node = node.setdefault(ch, {})
        node['#'] = True

    def search(self, word: str) -> bool:
        return self._search(self.root, word, 0)

    def _search(self, node: dict, word: str, i: int) -> bool:
        if i == len(word):
            return '#' in node
        ch = word[i]
        if ch == '.':
            # Try all children
            return any(
                self._search(child, word, i + 1)
                for key, child in node.items()
                if key != '#'
            )
        else:
            if ch not in node:
                return False
            return self._search(node[ch], word, i + 1)
```

**Edge Cases**
- `search(".")` → True if any single-character word inserted
- `search("...")` → True if any 3-character word exists
- All wildcards → traverses entire trie; worst-case O(n × m)

**Complexity**
- addWord: O(m)
- search (no wildcards): O(m)
- search (all wildcards): O(n × m) where n = number of nodes — exponential in worst case

**Follow-ups**
- "Multiple wildcards in sequence?" → Still handled by recursive DFS; performance degrades.
- "Case-insensitive search?" → Lowercase all inputs on insert and search.

---

## Interview Q&A

**Q1: Trie vs hash map for prefix operations — which is faster?**

A:
```
Hash map prefix check:
  - Must iterate ALL stored keys: O(n × m) worst case
  - No structural prefix sharing
  - O(m) exact lookup, O(n×m) prefix search

Trie:
  - Navigate to prefix in O(m) — independent of n
  - Then enumerate matches in O(k) where k = results
  - Structural prefix sharing reduces memory for common prefixes

Winner: Trie for prefix queries, especially autocomplete with large dictionaries.
Hash map if only exact lookups are needed.
```

---

**Q2: What is a compressed trie (radix tree) and when do you use it?**

A: A compressed trie merges chains of single-child nodes into single edges labeled with substrings. Example: "interview" → "interview" on one edge instead of 9 individual nodes. This reduces space from O(A×m×n) to O(n) nodes (one per stored string, plus splits). Use when: dictionary is large with few shared prefixes, or memory is constrained. Linux kernel's routing table uses a radix tree. Downside: slightly more complex insert/delete logic.

---

**Q3: What is a DAWG and how does it differ from a trie?**

A: A DAWG (Directed Acyclic Word Graph) also shares suffixes in addition to prefixes. A trie only shares prefixes — two words with the same suffix have separate paths from their divergence point. A DAWG merges identical suffixes too, giving minimal state representation. Result: DAWG can be 10-50x more compact than a trie for large dictionaries. Used in spell checkers (e.g., Scrabble word lists). Downside: much harder to construct (requires suffix sharing algorithm).

---

**Q4: What is the space complexity of a trie and how do you optimize it?**

A:
```
Naive trie:
  Array-based nodes: O(A × m × n) where A=alphabet, m=avg key len, n=keys
  For A=26, m=10, n=100K: 26 × 10 × 100K = 26M node slots
  At 8 bytes each: ~200MB — too large for production

Optimizations:
1. Dict-based children: only store actual children (sparse)
   Reduces to O(m × n) actual entries — 10× smaller

2. Compressed trie: merge single-child chains
   Reduces to O(n) nodes

3. DAWG: also share suffixes
   Most compact — often 10-50× smaller than trie

4. Ternary Search Tree (TST):
   Binary-tree-like with three children (< = >)
   Better cache performance than tries
   Space: O(m × n) with good constants
```

---

**Q5: Why is trie lookup O(m) regardless of how many words are stored?**

A: In a trie, each character of the query key navigates exactly one level down the tree. The traversal takes m steps — one per character — regardless of whether the trie stores 10 words or 10 million words. This contrasts with a hash map (which must compute hash of the full key, also O(m)) but is structurally different: the trie traversal naturally answers prefix queries, while the hash map does not.

---

**Q6: How would you implement autocomplete with top-k results?**

A: Augment each trie node with the k most frequent completions (sorted by frequency). On insert, update the completion lists up the path to root. On autocomplete query, navigate to the prefix in O(m) and return the pre-computed top-k list in O(1). Trade-off: O(k) extra space per node, O(m × k) update cost per insert. For production autocomplete (Google Search), trie is backed by inverted index with precomputed top-k per prefix node.

---

**Q7: What are the 3 main use cases for tries in systems design?**

A:
```
1. Autocomplete / type-ahead:
   - Navigate to typed prefix, enumerate completions
   - Google Search: trie + frequency scores per prefix
   - IDE code completion

2. Spell checker / dictionary lookup:
   - startsWith for "did you mean?" suggestions
   - Fast "word exists?" without full scan

3. IP routing (longest prefix match):
   - Binary trie on IP address bits
   - Router: match longest prefix → determine next hop
   - Linux kernel: radix tree for routing table
   - Each level: 0 or 1 (bit of IP address)
```

---

## Interview Tips

- **The dict-based trie shortcut.** Use nested dictionaries with `'#'` as end-of-word marker. It's 15 lines, easy to write under pressure, and works for all three LeetCode problems.
- **Space vs hash map comparison.** "Trie uses O(A × m × n) vs hash map's O(m × n). Trie costs more memory but gains prefix queries." Say this upfront.
- **Wildcard = DFS.** Any wildcard pattern matching in a trie becomes recursive DFS where `'.'` branches to all children. This is the key insight for LeetCode #211.
- **Prune in Word Search II.** Removing trie branches as they're exhausted (`del node[ch]`) is the critical optimization that makes LeetCode #212 fast enough.
- **When to suggest trie.** Any interview problem mentioning "autocomplete", "prefix", "spell check", or "dictionary of words" is a trie signal.
