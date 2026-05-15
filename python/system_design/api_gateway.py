class Service: __init__(self, name): self.name=name
class Route: __init__(self, path, svc): self.path=path; self.service=svc
class APIGateway:
    def __init__(self): self.routes={}
    def register(self, path, svc): self.routes[path]=svc
    def route(self, path, req): return self.routes.get(path, None)
if __name__ == "__main__": gw=APIGateway(); gw.register("/users", Service("user_svc")); print(gw.route("/users", None).name)