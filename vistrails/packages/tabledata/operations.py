try:
    import numpy
except ImportError: # pragma: no cover
    numpy = None
import re

from vistrails.core.modules.vistrails_module import ModuleError

from .common import TableObject, Table, choose_column, choose_columns

# FIXME use pandas?


def utf8(obj):
    if isinstance(obj, bytes):
        return obj
    elif isinstance(obj, unicode):
        return obj.encode('utf-8')
    else:
        return bytes(obj)


class JoinedTables(TableObject):
    def __init__(self, left_t, right_t, left_key_col, right_key_col,
                 case_sensitive=False, always_prefix=False):
        self.left_t = left_t
        self.right_t = right_t
        self.left_key_col = left_key_col
        self.right_key_col = right_key_col
        self.case_sensitive = case_sensitive
        self.always_prefix = always_prefix

        self.build_column_names()
        self.compute_row_map()
        self.column_cache = {}
        self.rows = len(self.row_map)

    def build_column_names(self):
        left_name = self.left_t.name
        if left_name is None:
            left_name = "left"
        right_name = self.right_t.name
        if right_name is None:
            right_name = "right"

        def get_col_names(table, other, prefix):
            names = []
            for i in xrange(table.columns):
                should_prefix = self.always_prefix
                if table.names is not None:
                    n = table.names[i]
                else:
                    n = "col %d" % i
                    should_prefix = True
                if not should_prefix and other.names is not None:
                    if n in other.names:
                        should_prefix = True
                names.append("%s%s" % (prefix + "." if should_prefix else "",
                                       n))
            return names

        self.names = (get_col_names(self.left_t, self.right_t, left_name) +
                      get_col_names(self.right_t, self.left_t, right_name))
        self.columns = len(self.names)

    def get_column(self, index, numeric=False):
        if (index, numeric) in self.column_cache:
            return self.column_cache[(index, numeric)]

        result = []
        if index < self.left_t.columns:
            column = self.left_t.get_column(index, numeric)
            for i in xrange(self.left_t.rows):
                if i in self.row_map:
                    result.append(column[i])
        else:
            column = self.right_t.get_column(index - self.left_t.columns,
                                             numeric)
            for i in xrange(self.left_t.rows):
                if i in self.row_map:
                    j = self.row_map[i]
                    result.append(column[j])

        if numeric and numpy is not None:
            result = numpy.array(result, dtype=numpy.float32)
        self.column_cache[(index, numeric)] = result
        return result

    def compute_row_map(self):
        def build_key_dict(table, key_col):
            key_dict = {}
            column = table.get_column(key_col)
            if self.case_sensitive:
                key_dict = dict((utf8(val).strip(), i)
                                for i, val in enumerate(column))
            else:
                key_dict = dict((utf8(val).strip().upper(), i)
                                for i, val in enumerate(column))
            return key_dict

        right_keys = build_key_dict(self.right_t, self.right_key_col)

        self.row_map = {}
        for left_row_idx, key in enumerate(
                self.left_t.get_column(self.left_key_col)):
            key = utf8(key).strip()
            if not self.case_sensitive:
                key = key.upper()
            if key in right_keys:
                self.row_map[left_row_idx] = right_keys[key]


class JoinTables(Table):
    """Joins data from two tables using equality of a pair of columns.

    This creates a table by combining the fields from the two tables. It will
    match the values in the two selected columns (one from each table). If a
    row from one of the table has a value for the selected field that doesn't
    exist in the other table, that row will not appear in the result
    (INNER JOIN semantics).
    """
    _input_ports = [('left_table', 'Table'),
                    ('right_table', 'Table'),
                    ('left_column_idx', 'basic:Integer'),
                    ('left_column_name', 'basic:String'),
                    ('right_column_idx', 'basic:Integer'),
                    ('right_column_name', 'basic:String'),
                    ('case_sensitive', 'basic:Boolean',
                     {"optional": True, "defaults": str(["False"])}),
                    ('always_prefix', 'basic:Boolean',
                     {"optional": True, "defaults": str(["False"])})]
    _output_ports = [('value', 'Table')]

    def compute(self):
        left_t = self.get_input('left_table')
        right_t = self.get_input('right_table')
        case_sensitive = self.get_input('case_sensitive')
        always_prefix = self.get_input('always_prefix')

        def get_column_idx(table, prefix):
            col_name_port = "%s_column_name" % prefix
            col_idx_port = '%s_column_idx' % prefix
            try:
                col_idx = choose_column(
                        table.columns,
                        column_names=table.names,
                        name=self.force_get_input(col_name_port, None),
                        index=self.force_get_input(col_idx_port, None))
            except ValueError, e:
                raise ModuleError(self, e.message)

            return col_idx

        left_key_col = get_column_idx(left_t, "left")
        right_key_col = get_column_idx(right_t, "right")

        table = JoinedTables(left_t, right_t, left_key_col, right_key_col,
                             case_sensitive, always_prefix)
        self.set_output('value', table)


class ProjectedTable(TableObject):
    def __init__(self, table, col_idxs, col_names):
        self.table = table
        self.col_map = dict(enumerate(col_idxs))
        self.columns = len(self.col_map)
        self.names = col_names

    def get_column(self, index, numeric=False):
        mapped_idx = self.col_map[index]
        return self.table.get_column(mapped_idx, numeric)

    @property
    def rows(self):
        return self.table.rows


# FIXME : test coverage for ProjectTable & ProjectedTable
class ProjectTable(Table):
    """Build a table from the columns of another table.

    This allows you to restrict, reorder or rename the columns of a table. You
    can also duplicate columns by mentioning them several times.
    """
    _input_ports = [("table", "Table"),
                    ("column_names", "basic:List"),
                    ("column_indexes", "basic:List"),
                    ("new_column_names", "basic:List",
                     {"optional": True})]
    _output_ports = [("value", "Table")]

    def compute(self):
        table = self.get_input("table")
        indexes = choose_columns(
                table.columns,
                column_names=table.names,
                names=self.force_get_input('column_names', None),
                indexes=self.force_get_input('column_indexes', None))
        if self.has_input('new_column_names'):
            column_names = self.get_input('new_column_names')
            if len(column_names) != len(indexes):
                raise ModuleError(self,
                                  "new_column_names was specified but doesn't "
                                  "have the right number of names")
        else:
            column_names = [table.names[i]
                            for i in indexes]

        projected_table = ProjectedTable(table, indexes, column_names)
        self.set_output("value", projected_table)


class SelectedTable(TableObject):
    @staticmethod
    def make_condition(comparand, comparer):
        if isinstance(comparand, float):
            with_cast = lambda f: lambda v: f(float(v))
        else:
            with_cast = lambda f: f
        if comparer == '==':
            return with_cast(lambda v: v == comparand)
        elif comparer == '!=':
            return with_cast(lambda v: v != comparand)
        elif comparer == '<':
            return with_cast(lambda v: v < comparand)
        elif comparer == '>':
            return with_cast(lambda v: v > comparand)
        elif comparer == '<=':
            return with_cast(lambda v: v <= comparand)
        elif comparer == '>=':
            return with_cast(lambda v: v >= comparand)
        elif comparer == '=~':
            regex = re.compile(comparand)
            return regex.match
        else:
            raise ValueError("Invalid comparison operator %r" % comparer)

    def __init__(self, table, idx, comparer, comparand):
        condition = self.make_condition(comparand, comparer)

        self.table = table
        self.matched_rows = []
        numeric = False
        if type(comparand) == float:
            numeric = True
        column = self.table.get_column(idx, numeric)
        for i, col_val in enumerate(column):
            if condition(col_val):
                self.matched_rows.append(i)

        self.rows = len(self.matched_rows)
        self.names = self.table.names
        self.columns = self.table.columns

    def get_column(self, index, numeric=False):
        col = self.table.get_column(index, numeric)
        return [col[i] for i in self.matched_rows]


# FIXME : test coverage for SelectFromTable & SelectedTable
class SelectFromTable(Table):
    """Builds a table from the rows of another table.

    This allows you to filter the records in a table according to a condition
    on a specific field.
    """
    _input_ports = [('table', 'Table'),
                    ('str_expr', 'basic:String,basic:String,basic:String',
                     {'entry_types': "['default','enum','default']",
                      'values': "[[], ['==', '!=', '=~'], []]"}),
                    ('float_expr', 'basic:String,basic:String,basic:Float',
                     {'entry_types': "['default','enum','default']",
                      'values': "[[], ['==', '!=', '<', '>', '<=', '>='], []]"})]
    _output_ports = [('value', 'Table')]

    def compute(self):
        table = self.get_input('table')

        if self.has_input('str_expr'):
            (col, comparer, val) = self.get_input('str_expr')
        elif self.has_input('float_expr'):
            (col, comparer, val) = self.get_input('float_expr')
        else:
            raise ModuleError(self, "Must have some expression")

        try:
            idx = int(col)
        except ValueError:
            try:
                idx = table.names.index(col)
            except ValueError:
                raise ModuleError(self, "No column %r" % col)

        selected_table = SelectedTable(table, idx, comparer, val)
        self.set_output('value', selected_table)


_modules = [JoinTables, ProjectTable, SelectFromTable]


###############################################################################

import unittest
from vistrails.tests.utils import execute, intercept_result
from .identifiers import identifier


class TestJoin(unittest.TestCase):
    def test_join(self):
        """Test joining tables that have column names.
        """
        with intercept_result(JoinTables, 'value') as results:
            self.assertFalse(execute([
                    ('BuildTable', identifier, [
                        ('id', [('List', repr([1, '2', 4, 5]))]),
                        ('A_name', [('List',
                            repr(['one', 2, 'four', 'five'])),
                        ]),
                    ]),
                    ('BuildTable', identifier, [
                        ('B_age', [('List',
                            repr([14, 50, '12', 22])),
                        ]),
                        ('id', [('List', repr(['1', 2, 3, 5]))]),
                    ]),
                    ('JoinTables', identifier, [
                        ('left_column_idx', [('Integer', '0')]),
                        ('right_column_name', [('String', 'id')]),
                        ('right_column_idx', [('Integer', '1')]),
                    ]),
                ],
                [
                    (0, 'value', 2, 'left_table'),
                    (1, 'value', 2, 'right_table'),
                ],
                add_port_specs=[
                    (0, 'input', 'id',
                     'org.vistrails.vistrails.basic:List'),
                    (0, 'input', 'A_name',
                     'org.vistrails.vistrails.basic:List'),
                    (1, 'input', 'B_age',
                     'org.vistrails.vistrails.basic:List'),
                    (1, 'input', 'id',
                     'org.vistrails.vistrails.basic:List'),
                ]))
        self.assertEqual(len(results), 1)
        table, = results

        self.assertEqual(table.names, ['left.id', 'A_name',
                                       'B_age', 'right.id'])

        self.assertEqual(table.get_column(0, False), [1, '2', 5])
        l = table.get_column(0, True)
        self.assertIsInstance(l, numpy.ndarray)
        self.assertEqual(list(l), [1, 2, 5])
        self.assertEqual(table.get_column(3, False), ['1', 2, 5])
        l = table.get_column(3, True)
        self.assertIsInstance(l, numpy.ndarray)
        self.assertEqual(list(l), [1, 2, 5])

        self.assertEqual(table.get_column(1, False), ['one', 2, 'five'])
        self.assertEqual(list(table.get_column(2, True)), [14, 50, 22])

    def test_noname(self):
        """Tests joining tables that have no column names.
        """
        with intercept_result(JoinTables, 'value') as results:
            self.assertFalse(execute([
                    ('WriteFile', 'org.vistrails.vistrails.basic', [
                        ('in_value', [('String', '1;one\n2;2\n4;four\n'
                                                 '5;five')]),
                    ]),
                    ('read|CSVFile', identifier, [
                        ('delimiter', [('String', ';')]),
                        ('header_present', [('Boolean', 'False')]),
                        ('sniff_header', [('Boolean', 'False')]),
                    ]),
                    ('WriteFile', 'org.vistrails.vistrails.basic', [
                        ('in_value', [('String', '14;1\n50;2\n12;3\n22;5\n')]),
                    ]),
                    ('read|CSVFile', identifier, [
                        ('delimiter', [('String', ';')]),
                        ('header_present', [('Boolean', 'False')]),
                        ('sniff_header', [('Boolean', 'False')]),
                    ]),
                    ('JoinTables', identifier, [
                        ('left_column_idx', [('Integer', '0')]),
                        ('right_column_idx', [('Integer', '1')]),
                    ]),
                ],
                [
                    (0, 'out_value', 1, 'file'),
                    (2, 'out_value', 3, 'file'),
                    (1, 'value', 4, 'left_table'),
                    (3, 'value', 4, 'right_table'),
                ]))
        self.assertEqual(len(results), 1)
        table, = results

        self.assertEqual(table.names, ['left.col 0', 'left.col 1',
                                       'right.col 0', 'right.col 1'])
        self.assertEqual(table.get_column(0, False), ['1', '2', '5'])
        self.assertEqual(table.get_column(1, False), ['one', '2', 'five'])
