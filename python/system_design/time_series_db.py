from collections import defaultdict
class TimeSeriesDB:
    def __init__(self): self.data=defaultdict(list)
    def write(self, metric, ts, val): self.data[metric].append((ts, val))
    def query(self, metric, start, end): 
        return [(t,v) for t,v in self.data[metric] if start<=t<=end]
if __name__ == "__main__": ts=TimeSeriesDB(); ts.write("cpu", 1000, 50); print(ts.query("cpu", 0, 2000))