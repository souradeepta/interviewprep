# Greedy Algorithms: Making Optimal Local Choices

**Level:** L3-L4
**Time to read:** ~10 min

Master greedy patterns for problems where local optimization leads to global optimality.

---

## Greedy Problem Solving

**Key Idea:** Make locally optimal choice at each step, hoping for global optimum.

**When it works:**
- Problem has optimal substructure
- Greedy choice property holds (local choice = global choice)

**When it fails:**
- Local optimal ≠ global optimal

---

## Greedy Choice Property

### Example: Activity Selection

```
Activities with start/end times:
A: 0-2
B: 1-3
C: 2-4
D: 3-5
E: 4-6

Greedy: Select activity that ends earliest
A (ends 2) → C (ends 4) → E (ends 6)
Result: 3 activities (optimal)
```

### Counter-example: Coin Change (Greedy Fails)

```
Coins: [25, 10, 1]
Target: 30

Greedy: Take 25, then need 5 cents
  Solution: 25 + 1 + 1 + 1 + 1 + 1 = 6 coins

Optimal: Take 10 + 10 + 10 = 3 coins

Greedy fails because 25 is too large
Use DP instead for coin change
```

---

## Classic Greedy Problems

### 1. Activity Selection (Interval Scheduling)

```python
def select_activities(activities):
    # Sort by end time
    activities.sort(key=lambda x: x[1])
    
    selected = [activities[0]]
    for i in range(1, len(activities)):
        # Select if doesn't overlap with last selected
        if activities[i][0] >= selected[-1][1]:
            selected.append(activities[i])
    
    return selected

# Time: O(n log n), Space: O(n)
```

### 2. Fractional Knapsack

```python
def fractional_knapsack(items, capacity):
    # Sort by value/weight ratio (descending)
    items.sort(key=lambda x: x[0]/x[1], reverse=True)
    
    total_value = 0
    for value, weight in items:
        if weight <= capacity:
            total_value += value
            capacity -= weight
        else:
            # Take fraction of last item
            total_value += (capacity / weight) * value
            break
    
    return total_value

# Time: O(n log n), Space: O(1)
```

### 3. Huffman Coding

```python
def huffman_coding(frequencies):
    import heapq
    
    # Create min heap of (frequency, unique_id, node)
    heap = []
    for i, freq in enumerate(frequencies):
        heapq.heappush(heap, (freq, i, chr(i)))  # Leaf node
    
    node_id = len(frequencies)
    while len(heap) > 1:
        freq1, _, node1 = heapq.heappop(heap)
        freq2, _, node2 = heapq.heappop(heap)
        
        merged_freq = freq1 + freq2
        heapq.heappush(heap, (merged_freq, node_id, (node1, node2)))
        node_id += 1
    
    return heap[0][2]  # Return tree root

# Time: O(n log n), Space: O(n)
# Optimal prefix code for given frequencies
```

### 4. Jump Game

```python
def can_jump(nums):
    max_reach = 0
    for i, jump_length in enumerate(nums):
        if i > max_reach:
            return False
        max_reach = max(max_reach, i + jump_length)
    return True

# Time: O(n), Space: O(1)
# Greedy: Always track farthest reachable position
```

### 5. Container with Most Water

```python
def max_area(heights):
    left, right = 0, len(heights) - 1
    max_area = 0
    
    while left < right:
        # Calculate area
        width = right - left
        height = min(heights[left], heights[right])
        area = width * height
        max_area = max(max_area, area)
        
        # Move pointer pointing to shorter height
        if heights[left] < heights[right]:
            left += 1
        else:
            right -= 1
    
    return max_area

# Time: O(n), Space: O(1)
# Greedy: Maximize area by moving inward, shrink taller wall first
```

---

## Proving Greedy Works

### Exchange Argument

If greedy choice differs from optimal:
1. Show that swapping greedy choice into optimal doesn't decrease value
2. Repeat until greedy solution = optimal solution
3. Therefore greedy is optimal

---

## Greedy vs DP

| Algorithm | When | Example |
|-----------|------|---------|
| **Greedy** | Local choice = global optimal | Activity selection, Huffman |
| **DP** | Local choice ≠ guaranteed global | Coin change (bounded), LCS |

---

## Greedy Checklist

- ✓ Identified greedy choice (what to pick at each step)
- ✓ Verified greedy choice property (local = global)
- ✓ Proved correctness (exchange or induction)
- ✓ Time complexity better than DP
- ✓ Tested on small examples
- ✓ Tested on edge cases

