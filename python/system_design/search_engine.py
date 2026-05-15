class InvertedIndex: __init__(self): self.idx={}
    def index(self, did, txt): 
        for w in txt.split(): self.idx.setdefault(w,[]).append(did)
    def search(self, q): return self.idx.get(q, [])
class SearchEngine:
    def __init__(self): self.idx=InvertedIndex(); self.docs={}
    def index_doc(self, did, txt): self.docs[did]=txt; self.idx.index(did, txt)
    def search(self, q): return self.idx.search(q)
if __name__ == "__main__": se=SearchEngine(); se.index_doc(1,"python"); print(se.search("python"))