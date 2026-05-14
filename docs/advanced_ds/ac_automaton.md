# Aho-Corasick Automaton

## Overview

The **Aho-Corasick Automaton** is a finite automaton that efficiently searches for multiple patterns in a text simultaneously. Built from a trie of patterns with failure links (similar to KMP's failure function), it processes the text in a single O(n + m + k) pass where n is text length, m is total pattern length, and k is the number of matches.

Invented by Aho and Corasick (1975), it revolutionized multi-pattern matching and is used in antivirus software (scanning for malware signatures), plagiarism detection, DNA sequence analysis, and network intrusion detection systems (NIDS).

Unlike checking patterns one-by-one (which would be O(n·p) for p patterns), Aho-Corasick processes all patterns simultaneously in a single pass, achieving linear time complexity in the text size.

## When to Use

- **Multiple pattern matching**: Simultaneously find occurrences of many patterns in text
- **Antivirus/malware scanning**: Check text against thousands of signatures in one pass
- **DNA sequence analysis**: Find multiple motifs in a genome
- **Plagiarism detection**: Compare text against database of known excerpts
- **Network intrusion detection**: Pattern match multiple attack signatures
- **Not ideal for**: Single pattern (use KMP), very short text (overhead not justified), patterns similar in structure (suffix tree may be better)

## ASCII Visualization

```
Patterns: {"he", "she", "his", "hers"}

AC Automaton Trie:
           root
          / | \
        h   s  (other)
       /|    \
      e i     h
      |       |
      r    (match "she")
     /
    s (match "hers")
   /
 (match "he")

Trie structure is standard; now add failure links:

       root (failure → root)
      / | \
    h   s
   /|    \
  e i     h
  |  |     |
  r  s    (match "she")
 / |
s  (match "hers")

Failure links (shown in dashed):
- from "he" → "e" (suffix match)
- from "hers" → "rs" (not in trie, continue to "s", which fails, continue to root)
- from "his" → "is" (not in trie, continue to "s", which fails, continue to root)
- etc.

Example: Processing text "ushers"
u       → root (no match)
us      → root (no match, failure link from "s")
ush     → root (no match, failure link)
ushe    → "he" (partial match on edge)
usher   → "r" (failure to root-h-e-r)
ushers  → detects "she" and "hers" (both present)
```

## Operations & Complexity

| Operation          | Time Complexity | Space Complexity | Notes |
|-------------------|:---------------:|:----------------:|-------|
| Build automaton    | O(m + σ)        | O(m·σ)           | m = total pattern length, σ = alphabet size |
| Build failure links| O(m)            | O(m)             | BFS from root |
| Search text        | O(n + k)        | O(1)             | n = text length, k = matches |
| Total             | O(m + n + k)    | O(m·σ)           | Multi-pattern matching in linear time |

> Much better than naive O(p·n·m) where p is number of patterns, n is text length, m is pattern length.

## Key Invariants

1. **Trie property**: Root has σ (alphabet size) transitions; internal nodes may have fewer.
2. **Failure link**: Each node has a failure link to the node representing the longest proper suffix.
3. **Match detection**: When reaching a node, check if it's a pattern end or if failure link reaches a pattern end (indicates match).
4. **Dictionary suffix**: Failure link follows a suffix chain; eventually reaches root.
5. **No wrong matches**: The automaton structure ensures all matches are found and no false positives occur.

## Solution Approach Flowchart

```mermaid
flowchart TD
    A["🎯 Problem: Multi-pattern matching in text"] -->|How many patterns?| B{Patterns count}
    B -->|Single pattern| C["✓ Use KMP<br/>O(n + m)"]
    B -->|Multiple patterns| D["✓ Aho-Corasick<br/>O(m + n + k)"]
    D --> E["📋 Step 1: Build trie<br/>from all patterns<br/>O(m)"]
    E --> F["🔗 Step 2: Compute failure links<br/>BFS from root<br/>O(m)"]
    F --> G["▶ Step 3: Process text<br/>character by character"]
    G --> H["🔍 For each character:<br/>follow transitions<br/>or failure links"]
    H --> I{"Current node<br/>pattern end?"}
    I -->|Yes| J["✓ Record match"]
    I -->|No| K["Check failure link<br/>for pattern ends"]
    K --> L{"Failure link<br/>reaches match?"}
    L -->|Yes| M["✓ Record overlapping match"]
    L -->|No| N["Continue"]
    J --> O["Next character"]
    M --> O
    N --> O
    O --> P["⏱ Time: O(n)<br/>Total: O(m + n + k)"]
    
    style A fill:#fff4e6
    style C fill:#e3f2fd
    style D fill:#e3f2fd
    style E fill:#f3e5f5
    style F fill:#f3e5f5
    style G fill:#f3e5f5
    style J fill:#e8f5e9
    style M fill:#e8f5e9
    style P fill:#fff3e0
```

## Pattern Recognition Flowchart

```mermaid
flowchart TD
    A["📊 Analyzing the string problem"] -->|What task?| B{Identify operation}
    B -->|Find patterns in text| C{Multiple or overlapping?}
    C -->|Single pattern| D["❌ Not Aho-Corasick<br/>Use KMP"]
    C -->|Multiple patterns| E["✓ Potential AC match"]
    B -->|Count occurrences| F["✓ AC can count<br/>per-pattern counters"]
    B -->|Real-time scanning| G{Can preprocess?}
    G -->|Yes| H["✓ AC ideal<br/>Precompile automaton<br/>Stream processing"]
    G -->|No streaming| I["❌ Reconsider approach"]
    B -->|Pattern with wildcards| J["⚠ AC needs modification<br/>Consider NFA or regex"]
    B -->|Approximate match| K["❌ Not AC<br/>Use edit distance/Levenshtein"]
    E --> L["✓ Continue with AC"]
    F --> L
    H --> L
    
    style A fill:#fff4e6
    style E fill:#e8f5e9
    style F fill:#e8f5e9
    style H fill:#e8f5e9
    style D fill:#ffebee
    style I fill:#ffebee
    style J fill:#fff3e0
    style K fill:#ffebee
    style L fill:#e3f2fd
```

## AC Automaton Building Flowchart

```mermaid
flowchart TD
    A["🏗 Build AC Automaton"] --> B["Receive pattern set<br/>P = {p1, p2, ...}"]
    B --> C["Step 1: Insert all patterns<br/>into trie"]
    C --> D["Trie[i] = map of chars<br/>to child nodes<br/>O(Σmi)"]
    D --> E["Step 2: Mark pattern ends<br/>is_end[node] = true<br/>for last char of each pattern"]
    E --> F["Step 3: Compute failure links<br/>using BFS"]
    F --> G{"At depth d=1:<br/>First char patterns"}
    G -->|Direct children| H["failure[node] = root<br/>for all first-char nodes"]
    H --> I["At depth d>1:<br/>Process in BFS order"]
    I --> J["For node u with parent p"]
    J --> K["parent_fail = failure[p]"]
    K --> L["Follow parent_fail<br/>until found matching char<br/>or reach root"]
    L --> M{"Found transition<br/>for u's char?"}
    M -->|Yes| N["failure[u] = that node"]
    M -->|No| O["failure[u] = root"]
    N --> P["Continue BFS"]
    O --> P
    P --> Q{"All nodes<br/>processed?"}
    Q -->|No| I
    Q -->|Yes| R["✓ Automaton ready<br/>O(m·σ) space"]
    
    style A fill:#f3e5f5
    style C fill:#f3e5f5
    style E fill:#f3e5f5
    style F fill:#f3e5f5
    style R fill:#e8f5e9
```

## Alternatives & Optimization Flowchart

```mermaid
flowchart TD
    A["🤔 Choosing pattern matching approach"] --> B{Data characteristics?}
    B -->|Single pattern| C{Pattern length?}
    C -->|Short| D["✓ KMP<br/>O(n+m)"]
    C -->|Very short| E["✓ Naive<br/>Overhead not justified"]
    B -->|Multiple patterns| F{Pattern count?}
    F -->|Few 2-5| G{Text size vs pattern?}
    G -->|Small text| H["✓ Use KMP<br/>p times O(n+m)"]
    G -->|Large text| I["✓ AC Automaton<br/>O(n+m+k)"]
    F -->|Many 10+| J{All patterns<br/>in one text?}
    J -->|Yes| K["✓ AC Automaton<br/>One pass"]
    J -->|No streaming| L["✓ AC ideal<br/>Precompile, reuse"]
    B -->|Overlapping analysis| M["✓ AC best<br/>Finds all overlaps"]
    B -->|Edit/fuzzy match| N["❌ Not AC<br/>Use edit distance"]
    
    H --> O["Decision: AC better?"]
    I --> O
    K --> O
    L --> O
    O -->|Yes AC| P["AC Automaton"]
    O -->|No| Q["Alternative method"]
    
    style A fill:#fff4e6
    style P fill:#e8f5e9
    style Q fill:#ffebee
    style K fill:#e3f2fd
    style I fill:#e3f2fd
```

## Common Patterns

1. **Finding All Pattern Occurrences**: Build AC automaton. Process text character-by-character, following transitions and failure links. When a node is reached that represents a pattern end, record the match position. Time: O(m + n + k).

2. **Counting Pattern Occurrences**: Similar to above, but maintain a counter for each pattern. Increment when that pattern's node is reached. Time: O(m + n + k).

3. **Detecting Any Pattern Match**: Early exit when first match is found (e.g., antivirus: "virus detected"). Time: O(m + min(n, position of first match)).

4. **Pattern Matching with Wildcards**: Extend AC automaton with ε-transitions or special handling for wildcard characters. More complex implementation.

## Interview Questions

1. **How does Aho-Corasick differ from checking patterns one-by-one with KMP?** One-by-one: O(p·(n+mᵢ)) where p is pattern count. AC: O(n + Σmᵢ + k) single pass. AC is much faster for many patterns.

2. **What is the failure link, and how is it computed?** Failure link at node u points to the node representing the longest proper suffix of the string represented by u. Computed via BFS: for each node at depth d+1, its failure link is found by following the parent's failure link, then following a transition. Root's failure link points to itself.

3. **Why do you need to check failure links when matching?** When a transition doesn't exist from current node, follow failure link and retry. This ensures all overlapping patterns are found. For example, "she" and "he" in "shers": at "sher", the "he" is found via a failure link from "sher" to "her" to "er" (fail) to "r" (fail) to root-h-e.

4. **Can you handle pattern updates in Aho-Corasick?** Hard. You'd need to rebuild the automaton. AC is designed for static pattern sets. For dynamic patterns, use suffix tree or other structures.

5. **How does AC handle overlapping pattern matches?** When a node is reached, check both if it's a pattern end and if any failure link ancestor is a pattern end. This catches overlaps. For example, "ab" and "abc" overlapping: when "abc" is matched, "ab" is also recorded via failure link from "c".

6. **What's the space complexity, and how can you optimize it?** O(m·σ) for full transition table (m nodes, σ transitions per node). Optimize with: (1) hash map instead of array (sparse transitions), (2) trie compression, (3) suffix tree instead of AC. Most competitive programming solutions use full table.

7. **How does Aho-Corasick relate to regular expressions?** AC handles literal patterns efficiently. For regex, use different automata (e.g., NFA with ε-transitions). Some regex engines use AC as a sub-component for literal pattern matching parts.

## Implementation Notes

- **Trie Construction**: Use arrays (trie[node][char]) or maps. For small alphabets (26 letters), arrays are faster. For large alphabets (unicode), hash maps save space.
- **Failure Link Computation**: BFS-based approach is standard. Use a queue. For each node at depth d+1, traverse parent's failure link chain until you find a node with a transition for the current character.
- **Match Detection**: Maintain an "is_pattern_end" boolean at each node. When processing text, check if current node is a pattern end. Also follow failure links to check if any suffix is a pattern end.
- **Multiple Matches Same Position**: If patterns overlap at the same position, all are found. For example, "aa" and "aaa" both match at position 2 in "aaa".
- **Testing**: Test overlapping patterns, patterns that are prefixes of others, patterns with common suffixes. Verify all k matches are found.

## References

1. Aho, A. V., & Corasick, M. J. (1975). "Efficient string matching: An aid to bibliographic search." *Communications of the ACM*, 18(6), 333-340.
2. Gusfield, D. (1997). *Algorithms on Strings, Trees, and Sequences*. Cambridge University Press.
3. Cormen, T. H., Leiserson, C. E., Rivest, R. L., & Stein, C. (2009). *Introduction to Algorithms* (3rd ed.). MIT Press.
