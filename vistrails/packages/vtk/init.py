from vistrails.core.system import get_vistrails_default_pkg_prefix
from vistrails.core.modules.config import CIPort, COPort, ModuleSettings

from .bases import _modules as base_modules, vtkObjectBase
#from .vtk_classes import _modules as vtk_modules
from .tf_widget import _modules as tf_modules
from .vtkcell import _modules as cell_modules
from . import inspectors, offscreen

from .generate.specs import SpecList, VTKModuleSpec
import vtk
import os

_modules = base_modules + tf_modules + cell_modules

# TODO only new-style module loading will work

#inspectors.initialize()
#offscreen.register_self()

#registry = get_module_registry()
#if registry.has_module('%s.spreadsheet' % get_vistrails_default_pkg_prefix(),
#                       'SpreadsheetCell'):
#    from . import vtkhandler, vtkviewcell
#    from .vtkcell import _modules as cell_modules
#    _modules += cell_modules
#    vtkhandler.registerSelf()
#    vtkviewcell.registerSelf()


from bases import vtkObjectBase

def translate_color(c):
    return c.tuple

def translate_file(f):
    return f.name

def get_translate(t_spec, t_ps):
    if t_ps.translations is None:
        return None
    elif type(t_ps.translations) == dict:
        t = "translate_%s_%s" % (t_spec.name, t_ps.name)
    else:
        t = t_ps.translations
    return locals().get(t) or globals().get(t)

# keep track of created modules for use as subclasses
klasses = {'vtkObjectBase': vtkObjectBase}

def gen_module(spec):
    """Create a module from a module specification

    Parameters
    ----------
    spec : VTKModuleSpec
        A vtk module specification
    """

    # convert input/output specs into VT port objects
    input_ports = [CIPort(ispec.name, ispec.get_port_type(), **ispec.get_port_attrs())
                   for ispec in spec.input_port_specs if not ispec.hide]
    output_ports = [COPort(ospec.name, ospec.get_port_type(), **ospec.get_port_attrs())
                    for ospec in spec.output_port_specs if not ospec.hide]

    set_method_table = {}
    for ps in spec.input_port_specs:
        set_method_table[ps.name] = (ps.method_name, ps.get_port_shape(),
                                     ps.get_other_params(), get_translate(spec, ps))

    get_method_table = {}
    for ps in spec.output_port_specs:
        get_method_table[ps.name] = (ps.method_name, ps.get_other_params())

    def compute(self):
        vtk_obj = getattr(vtk, spec.code_ref)()
        self.do_compute(vtk_obj, spec.is_algorithm)

    _settings = ModuleSettings(**spec.get_module_settings())
    new_klass = type(str(spec.module_name), (klasses[spec.superklass],),
                                {'compute': compute,
                                 '__module__': __name__,
                                 '_settings': _settings,
                                 '__doc__': spec.docstring,
                                 '__name__': spec.name or spec.module_name,
                                 '_input_ports': input_ports,
                                 '_output_ports': output_ports,
                                 'set_method_table': set_method_table,
                                 'get_method_table': get_method_table})
    klasses[spec.module_name] = new_klass
    return new_klass


def initialize():
    fname = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'vtk.xml')
    specs = SpecList.read_from_xml(fname, VTKModuleSpec)
    _modules.extend([gen_module(spec) for spec in specs.module_specs])
