import java.util.*;

/**
 * RateLimiter - [Brief description]
 *
 * <p>OVERVIEW:
 * [Detailed explanation of what this class does]
 *
 * <p>COMPLEXITY:
 * <ul>
 *   <li>Time: [See method documentation]</li>
 *   <li>Space: O(n) where n is [the element count]</li>
 * </ul>
 *
 * <p>USAGE:
 * [How to use this class, with example]
 *
 * @author Interview Preparation
 * @since 1.0
 */

public class RateLimiter {
    public static class TokenBucket {
        private double tokens, rate, capacity;
        private long lastRefill;
        
        /**
         * [Brief description]
         *
         * @param [param] [description]
         * @return [description]
         * @time O([complexity])
         */
        public TokenBucket(double rate, double capacity) {
            this.rate = rate;
            this.capacity = capacity;
            this.tokens = capacity;
            this.lastRefill = System.currentTimeMillis();
        }
        
        /**
         * [Brief description]
         *
         * @param [param] [description]
         * @return [description]
         * @time O([complexity])
         */
        public boolean isAllowed() {
            long now = System.currentTimeMillis();
            double elapsed = (now - lastRefill) / 1000.0;
            tokens = Math.min(capacity, tokens + elapsed * rate);
            lastRefill = now;
            if (tokens >= 1) {
                tokens--;
                return true;
            }
            return false;
        }
    }

    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public static void main(String[] args) {
        TokenBucket bucket = new TokenBucket(2, 5);
        for (int i = 0; i < 7; i++) {
            System.out.println("Request " + (i+1) + ": " + bucket.isAllowed());
        }
    }
}
