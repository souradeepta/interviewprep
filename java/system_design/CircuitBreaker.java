import java.util.*;
public class CircuitBreaker{enum State{CLOSED,OPEN,HALF_OPEN}State state=State.CLOSED;int failures=0;void fail(){failures++;if(failures>=5)state=State.OPEN;}public static void main(String[]a){CircuitBreaker cb=new CircuitBreaker();for(int i=0;i<5;i++)cb.fail();}}
