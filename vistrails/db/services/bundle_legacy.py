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
from vistrails.db.services.bundle import Bundle, BundleObj, XMLFileSerializer, \
    XMLAppendSerializer,FileRefSerializer, DirectorySerializer, \
    ZIPSerializer, Manifest, SingleRootBundleObjMapping, MultipleObjMapping, \
    MultipleFileRefMapping
import vistrails.db.versions

class DummyManifest(Manifest):
    def __init__(self, version, dir_path):
        Manifest.__init__(self, version)
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
                    self.add_entry('mashup', fname, fname)
                else:
                    debug.warning("Unkown file, ignoring:", os.path.join(root, fname))

    def save(self):
        # don't actually do anything here since legacy vts have no manifest file
        pass

#FIXME have some way to specify bundleobj mappings and serializers at once?
bundle_obj_maps = \
    {'vistrail':
         SingleRootBundleObjMapping(DBVistrail.vtType, 'vistrail'),
     'log':
         SingleRootBundleObjMapping(DBLog.vtType, 'log'),
     'mashup':
         MultipleObjMapping(DBMashuptrail.vtType,
                            lambda obj: obj.db_name,
                            'mashup'),
     'thumbnail': MultipleFileRefMapping('thumbnail', 'thumbnail'),
     'abstraction': MultipleFileRefMapping('abstraction', 'abstraction'),
     'job': SingleRootBundleObjMapping('job', 'job'),
     }

class LegacyVistrailBundle(Bundle):
    def __init__(self):
        Bundle.__init__(self, bundle_obj_maps, "vistrail")

class LegacyAbstractionFileSerializer(FileRefSerializer):
    def __init__(self):
        FileRefSerializer.__init__(self, 'abstraction')

    def get_obj_id(self, filename):
        return FileRefSerializer.get_obj_id(self, filename)[len('abstraction_'):]

    def get_basename(self, obj):
        return 'abstraction_%s' % obj.id

class LegacyLogXMLSerializer(XMLAppendSerializer):
    def __init__(self):
        XMLAppendSerializer.__init__(self, DBLog.vtType,
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

class LegacyMashupXMLSerializer(XMLFileSerializer):
    def __init__(self):
        XMLFileSerializer.__init__(self, DBMashuptrail.vtType,
                                   "http://www.vistrails.org/mashup.xsd",
                                   "translateMashup",
                                   inner_dir_name="mashups")

    def finish_load(self, b_obj):
        b_obj.obj_type = "mashup"

    def get_obj_id(self, vt_obj):
        return vt_obj.db_name

def add_legacy_serializers(s):
    s.add_serializer("vistrail",
                     XMLFileSerializer(DBVistrail.vtType,
                                       "http://www.vistrails.org/vistrail.xsd",
                                       "translateVistrail",
                                       True, True)),
    s.add_serializer("log", LegacyLogXMLSerializer(), is_lazy=True)
    s.add_serializer("mashup", LegacyMashupXMLSerializer())
    s.add_serializer("thumbnail", FileRefSerializer('thumbnail',
                                                    'thumbs'))
    s.add_serializer("abstraction", LegacyAbstractionFileSerializer())
    s.add_serializer("job", FileRefSerializer('job'))

def add_legacy_bundle_types(s):
    s.register_bundle_type(None, LegacyVistrailBundle)

class LegacyDirSerializer(DirectorySerializer):
    def __init__(self, dir_path, version=None, bundle=None, overwrite=False,
                 *args, **kwargs):
        if version is None:
            #FIXME hard-coded
            version = '1.0.4'
        DirectorySerializer.__init__(self, dir_path, version,
                                     bundle, overwrite,
                                     DummyManifest, *args, **kwargs)
        add_legacy_serializers(self)
        add_legacy_bundle_types(self)

class LegacyZIPSerializer(ZIPSerializer):
    def __init__(self, file_path=None, dir_path=None, version=None, bundle=None,
                 overwrite=False, *args, **kwargs):
        if version is None:
            #FIXME hard-coded
            version = '1.0.4'

        ZIPSerializer.__init__(self, file_path, dir_path, version, bundle,
                            overwrite, DummyManifest,
                               *args, **kwargs)
        add_legacy_serializers(self)
        add_legacy_bundle_types(self)

class TestLegacyBundles(unittest.TestCase):
    def compare_bundles(self, b1, b2):
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

        s1 = None
        s2 = None
        s3 = None
        try:
            s1 = LegacyZIPSerializer(in_fname)
            b1 = s1.load()
            s2 = LegacyZIPSerializer(out_fname, bundle=b1)
            s2.save()
            # FIXME check if file structure matches what we expect
            s3 = LegacyZIPSerializer(out_fname)
            b2 = s3.load()
            self.compare_bundles(b1, b2)
        finally:
            if s1:
                s1.cleanup()
            if s2:
                s2.cleanup()
            if s3:
                s3.cleanup()
            os.unlink(out_fname)

if __name__ == '__main__':
    unittest.main()