from vistrails.core.modules.config import CIPort, COPort, ModuleSettings
from vistrails.core.modules.vistrails_module import ModuleError, Module

from .bases import _modules as base_modules, vtkObjectBase
#from .vtk_classes import _modules as vtk_modules
from .tf_widget import _modules as tf_modules
from .vtkcell import _modules as cell_modules
from . import inspectors, offscreen

from .generate.specs import SpecList, VTKModuleSpec
import vtk
import os
import vtk_classes

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
klasses = {'vtkObjectBase': Module}

def gen_module(spec, lib):
    """Create a module from a python function specification

    Parameters
    ----------
    spec : ModuleSpec
        A module specification
    """

    _settings = ModuleSettings(**spec.get_module_settings())

    # convert input/output specs into VT port objects
    input_ports = [CIPort(ispec.name, ispec.get_port_type(), **ispec.get_port_attrs())
                   for ispec in spec.input_port_specs if not ispec.hide]
    output_ports = [COPort(ospec.name, ospec.get_port_type(), **ospec.get_port_attrs())
                    for ospec in spec.output_port_specs if not ospec.hide]

    def compute(self):

        inputs = dict([(s.name, self.force_get_input(s.name))
                       for s in self.input_specs.itervalues() if self.force_get_input(s.name) is not None])

        function = getattr(lib, spec.code_ref)
        try:
            result = function(**inputs)
        except Exception, e:
            raise ModuleError(self, e.message)

        print "FINAL OUT ORDER", self.output_specs_order
        if spec.output_type is None:
            for name in self.output_specs_order:
                self.set_output(name, result)
        elif spec.output_type == 'list':
            for name, value in zip(self.output_specs_order, result):
                self.set_output(name, value)
        elif spec.output_type == 'dict':
            for name in self.output_specs_order:
                self.set_output(name, result[name])

    new_klass = type(str(spec.module_name), (klasses.get(spec.superklass, Module),),
                                {'compute': compute,
                                 '__module__': __name__,
                                 '_settings': _settings,
                                 '__doc__': spec.docstring,
                                 '__name__': spec.name or spec.module_name,
                                 '_input_ports': input_ports,
                                 '_output_ports': output_ports})
    klasses[spec.module_name] = new_klass
    return new_klass


def initialize():
    _modules.extend([gen_module(spec, vtk_classes)
                     for spec in vtk_classes.specs.module_specs])
