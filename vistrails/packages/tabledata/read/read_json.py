###############################################################################
##
## Copyright (C) 2014-2016, New York University.
## Copyright (C) 2013-2014, NYU-Poly.
## All rights reserved.
## Contact: contact@vistrails.org
##
## This file is part of VisTrails.
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are met:
##
##  - Redistributions of source code must retain the above copyright notice,
##    this list of conditions and the following disclaimer.
##  - Redistributions in binary form must reproduce the above copyright
##    notice, this list of conditions and the following disclaimer in the
##    documentation and/or other materials provided with the distribution.
##  - Neither the name of the New York University nor the names of its
##    contributors may be used to endorse or promote products derived from
##    this software without specific prior written permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
## AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
## THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
## PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
## CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
## EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
## PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
## OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
## WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
## OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
## ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
##
###############################################################################

from __future__ import division

try:
    import simplejson as json
except ImportError:
    import json

from .convert import DictToTable, ListToTable


class JSONTable(object):
    def compute(self):
        json_file = self.get_input('file').name
        with open(json_file, 'rb') as fp:
            obj = json.load(fp)

        self.convert_to_table(obj)


class JSONObject(JSONTable, DictToTable):
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
    _input_ports = [('file', '(org.vistrails.vistrails.basic:File)')]


class JSONList(JSONTable, ListToTable):
    """Loads a JSON file and build a table from a list.

    In JSON, a list is written with [].

    Example:
        [[ 4, 14, 15,  1],
         [ 9,  7,  6, 12],
         [ 5, 11, 10,  8],
         [16,  2,  3, 13]]

        gives a 4x4 unnamed table.
    """
    _input_ports = [('file', '(org.vistrails.vistrails.basic:File)')]


_modules = [JSONObject, JSONList]


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
