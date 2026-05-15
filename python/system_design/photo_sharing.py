class Photo: __init__(self, uid, data): self.uid=uid; self.data=data; self.thumbs=[]
class PhotoService:
    def __init__(self): self.photos={}
    def upload(self, uid, data): p=Photo(uid, data); self.photos[uid]=p; self._gen_thumbs(p); return p
    def _gen_thumbs(self, p): p.thumbs=['small','medium','large']
    def get(self, uid): return self.photos.get(uid)
if __name__ == "__main__": ps=PhotoService(); ps.upload(1,b"data"); print(len(ps.get(1).thumbs))