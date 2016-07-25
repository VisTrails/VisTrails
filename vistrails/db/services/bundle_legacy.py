###############################################################################
##
## Copyright (C) 2014-2015, New York University.
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

import os
import tempfile
import unittest
from vistrails.core import debug
from vistrails.core.system import resource_directory, vistrails_root_directory
from vistrails.db import VistrailsDBException
from vistrails.db.domain import DBVistrail, DBLog, DBWorkflowExec, DBMashuptrail
import vistrails.db.services.bundle as vtbundle
import vistrails.db.versions

class DummyManifest(vtbundle.Manifest):
    def __init__(self, bundle_type='vistrail', bundle_version='1.0.4', dir_path=None):
        vtbundle.Manifest.__init__(self, bundle_type, bundle_version)
        self._dir_path = dir_path

    def load(self):
        for root, dirs, files in os.walk(self._dir_path):
            for fname in files:
                if fname == 'vistrail' and root == self._dir_path:
                    self.add_entry('vistrail', None, 'vistrail')
                elif fname == 'log' and root == self._dir_path:
                    self.add_entry('log', None, 'log')
                elif fname.startswith('abstraction_'):
                    abs_id = fname[len('abstraction_'):]
                    self.add_entry('abstraction', abs_id, fname)
                elif root == os.path.join(self._dir_path, 'thumbs'):
                    self.add_entry('thumbnail', fname, fname)
                elif root == os.path.join(self._dir_path, 'mashups'):
                    self.add_entry('mashuptrail', fname, fname)
                else:
                    debug.warning("Unkown file, ignoring:", os.path.join(root, fname))

    def save(self):
        # don't actually do anything here since legacy vts have no manifest file
        pass

class LegacyAbstractionFileSerializer(vtbundle.FileRefSerializer):
    def __init__(self, mapping):
        vtbundle.FileRefSerializer.__init__(self, mapping)

    def get_obj_id(self, filename):
        return vtbundle.FileRefSerializer.get_obj_id(self, filename)[len('abstraction_'):]

    def get_basename(self, obj):
        return 'abstraction_%s' % obj.id

class LegacyLogXMLSerializer(vtbundle.XMLAppendSerializer):
    def __init__(self, mapping):
        vtbundle.XMLAppendSerializer.__init__(self, mapping,
                                     "http://www.vistrails.org/log.xsd",
                                     "translateLog",
                                              DBWorkflowExec.vtType,
                                              True, True)

    def create_obj(self, inner_obj_list=None):
        if inner_obj_list is not None:
            return DBLog(workflow_execs=inner_obj_list)
        else:
            return DBLog()

    def get_inner_objs(self, vt_obj):
        return vt_obj.db_workflow_execs

    def add_inner_obj(self, vt_obj, inner_obj):
        vt_obj.db_add_workflow_exec(inner_obj)

class LegacyMashupXMLSerializer(vtbundle.XMLFileSerializer):
    def __init__(self, mapping):
        vtbundle.XMLFileSerializer.__init__(self, mapping,
                                   "http://www.vistrails.org/mashup.xsd",
                                   "translateMashup",
                                            inner_dir_name="mashups")

    def finish_load(self, b_obj):
        b_obj.obj_type = "mashup"

    def get_obj_id(self, b_obj):
        return b_obj.obj.db_name

class AbstractionFileRefMapping(vtbundle.MultipleObjMapping):
    def __init__(self, obj_type, attr_name=None, attr_plural_name=None):
        def obj_id_extract_f(obj):
            return os.path.basename(obj)[len('abstraction_'):]
        vtbundle.MultipleObjMapping.__init__(self, obj_type, obj_id_extract_f,
                                             attr_name, attr_plural_name)

def register_bundle_serializers(version):
    # FIXME want to specify serializer at same time--no bobj mapping later
    legacy_bmap = vtbundle.BundleMapping(version, 'vistrail',
                                         [vtbundle.SingleRootBundleObjMapping(
                                           DBVistrail.vtType, 'vistrail'),
                                           vtbundle.SingleRootBundleObjMapping(
                                               DBLog.vtType,
                                               'log'),
                                           vtbundle.MultipleObjMapping(
                                               DBMashuptrail.vtType,
                                               lambda obj: obj.db_name,
                                               'mashup'),
                                           vtbundle.MultipleFileRefMapping(
                                               'thumbnail'),
                                           AbstractionFileRefMapping(
                                               'abstraction'),
                                           vtbundle.SingleRootBundleObjMapping(
                                               'job'),
                                       ])
    vt_dir_serializer = vtbundle.DirectorySerializer(legacy_bmap,
                                                     [vtbundle.XMLFileSerializer(
                                                       legacy_bmap.get_mapping(
                                                           "vistrail"),
                                                       "http://www.vistrails.org/vistrail.xsd",
                                                       "translateVistrail",
                                                       True, True),
                                                       (LegacyLogXMLSerializer(
                                                           legacy_bmap.get_mapping(
                                                               "log")), True),
                                                       LegacyMashupXMLSerializer(
                                                           legacy_bmap.get_mapping(
                                                               "mashuptrail")),
                                                       vtbundle.FileRefSerializer(
                                                           legacy_bmap.get_mapping(
                                                               "thumbnail"),
                                                           'thumbs'),
                                                       LegacyAbstractionFileSerializer(
                                                           legacy_bmap.get_mapping(
                                                               "abstraction"))
                                                   ],
                                                     manifest_cls=DummyManifest)

    vtbundle.register_dir_serializer(vt_dir_serializer)

def unregister_bundle_serializers(version):
    vtbundle.unregister_dir_serializer(bundle_type='vistrail', version=version)

class TestLegacyBundles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        register_bundle_serializers('1.0.4')

    def compare_bundles(self, b1, b2):
        print "B1:", b1.get_items()
        print "B2:", b2.get_items()
        self.assertEqual(len(b1.get_items()), len(b2.get_items()))
        for obj_type, obj_id, obj in b1.get_items():
            obj2 = b2.get_bundle_obj(obj_type, obj_id)
            # not ideal, but fails when trying to compare objs without __eq__
            self.assertEqual(obj.obj.__class__, obj2.obj.__class__)
            # self.assertEqual(str(obj.obj), str(obj2.obj))

    def test_old_vt_zip(self):
        #FIXME need to test abstractions and mashups with this
        in_fname = os.path.join(vistrails_root_directory(),'tests',
                                'resources', 'terminator.vt')
        (h, out_fname) = tempfile.mkstemp(prefix='vtbundle_test', suffix='.zip')
        os.close(h)

        b1 = None
        b2 = None
        b3 = None
        try:
            s = vtbundle.get_serializer("zip_serializer")
            b1 = s.load(in_fname)
            s.save(b1, out_fname)

            # FIXME check if file structure matches what we expect
            b2 = s.load(out_fname)
            self.compare_bundles(b1, b2)
        finally:
            if b1:
                b1.cleanup()
            if b2:
                b2.cleanup()
            if b3:
                b3.cleanup()
            # print "OUT FNAME:", out_fname
            os.unlink(out_fname)

    def test_old_vt_with_mashup(self):
        in_fname = os.path.join(vistrails_root_directory(), 'tests',
                                'resources','jobs.vt')
        b = None
        try:
            b = vtbundle.get_serializer("zip_serializer").load(in_fname)
            bobjs = b.get_bundle_objs('mashuptrail')
            self.assertEquals(len(bobjs), 1)
            self.assertEquals(len(b.mashups), 1)
            self.assertEquals(bobjs[0].id, '80f58f50-57b1-11e5-a1da-000c2960b7d8')
        finally:
            if b:
                b.cleanup()

if __name__ == '__main__':
    unittest.main()