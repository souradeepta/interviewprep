import java.util.*;
public class SagaPattern{List<String>steps=new ArrayList<>();void addStep(String s){steps.add(s);}void execute(){System.out.println("Executing: "+steps);}public static void main(String[]a){SagaPattern s=new SagaPattern();s.addStep("debit");s.execute();}}
