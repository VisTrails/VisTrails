from vistrails.core.modules.basic_modules import Color, Path, PathObject, identifier as basic_pkg
from vistrails.core.modules.config import CIPort, COPort, ModuleSettings
from vistrails.core.modules.vistrails_module import ModuleError, Module
from vistrails.core.modules.module_registry import get_module_registry

from vistrails.core.upgradeworkflow import UpgradeWorkflowHandler
from vistrails.core.utils import InstanceObject
from vistrails.core.vistrail.connection import Connection

from .tf_widget import _modules as tf_modules
from .vtkcell import _modules as cell_modules
from .inspectors import _modules as inspector_modules
#offscreen

import re

from identifiers import identifier

from . import vtk_classes, hasher

_modules = tf_modules + cell_modules + inspector_modules

# TODO only new-style module loading will work

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

def _get_input_spec(cls, name):
    """ Get named input spec from self or superclass
    """
    klasses = iter(cls.__mro__)
    base = cls
    while base and hasattr(base, '_input_spec_table'):
        if name in base._input_spec_table:
            return base._input_spec_table[name]
        base = klasses.next()
    return None

def _get_output_spec(cls, name):
    """ Get named output spec from self or superclass
    """
    klasses = iter(cls.__mro__)
    base = cls
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
        d['_get_input_spec'] = classmethod(_get_input_spec)
        d['_get_output_spec'] = classmethod(_get_output_spec)

    new_klass = type(str(spec.module_name), (superklass,), d)
    klasses[spec.module_name] = new_klass
    return new_klass


def initialize():
    _modules.extend([gen_module(spec, vtk_classes, signature=hasher.vtk_hasher)
                     for spec in vtk_classes.specs.module_specs])

################# UPGRADES #####################################################

_remap = None
_controller = None
_pipeline = None

def _get_controller():
    global _controller
    return _controller

def _get_pipeline():
    global _pipeline
    return _pipeline

def build_remap(module_name=None):
    global _remap, _controller

    reg = get_module_registry()
    uscore_num = re.compile(r"(.+)_(\d+)$")

    def get_port_specs(descriptor, port_type):
        ports = {}
        for desc in reversed(reg.get_module_hierarchy(descriptor)):
            ports.update(reg.module_ports(port_type, desc))
        return ports

    def build_remap_method(desc, port_prefix, port_num, port_type):
        # for connection, need to differentiate between src and dst
        if port_type == 'input':
            conn_lookup = Connection._get_destination
            get_port_spec = reg.get_input_port_spec
            idx = 1
        else:
            conn_lookup = Connection._get_source
            get_port_spec = reg.get_output_port_spec
            idx = 0

        def remap(old_conn, new_module):
            create_new_connection = UpgradeWorkflowHandler.create_new_connection
            port = conn_lookup(old_conn)
            pipeline = _get_pipeline()
            modules = [pipeline.modules[old_conn.source.moduleId],
                       pipeline.modules[old_conn.destination.moduleId]]
            modules[idx] = new_module
            ports = [old_conn.source, old_conn.destination]
            for i in xrange(1, port_num):
                port_name = "%s_%d" % (port_prefix, i)
                port_spec = get_port_spec(modules[idx], port_name)
                if port_spec.sigstring == port.signature:
                    ports[idx] = port_name
                    new_conn = create_new_connection(_get_controller(),
                                                     modules[0],
                                                     ports[0],
                                                     modules[1],
                                                     ports[1])
                    return [('add', new_conn)]

            # if get here, just try to use _1 version?
            ports[idx] = "%s_%d" % (port_prefix, 1)
            new_conn = create_new_connection(_get_controller(),
                                             modules[0],
                                             ports[0],
                                             modules[1],
                                             ports[1])
            return [('add', new_conn)]
        return remap

    def build_function_remap_method(desc, port_prefix, port_num):
        f_map = {"vtkCellArray": {"InsertNextCell": 3}}
        def build_function(old_function, new_function_name, new_module):
            controller = _get_controller()
            if len(old_function.parameters) > 0:
                new_param_vals, aliases = \
                    zip(*[(p.strValue, p.alias)
                          for p in old_function.parameters])
            else:
                new_param_vals = []
                aliases = []
            new_function = controller.create_function(new_module,
                                                      new_function_name,
                                                      new_param_vals,
                                                      aliases)
            return new_function

        def remap(old_function, new_module):
            for i in xrange(1, port_num):
                port_name = "%s_%d" % (port_prefix, i)
                port_spec = reg.get_input_port_spec(new_module, port_name)
                old_sigstring = \
                    reg.expand_port_spec_string(old_function.sigstring,
                                                basic_pkg)
                if port_spec.sigstring == old_sigstring:
                    new_function = build_function(old_function, port_name,
                                                  new_module)
                    new_module.add_function(new_function)
                    return []
            port_idx = 1
            if desc.name in f_map:
                if port_prefix in f_map[desc.name]:
                    port_idx =  f_map[desc.name][port_prefix]
            port_name = "%s_%d" % (port_prefix, port_idx)
            new_function = build_function(old_function, port_name, new_module)
            new_module.add_function(new_function)
            return []

        return remap

    def process_ports(desc, port_type):
        if port_type == 'input':
            remap_dict_key = 'dst_port_remap'
        else:
            remap_dict_key = 'src_port_remap'
        ports = get_port_specs(desc, port_type)
        port_nums = {}
        for port_name, port_spec in ports.iteritems():
            # FIXME just start at 1 and go until don't find port (no
            # need to track max)?
            search_res = uscore_num.search(port_name)
            if search_res:
                port_prefix = search_res.group(1)
                port_num = int(search_res.group(2))
                if port_prefix not in port_nums:
                    port_nums[port_prefix] = port_num
                elif port_num > port_nums[port_prefix]:
                    port_nums[port_prefix] = port_num
        if desc.name not in _remap:
            _remap[desc.name] = [(None, '0.9.3', None, dict())]
        my_remap_dict = _remap[desc.name][0][3]
        for port_prefix, port_num in port_nums.iteritems():
            remap = build_remap_method(desc, port_prefix, port_num, port_type)
            my_remap_dict.setdefault(remap_dict_key, {})[port_prefix] = remap
            if port_type == 'input':
                remap = build_function_remap_method(desc, port_prefix, port_num)
                if 'function_remap' not in my_remap_dict:
                    my_remap_dict['function_remap'] = {}
                my_remap_dict['function_remap'][port_prefix] = remap
        if port_type == 'output' and desc.name in klasses:
            my_remap_dict.setdefault('src_port_remap', {})['self'] = 'Instance'

    def process_module(desc):
        # 0.9.3 upgrades
        process_ports(desc, 'input')
        process_ports(desc, 'output')
        # 0.9.5 upgrades
        if desc.name in klasses:
            _remap.setdefault(desc.name, []).append(('0.9.3', '0.9.5', None, {
                    'src_port_remap': {
                        'self': 'Instance',
                    }
                }))
        # 1.0.0 upgrades
        if desc.name in klasses:
            input_mappings = {}
            function_mappings = {}
            for spec in [desc.module._get_input_spec(s)
                         for s in get_port_specs(desc, 'input')]:
                def change_func(name, value):
                    def on_remap(old_func, new_module):
                        controller = _get_controller()
                        new_function = controller.create_function(new_module,
                                                                  name,
                                                                  [value])
                        op = ('change', old_func, new_function,
                              new_module.vtType, new_module.id)
                        new_module.add_function(new_function)
                        return [] #[op]
                    return on_remap
                if spec is None:
                    continue
                elif spec.port_type == 'basic:Boolean':
                    if spec.method_name.endswith('On'):
                        # Convert On/Off to single port
                        input_mappings[spec.name + 'On'] = spec.name
                        input_mappings[spec.name + 'Off'] = spec.name
                        function_mappings[spec.name + 'On'] = \
                                                  change_func(spec.name, True)
                        function_mappings[spec.name + 'Off'] = \
                                                 change_func(spec.name, False)
                    else:
                        # Add True to execute empty functions
                        function_mappings[spec.name] = change_func(spec.name, True)
                elif spec.entry_types and 'enum' in spec.entry_types:
                    # Add one mapping for each default
                    for enum in spec.values[0]:
                        input_mappings[spec.method_name + enum] = spec.name
                        # Add enum value to function
                        function_mappings[spec.method_name + enum] = \
                                                  change_func(spec.name, enum)
                elif spec.port_type == 'basic:Color':
                    # Remove 'Widget' suffix on Color
                    input_mappings[spec.method_name + 'Widget'] = spec.name
                elif spec.port_type == 'basic:File':
                    input_mappings[spec.method_name] = spec.name  # Set*FileName -> *File
                    input_mappings['Set' + spec.name] = spec.name # Set*File -> *File
                elif spec.method_name == 'Set' + spec.name:
                    # Remove 'Set' prefixes
                    input_mappings[spec.method_name] = spec.name
            output_mappings = {}
            for spec_name in get_port_specs(desc, 'output'):
                spec = desc.module._get_output_spec(spec_name)
                if spec is None:
                    continue
                if spec.method_name == 'Get' + spec.name:
                    # Remove 'Get' prefixes
                    output_mappings[spec.method_name] = spec.name

            if input_mappings or output_mappings or function_mappings:
                _remap.setdefault(desc.name, []).append(('0.9.5', '1.0.0', None, {
                        'dst_port_remap': input_mappings,
                        'src_port_remap': output_mappings,
                        'function_remap': function_mappings
                    }))

    pkg = reg.get_package_by_name(identifier)
    if module_name is not None:
        # print 'building remap for', module_name
        desc = reg.get_descriptor_by_name(identifier, module_name)
        process_module(desc)
    else:
        # FIXME do this by descriptor first, then build the hierarchies for each
        # module after that...
        for desc in pkg.descriptor_list:
            process_module(desc)

def handle_module_upgrade_request(controller, module_id, pipeline):
    global _remap, _controller, _pipeline
    if _remap is None:
        _remap = {'vtkInteractionHandler': [(None, '1.0.0', None, {})]}

    _controller = controller
    _pipeline = pipeline
    module_name = pipeline.modules[module_id].name
    if module_name not in _remap:
        build_remap(module_name)
    return UpgradeWorkflowHandler.remap_module(controller, module_id, pipeline,
                                              _remap)
