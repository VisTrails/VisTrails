############################################################################
##
## Copyright (C) 2006-2007 University of Utah. All rights reserved.
##
## This file is part of VisTrails.
##
## This file may be used under the terms of the GNU General Public
## License version 2.0 as published by the Free Software Foundation
## and appearing in the file LICENSE.GPL included in the packaging of
## this file.  Please review the following to ensure GNU General Public
## Licensing requirements will be met:
## http://www.opensource.org/licenses/gpl-license.php
##
## If you are unsure which license is appropriate for your use (for
## instance, you are interested in developing a commercial derivative
## of VisTrails), please contact us at vistrails@sci.utah.edu.
##
## This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
## WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
##
############################################################################

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
