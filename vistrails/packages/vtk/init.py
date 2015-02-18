from vistrails.core.modules.basic_modules import Color, Path, PathObject
from vistrails.core.modules.config import CIPort, COPort, ModuleSettings
from vistrails.core.modules.vistrails_module import ModuleError, Module

from .tf_widget import _modules as tf_modules
from vistrails.core.utils import InstanceObject
from .vtkcell import _modules as cell_modules
from . import inspectors, offscreen

import vtk
import os
from . import vtk_classes,hasher

_modules = tf_modules + cell_modules

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


# TODO: code below is independent of VTK and should be moved elsewhere

#### Automatic conversion between some vistrail and python types ####

def convert_input_param(value, _type):
    # convert from Path port
    if issubclass(_type, Path):
        return value.name
    if issubclass(_type, Color):
        return value.tuple
    return value

def convert_output_param(value, _type):
    # convert to Path port
    if isinstance(_type, Path):
        return PathObject(value)
    if isinstance(_type, Color):
        return InstanceObject(tuple=value)
    return value

def convert_input(value, signature):
    if len(signature) == 1:
        return convert_input_param(value, signature[0][0])
    return [convert_input_param(v, t[0]) for v, t in zip(value, signature)]

def convert_output(value, signature):
    if len(signature) == 1:
        return convert_output_param(value, signature[0][0])
    return [convert_output_param(v, t[0]) for v, t in zip(value, signature)]

####################################################################

# keep track of created modules for use as subclasses
klasses = {}

def _get_input_spec(self, name):
    """ Get named input spec from self or superclass
    """
    klasses = iter(type(self).__mro__)
    base = klasses.next()
    while base and hasattr(base, '_input_spec_table'):
        if name in base._input_spec_table:
            return base._input_spec_table[name]
        base = klasses.next()
    return None

def _get_output_spec(self, name):
    """ Get named output spec from self or superclass
    """
    klasses = iter(type(self).__mro__)
    base = klasses.next()
    while base and hasattr(base, '_output_spec_table'):
        if name in base._output_spec_table:
            return base._output_spec_table[name]
        base = klasses.next()
    return None

def gen_module(spec, lib, **module_settings):
    """Create a module from a python function specification

    Parameters
    ----------
    spec : ModuleSpec
        A module specification
    """
    module_settings.update(spec.get_module_settings())
    _settings = ModuleSettings(**module_settings)

    # convert input/output specs into VT port objects
    input_ports = [CIPort(ispec.name, ispec.get_port_type(), **ispec.get_port_attrs())
                   for ispec in spec.input_port_specs if not ispec.hide]
    output_ports = [COPort(ospec.name, ospec.get_port_type(), **ospec.get_port_attrs())
                    for ospec in spec.output_port_specs if not ospec.hide]


    _input_spec_table = {}
    for ps in spec.input_port_specs:
        _input_spec_table[ps.name] = ps
    _output_spec_table = {}
    for ps in spec.output_port_specs:
        _output_spec_table[ps.name] = ps

    def compute(self):
        # read inputs, convert, and translate to args
        inputs = dict([(self._get_input_spec(s.name).arg, convert_input(self.get_input(s.name),
                                              self.input_specs[s.name].signature))
                       for s in self.input_specs.itervalues() if self.has_input(s.name)])

        # Optional callback used for progress reporting
        if spec.callback:
            def callback(c):
                self.logging.update_progress(self, c)
            inputs[spec.callback] = callback

        # Optional temp file
        if spec.tempfile:
            inputs[spec.tempfile] = self._file_pool.create_file

        # Optional list of outputs to compute
        if spec.outputs:
            inputs[spec.outputs] = self.outputPorts.keys()

        function = getattr(lib, spec.code_ref)
        try:
            result = function(**inputs)
        except Exception, e:
            raise ModuleError(self, e.message)

        # convert outputs to dict
        outputs = {}
        outputs_list = self.output_specs_order
        outputs_list.remove('self') # self is automatically set by base Module

        if spec.output_type is None:
            for name in self.output_specs_order:
                outputs[name] = result
        elif spec.output_type == 'list':
            for name, value in zip(self.output_specs_order, result):
                outputs[name] = value
        elif spec.output_type == 'dict':
            # translate from args to names
            t = dict([(self._get_output_spec(s.name).arg, s.name)
                      for s in spec.output_port_specs])
            outputs = dict([(t[arg], value)
                            for arg, value in result.iteritems()])

        # convert values to vistrail types
        for name in outputs:
            if outputs[name]:
                outputs[name] = convert_output(outputs[name],
                                            self.output_specs[name].signature)

        # set outputs
        for key, value in outputs.iteritems():
            self.set_output(key, value)

    d = {'compute': compute,
         '__module__': __name__,
         '_settings': _settings,
         '__doc__': spec.docstring,
         '__name__': spec.name or spec.module_name,
         '_input_ports': input_ports,
         '_output_ports': output_ports,
         '_input_spec_table': _input_spec_table,
         '_output_spec_table': _output_spec_table}

    superklass = klasses.get(spec.superklass, Module)
    if superklass == Module:
        d['_get_input_spec'] = _get_input_spec
        d['_get_output_spec'] = _get_output_spec

    new_klass = type(str(spec.module_name), (superklass,), d)
    klasses[spec.module_name] = new_klass
    return new_klass


def initialize():
    _modules.extend([gen_module(spec, vtk_classes, signature=hasher.vtk_hasher)
                     for spec in vtk_classes.specs.module_specs])
