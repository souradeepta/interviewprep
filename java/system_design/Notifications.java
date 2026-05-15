import java.util.*;
public class Notifications{Map<Integer,List<String>>notifs=new HashMap<>();void send(int u,String m){notifs.computeIfAbsent(u,k->new ArrayList<>()).add(m);}public static void main(String[]a){Notifications n=new Notifications();n.send(1,"Hi");}}
