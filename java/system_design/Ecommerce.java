import java.util.*;
public class Ecommerce{Map<Integer,Integer>cart=new HashMap<>();void addCart(int p,int q){cart.put(p,q);}void checkout(){System.out.println("Order placed: "+cart.size());}public static void main(String[]a){Ecommerce e=new Ecommerce();e.addCart(1,5);e.checkout();}}
