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

class vtk_base(object):
    def __init__(self, n=None, *args, **kwargs):
        self._name = n
        self._args = args
        self._kwargs = kwargs
        
    def __call__(self, *args, **kwargs):
        # print 'calling %s __call__ with' % self.__class__.__name__, \
        #     args, kwargs
        return self.__class__.__dict__['_call'](self, self.n, *args, **kwargs)
        
    def __getattr__(self, name):
        # print 'calling %s __getattr__ with' % self.__class__.__name__, name
        if name in ('__str__','__repr__'): 
            return lambda: 'instance of %s at %s' % (str(self.__class__), 
                                                     id(self))
        self.n = name
        return self

    def _call(self, n, *args, **kwargs):
        # print 'calling _call with', n, args, kwargs
        pass

class vtk_function(vtk_base):
    id_count = 0

    def __init__(self, n=None, parent=None, *args, **kwargs):
        vtk_base.__init__(self, n, *args, **kwargs)
        self.parent = parent
        self.sub_functions = []
        self.id = vtk_function.id_count
        vtk_function.id_count += 1

    def _call(self, n, *args, **kwargs):
        vtk_base._call(self, n, *args, **kwargs)
        new_sub_function = vtk_function(n, self, *args, **kwargs)
        self.__dict__['sub_functions'].append(new_sub_function)
        return new_sub_function

class vtk_module(vtk_base):
    def __init__(self, n=None, *args, **kwargs):
        vtk_base.__init__(self, n, *args, **kwargs)
        self.functions = []

    def _call(self, n, *args, **kwargs):
        vtk_base._call(self, n, *args, **kwargs)
        new_function = vtk_function(n, self, *args, **kwargs)
        self.__dict__['functions'].append(new_function)
        return new_function
    
class vtk(vtk_base):

    def __init__(self, n=None, *args, **kwargs):
        vtk_base.__init__(self, n, *args, **kwargs)
        self.modules = []
        # print 'self.__dict__:', self.__dict__

    def _call(self, n, *args, **kwargs):
        vtk_base._call(self, n, *args, **kwargs)
        new_module = vtk_module(n, *args, **kwargs)
        self.__dict__['modules'].append(new_module)
        return new_module

    def to_vt(self, filename):
        from vtk_to_vt import VTK2VT
        my_writer = VTK2VT()
        for module in self.modules:
            my_writer.create_module(module)
        for module in self.modules:
            my_writer.create_functions(module)
        my_writer.print_vt(filename)
