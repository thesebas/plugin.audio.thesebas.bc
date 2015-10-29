__author__ = 'thesebas'


class Memoize:
    def __init__(self, func):
        self.func = func
        self.cache = {}

    def __call__(self, *args):
        if repr(args) not in self.cache:
            # print "MEMOIZE:(%s) real" % (self.func.func_name,)
            self.cache[repr(args)] = self.func(*args)
        else:
            # print "MEMOIZE(%s) from cache" % (self.func.func_name,)
            pass

        return self.cache[repr(args)]
