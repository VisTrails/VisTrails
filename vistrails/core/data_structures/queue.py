
################################################################################

class Queue(object):

    def __init__(self, capacity=8):
        """ Queue(capacity: int) -> Queue
        Initialize the queue with a default capacity of zero in size

        """
        self.__buffer = [None] * capacity
        self.__capacity = capacity
        self.__size = 0
        self.__begin = 0
        self.__end = 0
        
    def __len__(self):
        """ __len__() -> int
        Compute the number of elements when using the built-in len()
        and return an int

        """
        l = self.__end - self.__begin
        if l < 0:
            return self.__capacity - l
        else:
            return l
        
    def front(self):
        """ front() -> element type
        Get the front of the queue and return an element type

        """
        return self.__buffer[self.__begin]
    
    def back(self):
        """ back() -> element type
        Get the back (last) element of the queue and return an element type

        """
        return self.__buffer[(self.__end + self.__capacity - 1) %
                             self.__capacity]
    
    def push(self, obj):
        """ push(obj: element type) -> None
        Push obj onto the back queue and return nothing

        """
        if (self.__end + 1) % self.__capacity == self.__begin:
            self.__rebuffer(self.__capacity * 2)
        self.__buffer[self.__end] = obj
        self.__end += 1
        if self.__end == self.__capacity:
            self.__end = 0
            
    def pop(self):
        """ pop() -> element type
        Pop the front element of the queue and return an element type

        """
        r = self.__buffer[self.__begin]
        self.__buffer[self.__begin] = None
        self.__begin += 1
        if self.__begin == self.__capacity:
            self.__begin = 0
        if self.__capacity > 8 and (self.__capacity / len(self)) >= 4:
            self.__rebuffer(self.__capacity / 2)
        return r

    def __rebuffer(self, newcapacity):
        """ __rebuffer(newcapacity: int) -> none
        Reallocate the internal buffer to fit at newcapacity elements and
        return nothing

        """
        nb = [None] * newcapacity
        if self.__begin < self.__end:
            l = self.__end - self.__begin
            nb[0:l] = self.__buffer[self.__begin:self.__end]
            self.__begin = 0
            self.__end = l
        else:
            l1 = self.__capacity - self.__begin
            l2 = l1 + self.__end
            nb[0:l1] = self.__buffer[self.__begin:]
            nb[l1:l2] = self.__buffer[:self.__end]
            self.__begin = 0
            self.__end = l2
        self.__buffer = nb
        self.__capacity = newcapacity
        
    def __str__(self):
        """ __str__() -> str
        Format the queue for serialization and return a string

        """
        return str(self.__buffer)

################################################################################

import unittest
import random

class TestQueue(unittest.TestCase):
    
    def testBasic(self):
        """Test push/pop operations"""
        q = Queue()
        q.push(1)
        q.push(2)
        q.push(3)
        q.push(4)
        self.assertEquals(q.pop(), 1)
        self.assertEquals(q.pop(), 2)
        self.assertEquals(q.pop(), 3)
        self.assertEquals(q.pop(), 4)
        
    def testExpandBasic(self):
        """Test if the queue is expanding its capacity right with push()"""
        q = Queue()
        for i in range(12):
            q.push(i)
        self.assertEquals(len(q), 12)
        for i in range(12):
            self.assertEquals(q.pop(), i)
            
    def testExpandContract(self):
        """Test if the queue is expanding and contracting with push()/pop()"""
        pushed = 0
        popped = 0
        q = Queue()
        for t in xrange(100):
            for i in range(100):
                # Test expand with high probability
                a = random.choice([0,0,0,0,0,1])
                if (a == 0) or (len(q) == 0):
                    q.push(pushed)
                    pushed += 1
                else:
                    v = q.pop()
                    self.assertEquals(v, popped)
                    popped += 1
            for i in range(100):
                # Test contract with high probability
                a = random.choice([1,1,1,1,1,0])
                if (a == 0) or (len(q) == 0):
                    q.push(pushed)
                    pushed += 1
                else:
                    v = q.pop()
                    self.assertEquals(v, popped)
                    popped += 1

if __name__ == '__main__':
    unittest.main()
