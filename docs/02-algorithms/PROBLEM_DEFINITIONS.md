# New Curated Problems for Learning Paths

**Gap Target:** 58 problems to bring all domains to 8-10 per domain  
**Priority:** Follow order below (critical gaps first)

---

## Domain: Linked Lists (Need 9)

### Easy (4)
1. **Reverse Linked List** — Reverse a singly linked list
   - Pattern: Pointer reversal
   - Difficulty: Easy
   - Time: 20 min
   - Files: `python/new_problems/reverse_linked_list.py` | `java/new_problems/ReverseLinkedList.java`

2. **Detect Cycle** — Detect if linked list has a cycle
   - Pattern: Floyd's cycle detection
   - Difficulty: Easy
   - Time: 20 min
   - Files: `python/new_problems/detect_cycle.py` | `java/new_problems/DetectCycle.java`

3. **Remove Nth Node** — Remove nth node from end of list
   - Pattern: Two pointers / dummy node
   - Difficulty: Easy
   - Time: 25 min
   - Files: `python/new_problems/remove_nth_node.py` | `java/new_problems/RemoveNthNode.java`

4. **Merge Two Lists** — Merge two sorted linked lists
   - Pattern: Pointer traversal
   - Difficulty: Easy
   - Time: 20 min
   - Files: `python/new_problems/merge_sorted_lists.py` | `java/new_problems/MergeSortedLists.java`

### Medium (3)
5. **Reorder List** — Reorder list to: L0 → Ln → L1 → Ln-1 → ...
   - Pattern: Reversal + merge
   - Difficulty: Medium
   - Time: 30 min
   - Files: `python/new_problems/reorder_list.py` | `java/new_problems/ReorderList.java`

6. **Palindrome List** — Check if linked list is palindrome
   - Pattern: Slow/fast pointers + reversal
   - Difficulty: Medium
   - Time: 30 min
   - Files: `python/new_problems/palindrome_list.py` | `java/new_problems/PalindromeList.java`

7. **Copy Random Pointer** — Deep copy linked list with random pointers
   - Pattern: Hash map / pointer manipulation
   - Difficulty: Medium
   - Time: 35 min
   - Files: `python/new_problems/copy_random_pointer.py` | `java/new_problems/CopyRandomPointer.java`

### Hard (2)
8. **Reverse K Group** — Reverse every K group of nodes
   - Pattern: Recursion / iteration
   - Difficulty: Hard
   - Time: 35 min
   - Files: `python/new_problems/reverse_k_group.py` | `java/new_problems/ReverseKGroup.java`

9. **Flatten List** — Flatten multilevel linked list
   - Pattern: DFS
   - Difficulty: Hard
   - Time: 30 min
   - Files: `python/new_problems/flatten_list.py` | `java/new_problems/FlattenList.java`

---

## Domain: Bit Manipulation (Need 7)

### Easy (3)
1. **Single Number** — Find number appearing once, others twice
   - Pattern: XOR
   - Time: 15 min
   - Files: `python/new_problems/single_number.py` | `java/new_problems/SingleNumber.java`

2. **Power of Two** — Check if number is power of 2
   - Pattern: Bitwise AND trick
   - Time: 10 min
   - Files: `python/new_problems/power_of_two.py` | `java/new_problems/PowerOfTwo.java`

3. **Hamming Distance** — Count bit differences between two numbers
   - Pattern: XOR + bit counting
   - Time: 15 min
   - Files: `python/new_problems/hamming_distance.py` | `java/new_problems/HammingDistance.java`

### Medium (3)
4. **Bitwise AND of Range** — Bitwise AND of all numbers in range [m, n]
   - Pattern: Bit manipulation
   - Time: 25 min
   - Files: `python/new_problems/bitwise_and_range.py` | `java/new_problems/BitwiseAndRange.java`

5. **Number of 1 Bits** — Count number of 1 bits in binary representation
   - Pattern: Brian Kernighan's algorithm
   - Time: 20 min
   - Files: `python/new_problems/count_1_bits.py` | `java/new_problems/Count1Bits.java`

6. **Missing Number** — Find missing number in array 0 to n
   - Pattern: XOR or math
   - Time: 20 min
   - Files: `python/new_problems/missing_number.py` | `java/new_problems/MissingNumber.java`

### Hard (1)
7. **Max XOR Pair** — Find two numbers with max XOR value
   - Pattern: Trie or bit manipulation
   - Time: 35 min
   - Files: `python/new_problems/max_xor_pair.py` | `java/new_problems/MaxXorPair.java`

---

## Domain: Dynamic Programming (Need 7)

### Easy (2)
1. **Climbing Stairs** — Count ways to climb n stairs (1 or 2 at a time)
   - Pattern: Simple DP
   - Time: 15 min
   - Files: `python/new_problems/climbing_stairs.py` | `java/new_problems/ClimbingStairs.java`

2. **Best Time to Buy Stock** — Max profit from one buy-sell
   - Pattern: Single pass DP
   - Time: 20 min
   - Files: `python/new_problems/best_time_stock.py` | `java/new_problems/BestTimeStock.java`

### Medium (3)
3. **Coin Change** — Minimum coins to make amount
   - Pattern: Bottom-up DP
   - Time: 25 min
   - Files: `python/new_problems/coin_change.py` | `java/new_problems/CoinChange.java`

4. **House Robber** — Max loot from houses without robbing adjacent
   - Pattern: DP with states
   - Time: 25 min
   - Files: `python/new_problems/house_robber.py` | `java/new_problems/HouseRobber.java`

5. **Word Break** — Check if string can be segmented by dictionary
   - Pattern: DP with hash set
   - Time: 30 min
   - Files: `python/new_problems/word_break.py` | `java/new_problems/WordBreak.java`

### Hard (2)
6. **Longest Palindromic Substring** — Find longest palindrome in string
   - Pattern: DP or expand around center
   - Time: 30 min
   - Files: `python/new_problems/longest_palindrome_substring.py` | `java/new_problems/LongestPalindromeSubstring.java`

7. **Wildcard Matching** — Match string with ? and * wildcards
   - Pattern: 2D DP with greedy optimization
   - Time: 35 min
   - Files: `python/new_problems/wildcard_matching.py` | `java/new_problems/WildcardMatching.java`

---

## Domain: Strings (Need 7)

### Easy (3)
1. **Valid Anagram** — Check if two strings are anagrams
   - Pattern: Counting / sorting
   - Time: 15 min
   - Files: `python/new_problems/valid_anagram.py` | `java/new_problems/ValidAnagram.java`

2. **Isomorphic Strings** — Check if strings follow same pattern
   - Pattern: Hash map
   - Time: 20 min
   - Files: `python/new_problems/isomorphic_strings.py` | `java/new_problems/IsomorphicStrings.java`

3. **First Unique Character** — Find index of first unique char
   - Pattern: Counting
   - Time: 15 min
   - Files: `python/new_problems/first_unique_char.py` | `java/new_problems/FirstUniqueChar.java`

### Medium (3)
4. **Group Anagrams** — Group anagrams together
   - Pattern: Hash map + sorting
   - Time: 25 min
   - Files: `python/new_problems/group_anagrams.py` | `java/new_problems/GroupAnagrams.java`

5. **Shortest Palindrome** — Shortest palindrome by adding chars at front
   - Pattern: KMP or brute force
   - Time: 30 min
   - Files: `python/new_problems/shortest_palindrome.py` | `java/new_problems/ShortestPalindrome.java`

6. **Letter Combinations** — Letter combinations of phone number
   - Pattern: Backtracking
   - Time: 25 min
   - Files: `python/new_problems/letter_combinations.py` | `java/new_problems/LetterCombinations.java`

### Hard (1)
7. **Regular Expression Matching** — Match regex pattern with . and *
   - Pattern: 2D DP
   - Time: 35 min
   - Files: `python/new_problems/regex_matching.py` | `java/new_problems/RegexMatching.java`

---

## Domain: Arrays (Need 6)

### Easy (2)
1. **Buy & Sell Stock II** — Max profit from multiple transactions
   - Pattern: Greedy
   - Time: 20 min
   - Files: `python/new_problems/buy_sell_stock_2.py` | `java/new_problems/BuySellStock2.java`

2. **Rotate Array** — Rotate array by k positions
   - Pattern: Array rotation techniques
   - Time: 20 min
   - Files: `python/new_problems/rotate_array.py` | `java/new_problems/RotateArray.java`

### Medium (3)
3. **Container With Most Water** — Find two lines holding most water
   - Pattern: Two pointers
   - Time: 25 min
   - Files: `python/new_problems/container_water.py` | `java/new_problems/ContainerWater.java`

4. **Next Permutation** — Find next lexicographically larger permutation
   - Pattern: Array manipulation
   - Time: 30 min
   - Files: `python/new_problems/next_permutation.py` | `java/new_problems/NextPermutation.java`

5. **Product Array Except Self** — Product of all elements except current
   - Pattern: Prefix/suffix products
   - Time: 25 min
   - Files: `python/new_problems/product_except_self.py` | `java/new_problems/ProductExceptSelf.java`

### Hard (1)
6. **Trapping Rain Water** — Amount of water trapped after rain
   - Pattern: Two pointers or DP
   - Time: 35 min
   - Files: `python/new_problems/trapping_rain.py` | `java/new_problems/TrappingRain.java`

---

## Domain: Graphs (Need 6)

### Easy (2)
1. **Valid Tree** — Check if edges form a valid tree
   - Pattern: Union-Find or DFS
   - Time: 20 min
   - Files: `python/new_problems/valid_tree.py` | `java/new_problems/ValidTree.java`

2. **Clone Graph** — Deep copy of graph
   - Pattern: DFS/BFS with hash map
   - Time: 25 min
   - Files: `python/new_problems/clone_graph.py` | `java/new_problems/CloneGraph.java`

### Medium (3)
3. **Course Schedule** — Check if courses can be completed (cycle detection)
   - Pattern: Topological sort
   - Time: 25 min
   - Files: `python/new_problems/course_schedule.py` | `java/new_problems/CourseSchedule.java`

4. **Path Sum II** — All root-to-leaf paths summing to target
   - Pattern: DFS backtracking
   - Time: 30 min
   - Files: `python/new_problems/path_sum_2.py` | `java/new_problems/PathSum2.java`

5. **Surrounded Regions** — Capture regions surrounded by boundary
   - Pattern: DFS from edges
   - Time: 25 min
   - Files: `python/new_problems/surrounded_regions.py` | `java/new_problems/SurroundedRegions.java`

### Hard (1)
6. **Alien Dictionary** — Find alien dictionary order from sorted words
   - Pattern: Topological sort
   - Time: 35 min
   - Files: `python/new_problems/alien_dictionary.py` | `java/new_problems/AlienDictionary.java`

---

## Domain: Sorting & Searching (Need 6)

### Easy (2)
1. **First Bad Version** — Find first bad version (binary search)
   - Pattern: Binary search
   - Time: 15 min
   - Files: `python/new_problems/first_bad_version.py` | `java/new_problems/FirstBadVersion.java`

2. **Valid Perfect Square** — Check if number is perfect square
   - Pattern: Binary search
   - Time: 20 min
   - Files: `python/new_problems/perfect_square.py` | `java/new_problems/PerfectSquare.java`

### Medium (3)
3. **Kth Largest Element** — Find kth largest in unsorted array
   - Pattern: Heap or quickselect
   - Time: 25 min
   - Files: `python/new_problems/kth_largest.py` | `java/new_problems/KthLargest.java`

4. **Sorted Rotated Array Search II** — Search with duplicates allowed
   - Pattern: Binary search variant
   - Time: 30 min
   - Files: `python/new_problems/search_rotated_2.py` | `java/new_problems/SearchRotated2.java`

5. **Find Peak Element** — Find peak (greater than neighbors)
   - Pattern: Binary search
   - Time: 25 min
   - Files: `python/new_problems/find_peak.py` | `java/new_problems/FindPeak.java`

### Hard (1)
6. **Median of Two Sorted Arrays** — Find median of two sorted arrays
   - Pattern: Binary search
   - Time: 35 min
   - Files: `python/new_problems/median_sorted_arrays.py` | `java/new_problems/MedianSortedArrays.java`

---

## Domain: Heaps (Need 4)

### Easy (1)
1. **Last Stone Weight** — Simulate throwing stones at each other
   - Pattern: Max heap
   - Time: 20 min
   - Files: `python/new_problems/last_stone_weight.py` | `java/new_problems/LastStoneWeight.java`

### Medium (2)
2. **Top K Frequent** — Find k most frequent elements
   - Pattern: Min heap
   - Time: 25 min
   - Files: `python/new_problems/top_k_frequent.py` | `java/new_problems/TopKFrequent.java`

3. **Reorganize String** — Reorganize string so no adjacent chars are same
   - Pattern: Max heap
   - Time: 25 min
   - Files: `python/new_problems/reorganize_string.py` | `java/new_problems/ReorganizeString.java`

### Hard (1)
4. **Rearrange String K Distance Apart** — Rearrange with distance k
   - Pattern: Max heap + queue
   - Time: 30 min
   - Files: `python/new_problems/rearrange_string_k.py` | `java/new_problems/RearrangeStringK.java`

---

## Domain: Hash Tables (Need 3)

### Easy (1)
1. **Intersection of Arrays** — Find intersection of two arrays
   - Pattern: Hash set
   - Time: 15 min
   - Files: `python/new_problems/intersection_arrays.py` | `java/new_problems/IntersectionArrays.java`

### Medium (2)
2. **4Sum II** — Count quadruplets summing to target
   - Pattern: Hash map
   - Time: 25 min
   - Files: `python/new_problems/4sum_2.py` | `java/new_problems/4Sum2.java`

3. **Majority Element II** — Find all elements appearing > n/3 times
   - Pattern: Hash map or Boyer-Moore
   - Time: 25 min
   - Files: `python/new_problems/majority_element_2.py` | `java/new_problems/MajorityElement2.java`

---

## Domain: Stacks/Queues (Need 3)

### Easy (1)
1. **Min Stack** — Stack with O(1) min queries
   - Pattern: Auxiliary stack
   - Time: 20 min
   - Files: `python/new_problems/min_stack.py` | `java/new_problems/MinStack.java`

### Medium (2)
2. **Evaluate RPN** — Evaluate reverse Polish notation
   - Pattern: Stack
   - Time: 25 min
   - Files: `python/new_problems/evaluate_rpn.py` | `java/new_problems/EvaluateRPN.java`

3. **Implement Queue with Stacks** — Implement queue using two stacks
   - Pattern: Stack manipulation
   - Time: 20 min
   - Files: `python/new_problems/queue_with_stacks.py` | `java/new_problems/QueueWithStacks.java`

---

## Domain: System Design Fundamentals (Need 3)

### Easy (2)
1. **LRU Cache** — Implement LRU cache
   - Pattern: Hash map + doubly linked list
   - Time: 30 min
   - Files: `python/new_problems/lru_cache.py` | `java/new_problems/LRUCache.java`

2. **Design HashMap** — Implement hash map from scratch
   - Pattern: Array + linked list
   - Time: 30 min
   - Files: `python/new_problems/design_hashmap.py` | `java/new_problems/DesignHashMap.java`

### Medium (1)
3. **Design File System** — File system with add/search capabilities
   - Pattern: Trie + design
   - Time: 35 min
   - Files: `python/new_problems/design_filesystem.py` | `java/new_problems/DesignFileSystem.java`

---

## TOTAL: 58 NEW PROBLEMS

### Summary by Difficulty
- Easy: 21 problems
- Medium: 30 problems
- Hard: 7 problems

### Summary by Domain
- Linked Lists: 9
- Bit Manipulation: 7
- Dynamic Programming: 7
- Strings: 7
- Arrays: 6
- Graphs: 6
- Sorting & Searching: 6
- Heaps: 4
- Hash Tables: 3
- Stacks/Queues: 3
- System Design Fundamentals: 3

---

## Implementation Plan

For each problem:
1. Create Python skeleton: `python/new_problems/{name}.py`
2. Create Java skeleton: `java/new_problems/{Name}.java`
3. Add to appropriate domain file in `learning-paths/domains/`
4. Link from sequential tracks and playbooks

See `TEMPLATE.md` for code structure examples.
