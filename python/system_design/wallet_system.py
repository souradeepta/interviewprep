class Account: __init__(self, u): self.user=u; self.balance=0; self.txns=[]
class WalletSystem:
    def __init__(self): self.accounts={}
    def deposit(self, u, amt): self.accounts.setdefault(u, Account(u)).balance+=amt
    def withdraw(self, u, amt): self.accounts[u].balance-=amt if self.accounts[u].balance>=amt else 0
    def get_balance(self, u): return self.accounts.get(u, Account(u)).balance
if __name__ == "__main__": ws=WalletSystem(); ws.deposit(1, 100); print(ws.get_balance(1))