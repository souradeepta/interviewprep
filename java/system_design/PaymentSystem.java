import java.util.*;
public class PaymentSystem{class Payment{String id;int amount;Payment(int a){this.amount=a;this.id=UUID.randomUUID().toString();}}Map<String,Payment>payments=new HashMap<>();public static void main(String[]a){PaymentSystem ps=new PaymentSystem();}}
