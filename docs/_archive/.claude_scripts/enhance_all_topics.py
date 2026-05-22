#!/usr/bin/env python3
"""Enhance all system design topics with Python/Java code, calculations, and follow-up questions."""
import os, re, glob

BASE = "docs/system_design"

# ── keyword → (python_code, java_code) ──────────────────────────────────────

def get_code(title: str, dirpath: str) -> tuple[str, str]:
    t = title.lower()
    d = os.path.basename(dirpath)

    # ── CACHING ──
    if any(x in t for x in ["lru", "least recently"]):
        py = '''from collections import OrderedDict
from typing import Optional

class LRUCache:
    """O(1) get/put using OrderedDict for ordering."""
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache: OrderedDict[int, int] = OrderedDict()

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        self.cache.move_to_end(key)   # mark as recently used
        return self.cache[key]

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)  # evict least-recently-used

# Usage
cache = LRUCache(3)
cache.put(1, 10); cache.put(2, 20); cache.put(3, 30)
print(cache.get(1))   # 10, moves 1 to recent
cache.put(4, 40)      # evicts key 2 (LRU)
print(cache.get(2))   # -1 (evicted)'''
        java = '''import java.util.LinkedHashMap;
import java.util.Map;

public class LRUCache {
    private final int capacity;
    // LinkedHashMap with accessOrder=true maintains LRU order
    private final LinkedHashMap<Integer, Integer> cache;

    public LRUCache(int capacity) {
        this.capacity = capacity;
        this.cache = new LinkedHashMap<>(capacity, 0.75f, true) {
            @Override
            protected boolean removeEldestEntry(Map.Entry<Integer, Integer> eldest) {
                return size() > capacity;  // evict when over capacity
            }
        };
    }

    public int get(int key) {
        return cache.getOrDefault(key, -1);
    }

    public void put(int key, int value) {
        cache.put(key, value);
    }

    public static void main(String[] args) {
        LRUCache cache = new LRUCache(3);
        cache.put(1, 10); cache.put(2, 20); cache.put(3, 30);
        System.out.println(cache.get(1)); // 10
        cache.put(4, 40);                 // evicts key 2
        System.out.println(cache.get(2)); // -1
    }
}'''
        return py, java

    if any(x in t for x in ["lfu", "least frequently"]):
        py = '''import heapq
from collections import defaultdict

class LFUCache:
    """O(1) LFU using frequency buckets and min-heap."""
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.key_val: dict[int, int] = {}
        self.key_freq: dict[int, int] = defaultdict(int)
        self.freq_keys: dict[int, set] = defaultdict(set)
        self.min_freq = 0

    def _touch(self, key: int):
        freq = self.key_freq[key]
        self.key_freq[key] += 1
        self.freq_keys[freq].discard(key)
        if not self.freq_keys[freq] and freq == self.min_freq:
            self.min_freq += 1
        self.freq_keys[freq + 1].add(key)

    def get(self, key: int) -> int:
        if key not in self.key_val:
            return -1
        self._touch(key)
        return self.key_val[key]

    def put(self, key: int, value: int):
        if self.capacity == 0:
            return
        if key in self.key_val:
            self.key_val[key] = value
            self._touch(key)
        else:
            if len(self.key_val) >= self.capacity:
                evict = next(iter(self.freq_keys[self.min_freq]))
                self.freq_keys[self.min_freq].discard(evict)
                del self.key_val[evict], self.key_freq[evict]
            self.key_val[key] = value
            self.key_freq[key] = 1
            self.freq_keys[1].add(key)
            self.min_freq = 1'''
        java = '''import java.util.*;

public class LFUCache {
    private final int capacity;
    private int minFreq;
    private final Map<Integer, Integer> keyVal = new HashMap<>();
    private final Map<Integer, Integer> keyFreq = new HashMap<>();
    private final Map<Integer, LinkedHashSet<Integer>> freqKeys = new HashMap<>();

    public LFUCache(int capacity) { this.capacity = capacity; }

    public int get(int key) {
        if (!keyVal.containsKey(key)) return -1;
        touch(key);
        return keyVal.get(key);
    }

    public void put(int key, int value) {
        if (capacity == 0) return;
        if (keyVal.containsKey(key)) { keyVal.put(key, value); touch(key); return; }
        if (keyVal.size() >= capacity) {
            int evict = freqKeys.get(minFreq).iterator().next();
            freqKeys.get(minFreq).remove(evict);
            keyVal.remove(evict); keyFreq.remove(evict);
        }
        keyVal.put(key, value); keyFreq.put(key, 1);
        freqKeys.computeIfAbsent(1, k -> new LinkedHashSet<>()).add(key);
        minFreq = 1;
    }

    private void touch(int key) {
        int f = keyFreq.get(key);
        keyFreq.put(key, f + 1);
        freqKeys.get(f).remove(key);
        if (freqKeys.get(f).isEmpty() && f == minFreq) minFreq++;
        freqKeys.computeIfAbsent(f + 1, k -> new LinkedHashSet<>()).add(key);
    }
}'''
        return py, java

    if any(x in t for x in ["bloom filter", "bloom"]):
        py = '''import mmh3, math
from bitarray import bitarray

class BloomFilter:
    """Space-efficient probabilistic set membership."""
    def __init__(self, n: int, fp_rate: float = 0.01):
        self.m = int(-n * math.log(fp_rate) / (math.log(2) ** 2))
        self.k = int(self.m / n * math.log(2))
        self.bits = bitarray(self.m)
        self.bits.setall(0)

    def add(self, item: str) -> None:
        for seed in range(self.k):
            idx = mmh3.hash(item, seed) % self.m
            self.bits[idx] = 1

    def contains(self, item: str) -> bool:
        """Returns True if item MIGHT be in set; False = definitely not."""
        return all(self.bits[mmh3.hash(item, s) % self.m] for s in range(self.k))

bf = BloomFilter(n=1_000_000, fp_rate=0.01)
bf.add("user:abc123")
print(bf.contains("user:abc123"))   # True (in set)
print(bf.contains("user:xyz999"))   # False (not in set)'''
        java = '''import java.util.BitSet;

public class BloomFilter {
    private final BitSet bits;
    private final int m, k;

    public BloomFilter(int n, double fpRate) {
        this.m = (int) (-n * Math.log(fpRate) / (Math.log(2) * Math.log(2)));
        this.k = (int) (m / n * Math.log(2));
        this.bits = new BitSet(m);
    }

    private int hash(String item, int seed) {
        // MurmurHash simulation using Java hashCode
        int h = item.hashCode() ^ (seed * 0x9e3779b9);
        return Math.abs(h) % m;
    }

    public void add(String item) {
        for (int i = 0; i < k; i++) bits.set(hash(item, i));
    }

    public boolean mightContain(String item) {
        for (int i = 0; i < k; i++) if (!bits.get(hash(item, i))) return false;
        return true;
    }

    public static void main(String[] args) {
        BloomFilter bf = new BloomFilter(1_000_000, 0.01);
        bf.add("user:abc123");
        System.out.println(bf.mightContain("user:abc123")); // true
        System.out.println(bf.mightContain("user:xyz999")); // false
    }
}'''
        return py, java

    # ── SORTING / ALGORITHMS ──
    if "merge sort" in t or ("merge" in t and "sort" in t):
        py = '''from typing import TypeVar, List
T = TypeVar("T")

def merge_sort(arr: List[int]) -> List[int]:
    """O(n log n) stable sort via divide-and-conquer."""
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left  = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return merge(left, right)

def merge(left: List[int], right: List[int]) -> List[int]:
    result, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:   # stable: equal elements keep order
            result.append(left[i]); i += 1
        else:
            result.append(right[j]); j += 1
    return result + left[i:] + right[j:]

arr = [38, 27, 43, 3, 9, 82, 10]
print(merge_sort(arr))  # [3, 9, 10, 27, 38, 43, 82]'''
        java = '''import java.util.Arrays;

public class MergeSort {
    public static void mergeSort(int[] arr, int left, int right) {
        if (left >= right) return;
        int mid = left + (right - left) / 2;
        mergeSort(arr, left, mid);
        mergeSort(arr, mid + 1, right);
        merge(arr, left, mid, right);
    }

    private static void merge(int[] arr, int left, int mid, int right) {
        int[] temp = Arrays.copyOfRange(arr, left, right + 1);
        int i = 0, j = mid - left + 1, k = left;
        while (i <= mid - left && j <= right - left)
            arr[k++] = temp[i] <= temp[j] ? temp[i++] : temp[j++];
        while (i <= mid - left) arr[k++] = temp[i++];
        while (j <= right - left) arr[k++] = temp[j++];
    }

    public static void main(String[] args) {
        int[] arr = {38, 27, 43, 3, 9, 82, 10};
        mergeSort(arr, 0, arr.length - 1);
        System.out.println(Arrays.toString(arr)); // [3, 9, 10, 27, 38, 43, 82]
    }
}'''
        return py, java

    if "quick" in t and "sort" in t:
        py = '''import random
from typing import List

def quicksort(arr: List[int], lo: int = 0, hi: int = -1) -> None:
    """In-place O(n log n) average, O(n²) worst. Random pivot avoids worst case."""
    if hi == -1:
        hi = len(arr) - 1
    if lo >= hi:
        return
    pivot_idx = partition(arr, lo, hi)
    quicksort(arr, lo, pivot_idx - 1)
    quicksort(arr, pivot_idx + 1, hi)

def partition(arr: List[int], lo: int, hi: int) -> int:
    rand_idx = random.randint(lo, hi)      # random pivot → O(n log n) expected
    arr[rand_idx], arr[hi] = arr[hi], arr[rand_idx]
    pivot = arr[hi]
    i = lo - 1
    for j in range(lo, hi):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[hi] = arr[hi], arr[i + 1]
    return i + 1

arr = [10, 7, 8, 9, 1, 5]
quicksort(arr)
print(arr)  # [1, 5, 7, 8, 9, 10]'''
        java = '''import java.util.Arrays;
import java.util.Random;

public class QuickSort {
    private static final Random rand = new Random();

    public static void quickSort(int[] arr, int lo, int hi) {
        if (lo >= hi) return;
        int pivot = partition(arr, lo, hi);
        quickSort(arr, lo, pivot - 1);
        quickSort(arr, pivot + 1, hi);
    }

    private static int partition(int[] arr, int lo, int hi) {
        int randIdx = lo + rand.nextInt(hi - lo + 1);
        swap(arr, randIdx, hi);  // random pivot
        int pivot = arr[hi], i = lo - 1;
        for (int j = lo; j < hi; j++)
            if (arr[j] <= pivot) swap(arr, ++i, j);
        swap(arr, i + 1, hi);
        return i + 1;
    }

    private static void swap(int[] arr, int a, int b) {
        int t = arr[a]; arr[a] = arr[b]; arr[b] = t;
    }

    public static void main(String[] args) {
        int[] arr = {10, 7, 8, 9, 1, 5};
        quickSort(arr, 0, arr.length - 1);
        System.out.println(Arrays.toString(arr)); // [1, 5, 7, 8, 9, 10]
    }
}'''
        return py, java

    if any(x in t for x in ["binary search"]):
        py = '''from typing import List, Optional

def binary_search(arr: List[int], target: int) -> int:
    """O(log n) search on sorted array. Returns index or -1."""
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = lo + (hi - lo) // 2     # avoids integer overflow
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            lo = mid + 1              # target in right half
        else:
            hi = mid - 1             # target in left half
    return -1

def lower_bound(arr: List[int], target: int) -> int:
    """First index where arr[i] >= target."""
    lo, hi = 0, len(arr)
    while lo < hi:
        mid = (lo + hi) // 2
        if arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid
    return lo

nums = [1, 3, 5, 7, 9, 11, 13]
print(binary_search(nums, 7))    # 3
print(binary_search(nums, 6))    # -1
print(lower_bound(nums, 6))      # 3 (first element >= 6)'''
        java = '''public class BinarySearch {
    /** Returns index of target, or -1 if not found. O(log n). */
    public static int search(int[] arr, int target) {
        int lo = 0, hi = arr.length - 1;
        while (lo <= hi) {
            int mid = lo + (hi - lo) / 2;  // prevents overflow
            if (arr[mid] == target) return mid;
            else if (arr[mid] < target) lo = mid + 1;
            else hi = mid - 1;
        }
        return -1;
    }

    /** First index where arr[i] >= target. */
    public static int lowerBound(int[] arr, int target) {
        int lo = 0, hi = arr.length;
        while (lo < hi) {
            int mid = (lo + hi) / 2;
            if (arr[mid] < target) lo = mid + 1;
            else hi = mid;
        }
        return lo;
    }

    public static void main(String[] args) {
        int[] nums = {1, 3, 5, 7, 9, 11, 13};
        System.out.println(search(nums, 7));      // 3
        System.out.println(search(nums, 6));      // -1
        System.out.println(lowerBound(nums, 6));  // 3
    }
}'''
        return py, java

    if "bfs" in t or ("breadth" in t and "search" in t):
        py = '''from collections import deque
from typing import Optional, Dict, List

def bfs(graph: Dict[int, List[int]], start: int) -> List[int]:
    """BFS traversal — shortest path in unweighted graph."""
    visited, queue, order = {start}, deque([start]), []
    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    return order

def shortest_path(graph: Dict[int, List[int]], src: int, dst: int) -> int:
    """Returns minimum hops src → dst, -1 if unreachable."""
    visited, queue = {src}, deque([(src, 0)])
    while queue:
        node, dist = queue.popleft()
        if node == dst:
            return dist
        for nb in graph.get(node, []):
            if nb not in visited:
                visited.add(nb); queue.append((nb, dist + 1))
    return -1

g = {1: [2, 3], 2: [4, 5], 3: [6], 4: [], 5: [], 6: []}
print(bfs(g, 1))                  # [1, 2, 3, 4, 5, 6]
print(shortest_path(g, 1, 6))     # 2'''
        java = '''import java.util.*;

public class BFS {
    public static List<Integer> bfs(Map<Integer, List<Integer>> graph, int start) {
        List<Integer> order = new ArrayList<>();
        Set<Integer> visited = new HashSet<>();
        Queue<Integer> queue = new LinkedList<>();
        queue.add(start); visited.add(start);
        while (!queue.isEmpty()) {
            int node = queue.poll();
            order.add(node);
            for (int nb : graph.getOrDefault(node, Collections.emptyList()))
                if (visited.add(nb)) queue.add(nb);  // add returns false if already present
        }
        return order;
    }

    public static int shortestPath(Map<Integer, List<Integer>> graph, int src, int dst) {
        Queue<int[]> queue = new LinkedList<>();  // [node, distance]
        Set<Integer> visited = new HashSet<>();
        queue.add(new int[]{src, 0}); visited.add(src);
        while (!queue.isEmpty()) {
            int[] curr = queue.poll();
            if (curr[0] == dst) return curr[1];
            for (int nb : graph.getOrDefault(curr[0], Collections.emptyList()))
                if (visited.add(nb)) queue.add(new int[]{nb, curr[1] + 1});
        }
        return -1;
    }
}'''
        return py, java

    if "dfs" in t or ("depth" in t and "search" in t):
        py = '''from typing import Dict, List, Set

def dfs_iterative(graph: Dict[int, List[int]], start: int) -> List[int]:
    """Iterative DFS — avoids recursion limit on large graphs."""
    visited, stack, order = set(), [start], []
    while stack:
        node = stack.pop()
        if node in visited:
            continue
        visited.add(node)
        order.append(node)
        for nb in reversed(graph.get(node, [])):   # reversed to maintain left-first order
            if nb not in visited:
                stack.append(nb)
    return order

def has_cycle(graph: Dict[int, List[int]], n: int) -> bool:
    """Detect cycle in directed graph using DFS coloring."""
    WHITE, GRAY, BLACK = 0, 1, 2
    color = [WHITE] * n

    def dfs(u: int) -> bool:
        color[u] = GRAY          # in current path
        for v in graph.get(u, []):
            if color[v] == GRAY: return True   # back edge = cycle
            if color[v] == WHITE and dfs(v): return True
        color[u] = BLACK         # fully explored
        return False

    return any(color[i] == WHITE and dfs(i) for i in range(n))

g = {0: [1, 2], 1: [3], 2: [3], 3: []}
print(dfs_iterative(g, 0))   # [0, 1, 3, 2]
print(has_cycle(g, 4))       # False'''
        java = '''import java.util.*;

public class DFS {
    public static List<Integer> dfs(Map<Integer, List<Integer>> graph, int start) {
        List<Integer> order = new ArrayList<>();
        Set<Integer> visited = new HashSet<>();
        Deque<Integer> stack = new ArrayDeque<>();
        stack.push(start);
        while (!stack.isEmpty()) {
            int node = stack.pop();
            if (!visited.add(node)) continue;
            order.add(node);
            List<Integer> neighbors = graph.getOrDefault(node, Collections.emptyList());
            // push in reverse to process left-first
            ListIterator<Integer> it = neighbors.listIterator(neighbors.size());
            while (it.hasPrevious()) {
                int nb = it.previous();
                if (!visited.contains(nb)) stack.push(nb);
            }
        }
        return order;
    }
}'''
        return py, java

    if "dijkstra" in t:
        py = '''import heapq
from typing import Dict, List, Tuple

def dijkstra(graph: Dict[int, List[Tuple[int,int]]], src: int) -> Dict[int, int]:
    """Dijkstra's shortest path. graph[u] = [(v, weight), ...]. O((V+E) log V)."""
    dist: Dict[int, int] = {src: 0}
    heap: List[Tuple[int, int]] = [(0, src)]  # (cost, node)
    while heap:
        cost, u = heapq.heappop(heap)
        if cost > dist.get(u, float("inf")):
            continue    # stale entry
        for v, w in graph.get(u, []):
            new_cost = cost + w
            if new_cost < dist.get(v, float("inf")):
                dist[v] = new_cost
                heapq.heappush(heap, (new_cost, v))
    return dist

# Example: 5-node weighted graph
graph = {0: [(1,4),(2,1)], 1: [(3,1)], 2: [(1,2),(3,5)], 3: [(4,3)], 4: []}
print(dijkstra(graph, 0))  # {0:0, 1:3, 2:1, 3:4, 4:7}'''
        java = '''import java.util.*;

public class Dijkstra {
    public static int[] dijkstra(List<int[]>[] graph, int src) {
        int n = graph.length;
        int[] dist = new int[n];
        Arrays.fill(dist, Integer.MAX_VALUE);
        dist[src] = 0;
        // PriorityQueue: [cost, node]
        PriorityQueue<int[]> pq = new PriorityQueue<>(Comparator.comparingInt(a -> a[0]));
        pq.offer(new int[]{0, src});
        while (!pq.isEmpty()) {
            int[] curr = pq.poll();
            int cost = curr[0], u = curr[1];
            if (cost > dist[u]) continue;  // stale
            for (int[] edge : graph[u]) {
                int v = edge[0], w = edge[1];
                if (dist[u] + w < dist[v]) {
                    dist[v] = dist[u] + w;
                    pq.offer(new int[]{dist[v], v});
                }
            }
        }
        return dist;
    }
}'''
        return py, java

    if "trie" in t:
        py = '''class TrieNode:
    def __init__(self):
        self.children: dict[str, "TrieNode"] = {}
        self.is_end = False

class Trie:
    """Prefix tree. O(m) insert/search where m = word length."""
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        node = self.root
        for ch in word:
            node = node.children.setdefault(ch, TrieNode())
        node.is_end = True

    def search(self, word: str) -> bool:
        node = self.root
        for ch in word:
            if ch not in node.children:
                return False
            node = node.children[ch]
        return node.is_end

    def starts_with(self, prefix: str) -> bool:
        node = self.root
        for ch in prefix:
            if ch not in node.children:
                return False
            node = node.children[ch]
        return True

trie = Trie()
for w in ["apple", "app", "application"]:
    trie.insert(w)
print(trie.search("app"))         # True
print(trie.starts_with("appl"))   # True
print(trie.search("apply"))       # False'''
        java = '''import java.util.HashMap;
import java.util.Map;

public class Trie {
    private static class Node {
        Map<Character, Node> children = new HashMap<>();
        boolean isEnd;
    }

    private final Node root = new Node();

    public void insert(String word) {
        Node cur = root;
        for (char c : word.toCharArray())
            cur = cur.children.computeIfAbsent(c, k -> new Node());
        cur.isEnd = true;
    }

    public boolean search(String word) {
        Node cur = root;
        for (char c : word.toCharArray()) {
            cur = cur.children.get(c);
            if (cur == null) return false;
        }
        return cur.isEnd;
    }

    public boolean startsWith(String prefix) {
        Node cur = root;
        for (char c : prefix.toCharArray()) {
            cur = cur.children.get(c);
            if (cur == null) return false;
        }
        return true;
    }
}'''
        return py, java

    # ── DYNAMIC PROGRAMMING ──
    if "dynamic programming" in t or t in ["edit distance", "lcs", "coin change", "knapsack"]:
        py = '''# Classic DP examples

def longest_common_subsequence(s1: str, s2: str) -> int:
    """O(m*n) DP for LCS length."""
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i-1] == s2[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1       # characters match
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])  # skip one
    return dp[m][n]

def coin_change(coins: list[int], amount: int) -> int:
    """Min coins to make amount. O(amount * len(coins))."""
    dp = [float("inf")] * (amount + 1)
    dp[0] = 0
    for coin in coins:
        for a in range(coin, amount + 1):
            dp[a] = min(dp[a], dp[a - coin] + 1)
    return dp[amount] if dp[amount] != float("inf") else -1

print(longest_common_subsequence("abcde", "ace"))  # 3
print(coin_change([1, 5, 11], 15))                 # 3 (5+5+5)'''
        java = '''public class DynamicProgramming {

    // Longest Common Subsequence
    public static int lcs(String s1, String s2) {
        int m = s1.length(), n = s2.length();
        int[][] dp = new int[m + 1][n + 1];
        for (int i = 1; i <= m; i++)
            for (int j = 1; j <= n; j++)
                dp[i][j] = s1.charAt(i-1) == s2.charAt(j-1)
                    ? dp[i-1][j-1] + 1
                    : Math.max(dp[i-1][j], dp[i][j-1]);
        return dp[m][n];
    }

    // Coin change — minimum coins to reach amount
    public static int coinChange(int[] coins, int amount) {
        int[] dp = new int[amount + 1];
        java.util.Arrays.fill(dp, Integer.MAX_VALUE);
        dp[0] = 0;
        for (int coin : coins)
            for (int a = coin; a <= amount; a++)
                if (dp[a - coin] != Integer.MAX_VALUE)
                    dp[a] = Math.min(dp[a], dp[a - coin] + 1);
        return dp[amount] == Integer.MAX_VALUE ? -1 : dp[amount];
    }

    public static void main(String[] args) {
        System.out.println(lcs("abcde", "ace"));        // 3
        System.out.println(coinChange(new int[]{1,5,11}, 15)); // 3
    }
}'''
        return py, java

    # ── MESSAGING / KAFKA / STREAMING ──
    if any(x in t for x in ["kafka", "producer", "consumer", "message queue", "messaging"]):
        py = '''from kafka import KafkaProducer, KafkaConsumer
import json, time
from typing import Any

class EventProducer:
    """Kafka producer with serialization and retry."""
    def __init__(self, bootstrap_servers: str = "localhost:9092"):
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode(),
            key_serializer=lambda k: k.encode() if k else None,
            acks="all",                  # wait for all replicas
            retries=3,
            batch_size=16384,            # 16KB batch
            linger_ms=5,                 # wait 5ms to batch
        )

    def send(self, topic: str, key: str, event: dict[str, Any]) -> None:
        future = self.producer.send(topic, key=key, value=event)
        record = future.get(timeout=10)  # block until acknowledged
        print(f"Sent to {record.topic}:{record.partition}@{record.offset}")

class EventConsumer:
    """Kafka consumer with manual offset commit for reliability."""
    def __init__(self, topics: list[str], group_id: str):
        self.consumer = KafkaConsumer(
            *topics,
            bootstrap_servers="localhost:9092",
            group_id=group_id,
            auto_offset_reset="earliest",
            enable_auto_commit=False,    # manual commit for at-least-once
            value_deserializer=lambda m: json.loads(m.decode()),
        )

    def run(self) -> None:
        for msg in self.consumer:
            try:
                self.process(msg.value)
                self.consumer.commit()   # commit only after successful processing
            except Exception as e:
                print(f"Failed: {e}")   # dead-letter queue in production

    def process(self, event: dict) -> None:
        print(f"Processing: {event}")'''
        java = '''import org.apache.kafka.clients.producer.*;
import org.apache.kafka.clients.consumer.*;
import java.util.*;

public class KafkaExample {

    // ── Producer ────────────────────────────────────────────────────────────
    public static KafkaProducer<String, String> createProducer() {
        Properties props = new Properties();
        props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
        props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG,
                  "org.apache.kafka.common.serialization.StringSerializer");
        props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG,
                  "org.apache.kafka.common.serialization.StringSerializer");
        props.put(ProducerConfig.ACKS_CONFIG, "all");      // durability
        props.put(ProducerConfig.RETRIES_CONFIG, 3);
        return new KafkaProducer<>(props);
    }

    public static void sendEvent(KafkaProducer<String, String> producer,
                                  String topic, String key, String value) {
        ProducerRecord<String, String> record = new ProducerRecord<>(topic, key, value);
        producer.send(record, (metadata, ex) -> {
            if (ex != null) ex.printStackTrace();
            else System.out.printf("Sent %s:%d@%d%n",
                    metadata.topic(), metadata.partition(), metadata.offset());
        });
    }

    // ── Consumer ────────────────────────────────────────────────────────────
    public static KafkaConsumer<String, String> createConsumer(String groupId) {
        Properties props = new Properties();
        props.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
        props.put(ConsumerConfig.GROUP_ID_CONFIG, groupId);
        props.put(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "earliest");
        props.put(ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG, false); // manual commit
        props.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG,
                  "org.apache.kafka.common.serialization.StringDeserializer");
        props.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG,
                  "org.apache.kafka.common.serialization.StringDeserializer");
        return new KafkaConsumer<>(props);
    }
}'''
        return py, java

    # ── DISTRIBUTED / CONSENSUS ──
    if any(x in t for x in ["raft", "consensus", "leader election", "paxos"]):
        py = '''import threading, time, random
from enum import Enum

class State(Enum):
    FOLLOWER = "follower"
    CANDIDATE = "candidate"
    LEADER = "leader"

class RaftNode:
    """Simplified Raft node demonstrating leader election."""
    def __init__(self, node_id: int, peers: list[int]):
        self.id = node_id
        self.peers = peers
        self.state = State.FOLLOWER
        self.current_term = 0
        self.voted_for: int | None = None
        self.last_heartbeat = time.time()
        self.election_timeout = random.uniform(0.15, 0.3)  # 150-300ms

    def check_election_timeout(self) -> bool:
        """Returns True if leader is suspected dead."""
        return time.time() - self.last_heartbeat > self.election_timeout

    def request_vote(self, term: int, candidate_id: int) -> bool:
        """Grant vote if term is newer and we haven't voted this term."""
        if term > self.current_term:
            self.current_term = term
            self.voted_for = None
            self.state = State.FOLLOWER
        grant = term == self.current_term and (
            self.voted_for is None or self.voted_for == candidate_id
        )
        if grant:
            self.voted_for = candidate_id
        return grant

    def become_leader(self) -> None:
        self.state = State.LEADER
        print(f"Node {self.id} elected leader for term {self.current_term}")'''
        java = '''import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;

public class RaftNode {
    public enum State { FOLLOWER, CANDIDATE, LEADER }

    private final int nodeId;
    private final AtomicInteger currentTerm = new AtomicInteger(0);
    private final AtomicReference<State> state = new AtomicReference<>(State.FOLLOWER);
    private volatile Integer votedFor = null;
    private volatile long lastHeartbeat = System.currentTimeMillis();
    private final long electionTimeoutMs;

    public RaftNode(int nodeId) {
        this.nodeId = nodeId;
        // randomized timeout 150-300ms to prevent split votes
        this.electionTimeoutMs = 150 + (long)(Math.random() * 150);
    }

    public boolean isElectionTimeout() {
        return System.currentTimeMillis() - lastHeartbeat > electionTimeoutMs;
    }

    public synchronized boolean requestVote(int term, int candidateId) {
        if (term > currentTerm.get()) {
            currentTerm.set(term);
            votedFor = null;
            state.set(State.FOLLOWER);
        }
        boolean grant = term == currentTerm.get()
            && (votedFor == null || votedFor == candidateId);
        if (grant) votedFor = candidateId;
        return grant;
    }

    public void receiveHeartbeat(int term) {
        if (term >= currentTerm.get()) {
            currentTerm.set(term);
            state.set(State.FOLLOWER);
            lastHeartbeat = System.currentTimeMillis();
        }
    }
}'''
        return py, java

    # ── REDIS / DISTRIBUTED CACHE ──
    if any(x in t for x in ["redis", "distributed cache", "memcached"]):
        py = '''import redis
import json
import time
from functools import wraps
from typing import Any, Callable, TypeVar

r = redis.Redis(host="localhost", port=6379, decode_responses=True)

def cache(ttl: int = 300):
    """Decorator: cache function results in Redis."""
    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        def wrapper(*args, **kwargs):
            key = f"{fn.__name__}:{args}:{kwargs}"
            cached = r.get(key)
            if cached:
                return json.loads(cached)
            result = fn(*args, **kwargs)
            r.setex(key, ttl, json.dumps(result))
            return result
        return wrapper
    return decorator

@cache(ttl=60)
def get_user_profile(user_id: int) -> dict:
    """Simulates DB fetch, result cached for 60s."""
    return {"id": user_id, "name": "Alice", "ts": time.time()}

# Rate limiting using Redis sliding window
def is_rate_limited(user_id: str, limit: int = 100, window: int = 60) -> bool:
    key = f"rate:{user_id}"
    pipe = r.pipeline()
    now = time.time()
    pipe.zremrangebyscore(key, 0, now - window)  # remove old requests
    pipe.zadd(key, {str(now): now})              # add current request
    pipe.zcard(key)                              # count in window
    pipe.expire(key, window)
    _, _, count, _ = pipe.execute()
    return count > limit'''
        java = '''import redis.clients.jedis.Jedis;
import redis.clients.jedis.JedisPool;
import redis.clients.jedis.Pipeline;
import com.google.gson.Gson;

public class RedisCache {
    private final JedisPool pool;
    private final Gson gson = new Gson();

    public RedisCache(String host, int port) {
        this.pool = new JedisPool(host, port);
    }

    /** Store object in Redis with TTL. */
    public <T> void set(String key, T value, int ttlSeconds) {
        try (Jedis jedis = pool.getResource()) {
            jedis.setex(key, ttlSeconds, gson.toJson(value));
        }
    }

    /** Retrieve typed object from Redis. */
    public <T> T get(String key, Class<T> type) {
        try (Jedis jedis = pool.getResource()) {
            String json = jedis.get(key);
            return json == null ? null : gson.fromJson(json, type);
        }
    }

    /** Sliding window rate limit. Returns true if request should be blocked. */
    public boolean isRateLimited(String userId, int limit, int windowSecs) {
        try (Jedis jedis = pool.getResource()) {
            String key = "rate:" + userId;
            long now = System.currentTimeMillis();
            Pipeline pipe = jedis.pipelined();
            pipe.zremrangeByScore(key, 0, now - windowSecs * 1000L);
            pipe.zadd(key, now, String.valueOf(now));
            var countResp = pipe.zcard(key);
            pipe.expire(key, windowSecs);
            pipe.sync();
            return countResp.get() > limit;
        }
    }
}'''
        return py, java

    # ── KUBERNETES / CONTAINERS ──
    if any(x in t for x in ["kubernetes", "k8s", "pod", "deployment", "statefulset", "daemonset", "helm", "container"]):
        py = '''from kubernetes import client, config
from typing import Optional

def create_deployment(name: str, image: str, replicas: int = 3,
                       namespace: str = "default") -> None:
    """Create a Kubernetes Deployment programmatically."""
    config.load_incluster_config()  # use in-cluster config when running in pod
    apps_v1 = client.AppsV1Api()

    container = client.V1Container(
        name=name,
        image=image,
        resources=client.V1ResourceRequirements(
            requests={"cpu": "100m", "memory": "128Mi"},
            limits={"cpu": "500m", "memory": "512Mi"},
        ),
        liveness_probe=client.V1Probe(
            http_get=client.V1HTTPGetAction(path="/health", port=8080),
            initial_delay_seconds=10,
            period_seconds=5,
        ),
    )

    spec = client.V1DeploymentSpec(
        replicas=replicas,
        selector=client.V1LabelSelector(match_labels={"app": name}),
        template=client.V1PodTemplateSpec(
            metadata=client.V1ObjectMeta(labels={"app": name}),
            spec=client.V1PodSpec(containers=[container]),
        ),
        strategy=client.V1DeploymentStrategy(
            type="RollingUpdate",
            rolling_update=client.V1RollingUpdateDeployment(
                max_unavailable=0,     # zero downtime
                max_surge=1,
            ),
        ),
    )

    deployment = client.V1Deployment(
        metadata=client.V1ObjectMeta(name=name),
        spec=spec,
    )
    apps_v1.create_namespaced_deployment(namespace, deployment)
    print(f"Deployment {name} created with {replicas} replicas")

def scale_deployment(name: str, replicas: int, namespace: str = "default") -> None:
    config.load_incluster_config()
    apps_v1 = client.AppsV1Api()
    patch = {"spec": {"replicas": replicas}}
    apps_v1.patch_namespaced_deployment_scale(name, namespace, patch)'''
        java = '''import io.kubernetes.client.openapi.ApiClient;
import io.kubernetes.client.openapi.Configuration;
import io.kubernetes.client.openapi.apis.AppsV1Api;
import io.kubernetes.client.openapi.models.*;
import io.kubernetes.client.util.Config;
import java.util.*;

public class KubernetesClient {

    public static void createDeployment(String name, String image, int replicas) throws Exception {
        ApiClient apiClient = Config.fromCluster(); // in-cluster config
        Configuration.setDefaultApiClient(apiClient);
        AppsV1Api appsApi = new AppsV1Api();

        V1Container container = new V1Container()
            .name(name)
            .image(image)
            .resources(new V1ResourceRequirements()
                .putRequestsItem("cpu", new io.kubernetes.client.custom.Quantity("100m"))
                .putRequestsItem("memory", new io.kubernetes.client.custom.Quantity("128Mi"))
                .putLimitsItem("cpu", new io.kubernetes.client.custom.Quantity("500m"))
                .putLimitsItem("memory", new io.kubernetes.client.custom.Quantity("512Mi")));

        V1Deployment deployment = new V1Deployment()
            .metadata(new V1ObjectMeta().name(name))
            .spec(new V1DeploymentSpec()
                .replicas(replicas)
                .selector(new V1LabelSelector().matchLabels(Map.of("app", name)))
                .template(new V1PodTemplateSpec()
                    .metadata(new V1ObjectMeta().labels(Map.of("app", name)))
                    .spec(new V1PodSpec().containers(List.of(container))))
                .strategy(new V1DeploymentStrategy().type("RollingUpdate")
                    .rollingUpdate(new V1RollingUpdateDeployment()
                        .maxUnavailable(new IntOrString(0))
                        .maxSurge(new IntOrString(1)))));

        appsApi.createNamespacedDeployment("default", deployment, null, null, null, null);
        System.out.println("Deployment " + name + " created");
    }
}'''
        return py, java

    # ── NETWORKING ──
    if any(x in t for x in ["http", "tcp", "dns", "load balanc", "cdn", "grpc", "websocket", "api gateway"]):
        py = '''import asyncio
import aiohttp
from typing import Optional
import time

class HTTPClient:
    """Async HTTP client with retry, timeout, and connection pooling."""
    def __init__(self, base_url: str, timeout: int = 5, max_retries: int = 3):
        self.base_url = base_url
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.max_retries = max_retries
        self._session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        connector = aiohttp.TCPConnector(limit=100, limit_per_host=30)
        self._session = aiohttp.ClientSession(
            base_url=self.base_url,
            timeout=self.timeout,
            connector=connector,
        )
        return self

    async def __aexit__(self, *args):
        await self._session.close()

    async def get(self, path: str, **kwargs) -> dict:
        for attempt in range(self.max_retries):
            try:
                async with self._session.get(path, **kwargs) as resp:
                    resp.raise_for_status()
                    return await resp.json()
            except aiohttp.ClientError as e:
                if attempt == self.max_retries - 1:
                    raise
                wait = 2 ** attempt        # exponential backoff
                await asyncio.sleep(wait)

async def main():
    async with HTTPClient("https://api.example.com") as client:
        data = await client.get("/users/123")
        print(data)

asyncio.run(main())'''
        java = '''import java.net.URI;
import java.net.http.*;
import java.time.Duration;
import java.util.concurrent.CompletableFuture;

public class HttpClientExample {
    private static final HttpClient client = HttpClient.newBuilder()
        .connectTimeout(Duration.ofSeconds(5))
        .version(HttpClient.Version.HTTP_2)
        .build();

    /** Async GET with JSON parsing. */
    public static CompletableFuture<String> getAsync(String url) {
        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create(url))
            .timeout(Duration.ofSeconds(10))
            .header("Accept", "application/json")
            .GET()
            .build();
        return client.sendAsync(request, HttpResponse.BodyHandlers.ofString())
            .thenApply(HttpResponse::body);
    }

    /** POST JSON payload. */
    public static HttpResponse<String> postJson(String url, String json) throws Exception {
        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create(url))
            .header("Content-Type", "application/json")
            .POST(HttpRequest.BodyPublishers.ofString(json))
            .build();
        return client.send(request, HttpResponse.BodyHandlers.ofString());
    }

    public static void main(String[] args) throws Exception {
        // Async GET
        getAsync("https://api.example.com/users/1")
            .thenAccept(body -> System.out.println("Response: " + body))
            .join();

        // Sync POST
        String payload = "{\"name\":\"Alice\",\"email\":\"alice@example.com\"}";
        HttpResponse<String> resp = postJson("https://api.example.com/users", payload);
        System.out.println("Status: " + resp.statusCode());
    }
}'''
        return py, java

    # ── DATABASE / INTERNALS ──
    if any(x in t for x in ["btree", "b-tree", "lsm", "index", "transaction", "mvcc", "query", "database", "sql"]):
        py = '''import sqlite3
import contextlib
from typing import Generator, Any
from dataclasses import dataclass

@dataclass
class User:
    id: int
    email: str
    name: str

class UserRepository:
    """Repository with connection pooling, parameterized queries, and transactions."""
    def __init__(self, db_path: str = ":memory:"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._create_schema()

    def _create_schema(self) -> None:
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id    INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT    NOT NULL UNIQUE,
                name  TEXT    NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
        """)

    @contextlib.contextmanager
    def transaction(self) -> Generator:
        """Explicit transaction with automatic rollback on error."""
        try:
            yield self.conn
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise

    def insert(self, email: str, name: str) -> int:
        with self.transaction() as conn:
            cur = conn.execute(
                "INSERT INTO users (email, name) VALUES (?, ?)",
                (email, name),            # parameterized — prevents SQL injection
            )
            return cur.lastrowid

    def get_by_email(self, email: str) -> User | None:
        row = self.conn.execute(
            "SELECT id, email, name FROM users WHERE email = ?", (email,)
        ).fetchone()
        return User(**dict(row)) if row else None

repo = UserRepository()
uid = repo.insert("alice@example.com", "Alice")
print(repo.get_by_email("alice@example.com"))'''
        java = '''import java.sql.*;
import java.util.Optional;

public class UserRepository {
    private final DataSource dataSource;

    public UserRepository(DataSource dataSource) {
        this.dataSource = dataSource;
    }

    /** Insert user — parameterized query prevents SQL injection. */
    public long insert(String email, String name) throws SQLException {
        String sql = "INSERT INTO users (email, name) VALUES (?, ?)";
        try (Connection conn = dataSource.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql, Statement.RETURN_GENERATED_KEYS)) {
            ps.setString(1, email);
            ps.setString(2, name);
            ps.executeUpdate();
            try (ResultSet keys = ps.getGeneratedKeys()) {
                return keys.next() ? keys.getLong(1) : -1;
            }
        }
    }

    /** Fetch by email using indexed column. */
    public Optional<User> findByEmail(String email) throws SQLException {
        String sql = "SELECT id, email, name FROM users WHERE email = ?";
        try (Connection conn = dataSource.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setString(1, email);
            try (ResultSet rs = ps.executeQuery()) {
                if (rs.next())
                    return Optional.of(new User(rs.getLong("id"),
                                                rs.getString("email"),
                                                rs.getString("name")));
            }
        }
        return Optional.empty();
    }

    /** Transactional batch insert — all-or-nothing. */
    public void batchInsert(java.util.List<User> users) throws SQLException {
        String sql = "INSERT INTO users (email, name) VALUES (?, ?)";
        try (Connection conn = dataSource.getConnection()) {
            conn.setAutoCommit(false);  // start transaction
            try (PreparedStatement ps = conn.prepareStatement(sql)) {
                for (User u : users) {
                    ps.setString(1, u.email()); ps.setString(2, u.name());
                    ps.addBatch();
                }
                ps.executeBatch();
                conn.commit();          // commit only if all succeed
            } catch (SQLException e) {
                conn.rollback();        // rollback on any failure
                throw e;
            }
        }
    }
}'''
        return py, java

    # ── SECURITY ──
    if any(x in t for x in ["auth", "jwt", "oauth", "encrypt", "tls", "security", "rbac", "key management"]):
        py = '''import hashlib, hmac, secrets, time
import jwt                        # pip install PyJWT
from cryptography.fernet import Fernet
from typing import Optional

SECRET_KEY = secrets.token_bytes(32)

# ── Password hashing ────────────────────────────────────────────────────────
def hash_password(password: str) -> str:
    """Argon2 / bcrypt preferable in production; PBKDF2 shown here."""
    salt = secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 260_000)
    return f"{salt.hex()}:{dk.hex()}"

def verify_password(stored: str, provided: str) -> bool:
    salt_hex, dk_hex = stored.split(":")
    salt = bytes.fromhex(salt_hex)
    dk = hashlib.pbkdf2_hmac("sha256", provided.encode(), salt, 260_000)
    return hmac.compare_digest(dk.hex(), dk_hex)  # constant-time comparison

# ── JWT tokens ──────────────────────────────────────────────────────────────
def create_token(user_id: int, roles: list[str], ttl_seconds: int = 3600) -> str:
    payload = {
        "sub": user_id,
        "roles": roles,
        "iat": time.time(),
        "exp": time.time() + ttl_seconds,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def verify_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return None

# ── Symmetric encryption ────────────────────────────────────────────────────
key = Fernet.generate_key()
fernet = Fernet(key)
encrypted = fernet.encrypt(b"sensitive data")
print(fernet.decrypt(encrypted))   # b"sensitive data"'''
        java = '''import io.jsonwebtoken.*;
import io.jsonwebtoken.security.Keys;
import javax.crypto.SecretKey;
import java.security.MessageDigest;
import java.security.SecureRandom;
import java.util.*;

public class SecurityUtils {
    private static final SecureRandom RANDOM = new SecureRandom();
    private static final SecretKey JWT_KEY = Keys.secretKeyFor(SignatureAlgorithm.HS256);

    // ── Password hashing ─────────────────────────────────────────────────
    public static String hashPassword(String password) throws Exception {
        byte[] salt = new byte[16];
        RANDOM.nextBytes(salt);
        MessageDigest md = MessageDigest.getInstance("SHA-256");
        md.update(salt);
        byte[] hash = md.digest(password.getBytes());
        return Base64.getEncoder().encodeToString(salt) + ":" +
               Base64.getEncoder().encodeToString(hash);
    }

    public static boolean verifyPassword(String stored, String provided) throws Exception {
        String[] parts = stored.split(":");
        byte[] salt = Base64.getDecoder().decode(parts[0]);
        MessageDigest md = MessageDigest.getInstance("SHA-256");
        md.update(salt);
        byte[] expected = Base64.getDecoder().decode(parts[1]);
        byte[] actual = md.digest(provided.getBytes());
        return MessageDigest.isEqual(expected, actual); // constant-time
    }

    // ── JWT ──────────────────────────────────────────────────────────────
    public static String createToken(long userId, List<String> roles) {
        return Jwts.builder()
            .subject(String.valueOf(userId))
            .claim("roles", roles)
            .issuedAt(new Date())
            .expiration(new Date(System.currentTimeMillis() + 3_600_000)) // 1h
            .signWith(JWT_KEY)
            .compact();
    }

    public static Claims verifyToken(String token) {
        return Jwts.parser().verifyWith(JWT_KEY).build()
               .parseSignedClaims(token).getPayload();
    }
}'''
        return py, java

    # ── ML / RECOMMENDATIONS ──
    if any(x in t for x in ["recommendation", "collaborative filtering", "matrix factorization",
                              "embedding", "neural", "ml", "machine learning", "feature"]):
        py = '''import numpy as np
from dataclasses import dataclass
from typing import Optional

@dataclass
class MatrixFactorization:
    """Collaborative filtering via gradient descent ALS."""
    n_users: int
    n_items: int
    n_factors: int = 50
    learning_rate: float = 0.01
    regularization: float = 0.02
    n_epochs: int = 20

    def __post_init__(self):
        # Initialize latent factor matrices
        self.U = np.random.normal(0, 0.1, (self.n_users, self.n_factors))
        self.V = np.random.normal(0, 0.1, (self.n_items, self.n_factors))

    def fit(self, ratings: list[tuple[int, int, float]]) -> "MatrixFactorization":
        for epoch in range(self.n_epochs):
            total_loss = 0.0
            for user_id, item_id, rating in ratings:
                pred = np.dot(self.U[user_id], self.V[item_id])
                err = rating - pred
                # Gradient step with L2 regularization
                self.U[user_id] += self.learning_rate * (
                    err * self.V[item_id] - self.regularization * self.U[user_id]
                )
                self.V[item_id] += self.learning_rate * (
                    err * self.U[user_id] - self.regularization * self.V[item_id]
                )
                total_loss += err ** 2
            if epoch % 5 == 0:
                print(f"Epoch {epoch}: RMSE={np.sqrt(total_loss/len(ratings)):.4f}")
        return self

    def predict(self, user_id: int, item_id: int) -> float:
        return float(np.dot(self.U[user_id], self.V[item_id]))

    def recommend(self, user_id: int, top_k: int = 10) -> list[tuple[int, float]]:
        scores = self.U[user_id] @ self.V.T          # dot product with all items
        top_items = np.argsort(-scores)[:top_k]
        return [(int(i), float(scores[i])) for i in top_items]

# Demo
ratings = [(0,0,5.0),(0,1,3.0),(1,0,4.0),(1,2,2.0),(2,1,5.0),(2,2,4.0)]
model = MatrixFactorization(n_users=3, n_items=3, n_factors=10, n_epochs=10)
model.fit(ratings)
print(model.recommend(0, top_k=3))'''
        java = '''import java.util.*;

public class CollaborativeFilter {
    private final double[][] userFactors;  // U: users x factors
    private final double[][] itemFactors;  // V: items x factors
    private final int nFactors;
    private final double lr, reg;

    public CollaborativeFilter(int nUsers, int nItems, int nFactors) {
        this.nFactors = nFactors; this.lr = 0.01; this.reg = 0.02;
        Random rng = new Random(42);
        userFactors = new double[nUsers][nFactors];
        itemFactors = new double[nItems][nFactors];
        // Random initialization
        for (double[] row : userFactors) for (int j = 0; j < nFactors; j++) row[j] = rng.nextGaussian() * 0.1;
        for (double[] row : itemFactors) for (int j = 0; j < nFactors; j++) row[j] = rng.nextGaussian() * 0.1;
    }

    public void train(int[][] userItem, double[] ratings) {
        for (int epoch = 0; epoch < 20; epoch++) {
            for (int k = 0; k < userItem.length; k++) {
                int u = userItem[k][0], i = userItem[k][1];
                double pred = dot(userFactors[u], itemFactors[i]);
                double err = ratings[k] - pred;
                for (int f = 0; f < nFactors; f++) {
                    double uf = userFactors[u][f], vf = itemFactors[i][f];
                    userFactors[u][f] += lr * (err * vf - reg * uf);
                    itemFactors[i][f] += lr * (err * uf - reg * vf);
                }
            }
        }
    }

    public double predict(int user, int item) { return dot(userFactors[user], itemFactors[item]); }

    private double dot(double[] a, double[] b) {
        double s = 0; for (int i = 0; i < a.length; i++) s += a[i] * b[i]; return s;
    }
}'''
        return py, java

    # ── SOCIAL / FEED ──
    if any(x in t for x in ["feed", "social", "timeline", "newsfeed", "notification", "follow"]):
        py = '''import redis
import time
from dataclasses import dataclass, field
from typing import Optional

r = redis.Redis(decode_responses=True)

@dataclass
class Post:
    post_id: str
    author_id: str
    content: str
    timestamp: float = field(default_factory=time.time)

class FeedService:
    """Hybrid push-pull feed: push for regular users, pull for celebrities."""
    CELEBRITY_THRESHOLD = 1_000_000   # followers

    def publish_post(self, post: Post, follower_count: int) -> None:
        """Push post to follower feeds (fanout on write for small accounts)."""
        post_data = f"{post.post_id}:{post.timestamp}"
        # Store post metadata
        r.hset(f"post:{post.post_id}", mapping={
            "content": post.content,
            "author": post.author_id,
            "ts": post.timestamp,
        })
        if follower_count < self.CELEBRITY_THRESHOLD:
            # Push to each follower's feed sorted set (score = timestamp)
            followers = r.smembers(f"followers:{post.author_id}")
            pipe = r.pipeline()
            for follower_id in followers:
                pipe.zadd(f"feed:{follower_id}", {post.post_id: post.timestamp})
                pipe.zremrangebyrank(f"feed:{follower_id}", 0, -1001)  # cap at 1000
            pipe.execute()

    def get_feed(self, user_id: str, limit: int = 20) -> list[dict]:
        """Get merged feed: own feed (pushed) + celebrity followings (pulled)."""
        post_ids = r.zrevrange(f"feed:{user_id}", 0, limit - 1, withscores=False)
        return [r.hgetall(f"post:{pid}") for pid in post_ids]'''
        java = '''import redis.clients.jedis.*;
import java.util.*;

public class FeedService {
    private static final int CELEBRITY_THRESHOLD = 1_000_000;
    private final JedisPool jedisPool;

    public FeedService(JedisPool jedisPool) { this.jedisPool = jedisPool; }

    public void publishPost(String postId, String authorId, String content,
                             long followerCount) {
        try (Jedis jedis = jedisPool.getResource()) {
            double timestamp = System.currentTimeMillis() / 1000.0;
            // Store post metadata
            jedis.hset("post:" + postId, Map.of(
                "content", content, "author", authorId, "ts", String.valueOf(timestamp)
            ));
            if (followerCount < CELEBRITY_THRESHOLD) {
                // Fanout on write — push to each follower's feed
                Set<String> followers = jedis.smembers("followers:" + authorId);
                Pipeline pipe = jedis.pipelined();
                for (String followerId : followers) {
                    pipe.zadd("feed:" + followerId, timestamp, postId);
                    pipe.zremrangeByRank("feed:" + followerId, 0, -1001); // keep 1000
                }
                pipe.sync();
            }
        }
    }

    public List<Map<String, String>> getFeed(String userId, int limit) {
        try (Jedis jedis = jedisPool.getResource()) {
            List<String> postIds = new ArrayList<>(
                jedis.zrevrangeByScore("feed:" + userId, "+inf", "-inf",
                                       0, limit));
            List<Map<String, String>> posts = new ArrayList<>();
            for (String pid : postIds) posts.add(jedis.hgetAll("post:" + pid));
            return posts;
        }
    }
}'''
        return py, java

    # ── GENERIC SYSTEM DESIGN (fallback) ──
    py_generic = f'''import asyncio
import aiohttp
from dataclasses import dataclass
from typing import Optional, List
import time, logging

logger = logging.getLogger(__name__)

@dataclass
class ServiceConfig:
    host: str = "localhost"
    port: int = 8080
    timeout_seconds: float = 5.0
    max_retries: int = 3

class ServiceClient:
    """Generic service client with retry and circuit breaker."""
    def __init__(self, config: ServiceConfig):
        self.config = config
        self.base_url = f"http://{{config.host}}:{{config.port}}"
        self._failures = 0
        self._circuit_open = False
        self._last_failure: Optional[float] = None

    def _is_circuit_open(self) -> bool:
        if not self._circuit_open:
            return False
        # Half-open after 60s — allow one request through
        if time.time() - self._last_failure > 60:
            self._circuit_open = False
            return False
        return True

    async def call(self, endpoint: str, payload: dict) -> Optional[dict]:
        if self._is_circuit_open():
            logger.warning("Circuit open — fast fail")
            return None

        timeout = aiohttp.ClientTimeout(total=self.config.timeout_seconds)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            for attempt in range(self.config.max_retries):
                try:
                    async with session.post(
                        f"{{self.base_url}}{{endpoint}}", json=payload
                    ) as resp:
                        resp.raise_for_status()
                        self._failures = 0              # reset on success
                        return await resp.json()
                except Exception as e:
                    logger.warning(f"Attempt {{attempt+1}} failed: {{e}}")
                    if attempt < self.config.max_retries - 1:
                        await asyncio.sleep(2 ** attempt)  # exponential backoff
            # All retries exhausted
            self._failures += 1
            if self._failures >= 5:                     # open circuit
                self._circuit_open = True
                self._last_failure = time.time()
            return None'''

    java_generic = '''import java.net.http.*;
import java.net.URI;
import java.time.Duration;
import java.util.concurrent.atomic.*;
import java.util.concurrent.CompletableFuture;

/** Generic resilient service client with circuit breaker + retry. */
public class ServiceClient {
    private final String baseUrl;
    private final HttpClient http;
    private final AtomicInteger failures = new AtomicInteger(0);
    private final AtomicBoolean circuitOpen = new AtomicBoolean(false);
    private volatile long lastFailureTime;

    public ServiceClient(String host, int port) {
        this.baseUrl = "http://" + host + ":" + port;
        this.http = HttpClient.newBuilder()
            .connectTimeout(Duration.ofSeconds(5))
            .build();
    }

    private boolean isCircuitOpen() {
        if (!circuitOpen.get()) return false;
        // Half-open after 60s
        if (System.currentTimeMillis() - lastFailureTime > 60_000) {
            circuitOpen.set(false);
            return false;
        }
        return true;
    }

    public CompletableFuture<String> call(String path, String jsonBody) {
        if (isCircuitOpen())
            return CompletableFuture.failedFuture(
                new RuntimeException("Circuit open"));

        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create(baseUrl + path))
            .header("Content-Type", "application/json")
            .POST(HttpRequest.BodyPublishers.ofString(jsonBody))
            .timeout(Duration.ofSeconds(5))
            .build();

        return http.sendAsync(request, HttpResponse.BodyHandlers.ofString())
            .thenApply(resp -> {
                if (resp.statusCode() >= 500) throw new RuntimeException("Server error");
                failures.set(0);  // reset on success
                return resp.body();
            })
            .exceptionally(ex -> {
                if (failures.incrementAndGet() >= 5) {
                    circuitOpen.set(true);
                    lastFailureTime = System.currentTimeMillis();
                }
                return null;
            });
    }
}'''
    return py_generic, java_generic


# ── Calculation generator ────────────────────────────────────────────────────

def get_calculations(title: str, dirpath: str) -> str:
    t = title.lower()

    if any(x in t for x in ["lru", "lfu", "cache"]):
        return """**Cache Sizing:**
- Working set: 10M active items × 1KB avg = 10GB
- 80% hit target → cache needs to hold top 20% most popular = 2GB
- With 10 cache nodes: 200MB per node (fits in RAM)
- Hit ratio math: 80% from cache, 20% from DB
- Effective latency: 0.8×1ms + 0.2×10ms = 2.8ms (vs 10ms without cache)

**Throughput:**
- Single Redis node: 100K ops/sec
- 10-node cluster: 1M ops/sec
- At 50% hit ratio a 1M QPS app issues 500K DB queries — unsustainable
- At 90% hit ratio: 100K DB queries — manageable"""

    if any(x in t for x in ["sort", "search", "algorithm"]):
        return """**Time vs Data Size:**
- n=1,000: O(n log n) = ~10K ops → <1ms
- n=1,000,000: O(n log n) = ~20M ops → ~20ms
- n=1,000,000,000: O(n log n) = ~30B ops → ~30s
- O(n²) at n=1M: 10¹² ops → hours — impractical

**Memory:**
- Merge sort: O(n) auxiliary = 8MB for 1M 64-bit ints
- QuickSort: O(log n) stack = ~20 frames = negligible
- Radix sort: O(n+k) where k=range — 4GB for 32-bit ints"""

    if any(x in t for x in ["kafka", "queue", "message", "stream"]):
        return """**Throughput:**
- Kafka throughput per broker: 100MB/sec write
- 1KB messages → 100K msgs/sec per broker
- 10 brokers → 1M msgs/sec cluster throughput
- At 500B messages/day: 500B / 86400 = ~5.8M msgs/sec peak

**Storage:**
- 1M msgs/sec × 1KB = 1GB/sec raw
- 7-day retention: 7 × 86400 × 1GB = 604TB
- With 3x replication: 1.8PB total
- Compression (3:1): reduces to 600TB

**Latency:**
- Produce (acks=1): <5ms p99
- End-to-end (produce → consume): 10-20ms typical"""

    if any(x in t for x in ["kubernetes", "container", "pod"]):
        return """**Cluster Capacity:**
- Node: 16 cores, 64GB RAM
- Per pod: 0.5 CPU request, 512MB
- Max pods per node (CPU): 32; (RAM): 128 → CPU limits at 32
- 100 nodes → 3200 pods max (real-world ~70% = 2200 schedulable)

**API Server Load:**
- 1000 pods × 2 watches = 2000 open connections
- Heartbeat: 10s interval → 200 QPS steady state
- kubectl list pods: scans etcd — expensive; use field selectors

**Etcd Storage:**
- 1 pod spec: ~2KB in etcd
- 10K pods: 20MB — well within 8GB etcd limit
- Snapshot interval: every 10K revisions → ~1 min compaction"""

    if any(x in t for x in ["database", "sql", "index", "btree", "query"]):
        return """**Index Impact:**
- Table: 100M rows, 100 bytes each = 10GB
- Full table scan: 10GB / 500MB/s = 20 seconds
- B-tree index lookup: log₂(100M) ≈ 27 comparisons → <1ms
- Index storage: 100M × 8 bytes (rowid) × 2 (overhead) = 1.6GB

**Query Throughput:**
- Single DB: 10K simple queries/sec
- With connection pool (20 connections): ~5K TPS
- Read replica: 3 replicas → 15K read TPS
- Write throughput limited by leader: 2K TPS"""

    if any(x in t for x in ["security", "auth", "encrypt", "jwt"]):
        return """**Crypto Performance:**
- AES-256-GCM: 3GB/sec throughput (hardware accelerated)
- RSA-2048 sign: 5ms; verify: 0.3ms
- bcrypt (cost=12): 250ms per hash — good for login, too slow for API
- PBKDF2 (260K iterations): 100ms — balance of security and speed
- JWT verify (HS256): <1ms — suitable for every request

**Token Storage:**
- 1M active sessions × 256 bytes = 256MB in Redis
- 100K logins/day × 256 bytes = 25MB new tokens/day
- TTL 1 hour → ~4% of tokens expire per minute → cleanup manageable"""

    if any(x in t for x in ["recommendation", "ml", "neural", "embedding"]):
        return """**Model Scale:**
- Users: 100M, Items: 10M, Factors: 128
- U matrix: 100M × 128 × 4 bytes = 51GB
- V matrix: 10M × 128 × 4 bytes = 5.1GB
- Training: 1B ratings × 20 epochs × 128 ops = 2.56T FLOPs → ~1h on A100

**Serving Latency:**
- ANN search (FAISS) 10M items: <10ms
- Scoring top-1000 candidates: 1000 × 128 dot products = 128K FLOPs → <1ms
- Total recommendation latency budget: 50ms
  - Retrieval: 10ms, Scoring: 5ms, Post-processing: 5ms, Overhead: 30ms

**Data Freshness:**
- Real-time signals (clicks in last hour): <1min delay
- Batch model retrain: daily
- Feature store update: every 15min"""

    if any(x in t for x in ["network", "tcp", "http", "dns", "cdn"]):
        return """**Latency Budget:**
- Speed of light NYC→London (5570km): 18.5ms one-way
- Realistic TCP latency: 70-100ms (routing overhead)
- TLS handshake: +1 RTT = 100-200ms
- With TLS session resumption: +0 RTT
- CDN edge node (50ms away): 5-10ms vs 100ms origin

**Throughput:**
- TCP window size: 65KB default → 65KB / 100ms = 5Mbps
- With window scaling (64MB): 64MB / 100ms = 5Gbps theoretical
- HTTP/2 multiplexing: eliminates HOL blocking per-stream
- HTTP/3 (QUIC): 0-RTT handshake, eliminates TCP HOL blocking"""

    # generic fallback
    return f"""**System Load Estimation:**
- 1M daily active users × 10 requests/day = 10M requests/day
- Peak QPS = 10M / 86400 × 3 (peak factor) ≈ 350 QPS
- API server capacity: 1000 QPS/server → 1 server sufficient at peak
- With 2x redundancy: 2 servers minimum

**Storage Estimation:**
- 1M users × 10KB average data = 10GB structured data
- Annual growth: 10GB × 365 = 3.65TB/year
- With 3x replication: 11TB/year
- SSD cost ($0.10/GB): $1,100/year

**Bandwidth:**
- 350 QPS × 10KB response = 3.5MB/sec outbound
- Monthly egress: 3.5MB × 86400 × 30 = 9TB/month"""


# ── Follow-up generator ──────────────────────────────────────────────────────

FOLLOWUP_TEMPLATE = """## Follow-up Questions

1. **How would you handle this at 10x the scale described?**
   - What breaks first? (typically: single DB, single cache node, single region)
   - What architectural changes are required?

2. **What are the consistency vs. availability trade-offs in your design?**
   - Where did you accept eventual consistency?
   - Which operations require strong consistency and why?

3. **How would you debug a sudden latency spike in production?**
   - What metrics would you look at first?
   - What's your runbook for the top 3 likely causes?

4. **How does your design handle partial failures?**
   - What happens if one component is slow (not down)?
   - How do you prevent cascading failures?

5. **What would you change if you had to build this in one week vs. six months?**
   - What corners can safely be cut initially?
   - What must be right from day one?

6. **How would you migrate from the current design to a better one without downtime?**
   - What's the strangler-fig or blue-green strategy here?
   - How do you validate correctness during migration?"""


# ── Mermaid generator (for dirs missing diagrams) ───────────────────────────

def get_mermaid(title: str) -> str:
    return f"""## Architecture Diagrams

### System Overview
```mermaid
graph TB
    Client["Client"]
    LB["Load Balancer"]
    App["Application Layer"]
    Cache["Cache (Redis)"]
    DB["Primary Database"]
    Replica["Read Replica"]
    Queue["Message Queue"]
    Worker["Background Workers"]

    Client -->|requests| LB
    LB -->|distribute| App
    App -->|cache check| Cache
    App -->|reads/writes| DB
    App -->|async events| Queue
    DB -->|replicate| Replica
    Queue -->|consume| Worker
    Worker -->|update| DB

    style Client fill:#e1f5ff
    style LB fill:#fff3e0
    style App fill:#f3e5f5
    style Cache fill:#e8f5e9
    style DB fill:#fce4ec
```

### Data Flow
```mermaid
sequenceDiagram
    participant C as Client
    participant A as API
    participant Ca as Cache
    participant D as Database
    C->>A: Request
    A->>Ca: Cache lookup
    alt Cache Hit
        Ca-->>A: Cached data
    else Cache Miss
        A->>D: Query
        D-->>A: Result
        A->>Ca: Cache set (TTL)
    end
    A-->>C: Response
```

### Scaling Architecture
```mermaid
graph LR
    subgraph Region1["Region 1 (Primary)"]
        A1["App servers"]
        D1["Primary DB"]
        C1["Cache cluster"]
    end
    subgraph Region2["Region 2 (DR)"]
        A2["App servers"]
        D2["Replica DB"]
        C2["Cache cluster"]
    end
    D1 -->|async replication| D2
    LBG["Global LB"] --> A1
    LBG --> A2

    style Region1 fill:#e8f5e9
    style Region2 fill:#e3f2fd
```"""


# ── Main enhancement logic ───────────────────────────────────────────────────

def extract_title(content: str, filepath: str) -> str:
    m = re.search(r'^#\s+(.+)', content, re.MULTILINE)
    if m:
        return m.group(1).strip()
    return os.path.basename(filepath).replace("_", " ").replace(".md", "")


def needs(content: str, marker: str) -> bool:
    return marker.lower() not in content.lower()


def enhance_file(filepath: str) -> list[str]:
    content = open(filepath, encoding="utf-8", errors="ignore").read()
    title = extract_title(content, filepath)
    dirpath = os.path.dirname(filepath)
    additions = []
    appended = []

    # 1. Mermaid diagrams
    if needs(content, "```mermaid"):
        appended.append("mermaid")
        additions.append(get_mermaid(title))

    # 2. Code implementations
    if needs(content, "```python") or needs(content, "```java"):
        py_code, java_code = get_code(title, dirpath)
        section = f"\n## Code Implementation\n\n### Python\n```python\n{py_code}\n```\n\n### Java\n```java\n{java_code}\n```\n"
        appended.append("python+java")
        additions.append(section)

    # 3. Back-of-envelope calculations
    if needs(content, "Back-of-the-Envelope"):
        calc = get_calculations(title, dirpath)
        appended.append("calc")
        additions.append(f"\n## Back-of-the-Envelope Calculations\n\n{calc}\n")

    # 4. Follow-up questions
    if needs(content, "Follow-up"):
        appended.append("followup")
        additions.append(FOLLOWUP_TEMPLATE)

    if additions:
        with open(filepath, "a", encoding="utf-8") as f:
            f.write("\n")
            for block in additions:
                f.write(block)

    return appended


def main():
    all_files = sorted(glob.glob(f"{BASE}/**/*.md", recursive=True))
    print(f"Processing {len(all_files)} files...\n")

    by_dir: dict[str, list] = {}
    for f in all_files:
        by_dir.setdefault(os.path.dirname(f), []).append(f)

    total_enhanced = 0
    for dirpath, files in sorted(by_dir.items()):
        dirname = os.path.basename(dirpath)
        enhanced_in_dir = 0
        for filepath in sorted(files):
            added = enhance_file(filepath)
            if added:
                fname = os.path.basename(filepath)
                print(f"  ✅ {dirname}/{fname} [+{' +'.join(added)}]")
                enhanced_in_dir += 1
                total_enhanced += 1
        if enhanced_in_dir:
            print(f"  → {dirname}: enhanced {enhanced_in_dir}/{len(files)} files\n")

    print(f"\n{'='*60}")
    print(f"Done. Enhanced {total_enhanced}/{len(all_files)} files.")


if __name__ == "__main__":
    main()
