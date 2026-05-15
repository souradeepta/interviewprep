import java.util.*;
public class NewsFeed{Map<Integer,List<Integer>>f=new HashMap<>();Map<Integer,String>p=new HashMap<>();void post(int u,String c){p.put(u,c);for(int x:f.getOrDefault(u,new ArrayList<>()))System.out.println(x);}void follow(int u,int t){f.computeIfAbsent(t,k->new ArrayList<>()).add(u);}public static void main(String[]a){NewsFeed n=new NewsFeed();n.follow(1,2);n.post(2,"Hi");}}
