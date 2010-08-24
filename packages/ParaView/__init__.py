import paraview
import paraview.simple
import paraview.servermanager as sm
import PVBase
import core.modules
import core.modules.module_registry
from core.modules.vistrails_module import new_module, Module, ModuleError
from core.modules.module_registry import (registry, add_module,
                                          has_input_port,
                                          add_input_port, add_output_port)

version = '0.0.1'
name = 'ParaView'
identifier = 'edu.utah.sci.eranders.ParaView'

def package_dependencies():
    import core.packagemanager
    manager = core.packagemanager.get_package_manager()
    if manager.has_package('edu.utah.sci.vistrails.spreadsheet'):
        return ['edu.utah.sci.vistrails.spreadsheet']
    else:
        return []

def package_requirements():
    import core.requirements
    if not core.requirements.python_module_exists('vtk'):
        raise core.requirements.MissingRequirement('vtk')
    if not core.requirements.python_module_exists('PyQt4'):
        print 'PyQt4 is not available. There will be no interaction',
        print 'between VTK and the spreadsheet.'
    import vtk

forbidden = ['AlltoN',
             'Balance',
             'CTHSurface',
             'SelectionSourceBase']

def add_paraview_module(name, proxy, module_type, hide=False, pvFunction=None):

    mod = new_module(module_type, name)
    ns = get_namespace(name)
    mod.pvSpace = ns.lower()
    mod.pvClass = name
    if pvFunction != None:
        mod.pvFunction = pvFunction
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

def get_namespace(mod_name):
    if sm.sources.__dict__.has_key(mod_name):
        return 'Sources'
    if sm.filters.__dict__.has_key(mod_name):
        return 'Filters'
    if sm.animation.__dict__.has_key(mod_name):
        return 'Animation'
    if sm.writers.__dict__.has_key(mod_name):
        return 'Writers'
    if sm.rendering.__dict__.has_key(mod_name):
        return 'Rendering'
    return ''

def initialize(*args, **keywords):
    reg = core.modules.module_registry
    basic = core.modules.basic_modules
    add_module(PVBase.PVModule, namespace='base')
    mod_dict = {}

    mlist = [sm.sources, sm.filters, sm.animation, sm.writers]
    for m in mlist:
        dt = m.__dict__
        for key in dt.keys():
            if forbidden.__contains__(key):
                continue
            if key.__contains__('Base'):
                continue
            cl = dt[key]
            if not isinstance(cl, str):
                if paraview.simple._func_name_valid(key):
                    add_paraview_module(key, m.__dict__[key](no_update=True), PVBase.PVModule)


    add_paraview_module("GeometryRepresentation", sm.rendering.GeometryRepresentation(no_update=True), PVBase.PVModule, True, sm.rendering.GeometryRepresentation)
    add_paraview_module("PVLookupTable", sm.rendering.PVLookupTable(no_update=True), PVBase.PVModule, False, sm.rendering.PVLookupTable)

    import pvcell
    pvcell.registerSelf()
