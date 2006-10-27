import copy
from point import Point

################################################################################
# Rect

class Rect(object):
    def __init__(self, lowerLeft=None, upperRight=None):
        """Rect(Point, Point). Creates a Rect given the lowerLeft and
        the upperRight points. It creates a copy of the given points."""
        
        if lowerLeft == None:
            self.lowerLeft = Point()
        else:
            self.lowerLeft = copy.copy(lowerLeft)

        if upperRight == None:
            self.upperRight = Point()
        else:
            self.upperRight = copy.copy(upperRight)
        self.checkExtent()

    @staticmethod
    def create(left, right, down, up):
        """create(left, right, down, up) -> Point. Creates a Rect from four
        float extents."""
        return Rect(Point(min(left, right),
                          min(up, down)),
                    Point(max(left, right),
                          max(down, up)))
    
    def setLeft(self, x):
        """self.setLeft(x) -> None. Sets the left limit of the Rect."""
        self.lowerLeft.x = x

    def setRight(self, x):
        """self.setLeft(x) -> None. Sets the right limit of the Rect."""
        self.upperRight.x = x

    def setUp(self,y):
        """self.setLeft(x) -> None. Sets the upper limit of the Rect."""
        self.upperRight.y = y

    def setDown(self, y):
        """self.setLeft(x) -> None. Sets the lower limit of the Rect."""
        self.lowerLeft.y = y

    def center(self):
        """self.center() -> Point. Returns the center of the Rect."""
        return (self.upperRight + self.lowerLeft) * 0.5

    def checkExtent(self):
        """self.checkExtent() -> None. Makes sure left limit is less than right
        limit, and lower limit is less than upper limit. In other words, ensures
        that, immediately after the call, self.lowerLeft.x <= self.upperRight.x
        and self.lowerLeft.y <= self.upperRight.y"""
        if self.lowerLeft.x > self.upperRight.x:
            dlx = self.lowerLeft.x
            self.lowerLeft.x = self.upperRight.x
            self.upperRight.y = dlx

        if self.lowerLeft.y > self.upperRight.y:
            dly = self.lowerLeft.y
            self.lowerLeft.y = self.upperRight.y
            self.upperRight.y = dly

################################################################################
# Unit tests

import unittest
import random

class TestRect(unittest.TestCase):

    def testCreate(self):
        """Exercises Rect.create()"""
        for i in range(100):
            a = random.uniform(-1.0, 1.0)
            b = random.uniform(-1.0, 1.0)
            c = random.uniform(-1.0, 1.0)
            d = random.uniform(-1.0, 1.0)

            r = Rect.create(a, b, c, d)
            assert r.lowerLeft.x == min(a, b)
            assert r.upperRight.x == max(a, b)
            assert r.lowerLeft.y == min(c, d)
            assert r.upperRight.y == max(c, d)

if __name__ == '__main__':
    unittest.main()
