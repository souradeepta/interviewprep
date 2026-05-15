import java.util.*;
public class ChatSystem{class Msg{int f,t;String txt;Msg(int f,int t,String txt){this.f=f;this.t=t;this.txt=txt;}}Map<Integer,Msg>msgs=new HashMap<>();void send(int f,int t,String txt){msgs.put(msgs.size(),new Msg(f,t,txt));}public static void main(String[]a){ChatSystem c=new ChatSystem();c.send(1,2,"Hi");}}
