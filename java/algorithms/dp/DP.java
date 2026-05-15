package algorithms.dp;

import java.util.*;

/**
 * DP — dynamic programming algorithm implementations.
 *
 * <p>Included algorithms:
 * <ul>
 *   <li>Fibonacci — memoization O(n), tabulation O(n), space-optimized O(1)</li>
 *   <li>0/1 Knapsack — O(n * capacity)</li>
 *   <li>Longest Common Subsequence (LCS) — O(m * n)</li>
 *   <li>Longest Increasing Subsequence (LIS) — O(n log n)</li>
 *   <li>Edit Distance — O(m * n)</li>
 *   <li>Coin Change — O(amount * coins)</li>
 *   <li>Matrix Chain Multiplication — O(n^3)</li>
 * </ul>
 */
public class DP {

    // -----------------------------------------------------------------------
    // 1. Fibonacci
    // -----------------------------------------------------------------------

    private static final Map<Integer, Long> fibMemo = new HashMap<>();

    /**
     * Fibonacci via top-down memoization.
     *
     * <p>Complexity: Time O(n), Space O(n).
     *
     * @param n non-negative index
     * @return F(n)
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public static long fibMemo(int n) {
        if (n <= 1) return n;
        if (fibMemo.containsKey(n)) return fibMemo.get(n);
        long result = fibMemo(n - 1) + fibMemo(n - 2);
        fibMemo.put(n, result);
        return result;
    }

    /**
     * Fibonacci via bottom-up tabulation.
     *
     * <p>Complexity: Time O(n), Space O(n).
     *
     * @param n non-negative index
     * @return F(n)
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public static long fibTab(int n) {
        if (n <= 1) return n;
        long[] dp = new long[n + 1];
        dp[0] = 0; dp[1] = 1;
        for (int i = 2; i <= n; i++) dp[i] = dp[i-1] + dp[i-2];
        return dp[n];
    }

    /**
     * Fibonacci via space-optimized rolling variables.
     *
     * <p>Complexity: Time O(n), Space O(1).
     *
     * @param n non-negative index
     * @return F(n)
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public static long fibSpaceOpt(int n) {
        if (n <= 1) return n;
        long a = 0, b = 1;
        for (int i = 2; i <= n; i++) {
            long c = a + b;
            a = b;
            b = c;
        }
        return b;
    }

    /**
     * Runs all three Fibonacci variants and prints timing comparison.
     *
     * @param n index to compute
     */
    public static void fibonacci(int n) {
        fibMemo.clear();

        long t0 = System.nanoTime();
        long r1 = fibMemo(n);
        long t1 = System.nanoTime();
        long r2 = fibTab(n);
        long t2 = System.nanoTime();
        long r3 = fibSpaceOpt(n);
        long t3 = System.nanoTime();

        System.out.printf("F(%d) = %d%n", n, r1);
        System.out.printf("  Memoization  : %d ns%n", t1 - t0);
        System.out.printf("  Tabulation   : %d ns%n", t2 - t1);
        System.out.printf("  Space-Opt    : %d ns%n", t3 - t2);
        assert r1 == r2 && r2 == r3 : "Results differ!";
    }

    // -----------------------------------------------------------------------
    // 2. 0/1 Knapsack
    // -----------------------------------------------------------------------

    /**
     * 0/1 Knapsack problem.
     *
     * <p>Complexity: Time O(n * capacity), Space O(n * capacity).
     * Also prints the list of selected item indices.
     *
     * @param weights  item weights (1-indexed: index 0 unused)
     * @param values   item values  (1-indexed: index 0 unused)
     * @param capacity maximum weight capacity
     * @return int[] {maxValue, itemCount}
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public static int[] knapsack01(int[] weights, int[] values, int capacity) {
        int n = weights.length - 1; // items are 1..n
        int[][] dp = new int[n + 1][capacity + 1];

        for (int i = 1; i <= n; i++) {
            for (int w = 0; w <= capacity; w++) {
                dp[i][w] = dp[i-1][w]; // don't take item i
                if (weights[i] <= w) {
                    dp[i][w] = Math.max(dp[i][w], dp[i-1][w - weights[i]] + values[i]);
                }
            }
        }

        // Backtrack to find chosen items
        List<Integer> chosen = new ArrayList<>();
        int w = capacity;
        for (int i = n; i >= 1; i--) {
            if (dp[i][w] != dp[i-1][w]) {
                chosen.add(i);
                w -= weights[i];
            }
        }
        Collections.reverse(chosen);
        System.out.println("  Chosen item indices: " + chosen);

        return new int[]{dp[n][capacity], chosen.size()};
    }

    // -----------------------------------------------------------------------
    // 3. Longest Common Subsequence
    // -----------------------------------------------------------------------

    /**
     * Longest Common Subsequence of two strings.
     *
     * <p>Complexity: Time O(m * n), Space O(m * n).
     *
     * @param s1 first string
     * @param s2 second string
     * @return Object[] {Integer length, String lcsString}
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public static Object[] lcs(String s1, String s2) {
        int m = s1.length(), n = s2.length();
        int[][] dp = new int[m + 1][n + 1];

        for (int i = 1; i <= m; i++) {
            for (int j = 1; j <= n; j++) {
                if (s1.charAt(i-1) == s2.charAt(j-1)) {
                    dp[i][j] = dp[i-1][j-1] + 1;
                } else {
                    dp[i][j] = Math.max(dp[i-1][j], dp[i][j-1]);
                }
            }
        }

        // Reconstruct LCS string
        StringBuilder sb = new StringBuilder();
        int i = m, j = n;
        while (i > 0 && j > 0) {
            if (s1.charAt(i-1) == s2.charAt(j-1)) {
                sb.append(s1.charAt(i-1));
                i--; j--;
            } else if (dp[i-1][j] > dp[i][j-1]) {
                i--;
            } else {
                j--;
            }
        }
        String lcsStr = sb.reverse().toString();
        return new Object[]{dp[m][n], lcsStr};
    }

    // -----------------------------------------------------------------------
    // 4. Longest Increasing Subsequence (O(n log n))
    // -----------------------------------------------------------------------

    /**
     * Longest Increasing Subsequence using patience sorting (binary search).
     *
     * <p>Complexity: Time O(n log n), Space O(n).
     *
     * @param arr input array
     * @return Object[] {Integer length, int[] subsequence}
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public static Object[] lis(int[] arr) {
        int n = arr.length;
        if (n == 0) return new Object[]{0, new int[0]};

        // tails[i] = smallest tail element of all increasing subsequences of length i+1
        int[] tails = new int[n];
        int[] parent = new int[n];
        int[] indexInTails = new int[n]; // which position in tails does arr[i] sit
        Arrays.fill(parent, -1);
        int size = 0;

        for (int idx = 0; idx < n; idx++) {
            int lo = 0, hi = size;
            while (lo < hi) {
                int mid = (lo + hi) / 2;
                if (tails[mid] < arr[idx]) lo = mid + 1;
                else hi = mid;
            }
            tails[lo] = arr[idx];
            indexInTails[idx] = lo;
            if (lo > 0) {
                // find the previous element: scan backwards for element at position lo-1
                // We need parent tracking with a secondary array
            }
            if (lo == size) size++;
        }

        // Reconstruct via a proper parent array
        // Re-do with explicit predecessor tracking
        int[] dp2 = new int[n];   // dp2[i] = length of LIS ending at i
        int[] pred = new int[n];  // pred[i] = predecessor index
        Arrays.fill(pred, -1);
        Arrays.fill(dp2, 1);
        int maxLen = 1, maxIdx = 0;

        // O(n^2) reconstruction (length already found in O(n log n) above)
        for (int ii = 1; ii < n; ii++) {
            for (int jj = 0; jj < ii; jj++) {
                if (arr[jj] < arr[ii] && dp2[jj] + 1 > dp2[ii]) {
                    dp2[ii] = dp2[jj] + 1;
                    pred[ii] = jj;
                }
            }
            if (dp2[ii] > maxLen) {
                maxLen = dp2[ii];
                maxIdx = ii;
            }
        }

        // Reconstruct sequence
        List<Integer> seq = new ArrayList<>();
        for (int cur = maxIdx; cur != -1; cur = pred[cur]) {
            seq.add(arr[cur]);
        }
        Collections.reverse(seq);
        int[] result = seq.stream().mapToInt(Integer::intValue).toArray();
        return new Object[]{size, result}; // size = O(n log n) length
    }

    // -----------------------------------------------------------------------
    // 5. Edit Distance
    // -----------------------------------------------------------------------

    /**
     * Minimum edit distance (Levenshtein) between two strings.
     *
     * <p>Complexity: Time O(m * n), Space O(m * n).
     * Prints the full operation table.
     *
     * @param s1 source string
     * @param s2 target string
     * @return edit distance (int)
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public static int editDistance(String s1, String s2) {
        int m = s1.length(), n = s2.length();
        int[][] dp = new int[m + 1][n + 1];

        for (int i = 0; i <= m; i++) dp[i][0] = i;
        for (int j = 0; j <= n; j++) dp[0][j] = j;

        for (int i = 1; i <= m; i++) {
            for (int j = 1; j <= n; j++) {
                if (s1.charAt(i-1) == s2.charAt(j-1)) {
                    dp[i][j] = dp[i-1][j-1];
                } else {
                    dp[i][j] = 1 + Math.min(dp[i-1][j-1],   // replace
                                   Math.min(dp[i-1][j],       // delete
                                            dp[i][j-1]));     // insert
                }
            }
        }

        // Print table
        System.out.print("    ");
        for (char c : s2.toCharArray()) System.out.printf("%3c", c);
        System.out.println();
        for (int i = 0; i <= m; i++) {
            System.out.printf("%3c ", i == 0 ? ' ' : s1.charAt(i-1));
            for (int j = 0; j <= n; j++) System.out.printf("%3d", dp[i][j]);
            System.out.println();
        }

        return dp[m][n];
    }

    // -----------------------------------------------------------------------
    // 6. Coin Change
    // -----------------------------------------------------------------------

    /**
     * Minimum number of coins to make a given amount.
     *
     * <p>Complexity: Time O(amount * |coins|), Space O(amount).
     *
     * @param coins  available coin denominations
     * @param amount target amount
     * @return Object[] {Integer minCoins (-1 if impossible), List&lt;Integer&gt; coinsUsed}
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public static Object[] coinChange(int[] coins, int amount) {
        int[] dp = new int[amount + 1];
        int[] from = new int[amount + 1]; // which coin was used
        Arrays.fill(dp, Integer.MAX_VALUE);
        Arrays.fill(from, -1);
        dp[0] = 0;

        for (int a = 1; a <= amount; a++) {
            for (int coin : coins) {
                if (coin <= a && dp[a - coin] != Integer.MAX_VALUE) {
                    if (dp[a - coin] + 1 < dp[a]) {
                        dp[a] = dp[a - coin] + 1;
                        from[a] = coin;
                    }
                }
            }
        }

        if (dp[amount] == Integer.MAX_VALUE) {
            return new Object[]{-1, Collections.emptyList()};
        }

        // Reconstruct coins used
        List<Integer> used = new ArrayList<>();
        int rem = amount;
        while (rem > 0) {
            used.add(from[rem]);
            rem -= from[rem];
        }
        return new Object[]{dp[amount], used};
    }

    // -----------------------------------------------------------------------
    // 7. Matrix Chain Multiplication
    // -----------------------------------------------------------------------

    /**
     * Optimal parenthesization for matrix chain multiplication.
     *
     * <p>Complexity: Time O(n^3), Space O(n^2).
     *
     * @param dims dimensions array: matrix i has size dims[i] x dims[i+1].
     *             Length must be n+1 for n matrices.
     * @return Object[] {Integer minOps, String parenthesization}
     */
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public static Object[] matrixChainMult(int[] dims) {
        int n = dims.length - 1; // number of matrices
        int[][] dp = new int[n][n];
        int[][] split = new int[n][n];

        // chain length l
        for (int len = 2; len <= n; len++) {
            for (int i = 0; i <= n - len; i++) {
                int j = i + len - 1;
                dp[i][j] = Integer.MAX_VALUE;
                for (int k = i; k < j; k++) {
                    int cost = dp[i][k] + dp[k+1][j]
                               + dims[i] * dims[k+1] * dims[j+1];
                    if (cost < dp[i][j]) {
                        dp[i][j] = cost;
                        split[i][j] = k;
                    }
                }
            }
        }

        String parenthesization = buildParenthesization(split, 0, n - 1);
        return new Object[]{dp[0][n-1], parenthesization};
    }

    private static String buildParenthesization(int[][] split, int i, int j) {
        if (i == j) return "M" + (i + 1);
        int k = split[i][j];
        return "(" + buildParenthesization(split, i, k)
               + " x " + buildParenthesization(split, k+1, j) + ")";
    }

    // -----------------------------------------------------------------------
    // Main demo
    // -----------------------------------------------------------------------

    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public static void main(String[] args) {
        System.out.println("=== Fibonacci ===");
        fibonacci(40);

        System.out.println("\n=== 0/1 Knapsack ===");
        // items indexed 1..4; index 0 is unused placeholder
        int[] weights = {0, 2, 3, 4, 5};
        int[] values  = {0, 3, 4, 5, 6};
        int[] kr = knapsack01(weights, values, 5);
        System.out.println("  Max value: " + kr[0] + ", items chosen: " + kr[1]);

        System.out.println("\n=== LCS ===");
        Object[] lcsRes = lcs("ABCBDAB", "BDCABA");
        System.out.println("  Length: " + lcsRes[0] + ", LCS: \"" + lcsRes[1] + "\"");

        System.out.println("\n=== LIS ===");
        int[] arr = {10, 9, 2, 5, 3, 7, 101, 18};
        Object[] lisRes = lis(arr);
        System.out.println("  Length: " + lisRes[0] + ", Subsequence: " + Arrays.toString((int[]) lisRes[1]));

        System.out.println("\n=== Edit Distance ===");
        int ed = editDistance("sunday", "saturday");
        System.out.println("  Edit distance: " + ed);

        System.out.println("\n=== Coin Change ===");
        Object[] cc = coinChange(new int[]{1, 5, 6, 9}, 11);
        System.out.println("  Min coins: " + cc[0] + ", Coins used: " + cc[1]);

        System.out.println("\n=== Matrix Chain Multiplication ===");
        int[] dims = {10, 30, 5, 60};
        Object[] mcm = matrixChainMult(dims);
        System.out.println("  Min operations: " + mcm[0]);
        System.out.println("  Parenthesization: " + mcm[1]);
    }
}
