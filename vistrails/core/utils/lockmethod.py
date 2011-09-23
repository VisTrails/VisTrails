###############################################################################
##
## Copyright (C) 2006-2011, University of Utah. 
## All rights reserved.
## Contact: contact@vistrails.org
##
## This file is part of VisTrails.
##
## "Redistribution and use in source and binary forms, with or without 
## modification, are permitted provided that the following conditions are met:
##
##  - Redistributions of source code must retain the above copyright notice, 
##    this list of conditions and the following disclaimer.
##  - Redistributions in binary form must reproduce the above copyright 
##    notice, this list of conditions and the following disclaimer in the 
##    documentation and/or other materials provided with the distribution.
##  - Neither the name of the University of Utah nor the names of its 
##    contributors may be used to endorse or promote products derived from 
##    this software without specific prior written permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
## AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, 
## THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR 
## PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR 
## CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, 
## EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, 
## PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; 
## OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, 
## WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR 
## OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF 
## ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
##
###############################################################################
def lock_method(lock):
    
    def decorator(method):
        def decorated(self, *args, **kwargs):
            try:
                lock.acquire()
                result = method(self, *args, **kwargs)
            finally:
                lock.release()
            return result
        decorated.func_doc = method.__doc__
        return decorated

    return decorator

##############################################################################

import unittest
import threading

class TestLockMethod(unittest.TestCase):

    lock = threading.Lock()
    @lock_method(lock)
    def foo(self):
        self.assertEquals(self.lock.locked(), True)

    @lock_method(lock)
    def foo_throws(self):
        raise Exception()

    @lock_method(lock)
    def foo_finally(self):
        try:
            raise Exception
            return False
        finally:
            return True

    @lock_method(lock)
    def foo_docstring(self):
        """FOO"""
        pass

    def test_common(self):
        self.assertEquals(self.lock.locked(), False)
        self.foo()
        self.assertEquals(self.lock.locked(), False)

    def test_throws(self):
        self.assertEquals(self.lock.locked(), False)
        self.assertRaises(Exception, self.foo_throws)
        self.assertEquals(self.lock.locked(), False)

    def test_finally(self):
        self.assertEquals(self.lock.locked(), False)
        self.assertEquals(self.foo_finally(), True)
        self.assertEquals(self.lock.locked(), False)

    def test_docstring(self):
        self.assertEquals(self.foo_docstring.__doc__, "FOO")
        

if __name__ == '__main__':
    unittest.main()
