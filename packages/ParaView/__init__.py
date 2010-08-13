import paraview
import paraview.simple
import paraview.servermanager as sm
import PVBase
import core.modules
import core.modules.module_registry
from PyQt4 import QtGui, QtCore
from core.modules.basic_modules import String
from core.modules.constant_configuration import ConstantWidgetMixin
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
        return ['edu.utah.sci.vistrails.spreadsheet', 'edu.utah.sci.vistrails.vtk']
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

mod_list = []
mod_funcs = {}

type_dict = {}
type_dict['int'] = core.modules.basic_modules.Integer
type_dict['long'] = core.modules.basic_modules.Integer
type_dict['str'] = core.modules.basic_modules.String
type_dict['float'] = core.modules.basic_modules.Float
type_dict['list'] = core.modules.basic_modules.List
type_dict['PVModule'] = PVBase.PVModule

def add_paraview_module(m, name):
    mod_funcs[name] = []
    proxy = m.__dict__[name]()
    for prop in proxy.ListProperties():
        if prop == 'Input':
            mod_funcs[name].append(('Input', ['PVModule']))
            continue
        p = proxy.GetProperty(prop)
        if str(type(p)).__contains__('paraview.servermanager.FileNameProperty'):
            mod_funcs[name].append((prop, ['str']))
            continue
        if p.__str__().__contains__('paraview.servermanager'):
            mod_funcs[name].append((prop, ['PVModule']))
            continue
        if not hasattr(p, '__len__'):
            continue
#         if str(type(p)).__contains__('paraview.servermanager.VectorProperty'):
#             mod_funcs[name].append((prop, ['float']))
#             continue
        nel = len(p)
        if nel == 0:
            mod_funcs[name].append((prop, ['float']))
            continue
        typelist = []
        for i in range(nel):
            if p.GetElement(i) == None:
                typelist.append('float')
            else:
                typelist.append(str(type(p.GetElement(i))).split('\'')[1])
        mod_funcs[name].append((prop, typelist))
    
def translate_types(py_types):
    basic = core.modules.basic_modules
    vt_types = None
    vt_types = type_dict[py_types]
    return vt_types        

def get_namespace(mod_name):
    if sm.sources.__dict__.has_key(mod_name):
        return 'Sources'
    if sm.filters.__dict__.has_key(mod_name):
        return 'Filters'
    if sm.animation.__dict__.has_key(mod_name):
        return 'Animation'
    if sm.writers.__dict__.has_key(mod_name):
        return 'Writers'
    return ''

class EnumWidget(QtGui.QComboBox, ConstantWidgetMixin):
    def __init__(self, param, parent=None):
        """__init__(param: core.vistrail.module_param.ModuleParam,
                    parent: QWidget)

        """
        contents = param.strValue
        contentType = param.type
        QtGui.QComboBox.__init__(self, parent)
        ConstantWidgetMixin.__init__(self, param.strValue)
        # want to look up in registry based on parameter type
        
        self.addItem('')
        enum_lst = ['Outline',
                    'Points',
                    'Wireframe',
                    'Surface',
                    'Surface With Edges',
                    'Volume',
                    'Slice']
        for val in enum_lst:
            self.addItem(val)

        curIdx = self.findText(contents)
        if curIdx != -1:
            self.setCurrentIndex(curIdx)
        self._contentType = contentType
        self.connect(self,
                     QtCore.SIGNAL('currentIndexChanged(int)'),
                     self.update_parent)

    def contents(self):
        curIdx = self.currentIndex()
        if curIdx == -1:
            print '*** ""'
            return ''
        print '*** "%s"' % str(self.itemText(curIdx))
        return str(self.itemText(curIdx))

    def setContents(self, strValue, silent=True):
        curIdx = self.findText(contents)
        self.setCurrentIndex(curIdx)
        if not silent:
            self.update_parent()


class StringEnum(String):
    def __init__(self):
        String.__init__(self)

    @staticmethod
    def get_widget_class():
        return EnumWidget

class SetRenderMode(Module):
    def __init__(self):
        Module.__init__(self)
    
    ''' Take a PVModule as input for rendering and assign it a rendering mode -
    outline, surface, volume, etc.  Also takes TransferFunctions as input to
    assign lookuptables.'''
    def compute(self):
        pvIn = self.getInputFromPort("Input")
        lut = self.forceGetInputFromPort("Transfer Function", None)
        mode = self.forceGetInputFromPort("Render Mode", "Surface")
        out = PVBase.PVRenderable()
        out.alpha = self.forceGetInputFromPort("Opacity", 1.0)

        srange = pvIn.pvInstance.PointData.GetArray(0).GetRange()
        arname = pvIn.pvInstance.PointData.GetArray(0).Name

        print srange
        
        lut._min_range = srange[0]
        lut._max_range = srange[1]

        out.pvclut = paraview.simple.GetLookupTableForArray(arname, 1, RGBPoints=[0.0, 0.23, 0.23, 0.75,
                                                                                  255.0, 0.75, 0.15, 0.15],
                                                            ColorSpace='RGB', ScalarRangeInitialized=1.0)
    
        out.pvolut = paraview.simple.CreatePiecewiseFunction(Points=[0.0,0.0,255.0,1.0])
        if lut != None:
            colors = []
            alphas = []
            for pt in lut._pts:
                (scalar, opacity, color) = pt
                scalar = (scalar - lut._min_range) * (lut._max_range - lut._min_range)
                print scalar, color
                print scalar, opacity
                colors.append(scalar)
                colors.append(color[0])
                colors.append(color[1])
                colors.append(color[2])
                alphas.append(scalar)
                alphas.append(opacity)

            out.pvclut.RGBPoints = colors
            out.pvolut.Points = alphas

        out.pvInstance = pvIn.pvInstance
        out.pvLUT = lut
        out.pvMode = mode

        print "Renderable has mode = ", mode

        self.setResult("Renderable", out)
        
def initialize(*args, **keywords):
    reg = core.modules.module_registry
    basic = core.modules.basic_modules
    add_module(PVBase.PVModule, namespace='base')
    add_module(PVBase.PVRenderable, namespace='render')
    add_module(StringEnum, namespace='base')
    
    # Add the SetRenderMode module.
    add_module(SetRenderMode, name='Set Render Mode', namespace='render')
    add_input_port(SetRenderMode, "Input", PVBase.PVModule)
    add_input_port(SetRenderMode, "Transfer Function", reg.registry.get_descriptor_by_name('edu.utah.sci.vistrails.vtk', 'TransferFunction').module)
    add_input_port(SetRenderMode, "Render Mode", StringEnum)
    add_input_port(SetRenderMode, "Opacity", basic.Float)
    add_output_port(SetRenderMode, "Renderable", PVBase.PVRenderable)
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
                    add_paraview_module(m, key)
                        
    for mod_name in mod_funcs.keys():
        mod = new_module(PVBase.PVModule, mod_name)
        ns = get_namespace(mod_name)
        mod.pvSpace = ns.lower()
        mod.pvClass = mod_name
        add_module(mod, name = mod_name, namespace=ns)
        mod_dict[mod_name] = mod
        
    for mod_name in mod_funcs.keys():
        ports = mod_funcs[mod_name]
        # Ports is a list of (name, value list) tuples
        for method in ports:
            name = method[0]
            plist = method[1]
            params = []
            for param in plist:
                params.append(translate_types(param))

            add_input_port(mod_dict[mod_name], name, params)    
        add_output_port(mod_dict[mod_name], "Output", PVBase.PVModule)

    import pvcell
    pvcell.registerSelf()
