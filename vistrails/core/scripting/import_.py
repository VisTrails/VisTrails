"""Python to pipeline importing logic.

This contains read_workflow_from_python(), which imports a standalone Python
script as a VisTrails pipeline a standalone Python script.
"""

from __future__ import division, unicode_literals

import ast
import redbaron
import urllib2

from vistrails.core.db.action import create_action
from vistrails.core.modules.module_registry import get_module_registry


NUMBER_LITERALS = (redbaron.IntNode, redbaron.FloatNode, redbaron.LongNode,
                   redbaron.OctaNode, redbaron.HexaNode)


def eval_int_literal(node):
    """Takes one of the number literal nodes and returns its value.
    """
    if not isinstance(node, NUMBER_LITERALS):
        raise ValueError
    if isinstance(node, redbaron.IntNode):
        # FIXME: This branch probably shouldn't be required, filed as
        # https://github.com/Psycojoker/redbaron/issues/65
        return node.value
    else:
        return ast.literal_eval(node.value)


def read_workflow_from_python(controller, filename):
    """Imports a Python script as a workflow on the given controller.
    """
    # FIXME: Unicode support?
    with open(filename, 'rb') as f:
        script = redbaron.RedBaron(f.read())
    print ("Got %d-line Python script" % len(script))

    # Remove previous modules
    ops = [('delete', conn)
           for conn in controller.current_pipeline.connection_list]
    ops.extend(('delete', mod)
           for mod in controller.current_pipeline.module_list)

    # Create PythonSource
    md = get_module_registry().get_descriptor_by_name(
            'org.vistrails.vistrails.basic',
            'PythonSource')
    module = controller.create_module_from_descriptor(md)
    source = urllib2.quote(script.dumps())
    function = controller.create_function(module, 'source', [source])
    module.add_function(function)
    ops.append(('add', module))

    action = create_action(ops)
    controller.add_new_action(action, "Imported Python script")
    controller.perform_action(action)
    controller.change_selected_version(action.id)
    return True


###############################################################################

import unittest


class TestImport(unittest.TestCase):
    def test_int_literals(self):
        script = redbaron.RedBaron(
                '1\n'
                '2.0\n'
                '3L\n'
                'def foo(): pass\n'
                '04\n'
                '2+2\n'
                '0x5')
        values = []
        for statement in script:
            if isinstance(statement, NUMBER_LITERALS):
                values.append(eval_int_literal(statement))
            else:
                values.append('skipped')

        self.assertEqual(values, [1, 2.0, 3, 'skipped', 4, 'skipped', 5])
