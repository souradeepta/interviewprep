class Transaction: __init__(self): self.steps=[]
class DistributedTx:
    def __init__(self): self.txns=[]
    def begin(self): return Transaction()
    def add_step(self, t, step): t.steps.append(step)
    def commit(self, t): self.txns.append(t); return True
if __name__ == "__main__": dt=DistributedTx(); t=dt.begin(); dt.add_step(t, "debit"); dt.commit(t); print(len(dt.txns))