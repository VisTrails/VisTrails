from modules.vistrails_module import Module
from modules.basic_modules import Tuple
from modules.module_registry import registry
import vtk
import __builtin__

class vtkBaseModule(Module):

    def __init__(self):
        Module.__init__(self)
        self.vtkInstance = None

    def compute(self):
        if self.vtkInstance:
            del self.vtkInstance
        self.vtkInstance = self.vtkClass()
        for function in self.inputPorts.keys():
            paramList = self.forceGetInputListFromPort(function)
            if function[:18]=='SetInputConnection':
                paramList = zip([int(function[18:])]*len(paramList),
                                 paramList)
                function = 'SetInputConnection'
            for p in paramList:
                if type(p)==__builtin__.tuple:
                    param = list(p)
                elif p==None: param = []
                else: param = [p]
                for i in range(len(param)):
                    if hasattr(param[i], 'vtkInstance'):
                        param[i] = param[i].vtkInstance
                getattr(self.vtkInstance, function)(*param)
                
        for function in self.outputPorts.keys():
            if function[:13]=='GetOutputPort':
                i = int(function[13:])
                self.setResult(function,
                               vtkBaseModule.wrapperModule('vtkAlgorithmOutput',
                                                           self.vtkInstance.GetOutputPort(i)))
            elif hasattr(self.vtkInstance, function):
                retValues = getattr(self.vtkInstance, function)()
                if issubclass(retValues.__class__, vtk.vtkObject):
                    self.setResult(function,
                                   vtkBaseModule.wrapperModule(retValues.GetClassName(),
                                                               retValues))
                elif (type(retValues)==__builtin__.tuple or
                      type(retValues)==__builtin__.list):
                    result = list(retValues)
                    for i in range(len(result)):
                        if issubclass(result[i].__class__, vtk.vtkObject):
                            result[i] = vtkBaseModule.wrapperModule(result[i].GetClassName(),
                                                                    result[i])
                    self.setResult(function, type(retValues)(result))
                else:
                    self.setResult(function, retValues)
            elif function!='self':
                print 'Unknown output port %s from' % function, self.vtkClass

    @staticmethod
    def wrapperModule(classname, instance):
        result = registry.getDescriptorByName(classname).module()
        result.vtkInstance = instance
        return result
