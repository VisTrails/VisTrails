import paraview
import paraview.simple
import paraview.servermanager as sm
import PVBase
import core.modules
import core.modules.module_registry
from pvconfig import QPVConfigWindow
from core.modules.vistrails_module import new_module, Module, ModuleError
from core.modules.module_registry import (registry, add_module,
                                          has_input_port,
                                          add_input_port, add_output_port)
from core.modules.source_configure import SourceConfigurationWidget
from core.modules.python_source_configure import PythonEditor, PythonSourceConfigurationWidget
from core.modules.basic_modules import PythonSource
from configuration import configuration
import urllib

forbidden = ['AlltoN',
             'Balance',
             'CTHSurface',
             'SelectionSourceBase']


class ProgrammableFilterConfigurationWidget(SourceConfigurationWidget):
    def __init__(self, module, controller, parent=None):
        SourceConfigurationWidget.__init__(self, module, controller, 
                                           PythonEditor, False, False, parent,
                                           portName='Script', encode=False)

class PVServerPythonSourceConfigurationWidget(SourceConfigurationWidget):
    def __init__(self, module, controller, parent=None):
        SourceConfigurationWidget.__init__(self, module, controller, 
                                           PythonEditor, True, False, parent,
                                           portName='Script', encode=False)

class PVServerPythonSource(PVBase.PVModule):

    def compute(self):
        if self.pvInstance:
            del self.pvInstance
        paraview.simple.SetActiveSource(None)
        inputDefs = ''
        for k in self.inputPorts:
            if k=='Script':
                continue
            value = self.getInputFromPort(k)
            if type(value)==str:
                inputDefs += '%s = "%s"\n' % (k, value.replace('"', '\\"'))
            elif type(value)==int:
                inputDefs += '%s = %s\n' % (k, value)
        prefix = """
import paraview.servermanager as sm
import paraview.vtk.dataset_adapter as DA
proc = sm.vtkProcessModule.GetProcessModule()
nPartitions = proc.GetNumberOfLocalPartitions()
partitionId = proc.GetPartitionId()
result = ''
"""
        source = self.forceGetInputFromPort('Script', '')
        suffix = """
if len(result)>0:
    import vtk
    dataImporter = vtk.vtkImageImport()
    dataImporter.CopyImportVoidPointer(result, len(result))
    dataImporter.SetDataScalarTypeToUnsignedChar()
    dataImporter.SetNumberOfScalarComponents(1)
    dataImporter.SetDataExtent(0, len(result)-1, 0, 0, 0, 0)
    dataImporter.SetWholeExtent(0, len(result)-1, 0, 0, 0, 0)
    dataImporter.Update()
    self.GetOutputDataObject(0).DeepCopy(dataImporter.GetOutput())
"""
        self.pvInstance = paraview.simple.ProgrammableFilter()
        self.pvInstance.OutputDataSetType = 'vtkImageData'
        self.pvInstance.Script = inputDefs + prefix + source + suffix
        self.pvInstance.UpdatePipeline()

        self.setResult('Output', self)


class PVClientFetch(PythonSource):

    def compute(self):
        prefix = """
import paraview.servermanager as sm
import paraview.vtk.dataset_adapter as DA
proc = sm.vtkProcessModule.GetProcessModule()
nPartitions = proc.GetNumberOfPartitions(sm.ActiveConnection.ID)
module = self.getInputFromPort('ServerModule')
results = []
for i in xrange(nPartitions):
    data = sm.Fetch(module.pvInstance, i)
    if data==None or data.GetPointData().GetNumberOfArrays()==0:
        continue
    narray = DA.numpy_support.vtk_to_numpy(data.GetPointData().GetArray(0))
    result = narray.tostring()
    results.append(result)
"""
        s = urllib.unquote(str(self.forceGetInputFromPort('source', '')))
        self.run_code(prefix + s, use_input=True, use_output=True)
        
        
def add_paraview_module(name, proxy, module_type, ns, hide=False, pvFunction=None):

    mod = new_module(module_type, name)
    mod.pvSpace = ns.lower()
    mod.pvClass = name
    if pvFunction != None:
        mod.pvFunction = pvFunction
    if name=='ProgrammableFilter':
        add_module(mod, name = name, namespace=ns, configureWidgetType=ProgrammableFilterConfigurationWidget)
    else:
        add_module(mod, name = name, namespace=ns)

    for prop in proxy.ListProperties():
        optional = False
        if hide and prop != "Input":
            optional = True
        p = proxy.GetProperty(prop)
        if isinstance(p, sm.ProxyProperty):
            add_input_port(mod, prop, PVBase.PVModule, optional)
            continue
        if isinstance(p, sm.EnumerationProperty):
            add_input_port(mod, prop, core.modules.basic_modules.String, optional)
            continue
        if isinstance(p, sm.VectorProperty):
            params = []
            typ = None
            if p.IsA("vtkSMDoubleVectorProperty"):
                typ = core.modules.basic_modules.Float
            elif p.IsA("vtkSMIntVectorProperty"):
                typ = core.modules.basic_modules.Integer
            elif p.IsA("vtkSMStringVectorProperty"):
                typ = core.modules.basic_modules.String
            elif p.IsA("vtkSMIdTypeVectorProperty"):
                typ = core.modules.basic_modules.Integer
            nel = len(p)
            if nel > 0:
                for i in range(nel):
                    params.append(typ)
            else:
                params.append(typ)
            add_input_port(mod, prop, params, optional)

    add_output_port(mod, "Output", module_type)
        
def initialize(*args, **keywords):
    reg = core.modules.module_registry
    basic = core.modules.basic_modules
    add_module(PVBase.PVModule, namespace='base')
    mod_dict = {}

    mlist = [("Sources", sm.sources), ("Filters", sm.filters), 
             ("Animation", sm.animation), ("Writers", sm.writers)]
    for ns, m in mlist:
        dt = m.__dict__
        for key in dt.keys():
            if forbidden.__contains__(key):
                continue
            if key.__contains__('Base'):
                continue
            cl = dt[key]
            if not isinstance(cl, str):
                if paraview.simple._func_name_valid(key):
                    add_paraview_module(key, m.__dict__[key](no_update=True), PVBase.PVModule, ns)


    add_paraview_module("GeometryRepresentation", sm.rendering.GeometryRepresentation(no_update=True), PVBase.PVModule, "Rendering", True, sm.rendering.GeometryRepresentation)
    add_paraview_module("PVLookupTable", sm.rendering.PVLookupTable(no_update=True), PVBase.PVModule, "Rendering", False, sm.rendering.PVLookupTable)
    add_paraview_module("ScalarBarWidgetRepresentation", sm.rendering.ScalarBarWidgetRepresentation(no_update=True), PVBase.PVModule, "Rendering", True, sm.rendering.ScalarBarWidgetRepresentation)
    add_module(PVServerPythonSource, name = "PVServerPythonSource", configureWidgetType=PVServerPythonSourceConfigurationWidget)
    add_input_port(PVServerPythonSource, "Script", (core.modules.basic_modules.String, ""), True)
    add_output_port(PVServerPythonSource, "self", PVServerPythonSource)
    add_module(PVClientFetch, name = "PVClientFetch", configureWidgetType=PythonSourceConfigurationWidget)
    add_input_port(PVClientFetch, "ServerModule", (PVServerPythonSource, ""))
    add_input_port(PVClientFetch, "source", (core.modules.basic_modules.String, ""))

    import pvcell
    pvcell.registerSelf()

    global pvConfigWindow
    pvConfigWindow = QPVConfigWindow(proc_num=configuration.num_proc,
                                     port=configuration.port)
    pvConfigWindow.show()
    if configuration.start_server == True:
        pvConfigWindow.togglePVServer()