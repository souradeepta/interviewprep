/**
 * Coin Change
 *
 * Problem: Find the minimum number of coins to make a given amount.
 *
 * You have unlimited coins of each denomination. Find the minimum number of coins
 * needed to make the target amount. Return -1 if it's impossible.
 *
 * Input: coins = [1, 2, 5], amount = 5
 * Output: 1 (one coin of 5)
 *
 * Input: coins = [2], amount = 3
 * Output: -1 (impossible)
 *
 * Approach:
 * - Bottom-up dynamic programming
 * - dp[i] = minimum coins needed to make amount i
 * - For each amount, try all coins and take minimum
 * - Time: O(amount * len(coins)), Space: O(amount)
 */
public class CoinChange {

    /**
     * Find minimum number of coins to make amount.
     *
     * @param coins Array of coin denominations
     * @param amount Target amount
     * @return Minimum number of coins needed, or -1 if impossible
     *
     * Time: O(amount * len(coins))
     * Space: O(amount)
     */
    public int coinChange(int[] coins, int amount) {
        // dp[i] = minimum coins to make amount i
        // Initialize with amount + 1 (impossible value)
        int[] dp = new int[amount + 1];
        for (int i = 0; i <= amount; i++) {
            dp[i] = amount + 1;
        }
        dp[0] = 0;  // Base case: 0 coins needed for amount 0

        // For each amount from 1 to target
        for (int amt = 1; amt <= amount; amt++) {
            // Try each coin
            for (int coin : coins) {
                if (coin <= amt) {
                    // If this coin is valid, update minimum
                    dp[amt] = Math.min(dp[amt], dp[amt - coin] + 1);
                }
            }
        }

        // If dp[amount] is still amount + 1, it's impossible
        return dp[amount] <= amount ? dp[amount] : -1;
    }

    public static void main(String[] args) {
        CoinChange solver = new CoinChange();

        // Test case 1: Normal case
        int[] coins1 = {1, 2, 5};
        int amount1 = 5;
        int result1 = solver.coinChange(coins1, amount1);
        System.out.println("Test 1: " + result1 + " (expected 1)");

        // Test case 2: Impossible case
        int[] coins2 = {2};
        int amount2 = 3;
        int result2 = solver.coinChange(coins2, amount2);
        System.out.println("Test 2: " + result2 + " (expected -1)");

        // Test case 3: Amount is 0
        int[] coins3 = {1, 2, 5};
        int amount3 = 0;
        int result3 = solver.coinChange(coins3, amount3);
        System.out.println("Test 3: " + result3 + " (expected 0)");

        // Test case 4: Multiple coins
        int[] coins4 = {1, 3, 4};
        int amount4 = 6;
        int result4 = solver.coinChange(coins4, amount4);
        System.out.println("Test 4: " + result4 + " (expected 2, using 3+3)");
    }
}
