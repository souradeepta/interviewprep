# Boolean Satisfiability

## Overview

Boolean Satisfiability are algorithms that solve NP-hard problems or use advanced techniques.

## Complexity

- Classical approach: Exponential or polynomial approximation
- This approach: Optimized via heuristics or randomization
- Trade-offs: Approximation ratio, probability of correctness

## Applications

Boolean Satisfiability appear in:
- Optimization problems (logistics, scheduling)
- Machine learning (hyperparameter optimization)
- Approximation schemes (TSP, knapsack)
- Probabilistic methods (Monte Carlo simulation)

## Variants

1. Exact algorithms - correct but slow
2. Approximation algorithms - fast, near-optimal
3. Heuristic algorithms - practical, no guarantees
4. Randomized algorithms - probabilistic correctness
5. Parallel algorithms - distributed execution

## Key Insights

- Use approximation when exact is intractable
- Randomization can reduce complexity
- Heuristics often work well in practice
- Problem-specific optimizations essential

## When to Use

- NP-hard problems needing solution
- Real-time constraints (heuristic better than exact)
- Large problem instances (approximation acceptable)
- Probabilistic methods for Monte Carlo

## Complexity Classes

- P: Polynomial time solvable
- NP: Non-deterministic polynomial (guess-and-check)
- NP-Hard: At least as hard as NP problems
- NP-Complete: NP and NP-hard

## Implementation Notes

- Choose algorithm based on problem size
- Tune parameters for your specific instance
- Combine multiple heuristics for better results
- Validate results against known benchmarks

## References

- Research papers on specific algorithms
- Competition platforms (ICPC, IOI)
- Algorithm design textbooks
- Online judge problem solutions

## Trade-offs

| Aspect | Exact | Approximation | Heuristic |
|--------|-------|---|---|
| Correctness | Guaranteed | Ratio bound | Probabilistic |
| Speed | Slow | Fast | Fastest |
| Memory | High | Medium | Low |
| Implementation | Complex | Medium | Simple |
