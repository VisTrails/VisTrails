# -*- coding: utf-8 -*-

import vtk

from vistrails.core import debug
from vistrails.core.modules.vistrails_module import Module, ModuleError

from bases import vtkObjectBase
<%def name="get_translate(t_spec, t_ps)">\
% if t_ps.translations is None:
None\
% elif type(t_ps.translations) == dict:
translate_${t_spec.name}_${t_ps.name}\
% else:
${t_ps.translations}\
% endif
</%def>\

def translate_color(c):
    return c.tuple

def translate_file(f):
    return f.name

% for spec in specs.module_specs:
% for ps in spec.port_specs:
% if ps.translations and type(ps.translations) == dict:
def translate_${spec.name}_${ps.name}(val):
    translate_dict = ${ps.translations}
    return translate_dict[val]
% endif
% endfor
% endfor

% for spec in specs.module_specs:
class ${spec.name}(${spec.superklass}):
    """${spec.docstring}
    """
    _input_ports = [
        % for ps in spec.port_specs:
        % if not ps.hide:
              ("${ps.name}", "${ps.get_port_type()}",
               ${ps.get_port_attrs()}),
        % endif
        % endfor
         ]

    _output_ports = [
        ("self", "(${spec.name})"),
        % for ps in spec.output_port_specs:
              ("${ps.name}", "${ps.get_port_type()}",
                ${ps.get_port_attrs()}),
        % endfor
        ]
    
    set_method_table = {
        % for ps in spec.port_specs:
        "${ps.name}": ("${ps.method_name}", ${ps.get_port_shape()}, ${ps.get_other_params()}, ${get_translate(spec, ps)}),
        % endfor
        }

    get_method_table = {
        % for ps in spec.output_port_specs:
        "${ps.name}": ("${ps.method_name}", ${ps.get_other_params()}),
        % endfor
        }

    % if spec.get_init():
    ${spec.get_init()}
    % endif

    @staticmethod
    def get_set_method_info(port_name):
        if port_name in ${spec.name}.set_method_table:
            return ${spec.name}.set_method_table[port_name]
        return ${spec.superklass}.get_set_method_info(port_name)

    @staticmethod
    def get_get_method_info(port_name):
        if port_name in ${spec.name}.get_method_table:
            return ${spec.name}.get_method_table[port_name]
        return ${spec.superklass}.get_get_method_info(port_name)

    def compute(self):
        vtk_obj = ${spec.code_ref}()
        self.do_compute(vtk_obj, ${spec.is_algorithm})
        ## % if spec.get_compute_before():
        ## ${spec.get_compute_before()}
        ## % else:
        ## # call methods first
        ## ## methods = self.is_method.values()
        ## ## methods.sort()
        ## for value in sorted(self.is_method.itervalues()):
        ##     (_, port_name) = value
        ##     ## FIXME can we make this an iteritems thing with itemgetter(1)?
        ##     connector = self.is_method.inverse[value]
        ##     self.call_set_method(vtk_obj, port_name, connector())
        ## % endif
        ##
        ## % if spec.get_compute_inner():
        ## ${spec.get_compute_inner()}
        ## % else:
        ## for (port_name, connector_list) in self.inputPorts.iteritems():
        ##     params = self.get_input_list(port_name)
        ##     for p, connector in izip(params, connector_list):
        ##         ## Don't call method
        ##         if connector in self.is_method:
        ##             continue
        ##         self.call_set_method(vtk_obj, port_name, params)
        ## % endif
        ##
        ## % if spec.get_compute_after():
        ## ${spec.get_compute_after()}
        ## % endif
        ##
        ## if hasattr(vtk_obj, 'Update'):
        ##     % if spec.is_algorithm:
        ##     is_aborted = False
        ##     cbId = None
        ##     def ProgressEvent(obj, event):
        ##         try:
        ##             self.logging.update_progress(self, obj.GetProgress())
        ##         except AbortExecution:
        ##             obj.SetAbortExecute(True)
        ##             vtk_obj.RemoveObserver(cbId)
        ##             is_aborted = True
        ##     cbId = vtk_obj.AddObserver('ProgressEvent', ProgressEvent)
        ##     % endif
        ##     vtk_obj.Update()
        ##     % if spec.is_algorithm:
        ##     if not is_aborted:
        ##         vtk_obj.RemoveObserver(cbId)
        ##     % endif
        ##
        ## # Then update the output ports also with appropriate function calls
        ## for port_name in self.outputPorts:
        ##     if port_name == 'self':
        ##         self.set_output('self', vtk_obj)
        ##     else:
        ##         self.call_get_method(vtk_obj, port_name)

% endfor

_modules = [
% for spec in specs.module_specs:
            ${spec.name},
% endfor
]
