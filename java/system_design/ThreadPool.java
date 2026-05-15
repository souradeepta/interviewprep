import java.util.concurrent.*;
public class ThreadPool { ExecutorService pool; ThreadPool(int n) { pool = Executors.newFixedThreadPool(n); }
  void submit(Runnable r) { pool.submit(r); }
  void shutdown() { pool.shutdown(); }
  public static void main(String[] a) { ThreadPool tp = new ThreadPool(3); for(int i=0;i<5;i++) { int id=i; tp.submit(() -> System.out.println("Task "+id)); } tp.shutdown(); }
}
