import java.util.*;
public class Leaderboard{Map<Integer,Integer>scores=new HashMap<>();void update(int u,int pts){scores.put(u,scores.getOrDefault(u,0)+pts);}public static void main(String[]a){Leaderboard lb=new Leaderboard();lb.update(1,100);System.out.println(scores);}}
