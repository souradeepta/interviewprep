class LedgerEntry: __init__(self, f, t, amt): self.frm=f; self.to=t; self.amt=amt
class TransactionLedger:
    def __init__(self): self.entries=[]
    def append(self, f, t, amt): self.entries.append(LedgerEntry(f, t, amt))
    def get_balance(self, acc): 
        debits=sum(e.amt for e in self.entries if e.frm==acc)
        credits=sum(e.amt for e in self.entries if e.to==acc)
        return credits-debits
if __name__ == "__main__": tl=TransactionLedger(); tl.append(1, 2, 100); print(tl.get_balance(2))