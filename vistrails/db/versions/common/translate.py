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

from bundle import SaveBundle

import copy
import inspect

class ExternalData(object):
    def __init__(self, id_remap=None, translate_dict=None, child_extdata=None):
        self.id_remap = id_remap if id_remap is not None else {}
        self.translate_dict = translate_dict if translate_dict is not None else {}
        self.child_extdata = child_extdata if child_extdata is not None else {}

    def get_child_extdata(self, k, create=False, cls=None):
        if k not in self.child_extdata and create:
            return self.new_child_extdata(k, cls)
        return self.child_extdata[k]

    def new_child_extdata(self, k, cls=None):
        if cls is not None:
            self.child_extdata[k] = cls()
        else:
            self.child_extdata[k] = ExternalData()
        return self.child_extdata[k]

    def has_child_extdata(self, k):
        return k in self.child_extdata

    def has_translator(self, cls_name, attr_name):
        return (cls_name in self.translate_dict and
                attr_name in self.translate_dict[cls_name])

    def add_translator(self, cls_name, attr_name, f, overwrite=False):
        if cls_name not in self.translate_dict:
            self.translate_dict[cls_name] = {}
        if overwrite or attr_name not in cls_name:
            self.translate_dict[cls_name][attr_name] = f
        else:
            raise KeyError("Translation already exists for {}.{}. "
                           "May need to use overwrite=True.")

    def update_tdict(self, other):
        if hasattr(other, 'translate_dict'):
            translate_dict = other.translate_dict
        else:
            translate_dict = other
        for k1, tdict in translate_dict.iteritems():
            if k1 not in self.translate_dict:
                self.translate_dict[k1] = tdict
            else:
                for k2, f in tdict.iteritems():
                    self.translate_dict[k1][k2] = f

    def update_id_remap(self, other):
        # allow other to be an id_remap dict or ExternalData
        if hasattr(other, 'id_remap'):
            id_remap = other.id_remap
        else:
            id_remap = other
        for k, v in id_remap.iteritems():
            self.id_remap[k] = v

    def update(self, other):
        self.id_remap.update(other.id_remap)
        self.translate_dict.update(other.translate_dict)
        for k, c in other.child_extdata.iteritems():
            if k in self.child_extdata:
                self.child_extdata[k].update(c)
            else:
                self.child_extdata[k] = copy.copy(c)

    def remove_non_unique(self, non_unique, inplace=False):
        new_remap = {}
        for ((t, k1), k2) in self.id_remap.iteritems():
            if t not in non_unique:
                # check for idscope remap here...
                new_remap[(t, k1)] = k2
        if inplace:
            self.id_remap = new_remap
        return new_remap

    def invert_remaps(self, child_key_remap={}):
        to_delete = []
        to_add = []
        for k, c in self.child_extdata.iteritems():
            if k in child_key_remap:
                to_add.append((child_key_remap[k], c.invert_remaps()))
                to_delete.append(k)
            else:
                c.invert_remaps()
        for k, v in to_add:
            self.child_extdata[k] = v
        for k in to_delete:
            del self.child_extdata[k]
        self.id_remap = {(t, k2): k1 for (t, k1), k2 in self.id_remap.iteritems()}
        return self

    def print_remaps(self, prefix="", with_children=True):
        for k,v in self.id_remap.iteritems():
            print "{}{} -> {}".format(prefix,k,v)
        if with_children:
            for k,c in self.child_extdata.iteritems():
                print "*** {}{} ***".format(prefix,k)
                c.print_remaps(prefix, with_children)

    def __copy__(self):
        return ExternalData(id_remap=copy.copy(self.id_remap),
                            translate_dict=copy.copy(self.translate_dict),
                            child_extdata=copy.copy(self.child_extdata))
        # return {k: copy.copy(v) for k, v in self.iteritems()}

class GroupExternalData(ExternalData):
    def invert_remaps(self, child_key_remap={}):
        key_remap = {('group', k[1]): ('group', v)
                     for k, v in self.id_remap.iteritems()
                     if type(k) == tuple and k[0] == 'module'}

        res = super(GroupExternalData, self).invert_remaps(key_remap)
        return res


class LocalTranslateDictExtdata(ExternalData):
    """Create a local copy of the translate dictionary so that the tdict passed in is not modified"""
    def __init__(self, extdata):
        # Note that we do not copy anything, the same objects from extdata
        # will be updated except for the translate_dict in the context
        self.id_remap = extdata.id_remap
        self.translate_dict = extdata.translate_dict
        self.child_extdata = extdata.child_extdata
        self.orig_translate_dict = None

    def stash_translate_dict(self):
        self.orig_translate_dict = self.translate_dict
        # we only need a shallow copy here
        self.translate_dict = copy.copy(self.translate_dict)

    def revert_translate_dict(self):
        self.translate_dict = self.orig_translate_dict
        self.orig_translate_dict = None

    def __enter__(self):
        self.stash_translate_dict()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.revert_translate_dict()

def update_extdata(extdata, updates):
    for k, v in updates.iteritems():
        if k in extdata:
            extdata[k].update(v)
        else:
            extdata[k] = v


def get_full_version_str(version_str):
    while len(version_str.split('.')) < 3:
        version_str = version_str + '.0'
    return version_str

def get_version_name(version_no):
    return 'v' + get_full_version_str(version_no).replace('.', '_')

def get_domain_cls(version, obj_type):
    version_domain_id = 'vistrails.db.versions.{}.domain'.format(
        get_version_name(version))
    version_domain_pkg = __import__(version_domain_id, {}, {}, [''])
    for _, c in inspect.getmembers(version_domain_pkg):
        if inspect.isclass(c) and hasattr(c, 'vtType') and c.vtType == obj_type:
            return c
    raise KeyError('Domain class for type "{}" not found'.format(obj_type))

def get_translate_module(start_version, end_version):
    start_version = get_full_version_str(start_version)
    end_version = get_full_version_str(end_version)

    translate_dir = 'vistrails.db.versions.{}.translate.{}'.format(
        get_version_name(end_version), get_version_name(start_version))
    return __import__(translate_dir, {}, {}, [''])

def get_translate_object_f(obj_type, start_version, end_version):
    m = get_translate_module(start_version, end_version)
    if hasattr(m, "translate_{}".format(obj_type)):
        return getattr(m, "translate_{}".format(obj_type))
    elif hasattr(m, "translate{}".format(obj_type.capitalize())):
        return getattr(m, "translate{}".format(obj_type.capitalize()))
    return None

def translate_object_default_f(version):
    def translate_f(_obj, external_data=None):
        # if external_data is not None and "translate_dict" in external_data:
        #     translate_dict = external_data["translate_dict"]
        # else:
        #     translate_dict = {}
        if external_data is None:
            external_data = ExternalData()

        cls = get_domain_cls(version, _obj.vtType)
        obj = cls()
        if hasattr(cls, 'update_version'):
            obj = cls.update_version(_obj, external_data.translate_dict, obj)
        obj.db_version = version
        return obj
    return translate_f

def translate_with_groups_f(version):
    def translate_f(_obj, external_data=None):
        # if external_data is None:
        #     external_data = {}
        # if "translate_dict" not in external_data:
        #     external_data["translate_dict"] = {}
        # don't modify existing translate_dict-could hardcode incorrect version
        # translate_dict = copy.copy(external_data["translate_dict"])
        if external_data is None:
            external_data = ExternalData()
        with LocalTranslateDictExtdata(external_data) as extdata:
            # if 'DBGroup' not in translate_dict:
            #     translate_dict['DBGroup'] = {}
            # if 'workflow' not in translate_dict['DBGroup']:
            #     wf_cls = get_domain_cls(version, 'workflow')
            wf_cls = get_domain_cls(version, 'workflow')
            def update_workflow(old_obj, trans_dict):
                new_obj = wf_cls()
                new_obj = wf_cls.update_version(old_obj.db_workflow,
                                                trans_dict, new_obj)
                new_obj.db_version = version
                return new_obj
            extdata.add_translator('DBGroup', 'workflow', update_workflow)
            return translate_object_default_f(version)(_obj, extdata)
    return translate_f

def translate_bundle_f(version):
    def translate_f(_bundle, external_data=None):
        bundle = SaveBundle(_bundle.bundle_type)
        if _bundle.vistrail is not None:
            bundle.vistrail = translate_object(_bundle.vistrail, _bundle.vistrail.db_version, version, external_data, 'vistrail')
        if _bundle.workflow is not None:
            bundle.workflow = translate_object(_bundle.workflow, _bundle.workflow.db_version, version, external_data, 'workflow')
        if _bundle.log is not None:
            # print "TRANSLATING LOG VERSION:", _bundle.log.db_version, version
            bundle.log = translate_object(_bundle.log, _bundle.log.db_version, version, external_data, 'log')
        if _bundle.registry is not None:
            bundle.registry = translate_object(_bundle.registry, _bundle.registry.db_version, version, external_data, 'registry')
        if hasattr(_bundle, 'mashups'):
            for _mashup in _bundle.mashups:
                bundle.mashups.append(translate_object(_mashup, _mashup.db_version, version, external_data, 'mashup'))
        bundle.thumbnails = copy.copy(_bundle.thumbnails)
        bundle.opm_graph = _bundle.opm_graph
        # FIXME translate abstractions?
        for a in _bundle.abstractions:
            bundle.abstractions.append(a)
        for s in _bundle.subworkflows:
            bundle.subworkflows.append(s)
        return bundle

    # def translate_f(_bundle, external_data=None):
    #     if 'obj_types' in external_data:
    #         obj_types = external_data['obj_types']
    #     else:
    #         obj_types = ['vistrail', 'workflow', 'log', 'registry', ('mashup', True)]
    #     if 'update_extdata' in external_data:
    #         update_extdata = external_data["update_extdata"]
    #     else:
    #         update_extdata = {}
    #
    #     bundle = SaveBundle(_bundle.bunde_type)
    #     all_extdata = {}
    #     for obj_type in obj_types:
    #         is_plural = False
    #         if type(obj_type) == tuple:
    #             obj_type = obj_type[0]
    #             if len(obj_type) > 1:
    #                 is_plural = obj_type[1]
    #         extdata_k = "{}_extdata".format(obj_type)
    #         if extdata_k in external_data:
    #             obj_extdata = external_data[extdata_k]
    #         else:
    #             obj_extdata = {}
    #
    #         #FIXME add some way to update extdata across objects?
    #         if hasattr(_bundle, obj_type):
    #             update_extdata_f = None
    #             if obj_type in 'update_extdata':
    #                 update_extdata_f = update_extdata[obj_type]
    #
    #             def translate_one(_obj, obj_extdata):
    #                 if update_extdata_f is not None:
    #                     obj_extdata = update_extdata_f(version, all_extdata,
    #                                                    obj_extdata)
    #                 return translate_object(_obj, _obj.db_version, version, obj_extdata,
    #                                         obj_type)
    #
    #             if is_plural:
    #                 attr_name = "{}s".format(obj_type)
    #                 _objs = getattr(_bundle, "{}s".format(obj_type))
    #                 objs = []
    #                 for _obj in _objs:
    #                     if update_extdata_f is not None:
    #                         obj_extdata = update_extdata_f(version, all_extdata, obj_extdata)
    #                     objs.append(translate_object(version, _obj, obj_extdata))
    #                 setattr(bundle, attr_name, objs)
    #             else:
    #                 _obj = getattr(_bundle, obj_type)
    #                 obj = translate_object(version, _obj, obj_extdata)
    #                 setattr(bundle, obj_type, obj)

    return translate_f

defaults = {'vistrail': translate_with_groups_f,
            'workflow': translate_with_groups_f,
            'bundle': translate_bundle_f,
            }

def translate_object(_obj, start_version, end_version, external_data=None,
                     obj_type=None):
    # print "TRANSLATING:", obj_type, start_version, end_version
    if obj_type is None:
        obj_type = _obj.vtType
    translate_f = get_translate_object_f(obj_type, start_version, end_version)
    if translate_f is None:
        if obj_type not in defaults:
            translate_f = translate_object_default_f(end_version)
        else:
            translate_f = defaults[obj_type](end_version)
    fspec = inspect.getargspec(translate_f)
    if len(fspec.args) > 1:
        obj = translate_f(_obj, external_data)
    else:
        obj = translate_f(_obj)
    return obj