"""
Coin Change

Problem: Find the minimum number of coins to make a given amount.

You have unlimited coins of each denomination. Find the minimum number of coins
needed to make the target amount. Return -1 if it's impossible.

Input: coins = [1, 2, 5], amount = 5
Output: 1 (one coin of 5)

Input: coins = [2], amount = 3
Output: -1 (impossible)

Approach:
- Bottom-up dynamic programming
- dp[i] = minimum coins needed to make amount i
- For each amount, try all coins and take minimum
- Time: O(amount * len(coins)), Space: O(amount)
"""

def coinChange(coins, amount):
    """
    Find minimum number of coins to make amount.

    Args:
        coins: List of coin denominations
        amount: Target amount

    Returns:
        Minimum number of coins needed, or -1 if impossible

    Time: O(amount * len(coins))
    Space: O(amount)
    """
    # dp[i] = minimum coins to make amount i
    # Initialize with amount + 1 (impossible value)
    dp = [amount + 1] * (amount + 1)
    dp[0] = 0  # Base case: 0 coins needed for amount 0

    # For each amount from 1 to target
    for amt in range(1, amount + 1):
        # Try each coin
        for coin in coins:
            if coin <= amt:
                # If this coin is valid, update minimum
                dp[amt] = min(dp[amt], dp[amt - coin] + 1)

    # If dp[amount] is still amount + 1, it's impossible
    return dp[amount] if dp[amount] <= amount else -1

if __name__ == "__main__":
    # Test case 1: Normal case
    coins1 = [1, 2, 5]
    amount1 = 5
    result1 = coinChange(coins1, amount1)
    print(f"Test 1: coinChange({coins1}, {amount1}) = {result1} (expected 1)")

    # Test case 2: Impossible case
    coins2 = [2]
    amount2 = 3
    result2 = coinChange(coins2, amount2)
    print(f"Test 2: coinChange({coins2}, {amount2}) = {result2} (expected -1)")

    # Test case 3: Amount is 0
    coins3 = [1, 2, 5]
    amount3 = 0
    result3 = coinChange(coins3, amount3)
    print(f"Test 3: coinChange({coins3}, {amount3}) = {result3} (expected 0)")

    # Test case 4: Single coin matches
    coins4 = [1, 3, 4]
    amount4 = 6
    result4 = coinChange(coins4, amount4)
    print(f"Test 4: coinChange({coins4}, {amount4}) = {result4} (expected 2, using 3+3)")
