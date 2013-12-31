

class ResponseSet(object):

    def __getitem__(self, x):
        if isinstance(x, int):
            print x
        elif isinstance(x, slice):
            print x.start, x.stop
