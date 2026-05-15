import java.util.*;
public class DistributedTx{List<String>steps=new ArrayList<>();void addStep(String s){steps.add(s);}void commit(){System.out.println("Committed: "+steps.size());}public static void main(String[]a){DistributedTx dt=new DistributedTx();dt.addStep("debit");dt.commit();}}
