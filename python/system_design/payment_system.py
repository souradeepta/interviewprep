import uuid
class Payment: __init__(self, u, amt): self.id=str(uuid.uuid4()); self.user=u; self.amount=amt; self.status='pending'
class Gateway: pass
class PaymentSystem:
    def __init__(self): self.payments={}; self.gw=Gateway()
    def process(self, u, amt): p=Payment(u,amt); self.payments[p.id]=p; p.status='completed'; return p
if __name__ == "__main__": ps=PaymentSystem(); p=ps.process(1,99.99); print(f"{p.id}: {p.status}")