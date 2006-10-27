import math

################################################################################
# Point

class Point(object):
    """Point is a point in 2D. It behaves as a vector, too, because that's
convenient."""

    def __init__(self, x=0, y=0):
        """Constructor: Point(x=0, y=0) -> Point"""
        self.x = float(x)
        self.y = float(y)

    def reset(self,x,y):
        """reset(x,y) -> None. Resets the point to given coordinates."""
        self.x = float(x)
        self.y = float(y)

    def __neg__(self):
        """__neg__() -> Point. Returns a point p such that
        self + p == Point(0,0)"""
        return Point(-self.x,-self.y)

    def __add__(self,other):
        """__add__(other) -> Point. Returns a point p such that
        self + other == p"""
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self,other):
        """__sub__(other) -> Point. Returns a point p such that
        self + other == p"""
        return Point(self.x - other.x, self.y - other.y)

    def __mul__(self,other):
        """__mul__(other) -> Point. Interprets self as a vector and returns
        self * other, where other is a scalar."""
        return Point(self.x * other, self.y * other)

    def __rmul__(self,other):
        """__rmul__(other) -> Point. Interprets self as a vector and returns
        other * self, where other is a scalar."""
        return Point(self.x * other, self.y * other)

    def isInside(self,rect):
        """isInside(other) -> Point. Interprets self as a vector and returns
        other * self, where other is a scalar."""
        return (self.x >= rect.lowerLeft.x and
                self.x <= rect.upperRight.x and
                self.y >= rect.lowerLeft.y and
                self.y <= rect.upperRight.y)
    
    def length(self):
        """length() -> float. Interprets self as a vector and returns the L_2
        length of the vector."""
        return math.sqrt(self.x * self.x + self.y * self.y)

################################################################################
# Unit tests

import unittest
import random

class TestPoint(unittest.TestCase):

    @staticmethod
    def assertDoubleEquals(a, b, eps = 0.00001):
        assert abs(a-b) < eps

    def testAddLength(self):
        """Uses triangle inequality to exercise add and length"""
        for i in range(100):
            x = Point(random.uniform(-1.0, 1.0), random.uniform(-1.0, 1.0))
            y = Point(random.uniform(-1.0, 1.0), random.uniform(-1.0, 1.0))
            assert (x+y).length() <= x.length() + y.length()

    def testMulLength(self):
        """Uses vector space properties to exercise mul, rmul and length"""
        for i in range(100):
            x = Point(random.uniform(-1.0, 1.0), random.uniform(-1.0, 1.0))
            s = random.uniform(0.0, 10.0)
            self.assertDoubleEquals(s * x.length(), (s * x).length())
            self.assertDoubleEquals(s * x.length(), (x * s).length())

if __name__ == '__main__':
    unittest.main()
        
