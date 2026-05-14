package algorithms.math;

import java.util.*;

/**
 * MathAlgorithms — essential number-theory and combinatorics for SDE interviews.
 *
 * <p>Included algorithms:
 * <ul>
 *   <li>GCD (Euclidean) — O(log min(a,b))</li>
 *   <li>LCM — O(log min(a,b))</li>
 *   <li>Extended Euclidean — O(log min(a,b))</li>
 *   <li>Sieve of Eratosthenes — O(n log log n)</li>
 *   <li>Fast (Binary) Exponentiation — O(log exp)</li>
 *   <li>Modular Inverse via Fermat's Little Theorem — O(log p)</li>
 *   <li>Modular Inverse via Extended GCD — O(log min(a,m))</li>
 *   <li>Prime Factorization (trial division) — O(sqrt(n))</li>
 *   <li>Prime Factorization (Pollard's rho) — O(n^(1/4)) expected</li>
 *   <li>nCr via Pascal's Triangle DP — O(n^2) build, O(1) query</li>
 *   <li>nCr mod prime — O(n) precomputation</li>
 *   <li>nPr — O(r)</li>
 *   <li>Catalan Numbers DP — O(n^2)</li>
 *   <li>Matrix Exponentiation — O(k^3 log n)</li>
 *   <li>Fibonacci via Matrix Exponentiation — O(log n)</li>
 * </ul>
 */
public class MathAlgorithms {

    // -----------------------------------------------------------------------
    // 1. GCD / LCM — Euclidean + Extended Euclidean
    // -----------------------------------------------------------------------

    /**
     * Greatest Common Divisor via the Euclidean algorithm.
     *
     * <p>Recursively applies gcd(a, b) = gcd(b, a % b) until b == 0.
     *
     * <p>Complexity: Time O(log min(a,b)), Space O(log min(a,b)) stack.
     *
     * @param a non-negative integer
     * @param b non-negative integer
     * @return gcd(a, b); gcd(0, x) = x by convention
     */
    public static long gcd(long a, long b) {
        return b == 0 ? a : gcd(b, a % b);
    }

    /**
     * Least Common Multiple.
     *
     * <p>Uses LCM(a,b) = a / gcd(a,b) * b to avoid overflow on large values.
     *
     * <p>Complexity: Time O(log min(a,b)), Space O(1).
     *
     * @param a positive integer
     * @param b positive integer
     * @return lcm(a, b)
     */
    public static long lcm(long a, long b) {
        return a / gcd(a, b) * b;
    }

    /**
     * Extended Euclidean Algorithm.
     *
     * <p>Finds integers x, y such that {@code a*x + b*y = gcd(a,b)}.
     * Results are returned via a 3-element array {@code [g, x, y]}.
     *
     * <p>Complexity: Time O(log min(a,b)), Space O(log min(a,b)) stack.
     *
     * @param a first integer
     * @param b second integer
     * @return long[] {g, x, y} where a*x + b*y == g == gcd(a,b)
     */
    public static long[] extendedGcd(long a, long b) {
        if (b == 0) return new long[]{a, 1, 0};
        long[] sub = extendedGcd(b, a % b);
        long g  = sub[0];
        long x1 = sub[1];
        long y1 = sub[2];
        // a*y1 + b*(x1 - (a/b)*y1) = g
        return new long[]{g, y1, x1 - (a / b) * y1};
    }

    // -----------------------------------------------------------------------
    // 2. Sieve of Eratosthenes
    // -----------------------------------------------------------------------

    /**
     * Generate all primes up to {@code n} using the Sieve of Eratosthenes.
     *
     * <p>Marks composites by crossing out multiples of each prime p,
     * starting from p*p (smaller multiples already processed).
     *
     * <p>Complexity: Time O(n log log n), Space O(n).
     *
     * @param n upper bound (inclusive); must be >= 2
     * @return list of primes in ascending order
     */
    public static List<Integer> sieve(int n) {
        if (n < 2) return Collections.emptyList();
        boolean[] isComposite = new boolean[n + 1];
        for (int p = 2; (long) p * p <= n; p++) {
            if (!isComposite[p]) {
                for (int m = p * p; m <= n; m += p) {
                    isComposite[m] = true;
                }
            }
        }
        List<Integer> primes = new ArrayList<>();
        for (int i = 2; i <= n; i++) {
            if (!isComposite[i]) primes.add(i);
        }
        return primes;
    }

    // -----------------------------------------------------------------------
    // 3. Fast Exponentiation — binary exponentiation
    // -----------------------------------------------------------------------

    /**
     * Iterative binary exponentiation: base^exp % mod.
     *
     * <p>Squares the base and halves the exponent at each step.
     *
     * <p>Complexity: Time O(log exp), Space O(1).
     *
     * @param base the base value
     * @param exp  non-negative exponent
     * @param mod  modulus (pass 0 to skip modular reduction — use with care for large values)
     * @return base^exp % mod  (or base^exp if mod == 0)
     */
    public static long fastPow(long base, long exp, long mod) {
        long result = 1;
        if (mod > 0) base %= mod;
        while (exp > 0) {
            if ((exp & 1) == 1) {
                result = mod > 0 ? result * base % mod : result * base;
            }
            base = mod > 0 ? base * base % mod : base * base;
            exp >>= 1;
        }
        return result;
    }

    // -----------------------------------------------------------------------
    // 4. Modular Arithmetic — modular inverse
    // -----------------------------------------------------------------------

    /**
     * Modular inverse of {@code a} modulo prime {@code p} via Fermat's Little Theorem.
     *
     * <p>By Fermat: a^(p-1) ≡ 1 (mod p) ⟹ a^(-1) ≡ a^(p-2) (mod p).
     * Requires {@code p} to be prime and {@code gcd(a, p) == 1}.
     *
     * <p>Complexity: Time O(log p), Space O(1).
     *
     * @param a value to invert (1 &lt;= a &lt; p)
     * @param p a prime modulus
     * @return a^(-1) mod p
     */
    public static long modInverseFermat(long a, long p) {
        return fastPow(a, p - 2, p);
    }

    /**
     * Modular inverse of {@code a} modulo {@code m} via the Extended Euclidean Algorithm.
     *
     * <p>Works for any modulus m (not just prime), provided {@code gcd(a,m) == 1}.
     *
     * <p>Complexity: Time O(log min(a,m)), Space O(log min(a,m)).
     *
     * @param a the value to invert
     * @param m the modulus
     * @return x such that (a * x) % m == 1
     * @throws ArithmeticException if gcd(a, m) != 1
     */
    public static long modInverseExtGcd(long a, long m) {
        long[] res = extendedGcd(((a % m) + m) % m, m);
        if (res[0] != 1) {
            throw new ArithmeticException("Modular inverse does not exist: gcd(" + a + "," + m + ")=" + res[0]);
        }
        return (res[1] % m + m) % m;
    }

    // -----------------------------------------------------------------------
    // 5. Prime Factorization — trial division + Pollard-rho
    // -----------------------------------------------------------------------

    /**
     * Prime factorization via trial division.
     *
     * <p>Divides out 2, then tries all odd divisors d up to sqrt(n).
     *
     * <p>Complexity: Time O(sqrt(n)), Space O(log n).
     *
     * @param n positive integer >= 2
     * @return sorted list of prime factors with repetition
     */
    public static List<Long> primeFactorsTrial(long n) {
        List<Long> factors = new ArrayList<>();
        while (n % 2 == 0) { factors.add(2L); n /= 2; }
        for (long d = 3; d * d <= n; d += 2) {
            while (n % d == 0) { factors.add(d); n /= d; }
        }
        if (n > 1) factors.add(n);
        return factors;
    }

    // --- Miller-Rabin primality helpers ---

    private static boolean millerRabin(long n, long a) {
        if (n % a == 0) return n == a;
        long d = n - 1;
        int r = 0;
        while (d % 2 == 0) { d /= 2; r++; }
        long x = fastPow(a, d, n);
        if (x == 1 || x == n - 1) return true;
        for (int i = 0; i < r - 1; i++) {
            x = x * x % n;
            if (x == n - 1) return true;
        }
        return false;
    }

    /**
     * Deterministic primality test for n &lt; 3.3 * 10^24 using Miller-Rabin.
     *
     * <p>Complexity: Time O(log^2 n) (12 witnesses), Space O(1).
     *
     * @param n integer to test
     * @return true if n is prime
     */
    public static boolean isPrimeFast(long n) {
        if (n < 2) return false;
        for (long p : new long[]{2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37}) {
            if (n == p) return true;
            if (!millerRabin(n, p)) return false;
        }
        return true;
    }

    private static final Random RNG = new Random(42);

    private static long pollardRhoStep(long n) {
        if (n % 2 == 0) return 2;
        while (true) {
            long x = RNG.nextLong() % (n - 2) + 2;
            long y = x;
            long c = RNG.nextLong() % (n - 1) + 1;
            long d = 1;
            while (d == 1) {
                x = (x * x + c) % n;
                y = (y * y + c) % n;
                y = (y * y + c) % n;
                d = gcd(Math.abs(x - y), n);
            }
            if (d != n) return d;
        }
    }

    /**
     * Prime factorization using Pollard's rho algorithm.
     *
     * <p>Recursively splits composites using Floyd cycle detection.
     * Uses Miller-Rabin to confirm primality of each factor.
     *
     * <p>Complexity: Time O(n^(1/4)) expected per factor, Space O(log n).
     *
     * @param n positive integer >= 2
     * @return sorted list of prime factors with repetition
     */
    public static List<Long> primeFactorsPollard(long n) {
        List<Long> factors = new ArrayList<>();
        pollardHelper(n, factors);
        Collections.sort(factors);
        return factors;
    }

    private static void pollardHelper(long n, List<Long> factors) {
        if (n <= 1) return;
        if (isPrimeFast(n)) { factors.add(n); return; }
        long d = n;
        while (d == n) d = pollardRhoStep(n);
        pollardHelper(d, factors);
        pollardHelper(n / d, factors);
    }

    // -----------------------------------------------------------------------
    // 6. Combination / Permutation
    // -----------------------------------------------------------------------

    /**
     * Build Pascal's triangle up to row {@code maxN}.
     *
     * <p>{@code C[i][j] = C(i, j)} — number of ways to choose j items from i.
     *
     * <p>Complexity: Time O(maxN^2), Space O(maxN^2).
     *
     * @param maxN maximum n for nCr queries
     * @return 2-D table where C[n][r] = nCr
     */
    public static long[][] buildPascal(int maxN) {
        long[][] C = new long[maxN + 1][maxN + 1];
        for (int i = 0; i <= maxN; i++) {
            C[i][0] = 1;
            for (int j = 1; j <= i; j++) {
                C[i][j] = C[i - 1][j - 1] + C[i - 1][j];
            }
        }
        return C;
    }

    /**
     * nCr using a pre-built Pascal's triangle.
     *
     * <p>Complexity: O(1) with pre-built table.
     *
     * @param n    total items
     * @param r    items to choose (0 &lt;= r &lt;= n)
     * @param pascal pre-built Pascal table from {@link #buildPascal(int)}
     * @return C(n, r), or 0 if r &lt; 0 or r &gt; n
     */
    public static long nCr(int n, int r, long[][] pascal) {
        if (r < 0 || r > n) return 0;
        return pascal[n][r];
    }

    /**
     * nCr modulo a prime using precomputed factorials and modular inverses.
     *
     * <p>Complexity: Time O(n) precomputation, O(1) per query.
     *
     * @param n   total items
     * @param r   items to choose
     * @param mod prime modulus (e.g. 1_000_000_007)
     * @return C(n, r) % mod
     */
    public static long nCrMod(int n, int r, long mod) {
        if (r < 0 || r > n) return 0;
        long[] fact    = new long[n + 1];
        long[] invFact = new long[n + 1];
        fact[0] = 1;
        for (int i = 1; i <= n; i++) fact[i] = fact[i - 1] * i % mod;
        invFact[n] = modInverseFermat(fact[n], mod);
        for (int i = n - 1; i >= 0; i--) invFact[i] = invFact[i + 1] * (i + 1) % mod;
        return fact[n] * invFact[r] % mod * invFact[n - r] % mod;
    }

    /**
     * nPr — number of ordered r-arrangements from n elements.
     *
     * <p>nPr = n * (n-1) * ... * (n-r+1).
     *
     * <p>Complexity: Time O(r), Space O(1).
     *
     * @param n total items
     * @param r items to arrange (0 &lt;= r &lt;= n)
     * @return P(n, r), or 0 if r &lt; 0 or r &gt; n
     */
    public static long nPr(int n, int r) {
        if (r < 0 || r > n) return 0;
        long result = 1;
        for (int i = n; i > n - r; i--) result *= i;
        return result;
    }

    // -----------------------------------------------------------------------
    // 7. Catalan Numbers
    // -----------------------------------------------------------------------

    /**
     * Compute the first n+1 Catalan numbers C(0) .. C(n) via DP.
     *
     * <p>C(0)=1, C(n) = sum_{i=0}^{n-1} C(i) * C(n-1-i).
     *
     * <p>Catalan numbers count: balanced parenthesizations, distinct BSTs,
     * monotonic lattice paths, polygon triangulations, and more.
     *
     * <p>Complexity: Time O(n^2), Space O(n).
     *
     * @param n upper index (inclusive)
     * @return long[] cat where cat[i] = C(i) for i in 0..n
     */
    public static long[] catalan(int n) {
        long[] cat = new long[n + 1];
        cat[0] = 1;
        for (int i = 1; i <= n; i++) {
            for (int j = 0; j < i; j++) {
                cat[i] += cat[j] * cat[i - 1 - j];
            }
        }
        return cat;
    }

    // -----------------------------------------------------------------------
    // 8. Matrix Exponentiation
    // -----------------------------------------------------------------------

    /**
     * Multiply two square matrices A and B modulo {@code mod}.
     *
     * <p>Complexity: Time O(k^3), Space O(k^2).
     *
     * @param A   first matrix (k x k)
     * @param B   second matrix (k x k)
     * @param mod modulus (0 = no reduction)
     * @return A @ B [% mod]
     */
    public static long[][] matMul(long[][] A, long[][] B, long mod) {
        int k = A.length;
        long[][] C = new long[k][k];
        for (int i = 0; i < k; i++) {
            for (int l = 0; l < k; l++) {
                if (A[i][l] == 0) continue;
                for (int j = 0; j < k; j++) {
                    C[i][j] += A[i][l] * B[l][j];
                    if (mod > 0) C[i][j] %= mod;
                }
            }
        }
        return C;
    }

    /**
     * Raise a square matrix M to the power {@code exp} via binary exponentiation.
     *
     * <p>Returns the k*k identity matrix when {@code exp == 0}.
     *
     * <p>Complexity: Time O(k^3 log exp), Space O(k^2).
     *
     * @param M   square matrix (k x k)
     * @param exp non-negative integer exponent
     * @param mod modulus (0 = no reduction)
     * @return M^exp [% mod]
     */
    public static long[][] matPow(long[][] M, long exp, long mod) {
        int k = M.length;
        // Identity matrix
        long[][] result = new long[k][k];
        for (int i = 0; i < k; i++) result[i][i] = 1;
        // Deep-copy base
        long[][] base = new long[k][k];
        for (int i = 0; i < k; i++) base[i] = Arrays.copyOf(M[i], k);
        while (exp > 0) {
            if ((exp & 1) == 1) result = matMul(result, base, mod);
            base = matMul(base, base, mod);
            exp >>= 1;
        }
        return result;
    }

    /**
     * Compute F(n) using 2x2 matrix exponentiation.
     *
     * <p>Uses the identity:
     * {@code [[F(n+1)],[F(n)]] = [[1,1],[1,0]]^n * [[1],[0]]}.
     *
     * <p>Complexity: Time O(log n), Space O(1) — matrix is always 2x2.
     *
     * @param n   non-negative Fibonacci index (F(0)=0, F(1)=1)
     * @param mod modulus (0 = exact)
     * @return F(n) [% mod]
     */
    public static long fibMatrix(long n, long mod) {
        if (n == 0) return 0;
        long[][] M = {{1, 1}, {1, 0}};
        long[][] Mn = matPow(M, n, mod);
        return Mn[0][1]; // M^n[0][1] = F(n)
    }

    /**
     * Solve a linear recurrence of order k via matrix exponentiation.
     *
     * <p>Given f(n) = c[0]*f(n-1) + c[1]*f(n-2) + ... + c[k-1]*f(n-k)
     * with initial values initial[0]=f(0), ..., initial[k-1]=f(k-1).
     *
     * <p>Complexity: Time O(k^3 log n), Space O(k^2).
     *
     * @param coeffs  recurrence coefficients {c0, c1, ..., c_{k-1}}
     * @param initial initial values {f(0), f(1), ..., f(k-1)}
     * @param n       index to compute
     * @param mod     modulus (0 = exact)
     * @return f(n) [% mod]
     */
    public static long linearRecurrence(long[] coeffs, long[] initial, long n, long mod) {
        int k = coeffs.length;
        if (n < k) return mod > 0 ? initial[(int) n] % mod : initial[(int) n];
        // Companion matrix
        long[][] M = new long[k][k];
        for (int j = 0; j < k; j++) M[0][j] = coeffs[j];
        for (int i = 1; i < k; i++) M[i][i - 1] = 1;
        long[][] Mn = matPow(M, n - k + 1, mod);
        // State vector: [f(k-1), f(k-2), ..., f(0)]
        long result = 0;
        for (int j = 0; j < k; j++) {
            long contribution = Mn[0][j] * initial[k - 1 - j];
            result += mod > 0 ? contribution % mod : contribution;
        }
        return mod > 0 ? result % mod : result;
    }

    // -----------------------------------------------------------------------
    // Main demo
    // -----------------------------------------------------------------------

    public static void main(String[] args) {
        final String SEP = "=".repeat(60);

        System.out.println(SEP);
        System.out.println("MATH ALGORITHMS DEMO");
        System.out.println(SEP);

        // ---- GCD / LCM ----
        System.out.println("\n--- GCD / LCM ---");
        long a = 48, b = 18;
        System.out.printf("  gcd(%d, %d)            = %d%n", a, b, gcd(a, b));
        System.out.printf("  lcm(%d, %d)            = %d%n", a, b, lcm(a, b));
        long[] ext = extendedGcd(a, b);
        System.out.printf("  extGcd(%d,%d) => g=%d, x=%d, y=%d%n", a, b, ext[0], ext[1], ext[2]);
        System.out.printf("  verify: %d*%d + %d*%d = %d  (should be %d)%n",
                a, ext[1], b, ext[2], a * ext[1] + b * ext[2], ext[0]);

        // ---- Sieve ----
        System.out.println("\n--- Sieve of Eratosthenes (primes up to 50) ---");
        System.out.println("  " + sieve(50));

        // ---- Fast Exponentiation ----
        System.out.println("\n--- Fast Exponentiation ---");
        long MOD = 1_000_000_007L;
        System.out.printf("  2^10               = %d%n", fastPow(2, 10, 0));
        System.out.printf("  3^1000000 %% MOD    = %d%n", fastPow(3, 1_000_000L, MOD));

        // ---- Modular Inverse ----
        System.out.println("\n--- Modular Inverse ---");
        long aVal = 123456789L;
        long invF = modInverseFermat(aVal, MOD);
        long invE = modInverseExtGcd(aVal, MOD);
        System.out.printf("  inv(%d) Fermat     = %d%n", aVal, invF);
        System.out.printf("  inv(%d) ExtGCD     = %d%n", aVal, invE);
        System.out.printf("  verify: a * inv %% MOD = %d  (should be 1)%n",
                aVal * invF % MOD);

        // ---- Prime Factorization ----
        System.out.println("\n--- Prime Factorization ---");
        for (long num : new long[]{360, 97, 1_000_000_007L, (long) Math.pow(2, 32)}) {
            List<Long> ft = primeFactorsTrial(num);
            List<Long> fp = primeFactorsPollard(num);
            System.out.printf("  %15d: trial=%s  pollard=%s%n", num, ft, fp);
        }

        // ---- nCr / nPr ----
        System.out.println("\n--- Combinations / Permutations ---");
        long[][] pascal = buildPascal(10);
        System.out.printf("  C(10,3)            = %d%n", nCr(10, 3, pascal));
        System.out.printf("  C(10,3) mod 1e9+7  = %d%n", nCrMod(10, 3, MOD));
        System.out.printf("  P(10,3)            = %d%n", nPr(10, 3));
        System.out.print("  Pascal row 5       = [");
        for (int j = 0; j <= 5; j++) System.out.print(pascal[5][j] + (j < 5 ? ", " : ""));
        System.out.println("]");

        // ---- Catalan Numbers ----
        System.out.println("\n--- Catalan Numbers C(0)..C(9) ---");
        long[] cats = catalan(9);
        for (int i = 0; i <= 9; i++) {
            System.out.printf("  C(%d) = %d%n", i, cats[i]);
        }

        // ---- Matrix Exponentiation ----
        System.out.println("\n--- Matrix Exponentiation (Fibonacci) ---");
        for (int idx : new int[]{0, 1, 5, 10, 50}) {
            System.out.printf("  F(%2d) via matrix   = %d%n", idx, fibMatrix(idx, 0));
        }
        System.out.printf("  F(50) %% 1e9+7      = %d%n", fibMatrix(50, MOD));

        // ---- Linear Recurrence (Tribonacci) ----
        System.out.println("\n--- Tribonacci via linearRecurrence ---");
        long[] tCoeffs  = {1, 1, 1};
        long[] tInitial = {0, 0, 1};
        for (int idx = 0; idx < 10; idx++) {
            System.out.printf("  T(%d) = %d%n", idx, linearRecurrence(tCoeffs, tInitial, idx, 0));
        }
    }
}
