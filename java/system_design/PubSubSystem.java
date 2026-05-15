import java.util.*;
interface Callback { void call(String msg); }
class PubSub { Map<String,List<Callback>> topics = new HashMap<>();
  void sub(String t, Callback c) { topics.computeIfAbsent(t, k->new ArrayList<>()).add(c); }
  void pub(String t, String m) { for(Callback c : topics.getOrDefault(t,new ArrayList<>())) c.call(m); }
}
/**
 * PubSubSystem - [Brief description]
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
public class PubSubSystem { public static void main(String[] a) { PubSub ps = new PubSub(); ps.sub("news", m->System.out.println("Got: "+m)); ps.pub("news", "Breaking!"); } }
