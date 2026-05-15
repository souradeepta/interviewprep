class Cart: __init__(self): self.items={}
class Order: __init__(self, user, items): self.user=user; self.items=items; self.status='pending'
class Inventory: __init__(self): self.stock={}
    def reserve(self, p, q): self.stock[p] = self.stock.get(p,0)-q; return self.stock[p]>=0
    def release(self, p, q): self.stock[p]+=q
class ECommerce:
    def __init__(self): self.cart=Cart(); self.inv=Inventory(); self.orders=[]
    def checkout(self, user, items):
        o = Order(user, items); self.orders.append(o); return o
if __name__ == "__main__": e=ECommerce(); print(len(e.orders))