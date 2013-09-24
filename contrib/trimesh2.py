# VisTrails package for trimesh2 support
# Copyright Carlos Eduardo Scheidegger, 2007
# Get trimesh2 at www.cs.princeton.edu/gfx/proj/trimesh2/
#  or a patched version with more available file formats
# at www.sci.utah.edu/~cscheid/software

# License: GPLv2 or later

# ChangeLog:

# 2007-03-13  Carlos Scheidegger  <cscheid@juggernaut>
# 	* uses core.system.list2cmd to generate command lines.
# 2007-03-12  Carlos Scheidegger  <cscheid@juggernaut>
# 	* First release
##############################################################################

import core.modules
import core.modules.module_registry
from core.modules.vistrails_module import Module, ModuleError
from core.system import list2cmdline
import os

_mesh_filter_path = None

identifier = 'edu.utah.sci.cscheid.trimesh2'
version = '0.1'
name = 'trimesh2'

##############################################################################
# MeshFilter
class MeshFilter(Module):

    def guess_input_format(self, input_file_name):
        i = input_file_name.rfind('.')
        if i == -1:
            return None
        else:
            return input_file_name[i:]

    def compute(self):
        self.checkInputPort('input_file')
        input_file = self.get_input('input_file')
        if self.has_input('output_format'):
            output_suffix = self.get_input('output_format')
        else:
            output_suffix = self.guess_input_format(input_file.name)
        if not output_suffix:
            output_suffix = '.off'
        output_file = self.interpreter.filePool.create_file(suffix=output_suffix)
        values = [_mesh_filter_path,
                  input_file.name,
                  output_file.name]
        cmdline = list2cmdline(values)
        print cmdline
        result = os.system(cmdline)
        if result != 0:
            raise ModuleError(self, 'Execution failed')
        self.set_output('output_file', output_file)

##############################################################################
# PlanarSubdiv
class PlanarSubdiv(MeshFilter):

    def compute(self):
        self.checkInputPort('input_file')
        self.checkInputPort('iterations')
        iters = self.get_input('iterations')
        if iters < 1:
            raise ModuleError(self, 'iterations must be >=1')
        input_file = self.get_input('input_file')
        if self.has_input('output_format'):
            output_suffix = self.get_input('output_format')
        else:
            output_suffix = self.guess_input_format(input_file.name)
        if not output_suffix:
            output_suffix = '.off'
        output_file = self.interpreter.filePool.create_file(suffix=output_suffix)

        values = [_mesh_filter_path,
                  input_file.name,
                  '-subdiv',
                  output_file.name]
        cmdline = list2cmdline(values)
        print cmdline
        result = os.system(cmdline)
        if result != 0:
            raise ModuleError(self, 'Execution failed')

        for i in xrange(iters-1):
            cmdline = '%s %s -subdiv %s'  % (_mesh_filter_path,
                                             output_file.name,
                                             output_file.name)
            print cmdline
            result = os.system(cmdline)
            if result != 0:
                raise ModuleError(self, 'Execution failed')
            
        self.set_output('output_file', output_file)
    

def initialize(executable_path=None):
    global _mesh_filter_path
    if not executable_path:
        print "Assuming mesh_filter is in path"
        _mesh_filter_path = 'mesh_filter'
    else:
        print "Assuming mesh_filter is in '%s'" % executable_path
        _mesh_filter_path = executable_path + '/mesh_filter'

    reg = core.modules.module_registry

    reg.add_module(MeshFilter)

    reg.add_input_port(MeshFilter, 'input_file',
                       core.modules.basic_modules.File)
    reg.add_input_port(MeshFilter, 'output_format',
                       core.modules.basic_modules.String)
    reg.add_output_port(MeshFilter, 'output_file',
                        core.modules.basic_modules.File)

    reg.add_module(PlanarSubdiv)
    reg.add_input_port(PlanarSubdiv, 'iterations',
                       core.modules.basic_modules.Integer)
