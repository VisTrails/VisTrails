import matplotlib.pyplot
from vistrails.core.modules.vistrails_module import Module, ModuleError
from bases import MplPlot

<%def name="do_translate(t_spec, t_ps)">\
% if type(t_ps.translations) == dict:
val = translate_${t_spec.name}_${t_ps.name}(val)\
% else:
val = ${t_ps.translations}(val)\
% endif
</%def>

<%def name="get_port_val(spec, t_ps)">\
        % if t_ps.required:
        % if t_ps.has_alternate_versions():
        if self.has_input('${t_ps.name}'):
            val = self.get_input('${t_ps.name}')
            % if t_ps.translations:
            ${do_translate(spec, t_ps)}
            % endif
            % if t_ps.in_args:
            args.append(val)
            % elif t_ps.in_kwargs:
            kwargs['${t_ps.arg}'] = val
            % endif
        % for alt_ps in t_ps.alternate_specs:
        elif self.has_input('${alt_ps.name}'):
            val = self.get_input('${alt_ps.name}')
            % if alt_ps.translations:
            ${do_translate(spec, alt_ps)}
            % endif
            % if t_ps.in_args:
            args.append(val)
            % elif t_ps.in_kwargs:
            kwargs['${t_ps.arg}'] = val
            % endif
        % endfor
        else:
            raise ModuleError(self, 'Must set one of "${t_ps.name}", ' \
                                  '${', '.join('"%s"' % alt_ps.name for alt_ps in t_ps.alternate_specs)}')
        % else:
        val = self.get_input('${t_ps.name}')
        % if t_ps.in_args:
        args.append(val)
        % elif t_ps.in_kwargs:
        kwargs['${t_ps.arg}'] = val
        % endif
        % if t_ps.translations:
        ${do_translate(spec, t_ps)}
        % endif
        % endif
        % else:
        if self.has_input('${t_ps.name}'):
            val = self.get_input('${t_ps.name}')
            % if t_ps.translations:
            ${do_translate(spec, t_ps)}
            % endif
            % if t_ps.in_args:
            args.append(val)
            % elif t_ps.in_kwargs:
            kwargs['${t_ps.arg}'] = val
            % endif
        % for alt_ps in t_ps.alternate_specs:
        elif self.has_input('${alt_ps.name}'):
            val = self.get_input('${alt_ps.name}')
            % if alt_ps.translations:
            ${do_translate(spec, alt_ps)}
            % endif
            % if t_ps.in_args:
            args.append(val)
            % elif t_ps.in_kwargs:
            kwargs['${t_ps.arg}'] = val
            % endif
        % endfor
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
        % if ps.is_property():
              ("${ps.name}", "${ps.get_property_type()}",
               ${ps.get_port_attrs()}),
        % else:
              ("${ps.name}", "${ps.get_port_type()}",
               ${ps.get_port_attrs()}),
        % endif
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

    _output_ports = [
        ("value", "(${spec.name})"),
        % if any(not ps.is_property() for ps in spec.output_port_specs):
            # (this plot has additional output which are not exposed as ports
            # right now)
        % endif
        ]

    % if spec.get_init():
    ${spec.get_init()}
    % endif

    def compute(self):
        # get args into args, kwargs
        # write out translations
        args = []
        % for ps in spec.get_input_args():
${get_port_val(spec, ps)}\
        % endfor

        kwargs = {}
        % for ps in spec.port_specs:
        % if ps.is_property():
        if self.has_input('${ps.name}'):
            properties = self.get_input('${ps.name}')
            properties.update_kwargs(kwargs)
        % elif not ps.hide and not ps.in_args and ps.in_kwargs:
${get_port_val(spec, ps)}\
        % endif
        % endfor

        self.set_output('value', lambda figure: self.plot_figure(figure,
                                                                 args, kwargs))

    def plot_figure(self, figure, args, kwargs):
        % if spec.get_compute_before():
        ${spec.get_compute_before()}
        % endif
        % if spec.get_compute_inner():
        ${spec.get_compute_inner()}
        % elif spec.output_type is None:
        ${spec.code_ref}(*args, **kwargs)
        % elif spec.output_type == "object":
        ${spec.get_returned_output_port_specs()[0].compute_name} = ${spec.code_ref}(*args, **kwargs)
        % else:
        output = ${spec.code_ref}(*args, **kwargs)
        % endif
        % if spec.get_compute_after():
        ${spec.get_compute_after()}
        % endif
        % if spec.output_type == "dict":
        % for ps in spec.get_returned_output_port_specs():
        ${ps.compute_name} = output['${ps.property_key}']
        % endfor
        % elif spec.output_type == "tuple":
        % for ps in sorted(spec.get_returned_output_port_specs(), \
                               key=lambda ps: ps.property_key):
        ${ps.compute_name} = output[${ps.property_key}]
        % endfor
        % endif
        % for ps in spec.output_port_specs:
        % if ps.is_property():
        if self.has_input('${ps.name}'):
            properties = self.get_input('${ps.name}')
            % if ps.compute_parent:
            % if spec.get_output_port_spec(ps.compute_parent).plural:
            for obj in ${spec.get_output_port_spec(ps.compute_parent).compute_name}:
                properties.update(obj.${ps.compute_name})
            % else:
            if ${spec.get_output_port_spec(ps.compute_parent).compute_name}.${ps.compute_name} is not None:
                properties.update(${spec.get_output_port_spec(ps.compute_parent).compute_name}.${ps.compute_name})
            % endif
            % else:
            if ${ps.compute_name} is not None:
                properties.update_props(${ps.compute_name})
            % endif
        % else:
        self.set_output('${ps.name}', ${ps.compute_name})
        % endif
        % endfor

% endfor

_modules = [
% for spec in specs.module_specs:
            ${spec.name},
% endfor
]
