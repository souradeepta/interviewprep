package algorithms.graph;

import java.util.*;

/**
 * GraphAlgorithms — collection of fundamental graph algorithm implementations.
 *
 * <p>Included algorithms:
 * <ul>
 *   <li>Dijkstra's shortest path — O((V + E) log V)</li>
 *   <li>Bellman-Ford shortest path — O(V * E)</li>
 *   <li>Floyd-Warshall all-pairs shortest path — O(V^3)</li>
 *   <li>Kruskal's MST — O(E log E)</li>
 *   <li>Prim's MST — O((V + E) log V)</li>
 *   <li>Tarjan's SCC — O(V + E)</li>
 *   <li>Topological Sort (Kahn's BFS) — O(V + E)</li>
 *   <li>A* grid path search — O(E log V) with Manhattan heuristic</li>
 * </ul>
 */
public class GraphAlgorithms {

    // -----------------------------------------------------------------------
    // 1. Dijkstra's Algorithm
    // -----------------------------------------------------------------------

    /**
     * Single-source shortest paths using a min-heap priority queue.
     *
     * <p>Complexity: Time O((V + E) log V), Space O(V + E).
     * Does NOT handle negative edge weights.
     *
     * @param graph adjacency list: node -> list of {neighbor, weight}
     * @param start source node (0-indexed)
     * @param n     total number of nodes
     * @return int[] dist where dist[i] is the shortest distance from start to i;
     *         unreachable nodes have Integer.MAX_VALUE
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public static int[] dijkstra(Map<Integer, List<int[]>> graph, int start, int n) {
        int[] dist = new int[n];
        Arrays.fill(dist, Integer.MAX_VALUE);
        dist[start] = 0;

        // min-heap: {distance, node}
        PriorityQueue<int[]> pq = new PriorityQueue<>(Comparator.comparingInt(a -> a[0]));
        pq.offer(new int[]{0, start});

        while (!pq.isEmpty()) {
            int[] curr = pq.poll();
            int d = curr[0], u = curr[1];

            if (d > dist[u]) continue; // stale entry

            List<int[]> neighbors = graph.getOrDefault(u, Collections.emptyList());
            for (int[] edge : neighbors) {
                int v = edge[0], w = edge[1];
                if (dist[u] != Integer.MAX_VALUE && dist[u] + w < dist[v]) {
                    dist[v] = dist[u] + w;
                    pq.offer(new int[]{dist[v], v});
                }
            }
        }
        return dist;
    }

    // -----------------------------------------------------------------------
    // 2. Bellman-Ford
    // -----------------------------------------------------------------------

    /**
     * Single-source shortest paths that handles negative edge weights.
     *
     * <p>Complexity: Time O(V * E), Space O(V).
     *
     * @param n     number of nodes (0-indexed: 0..n-1)
     * @param edges array of {u, v, w} directed edges
     * @param start source node
     * @return Object[] with two elements: int[] dist and boolean hasNegCycle.
     *         Access as {@code (int[]) result[0]} and {@code (boolean) result[1]}.
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public static Object[] bellmanFord(int n, int[][] edges, int start) {
        int[] dist = new int[n];
        Arrays.fill(dist, Integer.MAX_VALUE);
        dist[start] = 0;

        // Relax all edges V-1 times
        for (int i = 0; i < n - 1; i++) {
            for (int[] edge : edges) {
                int u = edge[0], v = edge[1], w = edge[2];
                if (dist[u] != Integer.MAX_VALUE && dist[u] + w < dist[v]) {
                    dist[v] = dist[u] + w;
                }
            }
        }

        // Check for negative-weight cycles (V-th relaxation)
        boolean hasNegCycle = false;
        for (int[] edge : edges) {
            int u = edge[0], v = edge[1], w = edge[2];
            if (dist[u] != Integer.MAX_VALUE && dist[u] + w < dist[v]) {
                hasNegCycle = true;
                break;
            }
        }

        return new Object[]{dist, hasNegCycle};
    }

    // -----------------------------------------------------------------------
    // 3. Floyd-Warshall
    // -----------------------------------------------------------------------

    /**
     * All-pairs shortest paths via dynamic programming.
     *
     * <p>Complexity: Time O(V^3), Space O(1) extra (modifies in place).
     * Use Integer.MAX_VALUE / 2 to represent no edge (avoids overflow).
     *
     * @param matrix n x n adjacency matrix; matrix[i][i] == 0,
     *               matrix[i][j] == INF if no direct edge
     * @return the same matrix, updated with shortest path distances
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public static int[][] floydWarshall(int[][] matrix) {
        int n = matrix.length;
        final int INF = Integer.MAX_VALUE / 2;

        for (int k = 0; k < n; k++) {
            for (int i = 0; i < n; i++) {
                for (int j = 0; j < n; j++) {
                    if (matrix[i][k] < INF && matrix[k][j] < INF) {
                        matrix[i][j] = Math.min(matrix[i][j], matrix[i][k] + matrix[k][j]);
                    }
                }
            }
        }
        return matrix;
    }

    // -----------------------------------------------------------------------
    // 4. Kruskal's MST
    // -----------------------------------------------------------------------

    /** Union-Find (Disjoint Set Union) with path compression and union by rank. */
    private static class UnionFind {
        int[] parent, rank;

        UnionFind(int n) {
            parent = new int[n];
            rank = new int[n];
            for (int i = 0; i < n; i++) parent[i] = i;
        }

        int find(int x) {
            if (parent[x] != x) parent[x] = find(parent[x]);
            return parent[x];
        }

        boolean union(int x, int y) {
            int px = find(x), py = find(y);
            if (px == py) return false;
            if (rank[px] < rank[py]) { int t = px; px = py; py = t; }
            parent[py] = px;
            if (rank[px] == rank[py]) rank[px]++;
            return true;
        }
    }

    /**
     * Minimum Spanning Tree using Kruskal's algorithm.
     *
     * <p>Complexity: Time O(E log E), Space O(V).
     *
     * @param n     number of nodes
     * @param edges array of {u, v, w} undirected edges
     * @return Object[] with (List&lt;int[]&gt; mstEdges, int totalWeight).
     *         mstEdges contains {u, v, w} for each chosen edge.
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public static Object[] kruskalMST(int n, int[][] edges) {
        // Sort edges by weight
        int[][] sorted = edges.clone();
        Arrays.sort(sorted, Comparator.comparingInt(e -> e[2]));

        UnionFind uf = new UnionFind(n);
        List<int[]> mstEdges = new ArrayList<>();
        int totalWeight = 0;

        for (int[] edge : sorted) {
            int u = edge[0], v = edge[1], w = edge[2];
            if (uf.union(u, v)) {
                mstEdges.add(new int[]{u, v, w});
                totalWeight += w;
                if (mstEdges.size() == n - 1) break;
            }
        }
        return new Object[]{mstEdges, totalWeight};
    }

    // -----------------------------------------------------------------------
    // 5. Prim's MST
    // -----------------------------------------------------------------------

    /**
     * Minimum Spanning Tree using Prim's algorithm with a min-heap.
     *
     * <p>Complexity: Time O((V + E) log V), Space O(V + E).
     *
     * @param graph adjacency list: node -> list of {neighbor, weight}
     * @param start starting node
     * @param n     total number of nodes
     * @return List of int[] {u, v, w} representing MST edges
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public static List<int[]> primMST(Map<Integer, List<int[]>> graph, int start, int n) {
        boolean[] inMST = new boolean[n];
        // min-heap: {weight, node, parent}
        PriorityQueue<int[]> pq = new PriorityQueue<>(Comparator.comparingInt(a -> a[0]));
        pq.offer(new int[]{0, start, -1});

        List<int[]> mstEdges = new ArrayList<>();

        while (!pq.isEmpty() && mstEdges.size() < n) {
            int[] curr = pq.poll();
            int w = curr[0], u = curr[1], par = curr[2];

            if (inMST[u]) continue;
            inMST[u] = true;

            if (par != -1) {
                mstEdges.add(new int[]{par, u, w});
            }

            for (int[] edge : graph.getOrDefault(u, Collections.emptyList())) {
                int v = edge[0], ew = edge[1];
                if (!inMST[v]) {
                    pq.offer(new int[]{ew, v, u});
                }
            }
        }
        return mstEdges;
    }

    // -----------------------------------------------------------------------
    // 6. Tarjan's SCC
    // -----------------------------------------------------------------------

    private static int sccTimer;
    private static int[] sccId, low, disc;
    private static boolean[] onStack;
    private static Deque<Integer> sccStack;
    private static List<List<Integer>> sccs;

    /**
     * Finds all Strongly Connected Components using Tarjan's algorithm.
     *
     * <p>Complexity: Time O(V + E), Space O(V).
     *
     * @param graph directed adjacency list: node -> list of neighbors
     * @param n     number of nodes (0-indexed)
     * @return List of SCCs, each SCC is a List of node indices
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public static List<List<Integer>> tarjanSCC(Map<Integer, List<Integer>> graph, int n) {
        sccTimer = 0;
        disc = new int[n];
        low = new int[n];
        sccId = new int[n];
        onStack = new boolean[n];
        sccStack = new ArrayDeque<>();
        sccs = new ArrayList<>();
        Arrays.fill(disc, -1);

        for (int i = 0; i < n; i++) {
            if (disc[i] == -1) {
                tarjanDfs(graph, i);
            }
        }
        return sccs;
    }

    private static void tarjanDfs(Map<Integer, List<Integer>> graph, int u) {
        disc[u] = low[u] = sccTimer++;
        sccStack.push(u);
        onStack[u] = true;

        for (int v : graph.getOrDefault(u, Collections.emptyList())) {
            if (disc[v] == -1) {
                tarjanDfs(graph, v);
                low[u] = Math.min(low[u], low[v]);
            } else if (onStack[v]) {
                low[u] = Math.min(low[u], disc[v]);
            }
        }

        // u is root of an SCC
        if (low[u] == disc[u]) {
            List<Integer> scc = new ArrayList<>();
            while (true) {
                int w = sccStack.pop();
                onStack[w] = false;
                scc.add(w);
                if (w == u) break;
            }
            sccs.add(scc);
        }
    }

    // -----------------------------------------------------------------------
    // 7. Topological Sort (Kahn's BFS)
    // -----------------------------------------------------------------------

    /**
     * Topological ordering of a DAG using Kahn's BFS algorithm.
     *
     * <p>Complexity: Time O(V + E), Space O(V).
     *
     * @param graph directed adjacency list: node -> list of neighbors
     * @param n     number of nodes (0-indexed)
     * @return int[] topological order, or empty array if cycle detected
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public static int[] topologicalSortKahn(Map<Integer, List<Integer>> graph, int n) {
        int[] inDegree = new int[n];
        for (int u = 0; u < n; u++) {
            for (int v : graph.getOrDefault(u, Collections.emptyList())) {
                inDegree[v]++;
            }
        }

        Queue<Integer> queue = new LinkedList<>();
        for (int i = 0; i < n; i++) {
            if (inDegree[i] == 0) queue.offer(i);
        }

        int[] order = new int[n];
        int idx = 0;

        while (!queue.isEmpty()) {
            int u = queue.poll();
            order[idx++] = u;
            for (int v : graph.getOrDefault(u, Collections.emptyList())) {
                if (--inDegree[v] == 0) queue.offer(v);
            }
        }

        if (idx != n) {
            System.out.println("Cycle detected — topological sort not possible.");
            return new int[0];
        }
        return order;
    }

    // -----------------------------------------------------------------------
    // 8. A* Search
    // -----------------------------------------------------------------------

    /**
     * A* pathfinding on a 2-D grid using the Manhattan distance heuristic.
     *
     * <p>Complexity: Time O(V log V) where V = rows * cols.
     * Cells with value 1 are obstacles.
     *
     * @param grid  2-D grid (0 = open, 1 = wall)
     * @param start int[]{row, col}
     * @param end   int[]{row, col}
     * @return List of int[]{row, col} path from start to end (inclusive),
     *         or empty list if no path exists
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public static List<int[]> astar(int[][] grid, int[] start, int[] end) {
        int rows = grid.length, cols = grid[0].length;
        int[][] gScore = new int[rows][cols];
        int[][] fScore = new int[rows][cols];
        int[][] parent = new int[rows * cols][2];

        for (int[] row : gScore) Arrays.fill(row, Integer.MAX_VALUE);
        for (int[] row : fScore) Arrays.fill(row, Integer.MAX_VALUE);
        for (int[] p : parent) Arrays.fill(p, -1);

        int sr = start[0], sc = start[1], er = end[0], ec = end[1];
        gScore[sr][sc] = 0;
        fScore[sr][sc] = manhattan(sr, sc, er, ec);

        // min-heap: {fScore, row, col}
        PriorityQueue<int[]> open = new PriorityQueue<>(Comparator.comparingInt(a -> a[0]));
        open.offer(new int[]{fScore[sr][sc], sr, sc});

        boolean[][] closed = new boolean[rows][cols];
        int[][] dirs = {{-1,0},{1,0},{0,-1},{0,1}};

        while (!open.isEmpty()) {
            int[] curr = open.poll();
            int r = curr[1], c = curr[2];

            if (r == er && c == ec) {
                return reconstructPath(parent, rows, cols, sr, sc, er, ec);
            }

            if (closed[r][c]) continue;
            closed[r][c] = true;

            for (int[] d : dirs) {
                int nr = r + d[0], nc = c + d[1];
                if (nr < 0 || nr >= rows || nc < 0 || nc >= cols) continue;
                if (grid[nr][nc] == 1 || closed[nr][nc]) continue;

                int tentG = gScore[r][c] + 1;
                if (tentG < gScore[nr][nc]) {
                    gScore[nr][nc] = tentG;
                    fScore[nr][nc] = tentG + manhattan(nr, nc, er, ec);
                    parent[nr * cols + nc][0] = r;
                    parent[nr * cols + nc][1] = c;
                    open.offer(new int[]{fScore[nr][nc], nr, nc});
                }
            }
        }
        return Collections.emptyList(); // no path
    }

    private static int manhattan(int r1, int c1, int r2, int c2) {
        return Math.abs(r1 - r2) + Math.abs(c1 - c2);
    }

    private static List<int[]> reconstructPath(int[][] parent, int rows, int cols,
                                                int sr, int sc, int er, int ec) {
        List<int[]> path = new ArrayList<>();
        int r = er, c = ec;
        while (!(r == sr && c == sc)) {
            path.add(new int[]{r, c});
            int pr = parent[r * cols + c][0];
            int pc = parent[r * cols + c][1];
            r = pr; c = pc;
        }
        path.add(new int[]{sr, sc});
        Collections.reverse(path);
        return path;
    }

    // -----------------------------------------------------------------------
    // Main demo
    // -----------------------------------------------------------------------

    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public static void main(String[] args) {
        System.out.println("=== Dijkstra ===");
        Map<Integer, List<int[]>> g1 = new HashMap<>();
        g1.put(0, Arrays.asList(new int[]{1,4}, new int[]{2,1}));
        g1.put(1, Arrays.asList(new int[]{3,1}));
        g1.put(2, Arrays.asList(new int[]{1,2}, new int[]{3,5}));
        g1.put(3, Collections.emptyList());
        int[] dist = dijkstra(g1, 0, 4);
        System.out.println("Dist from 0: " + Arrays.toString(dist));
        // Expected: [0, 3, 1, 4]

        System.out.println("\n=== Bellman-Ford ===");
        int[][] bfEdges = {{0,1,4},{0,2,1},{2,1,2},{1,3,1},{2,3,5}};
        Object[] bfResult = bellmanFord(4, bfEdges, 0);
        System.out.println("Dist: " + Arrays.toString((int[]) bfResult[0]));
        System.out.println("Negative cycle: " + bfResult[1]);

        int[][] negEdges = {{0,1,1},{1,2,-1},{2,0,-1}};
        Object[] negResult = bellmanFord(3, negEdges, 0);
        System.out.println("Neg-cycle graph, hasNegCycle: " + negResult[1]);

        System.out.println("\n=== Floyd-Warshall ===");
        final int INF = Integer.MAX_VALUE / 2;
        int[][] fw = {
            {0,   3, INF, 5},
            {2,   0, INF, 4},
            {INF, 1,   0, INF},
            {INF, INF, 2, 0}
        };
        floydWarshall(fw);
        System.out.println("All-pairs distances:");
        for (int[] row : fw) System.out.println(Arrays.toString(row));

        System.out.println("\n=== Kruskal MST ===");
        int[][] kEdges = {{0,1,10},{0,2,6},{0,3,5},{1,3,15},{2,3,4}};
        Object[] mst = kruskalMST(4, kEdges);
        @SuppressWarnings("unchecked")
        List<int[]> kMSTEdges = (List<int[]>) mst[0];
        System.out.println("Total weight: " + mst[1]);
        for (int[] e : kMSTEdges) System.out.println("  " + e[0] + "-" + e[1] + " w=" + e[2]);

        System.out.println("\n=== Prim MST ===");
        Map<Integer, List<int[]>> pGraph = new HashMap<>();
        pGraph.put(0, Arrays.asList(new int[]{1,10}, new int[]{2,6}, new int[]{3,5}));
        pGraph.put(1, Arrays.asList(new int[]{0,10}, new int[]{3,15}));
        pGraph.put(2, Arrays.asList(new int[]{0,6}, new int[]{3,4}));
        pGraph.put(3, Arrays.asList(new int[]{0,5}, new int[]{1,15}, new int[]{2,4}));
        List<int[]> primEdges = primMST(pGraph, 0, 4);
        int primTotal = 0;
        for (int[] e : primEdges) { System.out.println("  " + e[0] + "-" + e[1] + " w=" + e[2]); primTotal += e[2]; }
        System.out.println("Total weight: " + primTotal);

        System.out.println("\n=== Tarjan SCC ===");
        Map<Integer, List<Integer>> sccGraph = new HashMap<>();
        sccGraph.put(0, Arrays.asList(1));
        sccGraph.put(1, Arrays.asList(2));
        sccGraph.put(2, Arrays.asList(0, 3));
        sccGraph.put(3, Arrays.asList(4));
        sccGraph.put(4, Arrays.asList(5));
        sccGraph.put(5, Arrays.asList(3));
        List<List<Integer>> sccs = tarjanSCC(sccGraph, 6);
        System.out.println("SCCs: " + sccs);

        System.out.println("\n=== Topological Sort (Kahn) ===");
        Map<Integer, List<Integer>> dag = new HashMap<>();
        dag.put(5, Arrays.asList(2, 0));
        dag.put(4, Arrays.asList(0, 1));
        dag.put(2, Arrays.asList(3));
        dag.put(3, Arrays.asList(1));
        dag.put(0, Collections.emptyList());
        dag.put(1, Collections.emptyList());
        int[] topoOrder = topologicalSortKahn(dag, 6);
        System.out.println("Topo order: " + Arrays.toString(topoOrder));

        System.out.println("\n=== A* Search ===");
        int[][] grid = {
            {0, 0, 0, 0, 0},
            {0, 1, 1, 1, 0},
            {0, 0, 0, 1, 0},
            {0, 1, 0, 0, 0},
            {0, 0, 0, 0, 0}
        };
        List<int[]> path = astar(grid, new int[]{0, 0}, new int[]{4, 4});
        System.out.print("Path: ");
        for (int[] cell : path) System.out.print("[" + cell[0] + "," + cell[1] + "] ");
        System.out.println();
    }
}
