import core.modules
import core.modules.module_registry
from core.modules.vistrails_module import Module, ModuleError

from paraview import servermanager
import paraview.simple as pv

def extract_pv_instances(paramList):
    newList = []
    for param in paramList:
        if hasattr(param, "pvInstance"):
            newList.append(param.pvInstance)
        else:
            newList.append(param)
    return newList

class PVModule(Module):
    def __init__(self):
        Module.__init__(self)
        self.pvInstance = None

    def compute(self):
        if self.pvInstance:
            del self.pvInstance
        pv.SetActiveSource(None)
        if not self.pvInstance:
            if hasattr(self, "pvFunction"):
                self.pvInstance = self.pvFunction()
            else:
                self.pvInstance = getattr(pv, self.pvClass)()

        # We need to set input before other properties
        if self.inputPorts.has_key('Input'):
            inp = extract_pv_instances(self.forceGetInputListFromPort('Input'))[0]
            setattr(self.pvInstance, "Input", inp)

        for (function, connector_list) in self.inputPorts.iteritems():
            paramList = extract_pv_instances(self.forceGetInputListFromPort(function))
            if function != 'Input':
                if len(paramList) > 1:
                    setattr(self.pvInstance, function, paramList)
                else:
                    setattr(self.pvInstance, function, paramList[0])

        if hasattr(self.pvInstance, 'UpdatePipeline'):
            self.pvInstance.UpdatePipeline()

        self.setResult('Output', self)

class _funcs_internals:
    "Internal class."
    rep_counter = 0

