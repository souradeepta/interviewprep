import java.util.*;
class Server { int id; int conn; Server(int i) { id=i; conn=0; } String handle(String req) { return "Server "+id; } }
interface Strategy { Server select(List<Server> s); }
/**
 * [Brief description]
 *
 * @param [param] [description]
 * @return [description]
 * @time O([complexity])
 */
class RoundRobin implements Strategy { int idx; public Server select(List<Server> s) { return s.get((idx++)%s.size()); } }
/**
 * [Brief description]
 *
 * @param [param] [description]
 * @return [description]
 * @time O([complexity])
 */
class LeastConn implements Strategy { public Server select(List<Server> s) { return s.stream().min((a,b)->a.conn-b.conn).orElse(null); } }
class LoadBalancer { Strategy strat; List<Server> servers = new ArrayList<>(); LoadBalancer(Strategy s) { strat=s; }
  void add(Server s) { servers.add(s); } String route(String req) { return strat.select(servers).handle(req); }
}
/**
 * LoadBalancer2 - [Brief description]
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
public class LoadBalancer2 { public static void main(String[] a) { LoadBalancer lb = new LoadBalancer(new RoundRobin()); lb.add(new Server(1)); lb.add(new Server(2)); System.out.println(lb.route("req")); } }
