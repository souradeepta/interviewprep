"""
Advanced Algorithms for SDE Interview Preparation
==================================================

This package contains advanced algorithm implementations:
- Dynamic Programming advanced techniques
- Graph algorithms (max flow, matching, 2-SAT)
- String algorithms (Boyer-Moore, Aho-Corasick, etc.)
- Computational Geometry
- Tree algorithms (Heavy-Light Decomposition, Square Root Decomposition)
"""

from .advanced_algorithms import (
    # DP Advanced
    ConvexHullTrick,
    DigitDP,
    TreeDP,
    KnuthYaoOptimization,
    SOS_DP,

    # Graph Algorithms
    MaxFlowFordFulkerson,
    MaxFlowDinic,
    MinCostMaxFlow,
    BipartiteMatchingAugmenting,
    BipartiteMatchingHopcroftKarp,
    TwoSAT,
    ArticulationPointsBridges,
    VertexConnectivity,
    TransitiveClosure,

    # String Algorithms
    BoyerMoore,
    AhoCorasick,
    SuffixArray,
    Manacher,
    ZAlgorithm,

    # Computational Geometry
    ConvexHullGrahamScan,
    ConvexHullAndrewChain,
    ClosestPair,
    LineIntersection,
    PointInPolygon,

    # Tree Algorithms
    HeavyLightDecomposition,
    SquareRootDecomposition,
    MosAlgorithm,

    # Miscellaneous
    BoyerMooreVoting,
    QuickSelect,
    HuffmanCoding,
    ActivitySelection,
)

__all__ = [
    'ConvexHullTrick', 'DigitDP', 'TreeDP', 'KnuthYaoOptimization', 'SOS_DP',
    'MaxFlowFordFulkerson', 'MaxFlowDinic', 'MinCostMaxFlow',
    'BipartiteMatchingAugmenting', 'BipartiteMatchingHopcroftKarp',
    'TwoSAT', 'ArticulationPointsBridges', 'VertexConnectivity',
    'TransitiveClosure',
    'BoyerMoore', 'AhoCorasick', 'SuffixArray', 'Manacher', 'ZAlgorithm',
    'ConvexHullGrahamScan', 'ConvexHullAndrewChain', 'ClosestPair',
    'LineIntersection', 'PointInPolygon',
    'HeavyLightDecomposition', 'SquareRootDecomposition', 'MosAlgorithm',
    'BoyerMooreVoting', 'QuickSelect', 'HuffmanCoding', 'ActivitySelection',
]
