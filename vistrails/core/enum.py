"""enum helps create enumeration classes.

TODO: Unit tests."""

def enum(className, enumValues, doc = None):
    """enum(className: str, enumValues: [str], doc = None) -> class.
    Creates a new enumeration class. For example:

    >>> import enum
    >>> Colors = enum.enum('Colors',
                           ['Red', 'Green', 'Blue'],
                           "Enumeration of primary colors")

    will create a class that can be used as follows:

    >>> x = Colors.Red
    >>> y = Colors.Blue
    >>> x == y
    False
    >>> z = Colors.REd
    Traceback (most recent call last):
      File "<stdin>", line 1, in ?
    AttributeError: type object 'Colors' has no attribute 'REd'
    >>> z = Colors.Red
    >>> z == x
    True
    >>> x.__doc__
    'Enumeration of primary colors'
    """
                           
    def __init__(self, v):
        self.__v = v
        
    def str(v):
        return theEnum.st[v]
    
    def __str__(self):
        return theEnum.str(self.__v)
    
    def __repr__(self):
        return className + "." + theEnum.str(self.__v)
    
    def __eq__(self, other):
        try:
            return self.__v == other.__v and self.__className == other.__className
        except AttributeError:
            return False
        
    theEnum = type(className, (object, ),
                   {'__init__': __init__,
                    'str': staticmethod(str),
                    '__str__': __str__,
                    '__repr__': __repr__,
                    'st': enumValues,
                    '__className': className,
                    '__eq__': __eq__,
                    '__doc__': doc})
    for (v, x) in zip(enumValues, range(len(enumValues))):
        setattr(theEnum, v, theEnum(x))
    return theEnum

################################################################################

import unittest

class TestEnum(unittest.TestCase):

    def test1(self):
        e1 = enum('e1', ['v1', 'v2', 'v3'])
        self.assertEquals(e1.v1, e1.v1)
        self.assertEquals(e1.v2, e1.v2)
        self.assertEquals(e1.v3, e1.v3)
        self.assertNotEquals(e1.v1, e1.v2)
        self.assertNotEquals(e1.v1, e1.v3)
        self.assertNotEquals(e1.v2, e1.v3)
        self.assertNotEquals(e1.v2, e1.v1)
        self.assertNotEquals(e1.v3, e1.v1)
        self.assertNotEquals(e1.v3, e1.v2)

    def test2(self):
        e1 = enum('e1', ['v1', 'v2', 'v3'])
        e2 = enum('e1', ['v1', 'v2', 'v3'])
        self.assertEquals(e1.v1, e2.v1)

    def test3(self):
        e1 = enum('e1', ['v1', 'v2', 'v3'])
        self.assertNotEquals(e1.v1, 5)

if __name__ == '__main__':
    unittest.main()
