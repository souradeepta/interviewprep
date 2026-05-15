import java.util.*;
public class FollowersSystem{Map<Integer,Set<Integer>>followers=new HashMap<>();void follow(int u,int t){followers.computeIfAbsent(t,k->new HashSet<>()).add(u);}public static void main(String[]a){FollowersSystem fs=new FollowersSystem();fs.follow(1,2);}}
