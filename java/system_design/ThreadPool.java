import java.util.concurrent.*;
/**
 * ThreadPool - [Brief description]
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

/**
 * [Brief description]
 *
 * @param [param] [description]
 * @return [description]
 * @time O([complexity])
 */
public class ThreadPool { ExecutorService pool; ThreadPool(int n) { pool = Executors.newFixedThreadPool(n); }
  void submit(Runnable r) { pool.submit(r); }
  void shutdown() { pool.shutdown(); }
  /**
   * [Brief description]
   *
   * @param [param] [description]
   * @return [description]
   * @time O([complexity])
   */
  public static void main(String[] a) { ThreadPool tp = new ThreadPool(3); for(int i=0;i<5;i++) { int id=i; tp.submit(() -> System.out.println("Task "+id)); } tp.shutdown(); }
}
