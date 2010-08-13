import core.modules
import core.modules.module_registry
from core.modules.vistrails_module import Module, ModuleError

from paraview import servermanager
import paraview.simple as pv

class PVModule(Module):
    def __init__(self):
        Module.__init__(self)
        self.pvInstance = None
        
    def compute(self):
        if self.pvInstance:
            del self.pvInstance
        print self.pvSpace, self.pvClass
        self.pvInstance = getattr(pv, self.pvClass)()

        for (function, connector_list) in self.inputPorts.iteritems():
            paramList = self.forceGetInputListFromPort(function)
            if function == "Input":
                pv.SetActiveSource(self.getInputFromPort("Input").pvInstance)
                continue
            if len(paramList) > 1:
                self.pvInstance.SetPropertyWithName(function, paramList)
            else:
                self.pvInstance.SetPropertyWithName(function, paramList[0])

        if hasattr(self.pvInstance, 'UpdatePipeline'):
            self.pvInstance.UpdatePipeline()

        self.setResult('Output', self)

class PVRenderable(Module):
    ''' Container for the PVCell '''
    def __init__(self):
        Module.__init__(self)
        self.pvInstance = None
        self.pvLUT = None
        self.pvMode = 'Surface'
    
    def compute(self):
        pass
