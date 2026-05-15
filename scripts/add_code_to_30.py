#!/usr/bin/env python3
"""
Add code implementations to 30 new concepts.
"""

import os
import re
import glob

base_path = "/home/sbisw/github/datastructures/docs/system_design"

code_implementations = {
    "01_consistent_hashing": {
        "python": """```python
class ConsistentHash:
    def __init__(self, nodes=None, replicas=3):
        self.replicas = replicas
        self.ring = {}
        self.sorted_keys = []
        if nodes:
            for node in nodes:
                self.add_node(node)

    def _hash(self, key):
        return hash(key) % (2**32)

    def add_node(self, node):

    """

    [Brief description of what this function does]


    Args:

        [param]: description


    Returns:

        [description of return value]


    Time: O([complexity])

    Space: O([complexity])

    """
        for i in range(self.replicas):
            virtual_key = f"{node}:{i}"
            hash_key = self._hash(virtual_key)
            self.ring[hash_key] = node
        self.sorted_keys = sorted(self.ring.keys())

    def remove_node(self, node):

    """

    [Brief description of what this function does]


    Args:

        [param]: description


    Returns:

        [description of return value]


    Time: O([complexity])

    Space: O([complexity])

    """
        for i in range(self.replicas):
            virtual_key = f"{node}:{i}"
            hash_key = self._hash(virtual_key)
            del self.ring[hash_key]
        self.sorted_keys = sorted(self.ring.keys())

    def get_node(self, key):

    """

    [Brief description of what this function does]


    Args:

        [param]: description


    Returns:

        [description of return value]


    Time: O([complexity])

    Space: O([complexity])

    """
        if not self.ring:
            return None
        hash_key = self._hash(key)
        idx = bisect.bisect_left(self.sorted_keys, hash_key) % len(self.sorted_keys)
        return self.ring[self.sorted_keys[idx]]
```""",
        "java": """```java
class ConsistentHash {
    private final int replicas;
    private final Map<Long, String> ring = new HashMap<>();
    private final SortedMap<Long, String> sortedRing = new TreeMap<>();

    public ConsistentHash(List<String> nodes, int replicas) {
        this.replicas = replicas;
        nodes.forEach(this::addNode);
    }

    private long hash(String key) {
        return Math.abs((long)key.hashCode());
    }

    public void addNode(String node) {
        for (int i = 0; i < replicas; i++) {
            long hash = hash(node + ":" + i);
            ring.put(hash, node);
            sortedRing.put(hash, node);
        }
    }

    public String getNode(String key) {
        if (ring.isEmpty()) return null;
        long hash = hash(key);
        SortedMap<Long, String> tail = sortedRing.tailMap(hash);
        long nodeKey = tail.isEmpty() ? sortedRing.firstKey() : tail.firstKey();
        return sortedRing.get(nodeKey);
    }
}
```"""
    },
    "02_geohashing": {
        "python": """```python
class GeoHash:
    def __init__(self, lat, lon, precision=6):
        self.lat = lat
        self.lon = lon
        self.precision = precision

    def encode(self):

    """

    [Brief description of what this function does]


    Args:

        [param]: description


    Returns:

        [description of return value]


    Time: O([complexity])

    Space: O([complexity])

    """
        lat_range = [-90, 90]
        lon_range = [-180, 180]
        geohash = []
        bits = 0
        bit = 0
        ch = 0

        while len(geohash) < self.precision:
            if bits % 2 == 0:
                mid = (lon_range[0] + lon_range[1]) / 2
                if self.lon > mid:
                    ch |= (1 << (4 - bit))
                    lon_range[0] = mid
                else:
                    lon_range[1] = mid
            else:
                mid = (lat_range[0] + lat_range[1]) / 2
                if self.lat > mid:
                    ch |= (1 << (4 - bit))
                    lat_range[0] = mid
                else:
                    lat_range[1] = mid

            bits += 1
            if bits == 5:
                geohash.append(self._base32_char(ch))
                bits = 0
                ch = 0
            bit += 1

        return ''.join(geohash)

    def _base32_char(self, val):
        base32 = '0123456789bcdefghjkmnpqrstuvwxyz'
        return base32[val]
```""",
        "java": """```java
class GeoHash {
    private final double lat, lon;
    private final int precision;
    private static final String BASE32 = "0123456789bcdefghjkmnpqrstuvwxyz";

    public GeoHash(double lat, double lon, int precision) {
        this.lat = lat;
        this.lon = lon;
        this.precision = precision;
    }

    public String encode() {
        double[] latRange = {-90, 90};
        double[] lonRange = {-180, 180};
        StringBuilder geohash = new StringBuilder();
        int bits = 0, ch = 0;

        while (geohash.length() < precision) {
            if (bits % 2 == 0) {
                double mid = (lonRange[0] + lonRange[1]) / 2;
                if (lon > mid) {
                    ch |= (1 << (4 - (bits / 2)));
                    lonRange[0] = mid;
                } else {
                    lonRange[1] = mid;
                }
            } else {
                double mid = (latRange[0] + latRange[1]) / 2;
                if (lat > mid) {
                    ch |= (1 << (4 - (bits / 2)));
                    latRange[0] = mid;
                } else {
                    latRange[1] = mid;
                }
            }

            bits++;
            if (bits == 5) {
                geohash.append(BASE32.charAt(ch));
                bits = 0;
                ch = 0;
            }
        }
        return geohash.toString();
    }
}
```"""
    },
    "03_trie_data_structure": {
        "python": """```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):

    """

    [Brief description of what this function does]


    Args:

        [param]: description


    Returns:

        [description of return value]


    Time: O([complexity])

    Space: O([complexity])

    """
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end = True

    def search(self, word):

    """

    [Brief description of what this function does]


    Args:

        [param]: description


    Returns:

        [description of return value]


    Time: O([complexity])

    Space: O([complexity])

    """
        node = self._find_node(word)
        return node is not None and node.is_end

    def autocomplete(self, prefix):
        node = self._find_node(prefix)
        if node is None:
            return []
        return self._dfs(node, prefix)

    def _find_node(self, prefix):

    """

    [Brief description of what this function does]


    Args:

        [param]: description


    Returns:

        [description of return value]


    Time: O([complexity])

    Space: O([complexity])

    """
        node = self.root
        for char in prefix:
            if char not in node.children:
                return None
            node = node.children[char]
        return node

    def _dfs(self, node, word):

    """

    [Brief description of what this function does]


    Args:

        [param]: description


    Returns:

        [description of return value]


    Time: O([complexity])

    Space: O([complexity])

    """
        results = []
        if node.is_end:
            results.append(word)
        for char, child in node.children.items():
            results.extend(self._dfs(child, word + char))
        return results
```""",
        "java": """```java
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
```"""
    }
}

def add_code(filepath, concept_id, implementations):
    """Add code to implementation section."""
    try:
        with open(filepath, 'r') as f:
            content = f.read()

        for key, impl in implementations.items():
            if key in concept_id:
                # Replace Python
                content = re.sub(
                    r'```python\n# Working implementation[^\n]*\n[^`]*```',
                    impl['python'],
                    content
                )

                # Replace Java
                content = re.sub(
                    r'```java\n// Object-oriented implementation[^\n]*\n[^`]*```',
                    impl['java'],
                    content
                )

                with open(filepath, 'w') as f:
                    f.write(content)
                return True

    except Exception as e:
        print(f"Error: {filepath}: {e}")

    return False

# Process files
added = 0
for filepath in glob.glob(f"{base_path}/10-*/01_consistent_hashing.md") + \
                glob.glob(f"{base_path}/10-*/02_geohashing.md") + \
                glob.glob(f"{base_path}/10-*/03_trie_data_structure.md"):

    concept_id = os.path.basename(filepath).replace(".md", "")
    if add_code(filepath, concept_id, code_implementations):
        added += 1
        print(f"✓ Added code: {os.path.dirname(filepath)}/{concept_id}")

print(f"\n✅ Added code implementations to {added} concepts")
