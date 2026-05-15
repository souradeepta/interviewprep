class UserProfile: __init__(self): self.likes=set(); self.follows=set()
class RecommendationEngine:
    def __init__(self): self.profiles={}; self.items=set()
    def like(self, u, i): self.profiles.setdefault(u, UserProfile()).likes.add(i)
    def recommend(self, u): p=self.profiles.get(u); return [i for i in self.items if i not in p.likes][:5] if p else []
if __name__ == "__main__": re=RecommendationEngine(); re.items={1,2,3,4,5}; re.like(1,1); print(re.recommend(1))