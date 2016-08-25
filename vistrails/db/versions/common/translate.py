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

import inspect

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

def translate_object_default(version):
    def translate_f(_obj, external_data=None):
        if "translate_dict" in external_data:
            translate_dict = external_data["translate_dict"]
        else:
            translate_dict = {}

        cls = get_domain_cls(version, _obj.vtType)
        obj = cls()
        if hasattr(cls, 'update_version'):
            obj = cls.update_version(_obj, translate_dict, obj)
        obj.db_version = version
        return obj
    return translate_f

def translate_with_groups(version):
    def translate_f(_obj, external_data=None):
        if external_data is None:
            external_data = {}
        if "translate_dict" not in external_data:
            external_data["translate_dict"] = {}
        translate_dict = external_data["translate_dict"]
        if 'DBGroup' not in translate_dict:
            translate_dict['DBGroup'] = {}
        if 'workflow' not in translate_dict['DBGroup']:
            wf_cls = get_domain_cls(version, 'workflow')
            def update_workflow(old_obj, trans_dict):
                return wf_cls.update_version(old_obj.db_workflow,
                                             trans_dict, wf_cls())
            translate_dict['DBGroup']['workflow'] = update_workflow
        return translate_object_default(version)(_obj, external_data)
    return translate_f

def translate_vistrail_default(version):
    return translate_with_groups(version)

def translate_workflow_default(version):
    return translate_with_groups(version)

# def translate_vistrail_default(version, _vistrail, external_data=None):
#     if "translate_dict" in external_data:
#         translate_dict = external_data["translate_dict"]
#     else:
#         translate_dict = {}
#
#     if 'DBGroup' not in translate_dict:
#         translate_dict['DBGroup'] = {}
#     if 'workflow' not in translate_dict['DBGroup']:
#         wf_cls = get_domain_cls(version, 'workflow')
#         def update_workflow(old_obj, trans_dict):
#             return wf_cls.update_version(old_obj.db_workflow,
#                                          trans_dict, wf_cls())
#         translate_dict['DBGroup']['workflow'] = update_workflow
#     return translate_object_default(version, _vistrail, external_data)
#
# def translate_workflow_default(version, _workflow, external_data=None):
#     if "translate_dict" in external_data:
#         translate_dict = external_data["translate_dict"]
#     else:
#         translate_dict = {}
#
#     if 'DBGroup' not in translate_dict:
#         translate_dict['DBGroup'] = {}
#     if 'workflow' not in translate_dict['DBGroup']:
#         wf_cls = get_domain_cls(version, 'workflow')
#         def update_workflow(old_obj, trans_dict):
#             return wf_cls.update_version(old_obj.db_workflow,
#                                          trans_dict, wf_cls())
#         translate_dict['DBGroup']['workflow'] = update_workflow
#     return translate_object_default(version, _workflow, external_data)

def translate_bundle(version, _bundle, external_data=None):
    if 'obj_types' in external_data:
        obj_types = external_data['obj_types']
    else:
        obj_types = ['vistrail', 'workflow', 'log', 'registry', ('mashup', True)]
    if 'update_extdata' in external_data:
        update_extdata = external_data["update_extdata"]
    else:
        update_extdata = {}

    bundle = SaveBundle(_bundle.bunde_type)
    all_extdata = {}
    for obj_type in obj_types:
        is_plural = False
        if type(obj_type) == tuple:
            obj_type = obj_type[0]
            if len(obj_type) > 1:
                is_plural = obj_type[1]
        extdata_k = "{}_extdata".format(obj_type)
        if extdata_k in external_data:
            obj_extdata = external_data[extdata_k]
        else:
            obj_extdata = {}

        #FIXME add some way to update extdata across objects?
        if hasattr(_bundle, obj_type):
            update_extdata_f = None
            if obj_type in 'update_extdata':
                update_extdata_f = update_extdata[obj_type]

            def translate_one(_obj, obj_extdata):
                if update_extdata_f is not None:
                    obj_extdata = update_extdata_f(version, all_extdata,
                                                   obj_extdata)

            if is_plural:
                attr_name = "{}s".format(obj_type)
                _objs = getattr(_bundle, "{}s".format(obj_type))
                objs = []
                for _obj in _objs:
                    if update_extdata_f is not None:
                        obj_extdata = update_extdata_f(version, all_extdata, obj_extdata)
                    objs.append(translate_object(version, _obj, obj_extdata))
                setattr(bundle, attr_name, objs)
            else:
                _obj = getattr(_bundle, obj_type)
                obj = translate_object(version, _obj, obj_extdata)
                setattr(bundle, obj_type, obj)

defaults = {'vistrail': translate_with_groups,
            'workflow': translate_with_groups,
            'bundle': translate_bundle,
            }

def translate_object(_obj, start_version, end_version, external_data=None,
                     obj_type=None):
    if obj_type is None:
        obj_type = _obj.vtType
    translate_f = get_translate_object_f(obj_type, start_version, end_version)
    if translate_f is None:
        if obj_type not in defaults:
            translate_f = translate_object_default(end_version)
        else:
            translate_f = defaults[obj_type](end_version)
    fspec = inspect.getargspec(translate_f)
    if len(fspec.args) > 1:
        obj = translate_f(_obj, external_data)
    else:
        obj = translate_f(_obj)
    return obj

# def translateBundle(_bundle):
#     bundle = SaveBundle(_bundle.bundle_type)
#     if _bundle.vistrail is not None:
#         bundle.vistrail = translateVistrail(_bundle.vistrail)
#     if _bundle.workflow is not None:
#         bundle.workflow = translateWorkflow(_bundle.workflow)
#     if _bundle.log is not None:
#         bundle.log = translateLog(_bundle.log)
#     if _bundle.registry is not None:
#         bundle.registry = translateRegistry(_bundle.registry)
#     for _mashup in _bundle.mashups:
#         bundle.mashups.append(translateMashup(_mashup))
#     bundle.thumbnails = copy.copy(_bundle.thumbnails)
#     bundle.opm_graph = _bundle.opm_graph
#     # FIXME translate abstractions?
#     for a in _bundle.abstractions:
#         bundle.abstractions.append(a)
#     return bundle
