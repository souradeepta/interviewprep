# Monotonic Stack Pattern

**Level:** L4-L5
**Time to read:** ~20 min
**Prerequisites:** [Arrays](../../06-data-structures/arrays/README.md)
**Related:** [Sliding Window](../sliding-window/README.md)

## Quick Summary

A stack that maintains strictly increasing or decreasing order by popping elements that violate the invariant before pushing a new one. Every element is pushed and popped at most once — O(n) amortized. Key signal: "next greater element", "previous smaller element", "largest rectangle", "daily temperatures", "span of stock price".

## When to Use It

Signal phrases that strongly indicate monotonic stack:

- "Next greater / next smaller element to the right"
- "Previous greater / previous smaller element to the left"
- "Days until warmer temperature"
- "Span of stock price"
- "Largest rectangle in histogram"
- "How much water can be trapped"
- "Remove k digits to make smallest number"

**Not a fit when:** you need the global max/min (use a variable), non-contiguous subsequences (use DP), or range queries over arbitrary windows (use segment tree / sparse table).

## How It Works

The key idea: when a new element `x` arrives, pop everything from the stack that `x` "beats" (greater than or less than, depending on the variant). Each popped element gets its answer resolved at that moment.

### Variant 1: Decreasing Stack (Next Greater Element)

Maintains a decreasing stack of indices. When a larger element arrives it resolves the waiting indices.

```
nums = [2, 1, 2, 4, 3]
         0  1  2  3  4

Process i=0 val=2:  stack=[]  → push 0.      stack=[0]
Process i=1 val=1:  1 < nums[0]=2, just push. stack=[0,1]
Process i=2 val=2:  2 > nums[1]=1 → pop 1, result[1]=2
                    2 == nums[0]=2, not strictly greater, just push.
                    stack=[0,2]
Process i=3 val=4:  4 > nums[2]=2 → pop 2, result[2]=4
                    4 > nums[0]=2 → pop 0, result[0]=4
                    stack=[3]
Process i=4 val=3:  3 < nums[3]=4, just push. stack=[3,4]

End of loop — remaining stack [3, 4] never got a greater element:
result[3] = result[4] = -1

result = [4, 2, 4, -1, -1]
```

Stack invariant: values at indices in the stack are always decreasing from bottom to top.

### Variant 2: Increasing Stack (Span / Histogram)

Maintains an increasing stack of indices. When a smaller element arrives it pops the taller bars and resolves their widths.

```
heights = [2, 1, 5, 6, 2, 3]
           0  1  2  3  4  5

Append sentinel 0 at the end → heights = [2,1,5,6,2,3,0]

Process i=0 h=2:  stack=[] → push 0.          stack=[0]
Process i=1 h=1:  1 < heights[0]=2 → pop 0
                    height=2, width=1 (stack empty), area=2
                  push 1.                       stack=[1]
Process i=2 h=5:  5>1, push.                   stack=[1,2]
Process i=3 h=6:  6>5, push.                   stack=[1,2,3]
Process i=4 h=2:  2 < heights[3]=6 → pop 3
                    height=6, width=4-2-1=1, area=6
                  2 < heights[2]=5 → pop 2
                    height=5, width=4-1-1=2, area=10  ← max so far
                  2 > heights[1]=1, push.       stack=[1,4]
Process i=5 h=3:  3>2, push.                   stack=[1,4,5]
Process i=6 h=0 (sentinel):
                  0 < heights[5]=3 → pop 5, height=3, width=6-4-1=1, area=3
                  0 < heights[4]=2 → pop 4, height=2, width=6-1-1=4, area=8
                  0 < heights[1]=1 → pop 1, height=1, width=6-(-1)-1=6, area=6
                  stack=[]

max_area = 10
```

Stack invariant: values at indices in the stack are always increasing from bottom to top.

## Two Core Patterns

### Pattern A: "Next Greater / Smaller to the Right"

```python
# Template: decreasing stack → next greater element
def next_greater(nums):
    result = [-1] * len(nums)
    stack = []                          # indices, values decreasing
    for i, val in enumerate(nums):
        while stack and nums[stack[-1]] < val:   # val beats top
            idx = stack.pop()
            result[idx] = val           # answer resolved here
        stack.append(i)
    return result                       # remaining stack → no answer → stays -1
```

Key: the comparison direction determines what "beats" means.
- `nums[stack[-1]] < val` → resolves "next GREATER" (decreasing stack)
- `nums[stack[-1]] > val` → resolves "next SMALLER" (increasing stack)

### Pattern B: "Span / Histogram / Contribution"

```python
# Template: increasing stack → largest rectangle
def largest_rectangle(heights):
    stack = []                          # indices, heights increasing
    max_area = 0
    for i, h in enumerate(heights + [0]):   # sentinel 0 flushes stack
        while stack and heights[stack[-1]] > h:
            height = heights[stack.pop()]
            width = i if not stack else i - stack[-1] - 1
            max_area = max(max_area, height * width)
        stack.append(i)
    return max_area
```

The sentinel `0` at the end forces all remaining bars to be popped and resolved.

## Decision Tree

```
Does the problem ask about "nearest" element or "range bounded by nearest"?
├── YES → What direction?
│         ├── Next greater/smaller to RIGHT → Decreasing/Increasing stack, scan L→R
│         ├── Previous greater/smaller to LEFT → same logic, answer fills on pop
│         └── Both (span) → stack gives left boundary; current index is right boundary
└── NO  → Does it involve rectangular/trapped areas bounded by bars?
          ├── YES → Increasing stack + sentinel
          └── NO  → Probably not monotonic stack
                    ├── Range min/max queries → Sparse table / segment tree
                    └── Non-contiguous → DP
```

## Complexity

| Operation | Time | Space | Notes |
|-----------|------|-------|-------|
| Single pass with stack | O(n) | O(n) | Amortized: each element pushed and popped at most once |
| Circular array (2x pass) | O(n) | O(n) | Two passes over n elements = 2n operations |
| Histogram with sentinel | O(n) | O(n) | Sentinel flushes stack without extra loop |

The "while" loop inside the "for" loop looks O(n²) but is actually O(n) amortized — each of the n elements is pushed once and popped at most once, for a total of at most 2n stack operations across the entire input.

## Common Mistakes

- **Wrong comparison direction:** `<` vs `>` determines whether you get "next greater" or "next smaller". Write out a small example to verify.
- **Not handling the remaining stack:** after the main loop, elements still in the stack have no answer to the right — their result stays at the default (usually -1 or 0). Never skip this.
- **Using `<=` instead of `<` (or vice versa):** strictly greater vs. greater-or-equal changes what happens with duplicates. LC #496 uses strictly greater; LC #84 pops on strictly greater height.
- **Forgetting the sentinel in histogram problems:** without a trailing `0`, bars that are never beaten stay in the stack and their areas are never calculated.
- **Off-by-one in width calculation:** `width = i - stack[-1] - 1` when the stack is non-empty (bars to the left block the full width), but `width = i` when the stack is empty (the bar extends all the way to index 0).
- **Circular array — not modding index:** in problems like LC #503 (circular array), use `i % n` when indexing `nums` during the second pass.

## Run the Code

```bash
# From repo root
pytest tests/patterns/test_monotonic_stack.py -v
```

**Implementation:** [`python/patterns/monotonic_stack.py`](../../../python/patterns/monotonic_stack.py)
**Tests:** [`tests/patterns/test_monotonic_stack.py`](../../../tests/patterns/test_monotonic_stack.py)

## Problems

6 problems with full think-process walk-throughs: [problems.md](problems.md)

| # | Problem | Difficulty | LeetCode | Variant |
|---|---------|-----------|---------|---------|
| 1 | Daily Temperatures | Medium | #739 | Decreasing stack — days until warmer |
| 2 | Next Greater Element I | Easy | #496 | Decreasing stack + hash map |
| 3 | Next Greater Element II | Medium | #503 | Circular array — two passes |
| 4 | Largest Rectangle in Histogram | Hard | #84 | Increasing stack + sentinel |
| 5 | Sum of Subarray Minimums | Medium | #907 | Contribution technique |
| 6 | Trapping Rain Water | Hard | #42 | Stack-based layer-by-layer water fill |
