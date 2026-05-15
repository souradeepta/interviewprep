import java.util.*;
public class RecommendationEngine{Map<Integer,Set<Integer>>likes=new HashMap<>();void like(int u,int i){likes.computeIfAbsent(u,k->new HashSet<>()).add(i);}public static void main(String[]a){RecommendationEngine re=new RecommendationEngine();re.like(1,1);}}
