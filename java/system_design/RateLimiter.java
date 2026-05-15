import java.util.*;

public class RateLimiter {
    public static class TokenBucket {
        private double tokens, rate, capacity;
        private long lastRefill;
        
        public TokenBucket(double rate, double capacity) {
            this.rate = rate;
            this.capacity = capacity;
            this.tokens = capacity;
            this.lastRefill = System.currentTimeMillis();
        }
        
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

    public static void main(String[] args) {
        TokenBucket bucket = new TokenBucket(2, 5);
        for (int i = 0; i < 7; i++) {
            System.out.println("Request " + (i+1) + ": " + bucket.isAllowed());
        }
    }
}
