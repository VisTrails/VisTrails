"""Pipeline to Python exporting logic.

This contains write_workflow_to_python(), which exports a VisTrails pipeline as
a standalone Python script.
"""

from __future__ import division, unicode_literals

import ast
import copy
import re

from vistrails.core import debug
from vistrails.core.modules.basic_modules import List
from vistrails.core.modules.module_registry import get_module_registry
from vistrails.core.scripting.scripts import make_unique, Script, Prelude, reserved
from vistrails.core.scripting.utils import utf8
from vistrails.core.vistrail.module_control_param import ModuleControlParam


def write_workflow_to_python(pipeline):
    """Writes a pipeline to a Python source file.

    :returns: An iterable over the lines (as unicode) of the generated script.
    """
    # The set of all currently bound symbols in the resulting script's global
    # scope
    # These are either variables from translated modules (internal or output
    # ports) or imported names
    all_vars = set(reserved)

    # Should we import izip or product from itertools?
    import_izip = False
    import_product = False

    # The parts of the final generated script
    text = []

    # The modules that have been translated, maps from the module's id to a
    # Script object
    modules = dict()

    # The preludes that have been collected
    # A "prelude" is a piece of code that is supposed to go at the top of the
    # file, and that shouldn't be repeated; things like import statements,
    # function/class definition, and constants
    preludes = []

    reg = get_module_registry()

    # set port specs and module depth
    pipeline.validate(False)

    # ########################################
    # Walk through the pipeline to get all the codes
    #
    for module_id in pipeline.graph.vertices_topological_sort():
        module = pipeline.modules[module_id]
        print("Processing module %s %d" % (module.name, module_id))

        desc = module.module_descriptor
        module_class = desc.module

        # Gets the code
        code_preludes = []
        if not hasattr(module_class, 'to_python_script'):
            # Use vistrails API to execute module
            code, code_preludes = generate_api_code(module)
        elif module_class.to_python_script is None:
            debug.critical("Module %s cannot be converted to Python" %
                           module.name)
            code = Script("# <Missing code>\n"
                          "# %s has empty function to_python_script()\n"
                          "# VisTrails cannot currently export such modules" %
                          module.name,
                          'variables', 'variables')
        else:
            # Call the module to get the base code
            code = module_class.to_python_script(module)
            if isinstance(code, tuple):
                code, code_preludes = code
            print("Got code:\n%r" % (code,))
            assert isinstance(code, Script)

        modules[module_id] = code
        preludes.extend(code_preludes)

    # ########################################
    # Processes the preludes and writes the beginning of the file
    #
    print("Writing preludes")
    # Adds all imported modules to the list of symbols
    for prelude in preludes:
        all_vars.update(prelude.imported_pkgs)
    # Removes collisions
    prelude_renames = {}
    for prelude in preludes:
        prelude_renames.update(prelude.avoid_collisions(all_vars))
    # remove duplicates
    final_preludes = []
    final_prelude_set = set()
    for prelude in [unicode(p) for p in preludes]:
        if prelude not in final_prelude_set:
            final_prelude_set.add(prelude)
            final_preludes.append(prelude)

    # Writes the preludes
    for prelude in final_preludes:
        text.append(prelude)
    #if preludes:
    #    text.append('# PRELUDE ENDS -- pipeline code follows\n\n')
    text.append('')

    # ########################################
    # Walk through the pipeline a second time to generate the full script
    #
    first = True
    # outer name of output is different from name in code if loop is used
    # so we keep this mapping: {(module_id, oport_name): outer_name}
    output_loop_map = {}
    for module_id in pipeline.graph.vertices_topological_sort():
        module = pipeline.modules[module_id]
        desc = module.module_descriptor
        print("Writing module %s %d" % (module.name, module_id))

        if not first:
            text.append('\n')
        else:
            first = False

        # Annotation, used to rebuild the pipeline
        text.append("# MODULE %d %s" % (module_id, desc.sigstring))

        code = modules[module_id]

        # Gets all the module's input and output port names
        input_ports = set(reg.module_destination_ports_from_descriptor(False, desc))
        input_ports.update(module.input_port_specs)

        input_port_names = set(p.name for p in input_ports)
        iports = dict((p.name, p) for p in input_ports)
        connected_inputs = set()
        for _, conn_id in pipeline.graph.edges_to(module_id):
            conn = pipeline.connections[conn_id]
            connected_inputs.add(utf8(conn.destination.name))
        for function in module.functions:
            connected_inputs.add(utf8(function.name))
        output_ports = set(reg.module_source_ports_from_descriptor(False, desc))
        output_ports.update(module.output_port_specs)
        output_port_names = set(p.name for p in output_ports)
        connected_outputs = set()
        for _, conn_id in pipeline.graph.edges_from(module_id):
            conn = pipeline.connections[conn_id]
            connected_outputs.add(utf8(conn.source.name))

        # Changes symbol names in this piece of code to prevent collisions
        # with already-encountered code
        old_all_vars = set(all_vars)
        code.normalize(input_port_names, output_port_names, all_vars)
        # Now, code knows what its inputs and outputs are
        print("Normalized code:\n%r" % (code,))
        print("New vars in all_vars: %r" % (all_vars - old_all_vars,))
        print("used_inputs: %r" % (code.used_inputs,))

        # build final inputs as result of merging connections
        # {dest_name: {source_name, depth_diff}}
        combined_inputs = {}
        # Adds functions
        for function in module.functions:
            port = utf8(function.name)
            code.unset_inputs.discard(port)
            if code.skip_functions:
                continue
            if port not in code.used_inputs:
                print("NOT adding function %s (not used in script)" % port)
                continue

            ## Creates a variable with the value
            name = make_unique(port, all_vars)
            if len(function.params) == 1:
                value = function.params[0].value()
            else:
                value = [p.value() for p in function.params]

            depth = - iports[port].depth
            print("Function %s: var %s, value %r" % (port,
                                                     name, value))
            text.append("# FUNCTION %s %s" % (port, name))
            text.append('%s = %r' % (name, value))
            if port not in combined_inputs:
                combined_inputs[port] = []
            combined_inputs[port].append((name, depth))

        # Sets input connections
        conn_ids = sorted([conn_id for _, conn_id in
                           pipeline.graph.edges_to(module_id)])
        for conn_id in conn_ids:
            conn = pipeline.connections[conn_id]
            dst = conn.destination
            port = utf8(dst.name)
            if port not in code.used_inputs:
                print("NOT connecting port %s (not used in script)" % dst.name)
                continue
            src = conn.source

            # Tells the code what the variable was
            src_mod = modules[src.moduleId]
            name = output_loop_map.get((src.moduleId, src.name),
                                       src_mod.get_output(src.name))

            # get depth difference to destination port
            depth = pipeline._connection_depths.get(conn_id, 0)
            # account for module looping
            depth += pipeline.modules[src.moduleId].list_depth

            print("Input %s: var %s" % (port, name))
            text.append("# CONNECTION %s %s" % (dst.name, name))
            #code.set_input(utf8(dst.name), name)
            code.unset_inputs.discard(utf8(dst.name))
            if port not in combined_inputs:
                combined_inputs[port] = []
            combined_inputs[port].append((name, depth))

        # Sets default values
        if code.unset_inputs:
            print("unset_inputs: %r" % (code.unset_inputs,))
            for port in set(code.unset_inputs):
                if port not in code.used_inputs:
                    continue
                # Creates a variable with the value
                name = make_unique(port, all_vars)
                default = iports[port].defaults
                if len(default) == 1:
                    default = default[0]
                print("Default: %s: var %s, value %r" % (
                      port, name, default))
                text.append("# DEFAULT %s %s" % (port, name))
                text.append('%s = %s' % (name, default))
                code.set_input(port, name)

        # merge connections
        # [(port, [names], depth)]
        merged_inputs = []
        # keep input port order
        for iport in sorted(input_ports, key=lambda x: (x.sort_key, x.id)):
            port = iport.name
            if port not in combined_inputs:
                continue
            conns = combined_inputs[port]
            descs = iports[port].descriptors()
            can_merge = ((len(descs) == 1 and isinstance(descs[0], List)) or
                         iports[port].depth > 0)
            if len(conns) == 1 or not can_merge:
                # no merge needed
                name = conns[0][0]
                depth = conns[0][1]
                if depth >= 0:
                    # add directly
                    new_names = [name]
                    for i in xrange(depth):
                        name = make_unique(new_names[-1] + '_item', all_vars)
                        new_names.append(name)
                    code.set_input(port, name)
                    merged_inputs.append((port, new_names, depth))
                else:
                    # wrap to correct depth as new variable
                    while depth:
                        depth += 1
                        name = '[%s]' % name
                    new_name = make_unique(code.inputs[port], all_vars)
                    text.append('%s = %s' % (new_name, name))
                    code.set_input(port, new_name)
                    merged_inputs.append((port, [new_name], 0))
            else:
                # merge connections
                items = []
                for name, depth in conns:
                    # wrap to max depth
                    while depth < 0:
                        depth += 1
                        name = '[%s]' % name
                    items.append(name)
                # assign names to list items in loop
                # like "xItem", "xItemItem", etc.
                new_names = [make_unique(code.inputs[port], all_vars)]
                max_depth = max([c[1] for c in conns])
                if max_depth > 0:
                    for i in xrange(max_depth):
                        new_name = make_unique(new_names[-1] + '_item', all_vars)
                        new_names.append(new_name)
                text.append('%s = %s' % (new_names[0], ' + '.join(items)))
                code.set_input(port, new_names[-1])
                merged_inputs.append((port, new_names, max_depth))

        #### Prepare looping #################################################
        max_level = module.list_depth
        # names for the looped output ports
        output_sub_ports = dict([(port, [code.get_output(port)])
                                 for port in connected_outputs])
        # add output names to global output name list
        for port, names in output_sub_ports.iteritems():
            output_loop_map[(module_id, port)] = names[0]
        offset_levels = []
        loop_args = []
        for level in xrange(1, max_level+1):
            # Output values are collected from the inside and out
            for port in connected_outputs:
                sub_ports = output_sub_ports[port]
                new_name = make_unique(sub_ports[-1] + '_item', all_vars)
                code.set_output(port, new_name)
                sub_ports.append(new_name)

            # construct the loop code
            combine_type = 'cartesian'
            if max_level == 1:
                # first level may use a complex port combination
                cps = {}
                for cp in module.control_parameters:
                    cps[cp.name] = cp.value
                if ModuleControlParam.LOOP_KEY in cps:
                    combine_type = cps[ModuleControlParam.LOOP_KEY]
                    if combine_type not in ['cartesian', 'pairwise']:
                        combine_type = ast.literal_eval(combine_type)
            if combine_type == 'cartesian':
                # make nested for loops for all iterated ports
                items = []
                for port, names, depth in merged_inputs:
                    if depth >= level:
                        # map parent level name to this level
                        items.append((names[level], names[level-1]))
                offset = 0
                loop_arg = []
                for item in items:
                    loop_arg.append('    ' * offset + 'for %s in %s:' % item)
                    offset += 1
                loop_args.append('\n'.join(loop_arg))
                offset_levels.append(offset)
            elif combine_type == 'pairwise':
                #  zip all iterated ports
                prev_items, cur_items = [], []
                for port, names, depth in merged_inputs:
                    if depth >= level:
                        # map parent level name to this level
                        prev_items.append(names[level-1])
                        cur_items.append(names[level])
                loop_arg = 'for %s in izip(%s):' % (', '.join(cur_items),
                                                    ', '.join(prev_items))
                import_izip = True
                loop_args.append(loop_arg)
                offset_levels.append(1)
            else:
                #  construct custom combination
                name_map = {}
                for port, names, depth in merged_inputs:
                    if depth >= level:
                        # map parent level name to this level
                        name_map[port] = (names[level-1], names[level])
                loop_arg = "for %s in %s:" % combine(combine_type, name_map)
                if 'izip' in loop_arg:
                    import_izip = True
                if 'product(' in loop_arg:
                    import_product = True
                loop_args.append(loop_arg)
                offset_levels.append(1)

        # TODO: handle while loop

        #### Write loop start ################################################
        for level in xrange(0, max_level):
            offset = sum(offset_levels[:level])

            for port in connected_outputs:
                sub_ports = output_sub_ports[port]
                text.append('   ' * offset + '%s = []' % sub_ports[level])
                sub_ports.append(new_name)

            for_loop = '\n'.join(['    ' * offset + f
                                  for f in loop_args[level].split('\n')])
            text.append(for_loop)

        #### Write module code ###############################################
        code_text = unicode(code)
        if offset_levels:
            code_text = code_text.split('\n')
            code_text = '\n'.join(['    '*sum(offset_levels) + t for t in code_text])
            # node.increase_indent(sum(offset_levels)*4)
        # Ok, add the module's code
        print("Rendering code")
        text.append(code_text)
        print("Total new vars: %r" % (all_vars - old_all_vars,))

        #### Write loop end ##################################################
        for level in reversed(xrange(0, max_level)):
            offset = sum(offset_levels[:level+1])
            for port in connected_outputs:
                sub_ports = output_sub_ports[port]
                text.append('    ' * offset +
                            '%s.append(%s)' % (sub_ports[level], sub_ports[level-1]))

    if import_izip or import_product:
        if not import_product:
            text.insert(0, 'from itertools import izip\n')
        elif not import_product:
            text.insert(0, 'from itertools import product\n')
        else:
            text.insert(0, 'from itertools import izip, product\n')
    return text


def generate_api_code(module):
    """ Start vistrails API, create module, assign inputs, compute, get outputs

        This executes a module directly, without going through the interpreter.
    """
    preludes = []
    desc = module.module_descriptor
    pkg_name = desc.identifier.replace('.', '_')
    preludes.append(Prelude('import vistrails.core.scripting.api as api'))
    preludes.append(Prelude("%s = api.Package(%r)" % (
                            pkg_name, desc.identifier)))
    code = ''
    # instance does not need to be stored, we use it as a function
    #instance = re.sub('(?!^)([A-Z]+)', r'_\1', desc.name).lower()
    #code += "%s = %s.%s()\n" % (instance, pkg_name, desc.name)
    instance = '.' + desc.name
    if desc.namespace:
        ns = desc.namespace
        parts = ''
        for part in ns.split('|'):
            if re.match('[_A-Za-z][_a-zA-Z0-9]*', part):
                parts += '.' + part
            else:
                parts += "['" + part + "']"
        instance = parts + instance

    function_ports = [p.name for p in module.functions]
    used_ports = set(function_ports)
    used_ports.update(module.connected_input_ports)
    # add default ports
    reg = get_module_registry()
    input_ports = set(reg.module_destination_ports_from_descriptor(False, desc))
    input_ports.update(module.input_port_specs)
    for iport in input_ports:
        if iport.defaults:
            used_ports.add(iport.name)
    # This does not work with VTK because ports have already been merged into connections
    kwargs = {}
    for port_name in used_ports:
        kwargs[port_name] = port_name
    kwargs = ', '.join('%s=%s' % (key, value) for key, value in kwargs.iteritems())
    outputs = tuple(module.connected_output_ports)
    if len(outputs) == 0:
        result_str = ''
    elif len(outputs) == 1:
        result_str = outputs[0] + ' = '
    else:
        result_str = ', '.join(outputs) + ' = '
    code += "%s%s%s(%r, %s)" % (result_str,
                                pkg_name,
                                instance,
                                outputs[0] if len(outputs)==1 else outputs,
                                kwargs)
    return Script(code, 'variables', 'variables'), preludes


def combine(ops, name_map):
    """ Build lor loop arguments from a port combination description

        ops is of shape ["cartesian", ["pairwise", "a", "b"], "c"]

        name_map ia a dict mapping from port name to inner/outer names in loop

        This would create:
        legend = ((a, b), c)
        prod = product(izip(a, b), c)

        Then just do:
        "from itertools import izip, product"
        "for %s in %s:" % combine(ops, name_map)
    """
    op = 'izip' if ops[0] == 'pairwise' else 'product'
    legend = []
    prod = []
    for port in ops[1:]:
        if isinstance(port, basestring):
            legend.append(name_map[port][1])
            prod.append(name_map[port][0])
        else:
            l, p = combine(port, name_map)
            legend.append(l)
            prod.append(p)
    if len(legend) > 1:
        legend = '(' + ', '.join(legend) + ')'
        prod = op + '(' + ', '.join(prod) + ')'
    else:
        legend = legend[0]
        prod = prod[0]
    return legend, prod


###############################################################################

import unittest


class TestExport(unittest.TestCase):
    def do_export(self, filename, expected_source):
        import os
        from vistrails.core.db.locator import FileLocator
        from vistrails.core.system import vistrails_root_directory
        from vistrails.core.vistrail.pipeline import Pipeline

        locator = FileLocator(os.path.join(vistrails_root_directory(),
                                           'tests', 'resources',
                                           filename))
        pipeline = locator.load(Pipeline)

        self.assertEqual('\n'.join(write_workflow_to_python(pipeline)) + '\n',
                         expected_source)

    def test_sources(self):
        self.do_export('script_sources.xml', """\
# MODULE 2 org.vistrails.vistrails.basic:Integer
value = 8


# MODULE 0 org.vistrails.vistrails.basic:PythonSource
# FUNCTION i i
i = 42
o = 1
o = i # comment
internal_var = 4


# MODULE 1 org.vistrails.vistrails.basic:PythonSource
# CONNECTION a o
# CONNECTION someint value
try:
    print(o) # note that this will be allowed to collide
except NameError:
    pass
print(o) # Yeah
internal_var_2 = value
""")

    def test_list(self):
        self.do_export('script_list.xml', """\
# MODULE 1 org.vistrails.vistrails.basic:Integer
value = 3


# MODULE 0 org.vistrails.vistrails.basic:List
# FUNCTION value value_3
value_3 = [1, 2]
# FUNCTION tail tail
tail = [4, 5]
# CONNECTION item0 value
value_2 = value_3 + [value] + tail


# MODULE 2 org.vistrails.vistrails.basic:StandardOutput
# CONNECTION value value_2
print value_2
""")

    def test_loop_combined(self):
        self.do_export('export_loop.xml', """\
from itertools import izip, product

# MODULE 26 org.vistrails.vistrails.basic:PythonSource
s1 = ['A', 'B', 'C']
s2 = ['+', '-', '*']
s3 = ['1', '2', '3']


# MODULE 24 org.vistrails.vistrails.basic:ConcatenateString
# CONNECTION str1 s1
# CONNECTION str2 s2
# CONNECTION str3 s3
value = []
for (s1Item, (s2Item, s3Item)) in product(s1, izip(s2, s3)):
    valueItem = s1Item + s2Item + s3Item
    value.append(valueItem)


# MODULE 25 org.vistrails.vistrails.basic:PythonSource
# FUNCTION expected expected
expected = 'A+1A-2A*3B+1B-2B*3C+1C-2C*3'
# CONNECTION s1 value
result = ''.join(value)
assert(result==expected)

""")

    def test_loop_wrap(self):
        self.do_export('export_loop_wrap.xml', """\
# MODULE 30 org.vistrails.vistrails.basic:Integer
value = 1


# MODULE 31 org.vistrails.vistrails.basic:PythonSource
# CONNECTION combine value
combine = [value]
assert(combine == [1])

""")

    def test_loop_append_mixed(self):
        self.do_export('export_loop_append_mixed.xml', """\
# MODULE 20 org.vistrails.vistrails.basic:PythonSource
o = [1,2,3]


# MODULE 19 org.vistrails.vistrails.basic:Integer
value = 5


# MODULE 18 org.vistrails.vistrails.basic:PythonSource
# CONNECTION i value
# CONNECTION i o
i = [value] + o
assert(len(i) == 4)

""")

    def test_loop_cartesian(self):
        self.do_export('export_loop_cartesian.xml', """\
# MODULE 21 org.vistrails.vistrails.basic:PythonSource
s1 = ['A', 'B', 'C']
s2 = ['1', '2', '3']


# MODULE 22 org.vistrails.vistrails.basic:ConcatenateString
# CONNECTION str1 s1
# CONNECTION str2 s2
value = []
for s1Item in s1:
    for s2Item in s2:
        valueItem = s1Item + s2Item
        value.append(valueItem)


# MODULE 23 org.vistrails.vistrails.basic:PythonSource
# FUNCTION expected expected
expected = 'A1A2A3B1B2B3C1C2C3'
# CONNECTION s1 value
result = ''.join(value)
assert(result == expected)
""")

    def test_loop_pairwise(self):
        self.do_export('export_loop_pairwise.xml', """\
from itertools import izip

# MODULE 26 org.vistrails.vistrails.basic:PythonSource
s1 = ['A', 'B', 'C']
s2 = ['1', '2', '3']


# MODULE 24 org.vistrails.vistrails.basic:ConcatenateString
# CONNECTION str2 s2
# CONNECTION str1 s1
value = []
for s1Item, s2Item in izip(s1, s2):
    valueItem = s1Item + s2Item
    value.append(valueItem)


# MODULE 25 org.vistrails.vistrails.basic:PythonSource
# FUNCTION expected expected
expected = 'A1B2C3'
# CONNECTION s1 value
result = ''.join(value)
assert(result == expected)

""")

    def test_loop_cartesian_reversed(self):
        self.do_export('export_loop_cartesian_reversed.xml', """\
from itertools import izip, product

# MODULE 29 org.vistrails.vistrails.basic:PythonSource
s1 = ['A', 'B', 'C']
s2 = ['1', '2', '3']


# MODULE 27 org.vistrails.vistrails.basic:ConcatenateString
# CONNECTION str2 s2
# CONNECTION str1 s1
value = []
for (s2Item, s1Item) in product(s2, s1):
    valueItem = s1Item + s2Item
    value.append(valueItem)


# MODULE 28 org.vistrails.vistrails.basic:PythonSource
# FUNCTION expected expected
expected = 'A1B1C1A2B2C2A3B3C3'
# CONNECTION s1 value
result = ''.join(value)
assert(result == expected)

""")
