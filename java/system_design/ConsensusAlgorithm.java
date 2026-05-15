import java.util.*;
public class ConsensusAlgorithm{enum State{FOLLOWER,CANDIDATE,LEADER}State state=State.FOLLOWER;int term=0;void startElection(){state=State.CANDIDATE;term++;}public static void main(String[]a){ConsensusAlgorithm ca=new ConsensusAlgorithm();ca.startElection();}}
