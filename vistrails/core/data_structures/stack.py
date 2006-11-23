"""Simple stack data structure."""

###############################################################################

class EmptyStack(Exception):
    pass


class Stack(object):

    def __init__(self):
        object.__init__(self)
        self.__cell = []
        self.__size = 0

    def top(self):
        """Returns the top of the stack."""
        if not self.__cell:
            raise EmptyStack()
        else:
            return self.__cell[0]

    def push(self, obj):
        """Pushes an element onto the stack."""
        self.__cell = [obj, self.__cell]
        self.__size += 1

    def pop(self):
        """Pops the top off of the stack."""
        if not self.__cell:
            raise EmptyStack()
        else:
            self.__cell = self.__cell[1]
            self.__size -= 1

    def __len__(self):
        return self.__size

    def __get_size(self):
        return self.__size

    size = property(__get_size, doc="The size of the stack.")

###############################################################################

import unittest

class TestStack(unittest.TestCase):

    def testBasic(self):
        s = Stack()
        self.assertEquals(s.size, 0)
        s.push(10)
        self.assertEquals(s.top(), 10)
        self.assertEquals(len(s), 1)
        s.pop()
        self.assertEquals(len(s), 0)
        self.assertEquals(0, s.size)

    def testPopEmptyRaises(self):
        s = Stack()
        self.assertRaises(EmptyStack, s.pop)

    def testTopEmptyRaises(self):
        s = Stack()
        self.assertRaises(EmptyStack, s.top)

if __name__ == '__main__':
    unittest.main()
