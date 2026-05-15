import java.util.*;
public class WalletSystem{Map<Integer,Integer>balances=new HashMap<>();void deposit(int u,int amt){balances.put(u,balances.getOrDefault(u,0)+amt);}int getBalance(int u){return balances.getOrDefault(u,0);}public static void main(String[]a){WalletSystem ws=new WalletSystem();ws.deposit(1,100);}}
