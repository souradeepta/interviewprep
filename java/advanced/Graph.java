package advanced;

import java.util.*;

/**
 * Directed or undirected weighted graph using an adjacency list representation.
 *
 * <p>Vertices are identified by generic labels (type {@code V}).
 * Edges carry {@code double} weights; use weight 1.0 for unweighted graphs.
 *
 * <p>Supported operations and complexities (V = vertices, E = edges):
 * <ul>
 *   <li>addVertex       – O(1) amortized</li>
 *   <li>addEdge         – O(1) amortized</li>
 *   <li>removeEdge      – O(degree(u))</li>
 *   <li>bfs             – O(V + E)</li>
 *   <li>dfs             – O(V + E)</li>
 *   <li>hasCycle        – O(V + E)</li>
 *   <li>topologicalSort – O(V + E) (Kahn's algorithm, directed only)</li>
 *   <li>shortestPath    – O((V + E) log V) Dijkstra with binary heap</li>
 * </ul>
 *
 * <p>Space complexity: O(V + E).
 *
 * @param <V> vertex label type (must implement {@link Comparable} for deterministic output)
 */
public class Graph<V extends Comparable<V>> {

    // -------------------------------------------------------------------------
    // Edge helper
    // -------------------------------------------------------------------------

    /** Represents a weighted directed edge to {@code dest}. */
    private static class Edge<V> {
        V dest;
        double weight;

        Edge(V dest, double weight) {
            this.dest = dest;
            this.weight = weight;
        }

        @Override
        public String toString() {
            return dest + "(" + weight + ")";
        }
    }

    // -------------------------------------------------------------------------
    // Fields
    // -------------------------------------------------------------------------

    /** Adjacency list: vertex -> list of outgoing edges. */
    private final Map<V, List<Edge<V>>> adjList;
    private final boolean directed;
    private int edgeCount;

    // -------------------------------------------------------------------------
    // Constructor
    // -------------------------------------------------------------------------

    /**
     * Creates a new graph.
     *
     * @param directed {@code true} for a directed graph, {@code false} for undirected
     */
    public Graph(boolean directed) {
        this.directed = directed;
        adjList = new LinkedHashMap<>();
    }

    // -------------------------------------------------------------------------
    // addVertex
    // -------------------------------------------------------------------------

    /**
     * Adds a vertex to the graph.  If the vertex already exists this is a no-op.
     *
     * <p>Time: O(1) amortized.
     *
     * @param v the vertex label
     */
    public void addVertex(V v) {
        adjList.putIfAbsent(v, new ArrayList<>());
    }

    // -------------------------------------------------------------------------
    // addEdge
    // -------------------------------------------------------------------------

    /**
     * Adds a weighted edge between {@code u} and {@code v}.
     * For undirected graphs a reverse edge is also added.
     * Both vertices are created if they do not already exist.
     *
     * <p>Time: O(1) amortized.
     *
     * @param u      source vertex
     * @param v      destination vertex
     * @param weight edge weight
     */
    public void addEdge(V u, V v, double weight) {
        addVertex(u);
        addVertex(v);
        adjList.get(u).add(new Edge<>(v, weight));
        edgeCount++;
        if (!directed) {
            adjList.get(v).add(new Edge<>(u, weight));
        }
    }

    /**
     * Convenience overload: adds an unweighted edge (weight = 1.0).
     *
     * @param u source vertex
     * @param v destination vertex
     */
    public void addEdge(V u, V v) {
        addEdge(u, v, 1.0);
    }

    // -------------------------------------------------------------------------
    // removeEdge
    // -------------------------------------------------------------------------

    /**
     * Removes the edge from {@code u} to {@code v} (and the reverse for undirected).
     *
     * <p>Time: O(degree(u)) [ + O(degree(v)) for undirected ].
     *
     * @param u source
     * @param v destination
     * @return {@code true} if the edge existed and was removed
     */
    public boolean removeEdge(V u, V v) {
        List<Edge<V>> uList = adjList.get(u);
        if (uList == null) return false;
        boolean removed = uList.removeIf(e -> e.dest.equals(v));
        if (removed) {
            edgeCount--;
            if (!directed) {
                adjList.get(v).removeIf(e -> e.dest.equals(u));
            }
        }
        return removed;
    }

    // -------------------------------------------------------------------------
    // BFS
    // -------------------------------------------------------------------------

    /**
     * Returns the vertices reachable from {@code start} in BFS order.
     *
     * <p>Time: O(V + E) | Space: O(V).
     *
     * @param start the starting vertex
     * @return BFS traversal order
     */
    public List<V> bfs(V start) {
        List<V> order = new ArrayList<>();
        if (!adjList.containsKey(start)) return order;

        Set<V> visited = new LinkedHashSet<>();
        Queue<V> queue = new LinkedList<>();

        visited.add(start);
        queue.offer(start);

        while (!queue.isEmpty()) {
            V cur = queue.poll();
            order.add(cur);
            List<Edge<V>> neighbors = adjList.getOrDefault(cur, Collections.emptyList());
            // Sort neighbors for deterministic output
            neighbors.stream()
                     .map(e -> e.dest)
                     .filter(n -> !visited.contains(n))
                     .sorted()
                     .forEach(n -> { visited.add(n); queue.offer(n); });
        }
        return order;
    }

    // -------------------------------------------------------------------------
    // DFS
    // -------------------------------------------------------------------------

    /**
     * Returns the vertices reachable from {@code start} in DFS order.
     *
     * <p>Time: O(V + E) | Space: O(V).
     *
     * @param start the starting vertex
     * @return DFS traversal order
     */
    public List<V> dfs(V start) {
        List<V> order = new ArrayList<>();
        if (!adjList.containsKey(start)) return order;
        Set<V> visited = new LinkedHashSet<>();
        dfsRec(start, visited, order);
        return order;
    }

    private void dfsRec(V cur, Set<V> visited, List<V> order) {
        visited.add(cur);
        order.add(cur);
        adjList.getOrDefault(cur, Collections.emptyList())
               .stream()
               .map(e -> e.dest)
               .filter(n -> !visited.contains(n))
               .sorted()
               .forEach(n -> dfsRec(n, visited, order));
    }

    // -------------------------------------------------------------------------
    // hasCycle
    // -------------------------------------------------------------------------

    /**
     * Returns {@code true} if the graph contains at least one cycle.
     *
     * <p>For <em>directed</em> graphs uses DFS with a recursion stack (WHITE-GRAY-BLACK coloring).
     * For <em>undirected</em> graphs uses DFS tracking the parent to avoid trivial back-edges.
     *
     * <p>Time: O(V + E) | Space: O(V).
     *
     * @return {@code true} if a cycle exists
     */
    public boolean hasCycle() {
        Set<V> visited = new HashSet<>();
        if (directed) {
            Set<V> recStack = new HashSet<>();
            for (V v : adjList.keySet()) {
                if (!visited.contains(v) && hasCycleDirected(v, visited, recStack)) return true;
            }
        } else {
            for (V v : adjList.keySet()) {
                if (!visited.contains(v) && hasCycleUndirected(v, null, visited)) return true;
            }
        }
        return false;
    }

    private boolean hasCycleDirected(V cur, Set<V> visited, Set<V> recStack) {
        visited.add(cur);
        recStack.add(cur);
        for (Edge<V> e : adjList.getOrDefault(cur, Collections.emptyList())) {
            if (!visited.contains(e.dest)) {
                if (hasCycleDirected(e.dest, visited, recStack)) return true;
            } else if (recStack.contains(e.dest)) {
                return true;
            }
        }
        recStack.remove(cur);
        return false;
    }

    private boolean hasCycleUndirected(V cur, V parent, Set<V> visited) {
        visited.add(cur);
        for (Edge<V> e : adjList.getOrDefault(cur, Collections.emptyList())) {
            if (!visited.contains(e.dest)) {
                if (hasCycleUndirected(e.dest, cur, visited)) return true;
            } else if (!e.dest.equals(parent)) {
                return true;
            }
        }
        return false;
    }

    // -------------------------------------------------------------------------
    // Topological Sort (Kahn's algorithm – directed graphs only)
    // -------------------------------------------------------------------------

    /**
     * Returns a topological ordering of the vertices (directed acyclic graphs only).
     *
     * <p>Uses Kahn's BFS-based algorithm.  If the graph has a cycle, returns an
     * empty list (not all vertices can be ordered).
     *
     * <p>Time: O(V + E) | Space: O(V).
     *
     * @return topological order, or empty list if a cycle exists / graph is undirected
     */
    public List<V> topologicalSort() {
        if (!directed) throw new UnsupportedOperationException("Topological sort requires a directed graph");

        // Compute in-degrees
        Map<V, Integer> inDegree = new LinkedHashMap<>();
        for (V v : adjList.keySet()) inDegree.put(v, 0);
        for (V u : adjList.keySet()) {
            for (Edge<V> e : adjList.get(u)) {
                inDegree.merge(e.dest, 1, Integer::sum);
            }
        }

        // Enqueue all zero-in-degree vertices (sorted for determinism)
        PriorityQueue<V> pq = new PriorityQueue<>();
        for (Map.Entry<V, Integer> entry : inDegree.entrySet()) {
            if (entry.getValue() == 0) pq.offer(entry.getKey());
        }

        List<V> order = new ArrayList<>();
        while (!pq.isEmpty()) {
            V cur = pq.poll();
            order.add(cur);
            for (Edge<V> e : adjList.getOrDefault(cur, Collections.emptyList())) {
                int newDeg = inDegree.merge(e.dest, -1, Integer::sum);
                if (newDeg == 0) pq.offer(e.dest);
            }
        }

        return order.size() == adjList.size() ? order : Collections.emptyList();
    }

    // -------------------------------------------------------------------------
    // Dijkstra's Shortest Path
    // -------------------------------------------------------------------------

    /**
     * Computes the shortest (minimum weight) path from {@code source} to all
     * other reachable vertices using Dijkstra's algorithm.
     *
     * <p>Assumes non-negative edge weights.
     *
     * <p>Time: O((V + E) log V) | Space: O(V).
     *
     * @param source the starting vertex
     * @return map from vertex to its shortest distance from {@code source};
     *         unreachable vertices map to {@link Double#POSITIVE_INFINITY}
     */
    public Map<V, Double> shortestPath(V source) {
        Map<V, Double> dist  = new HashMap<>();
        Map<V, V>      prev  = new HashMap<>();
        // Min-heap: [distance, vertex] – using a simple wrapper pair
        PriorityQueue<double[]> pq = new PriorityQueue<>(Comparator.comparingDouble(a -> a[0]));
        // We encode vertex index via a parallel index map
        List<V> vertices = new ArrayList<>(adjList.keySet());
        Map<V, Integer> indexMap = new HashMap<>();
        for (int i = 0; i < vertices.size(); i++) indexMap.put(vertices.get(i), i);

        for (V v : adjList.keySet()) dist.put(v, Double.POSITIVE_INFINITY);
        dist.put(source, 0.0);
        pq.offer(new double[]{0.0, indexMap.getOrDefault(source, -1)});

        while (!pq.isEmpty()) {
            double[] top = pq.poll();
            double d = top[0];
            int idx = (int) top[1];
            if (idx < 0 || idx >= vertices.size()) continue;
            V cur = vertices.get(idx);
            if (d > dist.get(cur)) continue; // stale entry

            for (Edge<V> e : adjList.getOrDefault(cur, Collections.emptyList())) {
                double newDist = dist.get(cur) + e.weight;
                if (newDist < dist.getOrDefault(e.dest, Double.POSITIVE_INFINITY)) {
                    dist.put(e.dest, newDist);
                    prev.put(e.dest, cur);
                    pq.offer(new double[]{newDist, indexMap.getOrDefault(e.dest, -1)});
                }
            }
        }
        return dist;
    }

    /**
     * Returns the shortest path (list of vertices) from {@code source} to {@code dest}.
     *
     * <p>Time: O((V + E) log V) | Space: O(V).
     *
     * @param source start
     * @param dest   end
     * @return ordered list of vertices on the shortest path, or empty list if unreachable
     */
    public List<V> shortestPathTo(V source, V dest) {
        // Re-run Dijkstra tracking predecessors
        Map<V, Double> dist = new HashMap<>();
        Map<V, V>      prev = new HashMap<>();
        List<V> vertices = new ArrayList<>(adjList.keySet());
        Map<V, Integer> indexMap = new HashMap<>();
        for (int i = 0; i < vertices.size(); i++) indexMap.put(vertices.get(i), i);

        for (V v : adjList.keySet()) dist.put(v, Double.POSITIVE_INFINITY);
        dist.put(source, 0.0);
        PriorityQueue<double[]> pq = new PriorityQueue<>(Comparator.comparingDouble(a -> a[0]));
        pq.offer(new double[]{0.0, indexMap.getOrDefault(source, -1)});

        while (!pq.isEmpty()) {
            double[] top = pq.poll();
            double d = top[0];
            int idx = (int) top[1];
            if (idx < 0 || idx >= vertices.size()) continue;
            V cur = vertices.get(idx);
            if (d > dist.get(cur)) continue;
            for (Edge<V> e : adjList.getOrDefault(cur, Collections.emptyList())) {
                double nd = dist.get(cur) + e.weight;
                if (nd < dist.getOrDefault(e.dest, Double.POSITIVE_INFINITY)) {
                    dist.put(e.dest, nd);
                    prev.put(e.dest, cur);
                    pq.offer(new double[]{nd, indexMap.getOrDefault(e.dest, -1)});
                }
            }
        }

        // Reconstruct path
        LinkedList<V> path = new LinkedList<>();
        V cur = dest;
        while (cur != null) {
            path.addFirst(cur);
            cur = prev.get(cur);
        }
        return path.getFirst().equals(source) ? path : Collections.emptyList();
    }

    // -------------------------------------------------------------------------
    // Accessors
    // -------------------------------------------------------------------------

    /** Returns the number of vertices. */
    public int vertexCount() { return adjList.size(); }

    /** Returns the number of edges (directed count for directed graphs). */
    public int edgeCount() { return edgeCount; }

    /** Returns true if the graph is directed. */
    public boolean isDirected() { return directed; }

    // -------------------------------------------------------------------------
    // toString – adjacency list view
    // -------------------------------------------------------------------------

    /**
     * Returns a human-readable adjacency list representation.
     *
     * <p>Time: O(V + E) | Space: O(V + E).
     *
     * @return adjacency list string
     */
    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append(directed ? "Directed" : "Undirected")
          .append(" Graph (V=").append(vertexCount())
          .append(", E=").append(edgeCount).append("):\n");
        for (Map.Entry<V, List<Edge<V>>> entry : adjList.entrySet()) {
            sb.append("  ").append(entry.getKey()).append(" -> ")
              .append(entry.getValue()).append("\n");
        }
        return sb.toString();
    }

    // -------------------------------------------------------------------------
    // Main – demo
    // -------------------------------------------------------------------------

    public static void main(String[] args) {
        System.out.println("=== Graph Demo ===\n");

        // --- Directed weighted graph ---
        Graph<String> dg = new Graph<>(true);
        dg.addEdge("A", "B", 4);
        dg.addEdge("A", "C", 2);
        dg.addEdge("B", "C", 5);
        dg.addEdge("B", "D", 10);
        dg.addEdge("C", "E", 3);
        dg.addEdge("E", "D", 4);
        dg.addEdge("D", "F", 11);

        System.out.println(dg);
        System.out.println("BFS from A  : " + dg.bfs("A"));
        System.out.println("DFS from A  : " + dg.dfs("A"));
        System.out.println("Has cycle   : " + dg.hasCycle());
        System.out.println("Topo sort   : " + dg.topologicalSort());

        Map<String, Double> dist = dg.shortestPath("A");
        System.out.println("\nDijkstra from A:");
        new TreeMap<>(dist).forEach((v, d) -> System.out.println("  A -> " + v + " : " + d));

        System.out.println("\nShortest path A -> F : " + dg.shortestPathTo("A", "F"));

        // --- Undirected graph with cycle ---
        Graph<Integer> ug = new Graph<>(false);
        ug.addEdge(1, 2);
        ug.addEdge(2, 3);
        ug.addEdge(3, 4);
        ug.addEdge(4, 2); // creates a cycle 2-3-4-2
        System.out.println("\n" + ug);
        System.out.println("Has cycle   : " + ug.hasCycle());
        System.out.println("BFS from 1  : " + ug.bfs(1));
        System.out.println("DFS from 1  : " + ug.dfs(1));

        // removeEdge demo
        System.out.println("\nRemove edge 4-2...");
        ug.removeEdge(4, 2);
        System.out.println("Has cycle after removal: " + ug.hasCycle());
        System.out.println(ug);

        // DAG topological sort
        Graph<String> dag = new Graph<>(true);
        dag.addEdge("wash", "dry");
        dag.addEdge("wash", "fold");
        dag.addEdge("dry",  "fold");
        dag.addEdge("fold", "put away");
        System.out.println("\nDAG topo sort (laundry): " + dag.topologicalSort());
    }
}
