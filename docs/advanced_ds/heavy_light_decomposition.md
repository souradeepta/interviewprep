# Heavy-Light Decomposition

## Overview

**Heavy-Light Decomposition (HLD)** is a tree decomposition technique that partitions a tree into heavy and light paths, enabling efficient queries and updates on tree paths. By decomposing an arbitrary tree into O(log n) disjoint paths and maintaining a segment tree or other structure for each path, HLD converts tree path queries to O(log² n) range queries.

Introduced by Sleator and Tarjan (1983) in their work on link-cut trees, HLD is fundamental for competitive programming and advanced tree algorithms. It's used in game engines (scene graph hierarchies), network routing (path analysis), and database query optimization.

Unlike LCA (Lowest Common Ancestor) preprocessing which answers point queries, HLD handles path updates and range queries on trees efficiently — for example, adding a value to all edges on a path from u to v, then querying the maximum value on that path.

## When to Use

- **Path queries on trees**: Sum/max/min of values on a path from u to v
- **Path updates on trees**: Add a value to all nodes/edges on a path u→v, then query
- **Subtree queries with changes**: Update a subtree and answer range queries
- **Tree edge weights change**: Dynamic trees with weighted queries
- **Not suitable if queries are mostly**: Point lookups (use LCA), subtree aggregation only (use DFS ordering + segment tree)

## ASCII Visualization

```
Example tree (edges labeled with weights):

           1(5)
          / \
        2(3) 3(1)
        / \     \
      4(2) 5(4)  6(2)
      /     |
     7(1)   8(3)

Heavy-Light Decomposition by child subtree sizes:

                1
              /   \
        [2-4-7]    [3]
           |
        [5-8]    6

Paths (heavy edges in black, light edges in red):
- Path 1: [1, 2, 4, 7] (following heavy edges: 1→2 heavy, 2→4 heavy, 4→7 heavy)
- Path 2: [2, 5, 8] (starting from left-out node 5, following heavy)
- Path 3: [1, 3, 6] (starting from right child of 1)

Each path maintains its own segment tree or array structure.

To query path 7→1:
- 7 is in path [7,4,2,1]
- Follow heavy chain upward to node 1
- If query crosses chains, use LCA to split
```

### Path Structure

```
Tree nodes organized by chain:
Chain 0: [1, 2, 4, 7]  - segment tree for edge weights
Chain 1: [5, 8]        - segment tree for edge weights  
Chain 2: [3, 6]        - segment tree for edge weights

Query path(u, v):
1. Find LCA(u, v)
2. While u != LCA: query current chain segment tree, jump up to parent chain
3. While v != LCA: query current chain segment tree, jump up to parent chain
4. Combine all query results
```

## Operations & Complexity

| Operation          | Time Complexity | Space Complexity | Notes |
|-------------------|:---------------:|:----------------:|-------|
| Preprocessing      | O(n)            | O(n)             | DFS to compute subtree sizes, assign positions |
| Path query         | O(log² n)       | O(1)             | At most O(log n) chains, O(log n) per segment tree query |
| Path update        | O(log² n)       | O(1)             | Same as path query, propagate updates up chains |
| Point query/update | O(log² n)       | O(1)             | Special case of path query |
| Space             | —               | O(n)             | One segment tree per chain, total O(n) nodes |

> HLD reduces tree to O(log n) chains. With segment trees: O(log² n) per operation. With link-cut trees: can achieve O(log n).

## Key Invariants

1. **Heavy-light property**: For each non-leaf node, the child with the largest subtree is the "heavy" child. Other children are "light".
2. **Chain partition**: Each path from a light edge to a leaf is a separate chain. Total O(log n) chains on any root-to-leaf path.
3. **Chain ordering**: All nodes in a chain are ordered by DFS preorder along that chain.
4. **Depth of chain tree**: O(log n); going up chains from any node to root passes through O(log n) chains.
5. **Subtree size invariant**: subtree_size[u] > subtree_size[v] if u is parent and on the same heavy path.

## Solution Approach Flowchart

```mermaid
flowchart TD
    A["🎯 Problem: Tree path query/update"] -->|Query type?| B{What's on tree?}
    B -->|Node values only<br/>subtree queries| C["❌ No HLD needed<br/>DFS preorder + segment tree"]
    B -->|Edge weights<br/>path operations| D["✓ Heavy-Light Decomposition"]
    D --> E["🏗 Preprocessing:<br/>1. DFS subtree sizes"]
    E --> F["🔗 2. Assign chain IDs<br/>& positions in chain"]
    F --> G["📋 3. Build segment tree<br/>for each chain"]
    G --> H["📊 Identify query type"]
    H -->|Single path query| I["🎯 Find LCA<br/>split path by chains"]
    H -->|Path range update| J["🔄 Update all chains<br/>from u→LCA and v→LCA"]
    H -->|Point update| K["Update single node<br/>on appropriate chain"]
    I --> L["For each chain:<br/>query segment tree<br/>O(log n) per chain"]
    J --> M["For each chain:<br/>range update segment tree<br/>with lazy propagation"]
    K --> N["Update segment tree entry<br/>for single position"]
    L --> O["Merge results<br/>from all chains<br/>O(log n) chains total"]
    M --> O
    N --> O
    O --> P["✓ Time: O(log² n)<br/>Per operation"]
    
    style A fill:#deb887,color:#000,stroke:#333,stroke-width:2px
    style D fill:#add8e6,color:#000,stroke:#333,stroke-width:2px
    style E fill:#dda0dd,color:#000,stroke:#333,stroke-width:2px
    style F fill:#dda0dd,color:#000,stroke:#333,stroke-width:2px
    style G fill:#dda0dd,color:#000,stroke:#333,stroke-width:2px
    style P fill:#90ee90,color:#000,stroke:#333,stroke-width:2px
```

## Tree Decomposition Decision Flowchart

```mermaid
flowchart TD
    A["📊 Analyzing tree problem"] --> B{Problem structure?}
    B -->|Subtree aggregation only| C["✓ DFS preorder<br/>+ segment tree<br/>O(log n)"]
    B -->|Path queries/updates| D{Edge weights?}
    D -->|No weights<br/>node values| E["✓ LCA with<br/>binary lifting<br/>O(log n)"]
    D -->|Weighted edges<br/>complex queries| F{Path type?}
    F -->|Simple path sums| G["✓ Heavy-Light HLD<br/>O(log² n)"]
    F -->|Arbitrary trees<br/>reroot needed| H["✓ Link-Cut Trees<br/>O(log n)"]
    B -->|All operations<br/>dynamic| I["✓ Link-Cut Trees<br/>or Centroid"]
    B -->|Heavy/light<br/>analysis| J["✓ Heavy-Light HLD<br/>for decomposition<br/>structure analysis"]
    C --> K["Choice depends on operation type"]
    E --> K
    G --> K
    H --> K
    I --> K
    J --> K
    
    style A fill:#deb887,color:#000,stroke:#333,stroke-width:2px
    style C fill:#90ee90,color:#000,stroke:#333,stroke-width:2px
    style E fill:#90ee90,color:#000,stroke:#333,stroke-width:2px
    style G fill:#90ee90,color:#000,stroke:#333,stroke-width:2px
    style H fill:#90ee90,color:#000,stroke:#333,stroke-width:2px
    style I fill:#90ee90,color:#000,stroke:#333,stroke-width:2px
```

## HLD Preprocessing & Chain Building Flowchart

```mermaid
flowchart TD
    A["🏗 Heavy-Light Decomposition Preprocessing"] --> B["Input: Tree with n nodes"]
    B --> C["Step 1: DFS calculate subtree sizes"]
    C --> D["For each node u:<br/>subtree_size[u] =<br/>1 + sum children sizes"]
    D --> E["Time: O(n)"]
    E --> F["Step 2: Identify heavy children"]
    F --> G["For each non-leaf node u:<br/>heavy_child[u] =<br/>child with max subtree_size"]
    G --> H["Time: O(n)"]
    H --> I["Step 3: DFS and assign chains"]
    I --> J["DFS from root:<br/>when on heavy edge,<br/>continue same chain<br/>when on light edge,<br/>start new chain"]
    J --> K["Assign chain_id[node]<br/>and position_in_chain[node]"]
    K --> L["Time: O(n)"]
    L --> M["Step 4: Build segment tree<br/>for each chain"]
    M --> N["For each chain of length L:<br/>create segment tree<br/>indexed by position"]
    N --> O["Total space: O(n)<br/>sum of all chains"]
    O --> P["All preprocessing done<br/>Ready for queries"]
    
    style A fill:#dda0dd,color:#000,stroke:#333,stroke-width:2px
    style C fill:#dda0dd,color:#000,stroke:#333,stroke-width:2px
    style F fill:#dda0dd,color:#000,stroke:#333,stroke-width:2px
    style I fill:#dda0dd,color:#000,stroke:#333,stroke-width:2px
    style M fill:#dda0dd,color:#000,stroke:#333,stroke-width:2px
    style P fill:#90ee90,color:#000,stroke:#333,stroke-width:2px
```

## HLD Path Query vs Alternatives Flowchart

```mermaid
flowchart TD
    A["🤔 Tree path operation analysis"] --> B{Operation frequency?}
    B -->|Few queries<br/>naive ok| C["✓ Simple DFS/BFS<br/>O(n) per query<br/>total O(queries·n)"]
    B -->|Many queries<br/>need fast| D{Query types?}
    D -->|Point lookups<br/>or single vertex| E["✓ LCA + preprocessing<br/>O(log n)"]
    D -->|Path aggregation| F{Can fit in memory?}
    F -->|Memory abundant| G["✓ HLD<br/>O(log² n) per query<br/>O(n) space"]
    F -->|Memory tight| H["✓ Link-Cut Trees<br/>O(log n) per query<br/>complex code"]
    B -->|Dynamic changes<br/>reroot needed| I["✓ Link-Cut Trees<br/>O(log n) per operation<br/>handles rerooting"]
    B -->|Offline queries| J["✓ Batch processing<br/>offline dynamic<br/>tree queries"]
    C --> K["Decision"]
    E --> K
    G --> K
    H --> K
    I --> K
    J --> K
    K --> L["HLD is sweet spot:<br/>easier than Link-Cut Trees<br/>faster than naive<br/>good for CP"]
    
    style A fill:#deb887,color:#000,stroke:#333,stroke-width:2px
    style G fill:#90ee90,color:#000,stroke:#333,stroke-width:2px
    style L fill:#dda0dd,color:#000,stroke:#333,stroke-width:2px
```

## Common Patterns

1. **Path Sum Query**: Build HLD with segment tree storing edge weights. To query sum on path u→v: (1) find LCA(u,v), (2) walk chains from u to LCA querying segment trees, (3) walk chains from v to LCA, (4) sum all results. Time: O(log² n).

2. **Path Range Update**: Same structure. To add a value to all edges on path u→v: (1) walk chains updating segment trees with lazy propagation, (2) propagate updates to children. Lazy propagation reduces it to O(log² n) without full tree traversal.

3. **Subtree Heaviness Analysis**: Use HLD to identify heavy subtrees. Process nodes in chain order to analyze locality; cache-friendly for applications like scene graphs.

4. **Link-Cut Tree Variant**: Use HLD as foundation for link-cut trees, enabling dynamic tree operations (reroot, change weights) in O(log n) amortized per operation.

## Interview Questions

1. **Why is heavy-light decomposition O(log n) chains deep?** Because each heavy edge goes to the child with >50% of subtree size. Going up the tree, each light edge reduces subtree size by ≥50%. Total: at most log₂(n) light edges before reaching root.

2. **How do you compute LCA efficiently in HLD?** Preprocess with binary lifting or another O(log n) LCA method (e.g., Tarjan's offline algorithm). HLD itself doesn't compute LCA; you use HLD for path queries given LCA as input.

3. **Can you handle edge updates with HLD?** Yes. Store edge weights in segment trees indexed by chain position. Updating edge (u, v) updates the segment tree entry for the deeper node.

4. **What's the difference between HLD and centroid decomposition?** HLD is for path operations; centroid decomposition is for subtree operations. HLD gives O(log n) chains; centroid decomposition gives O(log n) depth. Choose based on problem structure.

5. **How would you modify HLD for weighted edges?** Store weights in segment trees instead of node values. Edge (u, v) with weight w: store w at the deeper endpoint's position in the segment tree.

6. **Is HLD better than Link-Cut Trees?** HLD: simpler, O(log² n). Link-Cut Trees: more complex, O(log n). Both have their place. Link-Cut Trees are more flexible for arbitrary tree operations.

7. **How many chains can a path from node u to root pass through?** At most O(log n). Proof: Each time you jump to a different chain via a light edge, subtree size roughly halves.

## Implementation Notes

- **Subtree Size Calculation**: DFS to compute subtree_size[u] = 1 + sum(subtree_size[children]). Easy to forget that only direct children count.
- **Heavy Child Selection**: For each node, the child with maximum subtree_size is heavy. Ties can go either way; consistent selection matters for correctness.
- **Chain Assignment**: Use DFS to assign nodes to chains in order. Keep track of chain ID and position within chain for segment tree indexing.
- **LCA Preprocessing**: HLD assumes LCA is preprocessed separately (binary lifting, sparse table, etc.). Getting LCA wrong breaks path queries.
- **Segment Tree per Chain**: Each chain needs its own segment tree indexed 0..chain_length. Query intervals must map correctly to chain positions.
- **Testing**: Verify chain assignment is contiguous along edges. Verify O(log n) chains on any path. Test simple cases: line graph (1 chain), star graph (n-1 chains).

## References

1. Sleator, D. D., & Tarjan, R. E. (1983). "A data structure for dynamic trees." *Journal of Computer and System Sciences*, 26(3), 362-391.
2. Gusfield, D. (1997). *Algorithms on Strings, Trees, and Sequences*. Cambridge University Press.
3. Competitive Programming community documentation on HLD (Codeforces, TopCoder).
