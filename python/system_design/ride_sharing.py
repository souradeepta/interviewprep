import math
class Location: __init__(self,x,y): self.x=x; self.y=y
    def distance(self, o): return math.sqrt((self.x-o.x)**2+(self.y-o.y)**2)
class Ride: __init__(self,r,d): self.rider=r; self.driver=d; self.status='searching'
class RideSharing:
    def __init__(self): self.rides={}; self.drivers={}
    def request_ride(self, rid, loc): r=Ride(rid,None); self.rides[rid]=r; return r
    def find_drivers(self, loc, radius=5): return [d for d in self.drivers if loc.distance(d.loc)<=radius]
if __name__ == "__main__": rs=RideSharing(); print("Ride system initialized")