class Bidict(dict):
    """Subclass of mapping that automatically keeps track of the
inverse mapping. Note: self.inverse is a simple dict, so it won't keep
track of deletions directly to self.inverse and things like that. Use
this for lookups ONLY!"""

    def __init__(self, *args, **kwargs):

        dict.__init__(self, *args, **kwargs)
        self.inverse = {}
        for (k, v) in self.iteritems():
            self.inverse[v] = k

    def __setitem__(self, key, value):
        dict.__setitem__(self, key, value)
        self.inverse[value] = key

    def __delitem__(self, key):
        v = self[key]
        dict.__delitem__(self, key)
        del self.inverse[v]

##############################################################################

import unittest

class TestBidict(unittest.TestCase):

    def test1(self):
        x = Bidict()
        for i in range(10):
            x[i] = 9-i
        for i in range(10):
            self.assertEquals(x[i], 9-i)
            self.assertEquals(x.inverse[i], 9-i)
        del x[1]
        self.assertRaises(KeyError, x.__getitem__, 1)
        self.assertRaises(KeyError, x.inverse.__getitem__, 8)
        
if __name__ == '__main__':
    unittest.main()
