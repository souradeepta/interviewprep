class NewsFeeder:
    def __init__(self): self.posts = {}; self.followers = {}; self.feeds = {}
    def post(self, user, content): self.posts[user] = content; self._fanout(user, content)
    def _fanout(self, u, c): 
        for f in self.followers.get(u, []): 
            self.feeds.setdefault(f, []).insert(0, (u, c))
    def follow(self, u, target): self.followers.setdefault(target, []).append(u)
    def get_feed(self, u): return self.feeds.get(u, [])[:10]
if __name__ == "__main__":
    f = NewsFeeder(); f.follow(1,2); f.post(2,"Hello"); print(f.get_feed(1))