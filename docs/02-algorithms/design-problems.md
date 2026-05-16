# Design Problems

## LRU Cache
**When to use:** Bounded cache with least-recently-used eviction

**Best DS:** HashMap, Doubly LinkedList

**Key Algorithms:** Get: retrieve and move to front. Put: update or insert, move to front, evict tail if needed

**Example Problems:**
1. "LRU Cache design" → HashMap + doubly linked list. Your repo: `python/advanced/lru_cache.py`. Time: O(1) get/put

---

## LFU Cache
**When to use:** Frequency-based eviction, least-frequently-used policy

**Best DS:** HashMap (key → value/frequency), HashMap (frequency → keys), LinkedList (within frequency)

**Key Algorithms:** Get: increment frequency, move to next frequency list. Put: similar, evict min frequency

**Example Problems:**
1. "LFU Cache design" → Multiple data structures tracking frequency and recency. Your repo: `python/advanced/lfu_cache.py`. Time: O(1) get/put

---

## Trie-Based Design
**When to use:** Prefix matching, autocomplete, dictionary search

**Best DS:** Trie, HashMap (at each node)

**Key Algorithms:** Insert: traverse/create path, mark end of word. Search: traverse, return path existence

**Example Problems:**
1. "Implement Trie" → TreeNode with children map, isEndOfWord flag. Your repo: `python/advanced/trie.py`. Time: O(word_length)
2. "Autocomplete system" → Trie with frequency tracking per node. Time: O(word_length + results)

---

## Custom Data Structure Design
**When to use:** Specialized operations, time-based tracking, randomized access

**Best DS:** Combination of HashMap, Heap, LinkedList, etc.

**Key Algorithms:** Composition: combine multiple DS to achieve all operations efficiently

**Example Problems:**
1. "Time-based key-value store" → HashMap of key → list of (timestamp, value); binary search. Time: O(log n) get, O(1) set

---

See [Master Index](problem-to-pattern-matcher.md) for all 50+ patterns.
