"""
KD-Tree (K-Dimensional Tree)

Time Complexity:
- Construction: O(n log n)
- Nearest neighbor search: O(log n) average, O(n) worst case
- Range query: O(sqrt(n) + k) where k = number of results
- Point insertion: O(log n) average
- Point deletion: O(log n) average

Space Complexity: O(n)

Use Cases:
- Nearest neighbor search (k-NN)
- Range searching (all points in rectangle)
- Spatial indexing (databases)
- Clustering algorithms
- Graphics and gaming (collision detection)

Key Insight:
- Recursively partition space using alternating dimensions
- At depth d, split on dimension d mod k
- Pruning: skip subtrees when bounding box is far from query point
- Balance depends on insertion order
"""

from typing import List, Tuple, Optional
import math


class KDNode:
    """Node in KD-Tree."""

    def __init__(self, point: List[float], depth: int, k: int):
        self.point = point
        self.depth = depth
        self.k = k
        self.left = None
        self.right = None

    def get_axis(self) -> int:
        """Get the axis (dimension) for splitting at this depth."""
        return self.depth % self.k


class KDTree:
    """K-Dimensional Tree for spatial searching."""

    def __init__(self, points: List[List[float]], k: Optional[int] = None):
        """
        Initialize KD-Tree.

        Args:
            points: List of points (each point is a list of coordinates)
            k: Number of dimensions (auto-detected if None)
        """
        self.points = points
        self.k = k or (len(points[0]) if points else 0)
        self.root = self._build_tree(points, 0) if points else None

    def _build_tree(self, points: List[List[float]], depth: int) -> Optional[KDNode]:
        """Build KD-Tree recursively."""
        if not points:
            return None

        axis = depth % self.k
        sorted_points = sorted(points, key=lambda p: p[axis])
        median_idx = len(sorted_points) // 2

        return KDNode(
            sorted_points[median_idx],
            depth,
            self.k
        ).configure_children(
            self._build_tree(sorted_points[:median_idx], depth + 1),
            self._build_tree(sorted_points[median_idx + 1:], depth + 1)
        )

    def nearest_neighbor(self, point: List[float]) -> Tuple[List[float], float]:
        """
        Find nearest point in tree.

        Args:
            point: Query point

        Returns:
            (nearest_point, distance)
        """
        if not self.root:
            return None, float('inf')

        best = [None, float('inf')]
        self._nearest_neighbor_recursive(self.root, point, best)
        return best[0], best[1]

    def _nearest_neighbor_recursive(self, node: Optional[KDNode], point: List[float],
                                    best: List) -> None:
        """Recursive helper for nearest neighbor search."""
        if node is None:
            return

        distance = self._distance(point, node.point)
        if distance < best[1]:
            best[0] = node.point
            best[1] = distance

        axis = node.get_axis()
        diff = point[axis] - node.point[axis]

        # Choose which side to search first
        near_node = node.left if diff < 0 else node.right
        far_node = node.right if diff < 0 else node.left

        self._nearest_neighbor_recursive(near_node, point, best)

        # Check if we need to search far side
        if abs(diff) < best[1]:
            self._nearest_neighbor_recursive(far_node, point, best)

    def k_nearest_neighbors(self, point: List[float], k: int) -> List[Tuple[List[float], float]]:
        """
        Find k nearest points.

        Args:
            point: Query point
            k: Number of neighbors

        Returns:
            List of (point, distance) tuples sorted by distance
        """
        best = []
        self._k_nearest_recursive(self.root, point, k, best)
        return sorted(best, key=lambda x: x[1])

    def _k_nearest_recursive(self, node: Optional[KDNode], point: List[float],
                             k: int, best: List) -> None:
        """Recursive helper for k-nearest search."""
        if node is None:
            return

        distance = self._distance(point, node.point)

        # Add to best if room or better than worst
        if len(best) < k:
            best.append((node.point, distance))
            best.sort(key=lambda x: x[1], reverse=True)
        elif distance < best[0][1]:
            best[0] = (node.point, distance)
            best.sort(key=lambda x: x[1], reverse=True)

        axis = node.get_axis()
        diff = point[axis] - node.point[axis]

        near_node = node.left if diff < 0 else node.right
        far_node = node.right if diff < 0 else node.left

        self._k_nearest_recursive(near_node, point, k, best)

        # Prune if possible
        if len(best) < k or abs(diff) < best[0][1]:
            self._k_nearest_recursive(far_node, point, k, best)

    def range_search(self, lower: List[float], upper: List[float]) -> List[List[float]]:
        """
        Find all points in rectangular range.

        Args:
            lower: Lower bounds for each dimension
            upper: Upper bounds for each dimension

        Returns:
            List of points in range
        """
        result = []
        self._range_search_recursive(self.root, lower, upper, result)
        return result

    def _range_search_recursive(self, node: Optional[KDNode], lower: List[float],
                                upper: List[float], result: List) -> None:
        """Recursive helper for range search."""
        if node is None:
            return

        # Check if point is in range
        in_range = all(lower[i] <= node.point[i] <= upper[i] for i in range(self.k))
        if in_range:
            result.append(node.point)

        axis = node.get_axis()

        # Check which subtrees to search
        if lower[axis] <= node.point[axis]:
            self._range_search_recursive(node.left, lower, upper, result)

        if upper[axis] >= node.point[axis]:
            self._range_search_recursive(node.right, lower, upper, result)

    def _distance(self, p1: List[float], p2: List[float]) -> float:
        """Euclidean distance between two points."""
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(p1, p2)))


class KDNode:
    """Node in KD-Tree."""

    def __init__(self, point: List[float], depth: int, k: int):
        self.point = point
        self.depth = depth
        self.k = k
        self.left = None
        self.right = None

    def get_axis(self) -> int:
        """Get the axis (dimension) for splitting at this depth."""
        return self.depth % self.k

    def configure_children(self, left, right):
        """Helper to set children and return self."""
        self.left = left
        self.right = right
        return self


if __name__ == "__main__":
    # Example 1: 2D nearest neighbor
    print("=== Example 1: 2D Nearest Neighbor ===")
    points_2d = [[2, 3], [5, 4], [9, 6], [4, 7], [8, 1], [7, 2]]
    tree_2d = KDTree(points_2d)

    query = [9, 2]
    nearest, distance = tree_2d.nearest_neighbor(query)
    print(f"Points: {points_2d}")
    print(f"Query: {query}")
    print(f"Nearest: {nearest}, Distance: {distance:.2f}")

    # Example 2: k-nearest neighbors
    print("\n=== Example 2: k-Nearest Neighbors ===")
    knn = tree_2d.k_nearest_neighbors(query, 3)
    print(f"3-Nearest neighbors to {query}:")
    for point, dist in knn:
        print(f"  {point}, Distance: {dist:.2f}")

    # Example 3: Range search
    print("\n=== Example 3: Range Search ===")
    lower = [3, 2]
    upper = [8, 6]
    in_range = tree_2d.range_search(lower, upper)
    print(f"Points in range [{lower}, {upper}]: {in_range}")

    # Example 4: 3D points
    print("\n=== Example 4: 3D Points ===")
    points_3d = [[2, 3, 1], [5, 4, 2], [9, 6, 3], [4, 7, 4]]
    tree_3d = KDTree(points_3d)

    query_3d = [5, 5, 3]
    nearest_3d, distance_3d = tree_3d.nearest_neighbor(query_3d)
    print(f"3D Points: {points_3d}")
    print(f"Query: {query_3d}")
    print(f"Nearest: {nearest_3d}, Distance: {distance_3d:.2f}")
