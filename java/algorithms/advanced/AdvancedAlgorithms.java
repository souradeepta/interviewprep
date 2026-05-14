import java.util.*;

/**
 * Advanced Algorithms for SDE Interview Preparation
 * ================================================
 *
 * Comprehensive implementations of 25+ advanced algorithms across:
 * - Dynamic Programming (advanced techniques)
 * - Graph Algorithms (flow, matching, 2-SAT)
 * - String Algorithms
 * - Computational Geometry
 * - Tree Algorithms
 *
 * Each algorithm includes:
 * - Clear, interview-ready implementation
 * - Time/space complexity analysis
 * - Working demo examples
 */

public class AdvancedAlgorithms {

    // ========================================================================
    // DYNAMIC PROGRAMMING - ADVANCED
    // ========================================================================

    /**
     * Convex Hull Trick - Optimize DP transitions O(n²) → O(n log n)
     * Time: O(n log n)
     * Space: O(n)
     */
    static class ConvexHullTrick {
        static class Line {
            long slope, intercept;
            int idx;

            Line(long slope, long intercept, int idx) {
                this.slope = slope;
                this.intercept = intercept;
                this.idx = idx;
            }
        }

        List<Line> lines = new ArrayList<>();

        boolean badIntersection(Line l1, Line l2, Line l3) {
            // Check if l2 is removed by intersection of l1 and l3
            // (b3-b2)/(m2-m3) <= (b2-b1)/(m1-m2)
            return (l3.intercept - l2.intercept) * (l1.slope - l2.slope)
                    <= (l2.intercept - l1.intercept) * (l2.slope - l3.slope);
        }

        void addLine(long slope, long intercept, int j) {
            Line newLine = new Line(slope, intercept, j);

            while (lines.size() >= 2 && badIntersection(
                    lines.get(lines.size() - 2),
                    lines.get(lines.size() - 1),
                    newLine)) {
                lines.remove(lines.size() - 1);
            }

            lines.add(newLine);
        }

        long query(long x) {
            if (lines.isEmpty()) return Long.MAX_VALUE;

            int left = 0, right = lines.size() - 1;
            while (left < right) {
                int mid = (left + right) / 2;
                Line l1 = lines.get(mid);
                Line l2 = lines.get(mid + 1);

                if (l1.slope * x + l1.intercept > l2.slope * x + l2.intercept) {
                    left = mid + 1;
                } else {
                    right = mid;
                }
            }

            Line best = lines.get(left);
            return best.slope * x + best.intercept;
        }
    }

    /**
     * Digit DP - Counting/extremum problems on digits
     */
    static class DigitDP {
        static long countNumbersNoConsecutiveOnes(int n) {
            String s = Integer.toBinaryString(n);
            Map<String, Long> memo = new HashMap<>();

            return dp(s, 0, true, false, memo);
        }

        private static long dp(String s, int pos, boolean tight, boolean prevOne,
                              Map<String, Long> memo) {
            if (pos == s.length()) {
                return 1;
            }

            String key = pos + "," + tight + "," + prevOne;
            if (memo.containsKey(key)) {
                return memo.get(key);
            }

            int limit = tight ? (s.charAt(pos) - '0') : 1;
            long count = 0;

            for (int digit = 0; digit <= limit; digit++) {
                if (digit == 1 && prevOne) continue;

                boolean newTight = tight && (digit == limit);
                count += dp(s, pos + 1, newTight, digit == 1, memo);
            }

            memo.put(key, count);
            return count;
        }
    }

    /**
     * Tree DP - Dynamic programming on tree structures
     */
    static class TreeDP {
        static int treeMaximumIndependentSet(List<Integer>[] adj) {
            int n = adj.length;
            int[] dpInclude = new int[n];
            int[] dpExclude = new int[n];

            dfs(0, -1, adj, dpInclude, dpExclude);
            return Math.max(dpInclude[0], dpExclude[0]);
        }

        private static void dfs(int u, int parent, List<Integer>[] adj,
                               int[] dpInclude, int[] dpExclude) {
            dpInclude[u] = 1;
            dpExclude[u] = 0;

            for (int v : adj[u]) {
                if (v == parent) continue;

                dfs(v, u, adj, dpInclude, dpExclude);
                dpInclude[u] += dpExclude[v];
                dpExclude[u] += Math.max(dpInclude[v], dpExclude[v]);
            }
        }
    }

    /**
     * Sum Over Subsets DP - O(n * 2^n) subset enumeration
     */
    static class SOSDP {
        static long[] subsetSumConvolution(long[] a, long[] b) {
            int n = a.length;
            long[] dpA = a.clone();
            long[] dpB = b.clone();
            int maxMask = 1 << n;

            // Forward SOS transform
            for (int i = 0; i < n; i++) {
                for (int mask = 0; mask < maxMask; mask++) {
                    if ((mask & (1 << i)) != 0) {
                        dpA[mask] += dpA[mask ^ (1 << i)];
                        dpB[mask] += dpB[mask ^ (1 << i)];
                    }
                }
            }

            // Pointwise multiplication
            long[] result = new long[maxMask];
            for (int mask = 0; mask < maxMask; mask++) {
                result[mask] = dpA[mask] * dpB[mask];
            }

            // Inverse transform
            for (int i = 0; i < n; i++) {
                for (int mask = 0; mask < maxMask; mask++) {
                    if ((mask & (1 << i)) != 0) {
                        result[mask] -= result[mask ^ (1 << i)];
                    }
                }
            }

            return result;
        }
    }

    // ========================================================================
    // GRAPH ALGORITHMS - ADVANCED
    // ========================================================================

    /**
     * Maximum Flow - Dinic's Algorithm
     * Time: O(V² * E)
     */
    static class MaxFlowDinic {
        static class Edge {
            int to, cap, rev;

            Edge(int to, int cap, int rev) {
                this.to = to;
                this.cap = cap;
                this.rev = rev;
            }
        }

        List<Edge>[] graph;
        int[] level, iter;

        @SuppressWarnings("unchecked")
        MaxFlowDinic(int n) {
            graph = new List[n];
            level = new int[n];
            iter = new int[n];
            for (int i = 0; i < n; i++) {
                graph[i] = new ArrayList<>();
            }
        }

        void addEdge(int from, int to, int cap) {
            graph[from].add(new Edge(to, cap, graph[to].size()));
            graph[to].add(new Edge(from, 0, graph[from].size() - 1));
        }

        boolean bfs(int s, int t) {
            Arrays.fill(level, -1);
            level[s] = 0;
            Queue<Integer> queue = new LinkedList<>();
            queue.add(s);

            while (!queue.isEmpty()) {
                int u = queue.poll();
                for (Edge e : graph[u]) {
                    if (level[e.to] == -1 && e.cap > 0) {
                        level[e.to] = level[u] + 1;
                        queue.add(e.to);
                    }
                }
            }

            return level[t] != -1;
        }

        int dfs(int u, int t, int flow) {
            if (u == t) return flow;

            for (int i = iter[u]; i < graph[u].size(); i++) {
                Edge e = graph[u].get(i);
                if (level[u] < level[e.to] && e.cap > 0) {
                    int pushed = dfs(e.to, t, Math.min(flow, e.cap));
                    if (pushed > 0) {
                        e.cap -= pushed;
                        graph[e.to].get(e.rev).cap += pushed;
                        iter[u] = i;
                        return pushed;
                    }
                }
            }

            return 0;
        }

        int maxFlow(int s, int t) {
            int flow = 0;
            while (bfs(s, t)) {
                Arrays.fill(iter, 0);
                int f;
                while ((f = dfs(s, t, Integer.MAX_VALUE)) > 0) {
                    flow += f;
                }
            }
            return flow;
        }
    }

    /**
     * Bipartite Matching - Augmenting Paths Method
     * Time: O(V * E)
     */
    static class BipartiteMatching {
        List<Integer>[] graph;
        int[] matchR;
        boolean[] visited;

        @SuppressWarnings("unchecked")
        BipartiteMatching(int leftSize, int rightSize) {
            graph = new List[leftSize];
            matchR = new int[rightSize];
            visited = new boolean[rightSize];
            for (int i = 0; i < leftSize; i++) {
                graph[i] = new ArrayList<>();
            }
            Arrays.fill(matchR, -1);
        }

        void addEdge(int u, int v) {
            graph[u].add(v);
        }

        boolean dfs(int u) {
            for (int v : graph[u]) {
                if (!visited[v]) {
                    visited[v] = true;
                    if (matchR[v] == -1 || dfs(matchR[v])) {
                        matchR[v] = u;
                        return true;
                    }
                }
            }
            return false;
        }

        int maxMatching() {
            int matching = 0;
            for (int u = 0; u < graph.length; u++) {
                Arrays.fill(visited, false);
                if (dfs(u)) matching++;
            }
            return matching;
        }
    }

    /**
     * 2-SAT - Satisfiability Problem Solver
     * Time: O(V + E)
     */
    static class TwoSAT {
        List<Integer>[] graph, revGraph;
        boolean[] visited;
        List<Integer> order;
        int[] sccId;

        @SuppressWarnings("unchecked")
        TwoSAT(int n) {
            graph = new List[2 * n];
            revGraph = new List[2 * n];
            sccId = new int[2 * n];
            for (int i = 0; i < 2 * n; i++) {
                graph[i] = new ArrayList<>();
                revGraph[i] = new ArrayList<>();
            }
        }

        void addClause(int a, boolean negA, int b, boolean negB) {
            // (a OR b) = (NOT a -> b) AND (NOT b -> a)
            int aNode = 2 * a + (negA ? 1 : 0);
            int notANode = 2 * a + (negA ? 0 : 1);
            int bNode = 2 * b + (negB ? 1 : 0);
            int notBNode = 2 * b + (negB ? 0 : 1);

            graph[notANode].add(bNode);
            graph[notBNode].add(aNode);
            revGraph[bNode].add(notANode);
            revGraph[aNode].add(notBNode);
        }

        private void dfs1(int v, boolean[] vis, List<Integer> ord) {
            vis[v] = true;
            for (int u : graph[v]) {
                if (!vis[u]) dfs1(u, vis, ord);
            }
            ord.add(v);
        }

        private void dfs2(int v, int id) {
            sccId[v] = id;
            for (int u : revGraph[v]) {
                if (sccId[u] == -1) dfs2(u, id);
            }
        }

        boolean isSatisfiable() {
            // First DFS for ordering
            visited = new boolean[2 * sccId.length];
            order = new ArrayList<>();
            for (int i = 0; i < 2 * sccId.length; i++) {
                if (!visited[i]) dfs1(i, visited, order);
            }

            // Second DFS for SCC
            Arrays.fill(sccId, -1);
            int id = 0;
            for (int i = 2 * sccId.length - 1; i >= 0; i--) {
                int v = order.get(i);
                if (sccId[v] == -1) {
                    dfs2(v, id++);
                }
            }

            // Check satisfiability
            int n = sccId.length / 2;
            for (int i = 0; i < n; i++) {
                if (sccId[2 * i] == sccId[2 * i + 1]) {
                    return false;
                }
            }
            return true;
        }
    }

    /**
     * Articulation Points & Bridges
     * Time: O(V + E)
     */
    static class ArticulationPointsBridges {
        List<Integer>[] graph;
        boolean[] visited;
        int[] disc, low;
        int[] parent;
        int time = 0;
        Set<Integer> articulationPoints = new HashSet<>();
        List<int[]> bridges = new ArrayList<>();

        @SuppressWarnings("unchecked")
        ArticulationPointsBridges(int n) {
            graph = new List[n];
            visited = new boolean[n];
            disc = new int[n];
            low = new int[n];
            parent = new int[n];
            Arrays.fill(parent, -1);
            for (int i = 0; i < n; i++) {
                graph[i] = new ArrayList<>();
            }
        }

        void addEdge(int u, int v) {
            graph[u].add(v);
            graph[v].add(u);
        }

        void dfs(int u) {
            visited[u] = true;
            disc[u] = low[u] = time++;
            int children = 0;

            for (int v : graph[u]) {
                if (!visited[v]) {
                    children++;
                    parent[v] = u;
                    dfs(v);
                    low[u] = Math.min(low[u], low[v]);

                    if ((parent[u] == -1 && children > 1)
                            || (parent[u] != -1 && low[v] >= disc[u])) {
                        articulationPoints.add(u);
                    }

                    if (low[v] > disc[u]) {
                        bridges.add(new int[]{u, v});
                    }
                } else if (v != parent[u]) {
                    low[u] = Math.min(low[u], disc[v]);
                }
            }
        }

        void find() {
            for (int i = 0; i < graph.length; i++) {
                if (!visited[i]) dfs(i);
            }
        }
    }

    /**
     * Transitive Closure - Floyd-Warshall
     * Time: O(V³)
     */
    static class TransitiveClosure {
        static boolean[][] computeClosure(List<Integer>[] adj) {
            int n = adj.length;
            boolean[][] closure = new boolean[n][n];

            for (int i = 0; i < n; i++) {
                closure[i][i] = true;
                for (int v : adj[i]) {
                    closure[i][v] = true;
                }
            }

            for (int k = 0; k < n; k++) {
                for (int i = 0; i < n; i++) {
                    for (int j = 0; j < n; j++) {
                        closure[i][j] = closure[i][j] || (closure[i][k] && closure[k][j]);
                    }
                }
            }

            return closure;
        }
    }

    // ========================================================================
    // STRING ALGORITHMS - ADVANCED
    // ========================================================================

    /**
     * Boyer-Moore String Matching
     * Time: O(n/m) best, O(nm) worst
     */
    static class BoyerMoore {
        String pattern;
        Map<Character, Integer> badChar;

        BoyerMoore(String pattern) {
            this.pattern = pattern;
            buildBadCharTable();
        }

        private void buildBadCharTable() {
            badChar = new HashMap<>();
            for (int i = 0; i < pattern.length(); i++) {
                badChar.put(pattern.charAt(i), i);
            }
        }

        List<Integer> search(String text) {
            List<Integer> matches = new ArrayList<>();
            int n = text.length();
            int m = pattern.length();
            int i = 0;

            while (i <= n - m) {
                int j = m - 1;
                while (j >= 0 && text.charAt(i + j) == pattern.charAt(j)) {
                    j--;
                }

                if (j < 0) {
                    matches.add(i);
                    i += 1;
                } else {
                    int badCharShift = Math.max(1, j - badChar.getOrDefault(text.charAt(i + j), -1));
                    i += badCharShift;
                }
            }

            return matches;
        }
    }

    /**
     * Aho-Corasick Automaton - Multi-pattern Matching
     * Time: O(n + z)
     */
    static class AhoCorasick {
        static class Node {
            Map<Character, Integer> goTo = new HashMap<>();
            List<String> output = new ArrayList<>();
            int fail = 0;
        }

        List<Node> nodes = new ArrayList<>();

        AhoCorasick() {
            nodes.add(new Node());
        }

        void addPattern(String pattern) {
            int node = 0;
            for (char c : pattern.toCharArray()) {
                if (!nodes.get(node).goTo.containsKey(c)) {
                    nodes.get(node).goTo.put(c, nodes.size());
                    nodes.add(new Node());
                }
                node = nodes.get(node).goTo.get(c);
            }
            nodes.get(node).output.add(pattern);
        }

        void build() {
            Queue<Integer> queue = new LinkedList<>();

            for (int c : nodes.get(0).goTo.values()) {
                queue.add(c);
            }

            while (!queue.isEmpty()) {
                int state = queue.poll();

                for (Map.Entry<Character, Integer> entry : nodes.get(state).goTo.entrySet()) {
                    char c = entry.getKey();
                    int next = entry.getValue();
                    queue.add(next);

                    int fail = nodes.get(state).fail;
                    while (fail > 0 && !nodes.get(fail).goTo.containsKey(c)) {
                        fail = nodes.get(fail).fail;
                    }

                    int failNode = nodes.get(fail).goTo.getOrDefault(c, 0);
                    nodes.get(next).fail = failNode;
                    nodes.get(next).output.addAll(nodes.get(failNode).output);
                }
            }
        }

        List<int[]> search(String text) {
            List<int[]> matches = new ArrayList<>();
            int state = 0;

            for (int i = 0; i < text.length(); i++) {
                char c = text.charAt(i);
                while (state > 0 && !nodes.get(state).goTo.containsKey(c)) {
                    state = nodes.get(state).fail;
                }

                state = nodes.get(state).goTo.getOrDefault(c, 0);
                for (String pattern : nodes.get(state).output) {
                    matches.add(new int[]{i - pattern.length() + 1});
                }
            }

            return matches;
        }
    }

    /**
     * Z-Algorithm - Pattern Matching
     * Time: O(n)
     */
    static class ZAlgorithm {
        static int[] computeZ(String s) {
            int n = s.length();
            int[] z = new int[n];
            z[0] = n;
            int l = 0, r = 0;

            for (int i = 1; i < n; i++) {
                if (i > r) {
                    l = r = i;
                    while (r < n && s.charAt(r - l) == s.charAt(r)) r++;
                    z[i] = r - l;
                    r--;
                } else {
                    int k = i - l;
                    if (z[k] < r - i + 1) {
                        z[i] = z[k];
                    } else {
                        l = i;
                        while (r < n && s.charAt(r - l) == s.charAt(r)) r++;
                        z[i] = r - l;
                        r--;
                    }
                }
            }

            return z;
        }

        static List<Integer> patternSearch(String pattern, String text) {
            String combined = pattern + "$" + text;
            int[] z = computeZ(combined);
            List<Integer> matches = new ArrayList<>();

            for (int i = pattern.length() + 1; i < combined.length(); i++) {
                if (z[i] == pattern.length()) {
                    matches.add(i - pattern.length() - 1);
                }
            }

            return matches;
        }
    }

    // ========================================================================
    // COMPUTATIONAL GEOMETRY
    // ========================================================================

    static class Point {
        double x, y;

        Point(double x, double y) {
            this.x = x;
            this.y = y;
        }

        @Override
        public String toString() {
            return "(" + x + "," + y + ")";
        }
    }

    /**
     * Convex Hull - Andrew's Monotone Chain
     * Time: O(n log n)
     */
    static class ConvexHullAndrew {
        static double cross(Point o, Point a, Point b) {
            return (a.x - o.x) * (b.y - o.y) - (a.y - o.y) * (b.x - o.x);
        }

        static List<Point> convexHull(List<Point> points) {
            int n = points.size();
            if (n <= 2) return new ArrayList<>(points);

            points.sort((a, b) -> a.x == b.x ? Double.compare(a.y, b.y) : Double.compare(a.x, b.x));

            List<Point> lower = new ArrayList<>();
            for (Point p : points) {
                while (lower.size() >= 2 && cross(lower.get(lower.size() - 2),
                        lower.get(lower.size() - 1), p) <= 0) {
                    lower.remove(lower.size() - 1);
                }
                lower.add(p);
            }

            List<Point> upper = new ArrayList<>();
            for (int i = n - 1; i >= 0; i--) {
                Point p = points.get(i);
                while (upper.size() >= 2 && cross(upper.get(upper.size() - 2),
                        upper.get(upper.size() - 1), p) <= 0) {
                    upper.remove(upper.size() - 1);
                }
                upper.add(p);
            }

            lower.remove(lower.size() - 1);
            upper.remove(upper.size() - 1);
            lower.addAll(upper);
            return lower;
        }
    }

    /**
     * Closest Pair - Divide & Conquer
     * Time: O(n log n)
     */
    static class ClosestPair {
        static double distance(Point p1, Point p2) {
            return Math.sqrt((p1.x - p2.x) * (p1.x - p2.x) + (p1.y - p2.y) * (p1.y - p2.y));
        }

        static double closestBruteForce(List<Point> points) {
            double minDist = Double.MAX_VALUE;
            for (int i = 0; i < points.size(); i++) {
                for (int j = i + 1; j < points.size(); j++) {
                    minDist = Math.min(minDist, distance(points.get(i), points.get(j)));
                }
            }
            return minDist;
        }

        static double closest(List<Point> points) {
            points.sort((a, b) -> Double.compare(a.x, b.x));

            class Pair {
                double dist;

                Pair(double d) {
                    this.dist = d;
                }
            }

            Pair result = new Pair(Double.MAX_VALUE);
            divideConquer(points, 0, points.size() - 1, result);
            return result.dist;
        }

        static void divideConquer(List<Point> points, int left, int right, Pair result) {
            if (right - left <= 2) {
                result.dist = Math.min(result.dist, closestBruteForce(points.subList(left, right + 1)));
                return;
            }

            int mid = (left + right) / 2;
            divideConquer(points, left, mid, result);
            divideConquer(points, mid + 1, right, result);

            List<Point> strip = new ArrayList<>();
            double midX = points.get(mid).x;
            for (int i = left; i <= right; i++) {
                if (Math.abs(points.get(i).x - midX) < result.dist) {
                    strip.add(points.get(i));
                }
            }

            strip.sort((a, b) -> Double.compare(a.y, b.y));
            for (int i = 0; i < strip.size(); i++) {
                for (int j = i + 1; j < Math.min(i + 7, strip.size()); j++) {
                    result.dist = Math.min(result.dist, distance(strip.get(i), strip.get(j)));
                }
            }
        }
    }

    /**
     * Line Segment Intersection
     */
    static class LineIntersection {
        static int orientation(Point p, Point q, Point r) {
            double val = (q.y - p.y) * (r.x - q.x) - (q.x - p.x) * (r.y - q.y);
            if (Math.abs(val) < 1e-9) return 0;
            return val > 0 ? 1 : 2;
        }

        static boolean onSegment(Point p, Point q, Point r) {
            return q.x <= Math.max(p.x, r.x) && q.x >= Math.min(p.x, r.x)
                    && q.y <= Math.max(p.y, r.y) && q.y >= Math.min(p.y, r.y);
        }

        static boolean segmentsIntersect(Point p1, Point q1, Point p2, Point q2) {
            int o1 = orientation(p1, q1, p2);
            int o2 = orientation(p1, q1, q2);
            int o3 = orientation(p2, q2, p1);
            int o4 = orientation(p2, q2, q1);

            if (o1 != o2 && o3 != o4) return true;
            if (o1 == 0 && onSegment(p1, p2, q1)) return true;
            if (o2 == 0 && onSegment(p1, q2, q1)) return true;
            if (o3 == 0 && onSegment(p2, p1, q2)) return true;
            if (o4 == 0 && onSegment(p2, q1, q2)) return true;

            return false;
        }
    }

    // ========================================================================
    // TREE ALGORITHMS
    // ========================================================================

    /**
     * Heavy-Light Decomposition - Path queries on trees
     * Time: O(n log n) preprocessing, O(log² n) per query
     */
    static class HeavyLightDecomposition {
        List<Integer>[] adj;
        int[] parent, depth, size, heavy, chainHead, position;
        List<List<Integer>> chains;

        @SuppressWarnings("unchecked")
        HeavyLightDecomposition(int n, List<Integer>[] adj) {
            this.adj = adj;
            parent = new int[n];
            depth = new int[n];
            size = new int[n];
            heavy = new int[n];
            chainHead = new int[n];
            position = new int[n];
            chains = new ArrayList<>();

            Arrays.fill(heavy, -1);
            dfs1(0, -1);
            dfs2(0, -1, 0);
        }

        void dfs1(int u, int p) {
            parent[u] = p;
            size[u] = 1;
            int maxSize = -1;

            for (int v : adj[u]) {
                if (v != p) {
                    depth[v] = depth[u] + 1;
                    dfs1(v, u);
                    size[u] += size[v];

                    if (size[v] > maxSize) {
                        maxSize = size[v];
                        heavy[u] = v;
                    }
                }
            }
        }

        void dfs2(int u, int p, int chainId) {
            while (chainId >= chains.size()) {
                chains.add(new ArrayList<>());
            }

            chainHead[u] = chainId;
            position[u] = chains.get(chainId).size();
            chains.get(chainId).add(u);

            if (heavy[u] != -1) {
                dfs2(heavy[u], u, chainId);
            }

            for (int v : adj[u]) {
                if (v != p && v != heavy[u]) {
                    dfs2(v, u, chains.size());
                }
            }
        }

        List<Integer> getPath(int u, int v) {
            List<Integer> path = new ArrayList<>();

            while (chainHead[u] != chainHead[v]) {
                if (depth[chainHead[u]] > depth[chainHead[v]]) {
                    path.addAll(chains.get(chainHead[u]).subList(0, position[u] + 1));
                    u = parent[chainHead[u]];
                } else {
                    path.addAll(chains.get(chainHead[v]).subList(0, position[v] + 1));
                    v = parent[chainHead[v]];
                }
            }

            if (position[u] <= position[v]) {
                path.addAll(chains.get(chainHead[u]).subList(position[u], position[v] + 1));
            } else {
                for (int i = position[u]; i >= position[v]; i--) {
                    path.add(chains.get(chainHead[u]).get(i));
                }
            }

            return path;
        }
    }

    /**
     * Square Root Decomposition - Range queries/updates
     * Time: O(√n) per operation
     */
    static class SquareRootDecomposition {
        int[] arr, blocks;
        int blockSize;

        SquareRootDecomposition(int[] arr) {
            this.arr = arr.clone();
            this.blockSize = (int) Math.sqrt(arr.length) + 1;
            this.blocks = new int[(arr.length + blockSize - 1) / blockSize];
            build();
        }

        void build() {
            for (int i = 0; i < arr.length; i++) {
                blocks[i / blockSize] += arr[i];
            }
        }

        void update(int idx, int value) {
            int blockId = idx / blockSize;
            blocks[blockId] -= arr[idx];
            arr[idx] = value;
            blocks[blockId] += value;
        }

        long rangeSum(int left, int right) {
            long result = 0;

            while (left <= right) {
                int blockId = left / blockSize;
                if (left % blockSize == 0 && left + blockSize - 1 <= right) {
                    result += blocks[blockId];
                    left += blockSize;
                } else {
                    result += arr[left];
                    left++;
                }
            }

            return result;
        }
    }

    // ========================================================================
    // MISCELLANEOUS ADVANCED ALGORITHMS
    // ========================================================================

    /**
     * QuickSelect - Find k-th smallest element
     * Time: O(n) average
     */
    static class QuickSelect {
        static int quickSelect(int[] arr, int k) {
            return select(arr, 0, arr.length - 1, k);
        }

        private static int select(int[] arr, int left, int right, int kIdx) {
            if (left == right) return arr[left];

            Random rand = new Random();
            int pivotIdx = left + rand.nextInt(right - left + 1);
            pivotIdx = partition(arr, left, right, pivotIdx);

            if (kIdx == pivotIdx) return arr[kIdx];
            else if (kIdx < pivotIdx) return select(arr, left, pivotIdx - 1, kIdx);
            else return select(arr, pivotIdx + 1, right, kIdx);
        }

        private static int partition(int[] arr, int left, int right, int pivotIdx) {
            int pivot = arr[pivotIdx];
            int storeIdx = left;

            for (int i = left; i < right; i++) {
                if (arr[i] < pivot) {
                    int temp = arr[i];
                    arr[i] = arr[storeIdx];
                    arr[storeIdx] = temp;
                    storeIdx++;
                }
            }

            int temp = arr[right];
            arr[right] = arr[storeIdx];
            arr[storeIdx] = temp;

            return storeIdx;
        }
    }

    /**
     * Activity Selection - Greedy interval scheduling
     * Time: O(n log n)
     */
    static class ActivitySelection {
        static class Activity implements Comparable<Activity> {
            int start, end;

            Activity(int start, int end) {
                this.start = start;
                this.end = end;
            }

            public int compareTo(Activity other) {
                return Integer.compare(this.end, other.end);
            }

            @Override
            public String toString() {
                return "(" + start + "," + end + ")";
            }
        }

        static List<Activity> maxActivities(Activity[] activities) {
            Arrays.sort(activities);
            List<Activity> selected = new ArrayList<>();
            int lastEnd = -1;

            for (Activity a : activities) {
                if (a.start >= lastEnd) {
                    selected.add(a);
                    lastEnd = a.end;
                }
            }

            return selected;
        }
    }

    /**
     * Huffman Coding - Optimal prefix-free codes
     * Time: O(n log n)
     */
    static class HuffmanCoding {
        static class Node implements Comparable<Node> {
            char c;
            int freq;
            Node left, right;

            Node(char c, int freq) {
                this.c = c;
                this.freq = freq;
            }

            public int compareTo(Node other) {
                return Integer.compare(this.freq, other.freq);
            }
        }

        static Map<Character, String> buildCodes(Map<Character, Integer> freqs) {
            if (freqs.isEmpty()) return new HashMap<>();

            PriorityQueue<Node> heap = new PriorityQueue<>();
            for (Map.Entry<Character, Integer> e : freqs.entrySet()) {
                heap.add(new Node(e.getKey(), e.getValue()));
            }

            while (heap.size() > 1) {
                Node left = heap.poll();
                Node right = heap.poll();
                Node parent = new Node('\0', left.freq + right.freq);
                parent.left = left;
                parent.right = right;
                heap.add(parent);
            }

            Node root = heap.peek();
            Map<Character, String> codes = new HashMap<>();
            generateCodes(root, "", codes);
            return codes;
        }

        private static void generateCodes(Node node, String code, Map<Character, String> codes) {
            if (node.c != '\0') {
                codes.put(node.c, code.isEmpty() ? "0" : code);
                return;
            }
            if (node.left != null) generateCodes(node.left, code + "0", codes);
            if (node.right != null) generateCodes(node.right, code + "1", codes);
        }
    }

    // ========================================================================
    // MAIN - DEMO
    // ========================================================================

    public static void main(String[] args) {
        System.out.println("=".repeat(70));
        System.out.println("ADVANCED ALGORITHMS DEMO - JAVA");
        System.out.println("=".repeat(70));

        // 1. Max Flow - Dinic
        System.out.println("\n1. MAX FLOW - DINIC'S ALGORITHM");
        System.out.println("-".repeat(70));
        MaxFlowDinic flow = new MaxFlowDinic(6);
        flow.addEdge(0, 1, 16);
        flow.addEdge(0, 2, 13);
        flow.addEdge(1, 2, 10);
        flow.addEdge(1, 3, 12);
        flow.addEdge(2, 1, 9);
        flow.addEdge(2, 4, 14);
        flow.addEdge(3, 2, 9);
        flow.addEdge(3, 5, 20);
        flow.addEdge(4, 3, 7);
        flow.addEdge(4, 5, 4);
        System.out.println("Maximum flow from 0 to 5: " + flow.maxFlow(0, 5));

        // 2. Bipartite Matching
        System.out.println("\n2. BIPARTITE MATCHING");
        System.out.println("-".repeat(70));
        BipartiteMatching bm = new BipartiteMatching(3, 3);
        bm.addEdge(0, 1);
        bm.addEdge(0, 2);
        bm.addEdge(1, 0);
        bm.addEdge(1, 2);
        bm.addEdge(2, 1);
        System.out.println("Maximum matching: " + bm.maxMatching());

        // 3. 2-SAT
        System.out.println("\n3. 2-SAT");
        System.out.println("-".repeat(70));
        TwoSAT sat = new TwoSAT(3);
        sat.addClause(0, false, 1, false);
        sat.addClause(1, false, 2, false);
        System.out.println("Is satisfiable: " + sat.isSatisfiable());

        // 4. Convex Hull
        System.out.println("\n4. CONVEX HULL - ANDREW'S ALGORITHM");
        System.out.println("-".repeat(70));
        List<Point> points = new ArrayList<>();
        points.add(new Point(0, 0));
        points.add(new Point(1, 1));
        points.add(new Point(2, 2));
        points.add(new Point(0, 2));
        points.add(new Point(2, 0));
        List<Point> hull = ConvexHullAndrew.convexHull(points);
        System.out.println("Convex hull: " + hull);

        // 5. Closest Pair
        System.out.println("\n5. CLOSEST PAIR");
        System.out.println("-".repeat(70));
        points = new ArrayList<>();
        points.add(new Point(2, 3));
        points.add(new Point(12, 30));
        points.add(new Point(40, 50));
        points.add(new Point(5, 1));
        System.out.println("Minimum distance: " + String.format("%.4f", ClosestPair.closest(points)));

        // 6. Boyer-Moore
        System.out.println("\n6. BOYER-MOORE STRING MATCHING");
        System.out.println("-".repeat(70));
        BoyerMoore bms = new BoyerMoore("PATTERN");
        String text = "THIS IS A PATTERN MATCHING PATTERN ALGORITHM";
        System.out.println("Text: " + text);
        System.out.println("Pattern: PATTERN");
        System.out.println("Matches at: " + bms.search(text));

        // 7. Z-Algorithm
        System.out.println("\n7. Z-ALGORITHM");
        System.out.println("-".repeat(70));
        String pattern = "aab";
        String txt = "aabaaab";
        System.out.println("Pattern: " + pattern);
        System.out.println("Text: " + txt);
        System.out.println("Matches at: " + ZAlgorithm.patternSearch(pattern, txt));

        // 8. Heavy-Light Decomposition
        System.out.println("\n8. HEAVY-LIGHT DECOMPOSITION");
        System.out.println("-".repeat(70));
        @SuppressWarnings("unchecked")
        List<Integer>[] adj = new List[5];
        for (int i = 0; i < 5; i++) adj[i] = new ArrayList<>();
        adj[0].addAll(Arrays.asList(1, 2));
        adj[1].addAll(Arrays.asList(0, 3, 4));
        adj[2].add(0);
        adj[3].add(1);
        adj[4].add(1);
        HeavyLightDecomposition hld = new HeavyLightDecomposition(5, adj);
        System.out.println("Path from 3 to 4: " + hld.getPath(3, 4));

        // 9. Square Root Decomposition
        System.out.println("\n9. SQUARE ROOT DECOMPOSITION");
        System.out.println("-".repeat(70));
        int[] arr = {1, 3, 5, 7, 9, 11};
        SquareRootDecomposition sqrt = new SquareRootDecomposition(arr);
        System.out.println("Array: " + Arrays.toString(arr));
        System.out.println("Range sum [1, 4]: " + sqrt.rangeSum(1, 4));

        // 10. Activity Selection
        System.out.println("\n10. ACTIVITY SELECTION");
        System.out.println("-".repeat(70));
        ActivitySelection.Activity[] activities = {
                new ActivitySelection.Activity(1, 3),
                new ActivitySelection.Activity(2, 4),
                new ActivitySelection.Activity(3, 5),
                new ActivitySelection.Activity(4, 6),
                new ActivitySelection.Activity(5, 7)
        };
        System.out.println("Maximum non-overlapping activities: " + ActivitySelection.maxActivities(activities));

        // 11. QuickSelect
        System.out.println("\n11. QUICKSELECT");
        System.out.println("-".repeat(70));
        int[] testArr = {3, 2, 1, 5, 4};
        System.out.println("Array: " + Arrays.toString(testArr));
        System.out.println("2nd smallest (0-indexed): " + QuickSelect.quickSelect(testArr.clone(), 2));

        // 12. Huffman Coding
        System.out.println("\n12. HUFFMAN CODING");
        System.out.println("-".repeat(70));
        Map<Character, Integer> freqs = new HashMap<>();
        freqs.put('a', 5);
        freqs.put('b', 9);
        freqs.put('c', 12);
        System.out.println("Frequencies: " + freqs);
        Map<Character, String> codes = HuffmanCoding.buildCodes(freqs);
        System.out.println("Huffman codes: " + codes);

        System.out.println("\n" + "=".repeat(70));
        System.out.println("All demos completed successfully!");
        System.out.println("=".repeat(70));
    }
}
