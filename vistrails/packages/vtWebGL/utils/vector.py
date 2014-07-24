


class Vector3:

    def __init__(self, _x=0, _y=0, _z=0):
        self.x = _x
        self.y = _y
        self.z = _z

    def setValues(self, x, y, z):
        self.x = _x
        self.y = _y
        self.z = _z

    def sub(self, b):
        ret = Vector3(self.x - b.x, self.y - b.y, self.z - b.z)
        return ret

    def cross(self, b):
        return Vector3( self.y*b.z - self.z*b.y,
                       -self.x*b.z + self.z*b.x,
                        self.x*b.y - self.y*b.x)

    def dot(self, b):
        return self.x*b.x + self.y*b.y + self.z*b.z

    def copy(self):
        return Vector3(self.x, self.y, self.z)

# OVERLOADS

    def __getitem__(self, pos):            # Bracket Get
        if (pos == 0): return self.x
        if (pos == 1): return self.y
        if (pos == 2): return self.z

    def __setitem__(self, pos, value):     # Bracket Set
        l = [self.x, self.y, self.z]
        l[pos] = value
        self.x, self.y, self.z = l

    def __eq__(self, b):                   # ==
        if (not isinstance(b, Vector3)): return False
        return self.x==b.x and self.y==b.y and self.z==b.z

    def __repr__(self):						    # To Str
        return '[%.2f, %.2f, %.2f]' % (self.x, self.y, self.z)

# http://docs.python.org/library/operator.html
