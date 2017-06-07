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

from distutils.version import LooseVersion
import inspect
from itertools import izip
import os

from vistrails.core import debug
from vistrails.core.system import vistrails_root_directory
from vistrails.db import VistrailsDBException
from .common import translate as common_translate

currentVersion = '2.1.0'

version_map = {
    '0.3.0': '0.3.1',
    '0.3.1': '0.6.0',
    '0.5.0': '0.6.0',
    '0.6.0': '0.7.0',
    '0.7.0': '0.8.0',
    '0.8.0': '0.8.1',
    '0.8.1': '0.9.0',
    '0.9.0': '0.9.1',
    '0.9.1': '0.9.3',
    '0.9.2': '0.9.3',
    '0.9.3': '0.9.4',
    '0.9.4': '0.9.5',
    '0.9.5': '1.0.0',
    '1.0.0': '1.0.1',
    '1.0.1': '1.0.2',
    '1.0.2': '1.0.3',
    '0.1.0': '1.0.3', # for startup and mashups
    '1.0.3': '1.0.4',
    '1.0.4': '1.0.5',
    '1.0.5': '2.0.0',
    '2.0.0': '2.1.0',
}

rev_version_map = {
    '2.1.0': '2.0.0',
    '2.0.0': '1.0.5',
    '1.0.5': '1.0.4',
    '1.0.4': '1.0.3',
    '1.0.3': '1.0.2',
    '1.0.2': '1.0.1',
    '1.0.1': '1.0.0',
    '1.0.0': '0.9.5',
    '0.9.5': '0.9.4',
    '0.9.4': '0.9.3',
}

def get_current_version():
    return currentVersion

def get_sql_schema(version=None):
    if version is None:
        version = currentVersion
    try:
        pkg_name = 'vistrails.db.versions.' + get_version_name(version) + \
                   '.persistence.sql.alchemy'
        schema = __import__(pkg_name, {}, {}, [''])
    except ImportError as e:
        if str(e).startswith('No module named v'):
            msg = "Cannot find schema for version '%s'" % version
            raise VistrailsDBException(msg)
    return schema

def get_sql_utils(version=None):
    if version is None:
        version = currentVersion
    try:
        pkg_name = 'vistrails.db.versions.' + get_version_name(version) + \
                   '.persistence.sql.utils'
        utils = __import__(pkg_name, {}, {}, [''])
    except ImportError as e:
        import traceback
        traceback.print_exc()
        if str(e).startswith('No module named v'):
            msg = "Cannot find utils for version '%s'" % version
            raise VistrailsDBException(msg)
    return utils

def get_persistence(version=None):
    if version is None:
        version = currentVersion
    persistence_dir = 'vistrails.db.versions.' + get_version_name(version) + \
        '.persistence'
    try:
        persistence = __import__(persistence_dir, {}, {}, [''])
    except ImportError as e:
        if str(e).startswith('No module named v'):
            # assume version is not available
            msg = "Cannot find persistence for version '%s'" % version
            raise VistrailsDBException(msg)
        # assume other error
        import traceback
        raise VistrailsDBException(debug.format_exc())
    return persistence

get_persistence_version = get_persistence

def get_domain_obj(cls_name, version=None):
    if version is None:
        version = currentVersion
    domain_dir = 'vistrails.db.versions.' + get_version_name(version) + \
        '.domain'
    try:
        domain = __import__(domain_dir, {}, {}, [''])
    except ImportError as e:
        if str(e).startswith('No module named v'):
            # assume version is not available
            msg = "Cannot find domain for version '%s'" % version
            raise VistrailsDBException(msg)
        # assume other error
        import traceback
        raise VistrailsDBException(debug.format_exc())

    return getattr(domain, cls_name)

def version_list():
    v_list = []
    for (k,v) in version_map.items():
        v_list.append(LooseVersion(k))
    v_list.sort()
    return v_list

def get_versioned_f(f_name, version=None):
    if version is None:
        version = currentVersion
    v_list = version_list()
    v_idx = v_list.index(LooseVersion(version))
    while v_idx >= 0:
        v = str(v_list[v_idx])
        persistence = get_persistence(v)
        if hasattr(persistence, f_name):
           break
        v_idx -= 1
    if v_idx < 0:
        # FIXME should we use common??
        raise KeyError('No method "{}" found in version "{}" or earlier.'
                       .format(f_name, version))
    return getattr(persistence, f_name)

def register_bundle_serializers(version=None):
    pkg = get_persistence_version(version)
    if hasattr(pkg, 'register_bundle_serializers'):
        pkg.register_bundle_serializers()

def unregister_bundle_serializers(version=None):
    pkg = get_persistence_version(version)
    if hasattr(pkg, 'unregister_bundle_serializers'):
        pkg.unregister_bundle_serializers()

def getVersionDAO(version=None):
    if version is None:
        version = currentVersion
    persistence_dir = 'vistrails.db.versions.' + get_version_name(version) + \
        '.persistence'
    try:
        persistence = __import__(persistence_dir, {}, {}, [''])
    except ImportError as e:
        if str(e).startswith('No module named v'):
            # assume version is not available
            msg = "Cannot find DAO for version '%s'" % version
            raise VistrailsDBException(msg)
        # assume other error
        import traceback
        raise VistrailsDBException(debug.format_exc())
    return persistence.DAOList()

def get_version_path(version, target_version):
    old_tuple = get_version_tuple(version)
    new_tuple = get_version_tuple(target_version)
    used_map = version_map
    for i, j in izip(old_tuple, new_tuple):
        if i < j:
            # forward
            break
        elif i > j:
            # reverse
            used_map = rev_version_map
            break

    path = []
    while version != target_version:
        next_version = used_map[version]
        path.append((version, next_version))
        version = next_version
    return path

def translate_object(obj, method_name, version=None, target_version=None,
                     external_data=None):
    if version is None:
        try:
            version = obj.version
        except AttributeError:
            version = obj.db_version

    if target_version is None:
        target_version = currentVersion
    version = get_full_version_str(version)
    target_version = get_full_version_str(target_version)

    def get_translate_module(map, start_version, end_version):
        translate_dir = 'vistrails.db.versions.' + \
            get_version_name(end_version) + '.translate.' + \
            get_version_name(start_version)
        return __import__(translate_dir, {}, {}, [''])

    old_tuple = get_version_tuple(version)
    new_tuple = get_version_tuple(target_version)
    map = version_map
    for i, j in izip(old_tuple, new_tuple):
        if i < j:
            # forward
            break
        elif i > j:
            # reverse
            map = rev_version_map
            break

    # don't get stuck in an infinite loop
    count = 0
    while version != target_version:
        if count > len(map):
            break
        next_version = map[version]
        obj_type = method_name[9].lower() + method_name[10:]
        # print "TRANSLATING {} FROM {} TO {}".format(obj_type, version, next_version)
        obj = common_translate.translate_object(obj, version, next_version,
                                                external_data, obj_type)
        version = next_version
        count += 1

    if version != target_version:
        msg = "An error occurred when translating,"
        msg += "only able to translate to version '%s'" % version
        raise VistrailsDBException(msg)

    return obj

def translate_vistrail(vistrail, version=None, target_version=None, external_data=None):
    return translate_object(vistrail, 'translateVistrail', version, 
                            target_version, external_data)

def translate_workflow(workflow, version=None, target_version=None, external_data=None):
    return translate_object(workflow, 'translateWorkflow', version, 
                            target_version, external_data)

def translate_log(log, version=None, target_version=None, external_data=None):
    return translate_object(log, 'translateLog', version, target_version,
                            external_data)

def translate_registry(registry, version=None, target_version=None, external_data=None):
    return translate_object(registry, 'translateRegistry', version, 
                            target_version, external_data)

def translate_mashup(mashup, version=None, target_version=None, external_data=None):
    return translate_object(mashup, 'translateMashup', version,
                            target_version, external_data)

def translate_startup(startup, version=None, target_version=None, external_data=None):
    return translate_object(startup, 'translateStartup', version,
                            target_version, external_data)

def translate_bundle(bundle, version=None, target_version=None, external_data=None):
    return translate_object(bundle, 'translateBundle', version, target_version,
                            external_data)

def get_full_version_str(version_str):
    while len(version_str.split('.')) < 3:
        version_str = version_str + '.0'
    return version_str

def get_version_name(version_no):
    return 'v' + get_full_version_str(version_no).replace('.', '_')

def get_version_tuple(version_no):
    return get_full_version_str(version_no).split('.')

def getVersionSchemaDir(version=None):
    if version is None:
        version = currentVersion
    versionName = get_version_name(version)
    schemaDir = os.path.join(vistrails_root_directory(), 'db', 'versions', 
                             versionName, 'schemas', 'sql')
    return schemaDir
