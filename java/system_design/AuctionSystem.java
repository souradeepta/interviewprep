import java.util.*;
public class AuctionSystem{Map<Integer,int[]>bids=new HashMap<>();void bid(int aid,int u,int amt){bids.put(aid,new int[]{u,amt});}public static void main(String[]a){AuctionSystem aus=new AuctionSystem();aus.bid(1,1,100);}}
