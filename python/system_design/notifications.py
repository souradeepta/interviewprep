from enum import Enum
class Channel(Enum): EMAIL=1; SMS=2; PUSH=3; IN_APP=4
class Notification: __init__(self, u, m): self.user=u; self.msg=m; self.channels=[Channel.IN_APP]
class NotificationSystem:
    def __init__(self): self.notifs=[]
    def send(self, u, m, chans): n=Notification(u,m); n.channels=chans; self.notifs.append(n); return n
    def get(self, u): return [n for n in self.notifs if n.user==u]
if __name__ == "__main__": ns=NotificationSystem(); ns.send(1, "Hi", [Channel.PUSH]); print(len(ns.get(1)))