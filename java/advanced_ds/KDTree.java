package advanced_ds;

import java.util.*;

/**
 * KD-Tree (K-Dimensional Tree)
 *
 * Time Complexity:
 * - Construction: O(n log n)
 * - Nearest neighbor search: O(log n) average, O(n) worst case
 * - Range query: O(sqrt(n) + k) where k = number of results
 * - Point insertion: O(log n) average
 * - Point deletion: O(log n) average
 *
 * Space Complexity: O(n)
 *
 * Use Cases:
 * - Nearest neighbor search (k-NN)
 * - Range searching (all points in rectangle)
 * - Spatial indexing (databases)
 * - Clustering algorithms
 * - Graphics and gaming (collision detection)
 *
 * Key Insight:
 * - Recursively partition space using alternating dimensions
 * - At depth d, split on dimension d mod k
 * - Pruning: skip subtrees when bounding box is far from query point
 * - Balance depends on insertion order
 */
public class KDTree {

    static class Node {
        double[] point;
        int depth;
        int k;
        Node left, right;

        Node(double[] point, int depth, int k) {
            this.point = point.clone();
            this.depth = depth;
            this.k = k;
        }

        int getAxis() {
            return depth % k;
        }
    }

    private Node root;
    private int k;

    /**
     * Initialize KD-Tree.
     *
     * @param points List of points (each point is array of coordinates)
     */
    public KDTree(List<double[]> points) {
        if (points.isEmpty()) {
            this.k = 0;
            this.root = null;
        } else {
            this.k = points.get(0).length;
            this.root = buildTree(new ArrayList<>(points), 0);
        }
    }

    /**
     * Build KD-Tree recursively.
     */
    private Node buildTree(List<double[]> points, int depth) {
        if (points.isEmpty()) {
            return null;
        }

        int axis = depth % k;
        points.sort((a, b) -> Double.compare(a[axis], b[axis]));

        int median = points.size() / 2;
        Node node = new Node(points.get(median), depth, k);

        node.left = buildTree(new ArrayList<>(points.subList(0, median)), depth + 1);
        node.right = buildTree(new ArrayList<>(points.subList(median + 1, points.size())), depth + 1);

        return node;
    }

    /**
     * Result class for nearest neighbor search.
     */
    public static class NearestNeighbor {
        public double[] point;
        public double distance;

        NearestNeighbor(double[] point, double distance) {
            this.point = point;
            this.distance = distance;
        }

        @Override
        public String toString() {
            return String.format("%s (dist: %.2f)", Arrays.toString(point), distance);
        }
    }

    /**
     * Find nearest point in tree.
     *
     * @param point Query point
     * @return Nearest neighbor info
     */
    public NearestNeighbor nearestNeighbor(double[] point) {
        if (root == null) {
            return null;
        }

        double[] best = {Double.POSITIVE_INFINITY};
        double[] bestPoint = {null};

        nearestNeighborRecursive(root, point, best, bestPoint);

        return bestPoint[0] == null ? null : new NearestNeighbor(
                (double[]) bestPoint[0], best[0]);
    }

    /**
     * Recursive helper for nearest neighbor.
     */
    private void nearestNeighborRecursive(Node node, double[] point,
                                          double[] best, double[] bestPoint) {
        if (node == null) {
            return;
        }

        double distance = distance(point, node.point);
        if (distance < best[0]) {
            best[0] = distance;
            bestPoint[0] = node.point;
        }

        int axis = node.getAxis();
        double diff = point[axis] - node.point[axis];

        Node nearNode = diff < 0 ? node.left : node.right;
        Node farNode = diff < 0 ? node.right : node.left;

        nearestNeighborRecursive(nearNode, point, best, bestPoint);

        if (Math.abs(diff) < best[0]) {
            nearestNeighborRecursive(farNode, point, best, bestPoint);
        }
    }

    /**
     * Find k nearest neighbors.
     *
     * @param point Query point
     * @param k Number of neighbors
     * @return List of nearest neighbors sorted by distance
     */
    public List<NearestNeighbor> kNearestNeighbors(double[] point, int k) {
        PriorityQueue<NearestNeighbor> best = new PriorityQueue<>((a, b) ->
                Double.compare(b.distance, a.distance));

        kNearestRecursive(root, point, k, best);

        List<NearestNeighbor> result = new ArrayList<>(best);
        result.sort((a, b) -> Double.compare(a.distance, b.distance));
        return result;
    }

    /**
     * Recursive helper for k-nearest.
     */
    private void kNearestRecursive(Node node, double[] point, int k,
                                   PriorityQueue<NearestNeighbor> best) {
        if (node == null) {
            return;
        }

        double distance = distance(point, node.point);

        if (best.size() < k) {
            best.add(new NearestNeighbor(node.point, distance));
        } else if (distance < best.peek().distance) {
            best.poll();
            best.add(new NearestNeighbor(node.point, distance));
        }

        int axis = node.getAxis();
        double diff = point[axis] - node.point[axis];

        Node nearNode = diff < 0 ? node.left : node.right;
        Node farNode = diff < 0 ? node.right : node.left;

        kNearestRecursive(nearNode, point, k, best);

        if (best.size() < k || Math.abs(diff) < best.peek().distance) {
            kNearestRecursive(farNode, point, k, best);
        }
    }

    /**
     * Find all points in rectangular range.
     *
     * @param lower Lower bounds
     * @param upper Upper bounds
     * @return Points in range
     */
    public List<double[]> rangeSearch(double[] lower, double[] upper) {
        List<double[]> result = new ArrayList<>();
        rangeSearchRecursive(root, lower, upper, result);
        return result;
    }

    /**
     * Recursive helper for range search.
     */
    private void rangeSearchRecursive(Node node, double[] lower, double[] upper,
                                      List<double[]> result) {
        if (node == null) {
            return;
        }

        boolean inRange = true;
        for (int i = 0; i < k; i++) {
            if (node.point[i] < lower[i] || node.point[i] > upper[i]) {
                inRange = false;
                break;
            }
        }

        if (inRange) {
            result.add(node.point);
        }

        int axis = node.getAxis();

        if (lower[axis] <= node.point[axis]) {
            rangeSearchRecursive(node.left, lower, upper, result);
        }

        if (upper[axis] >= node.point[axis]) {
            rangeSearchRecursive(node.right, lower, upper, result);
        }
    }

    /**
     * Calculate Euclidean distance.
     */
    private double distance(double[] p1, double[] p2) {
        double sum = 0;
        for (int i = 0; i < p1.length; i++) {
            double diff = p1[i] - p2[i];
            sum += diff * diff;
        }
        return Math.sqrt(sum);
    }

    public static void main(String[] args) {
        // Example 1: 2D nearest neighbor
        System.out.println("=== Example 1: 2D Nearest Neighbor ===");
        List<double[]> points2d = Arrays.asList(
                new double[]{2, 3}, new double[]{5, 4}, new double[]{9, 6},
                new double[]{4, 7}, new double[]{8, 1}, new double[]{7, 2}
        );
        KDTree tree2d = new KDTree(points2d);

        double[] query = {9, 2};
        NearestNeighbor nearest = tree2d.nearestNeighbor(query);
        System.out.println("Points: " + points2d);
        System.out.println("Query: " + Arrays.toString(query));
        System.out.println("Nearest: " + nearest);

        // Example 2: k-nearest neighbors
        System.out.println("\n=== Example 2: k-Nearest Neighbors ===");
        List<NearestNeighbor> knn = tree2d.kNearestNeighbors(query, 3);
        System.out.println("3-Nearest neighbors to " + Arrays.toString(query) + ":");
        for (NearestNeighbor nn : knn) {
            System.out.println("  " + nn);
        }

        // Example 3: Range search
        System.out.println("\n=== Example 3: Range Search ===");
        double[] lower = {3, 2};
        double[] upper = {8, 6};
        List<double[]> inRange = tree2d.rangeSearch(lower, upper);
        System.out.println("Points in range [" + Arrays.toString(lower) + ", " +
                Arrays.toString(upper) + "]: " + inRange);

        // Example 4: 3D points
        System.out.println("\n=== Example 4: 3D Points ===");
        List<double[]> points3d = Arrays.asList(
                new double[]{2, 3, 1}, new double[]{5, 4, 2},
                new double[]{9, 6, 3}, new double[]{4, 7, 4}
        );
        KDTree tree3d = new KDTree(points3d);

        double[] query3d = {5, 5, 3};
        NearestNeighbor nearest3d = tree3d.nearestNeighbor(query3d);
        System.out.println("3D Points: " + points3d);
        System.out.println("Query: " + Arrays.toString(query3d));
        System.out.println("Nearest: " + nearest3d);
    }
}
