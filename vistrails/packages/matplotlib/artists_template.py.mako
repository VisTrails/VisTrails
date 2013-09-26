from vistrails.core.modules.vistrails_module import Module
from bases import MplProperties
import matplotlib.artist
import matplotlib.cbook

% if specs.custom_code:
${specs.custom_code}
% endif

<%def name="get_props(t_ps)">\
% if t_ps.constructor_arg:
self.constructor_props['${t_ps.arg}']\
% else:
self.props['${t_ps.arg}']\
% endif
</%def>

<%def name="do_translate(t_spec, t_ps, t_core_ps=None)">\
<%
if t_core_ps is None:
    t_core_ps = t_ps
%>\
% if type(t_ps.translations) == dict:
${get_props(t_core_ps)} = translate_${t_spec.name}_${t_ps.name}(${get_props(t_core_ps)})\
% else:
${get_props(t_core_ps)} = ${t_ps.translations}(${get_props(t_core_ps)})\
% endif
</%def>

def translate_color(c):
    return c.tuple

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
        % for alt_ps in ps.alternate_specs:
              ("${alt_ps.name}", "${alt_ps.get_port_type()}",
               ${alt_ps.get_port_attrs()}),
        % endfor
        % endif
        % endfor
        % for ps in spec.output_port_specs:
        % if ps.is_property():
              ("${ps.name}", "${ps.get_property_type()}",
                ${ps.get_port_attrs()}),
        % endif
        % endfor
        ]

    # no output ports except self
    _output_ports = [("self", "(${spec.name})")]

    def __init__(self):
        ${spec.superklass}.__init__(self)
        self.props = {}
        self.constructor_props = {}
        self.sub_props = {}
        % if spec.get_init():
        ${spec.get_init()}
        % endif

    def compute(self):
        % if spec.get_compute_before():
        ${spec.get_compute_before()}
        % endif
        ${spec.superklass}.compute(self)
        % for ps in spec.port_specs:
        % if not ps.hide and ps.in_kwargs:
        % if ps.required:
        % if ps.has_alternate_versions():
        if self.has_input('${ps.name}'):
            ${get_props(ps)} = self.get_input('${ps.name}')
            % if ps.translations:
            ${do_translate(spec, ps)}
            % endif
        % for alt_ps in ps.alternate_specs:
        elif self.has_input('${alt_ps.name}'):
            ${get_props(ps)} = self.get_input('${alt_ps.name}')
            % if alt_ps.translations:
            ${do_translate(spec, alt_ps, ps)}
            % endif
        % endfor
        else:
            raise ModuleError(self, 'Must set one of "${ps.name}", ' \
                                  '${', '.join('"%s"' % alt_ps.name for alt_ps in ps.alternate_specs)}')
        % else:
        ${get_props(ps)} = self.get_input('${ps.name}')
        % if ps.translations:
        ${do_translate(spec, ps)}
        % endif
        % endif
        ## self.props['${ps.arg}'] = self.get_input('${ps.name}')
        ## % if ps.translations:
        ## ${do_translate(spec, ps)}
        ## % endif
        % else:
        if self.has_input('${ps.name}'):
            ${get_props(ps)} = self.get_input('${ps.name}')
            % if ps.translations:
            ${do_translate(spec, ps)}
            % endif
        % for alt_ps in ps.alternate_specs:
        elif self.has_input('${alt_ps.name}'):
            ${get_props(ps)} = self.get_input('${alt_ps.name}')
            % if alt_ps.translations:
            ${do_translate(spec, alt_ps, ps)}
            % endif
        % endfor
        ## if self.has_input('${ps.name}'):
        ##     self.props['${ps.arg}'] = self.get_input('${ps.name}')
        ##     % if ps.translations:
        ##     ${do_translate(spec, ps)}
        ##     % endif
        % endif
        % endif
        % endfor
        % for ps in spec.output_port_specs:
        % if ps.is_property():
        if self.has_input('${ps.name}'):
            self.sub_props['${ps.arg}'] = self.get_input('${ps.name}')
        % endif
        % endfor            

        % if spec.get_compute_after():
        ${spec.get_compute_after()}
        % endif
        
    def update_props(self, objs):
        matplotlib.artist.setp(objs, **self.props)
        % if any(ps.is_property() for ps in spec.output_port_specs):
        if not matplotlib.cbook.iterable(objs):
            objs = [objs]
        else:
            objs = matplotlib.cbook.flatten(objs)
        for obj in objs:
            % for ps in spec.output_port_specs:
            % if ps.is_property():
            if '${ps.arg}' in self.sub_props:
                self.sub_props['${ps.arg}'].update_props(obj.${ps.compute_parent})
            % endif
            % endfor
        % endif

    def update_kwargs(self, kwargs):
        kwargs.update(self.constructor_props)
        kwargs.update(self.props)

% endfor

_modules = [
% for spec in specs.module_specs:
            ${spec.name},
% endfor
]
