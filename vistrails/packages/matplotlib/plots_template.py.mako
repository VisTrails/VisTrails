import matplotlib.pyplot
from core.modules.vistrails_module import Module
from bases import MplPlot

<%def name="do_translate(t_spec, t_ps)">\
% if type(t_ps.translations) == dict:
kwargs['${t_ps.arg}'] = translate_${t_spec.name}_${t_ps.name}(kwargs['${t_ps.arg}'])\
% else:
kwargs['${t_ps.arg}'] = ${t_ps.translations}(kwargs['${t_ps.arg}'])\
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
        % if ps.is_property_output():
              ("${ps.name}", "${ps.get_property_type()}",
                ${ps.get_port_attrs()}),
        % endif
        % endfor
        ]

    _output_ports = [
        ("self", "(${spec.name})"),
        % for ps in spec.output_port_specs:
        % if not ps.is_property_output():
              ("${ps.name}", "${ps.get_port_type()}",
                ${ps.get_port_attrs()}),
        % endif
        % endfor
        ]
    
    % if spec.get_init():
    ${spec.get_init()}
    % endif

    def compute(self):
        # get args into args, kwargs
        # write out translations
        kwargs = {}            
        % for ps in spec.port_specs:
        % if not ps.hide and ps.in_kwargs:
        % if ps.required:
        % if ps.has_alternate_versions():
        if self.hasInputFromPort('${ps.name}'):
            kwargs['${ps.arg}'] = self.getInputFromPort('${ps.name}')
            % if ps.translations:
            ${do_translate(spec, ps)}
            % endif
        % for alt_ps in ps.alternate_specs:
        elif self.hasInputFromPort('${alt_ps.name}'):
            kwargs['${ps.arg}'] = self.getInputFromPort('${alt_ps.name}')
            % if alt_ps.translations:
            ${do_translate(spec, alt_ps)}
            % endif
        % endfor
        else:
            raise ModuleError(self, 'Must set one of "${ps.name}", ' \
                                  '${', '.join('"%s"' % alt_ps.name for alt_ps in ps.alternate_specs)}')
        % else:
        kwargs['${ps.arg}'] = self.getInputFromPort('${ps.name}')
        % if ps.translations:
        ${do_translate(spec, ps)}
        % endif
        % endif
        % else:
        if self.hasInputFromPort('${ps.name}'):
            kwargs['${ps.arg}'] = self.getInputFromPort('${ps.name}')
            % if ps.translations:
            ${do_translate(spec, ps)}
            % endif
        % for alt_ps in ps.alternate_specs:
        elif self.hasInputFromPort('${alt_ps.name}'):
            kwargs['${ps.arg}'] = self.getInputFromPort('${alt_ps.name}')
            % if alt_ps.translations:
            ${do_translate(spec, alt_ps)}
            % endif
        % endfor
        % endif
        % endif
        % endfor
        # self.get_fig()
        % if spec.get_compute_before():
        ${spec.get_compute_before()}
        % endif
        % if spec.get_compute_inner():
        ${spec.get_compute_inner()}
        % elif spec.output_type is None:
        ${spec.code_ref}(**kwargs)        
        % elif spec.output_type == "object":
        ${spec.get_returned_output_port_specs()[0].compute_name} = ${spec.code_ref}(**kwargs)
        % else:
        output = ${spec.code_ref}(**kwargs)        
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
        % if ps.is_property_output():
        if self.hasInputFromPort('${ps.name}'):
            properties = self.getInputFromPort('${ps.name}')
            % if ps.compute_parent:
            % if spec.get_output_port_spec(ps.compute_parent).plural:
            for obj in ${spec.get_output_port_spec(ps.compute_parent).compute_name}:
                properties.update(obj.${ps.compute_name})
            % else:
                properties.update(${spec.get_output_port_spec(ps.compute_parent).compute_name}.${ps.compute_name})
            % endif
            ## % if ps.plural:
            ## for obj in ${ps.compute_name}:
            ##     properties.update(obj)
            ## % else:
            ## properties.update(${ps.compute_name})
            ## % endif
            % else:
            properties.update_props(${ps.compute_name})
            % endif
        % else:
        self.setResult('${ps.name}', ${ps.compute_name})
        % endif
        % endfor

% endfor        
          
_modules = [
% for spec in specs.module_specs:
            ${spec.name},
% endfor
]
