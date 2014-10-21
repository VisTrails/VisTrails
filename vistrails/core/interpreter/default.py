###############################################################################
##
## Copyright (C) 2011-2014, NYU-Poly.
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
import vistrails.core.interpreter.cached
import vistrails.core.interpreter.noncached

import unittest

cached_interpreter = vistrails.core.interpreter.cached.CachedInterpreter
noncached_interpreter = vistrails.core.interpreter.noncached.Interpreter
__default_interpreter = cached_interpreter

##############################################################################

def set_cache_configuration(field, value):
    assert field == 'cache'
    if value:
        set_default_interpreter(cached_interpreter)
    else:
        set_default_interpreter(noncached_interpreter)

def connect_to_configuration(configuration):
    configuration.subscribe('cache', set_cache_configuration)

def get_default_interpreter():
    """Returns an instance of the default interpreter class."""
    return __default_interpreter.get()

def set_default_interpreter(interpreter_class):
    """Sets the default interpreter class."""
    global __default_interpreter
    __default_interpreter = interpreter_class

##############################################################################


class TestDefaultInterpreter(unittest.TestCase):

    def test_set(self):
        old_interpreter = type(get_default_interpreter())
        try:
            set_default_interpreter(noncached_interpreter)
            self.assertEquals(type(get_default_interpreter()),
                              noncached_interpreter)
            set_default_interpreter(cached_interpreter)
            self.assertEquals(type(get_default_interpreter()),
                              cached_interpreter)
        finally:
            set_default_interpreter(old_interpreter)
            self.assertEquals(type(get_default_interpreter()),
                              old_interpreter)
