class SagaStep: __init__(self, action, comp): self.action=action; self.compensation=comp
class SagaOrchestrator:
    def __init__(self): self.steps=[]; self.executed=[]
    def add_step(self, step): self.steps.append(step)
    def execute(self): 
        for s in self.steps: self.executed.append(s.action)
        return len(self.executed)==len(self.steps)
if __name__ == "__main__": so=SagaOrchestrator(); so.add_step(SagaStep("debit", "credit")); print(so.execute())