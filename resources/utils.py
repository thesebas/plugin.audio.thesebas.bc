__author__ = 'thesebas'


class Memoize:
    def __init__(self, func):
        self.func = func
        self.cache = {}

    def __call__(self, *args):
        if repr(args) not in self.cache:
            self.cache[args] = self.func(*args)
        return self.cache[args]
