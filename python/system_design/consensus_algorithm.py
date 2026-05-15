from enum import Enum
class State(Enum): FOLLOWER=1; CANDIDATE=2; LEADER=3
class RaftNode:
    def __init__(self, id): self.id=id; self.state=State.FOLLOWER; self.term=0; self.votes=0
    def start_election(self): self.state=State.CANDIDATE; self.term+=1; self.votes=1
    def win_election(self): self.state=State.LEADER
if __name__ == "__main__": n=RaftNode(1); n.start_election(); n.win_election(); print(n.state)