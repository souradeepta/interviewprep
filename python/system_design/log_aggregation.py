class LogEntry: __init__(self, host, msg): self.host=host; self.msg=msg
class LogAggregator:
    def __init__(self): self.logs=[]
    def collect(self, host, msg): self.logs.append(LogEntry(host, msg))
    def search(self, q): return [l for l in self.logs if q in l.msg]
if __name__ == "__main__": la=LogAggregator(); la.collect("host1","error x"); print(len(la.search("error")))