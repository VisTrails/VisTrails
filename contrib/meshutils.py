import core.modules
import core.modules.module_registry
from core.modules.vistrails_module import Module, ModuleError
import core.bundles
import core.requirements
import os
import re

identifier = 'edu.utah.sci.cscheid.meshutils'
version = '0.1'
name = 'Mesh utility'

class MeshArea(Module):

    def compute(self):
        self.checkInputPort('input_file')
        f1 = self.get_input('input_file')
        text_output = self.interpreter.filePool.create_file()

        cmdline = []
        cmdline.append(meshareapath)
        cmdline.append(f1.name)
        cmdline.append('>' + text_output.name)
        cmdline = ('%s ' * len(cmdline)) % tuple(cmdline)
        print cmdline
        result = os.system(cmdline)
        if result != 0:
            raise ModuleError(self, "execution failed")
        try:
            l = file(text_output.name).readlines()[-1]
            v = float(l)
        except:
            raise ModuleError(self, "Expected a float, got '%s'" % l)
        self.setResult('area', v)

class MeshChoose(Module):

    def guess_input_format(self, input_file_name):
        i = input_file_name.rfind('.')
        if i == -1:
            return None
        else:
            return input_file_name[i:]

    def compute(self):
        self.checkInputPort('input_file_1')
        self.checkInputPort('input_file_2')

        input_file_1 = self.get_input('input_file_1')
        input_file_2 = self.get_input('input_file_2')

        if self.hasInputFromPort('output_format'):
            output_suffix = self.get_input('output_format')
        else:
            output_suffix = self.guess_input_format(input_file_2.name)

        output_file = self.interpreter.filePool.create_file(output_suffix)

        cmdline = [meshchoosepath,
                   input_file_1.name,
                   input_file_2.name,
                   output_file.name]
        cmdline = ('%s ' * len(cmdline)) % tuple(cmdline)
        print cmdline
        result = os.system(cmdline)
        if result != 0:
            raise ModuleError(self, "execution failed")
        self.setResult('output_file', output_file)

def setpath(prefix):
    global meshareapath
    meshareapath = prefix + 'mesh_area'
    global meshchoosepath
    meshchoosepath = prefix + 'mesh_choose'

def initialize(meshutilspath=None):
    global _mesh_utils_path
    if not meshutilspath:
        print "Assuming mesh_utils are on path"
        setpath('')
    else:
        print "Assuming mesh_utils are in '%s/'" % meshutilspath
        setpath(meshutilspath+'/')
    reg = core.modules.module_registry
    reg.add_module(MeshArea)
    reg.add_input_port(MeshArea, 'input_file',
                     core.modules.basic_modules.File)
    reg.add_output_port(MeshArea, 'area',
                      core.modules.basic_modules.Float)

    reg.add_module(MeshChoose)
    reg.add_input_port(MeshChoose, 'input_file_1',
                     core.modules.basic_modules.File)
    reg.add_input_port(MeshChoose, 'input_file_2',
                     core.modules.basic_modules.File)
    reg.add_input_port(MeshChoose, 'output_format',
                     core.modules.basic_modules.String)

    reg.add_output_port(MeshChoose, 'output_file',
                      core.modules.basic_modules.File)

        
        

