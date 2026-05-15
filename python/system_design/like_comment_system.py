class Post: __init__(self, uid, txt): self.uid=uid; self.txt=txt; self.likes=0; self.comments=[]
class LikeCommentSystem:
    def __init__(self): self.posts={}
    def create_post(self, uid, txt): p=Post(uid, txt); self.posts[id(p)]=p; return p
    def like(self, pid): self.posts[pid].likes+=1
    def comment(self, pid, txt): self.posts[pid].comments.append(txt)
if __name__ == "__main__": lcs=LikeCommentSystem(); p=lcs.create_post(1,"Hi"); lcs.like(id(p)); print(p.likes)