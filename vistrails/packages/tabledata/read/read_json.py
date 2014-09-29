try:
    import simplejson as json
except ImportError:
    import json

from vistrails.core.modules.vistrails_module import ModuleError

from ..common import TableObject, Table, InternalModuleError


class JSONTable(Table):
    _input_ports = [('file', '(org.vistrails.vistrails.basic:File)')]
    _output_ports = [
            ('column_count', '(org.vistrails.vistrails.basic:Integer)'),
            ('column_names', '(org.vistrails.vistrails.basic:List)'),
            ('value', Table)]

    def compute(self):
        json_file = self.get_input('file').name
        with open(json_file, 'rb') as fp:
            obj = json.load(fp)
        table = self.make_table(obj)
        self.set_output('column_count', table.columns)
        if table.names is not None:
            self.set_output('column_names', table.names)
        self.set_output('value', table)

    @staticmethod
    def add_list(columns, key, value):
        if not isinstance(value, list):
            raise InternalModuleError("Entry for key %r is not a list" % key)
        if key is not None:
            value = [key] + value
        for i, v in enumerate(value):
            columns[i].append(v)

    @staticmethod
    def add_dict(columns, keys, key_set, key, value):
        if not isinstance(value, dict):
            raise InternalModuleError(
                    "Entry for key %r is not an object" % key)
        value_keys = set(value.keys())
        m = key_set - value_keys
        if m:
            raise InternalModuleError(
                    "Entry for key %r is missing field %r" % (
                    key,
                    next(iter(m))))
        m = value_keys - key_set
        if m:
            raise InternalModuleError(
                    "Entry for key %r has unexpected field %r" % (
                    key,
                    next(iter(m))))
        if key is None:
            for i, k in enumerate(keys):
                columns[i].append(value[k])
        else:
            columns[0].append(key)
            for i, k in enumerate(keys):
                columns[i + 1].append(value[k])


class JSONObject(JSONTable):
    """Loads a JSON file and build a table from an object.

    In JSON, an object is written with {}. It is essentially an associative
    array. A column will contain the keys in this array.

    Example:
        {
            "John": {"lastname": "Smith", "age": 25, "city": "New York"},
            "Ashley": {"lastname": "Crofts", "age": 21, "city": "Fort Worth"},
            "Michael": {"lastname": "Buck", "age": 78, "city": "Goodman"}
        }

        key    | lastname | age |    city
        -------+----------+-----+-----------
        John   |  Smith   |  25 | New York
        Ashley |  Crofts  |  21 | Fort Worth
        Michal |  Buck    |  78 | Goodman

    Rows can also be lists (but they still all have to be in the same format).
    In this case, columns will not be named.

    To read a list of rows, use the JSONList module instead.
    """
    _input_ports = [('key_name', '(org.vistrails.vistrails.basic:String)',
                     {'optional': True, 'defaults': repr(["key"])})]

    def make_table(self, obj):
        if not isinstance(obj, dict):
            raise ModuleError(self, "JSON file is not an object")
        key_name = self.get_input('key_name', True)
        iterator = obj.iteritems()
        try:
            first_key, first_value = next(iterator)
        except StopIteration:
            raise ModuleError(self, "No entry in JSON object")
        count = 1
        if isinstance(first_value, list):
            keys = None
            columns = [[] for i in xrange(1 + len(first_value))]
            self.add_list(columns, first_key, first_value)
            for key, value in iterator:
                self.add_list(columns, key, value)
                count += 1
        elif isinstance(first_value, dict):
            keys = first_value.keys()
            key_set = set(keys)
            columns = [[] for i in xrange(1 + len(keys))]
            self.add_dict(columns, keys, key_set, first_key, first_value)
            for key, value in iterator:
                self.add_dict(columns, keys, key_set, key, value)
                count += 1
        else:
            raise ModuleError(self, "Values should be lists or objects")

        if keys is not None:
            names = [key_name] + keys
        else:
            names = None
        return TableObject(columns, count, names)


class JSONList(JSONTable):
    """Loads a JSON file and build a table from a list.

    In JSON, a list is written with [].

    Example:
        [[ 4, 14, 15,  1],
         [ 9,  7,  6, 12],
         [ 5, 11, 10,  8],
         [16,  2,  3, 13]]

        gives a 4x4 unnamed table.
    """
    def make_table(self, obj):
        if not isinstance(obj, list):
            raise ModuleError(self, "JSON file is not a list")
        iterator = iter(obj)
        try:
            first = next(iterator)
        except StopIteration:
            raise ModuleError(self, "No element in JSON list")
        count = 1
        if isinstance(first, list):
            keys = None
            columns = [[] for i in xrange(len(first))]
            self.add_list(columns, None, first)
            for value in iterator:
                self.add_list(columns, None, value)
                count += 1
        elif isinstance(first, dict):
            keys = first.keys()
            key_set = set(keys)
            columns = [[] for i in xrange(len(keys))]
            self.add_dict(columns, keys, key_set, None, first)
            for value in iterator:
                self.add_dict(columns, keys, key_set, None, value)
                count += 1
        else:
            raise ModuleError(self, "Values should be lists or objects")

        return TableObject(columns, count, keys)


_modules = [(JSONTable, {'abstract': True}), JSONObject, JSONList]


###############################################################################

import unittest
from vistrails.tests.utils import execute, intercept_results
from ..identifiers import identifier


class TestJSON(unittest.TestCase):
    def test_object(self):
        """Reads an object with object or list rows.
        """
        json_files = [
            ("""
            {
                "John": {"lastname": "Smith", "age": 25, "city": "New York"},
                "Lara": {"lastname": "Croft", "age": 21, "city": "Nashville"},
                "Michael": {"lastname": "Buck", "age": 78, "city": "Goodman"}
            }
            """, True),
            ("""
            {
                "John": ["Smith", 25, "New York"],
                "Lara": ["Croft", 21, "Nashville"],
                "Michael": ["Buck", 78, "Goodman"]
            }
            """, False),
            ]

        for json_file, has_names in json_files:
            with intercept_results(JSONObject, 'value', 'column_count',
                                   'column_names') as results:
                self.assertFalse(execute([
                        ('WriteFile', 'org.vistrails.vistrails.basic', [
                            ('in_value', [('String', json_file)]),
                        ]),
                        ('read|JSONObject', identifier, []),
                    ],
                    [
                        (0, 'out_value', 1, 'file'),
                    ]))
            self.assertTrue(all((len(r) == 1) for r in results[:2]))
            (table,), (count,), names = results
            self.assertEqual(count, 4)

            import numpy
            if has_names:
                self.assertEqual(names, [table.names])
                self.assertEqual(table.names[0], 'key')
                self.assertEqual(set(table.names[1:]),
                                 set(['lastname', 'age', 'city']))
                f_city = table.names.index('city')
                f_age = table.names.index('age')
            else:
                self.assertEqual(names, [])
                self.assertIsNone(table.names)
                f_city = 3
                f_age = 2
            self.assertEqual(set(table.get_column(f_city)),
                             set(["New York", "Nashville", "Goodman"]))
            l = table.get_column(f_age, True)
            self.assertIsInstance(l, numpy.ndarray)
            self.assertEqual(set(l), set([21, 25, 78]))

    def test_list(self):
        """Reads a list of object or list rows.
        """
        json_files = [
            """
            [
                {"firstname": "John", "lastname": "Smith", "age": 25},
                {"firstname": "Lara", "lastname": "Croft", "age": 21},
                {"firstname": "Michael", "lastname": "Buck", "age": 78}
            ]
            """,
            """
            [[2, 7, 6],
             [9, 5, 1],
             [4, 3, 8]]
            """,
            ]

        for nb, json_file in enumerate(json_files):
            with intercept_results(JSONList, 'value', 'column_count',
                                   'column_names') as results:
                self.assertFalse(execute([
                        ('WriteFile', 'org.vistrails.vistrails.basic', [
                            ('in_value', [('String', json_file)]),
                        ]),
                        ('read|JSONList', identifier, []),
                    ],
                    [
                        (0, 'out_value', 1, 'file'),
                    ]))
            self.assertTrue(all((len(r) == 1) for r in results[:2]))
            (table,), (count,), names = results
            self.assertEqual(count, 3)

            import numpy
            if nb == 0:
                self.assertEqual(names, [table.names])
                self.assertEqual(set(table.names),
                                 set(['firstname', 'lastname', 'age']))
                self.assertEqual(set(table.get_column_by_name('firstname')),
                                 set(["John", "Lara", "Michael"]))
                l = table.get_column_by_name('age', True)
                self.assertIsInstance(l, numpy.ndarray)
                self.assertEqual(set(l), set([21, 25, 78]))
            else:
                self.assertEqual(names, [])
                self.assertIsNone(table.names)
                self.assertEqual([table.get_column(col) for col in xrange(3)],
                                 [[2, 9, 4],
                                  [7, 5, 3],
                                  [6, 1, 8]])
