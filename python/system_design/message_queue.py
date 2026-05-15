from collections import deque
class Topic: __init__(self, name): self.name=name; self.queue=deque(); self.subs=[]
class MessageQueue:
    def __init__(self): self.topics={}
    def create_topic(self, t): self.topics[t]=Topic(t)
    def publish(self, t, m): self.topics[t].queue.append(m)
    def subscribe(self, t, f): self.topics[t].subs.append(f)
    def consume(self, t): return list(self.topics[t].queue) if t in self.topics else []
if __name__ == "__main__": mq=MessageQueue(); mq.create_topic("t1"); mq.publish("t1","msg1"); print(mq.consume("t1"))