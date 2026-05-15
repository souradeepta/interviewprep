class Shard: __init__(self): self.data={}
class ShardManager:
    def __init__(self, n): self.shards=[Shard() for _ in range(n)]; self.n=n
    def get_shard(self, k): return self.shards[hash(k)%self.n]
    def put(self, k, v): self.get_shard(k).data[k]=v
    def get(self, k): return self.get_shard(k).data.get(k)
if __name__ == "__main__": m=ShardManager(3); m.put("x",1); print(m.get("x"))