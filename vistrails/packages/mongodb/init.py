###############################################################################
##
## Copyright (C) 2014-2016, New York University.
## Copyright (C) 2011-2014, NYU-Poly.
## Copyright (C) 2006-2011, University of Utah.
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

import os
from pymongo import MongoClient

from vistrails.core.modules.vistrails_module import Module


class MongoDatabase(Module):
    """Connects to MongoDB and selects a database.
    """
    _input_ports = [('host', '(basic:String)',
                     {'optional': True, 'defaults': '["localhost"]'}),
                    ('port', '(basic:Integer)',
                     {'optional': True}),
                    ('database', '(basic:String)')]
    _output_ports = [('database', '(MongoDatabase)')]

    def compute(self):
        kwargs = {'host': self.get_input('host')}
        if self.has_input('port'):
            kwargs['port'] = self.get_input('port')
        client = MongoClient(**kwargs)

        database = client.get_database(self.get_input('database'))

        self.set_output('database', database)


# Database operations

class MongoCollection(Module):
    """A single collection in a mongo database.
    """
    _input_ports = [('database', MongoDatabase),
                    ('name', '(basic:String)')]
    _output_ports = [('collection', '(MongoCollection)')]

    def compute(self):
        self.set_output('collection',
                        self.get_input('database')[self.get_input('name')])


class DropCollection(Module):
    """Drops a collection from a MongoDB database.
    """
    _input_ports = [('collection', MongoCollection)]
    _output_ports = [('database', MongoDatabase)]

    def compute(self):
        collection = self.get_input('collection')
        database = collection.database

        collection.drop()

        self.set_output('database', database)


class RenameCollection(Module):
    """Renames a collection in a MongoDB database.
    """
    _input_ports = [('collection', MongoCollection),
                    ('new_name', '(basic:String)')]
    _output_ports = [('collection', MongoCollection),
                     ('database', MongoDatabase)]

    def compute(self):
        collection = self.get_input('collection')
        new_name = self.get_input('new_name')

        collection.rename(new_name)

        self.set_output('collection', collection)
        self.set_output('database', collection.database)


_modules = [MongoDatabase, MongoCollection, DropCollection, RenameCollection]


# Data operations

class BaseCollectionOperation(Module):
    _input_ports = [('collection', MongoCollection)]
    _output_ports = [('collection', MongoCollection)]

    collection_op_out = None

    def compute(self):
        collection = self.get_input('collection')

        out = self.collection_operation(collection)
        if self.collection_op_out is not None:
            self.set_output(self.collection_op_out, out)

        self.set_output('collection', collection)

    def collection_operation(self, collection):
        raise NotImplementedError


_modules.append((BaseCollectionOperation, {'abstract': True}))


def collection_op(input_ports, output=None, doc=None):
    def wrapper(func):
        dct = {'_input_ports': input_ports,
               'collection_operation': func,
               '__doc__': doc}
        if output:
            dct['_output_ports'] = [output]
            dct['collection_op_out'] = output[0]
        _modules.append(type(func.func_name, (BaseCollectionOperation,), dct))
        return func
    return wrapper


@collection_op([('document', '(basic:Dictionary)')],
               doc="Insert a single document into a collection.")
def InsertOne(self, coll):
    coll.insert_one(self.get_input('document'))


@collection_op([('filter', '(basic:Dictionary)'),
                ('document', '(basic:Dictionary)')],
               doc="Replace a single document matching the filter.")
def ReplaceOne(self, coll):
    coll.replace_one(self.get_input('filter'), self.get_input('document'))


@collection_op([('filter', '(basic:Dictionary)'), ('document', '(basic:Dictionary)'),
                ('insert_if_nomatch', '(basic:Boolean)',
                 {'optional': True, 'defaults': ['True']})],
               doc="Update one document matching the selector.")
def UpdateOne(self, coll):
    coll.update_one(self.get_input('filter'),
                    self.get_input('document'),
                    upsert=self.get_input('insert_if_nomatch'))


@collection_op([('filter', '(basic:Dictionary)')],
               doc="Delete a single document matching the filter.")
def DeleteOne(self, coll):
    coll.delete_one(self.get_input('filter'))


@collection_op([('filter', '(basic:Dictionary)')],
               doc="Delete one or more documents matching the filter.")
def DeleteMany(self, coll):
    coll.delete_many(self.get_input('filter'))


@collection_op([('pipeline', '(basic:List)')],
               output=('results', '(basic:List)'),
               doc="Calculate aggregate values for the data in the "
                   "collection.\n"
                   "\n"
                   "The pipeline is a list of operations. See the `aggregation"
                   " pipeline operators <https://docs.mongodb.com/manual/ref"
                   "erence/operator/aggregation-pipeline/>`__ for details.")
def Aggregate(self, coll):
    return list(coll.aggregate(self.get_input('pipeline')))


@collection_op([('filter', '(basic:Dictionary)'),
                ('limit', '(basic:Integer)', {'optional': True})],
               output=('results', '(basic:List)'),
               doc="Query the database.")
def Find(self, coll):
    return list(coll.find(self.get_input('filter'),
                          limit=self.force_get_input('limit', 0)))


@collection_op([('filter', '(basic:Dictionary)')],
               output=('document', '(basic:Dictionary)'),
               doc="Get a single document from the database.")
def FindOne(self, coll):
    return coll.find_one(self.get_input('filter'))


@collection_op([('filter', '(basic:Dictionary)')],
               output=('old_document', '(basic:Dictionary)'),
               doc="Finds a single document and deletes it, returning the "
                   "document.")
def FindOneAndDelete(self, coll):
    return coll.find_one_and_delete(self.get_input('filter'))


@collection_op([('filter', '(basic:Dictionary)'), ('document', '(basic:Dictionary)')],
               output=('old_document', '(basic:Dictionary)'),
               doc="Finds a single document and replaces it, returning the "
                   "old document.")
def FindOneAndReplace(self, coll):
    return coll.find_one_and_replace(self.get_input('filter'),
                                     self.get_input('document'))


@collection_op([('filter', '(basic:Dictionary)'),
                ('update', '(basic:Dictionary)')],
               output=('old_document', '(basic:Dictionary)'),
               doc="Finds a single document and updates it, returning the old "
                   "document.")
def FindOneAndUpdate(self, coll):
    return coll.find_one_and_update(self.get_input('filter'),
                                    self.get_input('update'))


@collection_op([('filter', '(basic:Dictionary)', {'optional': True})],
               output=('count', '(basic:Integer)'),
               doc="Get the number of documents in this collection, "
                   "optionally matching a filter.")
def Count(self, coll):
    return coll.count(self.force_get_input('filter'))


@collection_op([('key', '(basic:String)'), ('filter', '(basic:Dictionary)')],
               output=('results', '(basic:List)'),
               doc="Get a list of distinct values for `key` among all "
                   "documents in this collection, or the ones matching the "
                   "filter.")
def Distinct(self, coll):
    return list(coll.distinct(self.get_input('key'), self.get_input('filter')))


@collection_op([('key', '(basic:List)'), ('condition', '(basic:Dictionary)'),
                ('initial', '(basic:Variant)'), ('reduce', '(basic:String)'),
                ('finalize', '(basic:String)')],
               output=('results', '(basic:List)'),
               doc="Perform a query similar to an SQL *group by* operation.\n"
                   "\n"
                   "Returns an array of grouped items.\n"
                   "\n"
                   "  - `key` is a list of keys to group by.\n"
                   "  - `condition` specifies which documents to consider.\n"
                   "  - `initial` is the initial value of the aggregation "
                   "counter object.\n"
                   "  - `reduce` is the aggregation function as JavaScript.\n"
                   "  - `finalize` is the function to be called on each "
                   "object in the output list.")
def Group(self, coll):
    return list(coll.group(self.get_input('key'), self.get_input('condition'),
                           self.get_input('initial'), self.get_input('reduce'),
                           self.force_get_input('finalize', None)))


@collection_op([('map', '(basic:String)'), ('reduce', '(basic:String)'),
                ('out', '(basic:String)')],
               output=('results', MongoCollection),
               doc="Perform a map/reduce operation on this collection.\n"
                   "\n"
                   "Returns a collection object containing the results of the "
                   "operation.\n"
                   "\n"
                   "  - `map` is the map function as JavaScript.\n"
                   "  - `reduce` is the reduce function as JavaScript.\n"
                   "  - `out` is the output collection name.")
def MapReduce(self, coll):
    return coll.map_reduce(self.get_input('map'), self.get_input('reduce'),
                           self.get_input('out'))


###############################################################################

import unittest


class TestMongoDB(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if 'VISTRAILS_TEST_MONGODB' not in os.environ:
            raise unittest.SkipTest(
                    "MongoDB tests need $VISTRAILS_TEST_MONGODB to point to a "
                    "MongoDB server")
        else:
            uri = os.environ['VISTRAILS_TEST_MONGODB']
            host, port = uri.rsplit(':', 1)
            port = int(port)

            def mock_get_input(self, name):
                if name == 'host':
                    return host
                elif name == 'port':
                    return port
                else:
                    return Module.get_input(self, name)

            MongoDatabase.get_input = mock_get_input
            MongoDatabase.has_input = lambda s, n: True

    @classmethod
    def tearDownClass(cls):
        del MongoDatabase.get_input
        del MongoDatabase.has_input

    def test_example(self):
        """Runs the example vt file.
        """
        from vistrails.tests.utils import run_file

        self.assertFalse(run_file('examples/mongodb.vt'))
