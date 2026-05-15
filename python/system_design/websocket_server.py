class Client: __init__(self, cid): self.id=cid; self.room=None
class WebSocketServer:
    def __init__(self): self.clients={}; self.rooms={}
    def connect(self, cid): self.clients[cid]=Client(cid); return self.clients[cid]
    def send(self, cid, msg): return f"Sent to {cid}: {msg}"
    def broadcast(self, msg): return f"Broadcasted: {msg}"
if __name__ == "__main__": ws=WebSocketServer(); ws.connect(1); print(ws.send(1,"Hi"))