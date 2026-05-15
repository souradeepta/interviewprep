import java.util.*;
public class TransactionLedger{class Entry{int f,t,amt;Entry(int f,int t,int a){this.f=f;this.t=t;this.amt=a;}}List<Entry>entries=new ArrayList<>();void append(int f,int t,int a){entries.add(new Entry(f,t,a));}public static void main(String[]a){TransactionLedger tl=new TransactionLedger();tl.append(1,2,100);}}
