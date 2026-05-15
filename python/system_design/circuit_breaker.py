from enum import Enum
class State(Enum): CLOSED=1; OPEN=2; HALF_OPEN=3
class CircuitBreaker:
    def __init__(self): self.state=State.CLOSED; self.failures=0; self.threshold=5
    def call(self): return self.state==State.CLOSED
    def fail(self): self.failures+=1; self.state=State.OPEN if self.failures>=self.threshold else self.state
if __name__ == "__main__": cb=CircuitBreaker(); [cb.fail() for _ in range(5)]; print(cb.state)