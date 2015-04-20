"""Python to pipeline importing logic.

This contains read_workflow_from_python(), which imports a standalone Python
script as a VisTrails pipeline a standalone Python script.
"""

from __future__ import division, unicode_literals

import ast
import redbaron


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
