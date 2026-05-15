import java.util.*;
class Server { int id; int conn; Server(int i) { id=i; conn=0; } String handle(String req) { return "Server "+id; } }
interface Strategy { Server select(List<Server> s); }
class RoundRobin implements Strategy { int idx; public Server select(List<Server> s) { return s.get((idx++)%s.size()); } }
class LeastConn implements Strategy { public Server select(List<Server> s) { return s.stream().min((a,b)->a.conn-b.conn).orElse(null); } }
class LoadBalancer { Strategy strat; List<Server> servers = new ArrayList<>(); LoadBalancer(Strategy s) { strat=s; }
  void add(Server s) { servers.add(s); } String route(String req) { return strat.select(servers).handle(req); }
}
public class LoadBalancer2 { public static void main(String[] a) { LoadBalancer lb = new LoadBalancer(new RoundRobin()); lb.add(new Server(1)); lb.add(new Server(2)); System.out.println(lb.route("req")); } }
