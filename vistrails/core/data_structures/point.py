import math

################################################################################
# Point

class Point(object):
    """Point is a point in 2D. It behaves as a vector, too, because that's
convenient."""

    def __init__(self, x=0, y=0):
        """ Point(x: float, y: float) -> Point
        Initialize and return a Point
        
        """
        self.x = float(x)
        self.y = float(y)

    def reset(self,x,y):
        """ reset(x: float, y: float) -> None
        Resets the point to given coordinates and return nothing

        """
        self.x = float(x)
        self.y = float(y)

    def __neg__(self):
        """ __neg__() -> Point
        Compute a point p such that: self + p == Point(0,0), and return a Point
        
        """
        return Point(-self.x,-self.y)

    def __add__(self, other):
        """ __add__(other: Point) -> Point
        Returns a point p such that: self + other == p, and return a Point
        
        """
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        """ __sub__(other: Point) -> Point
        Returns a point p such that: self - other == p, and return a Point

        """
        return Point(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        """ __mul__(other: float) -> Point
        Interprets self as a vector to perform a scalar multiplication and
        return a Point

        """
        return Point(self.x * other, self.y * other)

    def __eq__(self, other):
        """__eq__(other: Point) -> boolean 
        Two points are equal if they have the same components 
        
        """
        if other:
            if self.x == other.x and self.y == other.y:
                return True
            else:
                return False
        else:
            return False
        
    def __ne__(self, other):
        """__ne__(other: Point) -> boolean 
        Two points are differenr if they don't have the same components 
        
        """
        return not self.__eq__(other)

    def __rmul__(self, other):
        """ __rmul__(other: float) -> Point
        Interprets self as a vector to perform a scalar multiplication and
        return a Point

        """
        return Point(self.x * other, self.y * other)

    def isInside(self, rect):
        """ isInside(rect: Rect) -> boolean
        Check if the point is falling inside rect and return a boolean
        
        """
        return (self.x >= rect.lowerLeft.x and
                self.x <= rect.upperRight.x and
                self.y >= rect.lowerLeft.y and
                self.y <= rect.upperRight.y)
    
    def length(self):
        """ length() -> float
        Interprets self as a vector to compute the L_2 norm and return a float

        """
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

    def testComparisonOperators(self):
        """ Test comparison operators """
        a = Point(0, 1)
        b = Point(0, 1)
        assert a == b
        assert a != None
        b = Point(0, 0.1)
        assert a != b

if __name__ == '__main__':
    unittest.main()
        
