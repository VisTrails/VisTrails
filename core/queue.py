class Queue(object):
    class EmptyQueue(Exception):
        pass
    def __init__(self, capacity=8):
        self.__buffer = [None] * capacity
        self.__capacity = capacity
        self.__size = 0
        self.__begin = 0
        self.__end = 0
    def __len__(self):
        l = self.__end - self.__begin
        if l < 0:
            return self.__capacity - l
        else:
            return l
    def front(self):
        return self.__buffer[self.__begin]
    def back(self):
        return self.__buffer[(self.__end + self.__capacity - 1) % self.__capacity]
    def push(self, obj):
        if (self.__end + 1) % self.__capacity == self.__begin:
            self.__rebuffer(self.__capacity * 2)
        self.__buffer[self.__end] = obj
        self.__end += 1
        if self.__end == self.__capacity:
            self.__end = 0
    def pop(self):
        r = self.__buffer[self.__begin]
        self.__buffer[self.__begin] = None
        self.__begin += 1
        if self.__begin == self.__capacity:
            self.__begin = 0
        if self.__capacity > 8 and (self.__capacity / len(self)) >= 4:
            self.__rebuffer(self.__capacity / 2)
        return r

    def __rebuffer(self, newcapacity):
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
        return str(self.__buffer)

################################################################################

import unittest

class TestQueue(unittest.TestCase):
    def testBasic(self):
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
        q = Queue()
        for i in range(12):
            q.push(i)
        self.assertEquals(len(q), 12)
        for i in range(12):
            self.assertEquals(q.pop(), i)
    def testExpandContract(self):
        import random
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
