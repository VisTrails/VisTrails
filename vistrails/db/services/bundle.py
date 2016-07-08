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
##  - Neither the name of the University of Utah nor the names of its 
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

import zipfile

from vistrails.core import debug
import vistrails.core.requirements
from vistrails.core.system import get_elementtree_library
from vistrails.core.utils import Chdir
from vistrails.db import VistrailsDBException
from vistrails.db.domain import DBLog, DBVistrail, DBWorkflowExec,\
                                DBMashuptrail, DBRegistry, DBWorkflow, \
                                DBAbstraction, DBAnnotation
import vistrails.db.versions
from vistrails.db.services.db_utils import MySQLDBConnection, SQLite3Connection

ElementTree = get_elementtree_library()

# We want the structure of the data to be distinct from the
# possible serialization modes.
#
# Bundle: representation of the objects tracked in a bundle
# BundleObjMapping: how to translate from object type to a bundle obj
#   (e.g. things like ids and naming)
# BundleSerializer: how to serialize the entire bundle (e.g. to dir, zip, db)
# BundleObjSerializer: how to serialize a single type of bundle object
# BaseSerializer: determine versions/bundle_type and pass to BundleSerializer

class BundleObj(object):
    """ A serializable object of type obj_type

    """

    def __init__(self, obj, obj_type=None, id=None, changed=False):
        self._obj = obj
        #FIXME deprecate this so we use mappings instead?
        if obj_type is None:
            if hasattr(obj, 'vtType'):
                self.obj_type = obj.vtType
            else:
                raise VistrailsDBException("Must have vtType or specify "
                                           "obj_type.")
        else:
            self.obj_type = obj_type
        self.id = id
        self.changed = changed

    def _get_obj(self):
        return self._obj
    def _set_obj(self, obj):
        self._obj = obj
    obj = property(_get_obj, _set_obj)

class LazyBundleObj(BundleObj):
    def __init__(self, load_f, obj_type, id, changed=False):
        BundleObj.__init__(self, None, obj_type, id, changed)
        self._loaded = False
        self.load_f = load_f

    def _get_obj(self):
        if not self._loaded:
            self._obj = self.load_f().obj
            self._loaded = True
        return self._obj
    def _set_obj(self, obj):
        # if we have object in memory, it's loaded
        self._loaded = True
        self._obj = obj
    obj = property(_get_obj, _set_obj)

class BundleObjDictionary(object):
    """ class for storing objects in a dictionary

    """
    def __init__(self):
        self._objs = {}
        # Which types should have single objects
        self.single_types = set()

    def _translate_args(self, obj):
        """ obj can be a BundleObj, tuple or type.
            Infer and return the (type, id)
        """
        if isinstance(obj, BundleObj):
            obj_type = obj.obj_type
            if obj_type not in self.single_types:
                obj_id = obj.id
            else:
                obj_id = None
        elif isinstance(obj, tuple):
            (obj_type, obj_id) = obj
        else:
            obj_type = obj
            obj_id = None
        return (obj_type, obj_id)

    def set_single_type(self, obj_type, is_single=True):
        if is_single:
            self.single_types.add(obj_type)
        else:
            self.single_types.discard(obj_type)

    def has_entry(self, obj_type, obj_id):
        if obj_type in self._objs:
            return obj_id in self._objs[obj_type]
        return False

    def has_entries(self, obj_type):
        return obj_type in self._objs

    def add_entry(self, obj, value):
        obj_type, obj_id = self._translate_args(obj)
        if self.has_entry(obj_type, obj_id):
            raise VistrailsDBException('Use change_entry to overwrite.')
        
        if obj_type not in self._objs:
            self._objs[obj_type] = {}
        self._objs[obj_type][obj_id] = value

    def remove_entry(self, obj):
        obj_type, obj_id = self._translate_args(obj)
        if not self.has_entry(obj_type, obj_id):
            raise VistrailsDBException('Entry does not exist.')
        del self._objs[obj_type][obj_id]

    def change_entry(self, obj, value):
        # not the most efficient, but that's ok
        BundleObjDictionary.remove_entry(self, obj)
        BundleObjDictionary.add_entry(self, obj, value)
        
    def get_value(self, obj):
        """ get_value(obj: translatable) -> BundleObj
        """
        obj_type, obj_id = self._translate_args(obj)
        if not self.has_entry(obj_type, obj_id):
            raise VistrailsDBException('Entry does not exist.')
        return self._objs[obj_type][obj_id]

    def get_values(self, obj_type):
        """ get_values(obj_type: basestring) -> [BundleObj]
        """
        return self._objs[obj_type].values()

    def get_items(self):
        """ returns all BundleObj:s in bundle as a (type, id, value) list
        """
        return [(k1, k2, v) for k1, k2_dict in self._objs.iteritems()
                for k2, v in k2_dict.iteritems()]

class BundleObjMapping(object):
    def __init__(self, obj_type, create_bundle_obj_f, attr_name=None,
                 attr_plural=False, attr_plural_name=None):
        self.obj_type = obj_type
        self.create_bundle_obj_f = create_bundle_obj_f
        if attr_name is None:
            attr_name = obj_type
        self.attr_name = attr_name
        self.attr_plural = attr_plural
        if attr_plural and attr_plural_name is None:
            attr_plural_name = attr_name + "s"
        self.attr_plural_name = attr_plural_name

class SingleRootBundleObjMapping(BundleObjMapping):
    def __init__(self, obj_type, attr_name=None, attr_plural=False,
                 attr_plural_name=None):
        def create_bundle_obj(obj):
            return BundleObj(obj, obj_type, None)
        BundleObjMapping.__init__(self, obj_type, create_bundle_obj, attr_name,
                                  attr_plural, attr_plural_name)

class MultipleObjMapping(BundleObjMapping):
    def __init__(self, obj_type, obj_id_extract_f, attr_name=None,
                 attr_plural_name=None):
        def create_bundle_obj(obj):
            return BundleObj(obj, obj_type, obj_id_extract_f(obj))
        BundleObjMapping.__init__(self, obj_type, create_bundle_obj, attr_name,
                                  True, attr_plural_name)

class MultipleFileRefMapping(MultipleObjMapping):
    def __init__(self, obj_type, attr_name=None, attr_plural_name=None):
        def obj_id_extract_f(obj):
            return os.path.basename(obj)
        MultipleObjMapping.__init__(self, obj_type, obj_id_extract_f,
                                        attr_name, attr_plural_name)


class BundleMapping(object):
    def __init__(self, version, bundle_type, mappings=[],
                 primary_obj_type=None):
        self._mappings_by_type = {}
        self._mappings_by_name = {}
        self.version = version
        self.bundle_type = bundle_type
        for mapping in mappings:
            self.add_mapping(mapping)
        self.primary_obj_type = primary_obj_type

    def add_mapping(self, mapping):
        self._mappings_by_type[mapping.obj_type] = mapping
        self._mappings_by_name[mapping.attr_name] = mapping
        if mapping.attr_plural_name is not None:
            self._mappings_by_name[mapping.attr_plural_name] = mapping

    def remove_mapping(self, obj_type):
        m = self._mappings_by_type[obj_type]
        del self._mappings_by_type[obj_type]
        del self._mappings_by_name[m.attr_name]
        if m.attr_plural_name in self._mappings_by_name:
            del self._mappings_by_name[m.attr_plural_name]

    def has_mapping(self, obj_type):
        return obj_type in self._mappings_by_type

    def get_mapping(self, obj_type):
        if self.has_mapping(obj_type):
            return self._mappings_by_type[obj_type]
        return None

    def mappings(self):
        return self._mappings_by_type.itervalues()

    def create_bundle_obj(self, obj, obj_type=None):
        if obj_type is None and hasattr(obj, 'vtType'):
            obj_type = obj.vtType
        if obj_type in self._mappings_by_type:
            mapping = self._mappings_by_type[obj_type]
            b_obj = mapping.create_bundle_obj_f(obj)
            return b_obj
        raise VistrailsDBException('Do not know how to create BundleObj for '
                                   'obj "%s", add BundleObjMapping')

    def get_obj_from_bundle(self, bundle, name):
        if name in self._mappings_by_name:
            mapping = self._mappings_by_name[name]
            if mapping.attr_plural_name == name:
                if bundle.has_entries(mapping.obj_type):
                    # return all of them
                    return [bo.obj for bo in bundle.get_values(mapping.obj_type)]
                return []
            else: # have single attr name
                if bundle.has_entry(mapping.obj_type, None):
                    return bundle.get_value((mapping.obj_type, None)).obj
        return None

    def new_bundle(self):
        return Bundle(self)

    def clone(self, version=None, bundle_type=None, primary_obj_type=None):
        if version is None:
            version = self.version
        if bundle_type is None:
            bundle_type = bundle_type
        if primary_obj_type is None:
            primary_obj_type = self.primary_obj_type
        return BundleMapping(version, bundle_type, self.mappings(),
                             primary_obj_type)


class Bundle(BundleObjDictionary):
    """ Assume a bundle contains a set of objects.  If an object is a list
        or dictionary, we serialize these to a directory.
    """
    def __init__(self, mapping):
        BundleObjDictionary.__init__(self)
        self._mapping = mapping
        self._serializer = None
        self._metadata = {}

    @property
    def bundle_type(self):
        return self._mapping.bundle_type

    @property
    def version(self):
        return self._mapping.version

    @property
    def mapping(self):
        return self._mapping

    def add_object(self, obj, obj_type=None):
        if not isinstance(obj, BundleObj):
            # check for BundleObjMapping, raises exception if cannot
            obj = self.mapping.create_bundle_obj(obj, obj_type)
        self.add_entry(obj, obj)

    def remove_object(self, obj, obj_type=None):
        if not isinstance(obj, BundleObj):
            # check for BundleObjMapping
            obj = self.mapping.create_bundle_obj(obj, obj_type)
        self.remove_entry(obj)

    def change_object(self, obj, obj_type=None):
        #FIXME path for LazyBundleObj -> BundleObj change?
        if not isinstance(obj, BundleObj):
            # check for BundleObjMapping
            obj = self.mapping.create_bundle_obj(obj, obj_type)
            raise VistrailsDBException('Can only change BundleObj objects.')
        self.change_entry(obj, obj)

    def add_lazy_object(self, obj):
        if not isinstance(obj, LazyBundleObj):
            raise VistrailsDBException('Can only add LazyBundleObj objects.')
        self.add_entry((obj.obj_type, obj.id), obj)

    def remove_lazy_object(self, obj):
        self.remove_entry(obj)

    def get_bundle_obj(self, obj_type, obj_id=None):
        return self.get_value((obj_type, obj_id))

    def get_bundle_objs(self, obj_type):
        return self.get_values(obj_type)

    def get_object(self, obj_type, obj_id=None):
        return self.get_bundle_obj(obj_type, obj_id).obj

    def get_objects(self, obj_type):
        return [bo.obj for bo in self.get_bundle_objs(obj_type)]

    def get_primary_obj(self):
        return self.get_object(self.mapping.primary_obj_type)

    def get_db_objs(self):
        """ Gets a list containing only the DB* objects in the bundle
        """
        return [obj for t in self._objs.itervalues() for obj in t.itervalues() if hasattr(obj.obj, 'vtType')]

    @property
    def serializer(self):
        return self._serializer

    @serializer.setter
    def serializer(self, s):
        self._serializer = s

    def get_metadata(self, k):
        if k not in self._metadata:
            return None
        return self._metadata[k]

    def set_metadata(self, k, v):
        self._metadata[k] = v

    def cleanup(self):
        if self.serializer is not None:
            self.serializer.cleanup(self)

    def translate(self, new_mapping, translate_map={}):
        new_bundle = Bundle(new_mapping)
        for obj_type, mapping in self.mapping._mappings_by_type.iteritems():
            new_obj_type = obj_type
            create_new_ids = False
            if obj_type in translate_map:
                new_obj_type = translate_map[obj_type]
                if type(new_obj_type) == tuple:
                    new_obj_type, create_new_ids = new_obj_type
            if self.has_entries(obj_type):
                for bobj in self.get_bundle_objs(obj_type):
                    #FIXME need to maintain id here!
                    # need to have some way to preserve ids...
                    # how do we know when to preserve ids?
                    if create_new_ids:
                        new_bundle.add_object(bobj.obj, new_obj_type)
                    else:
                        new_bobj = BundleObj(bobj.obj, new_obj_type, bobj.id)
                        new_bundle.add_object(new_bobj)
        return new_bundle

    def __getattr__(self, item):
        """ Returns the default bundleobj(s) of the specified type or None
        """
        return self._mapping.get_obj_from_bundle(self, item)


class WorkflowBundle(Bundle):
    def __init__(self):
        Bundle.__init__(self)
        self.set_single_type("log")

    def get_primary_obj(self):
        return self.get_object(DBWorkflow.vtType)

class LogBundle(Bundle):
    def __init__(self):
        Bundle.__init__(self)
        self.set_single_type("log")

    def get_primary_obj(self):
        return self.get_object(DBLog.vtType)

class RegistryBundle(Bundle):
    def get_primary_obj(self):
        return self.get_object(DBRegistry.vtType)

class BundleObjSerializer(object):
    def __init__(self, bundle_obj_mapping):
        self.mapping = bundle_obj_mapping

    def load(self, *args, **kwargs):
        raise NotImplementedError("Subclass must implement load.")

    def save(self, *args, **kwargs):
        raise NotImplementedError("Subclass must implement save.")

class BundleSerializer(object):
    def __init__(self, mapping, serializers=[]):
        self._mapping = mapping
        # self._bundle = bundle
        # self._bundle_type_dict = {}
        # _serializers[obj_key][serializer_type] = cls
        self._serializers = {}
        self._lazy_serializers = set()
        self.lazy = True
        for s in serializers:
            lazy = False
            if type(s) == tuple:
                (s, lazy) = s
            self.add_serializer(s, lazy)

    @property
    def bundle_type(self):
        return self._mapping.bundle_type

    @property
    def version(self):
        return self._mapping.version

    @property
    def mapping(self):
        return self._mapping

    # FIXME won't work because the BundleObjMappings require cloned mapping subobjs
    # def clone(self, version=None, mapping=None):
    #     if version is None:
    #         version = self.version
    #     if mapping is None:
    #         mapping = self.mapping.clone()
    #     return self.__class__(version, mapping, self._serializers.itervalues())

    def load(self, *args, **kwargs):
        raise NotImplementedError("Subclass must implement load.")

    def save(self, *args, **kwargs):
        raise NotImplementedError("Subclass must implement save.")

    def cleanup(self):
        pass

    def set_lazy_loading(self, lazy):
        self.lazy = lazy

    def add_serializer(self, serializer, is_lazy=False):
        # no need to separate serializer types (e.g. xml/json)
        # too much complication, just create a new mapping for that
        s_key = serializer.mapping.obj_type
        # print "REGISTERING:", s_key
        if s_key in self._serializers:
            raise VistrailsDBException('Serializer already has object serializer '
                                       'for "%s" registered.' % s_key)
        elif self._mapping.has_mapping(s_key):
            assert self._mapping.get_mapping(s_key) == serializer.mapping
            # raise VistrailsDBException('Mapping already has mapping for "%s" '
            #                            'registered' % s_key)

        self._serializers[s_key] = serializer
        if is_lazy:
            self._lazy_serializers.add(s_key)

    def remove_serializer(self, obj_type):
        if obj_type not in self._serializers:
            raise VistrailsDBException('Serializer does not have object '
                                       'serializer for "%s" registered.' %
                                        obj_type)
        del self._serializers[obj_type]
        # Note that self._mapping still has the object type registered...

    def has_serializer(self, obj_type):
        return obj_type in self._serializers

    def get_serializer(self, obj_type):
        if obj_type not in self._serializers:
            raise VistrailsDBException('Serializer does not have object '
                                       'serializer for "%s" registered.' %
                                        obj_type)
        return self._serializers[obj_type]

    def is_lazy(self, obj_type):
        return obj_type in self._lazy_serializers

    def new_bundle(self):
        return self._mapping.new_bundle()

class FileSerializer(BundleObjSerializer):
    """ Base serializer for DirectorySerializer
        Serializes the contents of a file using a root directory
        and obj.id as file name
    """
    def __init__(self, bundle_obj_mapping, inner_dir_name=None):
        BundleObjSerializer.__init__(self, bundle_obj_mapping)
        self.inner_dir_name = inner_dir_name

    def check_inner_dir(self, filename):
        if self.inner_dir_name:
            full_dir = os.path.dirname(filename)
            if not full_dir.endswith(self.inner_dir_name):
                import traceback
                traceback.print_stack()
                debug.warning('Expected "%s" to live in "%s" subdir.' %
                              (filename, self.inner_dir_name))

    def get_inner_dir(self, rootdir):
        if self.inner_dir_name:
            inner_dir = os.path.join(rootdir, self.inner_dir_name)
            if os.path.exists(inner_dir):
                if not os.path.isdir(inner_dir):
                    raise VistrailsDBException("%s exists and is not a "
                                               "directory" % self.inner_dir_name)
            else:
                os.mkdir(inner_dir)
            return inner_dir
        else:
            return rootdir

    def get_basename(self, obj):
        return obj.id

    def load(self, filename):
        """
        :param filename: Full path to file in bundle
        :return: BundleObj
        """
        if not os.path.exists(filename):
            raise VistrailsDBException('Cannot open file "%s".' % filename)
        with open(filename, 'rb') as f:
            data = f.read()
            b_obj = self.mapping.create_bundle_obj_f(data)
            return b_obj
    
    def save(self, obj, path):
        """
        :param obj: BundleObj
        :param path: full path to write file to
        :return: full path to written file
        """
        with open(path, 'wb') as f:
            f.write(obj.obj)

class FileRefSerializer(FileSerializer):
    """ Serializes the reference to a file using a root directory,
        a inner directory, and obj.id as file name.
    """
    def __init__(self, bundle_obj_mapping, inner_dir_name=None):
        FileSerializer.__init__(self, bundle_obj_mapping, inner_dir_name)

    # def get_obj_id(self, filename):
    #     return os.path.basename(filename)

    def load(self, filename):
        """ Create a BundleObj containing a reference to a file
            If inner dir name is specified, filename must contain it
        """

        #TODO make sure this uses a Ref mapping?
        b_obj = self.mapping.create_bundle_obj_f(filename)
        return b_obj

    def save(self, obj, path):
        """ Saves the referenced file to the new location
        """
        # FIXME check for changed content (e.g. overwrite?)
        if obj.obj != path:
            shutil.copyfile(obj.obj, path)


class XMLFileSerializer(FileSerializer):
    """ Serializes vistrails objects as xml files.
    """
    def __init__(self, bundle_obj_mapping, schema, translator_f,
                 obj_path_as_type=False, do_id_update=False,
                 inner_dir_name=None):
        FileSerializer.__init__(self, bundle_obj_mapping, inner_dir_name)
        self.translator_f = translator_f
        self.xml_tags = {'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
                         'xsi:schemaLocation': schema}
        self.obj_path_as_type = obj_path_as_type

    def load(self, filename):
        self.check_inner_dir(filename)
        tree = ElementTree.parse(filename)
        version = self.get_version_for_xml(tree.getroot())
        daoList = vistrails.db.versions.getVersionDAO(version)
        obj = daoList.open_from_xml(filename, self.mapping.obj_type, tree)
        obj = vistrails.db.versions.translate_object(obj, self.translator_f,
                                                     version)
        b_obj = self.mapping.create_bundle_obj_f(obj)
        # obj_id = self.get_obj_id(obj)
        # b_obj = BundleObj(obj, self.obj_type, obj_id)
        return b_obj

    def save(self, b_obj, path, version=None):
        b_obj = self.save_file(b_obj, path, version)

    def save_file(self, b_obj, file_obj, version=None):
        vt_obj = b_obj.obj
        if version is None:
            version = vistrails.db.versions.currentVersion
        if not hasattr(vt_obj, 'db_version') or not vt_obj.db_version:
            vt_obj.db_version = vistrails.db.versions.currentVersion
        vt_obj = vistrails.db.versions.translate_object(vt_obj,
                                                        self.translator_f,
                                                        vt_obj.db_version,
                                                        version)

        daoList = vistrails.db.versions.getVersionDAO(version)
        daoList.save_to_xml(vt_obj, file_obj, self.xml_tags, version)
        vt_obj = vistrails.db.versions.translate_object(vt_obj,
                                                        self.translator_f,
                                                        version)
        b_obj.obj = vt_obj
        self.finish_save(vt_obj)
        return b_obj

    # @classmethod
    # def load_xml(cls, filename, obj_type, tree):
    #     if tree is None:
    #         tree = ElementTree.parse(filename)
    #     obj = cls.read_xml_object(obj_type, tree.getroot())
    #     return obj
    #
    # @classmethod
    # def read_xml_object(cls, obj_type, node):
    #     raise NotImplementedError("Subclass must implement read_xml_object.")
    #
    # @classmethod
    # def write_xml_object(cls, obj, node=None):
    #     raise NotImplementedError("Subclass must implement write_xml_object.")
    #
    # @classmethod
    # def save_xml(cls, obj, filename, tags, version=None):
    #     """save_to_xml(obj : object, filename: str, tags: dict,
    #                    version: str) -> None
    #
    #     """
    #     root = cls.write_xml_object(obj)
    #     if version is None:
    #         version = my_version
    #     root.set('version', version)
    #     for k, v in tags.iteritems():
    #         root.set(k, v)
    #     tree = ElementTree.ElementTree(root)
    #     self.write_xml_file(filename, tree)

    def get_version_for_xml(self, root):
        version = root.get('version', None)
        if version is not None:
            return version
        msg = "Cannot find version information"
        raise VistrailsDBException(msg)

    def get_basename(self, b_obj):
        """Return the id by default."""
        if not self.mapping.attr_plural:
        # if self.obj_path_as_type:
            return self.mapping.obj_type
        else:
            return self.get_obj_id(b_obj)

    def get_obj_id(self, b_obj):
        if not self.mapping.attr_plural:
        # if self.obj_path_as_type:
            return None
        else:
            return b_obj.id

    def finish_load(self, b_obj):
        if self.do_id_update:
            service_mod = __import__("vistrails.db.services.%s" %
                                     b_obj.obj_type)
            service_mod.update_id_scope(b_obj.obj)

    def finish_save(self, vt_obj):
        pass

# class VistrailXMLSerializer(XMLFileSerializer):
#     """ Serializes the vistrail as 'vistrail'
#     """
#
#     @classmethod
#     def load(cls, filename):
#         obj = super(VistrailXMLSerializer, cls).load(filename,
#                                                      DBVistrail.vtType,
#                                                      "translateVistrail")
#         vistrails.db.services.vistrail.update_id_scope(obj.obj)
#         return obj
#
#     @classmethod
#     def save(cls, obj, rootdir):
#         version = vistrails.db.versions.currentVersion
#         return super(VistrailXMLSerializer, cls).save(obj, rootdir, version,
#                                     "http://www.vistrails.org/vistrail.xsd",
#                                                       "translateVistrail")
#
#     @classmethod
#     def get_obj_id(cls, vt_obj):
#         return None
#
#     @classmethod
#     def get_obj_path(cls, vt_obj):
#         return "vistrail"
#
class WorkflowXMLSerializer(XMLFileSerializer):
    """ Serializes a workflow as an xml file
    """

    def __init__(self, obj_type, schema, translator_f, obj_path_as_type=False,
                 do_id_update=False, inner_dir_name=None):
        WorkflowXMLSerializer.__init__(self,
                                       DBWorkflow.vtType,
                                       "http://www.vistrails.org/workflow.xsd",
                                        "translateWorkflow",
                                       True, True)

#
# class MashupXMLSerializer(XMLFileSerializer):
#     """ Serializes mashuptrails to the 'mashups' folder
#     """
#
#     @classmethod
#     def load(cls, filename):
#         obj = super(MashupXMLSerializer, cls).load(filename,
#                                                   DBMashuptrail.vtType,
#                                                   "translateMashup", "mashups")
#         if obj:
#             # mashuptrail is called 'mashup' in the bundle
#             obj.obj_type = 'mashup'
#         return obj
#
#     @classmethod
#     def save(cls, obj, rootdir):
#         version = vistrails.db.versions.currentVersion
#         return super(MashupXMLSerializer, cls).save(obj, rootdir, version,
#                                     "http://www.vistrails.org/mashup.xsd",
#                                                   "translateMashup",
#                                                   "mashups")
#     @classmethod
#     def get_obj_id(cls, vt_obj):
#         return vt_obj.db_name
#
# class RegistryXMLSerializer(XMLFileSerializer):
#     """ Serializes the registry to a file
#     """
#     @classmethod
#     def load(cls, filename):
#         obj = super(RegistryXMLSerializer, cls).load(filename,
#                                                      DBRegistry.vtType,
#                                                      "translateRegistry")
#         vistrails.db.services.registry.update_id_scope(obj.obj)
#         return obj
#
#     @classmethod
#     def save(cls, obj, filename, version):
#         version = vistrails.db.versions.currentVersion
#         return super(RegistryXMLSerializer, cls).save(cls, obj, filename,
#                                                       version,
#                                     "http://www.vistrails.org/registry.xsd",
#                                                       "translateRegistry")
#
#     @classmethod
#     def get_obj_id(cls, vt_obj):
#         return None
#
#     @classmethod
#     def get_obj_path(cls, vt_obj):
#         return "log"
#
# class StartupXMLSerializer(XMLFileSerializer):
#     """ Serializes preferences to a file
#     """
#     @classmethod
#     def load(cls, filename):
#         obj = super(StartupXMLSerializer, cls).load(filename,
#                                                     DBStartup.vtType,
#                                                     "translateStartup")
#         return obj
#
#     @classmethod
#     def save(cls, obj, filename, version):
#         version = vistrails.db.versions.currentVersion
#         return super(StartupXMLSerializer, cls).save(cls, obj, filename,
#                                                      version,
#                                     "http://www.vistrails.org/startup.xsd",
#                                                      "translateStartup")

class XMLAppendSerializer(XMLFileSerializer):
    """ Serializes files containing xml fragments
    """
    def __init__(self, bundle_obj_mapping, schema, translator_f, inner_obj_type,
                 xml_tag, obj_path_as_type=False, do_id_update=False,
                 inner_dir_name=None):
        XMLFileSerializer.__init__(self, bundle_obj_mapping, schema,
                                   translator_f, obj_path_as_type, do_id_update,
                                   inner_dir_name)
        self.inner_obj_type = inner_obj_type
        self.xml_tag = xml_tag

    def load(self, filename):
        parser = ElementTree.XMLTreeBuilder()
        parser.feed("<%s>\n" % self.xml_tag)
        f = open(filename, "rb")
        parser.feed(f.read())
        parser.feed("</%s>\n" % self.xml_tag)
        root = parser.close()
        obj_list = []
        for node in root:
            version = self.get_version_for_xml(node)
            daoList = vistrails.db.versions.getVersionDAO(version)
            inner_obj = daoList.read_xml_object(self.inner_obj_type, node)
            currentVersion = vistrails.db.versions.currentVersion
            if version != currentVersion:
                # if version is wrong, dump this into a dummy object, 
                # then translate, then get inner_obj back
                vt_obj = self.create_obj()
                vistrails.db.versions.translate_object(vt_obj, self.translator_f,
                                                       currentVersion, version)
                self.add_inner_obj(vt_obj, inner_obj)
                vt_obj = vistrails.db.versions.translate_object(vt_obj, 
                                                                self.translator_f,
                                                                version)
                inner_obj = self.get_inner_objs(vt_obj)[0]
            obj_list.append(inner_obj)
        vt_obj = self.create_obj(obj_list)
        b_obj = self.mapping.create_bundle_obj_f(vt_obj)
        return b_obj

    def save(self, obj, path, version=None):
        """Here, we assume that obj.obj is a **list**"""

        vt_obj = obj.obj
        # FIXME really want version to be whichever version is serializing...
        if version is None:
            version = vistrails.db.versions.currentVersion
        file_obj = open(path, 'ab')
        for inner_obj in self.get_inner_objs(vt_obj):
            cur_id = inner_obj.db_id
            inner_obj.db_id = -1
            inner_bundle_obj = BundleObj(inner_obj, inner_obj.vtType, -1)
            XMLAppendSerializer.save_file(self, inner_bundle_obj,
                                          file_obj, version)
            inner_obj.db_id = cur_id
        vistrails.db.versions.translate_object(vt_obj, self.translator_f, version)

#         if inner_obj_list:
#             return DBLog(workflow_execs=inner_obj_list)
#         return DBLog()
#
#     @classmethod
#     def add_inner_obj(cls, vt_obj, inner_obj):
#         vt_obj.db_add_workflow_exec(inner_obj)
#
#     @classmethod
#     def get_inner_objs(cls, vt_obj):
#         return vt_obj.db_workflow_execs


    def create_obj(self, inner_obj_list=None):
        raise NotImplementedError("Subclass must implement create_obj")

    def add_inner_obj(self, vt_obj, inner_obj):
        raise NotImplementedError("Subclass must implement add_inner_obj")

    def get_inner_objs(self, vt_obj):
        raise NotImplementedError("Subclass must implment get_inner_obj")

# class LogXMLSerializer(XMLAppendSerializer):
#     """ Serializes log as a file containing xml fragments
#     """
#     @classmethod
#     def load(cls, filename):
#         obj = super(LogXMLSerializer, cls).load(filename, DBLog.vtType, 'log',
#                                                 DBWorkflowExec.vtType,
#                                                 "translateLog")
#         vistrails.db.services.log.update_ids(obj.obj)
#         return obj
#
#     @classmethod
#     def save(cls, obj, rootdir):
#         version = vistrails.db.versions.currentVersion
#         return super(LogXMLSerializer, cls).save(obj, rootdir, version,
#                                                  "http://www.vistrails.org/log.xsd",
#                                                  "translateLog")
#
#     @classmethod
#     def get_obj_id(cls, obj):
#         return None
#
#     @classmethod
#     def get_obj_path(cls, vt_obj):
#         return "log"
#
#     @classmethod
#     def create_obj(cls, inner_obj_list=None):
#         if inner_obj_list:
#             return DBLog(workflow_execs=inner_obj_list)
#         return DBLog()
#
#     @classmethod
#     def add_inner_obj(cls, vt_obj, inner_obj):
#         vt_obj.db_add_workflow_exec(inner_obj)
#
#     @classmethod
#     def get_inner_objs(cls, vt_obj):
#         return vt_obj.db_workflow_execs

class DBDataSerializer(BundleObjSerializer):
    SCHEMA = """
    CREATE TABLE blobdata(
        id integer not null primary key auto_increment,
        data mediumblob
    );

    """

    DROP_SCHEMA = """DROP TABLE IF EXISTS blobdata;"""
    
    STMTS = {"load": "SELECT data FROM blobdata WHERE id=%s;",
             "delete": "DELETE FROM blobdata WHERE id=%s;",
             "insert": "INSERT INTO blobdata (data) VALUES (%s);",
             "update": "UPDATE blobdata SET data=%s WHERE id=%s;"}

    @staticmethod
    def load(db_id, connection_obj):
        c = connection_obj.get_connection().cursor()
        c.execute(connection_obj.format_stmt(DBDataSerializer.STMTS["load"]), 
                  (db_id,))
        rows = c.fetchall()
        data = rows[0][0]
        obj = BundleObj(data, 'data')
        return obj

    @staticmethod
    def save(obj, connection_obj):
        import sqlite3
        c = connection_obj.get_connection().cursor()

        c.execute(connection_obj.format_stmt(DBDataSerializer.STMTS["insert"]), 
                  (sqlite3.Binary(obj.obj),))
        db_id = c.lastrowid
        connection_obj.get_connection().commit()
        return db_id

class BaseDBSerializer(DBDataSerializer):
    @classmethod
    def load(cls, db_id, connection_obj, obj_type, translator_f, lock=False, 
             version=None):
        db_connection = connection_obj.get_connection()
        if version is None:
            version = cls.get_db_object_version(db_connection, db_id, obj_type)
        dao_list = vistrails.db.versions.getVersionDAO(version)
        vt_obj = dao_list.open_from_db(db_connection, obj_type, db_id, lock)
        vt_obj = vistrails.db.versions.translate_object(vt_obj, translator_f, 
                                                        version)
        obj_id = cls.get_obj_id(vt_obj)
        obj = BundleObj(vt_obj, obj_type, obj_id)
        return obj

    @classmethod
    def save(cls, obj, connection_obj, translator_f, overwrite=True,
             version=None):
        db_connection = connection_obj.get_connection()
        if version is None:
            version = cls.get_db_version(db_connection)
            if version is None:
                version = vistrails.db.versions.currentVersion

        # if not vt_obj.db_version:
        #     vt_obj.db_version = currentVersion

        vt_obj = obj.obj

        dao_list = vistrails.db.versions.getVersionDAO(version)
        vt_obj = vistrails.db.versions.translate_object(vt_obj, translator_f,
                                                        vt_obj.db_version, 
                                                        version)
        dao_list.save_to_db(db_connection, vt_obj, overwrite)
        vt_obj = vistrails.db.versions.translate_object(vt_obj, version,
                                        vistrails.db.versions.currentVersion)

        cls.finish_save(vt_obj, db_connection, dao_list)
        db_connection.commit()
        return vt_obj.db_id
    
    @staticmethod
    def translate_to_tbl_name(obj_type):
        map = {DBVistrail.vtType: 'vistrail',
               DBWorkflow.vtType: 'workflow',
               DBLog.vtType: 'log_tbl',
               DBRegistry.vtType: 'registry',
               DBAbstraction.vtType: 'abstraction',
               DBMashuptrail.vtType: 'mashuptrail',
               DBAnnotation.vtType: 'annotation',
               }
        return map[obj_type]

    @classmethod
    def get_db_object_version(cls, db_connection, obj_id, obj_type):
        command = """
        SELECT o.version
        FROM %s o
        WHERE o.id = %s
        """

        version = vistrails.db.versions.currentVersion
        try:
            c = db_connection.cursor()
            #print command % (cls.translate_to_tbl_name(obj_type), obj_id)
            c.execute(command % (cls.translate_to_tbl_name(obj_type), obj_id))
            version = c.fetchall()[0][0]
            c.close()
        finally:
            return version

    @staticmethod
    def get_db_version(db_connection):
        command = """
        SELECT `version`
        FROM `vistrails_version`
        """

        try:
            c = db_connection.cursor()
            c.execute(command)
            version = c.fetchall()[0][0]
            c.close()
        finally:
            # just return None if we hit an error
            return None
        return version

    @classmethod
    def get_obj_path(cls, vt_obj):
        """Return the id by default."""
        return cls.get_obj_id(vt_obj)

    @classmethod
    def get_obj_id(cls, vt_obj):
        return vt_obj.id

    @classmethod
    def finish_save(cls, obj, db_connection, dao_list):
        pass

class VistrailDBSerializer(BaseDBSerializer):
    @classmethod
    def load(cls, db_id, connection_obj, lock=False, version=None):
        obj = super(VistrailDBSerializer, cls).load(db_id, connection_obj, 
                                                    DBVistrail.vtType,
                                                    "translateVistrail", lock, 
                                                    version)
        for db_action in obj.obj.db_get_actions():
            db_action.db_operations.sort(key=lambda x: x.db_id)
        vistrails.db.services.vistrail.update_id_scope(obj.obj)
        return obj

    @classmethod
    def save(cls, obj, connection_obj, overwrite=True):
        # current_action holds the current action id 
        # (used by the controller--write_vistrail)
        version = vistrails.db.versions.currentVersion
        vt_obj = obj.obj
        current_action = vt_obj.db_version

        if overwrite and vt_obj.db_last_modified is not None:
            from vistrails.db.services.io import get_db_object_modification_time, \
                                     open_vistrail_from_db

            new_time = get_db_object_modification_time(connection_obj,
                                                       vt_obj.db_id,
                                                       DBVistrail.vtType)
            if new_time > vt_obj.db_last_modified:
                # need synchronization
                old_vistrail = open_vistrail_from_db(connection_obj,
                                                     vt_obj.db_id,
                                                     True, version)
                old_vistrail = vistrails.db.version.translate_vistrail(
                    old_vistrail, version)
                # the "old" one is modified and changes integrated
                current_action = \
                    vistrails.db.services.vistrail.synchronize(old_vistrail, 
                                                               vt_obj, 
                                                               current_action)
                obj.obj = old_vistrail
                obj.obj.db_currentVersion = current_action
        obj.obj.db_last_modified = connection_obj.get_current_time()
        
        db_id = super(VistrailDBSerializer, cls).save(obj, connection_obj, 
                                                      "translateVistrail", 
                                                      overwrite, version)
        return db_id

    @staticmethod
    def get_saved_workflows(vistrail, db_connection):
        """ Returns list of action id:s representing populated workflows.
        """
        if not vistrail.db_id:
            return []
        c = db_connection.cursor()
        c.execute("SELECT parent_id FROM workflow WHERE vistrail_id=%s;", 
                  (vistrail.db_id,))
        ids = [i[0] for i in c.fetchall()]
        c.close()
        return ids

    @classmethod
    def finish_save(cls, vt_obj, db_connection, dao_list):
        # update all missing tagged workflows
        # get saved workflows from db
        workflowIds = cls.get_saved_workflows(vt_obj, db_connection)
        #print "Workflows already saved:", workflowIds
        tagMap = {}
        for annotation in vt_obj.db_actionAnnotations:
            if annotation.db_key == '__tag__':
                tagMap[annotation.db_action_id] = annotation.db_value
        wfToSave = []
        for id, name in tagMap.iteritems():
            if id not in workflowIds:
                #print "creating workflow", vt_obj.db_id, id, name,
                workflow = vistrails.db.services.vistrail.materializeWorkflow(vt_obj, id)
                workflow.db_id = None
                workflow.db_vistrail_id = vt_obj.db_id
                workflow.db_parent_id = id
                workflow.db_group = id
                workflow.db_last_modified = \
                                    vt_obj.db_get_action_by_id(id).db_date
                workflow.db_name = name
                wfToSave.append(workflow)
        if wfToSave:
            dao_list.save_many_to_db(db_connection, wfToSave, True)
        # vt_obj.db_currentVersion = current_action

class WorkflowDBSerializer(BaseDBSerializer):
    @classmethod
    def load(cls, db_id, connection_obj):
        pass

class Manifest(BundleObjDictionary):
    """ Contains a dictionary of objects contained in the bundle
    """
    def __init__(self, bundle_type=None, bundle_version=None):
        BundleObjDictionary.__init__(self)
        self.bundle_version = bundle_version
        self.bundle_type = bundle_type

    def add_entry(self, obj_type, obj_id, value):
        if not obj_id:
            obj_id = None
        BundleObjDictionary.add_entry(self, (obj_type, obj_id), value)

    def remove_entry(self, obj_type, obj_id=None):
        BundleObjDictionary.remove_entry(self, (obj_type, obj_id))

    def change_entry(self, obj_type, obj_id, value):
        BundleObjDictionary.change_entry(self, (obj_type, obj_id), value)

    def get_value(self, obj_type, obj_id=None):
        return BundleObjDictionary.get_value(self, (obj_type, obj_id))

    def get_items(self, allow_none=False):
        if allow_none:
            return BundleObjDictionary.get_items(self)
        return [(i1, i2 if i2 else "", i3)
                for (i1, i2, i3) in BundleObjDictionary.get_items(self)]

class FileManifest(Manifest):
    """ Stores manifest as a tab-separated file
    """

    def __init__(self, bundle_type=None, bundle_version=None, dir_path=None):
        Manifest.__init__(self, bundle_type, bundle_version)
        self._fname = os.path.join(dir_path, "MANIFEST")

    def load(self):
        with open(self._fname, 'rU') as f:
            header = f.next()
            header_arr = header.split('\t')
            if header_arr[0].strip() != "VTBUNDLE":
                raise VistrailsDBException("Not a VisTrails bundle")
            if len(header_arr) > 1 and header_arr[1].strip() != "":
                self.bundle_version = header_arr[1].strip()
            if len(header_arr) > 2 and header_arr[2].strip() != "":
                self.bundle_type = header_arr[2].strip()
            for line in f:
                args = line.strip().split('\t')
                self.add_entry(*args)
    
    def save(self):
        with open(self._fname, 'w') as f:
            print >>f, "VTBUNDLE\t" + self.bundle_version + "\t" + self.bundle_type
            for obj_type, obj_id, fname in sorted(self.get_items()):
                print >>f, obj_type + "\t" + obj_id + "\t" + fname

class DummyManifest(Manifest):
    """Used when we don't have a manifest. Assume a legacy structure."""
    def __init__(self, bundle_type='vistrail', bundle_version='1.0.4', dir_path=None):
        Manifest.__init__(self, bundle_type, bundle_version)
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

class BundleMetadata(dict):
    pass

class BaseSerializer(object):
    def __init__(self):
        self._serializers = {}

    def register_serializer(self, s):
        # print "REGISTERING", s, bundle_type, version
        self._serializers[(s.bundle_type, s.version)] = s

    def unregister_serializer(self, bundle_type, version):
        del self._serializers[(bundle_type, version)]

    def get_serializer(self, bundle_type, version):
        if (bundle_type, version) not in self._serializers:
            raise ValueError('Version "%s" of bundle type "%s" not found.' %
                             (version, bundle_type))
        return self._serializers[(bundle_type, version)]

    def copy_serializers(self, other):
        """Copy serializers from other to self"""
        for s in other._serializers.itervalues():
            self.register_serializer(s)

    def new_bundle(self, bundle_type, version):
        return self.get_serializer(bundle_type, version).new_bundle()

    # def load_manifest(self, *args, **kwargs):
    #     raise NotImplementedError("Subclass must implement load_manifest.")
    # def save_manifest(self, *args, **kwargs):
    #     raise NotImplementedError("Subclass must implement save_manifest.")
    def load(self, *wargs, **kwargs):
        raise NotImplementedError("Subclass must implement load.")
    def save(self, *args, **kwargs):
        raise NotImplementedError("Subclass must implement save.")

class DirectoryBaseSerializer(BaseSerializer):
    """ Serializes manifest and bundle objects to a directory

    """
    def __init__(self):
        BaseSerializer.__init__(self)

    def load_manifest(self, manifest_cls, dir_path):
        manifest = manifest_cls(dir_path=dir_path)
        manifest.load()
        return manifest

    def save_manifest(self, manifest, dir_path, all_files):
        manifest.save()

        # remove files not in MANIFEST
        # FIXME looks like this would not remove abstraction/vistrail if
        # vistrail also existed
        manifest_files = [i[2] for i in manifest.get_items()]
        manifest_files.append('MANIFEST')
        if not dir_path.endswith(os.sep):
            dir_path = dir_path + os.sep
        else:
            dir_path = dir_path
        for f in all_files:
            if f[len(dir_path):] not in manifest_files:
                os.unlink(f)

    def load(self, dir_path):
        # allow manifests to be parsed diff. after serializer is identified
        manifest_fname = os.path.join(dir_path, "MANIFEST")
        if os.path.exists(manifest_fname):
            manifest = FileManifest(dir_path=dir_path)
        else:
            manifest = DummyManifest(dir_path=dir_path)
        manifest.load()
        s = self.get_serializer(manifest.bundle_type, manifest.bundle_version)
        manifest = self.load_manifest(s.manifest_cls, dir_path)
        bundle = s.load(dir_path, manifest)
        bundle.serializer = self
        return bundle

    def save(self, bundle, dir_path, overwrite=False):
        all_files = []
        if os.path.exists(dir_path):
            if os.path.isdir(dir_path):
                if not overwrite:
                    raise VistrailsDBException('Directory "%s" already '
                                               'exists and overwrite is '
                                               'off.' % dir_path)
                for path, subdirs, fnames in os.walk(dir_path):
                    all_files.extend(os.path.join(path, fname)
                                     for fname in fnames)
            elif not overwrite:
                raise VistrailsDBException('Directory "%s" already '
                                           'exists and overwrite is '
                                           'off.' % dir_path)
            else:
                os.unlink(dir_path)
        else:
            parent_dir = os.path.dirname(dir_path)
            if not os.path.exists(parent_dir) or not os.path.isdir(parent_dir):
                raise VistrailsDBException('Parent directory "%s" does not '
                                           'exist.' % parent_dir)
            os.mkdir(dir_path)

        s = self.get_serializer(bundle.bundle_type,
                                bundle.version)
        manifest = s.manifest_cls(bundle.bundle_type, bundle.version, dir_path)
        s.save(bundle, dir_path, manifest)
        self.save_manifest(manifest, dir_path, all_files)
        bundle.serializer = self

    def cleanup(self, bundle):
        pass

class DirectorySerializer(BundleSerializer):
    def __init__(self, mapping=None, serializers=[],
                 manifest_cls=FileManifest):
        BundleSerializer.__init__(self, mapping, serializers)
        self.manifest_cls = manifest_cls
        self.add_default_serializers()

    def add_default_serializers(self):
        for m in self.mapping.mappings():
            if not self.has_serializer(m.obj_type):
                if isinstance(m, SingleRootBundleObjMapping):
                    s = FileRefSerializer(m)
                elif isinstance(m, MultipleFileRefMapping):
                    s = FileRefSerializer(m, m.attr_plural_name)
                self.add_serializer(s)

    def load(self, dir_path, manifest):
        assert self.mapping.bundle_type == manifest.bundle_type
        bundle = self.new_bundle()

        for obj_type, obj_id, fname in manifest.get_items(allow_none=True):
            serializer = self.get_serializer(obj_type)
            path = os.path.join(dir_path, serializer.inner_dir_name or '',
                                fname)
            serializer.check_inner_dir(path)
            if self.lazy and self.is_lazy(obj_type):
                # For lazy, must have obj type and id correct
                lazy_obj = LazyBundleObj(lambda s=serializer,p=path: s.load(p),
                                         obj_type, obj_id)
                bundle.add_lazy_object(lazy_obj)
            else:
                obj = serializer.load(path)
                if obj is not None:
                    #FIXME test/assert that what serializer loads matches manifest
                    if obj.id is None:
                        obj.id = obj_id
                    if obj.obj_type is None:
                        obj.obj_type = obj_type
                    bundle.add_object(obj)
        #TODO assert that what was loaded matches the manifest?
        bundle.set_metadata("dir_path", dir_path)
        return bundle

    def save(self, bundle, dir_path, manifest):
        for obj_type, obj_id, bundle_obj in bundle.get_items():
            try:
                serializer = self.get_serializer(obj_type)
                # FIXME need to fix this...
                fname = serializer.get_basename(bundle_obj)
                path = os.path.join(serializer.get_inner_dir(dir_path),
                                    fname)
                serializer.save(bundle_obj, path)
                manifest.add_entry(obj_type, obj_id, fname)
            except VistrailsDBException:
                # cannot serialize object
                debug.warning('Cannot serialize object(s) of type "%s"' % \
                              obj_type)
        bundle.set_metadata("dir_path", dir_path)

class ZIPBaseSerializer(DirectoryBaseSerializer):
    """ a zipped version of a directory bundle
    """

    def load(self, file_path):
        # have path and temp dir
        #
        # first unzip it to a temporary directory and then
        # treat it like a directory bundle

        dir_path = tempfile.mkdtemp(prefix='vt_save')

        z = zipfile.ZipFile(file_path)
        try:
            z.extractall(dir_path)
        finally:
            z.close()

        bundle = super(ZIPBaseSerializer,self).load(dir_path)
        bundle.set_metadata("zip_fname", file_path)
        return bundle

    def save(self, bundle, file_path):
        # first save everything to a temporary directory as a
        # directory bundle and then zip it

        dir_path = bundle.get_metadata("dir_path")
        zip_fname = bundle.get_metadata("zip_fname")
        old_dir_path = None
        if (zip_fname is not None and
                    dir_path is not None and
                    os.path.abspath(file_path) != os.path.abspath(zip_fname)):
            # make sure we generate a new dir_path
            # we will clean up the old dir_path
            # !!! save as needs to be aware of this !!!
            # cannot do this here due to lazy loads
            old_dir_path = dir_path
            dir_path = None
        if dir_path is None:
            dir_path = tempfile.mkdtemp(prefix='vt_save')
            bundle.set_metadata("dir_path", dir_path)
        # FIXME should we overwrite?
        super(ZIPBaseSerializer, self).save(bundle, dir_path, overwrite=True)

        tmp_zip_dir = tempfile.mkdtemp(prefix='vt_zip')
        tmp_zip_file = os.path.join(tmp_zip_dir, "vt.zip")
        output = []
        rel_vt_save_dir = os.path.split(dir_path)[1]

        z = zipfile.ZipFile(tmp_zip_file, 'w')
        try:
            with Chdir(dir_path):
                # zip current directory
                for root, dirs, files in os.walk('.'):
                    for f in files:
                        z.write(os.path.join(root, f))
            z.close()
            shutil.copyfile(tmp_zip_file, file_path)
        finally:
            os.unlink(tmp_zip_file)
            os.rmdir(tmp_zip_dir)
            if old_dir_path is not None:
                shutil.rmtree(old_dir_path)
            bundle.set_metadata("zip_fname", file_path)

    def cleanup(self, bundle):
        dir_path = bundle.get_metadata("dir_path")
        if dir_path is not None:
            shutil.rmtree(dir_path)


class DBManifest(Manifest):
    SCHEMA = """
    CREATE TABLE manifest(
        bundle_id int not null,
        bundle_version char(15),
        obj_type varchar(255),
        obj_id varchar(255),
        db_id int not null,
        PRIMARY KEY (bundle_id, obj_type, obj_id)
    );

    """
    #  engine=InnoDB;
    DROP_SCHEMA = """DROP TABLE IF EXISTS manifest;"""

    STMTS = {"get_version": ("SELECT bundle_version FROM manifest "
                             "WHERE bundle_id=%s LIMIT 1;"),
             "load": ("SELECT obj_type, obj_id, db_id FROM manifest "
                      "WHERE bundle_id=%s;"),
             "delete": "DELETE FROM manifest WHERE bundle_id=%s;",
             "insert": ("INSERT INTO manifest (bundle_id, "
                        "bundle_version, obj_type, obj_id, db_id) "
                        "VALUES (%s, %s, %s, %s, %s);")}

    def __init__(self, connection_obj, version=None, bundle_id=None):
        Manifest.__init__(self, version)
        self._connection_obj = connection_obj
        self._bundle_id = bundle_id
        self._obj_db_ids = BundleObjDictionary()

    def set_bundle_id(self, bundle_id):
        self._bundle_id = bundle_id

    def load(self):
        c = self._connection_obj.get_connection().cursor()
        c.execute(self._connection_obj.format_stmt(self.STMTS["get_version"]),
                  (self._bundle_id,))
        self.version = c.fetchone()[0]
        c.execute(self._connection_obj.format_stmt(self.STMTS["load"]), 
                  (self._bundle_id,))
        rows = c.fetchall()
        for row in rows:
            self.add_entry(*row)

    def save(self):
        c = self._connection_obj.get_connection().cursor()
        c.execute(self._connection_obj.format_stmt(self.STMTS["delete"]), 
                  (self._bundle_id,))
        c.executemany(self._connection_obj.format_stmt(self.STMTS["insert"]),
                      [(self._bundle_id, self.version) + item
                       for item in sorted(self.get_items())])

class DBSerializer(BundleSerializer):
    SCHEMA = """
    CREATE TABLE bundle(
        id integer not null primary key auto_increment,
        name varchar(1023)
    );

    """

    DROP_SCHEMA = """DROP TABLE IF EXISTS bundle;"""
    
    STMTS = {"load": "SELECT name FROM bundle WHERE id=%s;",
             "delete": "DELETE FROM bundle WHERE id=%s;",
             "insert": "INSERT INTO bundle (name) VALUES (%s);",
             "update": "UPDATE bundle SET name=%s WHERE id=%s;"}

    def __init__(self, connection_obj, version=None, bundle_id=None, name="", bundle=None,
                 overwrite=False, *args, **kwargs):
        BundleSerializer.__init__(self, version, bundle, *args, **kwargs)
        self._connection_obj = connection_obj
        self._name = name
        self._bundle_id = bundle_id
        self._manifest = None
        self._overwrite = overwrite

    def create_manifest(self, connection_obj=None, bundle_id=None):
        if connection_obj is None:
            connection_obj = self._connection_obj
        self._manifest = DBManifest(connection_obj, self.version, bundle_id)

    def load_manifest(self, connection_obj=None, bundle_id=None):
        self.create_manifest(connection_obj, bundle_id)
        self._manifest.load()

    def load(self, connection_obj=None, bundle_id=None):
        if connection_obj is None:
            connection_obj = self._connection_obj
        if bundle_id is None:
            bundle_id = self._bundle_id
        if self._bundle is None:
            self._bundle = self._bundle_cls()
        self.load_manifest(connection_obj, bundle_id)

        c = connection_obj.get_connection().cursor()
        c.execute(connection_obj.format_stmt(self.STMTS["load"]), (bundle_id,))
        rows = c.fetchall()
        self._name = rows[0][0]

        for obj_type, obj_id, db_id in self._manifest.get_items(allow_none=True):
            serializer = self.get_serializer(obj_type, 
                                        DBDataSerializer.get_serializer_type())
            if self.lazy and self.is_lazy(obj_type,
                                          DBDataSerializer.get_serializer_type()):
                # For lazy, must have obj type and id correct
                lazy_obj = LazyBundleObj(lambda s=serializer,i=db_id,c=connection_obj: s.load(i,c),
                                         obj_type, obj_id)
                self._bundle.add_lazy_object(lazy_obj)
            else:
                obj = serializer.load(db_id, connection_obj)
                if obj is not None:
                    if obj.id is None:
                        obj.id = obj_id
                    if obj.obj_type is None:
                        obj.obj_type = obj_type
                    self._bundle.add_object(obj)

        self._bundle.serializer = self
        return self._bundle

    def save(self, connection_obj=None, bundle_id=None, name=None,
             overwrite=None):
        if connection_obj is None:
            connection_obj = self._connection_obj
        if bundle_id is None:
            bundle_id = self._bundle_id
        if name is None:
            name = self._name
        if overwrite is None:
            overwrite = self._overwrite
        
        if self._manifest is None:
            self.create_manifest(connection_obj, bundle_id)
        all_objs = []
        for obj_type, obj_id, obj in self._bundle.get_items():
            try:
                serializer = self.get_serializer(obj_type, 
                                    DBDataSerializer.get_serializer_type())
                db_id = serializer.save(obj, connection_obj)
                self._manifest.add_entry(obj_type, obj_id, db_id)
            except VistrailsDBException, e:
                import traceback
                traceback.print_exc()
                # cannot serialize object
                print 'cannot serialize obj', obj_type
                debug.warning('Cannot serialize object(s) of type "%s"' % \
                              obj_type)
        c = connection_obj.get_connection().cursor()
        if self._bundle_id is None:
            c.execute(connection_obj.format_stmt(self.STMTS['insert']),
                      (self._name,))
            self._bundle_id = c.lastrowid
            self._manifest.set_bundle_id(self._bundle_id)
        else:
            c.execute(connection_obj.format_stmt(self.STMTS['update']), 
                      (self._name,))
        self._manifest.save()
        connection_obj.get_connection().commit()
        self._bundle.serializer = self

# GLOBALS

bundle_mappings = {}
dir_serializer = DirectoryBaseSerializer()
zip_serializer = ZIPBaseSerializer()

def register_bundle_mapping(bmap):
    #FIXME handle case where already exists, for now, clobber
    if (bmap.bundle_type, bmap.version) not in bundle_mappings:
        pass
    bundle_mappings[(bmap.bundle_type, bmap.version)] = bmap

def unregister_bundle_mapping(bmap=None, bundle_type=None, version=None):
    if bmap is not None:
        bundle_type = bmap.bundle_type
        version = bmap.version
    if bundle_type is None or version is None:
        raise TypeError("Either bmap or the (bundle_type and version) arguments"
                        " must be passed.")
    del bundle_mappings[(bundle_type, version)]
    #TODO add checks on the serializers

def get_bundle_mapping(bundle_type='vistrail', version=None):
    if version is None:
        version = vistrails.db.versions.currentVersion
    if (bundle_type, version) not in bundle_mappings:
        raise ValueError('Mapping for bersion "%s" of bundle type "%s" '
                         'not found.' % (version, bundle_type))
    return bundle_mappings[(bundle_type, version)]

def new_bundle(bundle_type='vistrail', version=None):
    return get_bundle_mapping(bundle_type, version).new_bundle()

def register_dir_serializer(s, also_zip=True):
    dir_serializer.register_serializer(s)
    if also_zip:
        zip_serializer.register_serializer(s)
    register_bundle_mapping(s.mapping)

def register_zip_serializer(s, also_dir=False):
    zip_serializer.register_serializer(s)
    if also_dir:
        dir_serializer.register_serializer(s)
    register_bundle_mapping(s.mapping)

def unregister_dir_serializer(s=None, bundle_type=None, version=None,
                              also_zip=True):
    if s is not None:
        bundle_type = s.bundle_type
        version = s.version
    if bundle_type is None or version is None:
        raise TypeError("Either s or the (bundle_type and version) arguments"
                        " must be passed.")
    dir_serializer.unregister_serializer(bundle_type, version)
    if also_zip:
        zip_serializer.unregister_serializer(bundle_type, version)

def unregister_zip_serializer(s=None, bundle_type=None, version=None,
                              also_dir=False):
    if s is not None:
        bundle_type = s.bundle_type
        version = s.version
    if bundle_type is None or version is None:
        raise TypeError("Either s or the (bundle_type and version) arguments"
                        " must be passed.")
    zip_serializer.unregister_serializer(bundle_type, version)
    if also_dir:
        dir_serializer.unregister_serializer(bundle_type, version)

import unittest
import os
import shutil
import tempfile

class DatabaseTest(object):
    def __init__(self):
        self.connection_obj = None

    def setup(self):
        pass

    def cleanup(self):
        pass

class MySQLDatabaseTest(DatabaseTest):
    def setup(self):
        create_cmd = "CREATE DATABASE `vt_test`;"
        use_cmd = "USE `vt_test`;"

        db_config = {'host': 'localhost',
                     'port': 3306,
                     'user': 'vt_test',
                     }

        self.connection_obj = MySQLDBConnection(**db_config)
        c = self.connection_obj.get_connection().cursor()
        c.execute(create_cmd)
        c.execute(use_cmd)
        return self.connection_obj

    def cleanup(self):
        drop_cmd = "DROP DATABASE IF EXISTS `vt_test`;"

        c = self.connection_obj.get_connection().cursor()            
        c.execute(drop_cmd);
        self.connection_obj.close()

class SQLite3DatabaseTest(DatabaseTest):
    def setup(self):
        (h, self.fname) = \
                    tempfile.mkstemp(prefix='vt_test_db', suffix='.db')
        os.close(h)
        self.connection_obj = SQLite3Connection(self.fname)
        return self.connection_obj

    def cleanup(self):
        self.connection_obj.close()
        os.unlink(self.fname)

from vistrails.core.system import resource_directory, vistrails_root_directory

class TestBundles(unittest.TestCase):

    def register_vt_serializer(self):
        #FIXME want to specify serializer at same time--no bobj mapping later
        bmap = BundleMapping('0.0.0', 'vistrail',
                             [SingleRootBundleObjMapping(
                                 DBVistrail.vtType, 'vistrail'),
                                 SingleRootBundleObjMapping(DBLog.vtType,
                                                            'log'),
                                 SingleRootBundleObjMapping(
                                     DBRegistry.vtType, 'registry'),
                                 MultipleObjMapping(DBMashuptrail.vtType,
                                                    lambda obj: obj.db_name,
                                                    'mashup'),
                                 MultipleFileRefMapping('thumbnail'),
                                 MultipleFileRefMapping('abstraction'),
                                 SingleRootBundleObjMapping('job'),
                                 MultipleFileRefMapping('data'),
                             ])

        class LogXMLSerializer(XMLAppendSerializer):
            def __init__(self, mapping):
                XMLAppendSerializer.__init__(self, mapping,
                                             "http://www.vistrails.org/log.xsd",
                                             "translateLog",
                                             DBWorkflowExec.vtType,
                                             'log',
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

        class MashupXMLSerializer(XMLFileSerializer):
            def __init__(self, mapping):
                XMLFileSerializer.__init__(self, mapping,
                                           "http://www.vistrails.org/mashup.xsd",
                                           "translateMashup",
                                           inner_dir_name="mashups")

            def finish_load(self, b_obj):
                b_obj.obj_type = "mashup"

            def get_obj_id(self, b_obj):
                return b_obj.obj.db_name


        vt_dir_serializer = DirectorySerializer(bmap,
                                            [XMLFileSerializer(
                                                 bmap.get_mapping("vistrail"),
                                                 "http://www.vistrails.org/vistrail.xsd",
                                                 "translateVistrail",
                                                 True, True),
                                             (LogXMLSerializer(
                                                 bmap.get_mapping("log")), True),
                                             MashupXMLSerializer(
                                                 bmap.get_mapping("mashuptrail"))])

        register_dir_serializer(vt_dir_serializer)

    def unregister_vt_serializer(self):
        unregister_dir_serializer(bundle_type='vistrail', version='0.0.0')

    # # add_file_serializers(bmap, vt_dir_serializer)
    # base_dir_serializer.register_serializer(vt_dir_serializer)
    # base_zip_serializer = ZIPBaseSerializer()
    # base_zip_serializer.copy_serializers(base_dir_serializer)

    class VistrailsDBSerializer(DBSerializer):
        def __init__(self, connection_obj, version=None, bundle_id=None, name="",
                     bundle=None, overwrite=False, *args, **kwargs):
            if version is None:
                version = vistrails.db.versions.currentVersion
            DBSerializer.__init__(self, connection_obj, version, bundle_id, name,
                                  bundle, overwrite, *args, **kwargs)
            self.add_serializer("vistrail", VistrailDBSerializer)

    def test_manifest(self):
        manifest = Manifest()
        paths = [('vistrail', None, 'vistrail.xml'),
                 ('thumbnail', 'abc', 'thumbs/abc.png'),
                 ('thumbnail', 'def', 'thumbs/def.png')]
        for p in paths:
            manifest.add_entry(*p)
        manifest.remove_entry(paths[1][0], paths[1][1])
        self.assertEqual(len(manifest.get_items()), len(paths)-1)
        manifest.change_entry(paths[2][0], paths[2][1], 'thumbs/thumb-def.png')
        self.assertEqual(manifest.get_value(paths[2][0], paths[2][1]),
                         'thumbs/thumb-def.png')

    def test_manifest_file(self):
        d = tempfile.mkdtemp(prefix='vt_bundle_test')
        try:
            manifest = FileManifest('test', '1.0.0', d)
            paths = [('vistrail', None, 'vistrail.xml'),
                     ('thumbnail', 'abc', 'thumbs/abc.png'),
                     ('thumbnail', 'def', 'thumbs/def.png')]
            for p in paths:
                manifest.add_entry(*p)
            manifest.save()
            self.assertTrue(os.path.exists(os.path.join(d, "MANIFEST")))

            manifest2 = FileManifest('test', '1.0.0', d)
            manifest2.load()
            for p in paths:
                self.assertTrue(manifest2.has_entry(p[0], p[1]))
                self.assertEqual(manifest.get_value(p[0], p[1]),
                                 manifest2.get_value(p[0], p[1]))
        finally:
            shutil.rmtree(d)

    def create_bundle(self):
        # should be able to have default serializer
        # created from BundleObjMapping
        m = BundleMapping('0.0.0', 'image',
                          [MultipleFileRefMapping('image', 'image')])
        b = Bundle(m)
        fname1 = os.path.join(resource_directory(), 'images', 'info.png')
        o1 = BundleObj(fname1, "image", "abc")
        b.add_object(o1)
        fname2 = os.path.join(resource_directory(), 'images', 'left.png')
        o2 = BundleObj(fname2, "image", "def")
        b.add_object(o2)
        return b

    def compare_bundles(self, b1, b2):
        print b1.get_items()
        print b2.get_items()
        self.assertEqual(len(b1.get_items()), len(b2.get_items()))
        for obj_type, obj_id, obj in b1.get_items():
            obj2 = b2.get_bundle_obj(obj_type, obj_id)
            # not ideal, but fails when trying to compare objs without __eq__
            self.assertEqual(obj.obj.__class__, obj2.obj.__class__)
            # self.assertEqual(str(obj.obj), str(obj2.obj))

    def test_dir_bundle(self):
        d = tempfile.mkdtemp(prefix='vtbundle_test')
        inner_d = os.path.join(d, 'mybundle')

        b1 = None
        b2 = None
        try:
            b1 = self.create_bundle()
            s = DirectoryBaseSerializer()
            ds = DirectorySerializer(b1.mapping)
            s.register_serializer(ds)

            s.save(b1, inner_d)

            b2 = s.load(inner_d)

            self.compare_bundles(b1, b2)
        finally:
            shutil.rmtree(d)
            # pass
        
    def test_zip_bundle(self):
        (h, fname) = tempfile.mkstemp(prefix='vtbundle_test', suffix='.zip')
        os.close(h)
        b1 = None
        b2 = None
        try:
            b1 = self.create_bundle()
            s1 = ZIPBaseSerializer()
            ds1 = DirectorySerializer(b1.mapping)
            s1.register_serializer(ds1)

            s1.save(b1, fname)

            s2 = ZIPBaseSerializer()
            ds2 = DirectorySerializer(b1.mapping)
            s2.register_serializer(ds2)


            b2 = s2.load(fname)
            
            self.compare_bundles(b1, b2)
        finally:
            if b1:
                b1.cleanup()
            if b2:
                b2.cleanup()
            os.unlink(fname)

    # def run_manifest_db(self, db_klass):
    #     """To run this, you need to create a user named "vt_test" on
    #     localhost:3306.  You also need to grant "vt_test" create table
    #     priviledges.
    #
    #     > CREATE USER 'vt_test'@'localhost';
    #     > GRANT ALL PRIVILEGES ON `vt_test`.* TO 'vt_test'@'localhost';
    #
    #     Note that autocommit mode is off (PEP 249).
    #
    #     """
    #
    #     try:
    #         db = db_klass()
    #     except ImportError:
    #         self.skipTest("Cannot import dependencies for %s." % \
    #                       db_klass.__name__)
    #
    #     connection_obj = db.setup()
    #     c = connection_obj.get_connection().cursor()
    #     c.execute(connection_obj.format_stmt(DBManifest.SCHEMA))
    #
    #     try:
    #         manifest = DBManifest(connection_obj, '1.0.0', 0)
    #
    #         entries = [('vistrail', None, 0),
    #                    ('thumbnail', 'abc', 23),
    #                    ('thumbnail', 'def', 34)]
    #         for e in entries:
    #             manifest.add_entry(*e)
    #         manifest.save()
    #
    #         manifest2 = DBManifest(connection_obj, '1.0.0', 0)
    #         manifest2.load()
    #         for e in entries:
    #             self.assertTrue(manifest2.has_entry(e[0], e[1]))
    #             self.assertEqual(manifest.get_value(e[0], e[1]),
    #                              manifest2.get_value(e[0], e[1]))
    #         connection_obj.get_connection().commit()
    #     finally:
    #         c.execute(connection_obj.format_stmt(DBManifest.DROP_SCHEMA));
    #         db.cleanup()
    #
    # def run_bundle_db(self, db_klass):
    #     try:
    #         db = db_klass()
    #     except ImportError:
    #         self.skipTest("Cannot import dependencies for %s." % \
    #                       db_klass.__name__)
    #     connection_obj = db.setup()
    #     c = connection_obj.get_connection().cursor()
    #     c.execute(connection_obj.format_stmt(DBManifest.SCHEMA))
    #     c.execute(connection_obj.format_stmt(DBSerializer.SCHEMA))
    #     c.execute(connection_obj.format_stmt(DBDataSerializer.SCHEMA))
    #
    #     s1 = None
    #     s2 = None
    #     try:
    #         b1 = self.create_bundle()
    #         s1 = DBSerializer(connection_obj, name="test", bundle=b1)
    #         s1.add_serializer('data', DBDataSerializer)
    #         s1.save()
    #
    #         s2 = DBSerializer(connection_obj, bundle_id=1)
    #         s2.add_serializer('data', DBDataSerializer)
    #         b2 = s2.load()
    #
    #         self.compare_bundles(b1, b2)
    #     finally:
    #         if s1:
    #             s1.cleanup()
    #         if s2:
    #             s2.cleanup()
    #         c.execute(connection_obj.format_stmt(DBManifest.DROP_SCHEMA));
    #         c.execute(connection_obj.format_stmt(DBSerializer.DROP_SCHEMA));
    #         c.execute(connection_obj.format_stmt(DBDataSerializer.DROP_SCHEMA));
    #         db.cleanup()
    #
    # def test_manifest_mysql(self):
    #     self.run_manifest_db(MySQLDatabaseTest)
    #
    # def test_manifest_sqlite3(self):
    #     self.run_manifest_db(SQLite3DatabaseTest)
    #
    # def test_bundle_mysql(self):
    #     self.run_bundle_db(MySQLDatabaseTest)
    #
    # def test_bundle_sqlite3(self):
    #     self.run_bundle_db(SQLite3DatabaseTest)

    def create_vt_bundle(self):
        from vistrails.db.domain import DBVistrail
        from vistrails.db.domain import DBLog

        b = new_bundle('vistrail', '0.0.0')
        b.add_object(BundleObj(DBVistrail(), None, None))
        b.add_object(BundleObj(DBLog(), None, None))
        fname1 = os.path.join(resource_directory(), 'images', 'info.png')
        b.add_object(BundleObj(fname1, 'thumbnail', 'info.png'))
        fname2 = os.path.join(resource_directory(), 'images', 'left.png')
        b.add_object(BundleObj(fname2, 'thumbnail', 'left.png'))
        return b

    def test_vt_dir_bundle(self):
        d = tempfile.mkdtemp(prefix='vtbundle_test')
        inner_d = os.path.join(d, 'mybundle')

        self.register_vt_serializer()
        b1 = None
        b2 = None
        try:
            b1 = self.create_vt_bundle()
            dir_serializer.save(b1, inner_d)

            b2 = dir_serializer.load(inner_d)

            self.compare_bundles(b1, b2)
        finally:
            if b1:
                b1.cleanup()
            if b2:
                b2.cleanup()
            shutil.rmtree(d)
            self.unregister_vt_serializer()

    def test_vt_zip_bundle(self):
        (h, fname) = tempfile.mkstemp(prefix='vtbundle_test', suffix='.zip')
        os.close(h)

        self.register_vt_serializer()
        b1 = None
        b2 = None
        try:
            b1 = self.create_vt_bundle()
            zip_serializer.save(b1, fname)

            b2 = zip_serializer.load(fname)

            self.compare_bundles(b1, b2)
        finally:
            if b1:
                b1.cleanup()
            if b2:
                b2.cleanup()
            os.unlink(fname)
            self.unregister_vt_serializer()

    # def test_old_vt_dir_load(self):
    #     d = tempfile.mkdtemp(prefix='vtbundle_test')
    #     inner_d = os.path.join(d, 'mybundle')
    #
    #     s1 = None
    #     s2 = None
    #     try:
    #         s1 = NoManifestDirSerializer('/vistrails/tmp/terminator')
    #         b1 = s1.load()
    #         s2 = DefaultVistrailsDirSerializer(inner_d, bundle=b1)
    #         s2.save()
    #     finally:
    #         shutil.rmtree(d)
    #
    # def test_old_vt_zip_load(self):
    #     in_fname = os.path.join(vistrails_root_directory(),'tests',
    #                             'resources', 'terminator.vt')
    #     (h, out_fname) = tempfile.mkstemp(prefix='vtbundle_test', suffix='.zip')
    #     os.close(h)
    #
    #     s1 = None
    #     s2 = None
    #     try:
    #         s1 = NoManifestZIPSerializer(in_fname)
    #         b1 = s1.load()
    #         s2 = DefaultVistrailsZIPSerializer(out_fname, bundle=b1)
    #         s2.save()
    #     finally:
    #         os.unlink(out_fname)

    # def run_vt_db_bundle(self, db_klass):
    #     in_fname = os.path.join(vistrails_root_directory(),'tests',
    #                             'resources', 'terminator.vt')
    #     (h, out_fname) = tempfile.mkstemp(prefix='vtbundle_test', suffix='.zip')
    #     os.close(h)
    #
    #     try:
    #         db = db_klass()
    #     except ImportError:
    #         self.skipTest("Cannot import dependencies for %s." % \
    #                       db_klass.__name__)
    #     db_version = vistrails.db.versions.currentVersion
    #     connection_obj = db.setup()
    #     c = connection_obj.get_connection().cursor()
    #     c.execute(connection_obj.format_stmt(DBManifest.SCHEMA))
    #     c.execute(connection_obj.format_stmt(DBSerializer.SCHEMA))
    #     schema_dir = vistrails.db.versions.getVersionSchemaDir(db_version)
    #     vt_schema = os.path.join(schema_dir, 'vistrails.sql')
    #     connection_obj.run_sql_file(vt_schema)
    #
    #     s1 = None
    #     s2 = None
    #     try:
    #         s1 = NoManifestZIPSerializer(in_fname)
    #         b1 = s1.load()
    #         s2 = DefaultVistrailsDBSerializer(connection_obj, bundle=b1)
    #         s2.save()
    #     finally:
    #         if s1:
    #             s1.cleanup()
    #         if s2:
    #             s2.cleanup()
    #         c.execute(connection_obj.format_stmt(DBManifest.DROP_SCHEMA));
    #         c.execute(connection_obj.format_stmt(DBSerializer.DROP_SCHEMA));
    #         # schema_dir = vistrails.db.versions.getVersionSchemaDir(db_version)
    #         # vt_drop_schema = os.path.join(schema_dir, 'vistrails_drop.sql')
    #         # connection_obj.run_sql_file(vt_drop_schema)
    #         db.cleanup()

    # def test_vt_bundle_mysql(self):
    #     self.run_vt_db_bundle(MySQLDatabaseTest)
    #
    # def test_vt_bundle_sqlite(self):
    #     self.run_vt_db_bundle(SQLite3DatabaseTest)

if __name__ == '__main__':
    unittest.main()
    #suite = unittest.TestSuite()
    #suite.addTest(TestBundles("test_vt_bundle_sqlite"))
    #unittest.TextTestRunner().run(suite)
                  
