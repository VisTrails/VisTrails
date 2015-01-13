from __future__ import division, unicode_literals


def utf8(s):
    if isinstance(s, unicode):
        return s
    elif isinstance(s, str):
        return s.decode('utf-8')
    else:
        raise TypeError("Got %r instead of str or unicode" % type(s))


def indentation(line):
    """Gets the indentation level of a line of code.

    See Python Language Reference, 2.1.8. Indentation:
    https://docs.python.org/2/reference/lexical_analysis.html#indentation
    """
    indent = 0
    for c in line:
        if c == ' ':
            indent += 1
        elif c == '\t':
            indent += 8 - (indent % 8)
        else:
            break
    return indent


def dedent(line, level):
    """De-indent a line by the given level.

    If we end up inside of a tab, too bad.
    """
    rest = line.lstrip()
    full_indent = line[:len(line) - len(rest)]
    target = indentation(full_indent) - level
    indent = 0
    pos = 0
    for pos, c in enumerate(full_indent):
        if c == ' ':
            indent += 1
        elif c == '\t':
            indent += 8 - (indent % 8)
        if indent > target:
            break

    return full_indent[:pos] + rest


###############################################################################

import unittest


class TestUtils(unittest.TestCase):
    def test_indent(self):
        self.assertEqual(indentation('    s'), 4)
        self.assertEqual(indentation('   4'), 3)
        self.assertEqual(indentation('\tt'), 8)
        self.assertEqual(indentation('\t s'), 9)
        self.assertEqual(indentation(' \tneuf'), 8)
        self.assertEqual(indentation('       \ttab'), 8)
        self.assertEqual(indentation('        \t oops'), 17)

    def test_dedent(self):
        self.assertEqual(dedent('    s', 1), '   s')
        self.assertEqual(dedent('\t      t', 4), '\t  t')
        self.assertEqual(dedent('', 7), '')
        self.assertEqual(dedent('    h', 7), 'h')
        self.assertEqual(dedent('\t   r', 3), '\tr')
