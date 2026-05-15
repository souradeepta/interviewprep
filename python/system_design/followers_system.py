class SocialGraph:
    def __init__(self): self.followers={}; self.following={}
    def follow(self, u, t): self.followers.setdefault(t,[]).append(u); self.following.setdefault(u,[]).append(t)
    def unfollow(self, u, t): self.followers[t].remove(u); self.following[u].remove(t) if t in self.following[u] else None
    def get_followers(self, u): return self.followers.get(u, [])
    def get_following(self, u): return self.following.get(u, [])
if __name__ == "__main__": sg=SocialGraph(); sg.follow(1,2); print(sg.get_followers(2))