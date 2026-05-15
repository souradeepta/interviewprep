class Auction: __init__(self, item): self.item=item; self.bids=[]
class AuctionSystem:
    def __init__(self): self.auctions={}
    def create(self, item): a=Auction(item); self.auctions[id(a)]=a; return a
    def bid(self, aid, user, amt): self.auctions[aid].bids.append((user, amt))
    def get_winner(self, aid): bids=self.auctions[aid].bids; return max(bids, key=lambda x:x[1])[0] if bids else None
if __name__ == "__main__": aus=AuctionSystem(); a=aus.create("item"); aus.bid(id(a), 1, 100); print(aus.get_winner(id(a)))