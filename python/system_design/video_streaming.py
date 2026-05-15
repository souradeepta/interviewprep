class Video: __init__(self, uid, name): self.uid=uid; self.name=name; self.bitrates=[]
class Transcoder:
    def transcode(self, v): v.bitrates=['480p','720p','1080p']; return v.bitrates
class Stream:
    def __init__(self): self.videos={}; self.transcoder=Transcoder()
    def upload(self, uid, name): v=Video(uid,name); self.videos[uid]=v; return v
    def get_quality(self, uid, bw): return '480p' if bw<2 else '1080p' if bw>10 else '720p'
if __name__ == "__main__": s=Stream(); s.upload(1,"Movie"); print(s.get_quality(1,5))