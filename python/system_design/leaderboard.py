from collections import defaultdict
class Leaderboard:
    def __init__(self): self.scores={}
    def update(self, u, pts): self.scores[u]=self.scores.get(u,0)+pts
    def get_top(self, k=10): return sorted(self.scores.items(), key=lambda x: -x[1])[:k]
    def get_rank(self, u): ranked=self.get_top(len(self.scores)); return next((i for i,(uid,_) in enumerate(ranked) if uid==u), -1)+1
if __name__ == "__main__": lb=Leaderboard(); lb.update(1,100); lb.update(2,50); print(lb.get_top())