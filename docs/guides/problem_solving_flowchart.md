# General Problem-Solving Flowchart

## How to Use This Guide

This guide presents a systematic framework for solving interview problems from start to finish. Follow the flowchart step-by-step to ensure you don't miss critical details and arrive at an optimal solution.

**Duration:** Apply this 15-25 minute framework depending on problem complexity. In 45-minute interviews, you should spend:
- 5-7 minutes: Understanding and planning
- 15-20 minutes: Implementing
- 5-8 minutes: Testing and optimization
- 2-3 minutes: Complexity analysis

---

## The Interview Problem-Solving Framework (Enhanced)

```mermaid
graph TD
    A["🎯 START: Interview Problem Received"] --> B["Step 1: Clarify & Understand"]
    
    B --> C["Ask clarifying questions:<br/>- Input/output format?<br/>- Range of input?<br/>- Duplicates allowed?<br/>- Empty input?<br/>- Modify input OK?<br/>- Special constraints?<br/>- Examples provided?"]
    
    C --> D["Restate problem:<br/>- Repeat back<br/>- Show examples<br/>- List assumptions<br/>- Confirm with interviewer"]
    
    D --> E["Document:<br/>- Write problem statement<br/>- Note edge cases<br/>- Mark constraints"]
    
    E --> F["Step 2: Identify Constraints"]
    
    F --> G["Analyze input size:<br/>- Is n ≤ 10? 100? 1K? 10K?<br/>- What about m, k, etc?<br/>- Time limit implications<br/>- 10⁶-10⁸ operations/sec?"]
    
    F --> H["Identify constraints:<br/>- Time limit? Memory limit?<br/>- Sorted input?<br/>- All positive numbers?<br/>- Modulo required?<br/>- In-place required?"]
    
    E --> I["Identify patterns:<br/>- Subarray/substring?<br/>- Interval problem?<br/>- Tree/graph problem?<br/>- DP problem?<br/>- Greedy possible?"]
    
    I --> J["Step 3: Plan Approach"]
    
    J --> K["Identify operations needed:<br/>- Lookup frequency?<br/>- Insertion/deletion?<br/>- Range queries?<br/>- Ordering needed?<br/>- Caching needed?"]
    
    K --> L["Select data structure:<br/>- Use DS Selection Guide<br/>- Justify choice<br/>- Consider alternatives"]
    
    L --> M["Select algorithm:<br/>- Use Algorithm Guide<br/>- Verify complexity OK<br/>- Check against constraints"]
    
    M --> N["Walk through approach:<br/>- Trace 2-3 examples<br/>- Verify correctness<br/>- Identify edge cases"]
    
    N --> O{"Does approach<br/>work?"}
    
    O -->|No| P["Revise:<br/>- Change DS?<br/>- Change algorithm?<br/>- Try different approach"]
    
    P --> N
    
    O -->|Yes| Q["Get interviewer OK:<br/>- Explain approach<br/>- Ask for approval<br/>- Ask to proceed"]
    
    Q --> R["Step 4: Code the Solution"]
    
    R --> S["Edge case handling:<br/>- Add null/empty checks<br/>- Handle boundaries<br/>- Test edge cases first"]
    
    S --> T["Implement main logic:<br/>- Code step-by-step<br/>- Clear variable names<br/>- Add comments for complex"]
    
    T --> U["Code quality:<br/>- DRY principle<br/>- Early returns<br/>- Clear structure"]
    
    U --> V["Code review:<br/>- Check syntax<br/>- Verify logic<br/>- Spot obvious bugs"]
    
    V --> W["Step 5: Test Thoroughly"]
    
    W --> X["Test cases:<br/>- Simple example<br/>- Medium complexity<br/>- Large input<br/>- Edge cases"]
    
    X --> Y["Identified edge cases:<br/>- Empty input<br/>- Single element<br/>- All same values<br/>- Negative/zero<br/>- Boundary values"]
    
    Y --> Z["Trace execution:<br/>- Manual walkthrough<br/>- Print debugging<br/>- Verify state changes"]
    
    Z --> AA{"All tests<br/>pass?"}
    
    AA -->|No| AB["Debug:<br/>- Identify root cause<br/>- Fix logic issue<br/>- Re-test"]
    
    AB --> Z
    
    AA -->|Yes| AC["Verify correctness<br/>one more time"]
    
    AC --> AD["Step 6: Analyze Complexity"]
    
    AD --> AE["Time complexity:<br/>- Count all operations<br/>- Identify loop nesting<br/>- Account for DS ops<br/>- Check against limits"]
    
    AD --> AF["Space complexity:<br/>- Variables/DS size<br/>- Recursion depth<br/>- Hidden allocations<br/>- Stack vs heap"]
    
    AF --> AG["Verify against constraints:<br/>- Time OK?<br/>- Space OK?<br/>- Match requirements?"]
    
    AG --> AH{"Can we<br/>optimize?"}
    
    AH -->|Easy win| AI["Optimize:<br/>- Better DS?<br/>- Better algorithm?<br/>- Reduce overhead?<br/>- Re-code and test"]
    
    AI --> AD
    
    AH -->|No or risky| AJ["Present solution"]
    
    AJ --> AK["Step 7: Discuss & Refine"]
    
    AK --> AL["Discuss complexity:<br/>- Time analysis<br/>- Space analysis<br/>- Trade-offs made<br/>- Why this approach"]
    
    AL --> AM["Discuss alternatives:<br/>- Other DS choices?<br/>- Other algorithms?<br/>- Space-time tradeoffs?<br/>- Why not X?"]
    
    AM --> AN["Answer follow-ups:<br/>- Change for new constraint?<br/>- Handle duplicates better?<br/>- Optimize space?<br/>- Optimize time?<br/>- Parallel version?"]
    
    AN --> AO["Step 8: Final Review"]
    
    AO --> AP["Code correctness:<br/>- No bugs visible<br/>- Edge cases handled<br/>- Logic sound"]
    
    AO --> AQ["Communication:<br/>- Explained clearly<br/>- Answered questions<br/>- Good discussion"]
    
    AQ --> AR["✅ DONE:<br/>Clean solution<br/>Good explanation<br/>Problem solved"]
    
    style A fill:#ffb3ba,color:#000,stroke:#333,stroke-width:2px
    style AR fill:#90ee90,color:#000,stroke:#333,stroke-width:2px
    
    classDef step fill:#ffe6e6
    class B,F,J,R,W,AD,AK,AO step
```

---

## Edge Case Identification Flowchart

```mermaid
graph TD
    A["Identify Edge Cases"] --> B["Input constraints"]
    
    B --> C["Empty input?"]
    C -->|Yes| D["Handle empty array"]
    C -->|Depends| E["Ask interviewer"]
    
    B --> F["Single element?"]
    F -->|Yes| G["Does code handle?"]
    G -->|No| H["Add special case"]
    
    B --> I["All same values?"]
    I -->|Yes| J["Test duplicates"]
    
    B --> K["Negative numbers?"]
    K -->|Yes| L["Test negatives"]
    
    B --> M["Zero?"]
    M -->|Yes| N["Division by zero?"]
    N -->|Yes| O["Add zero check"]
    
    B --> P["Boundary values?"]
    P -->|Yes| Q["Test min/max"]
    
    B --> R["Order matters?"]
    R -->|Yes| S["Test different orders"]
    
    B --> T["Duplicates allowed?"]
    T -->|Yes| U["Test with duplicates"]
    
    D --> V["✓ Edge case<br/>handled"]
    E --> V
    H --> V
    J --> V
    L --> V
    O --> V
    Q --> V
    S --> V
    U --> V
    
    style V fill:#90ee90,color:#000,stroke:#333,stroke-width:2px
```

---

## Optimization Opportunity Detection Tree

```mermaid
graph TD
    A["Can we optimize?"] --> B["Check time complexity"]
    
    B --> C["Is it O(n²)?"]
    C -->|Yes, n large| D["Try O(n log n)"]
    C -->|Borderline| E["Consider optimizing"]
    C -->|Small n| F["Current is fine"]
    
    B --> G["Is it O(2ⁿ)?"]
    G -->|Yes| H["Use DP/memoization"]
    
    B --> I["Is it O(n³)?"]
    I -->|Yes, n small| J["Optimize carefully"]
    I -->|Yes, n large| K["Definitely optimize"]
    
    D --> L["Use sorting/hashing"]
    E --> M["Profile first"]
    F --> N["Keep current"]
    H --> O["Add memoization"]
    J --> P["Check O(n²) possible"]
    K --> Q["Must optimize"]
    
    L --> R["✓ Optimization path"]
    M --> R
    N --> R
    O --> R
    P --> R
    Q --> R
    
    style R fill:#90ee90,color:#000,stroke:#333,stroke-width:2px
```

---

## Testing Strategy Flowchart

```mermaid
graph TD
    A["Testing Strategy"] --> B["Simple case"]
    
    B --> C["Trace 1 example"]
    C -->|Pass| D["Medium case"]
    C -->|Fail| E["Debug code"]
    E --> B
    
    D --> F["Trace 2-3 examples"]
    F -->|Pass| G["Edge cases"]
    F -->|Fail| E
    
    G --> H["Test identified edges"]
    H -->|Pass| I["Boundary values"]
    H -->|Fail| E
    
    I --> J["Test min/max values"]
    J -->|Pass| K["Stress test"]
    J -->|Fail| E
    
    K --> L["Large input if time"]
    L -->|Pass| M["All tests pass"]
    L -->|Timeout| N["Optimize or accept"]
    
    M --> O["✓ Solution verified"]
    N --> O
    
    style O fill:#90ee90,color:#000,stroke:#333,stroke-width:2px
```

---

## Interview Communication Flowchart

```mermaid
graph TD
    A["How to communicate?"] --> B["Before coding"]
    
    B --> C["Restate problem"]
    C --> D["Ask clarifying Qs"]
    D --> E["Explain approach"]
    E --> F["Walk through example"]
    F --> G["Get approval"]
    
    G --> H["During coding"]
    H --> I["Explain logic"]
    I --> J["Comment code"]
    J --> K["Ask for feedback"]
    
    K --> L["After coding"]
    L --> M["Trace example"]
    M --> N["Explain complexity"]
    N --> O["Discuss trade-offs"]
    O --> P["Answer follow-ups"]
    
    C --> Q["✓ Communication<br/>complete"]
    D --> Q
    E --> Q
    F --> Q
    G --> Q
    I --> Q
    J --> Q
    K --> Q
    M --> Q
    N --> Q
    O --> Q
    P --> Q
    
    style Q fill:#90ee90,color:#000,stroke:#333,stroke-width:2px
```

---

## Debugging Decision Tree

```mermaid
graph TD
    A["Code doesn't work"] --> B["Identify failure point"]
    
    B --> C["Wrong output?"]
    C -->|Yes| D["Check logic"]
    
    B --> E["Crashes?"]
    E -->|Yes| F["Check null/bounds"]
    
    B --> G["Timeout?"]
    G -->|Yes| H["Check complexity"]
    
    D --> I["Logic error:<br/>- Loop condition<br/>- State transition<br/>- Edge case"]
    F --> J["Safety error:<br/>- Null pointer<br/>- Array index<br/>- Division by 0"]
    H --> K["Performance error:<br/>- Nested loops<br/>- Data structure<br/>- Algorithm"]
    
    I --> L["Add print statements"]
    J --> L
    K --> M["Profile code"]
    
    L --> N["Trace execution"]
    M --> O["Optimize algorithm"]
    
    N --> P["Find bug"]
    O --> Q["Verify fix"]
    
    P --> R["Fix and re-test"]
    Q --> R
    
    R --> S["✓ Debug complete"]
    
    style S fill:#90ee90,color:#000,stroke:#333,stroke-width:2px
```

---

## Complexity Analysis Decision Tree

```mermaid
graph TD
    A["Given Time Limit<br/>& Input Size"] --> B["Calculate target<br/>complexity"]
    
    B --> C["Input size n"]
    
    C -->|n ≤ 10| D1["O(n³) or slower OK<br/>Brute force fine"]
    C -->|n ≤ 100| D2["O(n²) OK<br/>O(n³) risky"]
    C -->|n ≤ 1000| D3["O(n log n) needed<br/>O(n²) risky"]
    C -->|n ≤ 10⁴| D4["O(n log n) needed<br/>O(n²) borderline"]
    C -->|n ≤ 10⁵| D5["O(n log n) needed<br/>O(n²) too slow"]
    C -->|n ≤ 10⁶| D6["O(n) or O(n log n)<br/>O(n²) too slow"]
    C -->|n ≤ 10⁷| D7["O(n) required<br/>O(n log n) risky"]
    C -->|n > 10⁷| D8["O(n) or constant<br/>Pre-compute OK"]
    
    D1 --> E1["Can solve by:<br/>- Brute force<br/>- Backtracking<br/>- Exponential DP"]
    D2 --> E2["Can solve by:<br/>- DP<br/>- Sorting + 2-pointer<br/>- Nested loops"]
    D3 --> E3["Can solve by:<br/>- Sorting<br/>- Binary search<br/>- Single DP"]
    D4 --> E4["Can solve by:<br/>- Sorting O(n log n)<br/>- Graph BFS/DFS<br/>- Single pass DP"]
    D5 --> E5["Need:<br/>- O(n log n) algorithm<br/>- Efficient DS<br/>- Avoid 2D arrays"]
    D6 --> E6["Need:<br/>- Linear O(n)<br/>- Single pass or<br/>- Hash-based"]
    D7 --> E7["Need:<br/>- Very tight O(n)<br/>- Hand-optimized code<br/>- Minimal overhead"]
    D8 --> E8["Need:<br/>- Preprocessing allowed<br/>- O(1) query<br/>- Space intensive"]
    
    E1 --> F["Typical approaches:<br/>1. Backtracking<br/>2. Brute force<br/>3. Recursion"]
    E2 --> F
    E3 --> F
    E4 --> F
    E5 --> F
    E6 --> F
    E7 --> F
    E8 --> F
    
    F --> G["Time budget: ~10⁸ ops/sec<br/>Adjust for:<br/>- Simple ops: 10⁹<br/>- Complex ops: 10⁷<br/>- Worst case: 10⁶"]
```

### Complexity Reference Quick Table

| Input Size | Acceptable Complexity | Achievable Operations | Example |
|---|---|---|---|
| n ≤ 10 | O(n³), O(2ⁿ) | Brute force, all subsets | Permutation generation |
| n ≤ 100 | O(n²), O(n² log n) | Nested loops | Selection sort on small data |
| n ≤ 1,000 | O(n²) tight, O(n log n) safe | ~10⁶ operations | Bubble sort, 2D DP |
| n ≤ 10,000 | O(n log n), O(n√n) | ~10⁷ operations | Merge sort, complex DP |
| n ≤ 100,000 | O(n log n) | ~10⁶ operations | Quick sort, Dijkstra |
| n ≤ 1,000,000 | O(n), O(n log n) | ~10⁷ operations | Hash lookup, BFS |
| n > 1,000,000 | O(n), O(1) with preprocessing | ~10⁸ operations | Streaming, precompute |

**Time calculation:** Operations ÷ (10⁶ to 10⁹) ≈ seconds (depending on operation complexity)

---

## Common Pitfalls & How to Avoid

### 1. Not Reading Carefully

**❌ Pitfall:** Miss key constraint like "sorted" or "in-place"

**Solution:**
- Reread problem statement word-by-word
- Circle important keywords
- Ask clarifying questions
- Restate problem to interviewer

**Example:** "Is the array sorted?" changes HashMap O(1) vs BST O(log n)

---

### 2. Wrong Data Structure Choice

**❌ Pitfall:** Use array when HashMap needed, or vice versa

**Solution:**
- Identify critical operations first (lookup vs insertion vs deletion)
- Match DS to operation frequency
- Use DS Selection Guide (ds_selection_guide.md)

**Example:** 
- Need fast lookup → HashMap
- Need ordered traversal → TreeMap or BST
- Need k-largest → Min Heap

---

### 3. Not Handling Edge Cases

**❌ Pitfall:** Code works for main case but fails on: empty input, single element, all duplicates

**Solution:**
- Explicitly list edge cases
- Test each one before submission
- Add boundary checks in code

**Edge case checklist:**
```
□ Empty input (array length 0)
□ Single element
□ Two elements
□ All same values
□ All negative/all positive (if applicable)
□ Maximum/minimum constraints
□ Null/None values
```

---

### 4. Inefficient Time Complexity

**❌ Pitfall:** O(n²) solution on n=10⁶ input (100 billion operations = timeout)

**Solution:**
- Calculate required complexity before coding
- Use complexity reference table
- Don't optimize prematurely but aim for required complexity first

**Example:**
- n=10⁶: Need O(n) or O(n log n)
- n=1000: Can do O(n²) or even O(n²·log n)

---

### 5. Space Leak or Unbounded Memory

**❌ Pitfall:** Store all intermediate results, hit memory limit

**Solution:**
- Calculate space needed upfront
- Use rolling arrays for DP when possible
- Clean up large temporary structures
- Consider streaming/online algorithms

**Example:** Don't store all prefixes; compute on the fly

---

### 6. Off-by-One Errors in Loops

**❌ Pitfall:** `for i in range(n)` vs `for i in range(n-1)`, fence-post errors

**Solution:**
- Be careful with array indexing
- Use inclusive/exclusive bounds clearly
- Test with small arrays: n=1, n=2, n=3

**Debug technique:**
```python
# Instead of: for i in range(n)
# Trace: what's the last value of i?
# If you need 0 to n-1: range(n) ✓
# If you need 0 to n-2: range(n-1) ✓
```

---

### 7. Inefficient String/Array Concatenation

**❌ Pitfall:** `result = "" + str(x)` in loop = O(n²) on strings

**Solution:**
- Use list and join: `result = []; result.append(x); ''.join(result)`
- Or StringBuilder equivalent in Java
- For array building, append not extend

**Java example:**
```java
StringBuilder sb = new StringBuilder();
for (char c : arr) {
    sb.append(c);
}
return sb.toString(); // O(n)
// NOT: String s = ""; for ... s += c; // O(n²)
```

---

### 8. Not Verifying Algorithm Correctness

**❌ Pitfall:** Implement algorithm without understanding it

**Solution:**
- Trace through algorithm with at least 2 examples
- Verify loop invariants
- Check base cases and termination

**Example:** Before coding binary search, trace with: [1,3], [1,3,5], [2,4,6,8]

---

### 9. Confusing Similar Data Structures

**❌ Pitfall:** Use HashMap when should use TreeMap (need sorted order)

**Solution:**
- Know when each DS is appropriate
- Review before coding:
  - HashMap: Fast lookup, no order
  - TreeMap: Fast lookup, sorted order
  - Heap: Fast min/max, no random access
  - Trie: Fast prefix matching

---

### 10. Not Communicating Progress

**❌ Pitfall:** Silent coding, interviewer can't follow your logic

**Solution:**
- Explain approach before coding
- Name variables clearly
- Add comments for non-obvious logic
- Ask for feedback at key points

---

## Step-by-Step Walkthrough Example

### Problem: "Two Sum"
Find two numbers that add to target value.

#### Step 1: Clarify
```
Q: Can I use the same element twice?
A: No, must be different indices.

Q: Can array have duplicates?
A: Yes.

Q: What if no solution exists?
A: Return empty array or [-1, -1].

Q: Can array be empty?
A: No, at least 2 elements.
```

#### Step 2: Constraints
```
Input: array of n numbers, 1 ≤ n ≤ 10⁵
Time: Should be < 1 second → O(n) or O(n log n)
Space: Not specified → O(n) acceptable
```

#### Step 3: Plan
```
Option 1: Brute force O(n²)
- Try every pair
- Problem: Too slow for n=10⁵

Option 2: Sort + two pointers O(n log n)
- Sort array
- Use two pointers
- Good for space-conscious

Option 3: HashMap O(n)
- For each number, check if (target - number) exists
- Best for time

✓ CHOOSE: HashMap (optimal)
```

#### Step 4: Code
```python
def twoSum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []
```

#### Step 5: Test
```
Test 1: nums=[2,7,11,15], target=9
- i=0, num=2: complement=7, not seen, seen={2:0}
- i=1, num=7: complement=2, FOUND seen[2]=0, return [0,1] ✓

Test 2: nums=[3,3], target=6
- i=0, num=3: complement=3, not seen, seen={3:0}
- i=1, num=3: complement=3, FOUND seen[3]=0, return [0,1] ✓

Test 3: nums=[1,2], target=4
- i=0, num=1: complement=3, not seen, seen={1:0}
- i=1, num=2: complement=2, not seen, seen={1:0,2:1}
- return [] ✓
```

#### Step 6: Complexity Analysis
```
Time: O(n) - single pass through array
Space: O(n) - hashmap stores up to n elements

Within constraints? ✓
Can optimize? No, O(n) is optimal for this approach
```

#### Step 7: Discussion
```
Interviewer: Can you optimize space?
Answer: Not with this approach. Could use two-pointer on sorted array:
- Space: O(1) if no output array (or O(n) for sorted copy)
- Time: O(n log n) due to sort
- Trade-off: Better space, worse time

I chose HashMap because time is usually more important in interviews,
and O(n) time with O(n) space is better than O(n log n) time.
```

---

## Interview Day Tips

### Before You Start Coding
1. **Read problem twice** - catch constraints
2. **Ask clarifying questions** - 2-3 minutes well spent
3. **State your approach** - "I'll use HashMap and iterate once"
4. **Trace with example** - before any code
5. **Get approval** - "Does this approach sound good?"

### While Coding
1. **Name variables clearly** - `complement` not `c`, `seen_numbers` not `s`
2. **Write edge case handling first** - empty input, single element
3. **Add comments for complex logic** - but not obvious parts
4. **Code slowly and deliberately** - no rushing
5. **Compile/run as you go** - test incrementally

### After Coding
1. **Walkthrough with example** - trace through your code
2. **Test edge cases** - empty, single, duplicates, boundary
3. **Explain complexity** - time AND space
4. **Discuss trade-offs** - why this over alternatives
5. **Answer follow-up questions** - show flexibility

---

## Problem-Solving Checklist

### Pre-Implementation
- [ ] Reread problem statement
- [ ] Clarify ambiguous parts with interviewer
- [ ] Identify input/output formats
- [ ] List all edge cases
- [ ] State algorithm approach
- [ ] Verify approach with examples
- [ ] Estimate time/space

### During Implementation
- [ ] Handle edge cases first
- [ ] Use clear variable names
- [ ] Comment non-obvious code
- [ ] Avoid common pitfalls (off-by-one, string concat, etc)
- [ ] Test incrementally

### Post-Implementation
- [ ] Manually trace with example
- [ ] Test with edge cases
- [ ] Calculate actual complexity
- [ ] Verify against time/space limits
- [ ] Discuss alternatives
- [ ] Answer follow-up questions

---

## Common Interview Follow-up Questions

**"Can you optimize the space complexity?"**
- Trade time for space? (e.g., sort array for two-pointer)
- Use auxiliary structures? (e.g., index structures)
- Use in-place modifications? (if input modifiable)

**"What if you can't modify the input?"**
- Use different approach that doesn't mutate
- Or use copy of input

**"How would this change if n was 10⁹?"**
- Would you use streaming/online algorithm?
- Preprocess/index data?
- Use external sorting/data structures?

**"How would you test this in production?"**
- Unit tests for edge cases
- Property-based testing
- Fuzz testing
- Performance benchmarks

**"How would you explain this to someone else?"**
- Teach out loud
- Draw diagrams
- Use simple examples
- Start with brute force, then optimize

---

## Practice Problem Structure

Use this structure when practicing:

```
PROBLEM: [Name & link]
CATEGORY: [Sorting/DP/Graph/etc]
DIFFICULTY: [Easy/Medium/Hard]

UNDERSTANDING:
- Input: [Format & constraints]
- Output: [Format & constraints]
- Examples: [At least 3]
- Edge cases: [List]

APPROACH:
- DS needed: [Which and why]
- Algorithm: [Which and why]
- Time: [Complexity]
- Space: [Complexity]

IMPLEMENTATION:
- Code
- Comments

TESTING:
- Test cases traced
- Edge cases verified

REVIEW:
- Complexity verified
- Alternatives discussed
- Mistakes learned
```

Use this framework for every problem you practice. After 20-30 problems, it becomes second nature!

