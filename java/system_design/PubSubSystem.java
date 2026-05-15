import java.util.*;
interface Callback { void call(String msg); }
class PubSub { Map<String,List<Callback>> topics = new HashMap<>();
  void sub(String t, Callback c) { topics.computeIfAbsent(t, k->new ArrayList<>()).add(c); }
  void pub(String t, String m) { for(Callback c : topics.getOrDefault(t,new ArrayList<>())) c.call(m); }
}
public class PubSubSystem { public static void main(String[] a) { PubSub ps = new PubSub(); ps.sub("news", m->System.out.println("Got: "+m)); ps.pub("news", "Breaking!"); } }
