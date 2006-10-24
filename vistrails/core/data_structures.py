import math
import copy

class Point(object):
    """Point is a simple class that stores a point in 2D space."""
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
        return Rect(Point(left,down),Point(right,up))
    
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
