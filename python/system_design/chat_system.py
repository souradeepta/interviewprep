class Message: __init__(self,f,t,txt): self.frm=f; self.to=t; self.txt=txt; self.status='sent'
class ChatSystem:
    def __init__(self): self.msgs={}; self.convs={}
    def send(self, f, t, txt): m=Message(f,t,txt); self.msgs[id(m)]=m; return m
    def get_msgs(self, u1, u2): return [m for m in self.msgs.values() if (m.frm==u1 and m.to==u2) or (m.frm==u2 and m.to==u1)]
if __name__ == "__main__": c=ChatSystem(); c.send(1,2,"Hi"); print(len(c.get_msgs(1,2)))