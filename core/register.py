class Register(set):
    def __call__(self, method):
        self.add(method)
        return method
        