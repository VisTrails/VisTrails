import modules
import modules.module_registry
import modules.basic_modules
from modules.vistrails_module import Module, ModuleError, newModule

import os
import vtk

################################################################################

class Afront(Module):

    def run(self, args):
        cmdline = ("afront -nogui " + (" %s" * len(args)))
        cmdline = cmdline % tuple(args)
        os.system(cmdline)
        
    def compute(self):
        o = self.interpreter.filePool.createFile()
        args = []
        if not self.hasInputFromPort("file"):
            raise ModuleError("Needs input file")
        args.append(self.getInputFromPort("file").name)
        if self.hasInputFromPort("rho"):
            args.append("-rho")
            args.append(self.getInputFromPort("rho"))
        if self.hasInputFromPort("eta"):
            args.append("-eta")
            args.append(self.getInputFromPort("eta"))
        args.append("-outname")
        args.append(o.name)
        args.append("-tri")
        self.run(args)
        self.setResult("output", o)

# class HHM_File_to_VTK(Module):

#     def compute(self):
        

################################################################################

def initialize(*args, **keywords):

    print "Afront VisTrails package"
    print "------------------------"
    print "Testing afront presence..."

    result = os.system("afront >/dev/null 2>&1")
    if result != 0:
        raise Exception("afront does not seem to be present.")
    print "Ok, found afront"
    __version__ = 0.9
    
    reg = modules.module_registry
    reg.addModule(Afront)
    reg.addInputPort(Afront, "rho", (modules.basic_modules.Float, 'rho'))
    reg.addInputPort(Afront, "eta", (modules.basic_modules.Float, 'eta'))
    reg.addInputPort(Afront, "file", (modules.basic_modules.File, 'the file to process'))
    reg.addOutputPort(Afront, "output", (modules.basic_modules.File, 'the result'))
    
