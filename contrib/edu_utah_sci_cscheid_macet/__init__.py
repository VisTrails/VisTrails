# VisTrails Macet package

# Macet is an isosurface triangle mesh generator that consistently
# generates good-triangle quality.

# Macet is described in

# Carlos Dietrich, Joao Comba, Luciana Nedel, Carlos Scheidegger, John
# Schreiner, Claudio Silva. Edge Transformations for Improving Mesh
# Quality of Marching Cubes. 2007, submitted.

# This package was created by Carlos Eduardo Scheidegger, 2007
# cscheid@sci.utah.edu. This is GPL v2 or later, your choice.

##############################################################################

import core.modules
import core.modules.module_registry
from core.modules.vistrails_module import Module, ModuleError
from core.system import list2cmdline

# This accomodates two different VisTrails versions: the released one,
# and the one in development


try:
    from core.configuration import ConfigurationObject
    global configuration
    configuration = ConfigurationObject(executable_path=(None, str))
    old_vistrails = False
except ImportError:
    old_vistrails = True

import os

identifier = 'edu.utah.sci.cscheid.macet'
version = '0.1.0'
name = 'Macet'

##############################################################################

def get_path():
    global _macet_path
    if old_vistrails:
        return _macet_path
    if configuration.has('executable_path'):
        p = configuration.executable_path + '/'
    else:
        p = ''
    p += 'macet'
    return p

class Macet(Module):

    def compute(self):
        self.checkInputPort('input_file')
        self.checkInputPort('iso_value')
        
        input_file = self.get_input('input_file')
        output_file = self.interpreter.filePool.create_file(suffix='.off')

        iso_value = self.get_input('iso_value')

        values = [get_path(), input_file.name,
                  str(iso_value), output_file.name, '-isCombined']
        cmdline = list2cmdline(values)
        print cmdline
        result = os.system(cmdline)
        if result != 0:
            raise ModuleError(self, 'Execution failed')

        self.set_output('output_file', output_file)

class MarchingCubes(Module):

    def compute(self):
        self.checkInputPort('input_file')
        self.checkInputPort('iso_value')
        
        input_file = self.get_input('input_file')
        output_file = self.interpreter.filePool.create_file(suffix='.off')

        iso_value = self.get_input('iso_value')

        values = [get_path(), input_file.name,
                  str(iso_value), output_file.name]
        cmdline = list2cmdline(values)
        print cmdline
        result = os.system(cmdline)
        if result != 0:
            raise ModuleError(self, 'Execution failed')

        self.set_output('output_file', output_file)

##############################################################################

def initialize(executable_path=None):

    if old_vistrails:
        global _macet_path
        if executable_path:
            _macet_path = executable_path + '/macet'
        else:
            _macet_path = 'macet'

    reg = core.modules.module_registry

    reg.add_module(Macet)

    reg.add_input_port(Macet, 'input_file',
                       core.modules.basic_modules.File)
    reg.add_input_port(Macet, 'iso_value',
                       core.modules.basic_modules.Float)
    reg.add_output_port(Macet, 'output_file',
                        core.modules.basic_modules.File)

    reg.add_module(MarchingCubes)

    reg.add_input_port(MarchingCubes, 'input_file',
                       core.modules.basic_modules.File)
    reg.add_input_port(MarchingCubes, 'iso_value',
                       core.modules.basic_modules.Float)
    reg.add_output_port(MarchingCubes, 'output_file',
                        core.modules.basic_modules.File)

